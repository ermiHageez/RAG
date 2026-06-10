from datetime import datetime, timedelta
from src.agent.nodes.tender_identification import identify_tenders, _score_relevance
from src.agent.state import AgentState


def test_score_relevance_with_index(mock_vectorstore):
    tender = {
        "title": "Security System",
        "description": "Security cameras for building",
        "procurement_category": "Security",
    }
    score = _score_relevance(tender, mock_vectorstore)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_score_relevance_no_index():
    tender = {"title": "test", "description": "", "procurement_category": ""}
    store = _EmptyIndexStore()
    import src.agent.store
    import src.agent.nodes.tender_identification as mod
    mod.get_vectorstore = lambda: store
    score = mod._score_relevance(tender, store)
    assert score == 0.0


class _EmptyIndexStore:
    class Index:
        pass
    index = None
    def query(self, text, top_k=1):
        return []


def test_identify_tenders_returns_list(empty_state, mock_vectorstore):
    result = identify_tenders(empty_state)
    assert "active_tender_listings" in result
    assert isinstance(result["active_tender_listings"], list)
