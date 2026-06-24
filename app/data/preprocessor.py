"""Zomato dataset preprocessing pipeline.

Cleaning rules (architecture §4.3):
- Rating: strip '/5', convert to float 0–5; invalid → null
- Cost: parse to integer INR; ranges use midpoint; invalid → null
- Budget band: low ≤ 300, medium 301–600, high > 600
- Cuisines: lowercase, trim, comma-split
- City: always Bangalore (dataset is Bangalore-only; ``listed_in(city)`` is a neighbourhood)
- Booleans: Yes/No → true/false
- Duplicates: drop by name+address, keep highest votes
- Invalid rows: drop if name is missing
"""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

COL_COST = "approx_cost(for two people)"
COL_CITY = "listed_in(city)"
COL_MEAL_TYPE = "listed_in(type)"

DEFAULT_CITY = "Bangalore"

BUDGET_BAND_DEFINITIONS = {
    "low": {"max_cost": 300, "label": "Low (≤ ₹300 for two)"},
    "medium": {"min_cost": 301, "max_cost": 600, "label": "Medium (₹301–₹600 for two)"},
    "high": {"min_cost": 601, "label": "High (> ₹600 for two)"},
}


def parse_rating(value: object) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NEW", "-", "NAN"}:
        return None
    text = text.replace("/5", "").strip()
    match = re.search(r"(-?\d+(?:\.\d+)?)", text)
    if not match:
        return None
    rating = float(match.group(1))
    if rating < 0:
        return 0.0
    if rating > 5:
        return 5.0
    return rating


def parse_cost(value: object) -> Optional[int]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)) and not pd.isna(value):
        return int(value)

    text = str(value).strip().lower()
    if not text or text in {"-", "nan"}:
        return None

    text = text.replace("₹", "").replace(",", "").replace(" ", "")
    range_match = re.match(r"^(\d+)(?:[-–—to]+(\d+))?$", text)
    if range_match:
        low = int(range_match.group(1))
        high = range_match.group(2)
        return low if high is None else int((low + int(high)) / 2)

    digits = re.findall(r"\d+", text)
    if not digits:
        return None
    return int(digits[0])


def derive_budget_band(cost: Optional[int]) -> Optional[str]:
    if cost is None:
        return None
    if cost <= 300:
        return "low"
    if cost <= 600:
        return "medium"
    return "high"


def parse_cuisines(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [part.strip().lower() for part in str(value).split(",") if part.strip()]


def parse_yes_no(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return str(value).strip().lower() == "yes"


def make_restaurant_id(name: str, address: str) -> str:
    key = f"{name.strip().lower()}|{address.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def derive_city(address: str) -> str:
    """Return the city for a restaurant.

    The Hugging Face dataset's ``listed_in(city)`` column holds neighbourhood
    names (e.g. Sarjapur Road, Koramangala), not the actual city. All rows in
    this dataset are in Bangalore, so ``city`` is set to Bangalore.
    """
    if address:
        address_lower = address.casefold()
        if "bangalore" in address_lower or "bengaluru" in address_lower:
            return DEFAULT_CITY
    return DEFAULT_CITY


def _safe_str(value: object, default: str = "") -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    return str(value).strip()


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Dataset is empty")

    required_columns = {"name", "location", COL_CITY, "cuisines", "rate", COL_COST}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")

    work = df.copy()
    initial_count = len(work)

    work["name"] = work["name"].map(lambda v: _safe_str(v))
    work = work[work["name"] != ""]
    work["address"] = work["address"].map(lambda v: _safe_str(v)) if "address" in work else ""
    work["location"] = work["location"].map(lambda v: _safe_str(v))
    work["city"] = work["address"].map(derive_city)
    work["rest_type"] = work["rest_type"].map(lambda v: _safe_str(v)) if "rest_type" in work else ""
    work["meal_type"] = work[COL_MEAL_TYPE].map(lambda v: _safe_str(v))
    work["dish_liked"] = work["dish_liked"].where(work["dish_liked"].notna(), None) if "dish_liked" in work else None
    work["url"] = work["url"].where(work["url"].notna(), None) if "url" in work else None

    work["rating"] = work["rate"].map(parse_rating)
    work["cost_for_two"] = work[COL_COST].map(parse_cost)
    work["budget_band"] = work["cost_for_two"].map(derive_budget_band)
    work["cuisines"] = work["cuisines"].map(parse_cuisines)
    work["online_order"] = work["online_order"].map(parse_yes_no) if "online_order" in work else False
    work["book_table"] = work["book_table"].map(parse_yes_no) if "book_table" in work else False
    work["votes"] = pd.to_numeric(work.get("votes", 0), errors="coerce").fillna(0).astype(int)

    work["restaurant_id"] = [
        make_restaurant_id(name, address)
        for name, address in zip(work["name"], work["address"])
    ]

    work = work.sort_values("votes", ascending=False)
    work = work.drop_duplicates(subset=["name", "address"], keep="first")
    work = work.reset_index(drop=True)

    valid_rating_pct = work["rating"].notna().mean() * 100
    valid_cost_pct = work["cost_for_two"].notna().mean() * 100
    logger.info(
        "Preprocessed %d rows (dropped %d). Valid rating: %.1f%%, valid cost: %.1f%%",
        len(work),
        initial_count - len(work),
        valid_rating_pct,
        valid_cost_pct,
    )
    if valid_rating_pct < 90 or valid_cost_pct < 90:
        logger.warning(
            "Valid rating (%.1f%%) or cost (%.1f%%) below 90%% threshold",
            valid_rating_pct,
            valid_cost_pct,
        )

    return work[
        [
            "restaurant_id",
            "name",
            "location",
            "city",
            "cuisines",
            "rating",
            "votes",
            "cost_for_two",
            "budget_band",
            "rest_type",
            "meal_type",
            "online_order",
            "book_table",
            "dish_liked",
            "address",
            "url",
        ]
    ]
