"""Review router - spaced repetition review endpoints."""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_async_session
from app.schemas.review import ReviewCardOut, ReviewCardUpdate, ReviewStats
from app.services.review_service import (
    update_after_review,
    get_due_cards,
    get_review_stats,
)

router = APIRouter()


@router.get("/review/due", response_model=List[ReviewCardOut])
async def list_due_cards(
    course_id: str | None = Query(None),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_async_session),
):
    """Get cards due for review, optionally filtered by course."""
    course_uuid = uuid.UUID(course_id) if course_id else None
    cards = await get_due_cards(db, course_id=course_uuid, limit=limit)
    return [ReviewCardOut.model_validate(c) for c in cards]


@router.post("/review/{card_id}")
async def review_card(
    card_id: str,
    rating: str = Query(..., pattern="^(again|hard|good|easy)$"),
    db: AsyncSession = Depends(get_async_session),
):
    """Submit a review rating for a card."""
    try:
        result = await update_after_review(db, uuid.UUID(card_id), rating)
        await db.commit()
        return {"status": "ok", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/review/stats", response_model=ReviewStats)
async def review_stats(
    course_id: str | None = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    """Get review statistics."""
    course_uuid = uuid.UUID(course_id) if course_id else None
    stats = await get_review_stats(db, course_id=course_uuid)
    return ReviewStats(**stats)
