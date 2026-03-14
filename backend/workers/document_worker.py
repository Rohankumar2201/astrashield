"""
workers/document_worker.py — Background worker for document forgery detection.

Analyzes uploaded ID documents (PDF, images of passports, Aadhaar, etc.)
for signs of digital manipulation using:
- ELA (Error Level Analysis) for compression inconsistencies
- OCR text extraction for font consistency checks
- Metadata analysis
- Edge/noise analysis
"""

from celery_app import celery_app
from database import jobs_collection, analysis_collection
from utils.storage import download_from_minio
from utils.ela import compute_ela
from utils.metadata import analyze_metadata
from scoring.ensemble import compute_final_score

import cv2
import numpy as np
import io
import asyncio
import fitz  # PyMuPDF — for reading PDFs
from PIL import Image
from datetime import datetime

try:
    import pytesseract  # OCR for reading text from images
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ pytesseract not available. Install tesseract-ocr for OCR features.")


def pdf_to_image(pdf_bytes: bytes) -> bytes:
    """Convert first page of PDF to an image (PNG bytes)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]  # First page
    # Render at 300 DPI (high quality)
    mat = fitz.Matrix(300/72, 300/72)
    pix = page.get_pixmap(matrix=mat)
    return pix.tobytes("png")


def analyze_noise_patterns(image_bytes: bytes) -> dict:
    """
    Analyze image noise patterns for forgery detection.
    
    In an authentic document photo:
    - Noise is uniform and consistent throughout
    - Camera sensor noise (PRNU) is consistent
    
    In a forged document:
    - Copy-pasted regions have different noise characteristics
    - Noise variance is inconsistent across regions
    """
    try:
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
        if image is None:
            return {"score": 0.0, "flags": ["Could not decode image"]}

        # Divide image into a grid and measure noise variance in each cell
        h, w = image.shape
        grid_size = 4  # 4×4 grid
        variances = []

        for i in range(grid_size):
            for j in range(grid_size):
                # Extract grid cell
                y1 = i * h // grid_size
                y2 = (i + 1) * h // grid_size
                x1 = j * w // grid_size
                x2 = (j + 1) * w // grid_size
                cell = image[y1:y2, x1:x2]
                variances.append(float(np.var(cell)))

        # High variance in variance = inconsistent noise = suspicious
        variance_of_variance = np.var(variances)
        mean_variance = np.mean(variances)

        # Normalize to 0-1 score
        # High ratio = inconsistent noise patterns across the document
        score = min(variance_of_variance / (mean_variance * 100 + 1e-8), 1.0)

        flags = []
        if score > 0.5:
            flags.append("Inconsistent noise patterns detected across document regions")
        if score > 0.7:
            flags.append("High probability of copy-paste manipulation")

        return {
            "score": float(round(score, 3)),
            "variance_of_variance": round(variance_of_variance, 2),
            "flags": flags
        }
    except Exception as e:
        return {"score": 0.0, "flags": [f"Noise analysis error: {str(e)}"]}


def extract_text_from_document(image_bytes: bytes) -> dict:
    """Extract text using OCR and check for font inconsistencies."""
    if not OCR_AVAILABLE:
        return {"text": "", "confidence": 0, "flags": ["OCR not available"]}

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Get detailed OCR data including confidence scores per word
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Get words with their confidence scores
        words = []
        low_conf_words = []
        for i, word in enumerate(data["text"]):
            conf = data["conf"][i]
            if word.strip() and conf != -1:
                words.append({"word": word, "confidence": conf})
                if conf < 40:  # Low OCR confidence = possibly inconsistent font
                    low_conf_words.append(word)

        flags = []
        if low_conf_words:
            flags.append(f"Low OCR confidence on {len(low_conf_words)} words (possible font inconsistency)")

        full_text = " ".join([w["word"] for w in words])
        avg_confidence = np.mean([w["confidence"] for w in words]) if words else 0

        return {
            "text": full_text[:500],  # Truncate for storage
            "word_count": len(words),
            "avg_confidence": round(float(avg_confidence), 1),
            "flags": flags,
            "score": 1.0 - min(avg_confidence / 100, 1.0) if words else 0.5
        }
    except Exception as e:
        return {"text": "", "flags": [str(e)], "score": 0.0}


@celery_app.task(bind=True, name="workers.document_worker.analyze_document")
def analyze_document(self, job_id: str, storage_path: str):
    """Main document analysis Celery task."""

    def update_status(status: str, progress: int, step: str = None):
        async def _update():
            update = {"status": status, "progress": progress}
            if step:
                update[f"steps.{step}"] = "completed"
            await jobs_collection.update_one({"job_id": job_id}, {"$set": update})
        asyncio.run(_update())

    try:
        start_time = datetime.utcnow()
        update_status("processing", 10, "preprocessing")

        file_bytes = download_from_minio(storage_path)

        # If PDF, convert first page to image for analysis
        is_pdf = storage_path.lower().endswith(".pdf")
        image_bytes = pdf_to_image(file_bytes) if is_pdf else file_bytes

        update_status("processing", 30)

        # Run all analysis modules
        ela_result = compute_ela(image_bytes)
        update_status("processing", 50, "ai_analysis")

        noise_result = analyze_noise_patterns(image_bytes)
        ocr_result = extract_text_from_document(image_bytes)
        metadata_result = analyze_metadata(file_bytes)

        update_status("processing", 75, "scoring")

        # Compute final score
        module_scores = {
            "ela_analysis":   {"score": ela_result.get("score", 0), "weight": 0.35},
            "noise_patterns": {"score": noise_result.get("score", 0), "weight": 0.30},
            "ocr_analysis":   {"score": ocr_result.get("score", 0), "weight": 0.20},
            "metadata":       {"score": metadata_result.get("score", 0), "weight": 0.15},
        }
        final_result = compute_final_score(module_scores)
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Collect all flags
        all_flags = (
            ela_result.get("flags", []) +
            noise_result.get("flags", []) +
            ocr_result.get("flags", []) +
            metadata_result.get("flags", [])
        )

        report = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "file_type": "document",
            "fraud_risk_score": final_result["fraud_risk_score"],
            "risk_category": final_result["risk_category"],
            "modules": {
                "ela_analysis": {
                    "score": round(ela_result.get("score", 0) * 100, 1),
                    "ela_image": ela_result.get("ela_image_b64"),
                    "interpretation": ela_result.get("interpretation", ""),
                },
                "noise_pattern_analysis": {
                    "score": round(noise_result.get("score", 0) * 100, 1),
                    "flags": noise_result.get("flags", []),
                },
                "ocr_analysis": {
                    "score": round(ocr_result.get("score", 0) * 100, 1),
                    "extracted_text_preview": ocr_result.get("text", "")[:200],
                    "avg_confidence": ocr_result.get("avg_confidence", 0),
                    "flags": ocr_result.get("flags", []),
                },
                "metadata_forensics": {
                    "score": round(metadata_result.get("score", 0) * 100, 1),
                    "flags": metadata_result.get("flags", []),
                },
            },
            "all_flags": all_flags,
            "recommendation": final_result["recommendation"],
            "processing_time_ms": processing_time,
        }

        async def _save():
            await analysis_collection.insert_one(report.copy())
            await jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": {"status": "completed", "progress": 100, "steps.report": "completed"}}
            )
        asyncio.run(_save())

        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        async def _fail():
            await jobs_collection.update_one(
                {"job_id": job_id}, {"$set": {"status": "failed", "error": str(e)}}
            )
        asyncio.run(_fail())
        raise
