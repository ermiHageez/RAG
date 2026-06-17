# Sprint 9.4 — RAG Integration with pgvector Knowledge Base

> Wire `search_knowledge()` into the `Retriever` as an optional second vector source alongside FAISS.

---

## File to Modify

### `src/rag/retriever.py` (modify)

Current `Retriever` class wraps only `FaissVectorStore`. Changes:

1. Add `pgvector_source` parameter (default `None`)
2. In `retrieve()`:
   - If `pgvector_source` is provided, call `search_knowledge(query_embedding)` to get top-K from pgvector
   - If both FAISS and pgvector return results, **interleave** them by similarity score (highest first), deduplicate by content
   - If only one source has results, return those

The query embedding comes from the same `EmbeddingPipeline.embed_query()` that FAISS uses — no new embedding infrastructure needed.

### Merge Strategy

| Source | Keys |
|--------|------|
| FAISS | `{metadata: {text, source}, distance}` |
| pgvector | `{id, content, metadata, created_at, similarity}` |

Normalize both to a common format `{text, source, score}` before merging, where score is 0–1 (higher = more relevant).
