"""Document model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A generated document (PDF/DOCX) from verified session data."""
    __tablename__ = "documents"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf | docx
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    # draft | ai_extracted | user_verified | final
    verification_status: Mapped[str] = mapped_column(String(50), default="unverified")
    content_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Frozen data at generation time
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="documents")  # noqa: F821
