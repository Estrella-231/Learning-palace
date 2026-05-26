"""LLM service - unified interface for multiple model providers.

Reads config.json to determine which model to use.
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.config import settings


# Client cache: {model_name: client_instance}
_openai_clients: dict[str, AsyncOpenAI] = {}
_anthropic_clients: dict[str, AsyncAnthropic] = {}


def _get_model_config(model_name: str | None = None) -> dict:
    """Get model config from config.json by name."""
    name = model_name or settings.default_model_name
    models = settings.models
    if name not in models:
        raise ValueError(f"Unknown model: {name}. Available: {list(models.keys())}")
    return models[name]


def _get_openai_client(model_name: str) -> AsyncOpenAI:
    cfg = _get_model_config(model_name)
    api_key = cfg["api_key"]
    base_url = cfg.get("base_url", "https://api.openai.com/v1")
    cache_key = f"{model_name}:{base_url}"
    if cache_key not in _openai_clients:
        _openai_clients[cache_key] = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return _openai_clients[cache_key]


def _get_anthropic_client(model_name: str = "claude") -> AsyncAnthropic:
    cfg = _get_model_config(model_name)
    api_key = cfg["api_key"]
    base_url = cfg.get("base_url")
    cache_key = f"{model_name}:{base_url or 'default'}"
    if cache_key not in _anthropic_clients:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        _anthropic_clients[cache_key] = AsyncAnthropic(**kwargs)
    return _anthropic_clients[cache_key]


async def chat(
    messages: list[dict],
    model_name: str | None = None,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """Send a chat request and return the complete response text."""
    name = model_name or settings.default_model_name
    cfg = _get_model_config(name)
    provider = cfg["provider"]

    if provider in ("openai", "openai-compatible"):
        client = _get_openai_client(name)
        kwargs = {"model": cfg["model"], "messages": messages, "temperature": temperature}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    elif provider == "anthropic":
        client = _get_anthropic_client(name)
        # Separate system message if present
        system = None
        msgs = []
        for m in messages:
            if m["role"] == "system" and not system:
                system = m["content"]
            else:
                msgs.append({"role": m["role"], "content": m["content"]})

        kwargs = {
            "model": cfg["model"],
            "messages": msgs,
            "max_tokens": 4096,
        }
        if system:
            kwargs["system"] = system
        resp = await client.messages.create(**kwargs)
        # Handle both TextBlock and ThinkingBlock (some models return thinking)
        texts = []
        for block in resp.content:
            if hasattr(block, 'text'):
                texts.append(block.text)
        return "".join(texts) or (resp.content[0].text if hasattr(resp.content[0], 'text') else "")

    else:
        raise ValueError(f"Unknown provider: {provider}")


async def chat_stream(
    messages: list[dict],
    model_name: str | None = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """Send a chat request and stream the response."""
    name = model_name or settings.default_model_name
    cfg = _get_model_config(name)
    provider = cfg["provider"]

    if provider in ("openai", "openai-compatible"):
        client = _get_openai_client(name)
        stream = await client.chat.completions.create(
            model=cfg["model"],
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    elif provider == "anthropic":
        client = _get_anthropic_client(name)
        system = None
        msgs = []
        for m in messages:
            if m["role"] == "system" and not system:
                system = m["content"]
            else:
                msgs.append({"role": m["role"], "content": m["content"]})

        kwargs = {
            "model": cfg["model"],
            "messages": msgs,
            "max_tokens": 4096,
        }
        if system:
            kwargs["system"] = system

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    else:
        raise ValueError(f"Unknown provider: {provider}")


async def chat_json(
    messages: list[dict],
    model_name: str | None = None,
) -> dict:
    """Send a chat request expecting JSON response."""
    name = model_name or settings.extraction_config.get("model", settings.default_model_name)
    # Ensure the prompt asks for JSON
    messages_with_instruction = list(messages)
    last_msg = messages_with_instruction[-1]
    if last_msg["role"] == "user":
        messages_with_instruction[-1] = {
            "role": "user",
            "content": last_msg["content"] + "\n\nOutput only valid JSON, no other text.",
        }

    text = await chat(
        messages_with_instruction,
        model_name=name,
        temperature=settings.extraction_config.get("temperature", 0.3),
    )
    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict:
    """Parse JSON from LLM response with robust error handling and repair strategies."""
    import re
    import logging
    logger = logging.getLogger(__name__)

    text = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: Extract from markdown code fences
    fence_patterns = [
        r'```(?:json)?\s*\n?(.*?)\n?```',  # ```json ... ```
        r'```(.*?)```',                      # ``` ... ```
    ]
    for pattern in fence_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                result = json.loads(match.strip())
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, ValueError):
                continue

    # Strategy 3: Remove markdown fence markers line by line
    lines = text.split("\n")
    cleaned_lines = [l for l in lines if not l.strip().startswith("```")]
    try:
        result = json.loads("\n".join(cleaned_lines))
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 4: Find the first { and last } to extract JSON object
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        try:
            result = json.loads(text[first_brace:last_brace + 1])
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 5: Try to fix common LLM JSON errors
    try:
        fixed = text
        # Remove trailing commas before closing ] or }
        fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
        # Fix missing quotes on keys (simple case)
        result = json.loads(fixed)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # All strategies failed, return error marker
    logger.error(f"Failed to parse JSON from LLM response. Raw text (first 500 chars): {text[:500]}")
    return {"_parse_error": True, "raw_text": text[:1000]}
