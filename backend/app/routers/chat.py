"""Chat router - the main conversation endpoint with knowledge extraction."""

from __future__ import annotations

import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.models.database import get_async_session, async_session as _async_session_maker
from app.models.course import Course
from app.models.user import User
from app.models.message import Message, Session
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.review_card import ReviewCard
from app.dependencies import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import chat as llm_chat, chat_stream
from app.services.extraction_service import (
    extract_concepts,
    extract_relations,
    generate_review_cards,
    detect_misconceptions,
)
from app.services.merge_service import merge_or_create

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Chat endpoint: answer the question, then extract and persist knowledge."""

    # 1. Get or create course
    course_id = await _get_or_create_course(db, req, user)

    # 2. Get or create session
    session_id = await _get_or_create_session(db, req, course_id)

    # 3. Build conversation history
    history = await _build_history(db, session_id)

    # 4. Save user message
    user_msg = Message(session_id=session_id, role="user", content=req.message)
    db.add(user_msg)
    await db.flush()

    # 5. Generate AI answer
    messages = [*history, {"role": "user", "content": req.message}]
    answer = await llm_chat(messages)

    # 6. Save assistant message
    assistant_msg = Message(session_id=session_id, role="assistant", content=answer)
    db.add(assistant_msg)
    await db.flush()

    # 7. Extract knowledge concurrently
    extraction = await extract_concepts(req.message, answer)

    # 8. Process each concept: merge/create nodes
    new_nodes = []
    new_edges = []
    all_concepts_for_relation = []
    all_node_ids: dict[str, KnowledgeNode] = {}  # title → node (new or merged)

    # Get existing nodes for relation extraction
    existing_nodes_q = select(KnowledgeNode).where(KnowledgeNode.course_id == course_id)
    existing_nodes_result = await db.execute(existing_nodes_q)
    existing_nodes = [
        {"id": str(n.id), "title": n.title, "type": n.type, "summary": n.summary}
        for n in existing_nodes_result.scalars().all()
    ]

    for i, concept in enumerate(extraction.get("concepts", [])):
        title = concept["title"]
        type_ = concept.get("type", "concept")
        summary = concept.get("summary", "")
        content = concept.get("key_points", [])
        content_str = "\n".join(f"- {p}" for p in content)

        node_id, is_new = await merge_or_create(
            session=db,
            course_id=course_id,
            title=title,
            type_=type_,
            summary=summary,
            content=content_str,
            source_message_id=assistant_msg.id,
        )

        # Fetch the node so we can set position and track it
        stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
        result = await db.execute(stmt)
        node = result.scalar_one()

        if is_new:
            node.position_x = 100 + i * 50
            node.position_y = 100 + i * 80
            new_nodes.append(node)

        all_node_ids[title] = node
        all_concepts_for_relation.append({
            "title": title, "type": type_, "summary": summary
        })

    # 9. Extract relationships
    if all_concepts_for_relation:
        relations = await extract_relations(all_concepts_for_relation, existing_nodes)
        title_to_id = {title: str(node.id) for title, node in all_node_ids.items()}
        for existing in existing_nodes:
            if existing["title"] not in title_to_id:
                title_to_id[existing["title"]] = existing["id"]

        for rel in relations.get("relations", []):
            src_id = title_to_id.get(rel.get("source_title"))
            tgt_id = title_to_id.get(rel.get("target_title"))
            if src_id and tgt_id:
                edge = KnowledgeEdge(
                    source_node_id=uuid.UUID(src_id),
                    target_node_id=uuid.UUID(tgt_id),
                    relation_type=rel.get("relation_type", "related"),
                    confidence=rel.get("confidence", 0.8),
                    evidence=rel.get("evidence", ""),
                )
                db.add(edge)
                new_edges.append(edge)

    # 10. Generate review cards
    review_cards = []
    if all_concepts_for_relation:
        cards_data = await generate_review_cards(all_concepts_for_relation, answer)
        for card_data in cards_data.get("cards", []):
            # Match card to node by concept_title (look in all nodes, not just new)
            concept_title = card_data.get("concept_title", "")
            matched_node = all_node_ids.get(concept_title)
            if matched_node:
                card = ReviewCard(
                    node_id=matched_node.id,
                    question=card_data.get("question", ""),
                    answer=card_data.get("answer", ""),
                    card_type=card_data.get("card_type", "basic"),
                    difficulty=2,
                )
                db.add(card)
                review_cards.append(card)

    await db.commit()

    # Build response
    return ChatResponse(
        answer=answer,
        session_id=str(session_id),
        course_id=str(course_id),
        new_nodes=[
            {
                "id": str(n.id),
                "title": n.title,
                "type": n.type,
                "summary": n.summary,
                "mastery": n.mastery,
                "position_x": n.position_x,
                "position_y": n.position_y,
            }
            for n in new_nodes
        ],
        new_edges=[
            {
                "id": str(e.id),
                "source_node_id": str(e.source_node_id),
                "target_node_id": str(e.target_node_id),
                "relation_type": e.relation_type,
                "confidence": e.confidence,
            }
            for e in new_edges
        ],
        review_cards=[
            {
                "id": str(c.id),
                "node_id": str(c.node_id),
                "question": c.question,
                "answer": c.answer,
                "card_type": c.card_type,
                "difficulty": c.difficulty,
            }
            for c in review_cards
        ],
    )


@router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Streaming chat endpoint - returns answer as SSE, then extraction results."""
    # Get or create course/session
    course_id = await _get_or_create_course(db, req)
    session_id = await _get_or_create_session(db, req, course_id)

    history = await _build_history(db, session_id)

    # Save user message
    user_msg = Message(session_id=session_id, role="user", content=req.message)
    db.add(user_msg)
    await db.flush()
    await db.commit()

    messages = [*history, {"role": "user", "content": req.message}]

    async def event_stream() -> AsyncGenerator[str, None]:
        # Stream the answer
        full_answer = ""
        yield "data: {\"type\": \"answer_start\"}\n\n"
        async for chunk in chat_stream(messages):
            full_answer += chunk
            yield f"data: {{\"type\": \"chunk\", \"content\": {json.dumps(chunk)}}}\n\n"
        yield f"data: {{\"type\": \"answer_end\", \"full_length\": {len(full_answer)}}}\n\n"

        # Save assistant message and persist knowledge
        async with _async_session_maker() as s2:
            assistant_msg = Message(
                session_id=session_id, role="assistant", content=full_answer
            )
            s2.add(assistant_msg)
            await s2.flush()

            # Extract knowledge
            extraction = await extract_concepts(req.message, full_answer)
            yield f"data: {{\"type\": \"extraction\", \"data\": {json.dumps(extraction)}}}\n\n"

            # Persist: merge/create nodes
            new_nodes_json = []
            new_edges_json = []
            review_cards_json = []

            # Get existing nodes for relation extraction
            existing_nodes_q = select(KnowledgeNode).where(KnowledgeNode.course_id == course_id)
            existing_nodes_result = await s2.execute(existing_nodes_q)
            existing_nodes = [
                {"id": str(n.id), "title": n.title, "type": n.type, "summary": n.summary}
                for n in existing_nodes_result.scalars().all()
            ]

            all_node_ids: dict[str, KnowledgeNode] = {}
            all_concepts_for_relation: list[dict] = []

            for i, concept in enumerate(extraction.get("concepts", [])):
                title = concept["title"]
                type_ = concept.get("type", "concept")
                summary = concept.get("summary", "")
                content = concept.get("key_points", [])
                content_str = "\n".join(f"- {p}" for p in content)

                node_id, is_new = await merge_or_create(
                    session=s2,
                    course_id=course_id,
                    title=title,
                    type_=type_,
                    summary=summary,
                    content=content_str,
                    source_message_id=assistant_msg.id,
                )

                stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
                result = await s2.execute(stmt)
                node = result.scalar_one()

                if is_new:
                    node.position_x = 100 + i * 50
                    node.position_y = 100 + i * 80
                    new_nodes_json.append({
                        "id": str(node.id),
                        "title": node.title,
                        "type": node.type,
                        "summary": node.summary,
                        "mastery": node.mastery,
                        "position_x": node.position_x,
                        "position_y": node.position_y,
                    })

                all_node_ids[title] = node
                all_concepts_for_relation.append({
                    "title": title, "type": type_, "summary": summary
                })

            # Extract and persist relations
            if all_concepts_for_relation:
                relations = await extract_relations(all_concepts_for_relation, existing_nodes)
                title_to_id = {title: str(node.id) for title, node in all_node_ids.items()}
                for existing in existing_nodes:
                    if existing["title"] not in title_to_id:
                        title_to_id[existing["title"]] = existing["id"]

                for rel in relations.get("relations", []):
                    src_id = title_to_id.get(rel.get("source_title"))
                    tgt_id = title_to_id.get(rel.get("target_title"))
                    if src_id and tgt_id:
                        edge = KnowledgeEdge(
                            source_node_id=uuid.UUID(src_id),
                            target_node_id=uuid.UUID(tgt_id),
                            relation_type=rel.get("relation_type", "related"),
                            confidence=rel.get("confidence", 0.8),
                            evidence=rel.get("evidence", ""),
                        )
                        s2.add(edge)
                        await s2.flush()
                        new_edges_json.append({
                            "id": str(edge.id),
                            "source_node_id": str(edge.source_node_id),
                            "target_node_id": str(edge.target_node_id),
                            "relation_type": edge.relation_type,
                            "confidence": edge.confidence,
                        })

                # Generate and persist review cards
                cards_data = await generate_review_cards(all_concepts_for_relation, full_answer)
                for card_data in cards_data.get("cards", []):
                    concept_title = card_data.get("concept_title", "")
                    matched_node = all_node_ids.get(concept_title)
                    if matched_node:
                        card = ReviewCard(
                            node_id=matched_node.id,
                            question=card_data.get("question", ""),
                            answer=card_data.get("answer", ""),
                            card_type=card_data.get("card_type", "basic"),
                            difficulty=2,
                        )
                        s2.add(card)
                        await s2.flush()
                        review_cards_json.append({
                            "id": str(card.id),
                            "node_id": str(card.node_id),
                            "question": card.question,
                            "answer": card.answer,
                            "card_type": card.card_type,
                            "difficulty": card.difficulty,
                        })

            await s2.commit()

            # Send persisted data back to frontend
            persisted = json.dumps({
                'new_nodes': new_nodes_json,
                'new_edges': new_edges_json,
                'review_cards': review_cards_json,
            })
            yield f"data: {{\"type\": \"persisted\", \"data\": {persisted}}}\n\n"

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Constants
DEFAULT_COURSE_NAME = "默认课程"


async def _get_or_create_course(db: AsyncSession, req: ChatRequest, user: User) -> uuid.UUID:
    """Get existing course by ID, or create/find default course for the user."""
    if req.course_id:
        return uuid.UUID(req.course_id)

    # Find or create default course for this user
    stmt = select(Course).where(
        Course.name == DEFAULT_COURSE_NAME,
        Course.user_id == user.id,
    ).limit(1)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()

    if not course:
        course = Course(name=DEFAULT_COURSE_NAME, description="自动创建的默认课程", user_id=user.id)
        db.add(course)
        await db.flush()

    return course.id


async def _get_or_create_session(
    db: AsyncSession, req: ChatRequest, course_id: uuid.UUID
) -> uuid.UUID:
    """Get existing session by ID, or create new session."""
    if req.session_id:
        return uuid.UUID(req.session_id)

    session = Session(course_id=course_id, title="新对话")
    db.add(session)
    await db.flush()
    return session.id


async def _build_history(db: AsyncSession, session_id: uuid.UUID) -> list[dict]:
    """Build conversation history from database messages."""
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in messages]
