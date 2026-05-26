"""Knowledge nodes router - CRUD for knowledge nodes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.database import get_async_session
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.review_card import ReviewCard
from app.models.message import Message
from app.schemas.knowledge import (
    KnowledgeNodeOut,
    KnowledgeNodeUpdate,
    NodeDetailResponse,
    KnowledgeEdgeOut,
)

router = APIRouter()


@router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
async def get_node_detail(
    node_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Get detailed view of a knowledge node with related nodes."""
    stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get source message
    source_message = None
    if node.source_message_id:
        msg_stmt = select(Message).where(Message.id == node.source_message_id)
        msg_result = await db.execute(msg_stmt)
        msg = msg_result.scalar_one_or_none()
        if msg:
            source_message = {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content[:500],
                "created_at": msg.created_at.isoformat(),
            }

    # Get related nodes via edges
    edges_stmt = select(KnowledgeEdge).where(
        (KnowledgeEdge.source_node_id == node_id)
        | (KnowledgeEdge.target_node_id == node_id)
    )
    edges_result = await db.execute(edges_stmt)
    edges = list(edges_result.scalars().all())

    related_ids = set()
    for edge in edges:
        if str(edge.source_node_id) != node_id:
            related_ids.add(edge.source_node_id)
        if str(edge.target_node_id) != node_id:
            related_ids.add(edge.target_node_id)

    related_nodes = []
    if related_ids:
        related_stmt = select(KnowledgeNode).where(
            KnowledgeNode.id.in_(related_ids)
        )
        related_result = await db.execute(related_stmt)
        related_nodes = list(related_result.scalars().all())

    # Get review cards for this node
    cards_stmt = select(ReviewCard).where(ReviewCard.node_id == node_id)
    cards_result = await db.execute(cards_stmt)
    cards = cards_result.scalars().all()

    return NodeDetailResponse(
        node=KnowledgeNodeOut.model_validate(node),
        source_message=source_message,
        related_nodes=[KnowledgeNodeOut.model_validate(n) for n in related_nodes],
        edges=[KnowledgeEdgeOut.model_validate(e) for e in edges],
        review_cards=[
            {
                "id": str(c.id),
                "question": c.question,
                "answer": c.answer,
                "card_type": c.card_type,
                "difficulty": c.difficulty,
                "next_review_at": c.next_review_at.isoformat(),
                "review_count": c.review_count,
            }
            for c in cards
        ],
    )


@router.patch("/nodes/{node_id}", response_model=KnowledgeNodeOut)
async def update_node(
    node_id: str,
    data: KnowledgeNodeUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """Update a knowledge node's metadata or position."""
    stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(node, key, value)

    await db.commit()
    await db.refresh(node)
    return KnowledgeNodeOut.model_validate(node)


@router.delete("/nodes/{node_id}")
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a knowledge node and its associated edges and cards."""
    stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Delete associated edges
    edge_stmt = select(KnowledgeEdge).where(
        (KnowledgeEdge.source_node_id == node_id)
        | (KnowledgeEdge.target_node_id == node_id)
    )
    edges = (await db.execute(edge_stmt)).scalars().all()
    for edge in edges:
        await db.delete(edge)

    # Delete associated review cards
    card_stmt = select(ReviewCard).where(ReviewCard.node_id == node_id)
    cards = (await db.execute(card_stmt)).scalars().all()
    for card in cards:
        await db.delete(card)

    await db.delete(node)
    await db.commit()

    return {"status": "deleted"}
