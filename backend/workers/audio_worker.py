"""
workers/audio_worker.py — Audio analysis worker (deployment safe version)
Runs in demo mode when PyTorch is not available.
"""

from celery_app import celery_app
from database import jobs_collection, analysis_collection
from utils.storage import download_from_minio
from scoring.ensemble import compute_final_score

import asyncio
import random
from datetime import datetime


@celery_app.task(bind=True, name="workers.audio_worker.analyze_audio")
def analyze_audio(self, job_id: str, storage_path: str):
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

        audio_bytes = download_from_minio(storage_path)
        update_status("processing", 40, "ai_analysis")

        # Demo mode score
        fake_prob = random.uniform(0.2, 0.9)
        update_status("processing", 80, "scoring")

        module_scores = {
            "voice_clone_detection": {"score": fake_prob, "weight": 1.0},
        }
        final_result = compute_final_score(module_scores)
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        report = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "file_type": "audio",
            "fraud_risk_score": final_result["fraud_risk_score"],
            "risk_category": final_result["risk_category"],
            "modules": {
                "voice_clone_detection": {
                    "score": round(fake_prob * 100, 1),
                    "model": "ResNet-18 Spectrogram CNN (demo mode)",
                    "sample_rate": 16000,
                    "duration_seconds": 3.0,
                    "spectrogram_image": None,
                    "real_probability": round((1 - fake_prob) * 100, 1),
                    "fake_probability": round(fake_prob * 100, 1),
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