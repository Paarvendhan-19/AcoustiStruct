"""Clarification generator — creates targeted questions for uncertain fields.

This module determines WHEN to ask a question and WHAT to ask, based on
field schemas and confidence levels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai.extraction.extractor import ExtractedFieldResult


@dataclass
class ClarificationQuestion:
    field_key: str
    question_text: str
    question_text_local: str | None
    detected_value: str | None
    reason: str


def generate_clarification_questions(
    extracted_fields: list[ExtractedFieldResult],
    schema: list[dict],
    language: str = "ta"
) -> list[ClarificationQuestion]:
    """Generate clarification questions for uncertain or missing required fields."""
    
    schema_map = {f.get("field_key", f.get("id", "")): f for f in schema}
    questions = []
    
    for field in extracted_fields:
        field_def = schema_map.get(field.field_key)
        if not field_def:
            continue
            
        label = field_def.get("label", field.field_key)
        label_local = field_def.get("label_local")
        
        # Scenario 1: Ambiguous or uncertain detection
        if field.status == "needs_review" and field.value is not None:
            q_en = f"I detected '{field.raw_value or field.value}' for {label}, but I'm not certain. Can you confirm or correct it?"
            
            # Simple localizations for demo
            q_local = None
            if language == "ta" and label_local:
                q_local = f"{label_local} '{field.raw_value or field.value}' என்று பதிவாகியுள்ளது, இது சரியா?"
                
            questions.append(ClarificationQuestion(
                field_key=field.field_key,
                question_text=q_en,
                question_text_local=q_local,
                detected_value=str(field.raw_value or field.value),
                reason="low_confidence",
            ))
            
        # Scenario 2: Missing required field
        elif field.status == "not_found" and field_def.get("required", False):
            q_en = f"I missed the information for {label}. Could you please provide it?"
            
            q_local = None
            if language == "ta" and label_local:
                q_local = f"{label_local} பற்றிய தகவல் இல்லை. தயவுசெய்து கூறவும்."
                
            questions.append(ClarificationQuestion(
                field_key=field.field_key,
                question_text=q_en,
                question_text_local=q_local,
                detected_value=None,
                reason="missing_required",
            ))
            
    return questions
