import pytest
from unittest.mock import patch, MagicMock
from src.agents.graph import build_agent


@pytest.fixture(autouse=True)
def mock_all_externals(monkeypatch, mock_vectorstore):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)

    mock_search = lambda query: [{"name": "Mock Corp", "sector": "Finance", "location": "Addis", "contact": "mock@corp.et", "description": "A test company", "source": "mock"}]
    mock_tenders = lambda sector=None: [{"title": "Test Tender", "description": "A test tender", "deadline": "2026-12-31T00:00:00", "url": "https://test.et", "category": "Finance", "source": "mock", "relevance_score": 0.9}]

    import mcp_server.tools.search as search_mod
    import mcp_server.tools.tenders as tenders_mod
    import src.agents.knowledge.knowledge_agent as ka_mod

    monkeypatch.setattr(search_mod, "discover_ethiopian_enterprises", mock_search)
    monkeypatch.setattr(tenders_mod, "fetch_active_tenders", mock_tenders)
    monkeypatch.setattr(ka_mod, "_get_retriever", lambda: MagicMock(
        retrieve=lambda q, top_k=5, rerank_top_k=3: [
            {"metadata": {"text": "eTech provides ERP solutions", "source": {}}, "distance": 0.5}
        ]
    ))


def test_e2e_pipeline_runs_successfully():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders in Ethiopia"})
    assert result is not None
    assert isinstance(result, dict)


def test_e2e_pipeline_populates_leads():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads"})
    assert len(result.get("qualified_leads", [])) > 0


def test_e2e_pipeline_populates_tenders():
    agent = build_agent()
    result = agent.invoke({"query": "find active tenders"})
    assert len(result.get("qualified_tenders", [])) > 0


def test_e2e_pipeline_produces_sales_intel():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders"})
    si = result.get("sales_intelligence", {})
    assert si is not None


def test_e2e_pipeline_creates_n8n_payload():
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads"})
    payload = result.get("n8n_payload")
    assert payload is not None
    assert "query" in payload
    assert "leads" in payload
    assert "tenders" in payload


def test_e2e_pipeline_empty_query_does_not_error():
    agent = build_agent()
    result = agent.invoke({"query": ""})
    assert result is not None


def test_e2e_pipeline_all_state_keys_present():
    agent = build_agent()
    expected_keys = {
        "query", "route", "qualified_leads", "qualified_tenders",
        "knowledge_context", "sales_intelligence", "draft_email",
        "requires_human_approval", "approval_reason", "n8n_payload",
    }
    result = agent.invoke({"query": "test"})
    assert expected_keys.issubset(result.keys())
