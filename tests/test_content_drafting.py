from src.agents.content.content_agent import (
    _validate_email,
    _personalization_score,
)


def test_validate_email_valid():
    assert _validate_email("test@example.com") is True
    assert _validate_email("user.name+tag@domain.co.et") is True


def test_validate_email_invalid():
    assert _validate_email("not-an-email") is False
    assert _validate_email("") is False
    assert _validate_email(None) is False


def test_personalization_score_high():
    body = "Dear Sample Bank, we at eTech understand the Finance sector in Ethiopia needs robust solutions."
    score = _personalization_score(body, "Sample Bank", "Finance")
    assert 0.5 <= score <= 1.0


def test_personalization_score_low():
    body = "Dear Sir/Madam, we are writing to you today."
    score = _personalization_score(body, "Unknown", "General")
    assert score <= 0.3
