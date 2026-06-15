# Sprint 9.2 — Knowledge Base CRUD

> Two clean functions for inserting and searching the `knowledge_base` table using cosine distance (`<=>`).

---

## File to Create

### `src/database/knowledge.py`

**`insert_knowledge(content: str, embedding: list[float], metadata: dict | None = None) -> int`**

- Obtains connection via `DatabaseManager.get_connection()`
- Runs `INSERT INTO knowledge_base (content, embedding, metadata) VALUES (%s, %s, %s) RETURNING id`
- Uses `register_vector()` to handle the vector type
- Returns the new row ID

**`search_knowledge(embedding: list[float], top_n: int = 5) -> list[dict]`**

- Runs:
  ```sql
  SELECT id, content, metadata, created_at,
         1 - (embedding <=> %s::vector) AS similarity
  FROM knowledge_base
  ORDER BY embedding <=> %s::vector
  LIMIT %s
  ```
- Returns list of `{id, content, metadata, created_at, similarity}` sorted by highest similarity
- Returns empty list on any error (connection failure, etc.) — never crashes the caller

---

## Integration Points

- Called from `ConversationMemory.add_interaction()` to save chat embeddings
- Called from `Retriever.retrieve()` to merge with FAISS results
