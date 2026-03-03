# LLMGuard

Local content and PII filtering library for LLM pipelines. Runs entirely locally — no cloud dependencies.

## Installation

```bash
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
```

## Quick Start

```python
from llmguard import LLMGuard

guard = LLMGuard({
    "pii_filter": {"enabled": True, "entities": ["EMAIL", "PHONE", "SSN"], "action": "mask"},
    "word_filter": {"enabled": True, "blocked_words": ["forbidden"]},
    "content_filter": {"enabled": True, "categories": {"hate": 0.5}},
    "topic_filter": {"enabled": True, "denied_topics": ["politics"]},
})

result = guard.validate("Contact john@example.com about the election")
print(result.is_valid)      # False
print(result.masked_text)   # "Contact <EMAIL_ADDRESS> about the election"
print(result.violations)    # [Violation(...), ...]

# Quick PII masking
masked = guard.mask_pii("Email: user@test.com")
```

## Filters

| Filter | Description |
|--------|-------------|
| **WordFilter** | Blocked words/phrases + profanity detection |
| **ContentFilter** | Keyword-based hate/violence/sexual/profanity classification |
| **PIIFilter** | Presidio-based PII detection & masking (email, phone, SSN, etc.) |
| **TopicFilter** | Keyword-based denied topic detection |

## Running Tests

```bash
pytest tests/
```
