from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ReviewCardOut(ORMModel):
    id: str
    node_id: str
    question: str
    answer: str
    card_type: str
    difficulty: int
    next_review_at: datetime
    stability: float
    retrievability: float
    review_count: int


class ReviewCardUpdate(BaseModel):
    difficulty: int | None = None
    next_review_at: datetime | None = None
    stability: float | None = None
    retrievability: float | None = None
    review_count: int | None = None


class ReviewStats(BaseModel):
    total_cards: int
    due_cards: int
    scheduled_cards: int
