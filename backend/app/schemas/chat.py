from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    course_id: str | None = None
    session_id: str | None = None


class KnowledgeNodeOut(ORMModel):
    id: str
    title: str
    type: str
    summary: str
    mastery: float
    position_x: float
    position_y: float


class KnowledgeEdgeOut(ORMModel):
    id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    confidence: float


class ReviewCardOut(ORMModel):
    id: str
    node_id: str
    question: str
    answer: str
    card_type: str
    difficulty: int


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    course_id: str
    new_nodes: list[KnowledgeNodeOut] = []
    new_edges: list[KnowledgeEdgeOut] = []
    review_cards: list[ReviewCardOut] = []
