"""
utils/file_validator.py — Simple file validator without libmagic
"""

def validate_file(contents: bytes, filename: str) -> str:
    """Detect file type from extension — simplified for deployment."""
    ext = filename.lower().split(".")[-1]
    ext_map = {
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "png":  "image/png",
        "webp": "image/webp",
        "mp3":  "audio/mpeg",
        "wav":  "audio/wav",
        "m4a":  "audio/mp4",
        "pdf":  "application/pdf",
    }
    return ext_map.get(ext, "application/octet-stream")