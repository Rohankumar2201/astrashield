"""
api/upload.py — File upload endpoint.

This is the first step: the user picks a file on the website,
it gets uploaded here, validated, saved to MinIO storage,
and a background analysis job is created.

Returns a job_id immediately so the frontend can track progress.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid
import os

from database import get_db, jobs_collection
from models import Case
from utils.file_validator import validate_file
from utils.storage import upload_to_minio
from workers.image_worker import analyze_image
from workers.audio_worker import analyze_audio
from workers.document_worker import analyze_document

router = APIRouter()

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024  # Convert MB to bytes

# Allowed file types and which detection module to use
ALLOWED_TYPES = {
    "image/jpeg":  "image",
    "image/png":   "image",
    "image/webp":  "image",
    "audio/mpeg":  "audio",    # MP3
    "audio/wav":   "audio",
    "audio/x-wav": "audio",
    "audio/mp4":   "audio",    # M4A
    "application/pdf": "document",
}


class UploadResponse(BaseModel):
    job_id: str
    filename: str
    file_type: str
    status: str
    message: str


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    notes: str = "",
):    
    """
    Upload a media file for fraud analysis.
    
    Accepts: JPEG, PNG, WEBP images | MP3, WAV, M4A audio | PDF documents
    Max size: 50MB
    Returns: A job_id you can use to track the analysis progress
    """

    # ── Step 1: Read the file contents ────────────────────────────────────────
    contents = await file.read()

    # ── Step 2: Check file size ────────────────────────────────────────────────
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {os.getenv('MAX_FILE_SIZE_MB', 50)}MB"
        )

    # ── Step 3: Validate the file type ────────────────────────────────────────
    # We check the actual file contents, not just the extension
    # (a hacker could rename a .exe to .jpg)
    detected_mime = validate_file(contents, file.filename)
    if detected_mime not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {detected_mime}. Allowed: JPEG, PNG, WEBP, MP3, WAV, M4A, PDF"
        )

    media_type = ALLOWED_TYPES[detected_mime]  # "image", "audio", or "document"

    # ── Step 4: Generate a unique job ID ──────────────────────────────────────
    job_id = f"astra_{str(uuid.uuid4())[:8]}"

    # ── Step 5: Save file to MinIO storage ────────────────────────────────────
    storage_path = f"{job_id}/{file.filename}"
    try:
        await upload_to_minio(contents, storage_path, detected_mime)
    except Exception as e:
        # If MinIO isn't running, save to local disk as fallback
        os.makedirs(f"uploads/{job_id}", exist_ok=True)
        with open(f"uploads/{job_id}/{file.filename}", "wb") as f_out:
            f_out.write(contents)

    # PostgreSQL disabled for deployment - using MongoDB only
    pass

    # ── Step 7: Create job status in MongoDB ──────────────────────────────────
    await jobs_collection.insert_one({
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "progress": 0,
        "steps": {
            "upload": "completed",
            "preprocessing": "pending",
            "ai_analysis": "pending",
            "scoring": "pending",
            "report": "pending"
        }
    })

    # ── Step 8: Dispatch the appropriate background task ──────────────────────
    # .delay() sends the task to Celery — it runs in the background
    if media_type == "image":
        analyze_image.delay(job_id, storage_path, detected_mime)
    elif media_type == "audio":
        analyze_audio.delay(job_id, storage_path)
    elif media_type == "document":
        analyze_document.delay(job_id, storage_path)

    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        file_type=media_type,
        status="queued",
        message="File uploaded successfully. Analysis starting..."
    )
