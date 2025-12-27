# app/api/recipes.py
"""Recipe generation API endpoints."""

import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recipe_agent import generate_recipe, build_shopping_list
from app.agents.embedding_agent import generate_recipe_embedding
from app.database.connection import get_async_session
from app.database.repositories import RecipeRepository
from app.models.recipe import GenerateRecipeRequest, GenerateRecipeResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get(
    "/health",
    summary="Check recipe service health",
    description="Verify the recipe generation service is operational.",
)
async def health_check() -> dict[str, str]:
    """Health check endpoint for the recipe service."""
    return {"status": "healthy", "service": "recipe-generator"}


@router.post(
    "/generate",
    response_model=GenerateRecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a recipe from a natural language prompt",
    description="""
    Generate a complete recipe with ingredients and step-by-step instructions
    using AI. The response includes a shopping list organized by grocery aisle.
    The recipe is automatically saved to the database with embeddings for
    similarity search.
    
    **Example prompts:**
    - "healthy chicken dinner for 4"
    - "quick vegan pasta under 30 minutes"
    - "traditional Italian lasagna"
    """,
)
async def generate_recipe_endpoint(
    request: GenerateRecipeRequest,
    session: AsyncSession = Depends(get_async_session),
) -> GenerateRecipeResponse:
    """
    Generate a recipe based on the user's prompt.

    - **prompt**: Natural language description of the desired recipe
    - **dietary_preferences**: Optional list of dietary restrictions
    - **cuisine_type**: Optional preferred cuisine style
    """
    try:
        logger.info("Generating recipe for prompt: %s", request.prompt)

        # Generate the recipe using the AI agent
        recipe = await generate_recipe(
            prompt=request.prompt,
            dietary_preferences=request.dietary_preferences,
            cuisine_type=request.cuisine_type,
        )

        # Build the shopping list from the recipe
        shopping_list = build_shopping_list(recipe)

        # Create response with unique ID
        response = GenerateRecipeResponse(
            id=uuid4(),
            recipe=recipe,
            shopping_list=shopping_list,
        )

        # Generate embedding for similarity search
        ingredient_names = [ing.name for ing in recipe.ingredients]
        embedding = await generate_recipe_embedding(
            title=recipe.title,
            description=recipe.description,
            ingredients=ingredient_names,
            cuisine_type=request.cuisine_type,
        )

        # Save to database
        repo = RecipeRepository(session)
        await repo.create(
            recipe_response=response,
            original_prompt=request.prompt,
            dietary_preferences=request.dietary_preferences,
            cuisine_type=request.cuisine_type,
            embedding=embedding,
        )

        logger.info("Successfully generated and saved recipe: %s", recipe.title)
        return response

    except Exception as e:
        logger.error("Failed to generate recipe: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate recipe. Please ensure LM Studio is running. Error: {str(e)}",
        ) from e


@router.get(
    "/{recipe_id}",
    response_model=GenerateRecipeResponse,
    summary="Get a recipe by ID",
)
async def get_recipe(
    recipe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> GenerateRecipeResponse:
    """Retrieve a specific recipe by its ID."""
    repo = RecipeRepository(session)
    db_recipe = await repo.get_by_id(recipe_id)

    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )

    # Convert DB model back to response model
    from app.models.recipe import Recipe, Ingredient, Instruction

    ingredients = [Ingredient(**ing) for ing in db_recipe.ingredients]
    instructions = [Instruction(**inst) for inst in db_recipe.instructions]

    recipe = Recipe(
        title=db_recipe.title,
        description=db_recipe.description,
        servings=db_recipe.servings,
        prep_time_minutes=db_recipe.prep_time_minutes,
        cook_time_minutes=db_recipe.cook_time_minutes,
        ingredients=ingredients,
        instructions=instructions,
    )

    return GenerateRecipeResponse(
        id=db_recipe.id,
        recipe=recipe,
        shopping_list=db_recipe.shopping_list,
    )


@router.get(
    "/{recipe_id}/similar",
    response_model=list[GenerateRecipeResponse],
    summary="Find similar recipes",
)
async def find_similar_recipes(
    recipe_id: UUID,
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_async_session),
) -> list[GenerateRecipeResponse]:
    """Find recipes similar to the given recipe using vector similarity."""
    repo = RecipeRepository(session)

    # Get the source recipe
    source_recipe = await repo.get_by_id(recipe_id)
    if not source_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )

    if source_recipe.embedding is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe does not have an embedding for similarity search",
        )

    # Find similar recipes
    similar = await repo.find_similar(
        embedding=source_recipe.embedding,
        limit=limit,
        exclude_id=recipe_id,
    )

    # Convert to response models
    from app.models.recipe import Recipe, Ingredient, Instruction

    results = []
    for db_recipe in similar:
        ingredients = [Ingredient(**ing) for ing in db_recipe.ingredients]
        instructions = [Instruction(**inst) for inst in db_recipe.instructions]

        recipe = Recipe(
            title=db_recipe.title,
            description=db_recipe.description,
            servings=db_recipe.servings,
            prep_time_minutes=db_recipe.prep_time_minutes,
            cook_time_minutes=db_recipe.cook_time_minutes,
            ingredients=ingredients,
            instructions=instructions,
        )

        results.append(
            GenerateRecipeResponse(
                id=db_recipe.id,
                recipe=recipe,
                shopping_list=db_recipe.shopping_list,
            )
        )

    return results


@router.get(
    "/",
    response_model=list[GenerateRecipeResponse],
    summary="List recent recipes",
)
async def list_recipes(
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, min_length=2),
    session: AsyncSession = Depends(get_async_session),
) -> list[GenerateRecipeResponse]:
    """List recent recipes, optionally filtered by search term."""
    repo = RecipeRepository(session)

    if search:
        db_recipes = await repo.search_by_title(search, limit=limit)
    else:
        db_recipes = await repo.list_recent(limit=limit)

    # Convert to response models
    from app.models.recipe import Recipe, Ingredient, Instruction

    results = []
    for db_recipe in db_recipes:
        ingredients = [Ingredient(**ing) for ing in db_recipe.ingredients]
        instructions = [Instruction(**inst) for inst in db_recipe.instructions]

        recipe = Recipe(
            title=db_recipe.title,
            description=db_recipe.description,
            servings=db_recipe.servings,
            prep_time_minutes=db_recipe.prep_time_minutes,
            cook_time_minutes=db_recipe.cook_time_minutes,
            ingredients=ingredients,
            instructions=instructions,
        )

        results.append(
            GenerateRecipeResponse(
                id=db_recipe.id,
                recipe=recipe,
                shopping_list=db_recipe.shopping_list,
            )
        )

    return results


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe",
)
async def delete_recipe(
    recipe_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a recipe by ID."""
    repo = RecipeRepository(session)
    deleted = await repo.delete(recipe_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )
