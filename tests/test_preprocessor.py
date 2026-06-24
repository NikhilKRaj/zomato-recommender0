import pandas as pd
import pytest

from app.data.preprocessor import (
    derive_budget_band,
    derive_city,
    make_restaurant_id,
    parse_cost,
    parse_cuisines,
    parse_rating,
    parse_yes_no,
    preprocess_dataframe,
)


def test_parse_rating_valid():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("3.5 / 5") == 3.5


def test_parse_rating_invalid():
    assert parse_rating(None) is None
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_rating_clamps():
    assert parse_rating("6.0/5") == 5.0
    assert parse_rating("-1/5") == 0.0


def test_parse_cost_numeric_and_range():
    assert parse_cost("800") == 800
    assert parse_cost("₹1,200") == 1200
    assert parse_cost("300-400") == 350
    assert parse_cost(500) == 500


def test_parse_cost_invalid():
    assert parse_cost(None) is None
    assert parse_cost("-") is None


def test_derive_budget_band():
    assert derive_budget_band(300) == "low"
    assert derive_budget_band(301) == "medium"
    assert derive_budget_band(600) == "medium"
    assert derive_budget_band(601) == "high"
    assert derive_budget_band(None) is None


def test_parse_cuisines():
    assert parse_cuisines("North Indian, Mughlai, Chinese") == [
        "north indian",
        "mughlai",
        "chinese",
    ]
    assert parse_cuisines(None) == []


def test_parse_yes_no():
    assert parse_yes_no("Yes") is True
    assert parse_yes_no("No") is False
    assert parse_yes_no(None) is False


def test_make_restaurant_id_stable():
    first = make_restaurant_id("Jalsa", "123 Street")
    second = make_restaurant_id("Jalsa", "123 Street")
    third = make_restaurant_id("Jalsa", "456 Street")
    assert first == second
    assert first != third


def test_preprocess_dataframe_drops_empty_name_and_duplicates():
    raw = pd.DataFrame(
        [
            {
                "name": "Alpha",
                "address": "Addr 1",
                "location": "Koramangala",
                "listed_in(city)": "Bangalore",
                "cuisines": "Italian",
                "rate": "4.0/5",
                "approx_cost(for two people)": "500",
                "votes": 10,
                "online_order": "Yes",
                "book_table": "No",
                "listed_in(type)": "Cafes",
                "rest_type": "Casual Dining",
            },
            {
                "name": "Alpha",
                "address": "Addr 1",
                "location": "Koramangala",
                "listed_in(city)": "Bangalore",
                "cuisines": "Italian",
                "rate": "3.0/5",
                "approx_cost(for two people)": "500",
                "votes": 100,
                "online_order": "Yes",
                "book_table": "No",
                "listed_in(type)": "Cafes",
                "rest_type": "Casual Dining",
            },
            {
                "name": "",
                "address": "Addr 2",
                "location": "Indiranagar",
                "listed_in(city)": "Bangalore",
                "cuisines": "Chinese",
                "rate": "4.0/5",
                "approx_cost(for two people)": "300",
                "votes": 5,
                "online_order": "No",
                "book_table": "No",
                "listed_in(type)": "Delivery",
                "rest_type": "Quick Bites",
            },
        ]
    )

    result = preprocess_dataframe(raw)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Alpha"
    assert result.iloc[0]["votes"] == 100
    assert result.iloc[0]["budget_band"] == "medium"
    assert result.iloc[0]["city"] == "Bangalore"
    assert result.iloc[0]["location"] == "Koramangala"


def test_derive_city_returns_bangalore():
    assert derive_city("123 Street, Sarjapur Road, Bangalore") == "Bangalore"
    assert derive_city("Indiranagar, Bengaluru") == "Bangalore"
    assert derive_city("") == "Bangalore"


def test_preprocess_missing_columns_raises():
    with pytest.raises(ValueError, match="missing required columns"):
        preprocess_dataframe(pd.DataFrame({"name": ["A"]}))
