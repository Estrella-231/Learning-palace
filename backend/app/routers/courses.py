"""Courses router - CRUD for courses."""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_async_session
from app.models.course import Course
from app.models.user import User
from app.models.message import Session
from app.dependencies import get_current_user
from app.schemas.knowledge import CourseOut, CourseCreate, SessionOut

router = APIRouter()


@router.post("/courses", response_model=CourseOut)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Create a new course for the current user."""
    course = Course(name=data.name, description=data.description, user_id=user.id)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return CourseOut.model_validate(course)


@router.get("/courses", response_model=List[CourseOut])
async def list_courses(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """List courses belonging to the current user."""
    stmt = select(Course).where(
        (Course.user_id == user.id) | (Course.user_id.is_(None))
    ).order_by(Course.created_at.desc())
    result = await db.execute(stmt)
    courses = result.scalars().all()
    return [CourseOut.model_validate(c) for c in courses]


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Delete a course (owner only)."""
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id and course.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your course")

    await db.delete(course)
    await db.commit()
    return {"status": "deleted"}


@router.get("/courses/{course_id}/sessions", response_model=List[SessionOut])
async def list_sessions(
    course_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    """List sessions for a course."""
    stmt = (
        select(Session)
        .where(Session.course_id == course_id)
        .order_by(Session.created_at.desc())
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return [SessionOut.model_validate(s) for s in sessions]


@router.post("/courses/{course_id}/sessions", response_model=SessionOut)
async def create_session(
    course_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new session in a course."""
    session = Session(course_id=uuid.UUID(course_id), title="新对话")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut.model_validate(session)
