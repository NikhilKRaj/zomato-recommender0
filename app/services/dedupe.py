from __future__ import annotations

from app.models.recommendation import Recommendation
from app.models.restaurant import Restaurant


def _normalized_name(name: str) -> str:
    return name.strip().casefold()


def dedupe_restaurants_by_name(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Keep one entry per restaurant name, preserving list order (best first)."""
    seen_names: set[str] = set()
    deduped: list[Restaurant] = []
    for restaurant in restaurants:
        key = _normalized_name(restaurant.name)
        if key in seen_names:
            continue
        seen_names.add(key)
        deduped.append(restaurant)
    return deduped


def dedupe_recommendations_by_name(recommendations: list[Recommendation]) -> list[Recommendation]:
    """Keep one recommendation per restaurant name, preserving rank order."""
    seen_names: set[str] = set()
    deduped: list[Recommendation] = []
    for item in sorted(recommendations, key=lambda entry: entry.rank):
        key = _normalized_name(item.restaurant.name)
        if key in seen_names:
            continue
        seen_names.add(key)
        deduped.append(item)

    return [
        Recommendation(
            rank=index,
            restaurant=item.restaurant,
            explanation=item.explanation,
        )
        for index, item in enumerate(deduped, start=1)
    ]
