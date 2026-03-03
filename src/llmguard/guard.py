"""Main LLMGuard class — orchestrates all filters."""

from __future__ import annotations

from pathlib import Path

from llmguard.config import GuardConfig
from llmguard.filters.content import ContentFilter
from llmguard.filters.pii import PIIFilter
from llmguard.filters.topic import TopicFilter
from llmguard.filters.word import WordFilter
from llmguard.result import ValidationResult


class LLMGuard:
    """Content and PII filtering for LLM pipelines.

    Usage::

        guard = LLMGuard({"pii_filter": {"enabled": True}})
        result = guard.validate("My email is test@example.com")
        print(result.is_valid, result.masked_text)
    """

    def __init__(self, config: GuardConfig | dict | str | None = None) -> None:
        if config is None:
            self.config = GuardConfig()
        elif isinstance(config, GuardConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = GuardConfig.from_dict(config)
        elif isinstance(config, (str, Path)):
            self.config = GuardConfig.from_yaml(config)
        else:
            raise TypeError(f"Unsupported config type: {type(config)}")

        self._filters: list[tuple[str, object]] = []
        self._pii_filter: PIIFilter | None = None

        if self.config.word_filter.enabled:
            self._filters.append(("word", WordFilter(self.config.word_filter)))

        if self.config.content_filter.enabled:
            self._filters.append(("content", ContentFilter(self.config.content_filter)))

        if self.config.pii_filter.enabled:
            self._pii_filter = PIIFilter(self.config.pii_filter)
            self._filters.append(("pii", self._pii_filter))

        if self.config.topic_filter.enabled:
            self._filters.append(("topic", TopicFilter(self.config.topic_filter)))

    def validate(self, text: str) -> ValidationResult:
        """Run all enabled filters against the text."""
        all_violations = []
        metadata: dict = {}
        masked_text = None
        is_valid = True

        for name, filt in self._filters:
            result = filt.validate(text)
            if not result.is_valid:
                is_valid = False
            all_violations.extend(result.violations)
            metadata.update(result.metadata)
            if result.masked_text is not None:
                masked_text = result.masked_text

        return ValidationResult(
            is_valid=is_valid,
            violations=all_violations,
            masked_text=masked_text,
            metadata=metadata,
        )

    def validate_input(self, text: str) -> ValidationResult:
        """Validate user input text. Alias for validate()."""
        return self.validate(text)

    def validate_output(self, text: str) -> ValidationResult:
        """Validate LLM output text. Alias for validate()."""
        return self.validate(text)

    def mask_pii(self, text: str) -> str:
        """Convenience: return PII-masked version of text.

        If PII filter is not enabled, returns original text.
        """
        if self._pii_filter is None:
            return text
        return self._pii_filter.mask(text)
