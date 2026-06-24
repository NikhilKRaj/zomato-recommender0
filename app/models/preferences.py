from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.models.restaurant import BudgetBand

BudgetChoice = Literal["low", "medium", "high"]


class UserPreferences(BaseModel):
    location: str
    budget: BudgetChoice
    cuisine: str
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=10)

    @field_validator("location", "cuisine")
    @classmethod
    def strip_and_validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned

    @field_validator("budget", mode="before")
    @classmethod
    def normalize_budget(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("additional_preferences")
    @classmethod
    def validate_additional_preferences_length(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if len(cleaned) > settings.additional_preferences_max_length:
            raise ValueError(
                f"additional_preferences must be at most "
                f"{settings.additional_preferences_max_length} characters"
            )
        return cleaned

    @property
    def budget_band(self) -> BudgetBand:
        return self.budget
