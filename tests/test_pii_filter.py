"""Tests for the PIIFilter."""

import pytest

from llmguard.config import PIIFilterConfig
from llmguard.filters.pii import PIIFilter


@pytest.fixture
def pii_filter():
    config = PIIFilterConfig(
        enabled=True,
        entities=["EMAIL", "PHONE", "SSN"],
        action="mask",
    )
    return PIIFilter(config)


def test_email_detected_and_masked(pii_filter):
    result = pii_filter.validate("Contact me at john@example.com please")
    assert len(result.violations) > 0
    assert any(v.category == "EMAIL_ADDRESS" for v in result.violations)
    assert result.masked_text is not None
    assert "john@example.com" not in result.masked_text


def test_phone_detected(pii_filter):
    config = PIIFilterConfig(
        enabled=True,
        entities=["PHONE"],
        action="mask",
        score_threshold=0.3,
    )
    f = PIIFilter(config)
    result = f.validate("My phone number is (212) 555-1234")
    assert any(v.category == "PHONE_NUMBER" for v in result.violations)


def test_ssn_detected(pii_filter):
    config = PIIFilterConfig(
        enabled=True,
        entities=["SSN"],
        action="mask",
        score_threshold=0.3,
    )
    f = PIIFilter(config)
    result = f.validate("My social security number is 219-09-9999")
    assert any(v.category == "US_SSN" for v in result.violations)


def test_clean_text_passes(pii_filter):
    result = pii_filter.validate("The weather is nice today")
    assert result.is_valid
    assert len(result.violations) == 0


def test_block_action():
    config = PIIFilterConfig(
        enabled=True,
        entities=["EMAIL"],
        action="block",
    )
    f = PIIFilter(config)
    result = f.validate("Email: test@example.com")
    assert not result.is_valid


def test_allow_action():
    config = PIIFilterConfig(
        enabled=True,
        entities=["EMAIL"],
        action="allow",
    )
    f = PIIFilter(config)
    result = f.validate("Email: test@example.com")
    assert result.is_valid
    assert len(result.violations) > 0  # Still detected, just allowed


def test_mask_convenience_method(pii_filter):
    masked = pii_filter.mask("My email is user@test.com")
    assert "user@test.com" not in masked


def test_empty_text(pii_filter):
    result = pii_filter.validate("")
    assert result.is_valid
