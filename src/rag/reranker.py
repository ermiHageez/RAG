from abc import ABC, abstractmethod


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        ...


class NoOpReranker(Reranker):
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        return results
