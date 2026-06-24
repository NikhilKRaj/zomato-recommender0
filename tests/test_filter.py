import pandas as pd
import pytest

from app.models.preferences import UserPreferences
from app.services.filter import CandidateFilter, parse_additional_filters
from app.services.restaurant_store import RestaurantStore


def _sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "restaurant_id": "r1",
                "name": "Truffles",
                "location": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["italian", "american"],
                "rating": 4.5,
                "votes": 500,
                "cost_for_two": 500,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "meal_type": "Cafes",
                "online_order": True,
                "book_table": True,
                "dish_liked": None,
                "address": "Koramangala 1",
                "url": None,
            },
            {
                "restaurant_id": "r2",
                "name": "Pizza Hub",
                "location": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["italian", "pizza"],
                "rating": 4.2,
                "votes": 800,
                "cost_for_two": 450,
                "budget_band": "medium",
                "rest_type": "Quick Bites",
                "meal_type": "Delivery",
                "online_order": True,
                "book_table": False,
                "dish_liked": None,
                "address": "Koramangala 2",
                "url": None,
            },
            {
                "restaurant_id": "r3",
                "name": "Chinese Wok",
                "location": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["chinese"],
                "rating": 4.8,
                "votes": 300,
                "cost_for_two": 400,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "meal_type": "Delivery",
                "online_order": False,
                "book_table": False,
                "dish_liked": None,
                "address": "Koramangala 3",
                "url": None,
            },
            {
                "restaurant_id": "r4",
                "name": "Budget Italian",
                "location": "Indiranagar",
                "city": "Bangalore",
                "cuisines": ["italian"],
                "rating": 3.8,
                "votes": 100,
                "cost_for_two": 250,
                "budget_band": "low",
                "rest_type": "Cafe",
                "meal_type": "Cafes",
                "online_order": True,
                "book_table": False,
                "dish_liked": None,
                "address": "Indiranagar 1",
                "url": None,
            },
        ]
    )


@pytest.fixture
def store() -> RestaurantStore:
    return RestaurantStore(_sample_dataframe())


@pytest.fixture
def candidate_filter() -> CandidateFilter:
    return CandidateFilter()


def test_filter_returns_empty_when_no_match(candidate_filter: CandidateFilter, store: RestaurantStore):
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Mexican",
        min_rating=4.0,
    )
    assert candidate_filter.filter(preferences, store) == []


def test_filter_matches_location_city_and_cuisine(candidate_filter: CandidateFilter, store: RestaurantStore):
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
    )
    candidates = candidate_filter.filter(preferences, store)
    assert 1 <= len(candidates) <= 30
    assert all(any("italian" in cuisine for cuisine in restaurant.cuisines) for restaurant in candidates)
    assert all(restaurant.budget_band == "medium" for restaurant in candidates)
    assert all((restaurant.rating or 0) >= 4.0 for restaurant in candidates)


def test_filter_respects_candidate_cap(candidate_filter: CandidateFilter):
    rows = []
    for index in range(40):
        rows.append(
            {
                "restaurant_id": f"r{index}",
                "name": f"Restaurant {index}",
                "location": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["italian"],
                "rating": 4.0 + (index % 10) * 0.05,
                "votes": index,
                "cost_for_two": 500,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "meal_type": "Cafes",
                "online_order": True,
                "book_table": False,
                "dish_liked": None,
                "address": f"Addr {index}",
                "url": None,
            }
        )
    store = RestaurantStore(pd.DataFrame(rows))
    preferences = UserPreferences(location="Koramangala", budget="medium", cuisine="Italian")
    candidates = candidate_filter.filter(preferences, store, max_candidates=30)
    assert len(candidates) == 30


def test_filter_additional_delivery_preference(candidate_filter: CandidateFilter, store: RestaurantStore):
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="delivery",
    )
    candidates = candidate_filter.filter(preferences, store)
    assert candidates
    assert all(restaurant.online_order for restaurant in candidates)
    assert all(restaurant.name != "Chinese Wok" for restaurant in candidates)


def test_filter_additional_keyword_on_rest_type(candidate_filter: CandidateFilter, store: RestaurantStore):
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_preferences="quick bites",
    )
    candidates = candidate_filter.filter(preferences, store)
    assert len(candidates) == 1
    assert candidates[0].name == "Pizza Hub"


def test_parse_additional_filters():
    parsed = parse_additional_filters("delivery, family-friendly")
    assert parsed.require_online_order is True
    assert parsed.require_book_table is False
    assert "family-friendly" in parsed.keywords


def test_user_preferences_validation():
    with pytest.raises(ValueError):
        UserPreferences(location="", budget="medium", cuisine="Italian")

    with pytest.raises(ValueError):
        UserPreferences(
            location="Koramangala",
            budget="medium",
            cuisine="Italian",
            additional_preferences="x" * 501,
        )


def test_filter_integration_with_cached_data():
    cache_path = pytest.importorskip("pathlib").Path(__file__).resolve().parents[1] / "data/processed/restaurants.parquet"
    if not cache_path.exists():
        pytest.skip("Processed dataset cache not available")

    store = RestaurantStore(pd.read_parquet(cache_path))
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
    )
    candidates = CandidateFilter().filter(preferences, store)
    assert 1 <= len(candidates) <= 30
    assert all(any("italian" in cuisine for cuisine in restaurant.cuisines) for restaurant in candidates)


def test_filter_dedupes_duplicate_restaurant_names():
    rows = [
        {
            "restaurant_id": "r1",
            "name": "Imperio Restaurant",
            "location": "Whitefield",
            "city": "Bangalore",
            "cuisines": ["biryani"],
            "rating": 4.4,
            "votes": 500,
            "cost_for_two": 800,
            "budget_band": "high",
            "rest_type": "Casual Dining",
            "meal_type": "Delivery",
            "online_order": True,
            "book_table": False,
            "dish_liked": None,
            "address": "Address A",
            "url": None,
        },
        {
            "restaurant_id": "r2",
            "name": "Imperio Restaurant",
            "location": "Whitefield",
            "city": "Bangalore",
            "cuisines": ["biryani"],
            "rating": 4.3,
            "votes": 400,
            "cost_for_two": 800,
            "budget_band": "high",
            "rest_type": "Casual Dining",
            "meal_type": "Delivery",
            "online_order": True,
            "book_table": False,
            "dish_liked": None,
            "address": "Address B",
            "url": None,
        },
        {
            "restaurant_id": "r3",
            "name": "Meghana Foods",
            "location": "Whitefield",
            "city": "Bangalore",
            "cuisines": ["biryani"],
            "rating": 4.5,
            "votes": 600,
            "cost_for_two": 800,
            "budget_band": "high",
            "rest_type": "Casual Dining",
            "meal_type": "Delivery",
            "online_order": True,
            "book_table": False,
            "dish_liked": None,
            "address": "Address C",
            "url": None,
        },
    ]
    store = RestaurantStore(pd.DataFrame(rows))
    preferences = UserPreferences(
        location="Whitefield",
        budget="high",
        cuisine="biryani",
        min_rating=4.0,
    )
    candidates = CandidateFilter().filter(preferences, store)
    names = [restaurant.name.casefold() for restaurant in candidates]
    assert len(names) == len(set(names))
    imperio = [restaurant for restaurant in candidates if restaurant.name == "Imperio Restaurant"]
    assert len(imperio) == 1
    assert imperio[0].id == "r1"
