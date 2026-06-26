from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        ...


class NoOpReranker(Reranker):
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        return results


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self._model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for CrossEncoderReranker. "
                    "Install it with: pip install sentence-transformers"
                )

    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        self._load()
        if not results:
            return results
        pairs = [(query, r.get("text", r.get("metadata", {}).get("text", ""))) for r in results]
        scores = self._model.predict(pairs)
        scored = list(zip(results, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored]
