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
