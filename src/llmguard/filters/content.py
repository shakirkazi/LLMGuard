"""Content filter — keyword-based content classification."""

from __future__ import annotations

import re

from llmguard.config import ContentFilterConfig
from llmguard.filters.base import BaseFilter
from llmguard.result import ValidationResult, Violation

# Built-in keyword lists per category (lowercase)
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "hate": [
        "hate",
        "racist",
        "racism",
        "bigot",
        "bigotry",
        "supremacist",
        "supremacy",
        "xenophobia",
        "xenophobic",
        "homophobia",
        "homophobic",
        "slur",
        "dehumanize",
        "inferior race",
        "ethnic cleansing",
    ],
    "violence": [
        "kill",
        "murder",
        "assault",
        "attack",
        "bomb",
        "shoot",
        "stab",
        "weapon",
        "torture",
        "execute",
        "massacre",
        "slaughter",
        "bloodshed",
        "dismember",
        "decapitate",
    ],
    "sexual": [
        "porn",
        "pornography",
        "explicit sexual",
        "nude",
        "nudity",
        "sexually explicit",
        "erotic",
        "obscene",
    ],
    "profanity": [
        "damn",
        "hell",
        "crap",
        "bastard",
    ],
}


def _score_category(text: str, keywords: list[str]) -> float:
    """Score how strongly a text matches a category based on keyword density."""
    text_lower = text.lower()
    words = re.findall(r"\w+", text_lower)
    total_words = max(len(words), 1)
    hits = sum(1 for kw in keywords if kw in text_lower)
    return min(hits / total_words * 5.0, 1.0)


class ContentFilter(BaseFilter):
    """Classifies text against content categories using keyword matching."""

    def __init__(self, config: ContentFilterConfig) -> None:
        self.config = config

    def validate(self, text: str) -> ValidationResult:
        violations: list[Violation] = []
        scores: dict[str, float] = {}

        for category, threshold in self.config.categories.items():
            keywords = _CATEGORY_KEYWORDS.get(category, [])
            if not keywords:
                continue
            score = _score_category(text, keywords)
            scores[category] = score
            if score >= threshold:
                violations.append(
                    Violation(
                        filter_name="content_filter",
                        category=category,
                        severity="high" if score > 0.7 else "medium",
                        message=f"Content classified as '{category}' (score={score:.2f}, threshold={threshold})",
                        confidence=score,
                    )
                )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            metadata={"content_filter": {"scores": scores}},
        )
