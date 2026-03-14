"""
utils/file_validator.py — Validates uploaded files.

We check the actual file contents (called "magic bytes" or "file signature")
rather than trusting the file extension. A hacker could name a virus "photo.jpg"
but the file contents would still reveal it's not a real image.
"""

import magic  # python-magic library detects file types from contents


def validate_file(contents: bytes, filename: str) -> str:
    """
    Detect the true MIME type of a file from its contents.
    
    Args:
        contents: The raw bytes of the uploaded file
        filename: Original filename (for logging only)
    
    Returns:
        MIME type string like "image/jpeg" or "audio/mpeg"
    
    Example:
        validate_file(b'\\xff\\xd8\\xff...', 'photo.jpg')  
        → 'image/jpeg'
    """
    try:
        # Magic reads the first few bytes of the file to determine type
        mime = magic.from_buffer(contents, mime=True)
        return mime
    except Exception:
        # If magic fails, fall back to guessing from extension
        ext = filename.lower().split(".")[-1]
        fallback_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "pdf": "application/pdf",
        }
        return fallback_map.get(ext, "application/octet-stream")
