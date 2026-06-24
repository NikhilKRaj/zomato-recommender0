from fastapi import APIRouter, Depends

from app.api.dependencies import get_data_loader, get_recommendation_service
from app.models.preferences import UserPreferences
from app.models.recommendation import RecommendationResponse
from app.services.data_loader import DataLoader
from app.services.recommendation import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(
    preferences: UserPreferences,
    loader: DataLoader = Depends(get_data_loader),
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    store = loader.get_restaurant_store()
    return service.recommend(preferences, store)
