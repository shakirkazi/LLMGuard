"""Tests for the TopicFilter."""

from llmguard.config import TopicFilterConfig
from llmguard.filters.topic import TopicFilter


def test_politics_detected():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["politics"],
    )
    f = TopicFilter(config)
    result = f.validate("The election campaign and the congress vote on legislation")
    assert not result.is_valid
    assert any(v.category == "politics" for v in result.violations)


def test_religion_detected():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["religion"],
    )
    f = TopicFilter(config)
    result = f.validate("The church prayer and worship service was beautiful")
    assert not result.is_valid


def test_clean_text_passes():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["politics", "religion"],
    )
    f = TopicFilter(config)
    result = f.validate("I enjoy programming in Python and building software")
    assert result.is_valid


def test_custom_topic_keywords():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["finance"],
        topic_keywords={"finance": ["stock", "trading", "investment", "portfolio"]},
    )
    f = TopicFilter(config)
    result = f.validate("My stock trading investment portfolio is doing well")
    assert not result.is_valid


def test_unknown_topic_uses_name():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["cooking"],
    )
    f = TopicFilter(config)
    result = f.validate("I love cooking meals every day")
    assert not result.is_valid


def test_empty_text():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["politics"],
    )
    f = TopicFilter(config)
    result = f.validate("")
    assert result.is_valid


def test_scores_in_metadata():
    config = TopicFilterConfig(
        enabled=True,
        denied_topics=["politics"],
    )
    f = TopicFilter(config)
    result = f.validate("Some text about the election")
    assert "topic_filter" in result.metadata
    assert "scores" in result.metadata["topic_filter"]
