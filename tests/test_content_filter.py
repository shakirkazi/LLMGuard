"""Tests for the ContentFilter."""

from llmguard.config import ContentFilterConfig
from llmguard.filters.content import ContentFilter


def test_hate_content_detected():
    config = ContentFilterConfig(
        enabled=True,
        categories={"hate": 0.3},
    )
    f = ContentFilter(config)
    result = f.validate("This racist bigot promotes supremacy and hate")
    assert not result.is_valid
    assert any(v.category == "hate" for v in result.violations)


def test_violence_content_detected():
    config = ContentFilterConfig(
        enabled=True,
        categories={"violence": 0.3},
    )
    f = ContentFilter(config)
    result = f.validate("They plan to kill murder and attack people")
    assert not result.is_valid
    assert any(v.category == "violence" for v in result.violations)


def test_clean_text_passes():
    config = ContentFilterConfig(
        enabled=True,
        categories={"hate": 0.5, "violence": 0.5},
    )
    f = ContentFilter(config)
    result = f.validate("The weather is nice today and birds are singing")
    assert result.is_valid


def test_scores_in_metadata():
    config = ContentFilterConfig(
        enabled=True,
        categories={"hate": 0.5, "violence": 0.5},
    )
    f = ContentFilter(config)
    result = f.validate("Some neutral text")
    assert "content_filter" in result.metadata
    assert "scores" in result.metadata["content_filter"]


def test_high_threshold_not_triggered():
    config = ContentFilterConfig(
        enabled=True,
        categories={"hate": 0.99},
    )
    f = ContentFilter(config)
    result = f.validate("One hate word in a long sentence of many words here today")
    assert result.is_valid


def test_empty_text():
    config = ContentFilterConfig(enabled=True, categories={"hate": 0.5})
    f = ContentFilter(config)
    result = f.validate("")
    assert result.is_valid
