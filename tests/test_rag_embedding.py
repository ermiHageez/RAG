import numpy as np
import pytest

from src.rag.embedding import EmbeddingPipeline


class MockEmbeddings:
    def embed_documents(self, texts):
        return [np.zeros(768) for _ in texts]

    def embed_query(self, text):
        return np.zeros(768)


class MockDocument:
    def __init__(self, content: str):
        self.page_content = content
        self.metadata = {}


class TestEmbeddingPipeline:
    @pytest.fixture
    def pipeline(self, monkeypatch):
        monkeypatch.setattr("src.rag.embedding.get_embedding_model", lambda: MockEmbeddings())
        return EmbeddingPipeline()

    def test_chunk_documents(self, pipeline):
        docs = [MockDocument("word " * 500)]
        chunks = pipeline.chunk_documents(docs)
        assert len(chunks) > 1

    def test_embed_query_returns_array(self, pipeline):
        result = pipeline.embed_query("test query")
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32

    def test_embed_query_cache(self, pipeline):
        result1 = pipeline.embed_query("cache test")
        result2 = pipeline.embed_query("cache test")
        assert np.array_equal(result1, result2)

    def test_embed_chunks(self, pipeline):
        docs = [MockDocument("Test document.")]
        chunks = pipeline.chunk_documents(docs)
        embeddings = pipeline.embed_chunks(chunks)
        assert isinstance(embeddings, np.ndarray)

    def test_clear_cache(self, pipeline):
        pipeline.embed_query("clear me")
        pipeline.clear_cache()
        # cache_clear shouldn't raise
        result = pipeline.embed_query("clear me")
        assert isinstance(result, np.ndarray)

    def test_async_embed_query(self, pipeline):
        import asyncio
        result = asyncio.run(pipeline.async_embed_query("async test"))
        assert isinstance(result, np.ndarray)

    def test_clean_documents(self, pipeline):
        docs = [MockDocument("Header\n=====\nBody text\n-----\nMore body")]
        cleaned = pipeline._clean_documents(docs)
        assert "=====" not in cleaned[0].page_content
        assert "Body text" in cleaned[0].page_content
