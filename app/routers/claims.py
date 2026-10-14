import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.auth import get_claim_by_token
from app.models.item import Item
from app.models.claim import Claim, ClaimAnswer
from app.schemas.claim import ClaimCreate, ClaimOut
from app.services.email import send_claim_verification_email, send_new_claim_notification

router = APIRouter(tags=["claims"])


@router.post(
    "/items/{item_id}/claims",
    response_model=ClaimOut,
    status_code=status.HTTP_201_CREATED,
)
async def submit_claim(
    item_id: uuid.UUID,
    payload: ClaimCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Item).where(Item.id == item_id).options(selectinload(Item.questions))
    )
    item = result.scalar_one_or_none()

    if item is None or not item.email_verified:
        raise HTTPException(404, "Item not found")
    if item.status not in ("active", "claim_pending"):
        raise HTTPException(400, "This item is no longer accepting claims")

    valid_ids = {q.id for q in item.questions}
    for ans in payload.answers:
        if ans.question_id not in valid_ids:
            raise HTTPException(400, "Answer refers to a question that doesn't belong to this item")

    claim = Claim(
        item_id=item.id,
        claimant_email=payload.claimant_email,
        claimant_phone=payload.claimant_phone,
        additional_proof=payload.additional_proof,
    )
    claim.answers = [
        ClaimAnswer(question_id=a.question_id, answer_text=a.answer_text)
        for a in payload.answers
    ]

    db.add(claim)
    await db.commit()

    background_tasks.add_task(
        send_claim_verification_email, claim.claimant_email, claim.id, claim.access_token
    )
    return claim


@router.get("/claims/{claim_id}/verify")
async def verify_claim_email(
    claim_id: uuid.UUID,
    token: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    claim = await get_claim_by_token(claim_id, token, db)

    if claim.email_verified:
        return {"detail": "Claim already verified."}

    claim.email_verified = True

    result = await db.execute(select(Item).where(Item.id == claim.item_id))
    item = result.scalar_one()
    if item.status == "active":
        item.status = "claim_pending"

    await db.commit()

    # Finder is only notified after the claimant's email is confirmed,
    # so fake or typo'd claims never reach them.
    background_tasks.add_task(
        send_new_claim_notification, item.finder_email, item.id, item.access_token, item.title
    )
    return {"detail": "Claim verified. The finder has been notified."}