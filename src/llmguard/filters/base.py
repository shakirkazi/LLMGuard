"""Abstract base class for all LLMGuard filters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llmguard.result import ValidationResult


class BaseFilter(ABC):
    """Base class that all filters must implement."""

    @abstractmethod
    def validate(self, text: str) -> ValidationResult:
        """Run the filter against the given text.

        Returns a ValidationResult with is_valid=True if the text passes,
        or is_valid=False with violations if it doesn't.
        """
