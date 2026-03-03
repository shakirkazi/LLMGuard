"""Integration tests for the LLMGuard class."""

import pytest

from llmguard import GuardConfig, LLMGuard, ValidationResult


def test_create_from_dict():
    guard = LLMGuard({"word_filter": {"enabled": True, "blocked_words": ["bad"]}})
    assert guard.config.word_filter.enabled


def test_create_from_config_object():
    config = GuardConfig(word_filter={"enabled": True, "blocked_words": ["bad"]})
    guard = LLMGuard(config)
    assert guard.config.word_filter.enabled


def test_create_default():
    guard = LLMGuard()
    result = guard.validate("Hello world")
    assert result.is_valid


def test_word_filter_integration():
    guard = LLMGuard({
        "word_filter": {
            "enabled": True,
            "blocked_words": ["forbidden"],
            "use_profanity_list": False,
        }
    })
    result = guard.validate("This is forbidden content")
    assert not result.is_valid
    assert any(v.filter_name == "word_filter" for v in result.violations)


def test_content_filter_integration():
    guard = LLMGuard({
        "content_filter": {
            "enabled": True,
            "categories": {"hate": 0.3},
        }
    })
    result = guard.validate("racist bigot hate supremacy")
    assert not result.is_valid


def test_pii_filter_integration():
    guard = LLMGuard({
        "pii_filter": {
            "enabled": True,
            "entities": ["EMAIL"],
            "action": "mask",
        }
    })
    result = guard.validate("Email me at test@example.com")
    assert result.masked_text is not None
    assert "test@example.com" not in result.masked_text


def test_topic_filter_integration():
    guard = LLMGuard({
        "topic_filter": {
            "enabled": True,
            "denied_topics": ["politics"],
        }
    })
    result = guard.validate("The election campaign and congress vote on legislation")
    assert not result.is_valid


def test_multiple_filters():
    guard = LLMGuard({
        "word_filter": {
            "enabled": True,
            "blocked_words": ["forbidden"],
            "use_profanity_list": False,
        },
        "content_filter": {
            "enabled": True,
            "categories": {"hate": 0.3},
        },
    })
    result = guard.validate("This forbidden racist hate content")
    assert not result.is_valid
    assert len(result.violations) >= 2


def test_validate_input_alias():
    guard = LLMGuard({"word_filter": {"enabled": True, "blocked_words": ["bad"], "use_profanity_list": False}})
    result = guard.validate_input("bad text")
    assert not result.is_valid


def test_validate_output_alias():
    guard = LLMGuard({"word_filter": {"enabled": True, "blocked_words": ["bad"], "use_profanity_list": False}})
    result = guard.validate_output("bad text")
    assert not result.is_valid


def test_mask_pii_convenience():
    guard = LLMGuard({
        "pii_filter": {
            "enabled": True,
            "entities": ["EMAIL"],
            "action": "mask",
        }
    })
    masked = guard.mask_pii("Contact user@test.com")
    assert "user@test.com" not in masked


def test_mask_pii_without_filter():
    guard = LLMGuard()
    result = guard.mask_pii("Contact user@test.com")
    assert result == "Contact user@test.com"


def test_validation_result_bool():
    r = ValidationResult(is_valid=True)
    assert bool(r) is True
    r2 = ValidationResult(is_valid=False)
    assert bool(r2) is False
