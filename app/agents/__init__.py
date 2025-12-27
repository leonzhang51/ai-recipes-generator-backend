# app/agents/__init__.py
"""AI Agents for recipe generation using PydanticAI."""

from app.agents.recipe_agent import recipe_agent, generate_recipe, build_shopping_list
from app.agents.embedding_agent import (
    EmbeddingAgent,
    get_embedding_agent,
    generate_recipe_embedding,
)

__all__ = [
    "recipe_agent",
    "generate_recipe",
    "build_shopping_list",
    "EmbeddingAgent",
    "get_embedding_agent",
    "generate_recipe_embedding",
]
