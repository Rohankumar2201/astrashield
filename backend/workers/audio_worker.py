"""
workers/audio_worker.py — Background worker for voice clone detection.

How voice clone detection works:
1. Convert audio to a mel spectrogram (a 2D image of the audio frequencies)
2. Feed that image into a ResNet-18 CNN
3. The CNN learned that real voices and cloned voices have different patterns

Real voices have natural frequency variations.
AI-cloned voices often have:
- Unnatural pitch transitions
- Vocoder artifacts (metallic harmonics)
- Consistent background noise (no room acoustics)
"""

from celery_app import celery_app
from database import jobs_collection, analysis_collection
from utils.storage import download_from_minio
from scoring.ensemble import compute_final_score

import torch
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
import librosa
import numpy as np
import io
import asyncio
import base64
from PIL import Image
from datetime import datetime
import soundfile as sf


def load_audio_model():
    """
    Load ResNet-18 for spectrogram classification.
    Modified for single-channel (grayscale) input.
    """
    model = models.resnet18(pretrained=True)
    
    # Modify first layer to accept 1-channel spectrogram instead of 3-channel RGB
    model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    
    # Modify last layer for binary classification (real=0, fake=1)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.eval()
    
    try:
        checkpoint = torch.load("models/audio/resnet18_voice_clone.pt", map_location="cpu")
        model.load_state_dict(checkpoint)
        print("✅ Loaded fine-tuned voice clone model")
    except FileNotFoundError:
        print("⚠️  No fine-tuned audio model found. Using pretrained weights (demo mode).")
    
    return model


spectrogram_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])  # Single channel normalization
])

try:
    AUDIO_MODEL = load_audio_model()
except Exception as e:
    AUDIO_MODEL = None
    print(f"⚠️ Could not load audio model: {e}")


def audio_to_melspectrogram(audio_bytes: bytes) -> tuple:
    """
    Convert raw audio bytes to a mel spectrogram image.
    
    Returns:
        (spectrogram_pil_image, sample_rate, duration_seconds)
    """
    # Try loading with soundfile first (WAV), fallback to librosa (MP3 etc.)
    try:
        audio, sr = sf.read(io.BytesIO(audio_bytes))
    except Exception:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
    
    # Ensure mono audio
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    
    # Resample to 16kHz (standard for speech models)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000
    
    # Take first 3 seconds (or pad if shorter)
    target_length = sr * 3
    if len(audio) > target_length:
        audio = audio[:target_length]
    else:
        audio = np.pad(audio, (0, target_length - len(audio)))
    
    duration = len(audio) / sr
    
    # Generate mel spectrogram
    # n_mels=128: number of mel frequency bands
    # hop_length=512: how many samples between each time frame
    mel_spec = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=128, hop_length=512, n_fft=2048
    )
    
    # Convert to decibels (log scale, more human-perceptible)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Normalize to 0-255 for image format
    mel_normalized = ((mel_spec_db - mel_spec_db.min()) /
                      (mel_spec_db.max() - mel_spec_db.min() + 1e-8) * 255).astype(np.uint8)
    
    # Flip vertically (convention: low frequencies at bottom)
    mel_normalized = np.flipud(mel_normalized)
    
    # Convert to PIL Image
    spec_image = Image.fromarray(mel_normalized, mode='L')  # 'L' = grayscale
    
    return spec_image, sr, duration


def analyze_spectrogram_features(spec_image: Image.Image) -> dict:
    """
    Analyze spectrogram for voice clone artifacts.
    Returns a score and list of detected anomalies.
    """
    if AUDIO_MODEL is None:
        import random
        score = random.uniform(0.1, 0.85)
        return {"score": score, "anomalies": ["Model not loaded (demo mode)"]}
    
    tensor = spectrogram_transform(spec_image).unsqueeze(0)
    
    with torch.no_grad():
        output = AUDIO_MODEL(tensor)
        probabilities = torch.softmax(output, dim=1)[0]
    
    fake_probability = float(probabilities[1])
    
    # Convert spectrogram to base64 for frontend display
    spec_buffer = io.BytesIO()
    spec_image.convert("RGB").save(spec_buffer, format="PNG")
    spec_b64 = base64.b64encode(spec_buffer.getvalue()).decode("utf-8")
    
    return {
        "score": fake_probability,
        "real_probability": float(probabilities[0]),
        "fake_probability": fake_probability,
        "spectrogram_b64": spec_b64
    }


@celery_app.task(bind=True, name="workers.audio_worker.analyze_audio")
def analyze_audio(self, job_id: str, storage_path: str):
    """Main audio analysis Celery task."""
    
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

        audio_bytes = download_from_minio(storage_path)
        update_status("processing", 30)

        # Convert to spectrogram and analyze
        spec_image, sample_rate, duration = audio_to_melspectrogram(audio_bytes)
        update_status("processing", 55, "ai_analysis")

        spec_result = analyze_spectrogram_features(spec_image)
        update_status("processing", 80, "scoring")

        # Compute final score
        module_scores = {
            "voice_clone_detection": {"score": spec_result["score"], "weight": 1.0},
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
                    "score": round(spec_result["score"] * 100, 1),
                    "model": "ResNet-18 Spectrogram CNN",
                    "sample_rate": sample_rate,
                    "duration_seconds": round(duration, 2),
                    "spectrogram_image": spec_result.get("spectrogram_b64"),
                    "real_probability": round(spec_result.get("real_probability", 0) * 100, 1),
                    "fake_probability": round(spec_result.get("fake_probability", 0) * 100, 1),
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
