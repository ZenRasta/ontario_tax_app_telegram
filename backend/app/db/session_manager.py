# app/db/session_manager.py
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from ..core.config import settings

# --------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------- #
connect_args = {}

# sqlite quirks in dev
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.ENVIRONMENT.lower() == "development",
    future=True,
    poolclass=NullPool if connect_args else None,
    connect_args=connect_args,
)

# --------------------------------------------------------------------- #
# Session factory
# --------------------------------------------------------------------- #
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# --------------------------------------------------------------------- #
# Declarative base
# --------------------------------------------------------------------- #
# Prefer importing Base from your models file so everything shares ONE MetaData
try:
    from .schemas import DbBase  # noqa: F401
except ImportError:
    DbBase = declarative_base()

# --------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------- #
async def create_db_and_tables() -> None:
    """Run at startup to create missing tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(DbBase.metadata.create_all)


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency providing an `AsyncSession`.
    Leave transaction control to route/CRUD layer.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # session closes automatically via context‑manager
            await session.close()
