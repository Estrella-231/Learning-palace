"""Review service - handles spaced repetition logic."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.review_card import ReviewCard
from app.models.knowledge_node import KnowledgeNode


# Simplified FSRS intervals (in days)
INTERVALS = {
    "again": 0,        # review again in 10 min (handled separately)
    "hard": 1,         # 1 day
    "good": 3,         # 3 days
    "easy": 7,         # 7 days
}

AGAIN_MINUTES = 10


async def update_after_review(
    session: AsyncSession,
    card_id: uuid.UUID,
    rating: str,  # "again", "hard", "good", "easy"
) -> dict:
    """Update a review card after user rates their recall."""
    stmt = select(ReviewCard).where(ReviewCard.id == card_id)
    result = await session.execute(stmt)
    card = result.scalar_one_or_none()

    if not card:
        raise ValueError(f"Review card not found: {card_id}")

    now = datetime.now(timezone.utc)

    if rating == "again":
        card.next_review_at = now + timedelta(minutes=AGAIN_MINUTES)
        card.stability = max(card.stability * 0.5, 0.1)
    else:
        days = INTERVALS.get(rating, 3)
        card.next_review_at = now + timedelta(days=days)
        card.stability = card.stability + 0.5

    card.retrievability = 0.9
    card.review_count += 1

    # Update mastery on the related knowledge node
    if card.node_id:
        node_stmt = select(KnowledgeNode).where(KnowledgeNode.id == card.node_id)
        node_result = await session.execute(node_stmt)
        node = node_result.scalar_one_or_none()
        if node:
            rating_scores = {"again": 0.0, "hard": 0.3, "good": 0.7, "easy": 1.0}
            boost = rating_scores.get(rating, 0.5)
            # Moving average
            node.mastery = min(1.0, node.mastery * 0.7 + boost * 0.3)

    await session.flush()

    return {
        "next_review_at": card.next_review_at.isoformat(),
        "stability": card.stability,
        "retrievability": card.retrievability,
        "review_count": card.review_count,
    }


async def get_due_cards(
    session: AsyncSession,
    course_id: uuid.UUID | None = None,
    limit: int = 20,
) -> list[ReviewCard]:
    """Get all review cards due for review."""
    now = datetime.now(timezone.utc)
    stmt = select(ReviewCard).where(ReviewCard.next_review_at <= now)

    if course_id:
        stmt = stmt.join(KnowledgeNode).where(KnowledgeNode.course_id == course_id)

    stmt = stmt.order_by(ReviewCard.next_review_at.asc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_review_stats(
    session: AsyncSession,
    course_id: uuid.UUID | None = None,
) -> dict:
    """Get review statistics."""
    now = datetime.now(timezone.utc)

    # Total cards
    total_q = select(func.count(ReviewCard.id))
    due_q = select(func.count(ReviewCard.id)).where(ReviewCard.next_review_at <= now)

    if course_id:
        total_q = total_q.join(KnowledgeNode).where(
            KnowledgeNode.course_id == course_id
        )
        due_q = due_q.join(KnowledgeNode).where(KnowledgeNode.course_id == course_id)

    total = (await session.execute(total_q)).scalar() or 0
    due = (await session.execute(due_q)).scalar() or 0

    return {
        "total_cards": total,
        "due_cards": due,
        "scheduled_cards": max(total - due, 0),
    }
