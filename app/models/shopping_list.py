# app/models/shopping_list.py
"""Pydantic models for Shopping List functionality."""

from typing import Optional

from pydantic import BaseModel, Field


class ShoppingItem(BaseModel):
    """A single item in a shopping list."""

    name: str = Field(..., description="Name of the item")
    quantity: str = Field(..., description="Quantity with unit (e.g., '2 cups', '500g')")
    aisle: str = Field(..., description="Store aisle category")
    checked: bool = Field(default=False, description="Whether the item has been checked off")
    notes: Optional[str] = Field(default=None, description="Additional notes for the item")


class ShoppingList(BaseModel):
    """A complete shopping list with items grouped by aisle."""

    items: list[ShoppingItem] = Field(default_factory=list, description="All shopping items")

    @property
    def by_aisle(self) -> dict[str, list[ShoppingItem]]:
        """Group items by their aisle category."""
        grouped: dict[str, list[ShoppingItem]] = {}
        for item in self.items:
            if item.aisle not in grouped:
                grouped[item.aisle] = []
            grouped[item.aisle].append(item)
        return grouped

    @property
    def unchecked_count(self) -> int:
        """Count of items not yet checked off."""
        return sum(1 for item in self.items if not item.checked)

    def to_aisle_dict(self) -> dict[str, list[str]]:
        """Convert to simple aisle -> item strings format for API response."""
        result: dict[str, list[str]] = {}
        for item in self.items:
            if item.aisle not in result:
                result[item.aisle] = []
            item_str = f"{item.quantity} {item.name}"
            if item.notes:
                item_str += f" ({item.notes})"
            result[item.aisle].append(item_str)
        return result
