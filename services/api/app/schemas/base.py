from typing import TypeVar, Generic
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PaginatedResponse(BaseSchema, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
