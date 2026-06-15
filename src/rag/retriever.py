from typing import Optional
from src.rag.vectorstore import FaissVectorStore
from src.rag.reranker import Reranker, NoOpReranker


class Retriever:
    def __init__(self, vectorstore: FaissVectorStore, reranker: Optional[Reranker] = None):
        self.vectorstore = vectorstore
        self.reranker = reranker or NoOpReranker()

    def retrieve(self, query: str, top_k: int = 20, rerank_top_k: int = 5) -> list[dict]:
        results = self.vectorstore.query(query, top_k=top_k)
        if results:
            results = self.reranker.rerank(query, results)
            results = results[:rerank_top_k]
        return results
