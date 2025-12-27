# app/models/recipe.py
"""Pydantic models for Recipe generation."""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """An ingredient in a recipe."""

    name: str = Field(..., description="Name of the ingredient")
    amount: float = Field(..., description="Quantity of the ingredient")
    unit: str = Field(..., description="Unit of measurement (e.g., cups, grams, pieces)")
    aisle: str = Field(
        ...,
        description="Grocery store aisle category (e.g., Produce, Meat & Poultry, Dairy)",
    )
    notes: Optional[str] = Field(
        default=None, description="Additional notes (e.g., diced, room temperature)"
    )


class Instruction(BaseModel):
    """A single instruction step in a recipe."""

    step: int = Field(..., description="Step number (1-indexed)")
    description: str = Field(..., description="Detailed instruction for this step")
    duration_minutes: Optional[int] = Field(
        default=None, description="Estimated time for this step in minutes"
    )
    ingredients_used: list[str] = Field(
        default_factory=list,
        description="List of ingredient names used in this step",
    )


class Recipe(BaseModel):
    """Complete recipe with ingredients and instructions."""

    title: str = Field(..., description="Recipe title")
    description: str = Field(..., description="Brief description of the dish")
    servings: int = Field(..., ge=1, description="Number of servings")
    prep_time_minutes: int = Field(..., ge=0, description="Preparation time in minutes")
    cook_time_minutes: int = Field(..., ge=0, description="Cooking time in minutes")
    ingredients: list[Ingredient] = Field(..., description="List of ingredients")
    instructions: list[Instruction] = Field(
        ..., description="Step-by-step instructions"
    )

    @property
    def total_time_minutes(self) -> int:
        """Total time to prepare and cook the recipe."""
        return self.prep_time_minutes + self.cook_time_minutes


class GenerateRecipeRequest(BaseModel):
    """Request body for generating a recipe."""

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language description of the desired recipe",
        examples=["healthy chicken dinner for 4", "quick vegan pasta"],
    )
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Dietary restrictions or preferences",
        examples=[["gluten-free", "dairy-free"], ["vegan"], ["keto"]],
    )
    cuisine_type: Optional[str] = Field(
        default=None,
        description="Preferred cuisine style",
        examples=["Italian", "Mexican", "Asian", "Mediterranean"],
    )


class GenerateRecipeResponse(BaseModel):
    """Response body for a generated recipe."""

    id: UUID = Field(default_factory=uuid4, description="Unique recipe identifier")
    recipe: Recipe = Field(..., description="The generated recipe")
    shopping_list: dict[str, list[str]] = Field(
        ...,
        description="Shopping list grouped by aisle",
        examples=[
            {
                "Meat & Poultry": ["4 chicken breasts"],
                "Produce": ["2 lemons", "1 bunch fresh oregano"],
                "Pantry": ["olive oil", "garlic"],
            }
        ],
    )
