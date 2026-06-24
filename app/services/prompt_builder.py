from __future__ import annotations

from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm.types import Message
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant


class PromptBuilder:
    """Assembles system and user prompts for Groq ranking requests."""

    DISH_LIKED_MAX_CHARS = 100

    def build(self, preferences: UserPreferences, candidates: list[Restaurant]) -> list[Message]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(
                preferences_text=self._serialize_preferences(preferences),
                candidates_text=self._serialize_candidates(candidates),
                top_n=preferences.top_n,
            )},
        ]

    def _serialize_preferences(self, preferences: UserPreferences) -> str:
        lines = [
            f"- location: {preferences.location}",
            f"- budget: {preferences.budget}",
            f"- cuisine: {preferences.cuisine}",
            f"- min_rating: {preferences.min_rating}",
            f"- top_n: {preferences.top_n}",
        ]
        if preferences.additional_preferences:
            lines.append(f"- additional_preferences: {preferences.additional_preferences}")
        return "\n".join(lines)

    def _serialize_candidates(self, candidates: list[Restaurant]) -> str:
        lines: list[str] = []
        for index, restaurant in enumerate(candidates, start=1):
            dish_liked = self._truncate(restaurant.dish_liked)
            cuisines = ", ".join(restaurant.cuisines)
            rating = restaurant.rating if restaurant.rating is not None else "N/A"
            cost = restaurant.cost_for_two if restaurant.cost_for_two is not None else "N/A"
            lines.append(
                f"{index}. id={restaurant.id} | name={restaurant.name} | "
                f"cuisines={cuisines} | rating={rating} | cost_for_two={cost} | "
                f"rest_type={restaurant.rest_type} | meal_type={restaurant.meal_type}"
                + (f" | dish_liked={dish_liked}" if dish_liked else "")
            )
        return "\n".join(lines)

    def _truncate(self, value: str | None) -> str:
        if not value:
            return ""
        if len(value) <= self.DISH_LIKED_MAX_CHARS:
            return value
        return value[: self.DISH_LIKED_MAX_CHARS - 3] + "..."
