"""Confidence engine — calculates realistic confidence scores for extracted fields.

Combines model confidence, heuristic checks (e.g. ASR confidence), and validation results.
"""

from __future__ import annotations

from typing import Any


def calculate_field_confidence(
    model_confidence: float | None,
    asr_confidence: float | None,
    certainty: str,
    is_valid: bool,
    risk_level: str = "medium",
) -> dict[str, float | str]:
    """Calculate combined confidence and determine review status."""
    
    # Base confidence is from the model, fallback to heuristic if missing
    base = model_confidence if model_confidence is not None else 0.8
    
    # Penalize if ASR confidence is low
    if asr_confidence is not None and asr_confidence < 0.7:
        base *= (asr_confidence + 0.3)
        
    # Penalize based on certainty markers
    if certainty == "uncertain":
        base *= 0.6
    elif certainty == "approximate":
        base *= 0.8
    elif certainty == "inferred":
        base *= 0.7
        
    # Zero out if invalid (shouldn't be trusted at all)
    if not is_valid:
        base = 0.0
        
    final_confidence = min(1.0, max(0.0, base))
    
    # Determine status based on risk level and final confidence
    thresholds = {
        "low": 0.6,
        "medium": 0.8,
        "high": 0.9,
        "critical": 0.98,
    }
    
    threshold = thresholds.get(risk_level, 0.8)
    
    if not is_valid:
        status = "needs_review"
    elif final_confidence >= threshold:
        status = "ai_extracted"
    else:
        status = "needs_review"
        
    return {
        "heuristic_confidence": asr_confidence,
        "final_confidence": round(final_confidence, 2),
        "status": status,
    }
