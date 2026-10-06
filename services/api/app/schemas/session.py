from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from app.schemas.base import BaseSchema

class SessionCreate(BaseSchema):
    form_id: str
    organization_id: str
    title: Optional[str] = None
    language: str = "ta"

class SessionSchema(BaseSchema):
    id: str
    user_id: str
    form_id: str
    organization_id: str
    status: str
    language: str
    dialect: Optional[str] = None
    dialect_confidence: Optional[float] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
class SessionStatusUpdate(BaseSchema):
    status: str
