"""Print candidate restaurants for sample preferences."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.preferences import UserPreferences
from app.services.data_loader import DataLoader
from app.services.filter import CandidateFilter


def main() -> None:
    loader = DataLoader()
    store = loader.get_restaurant_store()
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
    )

    candidates = CandidateFilter().filter(preferences, store)
    print(f"Found {len(candidates)} candidates for {preferences.location} / {preferences.cuisine}")
    for restaurant in candidates[:10]:
        print(
            f"- {restaurant.name} | rating={restaurant.rating} | votes={restaurant.votes} | "
            f"cuisines={restaurant.cuisines}"
        )


if __name__ == "__main__":
    main()
