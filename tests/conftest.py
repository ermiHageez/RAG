from typing import Any
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage


@pytest.fixture(autouse=True)
def mock_ollama():
    with patch("src.agents.llm.ChatOllama") as mock_chat, \
         patch("src.agents.llm.OllamaEmbeddings") as mock_emb:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content='{"route": ["lead", "tender", "knowledge"]}')
        mock_chat.return_value = mock_llm

        mock_emb_model = MagicMock()
        mock_emb_model.embed_documents.return_value = [[0.1] * 1024]
        mock_emb_model.embed_query.return_value = [0.1] * 1024
        mock_emb.return_value = mock_emb_model

        yield


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
    import src.rag.vectorstore as rag_vs
    monkeypatch.setattr(rag_vs, "get_vectorstore", lambda: store)
    return store


@pytest.fixture
def mock_old_vectorstore(monkeypatch) -> None:
    import src.rag.vectorstore as rag_vs
    store = MockFaissVectorStore()
    monkeypatch.setattr(rag_vs.FaissVectorStore, "load", lambda self: None)
    monkeypatch.setattr(rag_vs.FaissVectorStore, "query", lambda self, q, top_k=5: [
        {"metadata": {"text": "eTech provides ERP solutions for banks", "source": {}}, "distance": 0.5}
    ])
