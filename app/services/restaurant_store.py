from __future__ import annotations

from typing import Iterator, Optional

import pandas as pd

from app.data.preprocessor import parse_cuisines
from app.models.restaurant import Restaurant


def _normalize_cuisines(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, str):
        return parse_cuisines(value)
    if isinstance(value, (list, tuple)) or hasattr(value, "__iter__"):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return []


def _row_to_restaurant(row: dict) -> Restaurant:
    return Restaurant(
        id=row["restaurant_id"],
        name=row["name"],
        location=row["location"],
        city=row["city"],
        cuisines=_normalize_cuisines(row.get("cuisines")),
        rating=row.get("rating"),
        votes=int(row.get("votes") or 0),
        cost_for_two=row.get("cost_for_two"),
        budget_band=row.get("budget_band"),
        rest_type=row.get("rest_type") or "",
        meal_type=row.get("meal_type") or "",
        online_order=bool(row.get("online_order")),
        book_table=bool(row.get("book_table")),
        dish_liked=row.get("dish_liked"),
        address=row.get("address") or "",
        url=row.get("url"),
    )


class RestaurantStore:
    """In-memory restaurant store backed by a processed DataFrame."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df

    def __len__(self) -> int:
        return len(self._df)

    def iter_restaurants(self) -> Iterator[Restaurant]:
        for row in self._df.to_dict(orient="records"):
            yield _row_to_restaurant(row)

    def get_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        matches = self._df[self._df["restaurant_id"] == restaurant_id]
        if matches.empty:
            return None
        return _row_to_restaurant(matches.iloc[0].to_dict())

    def get_locations(self) -> list[str]:
        locations = set(self._df["location"].dropna().astype(str))
        locations.update(self._df["city"].dropna().astype(str))
        return sorted(loc for loc in locations if loc)

    def get_cuisines(self) -> list[str]:
        cuisines: set[str] = set()
        for items in self._df["cuisines"]:
            cuisines.update(_normalize_cuisines(items))
        return sorted(cuisines)
