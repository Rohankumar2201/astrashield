"""
api/upload.py — File upload endpoint (deployment version, no PostgreSQL)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import os

from database import jobs_collection
from utils.file_validator import validate_file
from workers.image_worker import analyze_image
from workers.audio_worker import analyze_audio
from workers.document_worker import analyze_document

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024

ALLOWED_TYPES = {
    "image/jpeg":  "image",
    "image/png":   "image",
    "image/webp":  "image",
    "audio/mpeg":  "audio",
    "audio/wav":   "audio",
    "audio/x-wav": "audio",
    "audio/mp4":   "audio",
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
    # Read file
    contents = await file.read()

    # Check size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")

    # Validate file type
    detected_mime = validate_file(contents, file.filename)
    if detected_mime not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed: JPEG, PNG, WEBP, MP3, WAV, M4A, PDF"
        )

    media_type = ALLOWED_TYPES[detected_mime]

    # Generate job ID
    job_id = f"astra_{str(uuid.uuid4())[:8]}"

    # Save file locally
    os.makedirs(f"uploads/{job_id}", exist_ok=True)
    file_path = f"uploads/{job_id}/{file.filename}"
    with open(file_path, "wb") as f_out:
        f_out.write(contents)

    # Create job status in MongoDB
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

    # Dispatch background task
    if media_type == "image":
        analyze_image.delay(job_id, file_path, detected_mime)
    elif media_type == "audio":
        analyze_audio.delay(job_id, file_path)
    elif media_type == "document":
        analyze_document.delay(job_id, file_path)

    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        file_type=media_type,
        status="queued",
        message="File uploaded successfully. Analysis starting..."
    )