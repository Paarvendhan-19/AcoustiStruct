"""AcoustiStruct API — Database engine and session management."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_config


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def _build_engine():
    cfg = get_config()
    return create_async_engine(
        cfg.database.url,
        echo=cfg.database.echo,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


engine = None
async_session_factory = None


def init_engine():
    global engine, async_session_factory
    engine = _build_engine()
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async database session."""
    if async_session_factory is None:
        init_engine()
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Standalone async context manager for use outside FastAPI DI."""
    if async_session_factory is None:
        init_engine()
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
