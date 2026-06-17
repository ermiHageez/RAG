# Sprint 6.2 — RAG Layer Refactor

> Restructure the RAG pipeline into a modular, production-ready layer under `src/rag/`.

---

## Goal

Replace the monolithic `src/embedding.py` + `src/vectorstore.py` with a clean four-module RAG layer that supports pluggable rerankers and preserves FAISS compatibility.

---

## New Structure

```
src/rag/
├── __init__.py
├── embedding.py      # Embedding generation (thin wrapper around factory)
├── vectorstore.py     # FAISS persistence & loading
├── retriever.py       # Top-k retrieval pipeline
└── reranker.py        # Abstract reranker interface + optional implementation
```

---

## Module Responsibilities

### `src/rag/embedding.py`

- Thin wrapper around `get_embedding_model()`
- Provides `EmbeddingPipeline` class:
  - `chunk_documents(docs)` — RecursiveCharacterTextSplitter (preserve existing strategy)
  - `embed_chunks(chunks)` — Calls `OllamaEmbeddings.embed_documents()`
  - `embed_query(query)` — Calls `OllamaEmbeddings.embed_query()`

```python
class EmbeddingPipeline:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.embeddings = get_embedding_model()
        self.splitter = RecursiveCharacterTextSplitter(...)

    def chunk_documents(self, documents) -> list:
        ...

    def embed_chunks(self, chunks) -> np.ndarray:
        texts = [c.page_content for c in chunks]
        vectors = self.embeddings.embed_documents(texts)
        return np.array(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.embeddings.embed_query(query)
        return np.array([vec], dtype=np.float32)
```

### `src/rag/vectorstore.py`

- Port existing `FaissVectorStore` from `src/vectorstore.py`
- Preserve `faiss.index` + `metadata.pkl` persistence format
- Preserve manifest-based cache invalidation
- Public API:
  - `build_from_documents(docs, data_dir)` → `bool`
  - `load()` → loads persisted index
  - `query(query, top_k)` → `list[dict]` (legacy compat)

### `src/rag/retriever.py`

New retrieval pipeline:

```python
class Retriever:
    def __init__(self, vectorstore: FaissVectorStore, reranker: Reranker | None = None):
        self.vectorstore = vectorstore
        self.reranker = reranker

    def retrieve(self, query: str, top_k: int = 20, rerank_top_k: int = 5) -> list[dict]:
        # 1. FAISS top-k (default 20)
        results = self.vectorstore.query(query, top_k=top_k)
        # 2. Optional reranking
        if self.reranker and results:
            results = self.reranker.rerank(query, results)
            results = results[:rerank_top_k]
        return results
```

### `src/rag/reranker.py`

Abstract interface for future reranker models:

```python
from abc import ABC, abstractmethod

class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        """Rerank retrieved results. Return sorted list."""
        ...

class NoOpReranker(Reranker):
    def rerank(self, query: str, results: list[dict]) -> list[dict]:
        return results
```

Future implementations:
- `CrossEncoderReranker` — e.g., `BAAI/bge-reranker-v2-m3`
- `LLMReranker` — Use local Ollama model for relevance scoring

---

## Data Flow

```
Query
  ↓
embedding.py: embed_query(query)
  ↓
vectorstore.py: FAISS search (top-20)
  ↓
retriever.py: raw results
  ↓
reranker.py: rerank (NO-OP for now)
  ↓
retriever.py: top-5 final results
  ↓
LLM Context
```

---

## Files Changed

| File | Change |
|---|---|
| `src/rag/__init__.py` | **NEW** |
| `src/rag/embedding.py` | **NEW** — migrated from `src/embedding.py` |
| `src/rag/vectorstore.py` | **NEW** — migrated from `src/vectorstore.py` |
| `src/rag/retriever.py` | **NEW** |
| `src/rag/reranker.py` | **NEW** |
| `src/embedding.py` | **DEPRECATED** — remove after migration |
| `src/vectorstore.py` | **DEPRECATED** — remove after migration |

---

## Verification

```python
from src.rag.retriever import Retriever
from src.rag.vectorstore import FaissVectorStore

store = FaissVectorStore("faiss_store")
store.load()
retriever = Retriever(store)
results = retriever.retrieve("Who is the CEO of eTech?", top_k=5)
print(len(results), results[0].keys() if results else "empty")
```
