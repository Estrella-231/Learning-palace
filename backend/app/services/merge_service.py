"""Node merge service - handles merging similar knowledge nodes."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.services.embedding_service import embed_single
from app.services.extraction_service import merge_decision


SIMILARITY_THRESHOLD = 0.85


async def find_similar_nodes(
    session: AsyncSession,
    course_id: uuid.UUID,
    title: str,
    limit: int = 3,
) -> list[dict]:
    """Find existing nodes similar to the given title using pgvector."""
    embedding = await embed_single(title)
    if not embedding:
        return []  # No embedding available, skip similarity check
    embedding_str = f"[{','.join(str(v) for v in embedding)}]"

    query = text("""
        SELECT id, title, type, summary, mastery,
               1 - (embedding <=> :emb::vector) AS similarity
        FROM knowledge_nodes
        WHERE course_id = :course_id
          AND embedding IS NOT NULL
          AND 1 - (embedding <=> :emb::vector) > :threshold
        ORDER BY embedding <=> :emb::vector
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {
            "emb": embedding_str,
            "course_id": course_id,
            "threshold": SIMILARITY_THRESHOLD,
            "limit": limit,
        },
    )
    rows = result.fetchall()

    return [
        {
            "id": str(row.id),
            "title": row.title,
            "type": row.type,
            "summary": row.summary,
            "mastery": row.mastery,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]


async def _create_node(
    session: AsyncSession,
    course_id: uuid.UUID,
    title: str,
    type_: str,
    summary: str,
    content: str,
    source_message_id: uuid.UUID,
) -> KnowledgeNode:
    """Create and flush a new knowledge node."""
    node = KnowledgeNode(
        course_id=course_id,
        title=title,
        type=type_,
        summary=summary,
        content=content,
        source_message_id=source_message_id,
        embedding=await embed_single(title),
    )
    session.add(node)
    await session.flush()
    return node


def _safe_uuid(value: str) -> uuid.UUID | None:
    """Parse a UUID string safely, returning None on failure."""
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        return None


async def merge_or_create(
    session: AsyncSession,
    course_id: uuid.UUID,
    title: str,
    type_: str,
    summary: str,
    content: str,
    source_message_id: uuid.UUID,
) -> tuple[uuid.UUID, bool]:
    """Check for similar nodes and decide to merge/create.

    Returns (node_id, is_new).
    """
    similar = await find_similar_nodes(session, course_id, title)

    if not similar:
        node = await _create_node(session, course_id, title, type_, summary, content, source_message_id)
        return node.id, True

    # Ask LLM whether to merge
    decision = await merge_decision({"title": title, "type": type_, "summary": summary}, similar)

    action = decision.get("action", "create_new")
    if action == "update_existing":
        # Try the LLM-suggested ID first, fall back to top similar match
        llm_id = _safe_uuid(decision.get("similar_node_id", ""))
        target_id = llm_id or _safe_uuid(similar[0]["id"])
        if target_id:
            stmt = select(KnowledgeNode).where(KnowledgeNode.id == target_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                existing.summary = decision.get("merged_summary", existing.summary)
                existing.content = existing.content + "\n\n---\n\n" + content
                existing.mastery = max(existing.mastery, 0.1)
                await session.flush()
                return existing.id, False

    # Create new node (for both "create_new" and unknown actions)
    node = await _create_node(session, course_id, title, type_, summary, content, source_message_id)
    return node.id, True
