import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ClaimAnswerIn(BaseModel):
    question_id: uuid.UUID
    answer_text: str | None = None  # null or blank = skipped


class ClaimCreate(BaseModel):
    claimant_email: EmailStr
    claimant_phone: str | None = Field(None, max_length=20)
    additional_proof: str | None = Field(None, max_length=2000)
    answers: list[ClaimAnswerIn] = Field(default_factory=list)


class ClaimOut(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True