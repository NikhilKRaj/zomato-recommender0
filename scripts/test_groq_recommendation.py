from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.exceptions import LLMError
from app.llm.groq_client import GroqLLMClient
from app.llm.parser import ResponseParser
from app.models.preferences import UserPreferences
from app.services.data_loader import DataLoader
from app.services.filter import CandidateFilter
from app.services.prompt_builder import PromptBuilder


def main() -> None:
    loader = DataLoader()
    store = loader.get_restaurant_store()
    preferences = UserPreferences(
        location="Koramangala",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_n=5,
    )

    candidates = CandidateFilter().filter(preferences, store)
    if not candidates:
        print("No candidates found for the sample preferences.")
        return

    messages = PromptBuilder().build(preferences, candidates)
    client = GroqLLMClient()
    parser = ResponseParser()

    try:
        result = parser.parse_with_retry(
            client,
            messages,
            candidates,
            preferences.top_n,
        )
    except LLMError as exc:
        print(f"LLM pipeline failed: {exc}")
        raise SystemExit(1) from exc

    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
