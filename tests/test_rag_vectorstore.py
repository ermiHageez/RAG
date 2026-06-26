import os
import numpy as np
import pytest

from src.rag.vectorstore import FaissVectorStore


class MockDocument:
    def __init__(self, content: str):
        self.page_content = content
        self.metadata = {}


class TestFaissVectorStore:
    @pytest.fixture
    def store(self, tmp_path):
        persist_dir = str(tmp_path / "faiss_test")
        return FaissVectorStore(persist_dir)

    def test_build_and_query(self, store):
        docs = [MockDocument("eTech provides ERP solutions for Ethiopian enterprises.")]
        result = store.build_from_documents(docs, data_dir="data")
        assert result is True
        assert store.index is not None
        assert len(store.metadata) > 0

        results = store.query("eTech ERP", top_k=1)
        assert len(results) >= 1

    def test_save_load_roundtrip(self, tmp_path):
        persist_dir = str(tmp_path / "faiss_roundtrip")
        store1 = FaissVectorStore(persist_dir)
        docs = [MockDocument("Test document for roundtrip.")]
        store1.build_from_documents(docs)
        assert store1.index is not None

        store2 = FaissVectorStore(persist_dir)
        store2.load()
        assert store2.index is not None
        assert len(store2.metadata) == len(store1.metadata)

        results = store2.query("test", top_k=1)
        assert len(results) >= 1

    def test_empty_index_returns_empty(self, store):
        results = store.query("anything")
        assert results == []

    def test_query_cache(self, store):
        docs = [MockDocument("Cached document about caching.")]
        store.build_from_documents(docs)
        assert store.index is not None

        store._query_cache.clear()
        results1 = store.query("caching", top_k=1)
        assert len(results1) >= 1

        # second call should hit cache
        results2 = store.query("caching", top_k=1)
        assert len(results2) >= 1

    def test_hnsw_params(self, store):
        os.environ["HNSW_EF_CONSTRUCTION"] = "100"
        os.environ["HNSW_EF_SEARCH"] = "30"
        docs = [MockDocument("HNSW parameter test.")]
        store.build_from_documents(docs)
        assert store.index is not None

