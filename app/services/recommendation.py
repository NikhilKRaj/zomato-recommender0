from __future__ import annotations

import logging

from app.core.config import settings
from app.core.exceptions import LLMError, NoCandidatesError
from app.llm.groq_client import GroqLLMClient
from app.llm.parser import ResponseParser
from app.models.preferences import UserPreferences
from app.models.recommendation import Recommendation, RecommendationResponse, ResponseMeta
from app.models.restaurant import Restaurant
from app.services.dedupe import dedupe_recommendations_by_name
from app.services.fallback_ranker import FallbackRanker
from app.services.filter import CandidateFilter
from app.services.prompt_builder import PromptBuilder
from app.services.restaurant_store import RestaurantStore

logger = logging.getLogger(__name__)


class RecommendationService:
    """Orchestrates filter → prompt → Groq → parse with fallback ranking."""

    def __init__(
        self,
        candidate_filter: CandidateFilter | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm_client: GroqLLMClient | None = None,
        response_parser: ResponseParser | None = None,
        fallback_ranker: FallbackRanker | None = None,
    ) -> None:
        self.candidate_filter = candidate_filter or CandidateFilter()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm_client = llm_client or GroqLLMClient()
        self.response_parser = response_parser or ResponseParser()
        self.fallback_ranker = fallback_ranker or FallbackRanker()

    def recommend(
        self,
        preferences: UserPreferences,
        store: RestaurantStore,
    ) -> RecommendationResponse:
        candidates = self.candidate_filter.filter(preferences, store)
        if not candidates:
            raise NoCandidatesError(
                "No restaurants match your filters. Try broadening location, cuisine, budget, or rating."
            )

        candidates_considered = len(candidates)

        try:
            return self._recommend_with_llm(preferences, candidates, candidates_considered)
        except LLMError as exc:
            logger.warning("LLM recommendation failed, using fallback ranker: %s", exc)
            return self._recommend_with_fallback(preferences, candidates, candidates_considered)

    def _recommend_with_llm(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        candidates_considered: int,
    ) -> RecommendationResponse:
        messages = self.prompt_builder.build(preferences, candidates)
        llm_result = self.response_parser.parse_with_retry(
            self.llm_client,
            messages,
            candidates,
            preferences.top_n,
        )

        candidate_map = {restaurant.id: restaurant for restaurant in candidates}
        recommendations = dedupe_recommendations_by_name(
            [
                Recommendation(
                    rank=item.rank,
                    restaurant=candidate_map[item.restaurant_id],
                    explanation=item.explanation,
                )
                for item in llm_result.recommendations
            ]
        )

        return RecommendationResponse(
            summary=llm_result.summary,
            recommendations=recommendations,
            meta=ResponseMeta(
                candidates_considered=candidates_considered,
                source="llm",
                model=settings.groq_model,
            ),
        )

    def _recommend_with_fallback(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        candidates_considered: int,
    ) -> RecommendationResponse:
        ranked = self.fallback_ranker.rank(candidates, preferences.top_n)
        recommendations = dedupe_recommendations_by_name(
            [
                Recommendation(
                    rank=index,
                    restaurant=restaurant,
                    explanation=self._fallback_explanation(restaurant, preferences),
                )
                for index, restaurant in enumerate(ranked, start=1)
            ]
        )

        return RecommendationResponse(
            summary=None,
            recommendations=recommendations,
            meta=ResponseMeta(
                candidates_considered=candidates_considered,
                source="fallback",
                model=None,
            ),
        )

    @staticmethod
    def _fallback_explanation(restaurant: Restaurant, preferences: UserPreferences) -> str:
        rating_text = f"{restaurant.rating}/5" if restaurant.rating is not None else "unrated"
        cuisines = ", ".join(restaurant.cuisines)
        cost_text = (
            f"₹{restaurant.cost_for_two} for two"
            if restaurant.cost_for_two is not None
            else "price unavailable"
        )
        return (
            f"Rated {rating_text} with {restaurant.votes} votes. "
            f"Serves {cuisines} in {restaurant.location}, fits your {preferences.budget} budget "
            f"({cost_text}), and matches your {preferences.cuisine} cuisine preference."
        )
