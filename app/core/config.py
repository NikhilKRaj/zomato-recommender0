from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


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

    cors_origins: List[str] = DEFAULT_CORS_ORIGINS

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        """Accept JSON array or comma-separated origins (Railway / Vercel env vars)."""
        if value is None:
            return DEFAULT_CORS_ORIGINS
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return DEFAULT_CORS_ORIGINS
            if stripped.startswith("[") or stripped.startswith("{"):
                parsed = json.loads(stripped)
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON must be an array")
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value


settings = Settings()
