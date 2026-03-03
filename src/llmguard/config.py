"""Configuration models for LLMGuard."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ContentFilterConfig(BaseModel):
    """Configuration for the content filter."""

    enabled: bool = False
    categories: dict[str, float] = Field(
        default_factory=lambda: {
            "hate": 0.5,
            "violence": 0.5,
            "sexual": 0.5,
            "profanity": 0.5,
        },
        description="Category name to confidence threshold mapping",
    )


class PIIFilterConfig(BaseModel):
    """Configuration for the PII filter."""

    enabled: bool = False
    entities: list[str] = Field(
        default_factory=lambda: [
            "EMAIL",
            "PHONE",
            "SSN",
            "CREDIT_CARD",
            "IP_ADDRESS",
            "PERSON",
            "LOCATION",
            "DATE_TIME",
        ]
    )
    action: Literal["mask", "block", "allow"] = "mask"
    score_threshold: float = 0.5


class WordFilterConfig(BaseModel):
    """Configuration for the word filter."""

    enabled: bool = False
    blocked_words: list[str] = Field(default_factory=list)
    blocked_phrases: list[str] = Field(default_factory=list)
    use_profanity_list: bool = True
    case_sensitive: bool = False


class TopicFilterConfig(BaseModel):
    """Configuration for the topic filter."""

    enabled: bool = False
    denied_topics: list[str] = Field(default_factory=list)
    topic_keywords: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Custom keyword lists per topic. If empty, built-in defaults are used.",
    )
    threshold: float = 0.3


class GuardConfig(BaseModel):
    """Main configuration for LLMGuard."""

    content_filter: ContentFilterConfig = Field(default_factory=ContentFilterConfig)
    pii_filter: PIIFilterConfig = Field(default_factory=PIIFilterConfig)
    word_filter: WordFilterConfig = Field(default_factory=WordFilterConfig)
    topic_filter: TopicFilterConfig = Field(default_factory=TopicFilterConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> GuardConfig:
        """Load configuration from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    @classmethod
    def from_dict(cls, data: dict) -> GuardConfig:
        """Load configuration from a dictionary."""
        return cls.model_validate(data)
