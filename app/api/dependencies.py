from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterator

from fastapi import FastAPI, Request

from app.core.config import settings
from app.core.exceptions import DataLoadError
from app.services.data_loader import DataLoader
from app.services.recommendation import RecommendationService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    loader = DataLoader(cache_path=settings.data_cache_path)
    try:
        loader.load()
        app.state.data_loader = loader
    except DataLoadError as exc:
        app.state.data_loader = None
        if not settings.debug:
            raise
        import logging

        logging.getLogger(__name__).warning("Dataset not loaded: %s", exc)
    yield


def get_data_loader(request: Request) -> DataLoader:
    loader = getattr(request.app.state, "data_loader", None)
    if loader is None:
        raise DataLoadError("Restaurant dataset is not loaded")
    return loader


@lru_cache
def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
