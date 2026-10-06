"""Transcript and TranscriptSegment models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Float, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Transcript(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Full transcript for a session/audio."""
    __tablename__ = "transcripts"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False)
    audio_id: Mapped[str] = mapped_column(String(36), ForeignKey("audio_records.id"), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ta")
    full_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Provider metadata
    asr_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    asr_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    asr_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="transcripts")  # noqa: F821
    segments: Mapped[list["TranscriptSegment"]] = relationship(back_populates="transcript")


class TranscriptSegment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A time-aligned segment within a transcript."""
    __tablename__ = "transcript_segments"

    transcript_id: Mapped[str] = mapped_column(String(36), ForeignKey("transcripts.id"), nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    speaker: Mapped[str | None] = mapped_column(String(100), nullable=True)

    transcript: Mapped["Transcript"] = relationship(back_populates="segments")
