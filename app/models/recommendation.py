from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

from app.models.restaurant import Restaurant


class ResponseMeta(BaseModel):
    candidates_considered: int
    source: Literal["llm", "fallback"]
    model: Optional[str] = None


class Recommendation(BaseModel):
    rank: int
    restaurant: Restaurant
    explanation: str


class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: list[Recommendation]
    meta: ResponseMeta
