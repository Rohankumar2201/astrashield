"""
scripts/generate_demo_data.py — Populates MongoDB with fake analysis results
so you can see the dashboard working before training real AI models.

Run this from the backend folder:
  cd backend
  python ../scripts/generate_demo_data.py
"""

import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "astrashield")

# Realistic fake filenames for demo
IMAGE_NAMES    = ["face_photo.jpg", "profile_pic.png", "id_scan.jpg", "passport.png", "headshot.webp"]
AUDIO_NAMES    = ["voice_message.mp3", "phone_call.wav", "ceo_audio.m4a", "interview.wav"]
DOCUMENT_NAMES = ["passport_scan.pdf", "aadhaar_card.pdf", "drivers_license.pdf", "pan_card.pdf"]

RECOMMENDATIONS = {
    "LOW":      "Content appears authentic. No significant AI manipulation detected.",
    "MEDIUM":   "Some suspicious indicators detected. Manual review recommended.",
    "HIGH":     "Strong indicators of AI manipulation. Escalate to senior analyst.",
    "CRITICAL": "HIGH CONFIDENCE AI GENERATION DETECTED. Do not use as authentic media.",
}


def random_score_for_category(category: str) -> int:
    """Return a realistic score for each risk category."""
    ranges = {"LOW": (5, 29), "MEDIUM": (31, 59), "HIGH": (62, 84), "CRITICAL": (87, 99)}
    lo, hi = ranges[category]
    return random.randint(lo, hi)


def make_image_report(job_id: str, score: int, category: str, ts: str) -> dict:
    fake_prob = score / 100
    return {
        "job_id": job_id,
        "timestamp": ts,
        "file_type": "image",
        "fraud_risk_score": score,
        "risk_category": category,
        "recommendation": RECOMMENDATIONS[category],
        "processing_time_ms": random.randint(800, 3200),
        "modules": {
            "image_deepfake": {
                "score": round(fake_prob * 100 + random.uniform(-5, 5), 1),
                "faces_detected": random.randint(0, 2),
                "model": "EfficientNet-B4",
                "face_results": [{
                    "bounding_box": {"x": 120, "y": 80, "w": 160, "h": 180},
                    "deepfake_probability": fake_prob,
                    "real_probability": 1 - fake_prob,
                }] if random.random() > 0.3 else [],
            },
            "ela_analysis": {
                "score": round(fake_prob * 100 + random.uniform(-8, 8), 1),
                "ela_image": None,
                "mean_diff": round(random.uniform(2, 35), 2),
                "interpretation": "High tampering detected" if score > 60 else "Low tampering",
            },
            "metadata_forensics": {
                "score": round(fake_prob * 100 + random.uniform(-10, 10), 1),
                "flags": (
                    ["No EXIF metadata found", "AI software signature: StableDiffusion"]
                    if score > 60 else []
                ),
                "metadata_fields_count": 0 if score > 60 else random.randint(15, 40),
            },
        },
    }


def make_audio_report(job_id: str, score: int, category: str, ts: str) -> dict:
    fake_prob = score / 100
    return {
        "job_id": job_id,
        "timestamp": ts,
        "file_type": "audio",
        "fraud_risk_score": score,
        "risk_category": category,
        "recommendation": RECOMMENDATIONS[category],
        "processing_time_ms": random.randint(600, 2400),
        "modules": {
            "voice_clone_detection": {
                "score": round(fake_prob * 100 + random.uniform(-5, 5), 1),
                "model": "ResNet-18 Spectrogram CNN",
                "sample_rate": 16000,
                "duration_seconds": round(random.uniform(2, 8), 2),
                "spectrogram_image": None,
                "real_probability": round((1 - fake_prob) * 100, 1),
                "fake_probability": round(fake_prob * 100, 1),
            },
        },
    }


def make_document_report(job_id: str, score: int, category: str, ts: str) -> dict:
    fake_prob = score / 100
    return {
        "job_id": job_id,
        "timestamp": ts,
        "file_type": "document",
        "fraud_risk_score": score,
        "risk_category": category,
        "recommendation": RECOMMENDATIONS[category],
        "processing_time_ms": random.randint(1200, 4000),
        "modules": {
            "ela_analysis": {
                "score": round(fake_prob * 100 + random.uniform(-6, 6), 1),
                "ela_image": None,
                "interpretation": "High tampering detected" if score > 60 else "Low tampering",
            },
            "noise_pattern_analysis": {
                "score": round(fake_prob * 100 + random.uniform(-8, 8), 1),
                "flags": ["Inconsistent noise patterns detected"] if score > 60 else [],
            },
            "ocr_analysis": {
                "score": round(fake_prob * 50 + random.uniform(-5, 5), 1),
                "extracted_text_preview": "PASSPORT Republic of India...",
                "avg_confidence": round(random.uniform(40, 95), 1),
                "flags": ["Low OCR confidence on 3 words"] if score > 60 else [],
            },
            "metadata_forensics": {
                "score": round(fake_prob * 80 + random.uniform(-5, 5), 1),
                "flags": ["No EXIF metadata found"] if score > 50 else [],
            },
        },
        "all_flags": (
            ["Inconsistent noise patterns", "No EXIF metadata"] if score > 60 else []
        ),
    }


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    analyses = db["analyses"]
    jobs     = db["jobs"]

    # Clear existing demo data
    await analyses.delete_many({})
    await jobs.delete_many({})
    print("Cleared existing data...")

    # Generate 30 demo analyses spread over the last 7 days
    categories = ["LOW", "LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "CRITICAL"]  # Weighted distribution
    file_types = ["image", "image", "audio", "document"]

    for i in range(30):
        category  = random.choice(categories)
        file_type = random.choice(file_types)
        score     = random_score_for_category(category)
        job_id    = f"demo_{i+1:03d}_{random.randint(1000, 9999)}"

        # Spread timestamps over the last 7 days
        ts_dt = datetime.utcnow() - timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        ts = ts_dt.isoformat()

        # Build appropriate report
        if file_type == "image":
            report = make_image_report(job_id, score, category, ts)
        elif file_type == "audio":
            report = make_audio_report(job_id, score, category, ts)
        else:
            report = make_document_report(job_id, score, category, ts)

        await analyses.insert_one(report)

        # Create matching job record
        await jobs.insert_one({
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "created_at": ts,
            "steps": {
                "upload": "completed",
                "preprocessing": "completed",
                "ai_analysis": "completed",
                "scoring": "completed",
                "report": "completed",
            }
        })

    print(f"✅ Generated 30 demo analyses in MongoDB!")
    print(f"   Database: {MONGO_URL}/{MONGO_DB}")
    print(f"\n   Now start the frontend and visit http://localhost:3000")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
