from src.agents.tender.tender_agent import _score_relevance


class MockVS:
    class Index:
        pass
    index = Index()

    def query(self, text, top_k=1):
        return [{"distance": 0.5}]


def test_score_relevance_with_index():
    vs = MockVS()
    tender = {"title": "Security System", "description": "Install cameras", "procurement_category": "Security"}
    score = _score_relevance(tender, vs)
    assert 0.0 <= score <= 1.0


class MockEmptyVS:
    index = None

    def query(self, text, top_k=1):
        return []


def test_score_relevance_no_index():
    vs = MockEmptyVS()
    tender = {"title": "Test", "description": "", "procurement_category": ""}
    score = _score_relevance(tender, vs)
    assert score == 0.0
