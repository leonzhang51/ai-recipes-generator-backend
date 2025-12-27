# app/database/connection.py
"""Async database connection management for PostgreSQL."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Initialize database connection and create tables."""
    global _engine, AsyncSessionLocal  # noqa: PLW0603

    settings = get_settings()

    logger.info("Initializing database connection to: %s", settings.database_url)

    _engine = create_async_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.debug,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Create tables and enable pgvector extension
    async with _engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension enabled")

        # Import models to register them with Base
        from app.database.models import Base

        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


async def close_db() -> None:
    """Close database connections."""
    global _engine, AsyncSessionLocal  # noqa: PLW0603

    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")
        _engine = None
        AsyncSessionLocal = None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
