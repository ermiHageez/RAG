from typing import Optional, Callable
from src.rag.vectorstore import FaissVectorStore
from src.rag.reranker import Reranker, NoOpReranker


class Retriever:
    def __init__(
        self,
        vectorstore: FaissVectorStore,
        reranker: Optional[Reranker] = None,
        pgvector_source: Optional[Callable] = None,
    ):
        self.vectorstore = vectorstore
        self.reranker = reranker or NoOpReranker()
        self.pgvector_source = pgvector_source

    def retrieve(self, query: str, top_k: int = 20, rerank_top_k: int = 5) -> list[dict]:
        results = self.vectorstore.query(query, top_k=top_k)
        if self.pgvector_source:
            pg_results = self.pgvector_source(query, top_k=top_k)
            results = self._merge_results(results, pg_results)
        if results:
            results = self.reranker.rerank(query, results)
            results = results[:rerank_top_k]
        return results

    @staticmethod
    def _merge_results(faiss_results: list[dict], pg_results: list[dict]) -> list[dict]:
        seen = set()
        merged = []

        for r in faiss_results:
            text = r.get("metadata", {}).get("text", "")
            if text and text not in seen:
                seen.add(text)
                merged.append({
                    "text": text,
                    "source": r.get("metadata", {}).get("source", "faiss"),
                    "score": 1.0 / (1.0 + r.get("distance", 1.0)),
                })

        for r in pg_results:
            text = r.get("content", "")
            if text and text not in seen:
                seen.add(text)
                merged.append({
                    "text": text,
                    "source": "pgvector",
                    "score": r.get("similarity", 0.0),
                })

        merged.sort(key=lambda x: x["score"], reverse=True)
        return merged
