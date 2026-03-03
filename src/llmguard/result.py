"""Validation result types for LLMGuard."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Violation:
    """A single filter violation."""

    filter_name: str
    category: str
    severity: str  # "low", "medium", "high"
    message: str
    span: tuple[int, int] | None = None  # character offsets if applicable
    confidence: float = 1.0


@dataclass
class ValidationResult:
    """Result of running text through LLMGuard filters."""

    is_valid: bool
    violations: list[Violation] = field(default_factory=list)
    masked_text: str | None = None
    metadata: dict = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.is_valid
