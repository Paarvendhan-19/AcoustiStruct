"""Session model — represents one data-capture session."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin

# Valid state transitions enforced in service layer
SESSION_STATES = [
    "created",
    "recording",
    "uploaded",
    "transcribing",
    "transcribed",
    "extracting",
    "extracted",
    "validating",
    "needs_clarification",
    "under_review",
    "verified",
    "generating_document",
    "completed",
    "failed",
]

VALID_TRANSITIONS = {
    "created": ["recording", "uploaded", "failed"],
    "recording": ["uploaded", "failed"],
    "uploaded": ["transcribing", "failed"],
    "transcribing": ["transcribed", "failed"],
    "transcribed": ["extracting", "failed"],
    "extracting": ["extracted", "failed"],
    "extracted": ["validating", "failed"],
    "validating": ["needs_clarification", "under_review", "failed"],
    "needs_clarification": ["validating", "under_review", "failed"],
    "under_review": ["verified", "needs_clarification", "failed"],
    "verified": ["generating_document", "failed"],
    "generating_document": ["completed", "failed"],
    "completed": [],  # terminal
    "failed": ["created", "uploaded", "transcribing"],  # allow retry
}


class Session(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single data-capture session from start to document generation."""
    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ta")
    dialect: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dialect_confidence: Mapped[float | None] = mapped_column(nullable=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")  # noqa: F821
    form: Mapped["Form"] = relationship()  # noqa: F821
    audio_records: Mapped[list["AudioRecord"]] = relationship(back_populates="session")  # noqa: F821
    transcripts: Mapped[list["Transcript"]] = relationship(back_populates="session")  # noqa: F821
    extracted_fields: Mapped[list["ExtractedField"]] = relationship(back_populates="session")  # noqa: F821
    clarification_requests: Mapped[list["ClarificationRequest"]] = relationship(back_populates="session")  # noqa: F821
    documents: Mapped[list["Document"]] = relationship(back_populates="session")  # noqa: F821

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in VALID_TRANSITIONS.get(self.status, [])
