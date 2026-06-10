from typing import Any
import pytest
from src.agent.state import AgentState


class MockFaissIndex:
    pass


class MockFaissVectorStore:
    def __init__(self):
        self.index = MockFaissIndex()
        self.metadata = [
            {"text": "eTech provides enterprise resource planning (ERP) solutions for banks and financial institutions", "source": {}},
            {"text": "eTech offers security surveillance systems and access control for government buildings", "source": {}},
            {"text": "eTech delivers network infrastructure including switches, routers, and fiber optics", "source": {}},
            {"text": "eTech provides database management systems and annual maintenance contracts", "source": {}},
            {"text": "eTech implements end-to-end ERP solutions including finance, HR, and procurement modules", "source": {}},
        ]

    def query(self, query: str, top_k: int = 3) -> list[dict]:
        results = []
        for i, meta in enumerate(self.metadata[:top_k]):
            results.append({
                "metadata": meta,
                "distance": 0.5 + (i * 0.1),
            })
        return results


@pytest.fixture
def empty_state() -> AgentState:
    return AgentState(
        query="",
        rag_context=[],
        found_leads=[],
        active_tender_listings=[],
        sales_intel=[],
        sales_report=None,
        email_drafts=[],
        n8n_payload=None,
    )


@pytest.fixture
def sample_leads() -> list[dict]:
    return [
        {"name": "Sample Bank SC", "sector": "Finance", "location": "Addis Ababa", "contact": "info@samplebank.et", "description": "Commercial bank", "source": "mock"},
        {"name": "Sample Insurance PLC", "sector": "Insurance", "location": "Addis Ababa", "contact": "info@sampleins.et", "description": "Insurance provider", "source": "mock"},
    ]


@pytest.fixture
def sample_tenders() -> list[dict]:
    return [
        {"title": "Security System Tender", "description": "Security cameras", "deadline": "2026-12-01T00:00:00", "url": "https://ppa.gov.et/001", "category": "Security Systems", "source": "mock", "relevance_score": 0.85},
        {"title": "ERP Implementation", "description": "ERP system", "deadline": "2026-08-15T00:00:00", "url": "https://ppa.gov.et/002", "category": "ERP Implementation", "source": "mock", "relevance_score": 0.72},
    ]


@pytest.fixture
def mock_vectorstore(monkeypatch) -> MockFaissVectorStore:
    store = MockFaissVectorStore()
    import src.agent.store
    monkeypatch.setattr(src.agent.store, "get_vectorstore", lambda: store)
    return store
