from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from datasets import load_dataset

from app.core.exceptions import DataLoadError
from app.data.preprocessor import BUDGET_BAND_DEFINITIONS, preprocess_dataframe
from app.services.restaurant_store import RestaurantStore

logger = logging.getLogger(__name__)

DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_PATH = PROJECT_ROOT / "data" / "processed" / "restaurants.parquet"


class DataLoader:
    """Loads, preprocesses, and caches the Zomato restaurant dataset."""

    def __init__(self, cache_path: Optional[Path] = None) -> None:
        self.cache_path = cache_path or DEFAULT_CACHE_PATH
        self._store: Optional[RestaurantStore] = None

    def load(self, force_refresh: bool = False) -> pd.DataFrame:
        if not force_refresh and self.cache_path.exists():
            logger.info("Loading cached restaurants from %s", self.cache_path)
            df = pd.read_parquet(self.cache_path)
        else:
            logger.info("Downloading dataset from Hugging Face: %s", DATASET_NAME)
            try:
                dataset = load_dataset(DATASET_NAME, split="train")
                raw_df = dataset.to_pandas()
            except Exception as exc:
                raise DataLoadError(f"Failed to load dataset '{DATASET_NAME}': {exc}") from exc

            try:
                df = preprocess_dataframe(raw_df)
            except Exception as exc:
                raise DataLoadError(f"Failed to preprocess dataset: {exc}") from exc

            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(self.cache_path, index=False)
            logger.info("Wrote processed cache to %s", self.cache_path)

        if df.empty:
            raise DataLoadError("Processed dataset is empty")

        self._store = RestaurantStore(df)
        return df

    def get_restaurant_store(self) -> RestaurantStore:
        if self._store is None:
            self.load()
        assert self._store is not None
        return self._store

    def get_locations(self) -> list[str]:
        return self.get_restaurant_store().get_locations()

    def get_cuisines(self) -> list[str]:
        return self.get_restaurant_store().get_cuisines()

    def get_budget_bands(self) -> dict:
        return BUDGET_BAND_DEFINITIONS
