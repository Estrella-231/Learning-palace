"""FastAPI dependencies — injectable request-scoped helpers."""

from __future__ import annotations

import uuid

from fastapi import Header
from sqlalchemy import select

from app.models.user import User
from app.models.database import async_session

DEFAULT_USERNAME = "default"


async def get_current_user(x_user_id: str | None = Header(None, alias="x-user-id")) -> User:
    """Resolve the current user from the x-user-id header.

    Falls back to the default user when no header is provided (MVP / no auth).
    """
    user_uuid = uuid.UUID(x_user_id) if x_user_id else None

    async with async_session() as session:
        if user_uuid:
            stmt = select(User).where(User.id == user_uuid)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user

        # Fallback: find or create the default user
        stmt = select(User).where(User.username == DEFAULT_USERNAME)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user

        user = User(username=DEFAULT_USERNAME)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
