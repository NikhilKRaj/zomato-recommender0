from __future__ import annotations

from app.models.restaurant import Restaurant


class FallbackRanker:
    """Rule-based ranking when the LLM is unavailable."""

    def rank(self, candidates: list[Restaurant], top_n: int = 5) -> list[Restaurant]:
        if not candidates:
            return []

        limit = max(1, min(top_n, len(candidates)))
        return sorted(
            candidates,
            key=lambda restaurant: (
                restaurant.rating if restaurant.rating is not None else -1.0,
                restaurant.votes,
            ),
            reverse=True,
        )[:limit]
