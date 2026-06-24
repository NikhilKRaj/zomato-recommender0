from __future__ import annotations

import pytest

from app.models.restaurant import Restaurant
from app.services.fallback_ranker import FallbackRanker


def _restaurant(restaurant_id: str, rating: float | None, votes: int) -> Restaurant:
    return Restaurant(
        id=restaurant_id,
        name=restaurant_id,
        location="Koramangala",
        city="Bangalore",
        cuisines=["italian"],
        rating=rating,
        votes=votes,
        cost_for_two=500,
        budget_band="medium",
    )


def test_fallback_ranker_sorts_by_rating_then_votes():
    ranker = FallbackRanker()
    candidates = [
        _restaurant("a", 4.5, 100),
        _restaurant("b", 4.8, 50),
        _restaurant("c", 4.8, 200),
        _restaurant("d", None, 999),
    ]

    ranked = ranker.rank(candidates, top_n=3)
    assert [restaurant.id for restaurant in ranked] == ["c", "b", "a"]


def test_fallback_ranker_respects_top_n():
    ranker = FallbackRanker()
    candidates = [
        _restaurant("a", 4.0, 10),
        _restaurant("b", 4.5, 10),
        _restaurant("c", 4.2, 10),
    ]
    ranked = ranker.rank(candidates, top_n=2)
    assert len(ranked) == 2
    assert ranked[0].id == "b"


def test_fallback_ranker_empty_input():
    assert FallbackRanker().rank([], top_n=5) == []
