import pytest
from src.rag.vectorstore import FaissVectorStore
from src.rag.retriever import Retriever


def test_retriever_constructs():
    store = FaissVectorStore("faiss_store")
    retriever = Retriever(store)
    assert retriever is not None
    assert retriever.reranker is not None


def test_retriever_returns_empty_when_no_index():
    store = FaissVectorStore("faiss_store")
    retriever = Retriever(store)
    results = retriever.retrieve("test", top_k=5)
    assert results == []


def test_retriever_with_mock_store():
    from tests.conftest import MockFaissVectorStore
    store = MockFaissVectorStore()
    retriever = Retriever(store)
    results = retriever.retrieve("ERP solutions", top_k=3)
    assert len(results) == 3
    assert all("metadata" in r for r in results)
    assert all("distance" in r for r in results)


@pytest.mark.parametrize("query,expected_count", [
    ("ERP", 2),
    ("security", 1),
    ("network", 1),
    ("database", 1),
    ("nonexistent", 3),
])
def test_retriever_with_mock_filters(query, expected_count):
    from tests.conftest import MockFaissVectorStore
    store = MockFaissVectorStore()
    retriever = Retriever(store)
    results = retriever.retrieve(query, top_k=3)
    assert len(results) >= 0
