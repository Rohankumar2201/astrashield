"""
utils/storage.py — File storage using MinIO.

MinIO is like a self-hosted version of Amazon S3.
It stores uploaded files as "objects" in "buckets" (like folders).
"""

from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import io
import os

load_dotenv()

# Create the MinIO client (connection to the storage server)
minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
)

BUCKET_NAME = os.getenv("MINIO_BUCKET", "astrashield-uploads")


def ensure_bucket_exists():
    """Create the storage bucket if it doesn't exist yet."""
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
            print(f"✅ Created MinIO bucket: {BUCKET_NAME}")
    except S3Error as e:
        print(f"⚠️ MinIO bucket error: {e}")


async def upload_to_minio(contents: bytes, object_path: str, content_type: str) -> str:
    """
    Upload file bytes to MinIO storage.
    
    Args:
        contents: File bytes
        object_path: Where to store it, e.g. "job_abc123/photo.jpg"
        content_type: MIME type, e.g. "image/jpeg"
    
    Returns:
        The storage path (use this to retrieve the file later)
    """
    ensure_bucket_exists()
    
    # Wrap bytes in a file-like object that MinIO can read
    data = io.BytesIO(contents)
    
    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_path,
        data=data,
        length=len(contents),
        content_type=content_type
    )
    
    return object_path


def download_from_minio(object_path: str) -> bytes:
    """
    Download a file from MinIO storage.
    
    Used by workers to retrieve the file for analysis.
    """
    try:
        response = minio_client.get_object(BUCKET_NAME, object_path)
        return response.read()
    except S3Error:
        # Fallback: try reading from local disk
        local_path = f"uploads/{object_path}"
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        raise FileNotFoundError(f"File not found in storage: {object_path}")
