import uuid
from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))

    claimant_email: Mapped[str] = mapped_column(String(255), nullable=False)
    claimant_phone: Mapped[str | None] = mapped_column(String(30))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    access_token: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid.uuid4, unique=True)

    additional_proof: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending | accepted | rejected
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    answers: Mapped[list["ClaimAnswer"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )


class ClaimAnswer(Base):
    __tablename__ = "claim_answers"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("item_questions.id"))
    answer_text: Mapped[str | None] = mapped_column(Text)  # null = skipped

    claim: Mapped["Claim"] = relationship(back_populates="answers")