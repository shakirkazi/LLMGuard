"""Word filter — blocks specific words and phrases."""

from __future__ import annotations

from llmguard.config import WordFilterConfig
from llmguard.filters.base import BaseFilter
from llmguard.result import ValidationResult, Violation


class WordFilter(BaseFilter):
    """Filters text based on blocked words, phrases, and optional profanity detection."""

    def __init__(self, config: WordFilterConfig) -> None:
        self.config = config
        self._profanity = None
        if config.use_profanity_list:
            try:
                from better_profanity import profanity

                profanity.load_censor_words()
                self._profanity = profanity
            except ImportError:
                pass

    def validate(self, text: str) -> ValidationResult:
        violations: list[Violation] = []
        check_text = text if self.config.case_sensitive else text.lower()

        # Check blocked words
        for word in self.config.blocked_words:
            check_word = word if self.config.case_sensitive else word.lower()
            if check_word in check_text.split() or check_word in check_text:
                violations.append(
                    Violation(
                        filter_name="word_filter",
                        category="blocked_word",
                        severity="high",
                        message=f"Blocked word detected: '{word}'",
                    )
                )

        # Check blocked phrases
        for phrase in self.config.blocked_phrases:
            check_phrase = phrase if self.config.case_sensitive else phrase.lower()
            if check_phrase in check_text:
                violations.append(
                    Violation(
                        filter_name="word_filter",
                        category="blocked_phrase",
                        severity="high",
                        message=f"Blocked phrase detected: '{phrase}'",
                    )
                )

        # Check profanity via better-profanity
        if self._profanity and self._profanity.contains_profanity(text):
            violations.append(
                Violation(
                    filter_name="word_filter",
                    category="profanity",
                    severity="medium",
                    message="Profanity detected in text",
                )
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            metadata={"word_filter": {"checked": True}},
        )
