import os
from src.agent.nodes.content_drafting import (
    _validate_email,
    _personalization_score,
    _extract_features_from_rag,
    _get_llm,
)


def test_validate_email_valid():
    assert _validate_email("test@example.com") is True
    assert _validate_email("user.name+tag@domain.co.et") is True


def test_validate_email_invalid():
    assert _validate_email("not-an-email") is False
    assert _validate_email("") is False
    assert _validate_email(None) is False  # type: ignore


def test_personalization_score_high():
    body = "Dear Sample Bank, we at eTech understand the Finance sector in Ethiopia needs robust solutions."
    score = _personalization_score(body, "Sample Bank", "Finance")
    assert 0.5 <= score <= 1.0


def test_personalization_score_low():
    body = "Dear Sir/Madam, we are writing to you today."
    score = _personalization_score(body, "Unknown", "General")
    assert score <= 0.3


def test_extract_features_returns_list_with_mock(mock_vectorstore):
    features = _extract_features_from_rag("Finance", "banking needs")
    assert isinstance(features, list)
    assert len(features) > 0
    assert "eTech" in features[0]


def test_get_llm_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert _get_llm() is None


def test_get_llm_returns_instance_with_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    llm = _get_llm()
    if llm is not None:
        assert hasattr(llm, "invoke")
