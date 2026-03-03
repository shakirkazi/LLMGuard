"""Topic filter — detects denied topics via keyword matching."""

from __future__ import annotations

import re

from llmguard.config import TopicFilterConfig
from llmguard.filters.base import BaseFilter
from llmguard.result import ValidationResult, Violation

# Built-in topic keyword lists
_DEFAULT_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "politics": [
        "election",
        "democrat",
        "republican",
        "congress",
        "senate",
        "president",
        "liberal",
        "conservative",
        "vote",
        "ballot",
        "political",
        "politician",
        "legislation",
        "partisan",
        "campaign",
    ],
    "religion": [
        "church",
        "mosque",
        "temple",
        "bible",
        "quran",
        "torah",
        "prayer",
        "worship",
        "christian",
        "muslim",
        "jewish",
        "hindu",
        "buddhist",
        "atheist",
        "religious",
    ],
    "gambling": [
        "casino",
        "bet",
        "betting",
        "gamble",
        "gambling",
        "poker",
        "slot machine",
        "wager",
        "lottery",
        "blackjack",
    ],
    "drugs": [
        "cocaine",
        "heroin",
        "methamphetamine",
        "marijuana",
        "cannabis",
        "narcotic",
        "opioid",
        "drug dealer",
        "drug trafficking",
    ],
    "weapons": [
        "gun",
        "firearm",
        "rifle",
        "pistol",
        "ammunition",
        "explosive",
        "grenade",
        "missile",
    ],
}


class TopicFilter(BaseFilter):
    """Detects denied topics in text using keyword matching."""

    def __init__(self, config: TopicFilterConfig) -> None:
        self.config = config
        # Merge built-in defaults with any user overrides
        self._topic_keywords: dict[str, list[str]] = {}
        for topic in config.denied_topics:
            topic_lower = topic.lower()
            if topic_lower in config.topic_keywords:
                self._topic_keywords[topic_lower] = config.topic_keywords[topic_lower]
            elif topic_lower in _DEFAULT_TOPIC_KEYWORDS:
                self._topic_keywords[topic_lower] = _DEFAULT_TOPIC_KEYWORDS[topic_lower]
            else:
                # If no keywords known, use the topic name itself
                self._topic_keywords[topic_lower] = [topic_lower]

    def validate(self, text: str) -> ValidationResult:
        violations: list[Violation] = []
        matched_topics: dict[str, float] = {}

        text_lower = text.lower()
        words = re.findall(r"\w+", text_lower)
        total_words = max(len(words), 1)

        for topic, keywords in self._topic_keywords.items():
            hits = sum(1 for kw in keywords if kw in text_lower)
            score = min(hits / total_words * 5.0, 1.0)
            matched_topics[topic] = score

            if score >= self.config.threshold:
                violations.append(
                    Violation(
                        filter_name="topic_filter",
                        category=topic,
                        severity="high",
                        message=f"Denied topic detected: '{topic}' (score={score:.2f})",
                        confidence=score,
                    )
                )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            metadata={"topic_filter": {"scores": matched_topics}},
        )
