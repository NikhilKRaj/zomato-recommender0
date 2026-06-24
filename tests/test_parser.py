from __future__ import annotations

import pytest

from app.core.exceptions import LLMError
from app.llm.groq_client import GroqLLMClient
from app.llm.parser import ResponseParser
from app.llm.types import LLMClient, Message
from app.models.restaurant import Restaurant
from app.models.preferences import UserPreferences
from app.services.prompt_builder import PromptBuilder


def _restaurant(restaurant_id: str, name: str = "Test") -> Restaurant:
    return Restaurant(
        id=restaurant_id,
        name=name,
        location="Koramangala",
        city="Bangalore",
        cuisines=["italian"],
        rating=4.5,
        votes=100,
        cost_for_two=500,
        budget_band="medium",
        rest_type="Casual Dining",
        meal_type="Cafes",
        dish_liked="A very long dish list " * 10,
    )


class MockLLMClient(LLMClient):
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls = 0

    def complete(
        self,
        messages: list[Message],
        response_format: dict | None = None,
        temperature: float = 0.3,
    ) -> str:
        del messages, response_format, temperature
        if self.calls >= len(self.responses):
            raise LLMError("No more mock responses")
        response = self.responses[self.calls]
        self.calls += 1
        return response


def test_prompt_builder_truncates_dish_liked_and_serializes_candidates():
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        top_n=3,
    )
    candidates = [_restaurant("r1", "Truffles")]
    messages = PromptBuilder().build(preferences, candidates)

    assert messages[0]["role"] == "system"
    user_content = messages[1]["content"]
    assert "id=r1" in user_content
    assert "top 3" in user_content
    assert "..." in user_content


def test_parser_accepts_valid_json():
    parser = ResponseParser()
    candidates = [_restaurant("r1"), _restaurant("r2", "Other")]
    raw = """
    {
      "summary": "Great Italian picks",
      "recommendations": [
        {"restaurant_id": "r1", "rank": 1, "explanation": "Matches Italian and budget."},
        {"restaurant_id": "r2", "rank": 2, "explanation": "Solid backup option."}
      ]
    }
    """
    result = parser.parse_and_validate(raw, candidates, top_n=2)
    assert result.summary == "Great Italian picks"
    assert [item.restaurant_id for item in result.recommendations] == ["r1", "r2"]


def test_parser_strips_markdown_fences():
    parser = ResponseParser()
    candidates = [_restaurant("r1")]
    raw = """```json
    {"summary": "ok", "recommendations": [{"restaurant_id": "r1", "rank": 1, "explanation": "fit"}]}
    ```"""
    result = parser.parse_and_validate(raw, candidates, top_n=1)
    assert result.recommendations[0].restaurant_id == "r1"


def test_parser_rejects_hallucinated_ids():
    parser = ResponseParser()
    candidates = [_restaurant("r1")]
    raw = """
    {
      "summary": "bad",
      "recommendations": [
        {"restaurant_id": "fake-id", "rank": 1, "explanation": "hallucinated"}
      ]
    }
    """
    with pytest.raises(LLMError, match="No valid recommendations"):
        parser.parse_and_validate(raw, candidates, top_n=1)


def test_parser_retries_on_malformed_json():
    parser = ResponseParser()
    candidates = [_restaurant("r1")]
    mock_client = MockLLMClient(
        [
            "not-json",
            """
            {
              "summary": "fixed",
              "recommendations": [
                {"restaurant_id": "r1", "rank": 1, "explanation": "valid"}
              ]
            }
            """,
        ]
    )
    messages: list[Message] = [{"role": "user", "content": "test"}]
    result = parser.parse_with_retry(mock_client, messages, candidates, top_n=1)
    assert result.summary == "fixed"
    assert mock_client.calls == 2


def test_groq_client_requires_api_key():
    client = GroqLLMClient(use_settings_api_key=False)
    with pytest.raises(LLMError, match="GROQ_API_KEY is not set"):
        client.complete([{"role": "user", "content": "hello"}])
