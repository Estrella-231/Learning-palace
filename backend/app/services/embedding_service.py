"""Embedding service - text vectorization for similarity search."""

from __future__ import annotations

import logging
import asyncio
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None

# Expected dimension for text-embedding-3-small
EXPECTED_DIM = 1536


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        cfg = settings.embedding_config
        _client = AsyncOpenAI(
            api_key=cfg.get("api_key", ""),
            base_url=cfg.get("base_url", "https://api.openai.com/v1"),
        )
    return _client


def _is_api_key_configured() -> bool:
    """Check if embedding API key is properly configured."""
    cfg = settings.embedding_config
    api_key = cfg.get("api_key", "")
    if not api_key:
        logger.info("Embedding API key not configured, skipping vectorization")
        return False
    if api_key.startswith("${"):
        logger.debug("Embedding API key is a placeholder (${...}), skipping")
        return False
    return True


async def embed(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts. Returns empty list when unavailable."""
    if not texts:
        return []
    if not _is_api_key_configured():
        return []

    max_retries = 2
    last_exception = None

    for attempt in range(max_retries):
        try:
            client = _get_client()
            cfg = settings.embedding_config
            resp = await client.embeddings.create(
                model=cfg.get("model", "text-embedding-3-small"),
                input=texts,
                timeout=cfg.get("timeout", 10),
            )
            embeddings = [d.embedding for d in resp.data]

            # Validate dimensionality
            if embeddings and len(embeddings[0]) != EXPECTED_DIM:
                logger.warning(
                    f"Embedding dimension mismatch: expected {EXPECTED_DIM}, "
                    f"got {len(embeddings[0])}. Model may have changed."
                )

            return embeddings

        except asyncio.TimeoutError:
            last_exception = "timeout"
            logger.warning(
                f"Embedding API timeout (attempt {attempt + 1}/{max_retries})"
            )
        except Exception as e:
            last_exception = str(e)[:200]
            logger.error(
                f"Embedding API error (attempt {attempt + 1}/{max_retries}): {e}"
            )

        if attempt < max_retries - 1:
            await asyncio.sleep(0.5 * (attempt + 1))

    logger.error(
        f"Embedding failed after {max_retries} attempts. "
        f"Last error: {last_exception}. "
        f"Semantic similarity search will be degraded."
    )
    return []


async def embed_single(text: str) -> list[float]:
    """Generate embedding for a single text."""
    results = await embed([text])
    return results[0] if results else []
