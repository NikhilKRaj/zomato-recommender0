class AppError(Exception):
    """Base exception for domain errors."""


class NoCandidatesError(AppError):
    """Raised when no restaurants match the user's filters."""


class LLMError(AppError):
    """Raised when the Groq LLM call or response parsing fails."""


class DataLoadError(AppError):
    """Raised when the restaurant dataset cannot be loaded or validated."""
