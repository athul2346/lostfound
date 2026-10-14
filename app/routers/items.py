import uuid
from pathlib import Path

from fastapi import (
    APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db import get_db
from app.core.auth import get_item_by_token
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.models.item_question import ItemQuestion
from app.schemas.item import ItemCreate, ItemOut, ItemCreatedOut, ItemPhotoOut
from app.services.email import send_item_verification_email

router = APIRouter(prefix="/items", tags=["items"])

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


@router.post("", response_model=ItemCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if not payload.category_id and not payload.custom_category:
        raise HTTPException(400, "Provide either category_id or custom_category")

    item = Item(
        category_id=payload.category_id,
        custom_category=payload.custom_category,
        title=payload.title,
        description=payload.description,
        location_text=payload.location_text,
        latitude=payload.latitude,
        longitude=payload.longitude,
        finder_email=payload.finder_email,
        finder_phone=payload.finder_phone,
        item_date=payload.item_date,
        reply_to_customer=payload.reply_to_customer,
        holding_location=payload.holding_location,
    )
    item.questions = [
        ItemQuestion(question_text=q.question_text, order_index=i)
        for i, q in enumerate(payload.questions)
    ]

    db.add(item)
    await db.commit()
    await db.refresh(item, attribute_names=["questions", "photos"])

    background_tasks.add_task(
        send_item_verification_email, item.finder_email, item.id, item.access_token
    )
    return item


@router.post("/{item_id}/photos", response_model=ItemPhotoOut, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    item: Item = Depends(get_item_by_token),  # needs ?token= (finder only)
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only JPEG, PNG or WEBP images are allowed")

    count = await db.scalar(
        select(func.count()).select_from(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )
    if count >= settings.MAX_PHOTOS_PER_ITEM:
        raise HTTPException(400, f"Maximum {settings.MAX_PHOTOS_PER_ITEM} photos per item")

    data = await file.read(settings.MAX_PHOTO_BYTES + 1)
    if len(data) > settings.MAX_PHOTO_BYTES:
        raise HTTPException(400, "Photo too large (max 5 MB)")

    # Server-generated filename: never trust the client's filename
    filename = f"{uuid.uuid4()}{ALLOWED_TYPES[file.content_type]}"
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    (Path(settings.UPLOAD_DIR) / filename).write_bytes(data)

    photo = ItemPhoto(item_id=item.id, url=f"/uploads/{filename}", order_index=count)
    db.add(photo)
    await db.commit()
    return photo


@router.get("/{item_id}/verify")
async def verify_item_email(
    item_id: uuid.UUID,
    token: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_item_by_token(item_id, token, db)
    item.email_verified = True
    await db.commit()
    return {"detail": "Email verified. Your item is now live."}


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Item)
        .where(Item.id == item_id)
        .options(selectinload(Item.questions), selectinload(Item.photos))
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(404, "Item not found")
    return item