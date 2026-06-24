import pandas as pd

from app.services.data_loader import DataLoader
from app.services.restaurant_store import RestaurantStore


def test_restaurant_store_metadata():
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "abc123",
                "name": "Truffles",
                "location": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["italian", "american"],
                "rating": 4.5,
                "votes": 100,
                "cost_for_two": 500,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "meal_type": "Cafes",
                "online_order": True,
                "book_table": True,
                "dish_liked": None,
                "address": "123 Street",
                "url": "https://example.com",
            }
        ]
    )
    store = RestaurantStore(df)

    locations = store.get_locations()
    assert "Koramangala" in locations
    assert "Bangalore" in locations

    cuisines = store.get_cuisines()
    assert "italian" in cuisines

    restaurant = store.get_by_id("abc123")
    assert restaurant is not None
    assert restaurant.name == "Truffles"
    assert restaurant.id == "abc123"


def test_data_loader_uses_cache(tmp_path):
    cache_path = tmp_path / "restaurants.parquet"
    sample = pd.DataFrame(
        [
            {
                "restaurant_id": "id1",
                "name": "Sample",
                "location": "Banashankari",
                "city": "Bangalore",
                "cuisines": ["north indian"],
                "rating": 4.0,
                "votes": 10,
                "cost_for_two": 400,
                "budget_band": "medium",
                "rest_type": "Casual Dining",
                "meal_type": "Buffet",
                "online_order": True,
                "book_table": False,
                "dish_liked": None,
                "address": "Addr",
                "url": None,
            }
        ]
    )
    sample.to_parquet(cache_path, index=False)

    loader = DataLoader(cache_path=cache_path)
    df = loader.load()
    assert len(df) == 1
    assert loader.get_locations() == ["Banashankari", "Bangalore"]
    assert loader.get_cuisines() == ["north indian"]
