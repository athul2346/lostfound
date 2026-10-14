import uuid
from datetime import date, datetime

from sqlalchemy import String, Text, Float, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    custom_category: Mapped[str | None] = mapped_column(String(100))

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location_text: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    finder_email: Mapped[str] = mapped_column(String(255), nullable=False)
    finder_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    item_date: Mapped[date | None] = mapped_column(Date)
    reply_to_customer: Mapped[str | None] = mapped_column(Text)
    holding_location: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(30), default="active")
    access_token: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid.uuid4, unique=True)
    photos: Mapped[list["ItemPhoto"]] = relationship(
        back_populates="item", cascade="all, delete-orphan", order_by="ItemPhoto.order_index"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    questions: Mapped[list["ItemQuestion"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )