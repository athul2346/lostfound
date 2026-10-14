import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.item import Item
from app.models.claim import Claim


async def get_item_by_token(
    item_id: uuid.UUID,
    token: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None or item.access_token != token:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid or expired link")

    return item


async def get_claim_by_token(
    claim_id: uuid.UUID,
    token: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Claim:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()

    if claim is None or claim.access_token != token:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid or expired link")

    return claim