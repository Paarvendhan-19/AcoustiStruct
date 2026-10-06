from typing import Optional, List, Any
from datetime import datetime

from app.schemas.base import BaseSchema

class EvidenceSpanSchema(BaseSchema):
    id: str
    extracted_field_id: str
    audio_id: Optional[str] = None
    transcript_segment_id: Optional[str] = None
    evidence_text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    span_type: str
    created_at: datetime

class ExtractedFieldSchema(BaseSchema):
    id: str
    session_id: str
    field_key: str
    value: Optional[str] = None
    value_normalized: Optional[str] = None
    value_type: str
    
    model_confidence: Optional[float] = None
    heuristic_confidence: Optional[float] = None
    validated_confidence: Optional[float] = None
    final_confidence: Optional[float] = None
    
    status: str
    is_verified: bool
    verification_source: Optional[str] = None
    certainty: str
    
    created_at: datetime
    updated_at: datetime
    evidence_spans: List[EvidenceSpanSchema] = []

class ExtractedFieldUpdate(BaseSchema):
    value: Optional[str] = None
    is_verified: bool = True
    status: str = "user_corrected"
