# app/database/repositories.py
"""Repository pattern for database operations."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import RecipeDB
from app.models.recipe import GenerateRecipeResponse

logger = logging.getLogger(__name__)


class RecipeRepository:
    """Repository for Recipe database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        recipe_response: GenerateRecipeResponse,
        original_prompt: str,
        dietary_preferences: Optional[list[str]] = None,
        cuisine_type: Optional[str] = None,
        embedding: Optional[list[float]] = None,
    ) -> RecipeDB:
        """
        Create a new recipe in the database.

        Args:
            recipe_response: The generated recipe response
            original_prompt: The original user prompt
            dietary_preferences: List of dietary preferences
            cuisine_type: Cuisine type preference
            embedding: Vector embedding for similarity search

        Returns:
            The created RecipeDB instance
        """
        recipe = recipe_response.recipe

        db_recipe = RecipeDB(
            id=recipe_response.id,
            title=recipe.title,
            description=recipe.description,
            servings=recipe.servings,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            ingredients=[ing.model_dump() for ing in recipe.ingredients],
            instructions=[inst.model_dump() for inst in recipe.instructions],
            shopping_list=recipe_response.shopping_list,
            original_prompt=original_prompt,
            dietary_preferences=dietary_preferences,
            cuisine_type=cuisine_type,
            embedding=embedding,
        )

        self.session.add(db_recipe)
        await self.session.flush()

        logger.info("Created recipe in database: %s", db_recipe.id)
        return db_recipe

    async def get_by_id(self, recipe_id: UUID) -> Optional[RecipeDB]:
        """Get a recipe by its ID."""
        result = await self.session.execute(
            select(RecipeDB).where(RecipeDB.id == recipe_id)
        )
        return result.scalar_one_or_none()

    async def find_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        exclude_id: Optional[UUID] = None,
    ) -> list[RecipeDB]:
        """
        Find similar recipes using vector similarity search.

        Args:
            embedding: The query embedding vector
            limit: Maximum number of results to return
            exclude_id: Optional recipe ID to exclude from results

        Returns:
            List of similar recipes ordered by similarity
        """
        # Use pgvector's cosine distance operator (<=>)
        query = (
            select(RecipeDB)
            .where(RecipeDB.embedding.isnot(None))
            .order_by(RecipeDB.embedding.cosine_distance(embedding))
            .limit(limit)
        )

        if exclude_id:
            query = query.where(RecipeDB.id != exclude_id)

        result = await self.session.execute(query)
        recipes = list(result.scalars().all())

        logger.info("Found %d similar recipes", len(recipes))
        return recipes

    async def search_by_title(
        self,
        search_term: str,
        limit: int = 10,
    ) -> list[RecipeDB]:
        """Search recipes by title (case-insensitive)."""
        result = await self.session.execute(
            select(RecipeDB)
            .where(RecipeDB.title.ilike(f"%{search_term}%"))
            .order_by(RecipeDB.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_recent(self, limit: int = 20) -> list[RecipeDB]:
        """Get the most recently created recipes."""
        result = await self.session.execute(
            select(RecipeDB)
            .order_by(RecipeDB.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, recipe_id: UUID) -> bool:
        """Delete a recipe by ID. Returns True if deleted."""
        recipe = await self.get_by_id(recipe_id)
        if recipe:
            await self.session.delete(recipe)
            await self.session.flush()
            logger.info("Deleted recipe: %s", recipe_id)
            return True
        return False
