"""Knowledge extraction service - the core pipeline that extracts
structured knowledge from AI responses.
"""

from __future__ import annotations

from app.services.llm_service import chat_json
from app.prompts.extraction import EXTRACTION_PROMPT
from app.prompts.relation import RELATION_PROMPT
from app.prompts.merge import MERGE_PROMPT
from app.prompts.review_card import REVIEW_CARD_PROMPT
from app.prompts.misconception import MISCONCEPTION_PROMPT


async def extract_concepts(question: str, answer: str) -> dict:
    """Extract concepts and definitions from an AI answer."""
    prompt = EXTRACTION_PROMPT.format(question=question, answer=answer)
    messages = [{"role": "user", "content": prompt}]
    return await chat_json(messages)


async def extract_relations(concepts: list[dict], existing_nodes: list[dict]) -> dict:
    """Extract relationships between concepts."""
    import json
    prompt = RELATION_PROMPT.format(
        new_concepts=json.dumps(concepts, ensure_ascii=False),
        existing_nodes=json.dumps(existing_nodes, ensure_ascii=False),
    )
    messages = [{"role": "user", "content": prompt}]
    return await chat_json(messages)


async def merge_decision(new_node: dict, similar_nodes: list[dict]) -> dict:
    """Decide whether to merge a new node with existing similar nodes."""
    import json
    prompt = MERGE_PROMPT.format(
        new_node=json.dumps(new_node, ensure_ascii=False),
        similar_nodes=json.dumps(similar_nodes, ensure_ascii=False),
    )
    messages = [{"role": "user", "content": prompt}]
    return await chat_json(messages)


async def generate_review_cards(concepts: list[dict], answer: str) -> dict:
    """Generate spaced-repetition review cards from concepts."""
    import json
    prompt = REVIEW_CARD_PROMPT.format(
        concepts=json.dumps(concepts, ensure_ascii=False),
        context=answer[:2000],
    )
    messages = [{"role": "user", "content": prompt}]
    return await chat_json(messages)


async def detect_misconceptions(question: str, answer: str) -> dict:
    """Detect conceptual misconceptions in the user's question."""
    prompt = MISCONCEPTION_PROMPT.format(question=question, answer=answer)
    messages = [{"role": "user", "content": prompt}]
    return await chat_json(messages)
