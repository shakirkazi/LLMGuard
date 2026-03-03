"""Tests for the WordFilter."""

from llmguard.config import WordFilterConfig
from llmguard.filters.word import WordFilter


def test_blocked_word_detected():
    config = WordFilterConfig(
        enabled=True,
        blocked_words=["badword"],
        use_profanity_list=False,
    )
    f = WordFilter(config)
    result = f.validate("This contains badword in it")
    assert not result.is_valid
    assert len(result.violations) == 1
    assert result.violations[0].category == "blocked_word"


def test_blocked_phrase_detected():
    config = WordFilterConfig(
        enabled=True,
        blocked_phrases=["bad phrase"],
        use_profanity_list=False,
    )
    f = WordFilter(config)
    result = f.validate("This has a bad phrase inside")
    assert not result.is_valid
    assert result.violations[0].category == "blocked_phrase"


def test_clean_text_passes():
    config = WordFilterConfig(
        enabled=True,
        blocked_words=["badword"],
        blocked_phrases=["bad phrase"],
        use_profanity_list=False,
    )
    f = WordFilter(config)
    result = f.validate("This is perfectly fine text")
    assert result.is_valid
    assert len(result.violations) == 0


def test_case_insensitive_by_default():
    config = WordFilterConfig(
        enabled=True,
        blocked_words=["BadWord"],
        use_profanity_list=False,
    )
    f = WordFilter(config)
    result = f.validate("BADWORD is here")
    assert not result.is_valid


def test_case_sensitive_mode():
    config = WordFilterConfig(
        enabled=True,
        blocked_words=["BadWord"],
        use_profanity_list=False,
        case_sensitive=True,
    )
    f = WordFilter(config)
    result = f.validate("badword is here")
    assert result.is_valid


def test_empty_text():
    config = WordFilterConfig(
        enabled=True,
        blocked_words=["bad"],
        use_profanity_list=False,
    )
    f = WordFilter(config)
    result = f.validate("")
    assert result.is_valid


def test_profanity_detection():
    config = WordFilterConfig(enabled=True, use_profanity_list=True)
    f = WordFilter(config)
    result = f.validate("What the shit is this")
    if f._profanity:
        assert not result.is_valid
        assert any(v.category == "profanity" for v in result.violations)
