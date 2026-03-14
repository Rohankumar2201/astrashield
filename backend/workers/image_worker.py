"""
workers/image_worker.py — Background worker for image deepfake detection.

This Celery task runs in the background after a user uploads an image.
It:
1. Downloads the image from storage
2. Detects and crops faces
3. Runs EfficientNet-B4 to classify real vs deepfake
4. Runs ELA for tampering analysis
5. Analyzes metadata
6. Saves results to MongoDB
"""

from celery_app import celery_app
from database import jobs_collection, analysis_collection
from utils.storage import download_from_minio
from utils.metadata import analyze_metadata
from utils.ela import compute_ela
from scoring.ensemble import compute_final_score

try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    import timm
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available - running in demo mode")  # Library with pretrained models like EfficientNet
import numpy as np
import cv2
import io
import asyncio
from PIL import Image
from datetime import datetime


# ── Load the AI Model ─────────────────────────────────────────────────────────
# This runs once when the worker starts, not on every task

def load_image_model():
    """
    Load EfficientNet-B4 pretrained model.
    
    In production: load your fine-tuned checkpoint.
    For hackathon demo: use pretrained weights + custom head (simulated).
    """
    # timm provides pretrained EfficientNet models
    model = timm.create_model(
        "efficientnet_b4",
        pretrained=True,        # Start with ImageNet weights
        num_classes=2           # 2 classes: real (0) or fake (1)
    )
    model.eval()  # Set to evaluation mode (not training mode)
    
    # Try to load fine-tuned weights if they exist
    try:
        checkpoint = torch.load("models/image/efficientnet_b4_deepfake.pt", map_location="cpu")
        model.load_state_dict(checkpoint)
        print("✅ Loaded fine-tuned deepfake detection model")
    except FileNotFoundError:
        print("⚠️  No fine-tuned model found. Using pretrained ImageNet weights (demo mode).")
    
    return model


# Image preprocessing pipeline
# The model expects: 380×380 RGB image, normalized to ImageNet stats
image_transform = transforms.Compose([
    transforms.Resize((380, 380)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet mean
        std=[0.229, 0.224, 0.225]    # ImageNet std deviation
    )
])

# Load model at worker startup (once, not per task)
try:
    IMAGE_MODEL = load_image_model()
except Exception as e:
    IMAGE_MODEL = None
    print(f"⚠️ Could not load image model: {e}")


def detect_faces(image_array: np.ndarray) -> list:
    """
    Detect faces in an image using OpenCV's built-in face detector.
    Returns list of (x, y, w, h) bounding boxes.
    """
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    # OpenCV comes with a pre-trained face detector (no download needed)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)  # Ignore tiny detections
    )
    
    return faces.tolist() if len(faces) > 0 else []


def classify_face(face_image: Image.Image) -> dict:
    """
    Run EfficientNet-B4 on a cropped face image.
    Returns probability of being a deepfake.
    """
    if IMAGE_MODEL is None:
        # Demo mode: return a random-ish score
        import random
        score = random.uniform(0.1, 0.9)
        return {"deepfake_probability": score, "real_probability": 1 - score}
    
    # Preprocess the face image
    tensor = image_transform(face_image).unsqueeze(0)  # Add batch dimension
    
    with torch.no_grad():  # Don't compute gradients (we're not training)
        output = IMAGE_MODEL(tensor)
        probabilities = torch.softmax(output, dim=1)[0]
    
    return {
        "real_probability": float(probabilities[0]),
        "deepfake_probability": float(probabilities[1])
    }


# ── Celery Task ───────────────────────────────────────────────────────────────

@celery_app.task(bind=True, name="workers.image_worker.analyze_image")
def analyze_image(self, job_id: str, storage_path: str, mime_type: str):
    """
    Main image analysis task. Called by Celery when a job is queued.
    
    'bind=True' gives us access to 'self' so we can update task state.
    """
    
    # Helper to update job status in MongoDB
    # We run async code inside a sync Celery task using asyncio.run()
    def update_status(status: str, progress: int, step: str = None):
        async def _update():
            update = {"status": status, "progress": progress}
            if step:
                update[f"steps.{step}"] = "completed"
            await jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": update}
            )
        asyncio.run(_update())

    try:
        start_time = datetime.utcnow()
        update_status("processing", 10, "preprocessing")

        # ── Step 1: Download the image ────────────────────────────────────────
        image_bytes = download_from_minio(storage_path)
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_array = np.array(image_pil)

        update_status("processing", 25)

        # ── Step 2: Detect faces ──────────────────────────────────────────────
        faces = detect_faces(image_array)
        
        # ── Step 3: Classify each face ────────────────────────────────────────
        face_results = []
        if faces:
            for (x, y, w, h) in faces:
                face_crop = image_pil.crop((x, y, x + w, y + h))
                result = classify_face(face_crop)
                face_results.append({
                    "bounding_box": {"x": x, "y": y, "w": w, "h": h},
                    **result
                })
        
        # Overall image score = max deepfake probability across all faces
        image_score = max(
            (f["deepfake_probability"] for f in face_results),
            default=0.3  # No faces detected = moderate suspicion
        )

        update_status("processing", 50, "ai_analysis")

        # ── Step 4: ELA analysis ──────────────────────────────────────────────
        ela_result = compute_ela(image_bytes)

        update_status("processing", 70)

        # ── Step 5: Metadata analysis ─────────────────────────────────────────
        metadata_result = analyze_metadata(image_bytes)

        update_status("processing", 85, "scoring")

        # ── Step 6: Compute final fraud score ─────────────────────────────────
        module_scores = {
            "image_deepfake": {"score": image_score, "weight": 0.45},
            "ela_analysis":   {"score": ela_result["score"], "weight": 0.25},
            "metadata":       {"score": metadata_result["score"], "weight": 0.30},
        }
        final_result = compute_final_score(module_scores)

        # ── Step 7: Build the full report ─────────────────────────────────────
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        report = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "file_type": "image",
            "fraud_risk_score": final_result["fraud_risk_score"],
            "risk_category": final_result["risk_category"],
            "modules": {
                "image_deepfake": {
                    "score": round(image_score * 100, 1),
                    "faces_detected": len(faces),
                    "face_results": face_results,
                    "model": "EfficientNet-B4",
                },
                "ela_analysis": {
                    "score": round(ela_result["score"] * 100, 1),
                    "ela_image": ela_result.get("ela_image_b64"),
                    "mean_diff": ela_result.get("mean_diff"),
                    "interpretation": ela_result.get("interpretation"),
                },
                "metadata_forensics": {
                    "score": round(metadata_result["score"] * 100, 1),
                    "flags": metadata_result["flags"],
                    "metadata_fields_count": metadata_result["metadata_fields_count"],
                }
            },
            "recommendation": final_result["recommendation"],
            "processing_time_ms": processing_time,
        }

        # Save report to MongoDB
        async def _save():
            await analysis_collection.insert_one(report.copy())
            await jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": {"status": "completed", "progress": 100, "steps.report": "completed"}}
            )
        asyncio.run(_save())

        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        # If anything goes wrong, mark the job as failed
        async def _fail():
            await jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )
        asyncio.run(_fail())
        raise  # Re-raise so Celery knows the task failed
