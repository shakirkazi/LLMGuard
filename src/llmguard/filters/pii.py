"""PII filter — detects and masks personally identifiable information using Presidio."""

from __future__ import annotations

from llmguard.config import PIIFilterConfig
from llmguard.defaults.pii_patterns import DEFAULT_ENTITIES, resolve_entity
from llmguard.filters.base import BaseFilter
from llmguard.result import ValidationResult, Violation


class PIIFilter(BaseFilter):
    """Detects and optionally masks PII in text using Presidio."""

    def __init__(self, config: PIIFilterConfig) -> None:
        self.config = config
        self._entities = [resolve_entity(e) for e in config.entities] or DEFAULT_ENTITIES
        self._analyzer = None
        self._anonymizer = None

    def _ensure_loaded(self) -> None:
        """Lazy-load Presidio engines on first use."""
        if self._analyzer is not None:
            return
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine

        self._analyzer = AnalyzerEngine()
        self._anonymizer = AnonymizerEngine()

    def validate(self, text: str) -> ValidationResult:
        self._ensure_loaded()

        results = self._analyzer.analyze(
            text=text,
            entities=self._entities,
            language="en",
            score_threshold=self.config.score_threshold,
        )

        violations: list[Violation] = []
        detected: list[dict] = []

        for r in results:
            detected.append(
                {
                    "entity_type": r.entity_type,
                    "start": r.start,
                    "end": r.end,
                    "score": r.score,
                    "text": text[r.start : r.end],
                }
            )
            violations.append(
                Violation(
                    filter_name="pii_filter",
                    category=r.entity_type,
                    severity="high",
                    message=f"PII detected: {r.entity_type} at position {r.start}-{r.end}",
                    span=(r.start, r.end),
                    confidence=r.score,
                )
            )

        masked_text = None
        if results and self.config.action == "mask":
            anonymized = self._anonymizer.anonymize(
                text=text, analyzer_results=results
            )
            masked_text = anonymized.text

        is_valid = True
        if self.config.action == "block" and violations:
            is_valid = False
        elif self.config.action == "allow":
            is_valid = True
        elif self.config.action == "mask":
            is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            masked_text=masked_text,
            metadata={"pii_filter": {"detected": detected, "action": self.config.action}},
        )

    def mask(self, text: str) -> str:
        """Convenience method: return the PII-masked version of text."""
        result = self.validate(text)
        return result.masked_text if result.masked_text else text
