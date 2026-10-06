"""Form and FormField models — schema-driven form engine."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Form(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A configurable form definition (e.g. 'Agriculture Assessment')."""
    __tablename__ = "forms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)  # agriculture, health, etc.
    description: Mapped[str] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    language: Mapped[str] = mapped_column(String(10), default="ta")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    document_template: Mapped[str] = mapped_column(String(255), nullable=True)

    fields: Mapped[list["FormField"]] = relationship(
        back_populates="form", order_by="FormField.sort_order"
    )


class FormField(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single field definition within a form."""
    __tablename__ = "form_fields"

    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. farmer_name
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    label_local: Mapped[str] = mapped_column(String(255), nullable=True)  # Tamil label
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)  # string|integer|float|boolean|date|datetime|enum|multiselect|location|long_text
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low|medium|high|critical
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    description_local: Mapped[str] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=True)  # acre, hectare, kg, etc.
    enum_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # ["rice","wheat",...]
    min_value: Mapped[float | None] = mapped_column(nullable=True)
    max_value: Mapped[float | None] = mapped_column(nullable=True)
    default_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    form: Mapped["Form"] = relationship(back_populates="fields")
