from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Zomato Recommendation API"
    debug: bool = False

    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout_seconds: int = 30
    groq_max_tokens: int = 2048

    max_candidates: int = 30
    additional_preferences_max_length: int = 500

    data_cache_path: Path = PROJECT_ROOT / "data" / "processed" / "restaurants.parquet"

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
