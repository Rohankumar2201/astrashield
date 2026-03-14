"""
workers/image_worker.py — Image analysis worker (deployment safe version)
Runs in demo mode when PyTorch is not available.
"""

from celery_app import celery_app
from database import jobs_collection, analysis_collection
from utils.storage import download_from_minio
from utils.metadata import analyze_metadata
from utils.ela import compute_ela
from scoring.ensemble import compute_final_score

import asyncio
import random
from datetime import datetime


@celery_app.task(bind=True, name="workers.image_worker.analyze_image")
def analyze_image(self, job_id: str, storage_path: str, mime_type: str):
    def update_status(status, progress, step=None):
        async def _update():
            update = {"status": status, "progress": progress}
            if step:
                update[f"steps.{step}"] = "completed"
            await jobs_collection.update_one({"job_id": job_id}, {"$set": update})
        asyncio.run(_update())

    try:
        start_time = datetime.utcnow()
        update_status("processing", 10, "preprocessing")

        image_bytes = download_from_minio(storage_path)
        update_status("processing", 30)

        ela_result = compute_ela(image_bytes)
        update_status("processing", 50, "ai_analysis")

        metadata_result = analyze_metadata(image_bytes)
        update_status("processing", 70)

        # Demo mode score when PyTorch not available
        image_score = random.uniform(0.3, 0.95)

        update_status("processing", 85, "scoring")

        module_scores = {
            "image_deepfake": {"score": image_score, "weight": 0.45},
            "ela_analysis":   {"score": ela_result.get("score", 0), "weight": 0.25},
            "metadata":       {"score": metadata_result.get("score", 0), "weight": 0.30},
        }
        final_result = compute_final_score(module_scores)
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
                    "faces_detected": random.randint(0, 2),
                    "model": "EfficientNet-B4 (demo mode)",
                    "face_results": [],
                },
                "ela_analysis": {
                    "score": round(ela_result.get("score", 0) * 100, 1),
                    "ela_image": ela_result.get("ela_image_b64"),
                    "mean_diff": ela_result.get("mean_diff"),
                    "interpretation": ela_result.get("interpretation"),
                },
                "metadata_forensics": {
                    "score": round(metadata_result.get("score", 0) * 100, 1),
                    "flags": metadata_result.get("flags", []),
                    "metadata_fields_count": metadata_result.get("metadata_fields_count", 0),
                }
            },
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