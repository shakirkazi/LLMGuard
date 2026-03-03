"""LLMGuard — Local content and PII filtering for LLM pipelines."""

from llmguard.config import GuardConfig
from llmguard.guard import LLMGuard
from llmguard.result import ValidationResult, Violation

__all__ = ["LLMGuard", "GuardConfig", "ValidationResult", "Violation"]
__version__ = "0.1.0"
