import pytest
from unittest.mock import MagicMock
from src.agents.graph import build_agent


@pytest.fixture(autouse=True)
def mock_externals(monkeypatch, mock_vectorstore):
    mock_search = lambda query: [{"name": "Test Corp", "sector": "Finance", "location": "Addis", "contact": "", "description": "Test", "source": "mock"}]
    mock_tenders = lambda sector=None: [{"title": "Test Tender", "description": "Test", "deadline": "2026-12-31T00:00:00", "url": "https://test.et", "category": "Finance", "source": "mock", "relevance_score": 0.9}]

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


def test_graph_runs_with_all_agents(mock_ollama):
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads and tenders"})
    assert "route" in result
    assert "n8n_payload" in result


def test_graph_returns_leads(mock_ollama):
    agent = build_agent()
    result = agent.invoke({"query": "find finance leads"})
    assert len(result.get("qualified_leads", [])) > 0


def test_graph_returns_tenders(mock_ollama):
    agent = build_agent()
    result = agent.invoke({"query": "find active tenders"})
    assert len(result.get("qualified_tenders", [])) > 0


def test_graph_returns_knowledge(mock_ollama):
    agent = build_agent()
    result = agent.invoke({"query": "what services does eTech offer"})
    assert len(result.get("knowledge_context", [])) > 0


def test_graph_approval_gate(mock_ollama):
    agent = build_agent()
    result = agent.invoke({"query": "find leads"})
    assert "requires_human_approval" in result
    assert "approval_reason" in result
