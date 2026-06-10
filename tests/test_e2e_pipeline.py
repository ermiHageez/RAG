import pytest
from unittest.mock import patch
from src.agent.graph import build_agent


@pytest.fixture(autouse=True)
def mock_all_externals(monkeypatch, mock_vectorstore):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)

    def mock_search(query: str):
        return [{"name": "Mock Corp", "sector": "Finance", "location": "Addis", "contact": "mock@corp.et", "description": "A test company", "source": "mock"}]

    def mock_tenders(sector=None):
        return [{"title": "Test Tender", "description": "A test tender", "deadline": "2026-12-31T00:00:00", "url": "https://test.et", "category": "Finance", "source": "mock", "relevance_score": 0.9}]

    import mcp_server.tools.search as search_mod
    import mcp_server.tools.tenders as tenders_mod

    monkeypatch.setattr(search_mod, "discover_ethiopian_enterprises", mock_search)
    monkeypatch.setattr(tenders_mod, "fetch_active_tenders", mock_tenders)


def test_e2e_pipeline_runs_successfully():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders in Ethiopia"})
    assert result is not None
    assert isinstance(result, dict)


def test_e2e_pipeline_populates_leads():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads"})
    assert len(result.get("found_leads", [])) > 0


def test_e2e_pipeline_populates_tenders():
    agent = build_agent()
    result = agent.invoke({"query": "find active tenders"})
    assert len(result.get("active_tender_listings", [])) > 0


def test_e2e_pipeline_produces_sales_intel():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders"})
    assert len(result.get("sales_intel", [])) > 0
    types = {i["type"] for i in result["sales_intel"]}
    assert "lead" in types
    assert "tender" in types


def test_e2e_pipeline_generates_report():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders"})
    assert result.get("sales_report") is not None
    assert "eTech Sales Intelligence Report" in result["sales_report"]


def test_e2e_pipeline_generates_email_drafts():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders"})
    assert len(result.get("email_drafts", [])) > 0


def test_e2e_pipeline_creates_n8n_payload():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads"})
    payload = result.get("n8n_payload")
    assert payload is not None
    assert "batch" in payload
    assert "total" in payload


def test_e2e_pipeline_empty_query_does_not_error():
    agent = build_agent()
    result = agent.invoke({"query": ""})
    assert result is not None


def test_e2e_pipeline_all_state_keys_present():
    agent = build_agent()
    expected_keys = {
        "query", "rag_context", "found_leads", "active_tender_listings",
        "sales_intel", "sales_report", "email_drafts", "n8n_payload",
    }
    result = agent.invoke({"query": "test"})
    assert expected_keys.issubset(result.keys())
