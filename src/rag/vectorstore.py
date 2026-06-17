import os
import pickle
import numpy as np
import faiss
from typing import Any, List, Optional
from src.rag.embedding import EmbeddingPipeline
from src.manifest import save_manifest


class FaissVectorStore:
    def __init__(
        self,
        persist_dir: str,
    ):
        self.persist_dir = persist_dir
        self.embedding_pipeline = EmbeddingPipeline()
        self.index: Optional[faiss.Index] = None
        self.metadata: List[dict] = []

    def build_from_documents(self, documents: List[Any], data_dir: str = "data") -> bool:
        os.makedirs(self.persist_dir, exist_ok=True)
        chunks = self.embedding_pipeline.chunk_documents(documents)
        if not chunks:
            return False
        embeddings = self.embedding_pipeline.embed_chunks(chunks)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
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
        if self.index is None:
            return []
        query_emb = self.embedding_pipeline.embed_query(query)
        distances, indices = self.index.search(query_emb.astype(np.float32), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append(
                    {
                        "metadata": self.metadata[idx],
                        "distance": float(distances[0][i]),
                    }
                )
        return results


_VECTORSTORE: FaissVectorStore | None = None


def get_vectorstore(persist_dir: str = "faiss_store") -> FaissVectorStore:
    global _VECTORSTORE
    if _VECTORSTORE is None:
        store = FaissVectorStore(persist_dir)
        store.load()
        _VECTORSTORE = store
    return _VECTORSTORE
