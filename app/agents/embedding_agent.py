# app/agents/embedding_agent.py
"""Embedding agent for generating recipe embeddings using LM Studio."""

import logging
from typing import Optional

import httpx

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class EmbeddingAgent:
    """Agent for generating text embeddings using LM Studio's embedding model."""

    base_url: str
    model: str
    api_key: str

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = str(settings.lm_studio_base_url).rstrip("/v1")
        self.model = str(settings.lm_studio_embedding_model)
        self.api_key = str(settings.lm_studio_api_key)

    async def generate_embedding(self, text: str) -> Optional[list[float]]:
        """
        Generate an embedding vector for the given text.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding, or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": text,
                    },
                )
                response.raise_for_status()

                data = response.json()
                embedding = data["data"][0]["embedding"]

                logger.debug(
                    "Generated embedding with %d dimensions for text: %s...",
                    len(embedding),
                    text[:50],
                )
                return embedding

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error generating embedding: %s - %s",
                e.response.status_code,
                e.response.text,
            )
            return None
        except (httpx.RequestError, KeyError, IndexError) as e:
            logger.error("Error generating embedding: %s", e)
            return None

    async def generate_recipe_embedding(
        self,
        title: str,
        description: str,
        ingredients: list[str],
        cuisine_type: Optional[str] = None,
    ) -> Optional[list[float]]:
        """
        Generate an embedding for a recipe by combining its key attributes.

        Args:
            title: Recipe title
            description: Recipe description
            ingredients: List of ingredient names
            cuisine_type: Optional cuisine type

        Returns:
            Embedding vector or None if failed
        """
        # Combine recipe information into a searchable text
        text_parts = [
            f"Recipe: {title}",
            f"Description: {description}",
            f"Ingredients: {', '.join(ingredients)}",
        ]

        if cuisine_type:
            text_parts.append(f"Cuisine: {cuisine_type}")

        combined_text = "\n".join(text_parts)

        return await self.generate_embedding(combined_text)


# Singleton instance
_embedding_agent: Optional[EmbeddingAgent] = None


def get_embedding_agent() -> EmbeddingAgent:
    """Get or create the embedding agent singleton."""
    global _embedding_agent  # noqa: PLW0603
    if _embedding_agent is None:
        _embedding_agent = EmbeddingAgent()
    return _embedding_agent


async def generate_recipe_embedding(
    title: str,
    description: str,
    ingredients: list[str],
    cuisine_type: Optional[str] = None,
) -> Optional[list[float]]:
    """
    Convenience function to generate a recipe embedding.

    Args:
        title: Recipe title
        description: Recipe description
        ingredients: List of ingredient names
        cuisine_type: Optional cuisine type

    Returns:
        Embedding vector or None if failed
    """
    agent = get_embedding_agent()
    return await agent.generate_recipe_embedding(
        title=title,
        description=description,
        ingredients=ingredients,
        cuisine_type=cuisine_type,
    )
