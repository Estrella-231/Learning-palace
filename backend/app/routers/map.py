"""Map router - provides data for the knowledge map visualization."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_async_session
from app.models.course import Course
from app.models.user import User
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.dependencies import get_current_user
from app.schemas.knowledge import MapResponse, KnowledgeNodeOut, KnowledgeEdgeOut

router = APIRouter()


@router.get("/map/{course_id}", response_model=MapResponse)
async def get_map(
    course_id: str,
    type_filter: str | None = Query(None, alias="type"),
    search: str | None = None,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Get all nodes and edges for a course's knowledge map."""
    # Verify course ownership
    course_stmt = select(Course).where(Course.id == course_id)
    course_result = await db.execute(course_stmt)
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id and course.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    # Query nodes
    stmt = select(KnowledgeNode).where(KnowledgeNode.course_id == course_id)

    if type_filter:
        stmt = stmt.where(KnowledgeNode.type == type_filter)

    if search:
        stmt = stmt.where(KnowledgeNode.title.ilike(f"%{search}%"))

    stmt = stmt.order_by(KnowledgeNode.created_at.desc())
    nodes_result = await db.execute(stmt)
    nodes = list(nodes_result.scalars().all())

    # Query edges between these nodes
    node_ids = [n.id for n in nodes]
    edges = []
    if node_ids:
        edge_stmt = select(KnowledgeEdge).where(
            KnowledgeEdge.source_node_id.in_(node_ids)
            | KnowledgeEdge.target_node_id.in_(node_ids)
        )
        edges_result = await db.execute(edge_stmt)
        edges = list(edges_result.scalars().all())

    return MapResponse(
        nodes=[KnowledgeNodeOut.model_validate(n) for n in nodes],
        edges=[KnowledgeEdgeOut.model_validate(e) for e in edges],
    )
