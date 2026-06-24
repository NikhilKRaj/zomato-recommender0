from __future__ import annotations

from typing import Literal, Optional, TypedDict


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMClient:
    """Protocol-style base for LLM clients used in tests and production."""

    def complete(
        self,
        messages: list[Message],
        response_format: Optional[dict] = None,
        temperature: float = 0.3,
    ) -> str:
        raise NotImplementedError
