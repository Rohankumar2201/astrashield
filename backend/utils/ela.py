"""
utils/ela.py — Error Level Analysis (ELA) for image tampering detection.

ELA is a classical forensic technique that works like this:
1. Take the original image
2. Re-save it as JPEG at a known compression level (e.g., quality=90)
3. Calculate the pixel-by-pixel difference between original and re-saved
4. High-difference areas = recently edited (brighter in the ELA map)

In a real unedited photo, compression errors are uniform.
In an edited photo, copy-pasted regions look different because they were
compressed a different number of times.
"""

import numpy as np
from PIL import Image
import io
import base64


def compute_ela(image_bytes: bytes, quality: int = 90) -> dict:
    """
    Compute Error Level Analysis on an image.
    
    Args:
        image_bytes: Raw image bytes
        quality: JPEG re-save quality (90 is standard for ELA)
    
    Returns:
        {
            "score": 0.0-1.0,        # Higher = more suspicious
            "ela_image_b64": "...",  # Base64 ELA map to display in frontend
            "max_diff": ...,         # Maximum pixel difference found
            "mean_diff": ...,        # Average pixel difference
        }
    """
    try:
        # Open the original image
        original = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Re-save at controlled quality to get "what it should look like"
        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer).convert("RGB")

        # Convert both to numpy arrays for math operations
        orig_array = np.array(original, dtype=np.float64)
        resaved_array = np.array(resaved, dtype=np.float64)

        # Calculate absolute difference (amplified for visibility)
        diff = np.abs(orig_array - resaved_array) * 10  # ×10 to make differences visible
        diff = np.clip(diff, 0, 255).astype(np.uint8)

        # Calculate statistics
        max_diff = float(np.max(diff))
        mean_diff = float(np.mean(diff))

        # Score: normalize mean difference to 0-1
        # Typical unedited images have mean_diff < 5
        # Heavily edited images can have mean_diff > 30
        score = min(mean_diff / 30.0, 1.0)

        # Convert ELA map to base64 for sending to frontend
        ela_image = Image.fromarray(diff)
        ela_buffer = io.BytesIO()
        ela_image.save(ela_buffer, format="PNG")
        ela_b64 = base64.b64encode(ela_buffer.getvalue()).decode("utf-8")

        return {
            "score": round(score, 3),
            "ela_image_b64": ela_b64,
            "max_diff": round(max_diff, 2),
            "mean_diff": round(mean_diff, 2),
            "interpretation": (
                "Low tampering" if score < 0.3
                else "Moderate tampering" if score < 0.6
                else "High tampering detected"
            )
        }

    except Exception as e:
        return {
            "score": 0.0,
            "ela_image_b64": None,
            "error": str(e)
        }
