# app/database/models.py
"""SQLAlchemy models for PostgreSQL with pgvector."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.settings import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class RecipeDB(Base):
    """Recipe database model with vector embedding for similarity search."""

    __tablename__ = "recipes"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Recipe metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    cook_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Store ingredients and instructions as JSONB
    ingredients: Mapped[dict] = mapped_column(JSONB, nullable=False)
    instructions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    shopping_list: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Original prompt and preferences
    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    dietary_preferences: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    cuisine_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Vector embedding for similarity search (embeddinggemma-300m uses 768 dimensions)
    embedding: Mapped[Optional[list]] = mapped_column(
        Vector(get_settings().embedding_dimensions),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title='{self.title}')>"
