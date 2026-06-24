from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_recommendation_service
from app.main import app
from app.models.recommendation import Recommendation, RecommendationResponse, ResponseMeta
from app.models.restaurant import Restaurant
from app.services.recommendation import RecommendationService

VALID_REQUEST = {
    "location": "Koramangala",
    "budget": "medium",
    "cuisine": "Italian",
    "min_rating": 4.0,
    "top_n": 5,
}


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_restaurant() -> Restaurant:
    return Restaurant(
        id="r1",
        name="Truffles",
        location="Koramangala",
        city="Bangalore",
        cuisines=["italian", "american"],
        rating=4.5,
        votes=500,
        cost_for_two=500,
        budget_band="medium",
    )


def test_metadata_locations(client: TestClient):
    response = client.get("/metadata/locations")
    assert response.status_code == 200
    body = response.json()
    assert "locations" in body
    assert len(body["locations"]) > 0
    assert "Bangalore" in body["locations"]


def test_metadata_cuisines(client: TestClient):
    response = client.get("/metadata/cuisines")
    assert response.status_code == 200
    body = response.json()
    assert "cuisines" in body
    assert len(body["cuisines"]) > 0


def test_metadata_budget_bands(client: TestClient):
    response = client.get("/metadata/budget-bands")
    assert response.status_code == 200
    body = response.json()
    assert "budget_bands" in body
    assert "low" in body["budget_bands"]
    assert "medium" in body["budget_bands"]
    assert "high" in body["budget_bands"]


def test_recommend_invalid_body_returns_400(client: TestClient):
    response = client.post("/recommend", json={"location": "Koramangala"})
    assert response.status_code == 400


def test_recommend_no_candidates_returns_404(client: TestClient):
    response = client.post(
        "/recommend",
        json={
            "location": "Koramangala",
            "budget": "medium",
            "cuisine": "Martian",
            "min_rating": 4.0,
            "top_n": 5,
        },
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_recommend_returns_fallback_when_llm_fails(
    client: TestClient,
    sample_restaurant: Restaurant,
):
    mock_service = MagicMock(spec=RecommendationService)
    mock_service.recommend.return_value = RecommendationResponse(
        summary=None,
        recommendations=[
            Recommendation(
                rank=1,
                restaurant=sample_restaurant,
                explanation="Fallback explanation",
            )
        ],
        meta=ResponseMeta(
            candidates_considered=3,
            source="fallback",
            model=None,
        ),
    )
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service
    try:
        response = client.post("/recommend", json=VALID_REQUEST)
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["source"] == "fallback"
        assert body["meta"]["candidates_considered"] == 3
        assert len(body["recommendations"]) == 1
        assert body["recommendations"][0]["restaurant"]["name"] == "Truffles"
    finally:
        app.dependency_overrides.clear()


def test_recommend_integration_uses_llm_or_fallback(client: TestClient):
    response = client.post("/recommend", json=VALID_REQUEST)
    assert response.status_code == 200
    body = response.json()
    assert "recommendations" in body
    assert 1 <= len(body["recommendations"]) <= 5
    assert body["meta"]["candidates_considered"] >= 1
    assert body["meta"]["source"] in {"llm", "fallback"}
    first = body["recommendations"][0]
    assert "rank" in first
    assert "explanation" in first
    assert "restaurant" in first
    assert first["restaurant"]["name"]


def test_recommendation_service_fallback_on_llm_error(sample_restaurant: Restaurant):
    from app.core.exceptions import LLMError
    from app.llm.types import LLMClient
    from app.models.preferences import UserPreferences
    from app.services.data_loader import DataLoader

    class FailingLLM(LLMClient):
        def complete(self, messages, response_format=None, temperature=0.3) -> str:
            del messages, response_format, temperature
            raise LLMError("boom")

    loader = DataLoader()
    store = loader.get_restaurant_store()
    service = RecommendationService(llm_client=FailingLLM())  # type: ignore[arg-type]

    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_n=3,
    )
    result = service.recommend(preferences, store)
    assert result.meta.source == "fallback"
    assert len(result.recommendations) >= 1
    assert result.recommendations[0].explanation
