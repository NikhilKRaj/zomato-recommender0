from __future__ import annotations

import logging
from typing import Optional

from groq import Groq

from app.core.config import settings
from app.core.exceptions import LLMError
from app.llm.types import LLMClient, Message

logger = logging.getLogger(__name__)


class GroqLLMClient(LLMClient):
    """Groq SDK wrapper for structured chat completions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        max_tokens: Optional[int] = None,
        *,
        use_settings_api_key: bool = True,
    ) -> None:
        if api_key is not None:
            self.api_key = api_key
        elif use_settings_api_key:
            self.api_key = settings.groq_api_key
        else:
            self.api_key = None
        self.model = model or settings.groq_model
        self.timeout_seconds = timeout_seconds or settings.groq_timeout_seconds
        self.max_tokens = max_tokens or settings.groq_max_tokens
        self._client: Optional[Groq] = None

    def _get_client(self) -> Groq:
        if not self.api_key:
            raise LLMError(
                "GROQ_API_KEY is not set. Add it to your .env file before using the LLM."
            )
        if self._client is None:
            self._client = Groq(api_key=self.api_key, timeout=self.timeout_seconds)
        return self._client

    def complete(
        self,
        messages: list[Message],
        response_format: Optional[dict] = None,
        temperature: float = 0.3,
    ) -> str:
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
            )
        except LLMError:
            raise
        except Exception as exc:
            logger.exception("Groq API call failed")
            raise LLMError(f"Groq API call failed: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMError("Groq returned an empty response")
        return content
