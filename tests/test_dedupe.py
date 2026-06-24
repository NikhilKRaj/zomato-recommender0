from app.models.recommendation import Recommendation
from app.models.restaurant import Restaurant
from app.services.dedupe import dedupe_recommendations_by_name, dedupe_restaurants_by_name


def _restaurant(restaurant_id: str, name: str, rating: float = 4.0, votes: int = 100) -> Restaurant:
    return Restaurant(
        id=restaurant_id,
        name=name,
        location="Whitefield",
        city="Bangalore",
        cuisines=["biryani"],
        rating=rating,
        votes=votes,
        cost_for_two=800,
        budget_band="high",
    )


def test_dedupe_restaurants_by_name_keeps_best_first():
    restaurants = [
        _restaurant("a", "Imperio Restaurant", rating=4.4, votes=500),
        _restaurant("b", "Imperio Restaurant", rating=4.3, votes=400),
        _restaurant("c", "Meghana Foods", rating=4.5, votes=600),
    ]
    deduped = dedupe_restaurants_by_name(restaurants)
    assert [restaurant.id for restaurant in deduped] == ["a", "c"]


def test_dedupe_recommendations_by_name_re_ranks():
    recommendations = [
        Recommendation(rank=1, restaurant=_restaurant("a", "Imperio Restaurant"), explanation="first"),
        Recommendation(rank=2, restaurant=_restaurant("b", "Imperio Restaurant"), explanation="duplicate"),
        Recommendation(rank=3, restaurant=_restaurant("c", "Meghana Foods"), explanation="unique"),
    ]
    deduped = dedupe_recommendations_by_name(recommendations)
    assert len(deduped) == 2
    assert deduped[0].restaurant.id == "a"
    assert deduped[1].restaurant.id == "c"
    assert [item.rank for item in deduped] == [1, 2]
