"""Audio record model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class AudioRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An audio recording associated with a session."""
    __tablename__ = "audio_records"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="audio/webm")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")  # uploaded|processing|processed|failed
    language: Mapped[str] = mapped_column(String(10), default="ta")
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="audio_records")  # noqa: F821
