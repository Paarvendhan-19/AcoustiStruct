"""Extraction, Evidence, Clarification, and Confidence models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Float, Text, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class ExtractedField(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single extracted field value from semantic processing."""
    __tablename__ = "extracted_fields"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_normalized: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(50), default="string")

    # Confidence
    model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    heuristic_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    validated_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="ai_extracted")
    # ai_extracted | needs_review | user_confirmed | user_corrected | clarified | not_found | rejected
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ai|user|clarification

    # Extraction metadata
    extraction_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    extraction_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Certainty from source
    certainty: Mapped[str] = mapped_column(String(50), default="explicit")
    # explicit | inferred | uncertain | approximate | negated

    session: Mapped["Session"] = relationship(back_populates="extracted_fields")  # noqa: F821
    evidence_spans: Mapped[list["EvidenceSpan"]] = relationship(back_populates="extracted_field")


class EvidenceSpan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Links an extracted field to its source in the transcript/audio."""
    __tablename__ = "evidence_spans"

    extracted_field_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("extracted_fields.id"), nullable=False
    )
    audio_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("audio_records.id"), nullable=True)
    transcript_segment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("transcript_segments.id"), nullable=True
    )

    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    span_type: Mapped[str] = mapped_column(String(50), default="transcript")  # transcript | audio | user_input

    extracted_field: Mapped["ExtractedField"] = relationship(back_populates="evidence_spans")


class ClarificationRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A clarification question generated for uncertain fields."""
    __tablename__ = "clarification_requests"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    extracted_field_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("extracted_fields.id"), nullable=True
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_text_local: Mapped[str | None] = mapped_column(Text, nullable=True)  # Question in user's language
    detected_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # pending | answered | skipped | expired

    session: Mapped["Session"] = relationship(back_populates="clarification_requests")  # noqa: F821
    responses: Mapped[list["ClarificationResponse"]] = relationship(back_populates="clarification_request")


class ClarificationResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User's response to a clarification question."""
    __tablename__ = "clarification_responses"

    clarification_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clarification_requests.id"), nullable=False
    )
    response_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # voice | text | selection | confirm | reject
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    clarification_request: Mapped["ClarificationRequest"] = relationship(back_populates="responses")
