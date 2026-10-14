import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class ItemQuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=3, max_length=300)


class ItemQuestionOut(BaseModel):
    id: uuid.UUID
    question_text: str
    order_index: int

    class Config:
        from_attributes = True


class ItemPhotoOut(BaseModel):
    id: uuid.UUID
    url: str
    order_index: int

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    category_id: int | None = None
    custom_category: str | None = Field(None, max_length=100)
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    location_text: str = Field(..., min_length=2)
    latitude: float | None = None
    longitude: float | None = None
    item_date: date | None = None
    reply_to_customer: str | None = None
    holding_location: str | None = None
    finder_email: EmailStr
    finder_phone: str = Field(..., min_length=7, max_length=20)
    questions: list[ItemQuestionCreate] = Field(default_factory=list, max_length=2)


class ItemOut(BaseModel):
    id: uuid.UUID
    category_id: int | None
    custom_category: str | None
    title: str
    description: str
    location_text: str
    latitude: float | None
    longitude: float | None
    item_date: date | None = None
    reply_to_customer: str | None = None
    holding_location: str | None = None
    status: str
    created_at: datetime
    questions: list[ItemQuestionOut] = []
    photos: list[ItemPhotoOut] = []

    class Config:
        from_attributes = True


class ItemCreatedOut(ItemOut):
    access_token: uuid.UUID