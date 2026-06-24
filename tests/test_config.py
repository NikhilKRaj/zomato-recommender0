import json

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_cors_origins_json_array():
    settings = Settings(cors_origins='["https://app.vercel.app"]')
    assert settings.cors_origins == ["https://app.vercel.app"]


def test_cors_origins_comma_separated():
    settings = Settings(
        cors_origins="https://app.vercel.app, https://preview.vercel.app"
    )
    assert settings.cors_origins == [
        "https://app.vercel.app",
        "https://preview.vercel.app",
    ]


def test_cors_origins_list():
    settings = Settings(cors_origins=["https://a.vercel.app", "https://b.vercel.app"])
    assert len(settings.cors_origins) == 2


def test_cors_origins_invalid_json():
    with pytest.raises(ValidationError):
        Settings(cors_origins='{"not": "array"}')
