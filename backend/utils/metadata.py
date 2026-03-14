"""
utils/metadata.py — Extracts and analyzes EXIF metadata from files.

EXIF = Exchangeable Image File Format
Every photo taken by a camera contains hidden metadata like:
- Camera make/model
- GPS coordinates
- Date/time taken
- Software used to edit

AI-generated images often have NO metadata (suspicious!) or contain
signatures from AI tools like Stable Diffusion.
"""

import exifread
import io
from datetime import datetime


# Known AI generation software signatures found in metadata
AI_SOFTWARE_SIGNATURES = [
    "stable diffusion", "midjourney", "dall-e", "dall·e",
    "generative", "ai generated", "artificial intelligence",
    "runway", "adobe firefly", "deepfake", "faceswap",
    "deepfaclab", "reface", "wombo"
]


def extract_metadata(file_bytes: bytes) -> dict:
    """
    Extract EXIF metadata from an image file.
    
    Returns:
        A dict with all metadata fields, or empty dict if none found.
    """
    try:
        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)
        # Convert exifread Tag objects to plain strings
        return {str(k): str(v) for k, v in tags.items()}
    except Exception:
        return {}


def analyze_metadata(file_bytes: bytes) -> dict:
    """
    Analyze metadata for fraud indicators.
    
    Returns:
        {
            "score": 0.0-1.0,          # 1.0 = definitely suspicious
            "flags": [...],             # List of suspicious findings
            "metadata": {...}           # Raw metadata
        }
    """
    metadata = extract_metadata(file_bytes)
    flags = []
    suspicion_score = 0.0

    # ── Check 1: No metadata at all ──────────────────────────────────────────
    # Real photos from cameras always have EXIF data.
    # AI-generated images typically have none.
    if not metadata:
        flags.append("No EXIF metadata found — typical of AI-generated images")
        suspicion_score += 0.35

    else:
        # ── Check 2: AI software signatures ──────────────────────────────────
        # Check if any metadata field mentions known AI tools
        metadata_text = " ".join(str(v) for v in metadata.values()).lower()
        for sig in AI_SOFTWARE_SIGNATURES:
            if sig in metadata_text:
                flags.append(f"AI software signature detected: '{sig}'")
                suspicion_score += 0.5
                break

        # ── Check 3: Missing camera info ─────────────────────────────────────
        has_camera = any("Make" in k or "Model" in k for k in metadata.keys())
        if not has_camera:
            flags.append("No camera make/model in metadata")
            suspicion_score += 0.15

        # ── Check 4: Suspicious creation date ────────────────────────────────
        date_keys = [k for k in metadata if "DateTime" in k]
        if date_keys:
            date_str = str(metadata[date_keys[0]])
            try:
                # Format: "2024:01:15 10:30:00"
                photo_date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                # Flag if date is in the future (impossible for real photos)
                if photo_date > datetime.now():
                    flags.append(f"Metadata date is in the future: {date_str}")
                    suspicion_score += 0.3
            except ValueError:
                flags.append("Malformed date in metadata")
                suspicion_score += 0.1

    # Cap score at 1.0
    suspicion_score = min(suspicion_score, 1.0)

    return {
        "score": round(suspicion_score, 3),
        "flags": flags,
        "metadata_fields_count": len(metadata),
        "metadata": metadata
    }
