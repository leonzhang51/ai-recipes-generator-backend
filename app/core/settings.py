# app/core/settings.py
"""Application settings using Pydantic Settings for configuration management."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    project_name: str = Field(
        default="AI Recipe Generator",
        description="Name of the application",
    )
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")

    # LM Studio Configuration
    lm_studio_base_url: str = Field(
        default="http://127.0.0.1:1234/v1",
        description="Base URL for LM Studio OpenAI-compatible API",
    )
    lm_studio_model: str = Field(
        default="qwen3-vl-4b-instruct-mlx",
        description="Chat/instruct model name in LM Studio",
    )
    lm_studio_embedding_model: str = Field(
        default="text-embedding-embeddinggemma-300m-qat",
        description="Embedding model name in LM Studio",
    )
    lm_studio_api_key: str = Field(
        default="lm-studio",
        description="API key for LM Studio (usually 'lm-studio' for local)",
    )

    # AI Generation Settings
    ai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for AI generation (0=deterministic, 2=creative)",
    )
    ai_max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens for AI response",
    )
    ai_timeout_seconds: int = Field(
        default=120,
        ge=10,
        le=300,
        description="Timeout for AI API calls in seconds",
    )

    # Embedding Settings
    embedding_dimensions: int = Field(
        default=768,
        description="Dimensions of the embedding vector (embeddinggemma-300m uses 768)",
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/recipes",
        description="PostgreSQL async connection URL",
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Database connection pool size",
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=30,
        description="Maximum overflow connections",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
