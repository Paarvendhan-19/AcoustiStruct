from typing import Optional, List, Any
from datetime import datetime
from pydantic import Field

from app.schemas.base import BaseSchema

class FormFieldSchema(BaseSchema):
    id: str
    field_key: str
    label: str
    label_local: Optional[str] = None
    field_type: str
    required: bool = False
    risk_level: str = "low"
    sort_order: int = 0
    description: Optional[str] = None
    description_local: Optional[str] = None
    unit: Optional[str] = None
    enum_values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[str] = None

class FormSchema(BaseSchema):
    id: str
    name: str
    slug: str
    domain: str
    description: Optional[str] = None
    version: int
    language: str
    is_active: bool
    document_template: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    fields: List[FormFieldSchema] = []
