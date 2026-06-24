from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from app.core.config import settings
from app.models.preferences import UserPreferences
from app.models.restaurant import Restaurant
from app.services.dedupe import dedupe_restaurants_by_name
from app.services.restaurant_store import RestaurantStore, _row_to_restaurant

DELIVERY_KEYWORDS = ("delivery", "online order", "online_order", "takeaway", "take away")
BOOKING_KEYWORDS = ("book table", "table booking", "reservation", "dine-in", "dine in")


@dataclass(frozen=True)
class AdditionalFilters:
    require_online_order: bool = False
    require_book_table: bool = False
    keywords: tuple[str, ...] = ()


def parse_additional_filters(additional_preferences: str | None) -> AdditionalFilters:
    if not additional_preferences:
        return AdditionalFilters()

    lowered = additional_preferences.lower()
    require_online_order = any(keyword in lowered for keyword in DELIVERY_KEYWORDS)
    require_book_table = any(keyword in lowered for keyword in BOOKING_KEYWORDS)

    keywords: list[str] = []
    for part in re.split(r"[,;]+", lowered):
        token = part.strip()
        if not token:
            continue
        if any(keyword in token for keyword in DELIVERY_KEYWORDS):
            continue
        if any(keyword in token for keyword in BOOKING_KEYWORDS):
            continue
        keywords.append(token)

    return AdditionalFilters(
        require_online_order=require_online_order,
        require_book_table=require_book_table,
        keywords=tuple(keywords),
    )


def _matches_location(df: pd.DataFrame, location: str) -> pd.Series:
    needle = location.casefold()
    location_match = df["location"].astype(str).str.casefold().str.contains(needle, regex=False, na=False)
    city_match = df["city"].astype(str).str.casefold().str.contains(needle, regex=False, na=False)
    return location_match | city_match


def _matches_cuisine(df: pd.DataFrame, cuisine: str) -> pd.Series:
    needle = cuisine.casefold().strip()

    def cuisine_match(value: object) -> bool:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return False
        if isinstance(value, str):
            items = [value]
        elif isinstance(value, (list, tuple)) or hasattr(value, "__iter__"):
            items = [str(item) for item in value]
        else:
            items = [str(value)]
        return any(needle in item.casefold() for item in items)

    return df["cuisines"].map(cuisine_match)


def _matches_keywords(df: pd.DataFrame, keywords: tuple[str, ...]) -> pd.Series:
    if not keywords:
        return pd.Series(True, index=df.index)

    rest_type = df["rest_type"].astype(str).str.casefold()
    meal_type = df["meal_type"].astype(str).str.casefold()

    def keyword_match(index: int) -> bool:
        haystacks = (rest_type.iloc[index], meal_type.iloc[index])
        return any(
            keyword in haystack
            for keyword in keywords
            for haystack in haystacks
        )

    return pd.Series((keyword_match(i) for i in range(len(df))), index=df.index)


class CandidateFilter:
    """Deterministic restaurant filter before LLM ranking."""

    def filter(
        self,
        preferences: UserPreferences,
        store: RestaurantStore,
        max_candidates: int | None = None,
    ) -> list[Restaurant]:
        cap = max_candidates if max_candidates is not None else settings.max_candidates
        df = store.dataframe
        if df.empty:
            return []

        mask = pd.Series(True, index=df.index)
        mask &= _matches_location(df, preferences.location)
        mask &= _matches_cuisine(df, preferences.cuisine)
        mask &= df["budget_band"].astype(str).str.casefold() == preferences.budget_band

        if preferences.min_rating > 0:
            mask &= df["rating"].notna() & (df["rating"] >= preferences.min_rating)

        additional = parse_additional_filters(preferences.additional_preferences)
        if additional.require_online_order:
            mask &= df["online_order"].astype(bool)
        if additional.require_book_table:
            mask &= df["book_table"].astype(bool)
        if additional.keywords:
            mask &= _matches_keywords(df, additional.keywords)

        filtered = df[mask].copy()
        if filtered.empty:
            return []

        filtered = filtered.sort_values(
            by=["rating", "votes"],
            ascending=[False, False],
            na_position="last",
        )
        if len(filtered) > cap:
            filtered = filtered.head(cap)

        restaurants = [_row_to_restaurant(row) for row in filtered.to_dict(orient="records")]
        return dedupe_restaurants_by_name(restaurants)
