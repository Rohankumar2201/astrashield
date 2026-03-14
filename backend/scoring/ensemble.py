"""
scoring/ensemble.py — The Fraud Risk Scoring Engine.

This is the "judge" of AstraShield. It takes scores from all the
detection modules and combines them into one final Fraud Risk Score (0-100).

How it works:
1. Each module returns a score between 0.0 and 1.0
2. We multiply each score by its weight (importance)
3. We add them all up → weighted average
4. We apply Platt Scaling to calibrate the probability
5. We multiply by 100 → final score 0-100
6. We categorize: LOW / MEDIUM / HIGH / CRITICAL

Example:
  image_deepfake score=0.85, weight=0.45
  ela_analysis   score=0.60, weight=0.25
  metadata       score=0.70, weight=0.30

  weighted = (0.85×0.45) + (0.60×0.25) + (0.70×0.30)
           = 0.3825 + 0.15 + 0.21
           = 0.7425  →  fraud_risk_score = 74
"""

import numpy as np
from sklearn.calibration import CalibratedClassifierCV


# ── Risk Thresholds ────────────────────────────────────────────────────────────
# These define what score range maps to which risk category
RISK_THRESHOLDS = {
    "LOW":      (0,  30),
    "MEDIUM":   (31, 60),
    "HIGH":     (61, 85),
    "CRITICAL": (86, 100),
}

# Recommendation text for each risk category
RECOMMENDATIONS = {
    "LOW": (
        "Content appears authentic. No significant AI manipulation detected. "
        "Exercise standard due diligence."
    ),
    "MEDIUM": (
        "Some suspicious indicators detected. Manual review recommended before "
        "using this content as evidence or identity verification."
    ),
    "HIGH": (
        "Strong indicators of AI manipulation detected. Do NOT use as authentic "
        "media. Escalate to a senior analyst for review."
    ),
    "CRITICAL": (
        "HIGH CONFIDENCE AI GENERATION OR MANIPULATION DETECTED. "
        "This content is almost certainly synthetic. Do not use as authentic media. "
        "Report to relevant authorities if used for fraud."
    ),
}


def platt_scaling(raw_score: float, a: float = -2.5, b: float = 1.2) -> float:
    """
    Apply Platt Scaling to calibrate a raw probability score.
    
    Platt Scaling applies a sigmoid function to convert an uncalibrated
    model output into a well-calibrated probability.
    
    The formula: P = 1 / (1 + exp(a * score + b))
    
    We tweak 'a' and 'b' so that:
    - Very low raw scores map to near 0
    - Very high raw scores map to near 1
    - Middle scores are appropriately spread out
    
    In production: fit a and b on a validation set.
    For now: these default values work reasonably well.
    """
    calibrated = 1.0 / (1.0 + np.exp(a * raw_score + b))
    return float(np.clip(calibrated, 0.0, 1.0))


def compute_final_score(module_scores: dict) -> dict:
    """
    Compute the final Fraud Risk Score from all module outputs.
    
    Args:
        module_scores: Dict of {module_name: {"score": 0.0-1.0, "weight": 0.0-1.0}}
        
        Example:
        {
            "image_deepfake": {"score": 0.85, "weight": 0.45},
            "ela_analysis":   {"score": 0.60, "weight": 0.25},
            "metadata":       {"score": 0.70, "weight": 0.30},
        }
    
    Returns:
        {
            "fraud_risk_score": 74,         # 0-100
            "raw_score": 0.7425,            # Pre-calibration weighted average
            "calibrated_score": 0.74,       # After Platt Scaling
            "risk_category": "HIGH",        # LOW/MEDIUM/HIGH/CRITICAL
            "recommendation": "...",        # Human-readable advice
            "module_breakdown": {...}       # Per-module contribution
        }
    """
    if not module_scores:
        return {
            "fraud_risk_score": 0,
            "risk_category": "LOW",
            "recommendation": RECOMMENDATIONS["LOW"],
            "raw_score": 0.0,
            "calibrated_score": 0.0,
        }

    # ── Step 1: Normalize weights so they sum to 1.0 ─────────────────────────
    total_weight = sum(m["weight"] for m in module_scores.values())
    normalized = {
        name: {
            "score": m["score"],
            "weight": m["weight"] / total_weight,  # Normalize
        }
        for name, m in module_scores.items()
    }

    # ── Step 2: Compute weighted average ──────────────────────────────────────
    raw_score = sum(
        m["score"] * m["weight"]
        for m in normalized.values()
    )

    # ── Step 3: Apply Platt Scaling calibration ────────────────────────────────
    calibrated_score = platt_scaling(raw_score)

    # ── Step 4: Convert to 0-100 integer ──────────────────────────────────────
    fraud_risk_score = int(round(calibrated_score * 100))

    # ── Step 5: Categorize risk ────────────────────────────────────────────────
    risk_category = "LOW"
    for category, (low, high) in RISK_THRESHOLDS.items():
        if low <= fraud_risk_score <= high:
            risk_category = category
            break

    # ── Step 6: Build per-module breakdown ────────────────────────────────────
    module_breakdown = {
        name: {
            "raw_score": round(m["score"], 3),
            "weight": round(m["weight"], 3),
            "contribution": round(m["score"] * m["weight"], 3),
            "score_pct": round(m["score"] * 100, 1),
        }
        for name, m in normalized.items()
    }

    return {
        "fraud_risk_score": fraud_risk_score,
        "raw_score": round(raw_score, 4),
        "calibrated_score": round(calibrated_score, 4),
        "risk_category": risk_category,
        "recommendation": RECOMMENDATIONS[risk_category],
        "module_breakdown": module_breakdown,
    }


def get_risk_color(risk_category: str) -> str:
    """Return a hex color code for the risk category."""
    colors = {
        "LOW":      "#22c55e",   # Green
        "MEDIUM":   "#eab308",   # Yellow
        "HIGH":     "#f97316",   # Orange
        "CRITICAL": "#ef4444",   # Red
    }
    return colors.get(risk_category, "#6b7280")
