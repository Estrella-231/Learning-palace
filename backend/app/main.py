from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.models.database import engine, Base, async_session
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if not exist (dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure a default user exists
    async with async_session() as session:
        stmt = select(User).where(User.username == "default")
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            session.add(User(username="default"))
            await session.commit()

    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(title="Learning Palace API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
from app.routers import chat, nodes, map, review, courses

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(nodes.router, prefix="/api", tags=["nodes"])
app.include_router(map.router, prefix="/api", tags=["map"])
app.include_router(review.router, prefix="/api", tags=["review"])
app.include_router(courses.router, prefix="/api", tags=["courses"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
