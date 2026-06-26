import functools
import os
import pickle
import time

import numpy as np
import faiss
from typing import Any, List, Optional

from src.rag.embedding import EmbeddingPipeline
from src.manifest import save_manifest

_VECTOR_CACHE_TTL = int(os.getenv("VECTOR_CACHE_TTL", "60"))
_EF_CONSTRUCTION = int(os.getenv("HNSW_EF_CONSTRUCTION", "200"))
_EF_SEARCH = int(os.getenv("HNSW_EF_SEARCH", "50"))


class FaissVectorStore:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.embedding_pipeline = EmbeddingPipeline()
        self.index: Optional[faiss.Index] = None
        self.metadata: List[dict] = []
        self._query_cache: dict[str, tuple[float, list[dict]]] = {}

    def build_from_documents(self, documents: List[Any], data_dir: str = "data") -> bool:
        os.makedirs(self.persist_dir, exist_ok=True)
        chunks = self.embedding_pipeline.chunk_documents(documents)
        if not chunks:
            return False
        embeddings = self.embedding_pipeline.embed_chunks(chunks)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexHNSWFlat(dimension, 32)
        self.index.hnsw.efConstruction = _EF_CONSTRUCTION
        self.index.add(embeddings.astype(np.float32))
        self.metadata = [
            {"text": chunk.page_content, "source": getattr(chunk, "metadata", {})}
            for chunk in chunks
        ]
        self._save()
        save_manifest(self.persist_dir, data_dir)
        return True

    def _save(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        if self.index is None:
            raise RuntimeError("Index not built yet")
        faiss.write_index(self.index, os.path.join(self.persist_dir, "faiss.index"))
        with open(os.path.join(self.persist_dir, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        if os.path.exists(faiss_path) and os.path.exists(meta_path):
            self.index = faiss.read_index(faiss_path)
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)

    def query(self, query: str, top_k: int = 5) -> List[dict]:
        cache_key = f"{query}:{top_k}"
        now = time.time()
        cached = self._query_cache.get(cache_key)
        if cached and (now - cached[0]) < _VECTOR_CACHE_TTL:
            from app.ml.metrics import increment
            increment("vector_cache_hits")
            return cached[1]

        if self.index is None:
            return []

        query_emb = self.embedding_pipeline.embed_query(query)
        if hasattr(self.index, 'hnsw'):
            self.index.hnsw.efSearch = _EF_SEARCH
        distances, indices = self.index.search(query_emb.astype(np.float32), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "metadata": self.metadata[idx],
                    "distance": float(distances[0][i]),
                })
        self._query_cache[cache_key] = (now, results)
        return results

    def clear_cache(self):
        self._query_cache.clear()

    def invalidate_cache(self):
        self._query_cache.clear()


_VECTORSTORE: FaissVectorStore | None = None


def get_vectorstore(persist_dir: str = "faiss_store") -> FaissVectorStore:
    global _VECTORSTORE
    if _VECTORSTORE is None:
        store = FaissVectorStore(persist_dir)
        store.load()
        _VECTORSTORE = store
    return _VECTORSTORE
