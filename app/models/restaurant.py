from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

BudgetBand = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    city: str
    cuisines: list[str]
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    votes: int = 0
    cost_for_two: Optional[int] = Field(default=None, ge=0)
    budget_band: Optional[BudgetBand] = None
    rest_type: str = ""
    meal_type: str = ""
    online_order: bool = False
    book_table: bool = False
    dish_liked: Optional[str] = None
    address: str = ""
    url: Optional[str] = None
