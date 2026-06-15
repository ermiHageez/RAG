# Sprint 9.5 — build_agent() Wiring

> Connect `PostgresMemoryStore` and pgvector knowledge_base into the LangGraph agent builder.

---

## Files to Modify

### `src/agents/graph.py` (modify)

Current `build_agent(memory_store: Optional[MemoryStore])` already injects memory wrappers. Extend with:

- **`knowledge_base: Optional[object]`** — a callable with `insert(content, embedding, metadata)` for `ConversationMemory` to write chat interactions into pgvector
- When both `memory_store` and `knowledge_base` are provided:
  - `ConversationMemory.add_interaction()` also calls `knowledge_base.insert()` with an embedding of the query
- No changes to `LeadMemory` or `TenderMemory` — they use the memory_store as-is
- The `knowledge_base` parameter is `None` by default, so existing callers are unaffected

### `src/memory/conversation_memory.py` (modify)

Add optional `knowledge_base` parameter to `__init__()`. If provided, `add_interaction()`:
1. Gets embedding via `EmbeddingPipeline.embed_query()`
2. Calls `knowledge_base.insert(content=query, embedding=embedding.tolist()[0], metadata={...})`

No change to `get_history()` or `clear()`.
