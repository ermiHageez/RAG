import asyncio
import functools
import re
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from typing import Any, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.agents.llm import get_embedding_model

_embed_executor = ThreadPoolExecutor(max_workers=2)


class EmbeddingPipeline:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.embeddings = get_embedding_model()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load embedding model. Check that Ollama is running "
                f"and the model is pulled (`ollama pull <model>`). Error: {e}"
            )

    @staticmethod
    def _clean_documents(documents: List[Any]) -> List[Any]:
        for doc in documents:
            lines = doc.page_content.split("\n")
            cleaned = [l for l in lines if not re.match(r"^[\s]*[-=]{3,}[\s]*$", l)]
            doc.page_content = "\n".join(cleaned)
        return documents

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        documents = self._clean_documents(documents)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(documents)
        return chunks

    def embed_chunks(self, chunks: List[Any], batch_size: int = 50) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        all_vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            vectors = self.embeddings.embed_documents(batch)
            all_vectors.extend(vectors)
        embeddings = np.array(all_vectors, dtype=np.float32)
        return embeddings

    @functools.lru_cache(maxsize=1024)
    def embed_query(self, query: str) -> np.ndarray:
        from app.ml.metrics import increment
        increment("embedding_query_count")
        vec = self.embeddings.embed_query(query)
        return np.array([vec], dtype=np.float32)

    def clear_cache(self):
        self.embed_query.cache_clear()

    async def async_embed_query(self, query: str) -> np.ndarray:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_embed_executor, self.embed_query, query)

    async def async_embed_chunks(self, chunks: List[Any], batch_size: int = 50) -> np.ndarray:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_embed_executor, self.embed_chunks, chunks, batch_size)
