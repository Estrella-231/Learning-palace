from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class KnowledgeNodeOut(ORMModel):
    id: str
    course_id: str
    title: str
    type: str
    summary: str
    content: str
    mastery: float
    position_x: float
    position_y: float
    source_message_id: str | None
    created_at: datetime
    updated_at: datetime


class KnowledgeNodeUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    content: str | None = None
    position_x: float | None = None
    position_y: float | None = None


class KnowledgeEdgeOut(ORMModel):
    id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    confidence: float
    evidence: str | None


class MapResponse(BaseModel):
    nodes: list[KnowledgeNodeOut]
    edges: list[KnowledgeEdgeOut]


class NodeDetailResponse(BaseModel):
    node: KnowledgeNodeOut
    source_message: dict | None
    related_nodes: list[KnowledgeNodeOut]
    edges: list[KnowledgeEdgeOut]
    review_cards: list


class CourseOut(ORMModel):
    id: str
    name: str
    description: str
    created_at: datetime


class CourseCreate(BaseModel):
    name: str
    description: str = ""


class SessionOut(ORMModel):
    id: str
    course_id: str
    title: str
    created_at: datetime
