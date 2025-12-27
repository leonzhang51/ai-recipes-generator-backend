# app/agents/recipe_agent.py
"""PydanticAI agent for recipe generation using LM Studio."""

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.settings import get_settings
from app.models.recipe import Recipe, Ingredient, Instruction


class RecipeGenerationContext(BaseModel):
    """Context passed to the recipe generation agent."""

    prompt: str = Field(..., description="User's recipe request")
    dietary_preferences: list[str] = Field(default_factory=list)
    cuisine_type: Optional[str] = None


class GeneratedRecipe(BaseModel):
    """Output schema for the AI-generated recipe."""

    title: str = Field(..., description="A descriptive title for the recipe")
    description: str = Field(
        ..., description="A brief, appetizing description of the dish (1-2 sentences)"
    )
    servings: int = Field(..., ge=1, le=20, description="Number of servings")
    prep_time_minutes: int = Field(..., ge=0, le=180, description="Prep time in minutes")
    cook_time_minutes: int = Field(..., ge=0, le=480, description="Cook time in minutes")
    ingredients: list[Ingredient] = Field(
        ..., min_length=1, description="Complete list of ingredients"
    )
    instructions: list[Instruction] = Field(
        ..., min_length=1, description="Step-by-step cooking instructions"
    )


# System prompt for the recipe generation agent
RECIPE_SYSTEM_PROMPT = """You are an expert chef and recipe developer. Your task is to create detailed, 
accurate, and delicious recipes based on user requests.

When generating recipes:
1. Create realistic, tested-quality recipes with accurate measurements
2. Assign each ingredient to an appropriate grocery aisle category:
   - Produce (fruits, vegetables, herbs)
   - Meat & Poultry
   - Seafood
   - Dairy & Eggs
   - Bakery
   - Frozen Foods
   - Pantry (oils, spices, canned goods, pasta, rice)
   - Beverages
   - Condiments & Sauces
3. Ensure every ingredient listed is used in at least one instruction step
4. Include the ingredient names used in each instruction's ingredients_used field
5. Provide realistic prep and cook times
6. Write clear, detailed instructions that a home cook can follow

If dietary preferences are specified, ensure the recipe fully complies with them.
If a cuisine type is specified, create an authentic dish from that culinary tradition."""


def create_recipe_agent() -> Agent[None, GeneratedRecipe]:
    """Create and configure the recipe generation agent."""
    settings = get_settings()

    # Configure the LM Studio model (OpenAI-compatible) using OpenAIProvider
    provider = OpenAIProvider(
        base_url=settings.lm_studio_base_url,
        api_key=settings.lm_studio_api_key,
    )

    model = OpenAIChatModel(
        settings.lm_studio_model,
        provider=provider,
    )

    agent: Agent[None, GeneratedRecipe] = Agent(
        model=model,
        output_type=GeneratedRecipe,
        system_prompt=RECIPE_SYSTEM_PROMPT,
        retries=2,
    )

    return agent


# Global agent instance (lazy initialization)
_recipe_agent: Optional[Agent[None, GeneratedRecipe]] = None


def get_recipe_agent() -> Agent[None, GeneratedRecipe]:
    """Get or create the recipe agent singleton."""
    global _recipe_agent  # noqa: PLW0603
    if _recipe_agent is None:
        _recipe_agent = create_recipe_agent()
    return _recipe_agent


# Convenience alias
recipe_agent = get_recipe_agent


async def generate_recipe(
    prompt: str,
    dietary_preferences: Optional[list[str]] = None,
    cuisine_type: Optional[str] = None,
) -> Recipe:
    """
    Generate a recipe using the AI agent.

    Args:
        prompt: Natural language description of the desired recipe
        dietary_preferences: List of dietary restrictions (e.g., ["gluten-free", "vegan"])
        cuisine_type: Preferred cuisine style (e.g., "Italian", "Mexican")

    Returns:
        A fully structured Recipe object
    """
    agent = get_recipe_agent()

    # Build the full prompt with context
    full_prompt = f"Create a recipe for: {prompt}"
    if dietary_preferences:
        full_prompt += f"\nDietary requirements: {', '.join(dietary_preferences)}"
    if cuisine_type:
        full_prompt += f"\nCuisine style: {cuisine_type}"

    # Run the agent
    result = await agent.run(full_prompt)

    # Convert to our Recipe model
    generated = result.output
    return Recipe(
        title=generated.title,
        description=generated.description,
        servings=generated.servings,
        prep_time_minutes=generated.prep_time_minutes,
        cook_time_minutes=generated.cook_time_minutes,
        ingredients=generated.ingredients,
        instructions=generated.instructions,
    )


def build_shopping_list(recipe: Recipe) -> dict[str, list[str]]:
    """
    Build a shopping list grouped by aisle from a recipe.

    Args:
        recipe: The recipe to extract ingredients from

    Returns:
        Dictionary mapping aisle names to lists of ingredient strings
    """
    shopping_list: dict[str, list[str]] = {}

    for ingredient in recipe.ingredients:
        aisle = ingredient.aisle
        if aisle not in shopping_list:
            shopping_list[aisle] = []

        # Format the ingredient string
        item_str = f"{ingredient.amount} {ingredient.unit} {ingredient.name}"
        if ingredient.notes:
            item_str += f" ({ingredient.notes})"

        shopping_list[aisle].append(item_str)

    return shopping_list
