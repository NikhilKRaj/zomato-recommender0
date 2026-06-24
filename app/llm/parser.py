from __future__ import annotations

import json
import logging
import re
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

from app.core.exceptions import LLMError
from app.llm.prompts import REPAIR_PROMPT
from app.llm.types import LLMClient, Message
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class LLMRecommendationItem(BaseModel):
    restaurant_id: str
    rank: int = Field(ge=1)
    explanation: str = Field(min_length=1)


class LLMRecommendationResult(BaseModel):
    summary: Optional[str] = None
    recommendations: list[LLMRecommendationItem]


class ResponseParser:
    """Parse and validate Groq JSON output against the candidate restaurant set."""

    def parse_and_validate(
        self,
        content: str,
        candidates: list[Restaurant],
        top_n: int,
    ) -> LLMRecommendationResult:
        data = self._load_json(content)
        return self._validate_payload(data, candidates, top_n)

    def parse_with_retry(
        self,
        llm_client: LLMClient,
        messages: list[Message],
        candidates: list[Restaurant],
        top_n: int,
        *,
        temperature: float = 0.3,
        response_format: Optional[dict] = None,
    ) -> LLMRecommendationResult:
        raw = llm_client.complete(
            messages,
            response_format=response_format or {"type": "json_object"},
            temperature=temperature,
        )
        try:
            return self.parse_and_validate(raw, candidates, top_n)
        except LLMError as first_error:
            logger.warning("Initial LLM response invalid: %s", first_error)
            repair_messages = list(messages) + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": REPAIR_PROMPT},
            ]
            repaired = llm_client.complete(
                repair_messages,
                response_format=response_format or {"type": "json_object"},
                temperature=temperature,
            )
            try:
                return self.parse_and_validate(repaired, candidates, top_n)
            except LLMError as second_error:
                raise LLMError(
                    f"LLM response validation failed after repair: {second_error}"
                ) from second_error

    def _load_json(self, content: str) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Failed to parse LLM JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise LLMError("LLM JSON root must be an object")
        return data

    def _validate_payload(
        self,
        data: dict,
        candidates: list[Restaurant],
        top_n: int,
    ) -> LLMRecommendationResult:
        if "recommendations" not in data:
            raise LLMError("LLM JSON missing 'recommendations' field")

        try:
            parsed = LLMRecommendationResult.model_validate(data)
        except ValidationError as exc:
            raise LLMError(f"LLM JSON schema validation failed: {exc}") from exc

        valid_ids = {restaurant.id for restaurant in candidates}
        seen_ids: set[str] = set()
        validated_items: list[LLMRecommendationItem] = []

        for item in sorted(parsed.recommendations, key=lambda entry: entry.rank):
            if item.restaurant_id not in valid_ids:
                logger.warning("Rejecting hallucinated restaurant_id: %s", item.restaurant_id)
                continue
            if item.restaurant_id in seen_ids:
                logger.warning("Rejecting duplicate restaurant_id: %s", item.restaurant_id)
                continue
            seen_ids.add(item.restaurant_id)
            validated_items.append(item)

        if not validated_items:
            raise LLMError("No valid recommendations remained after ID validation")

        normalized = [
            LLMRecommendationItem(
                restaurant_id=item.restaurant_id,
                rank=index,
                explanation=item.explanation,
            )
            for index, item in enumerate(validated_items[:top_n], start=1)
        ]

        return LLMRecommendationResult(
            summary=parsed.summary,
            recommendations=normalized,
        )
