# Sprint 9.3 — PostgresMemoryStore

> Production-ready `MemoryStore` implementation backed by PostgreSQL, replacing `JSONMemoryStore` for concurrent-safe, queryable memory.

---

## File to Create

### `src/memory/postgres_memory.py`

Class `PostgresMemoryStore(MemoryStore)` implementing the ABC:

| Method | Implementation |
|--------|---------------|
| `save(key, value)` | `INSERT INTO memory_store (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s, updated_at = NOW()` |
| `load(key)` | `SELECT value FROM memory_store WHERE key = %s` → returns parsed JSON or `None` |
| `list_keys()` | `SELECT key FROM memory_store ORDER BY key` |
| `delete(key)` | `DELETE FROM memory_store WHERE key = %s` |

**Auto-creates** the `memory_store` table on first use:
```sql
CREATE TABLE IF NOT EXISTS memory_store (
    key       TEXT PRIMARY KEY,
    value     JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

Takes the same env config as `DatabaseManager` — reuses the same connection pool.

---

## Why Not Migrate ABC to Vector?

The `MemoryStore` ABC is key-value by design (`save(key, value)` / `load(key)`). That's the right abstraction for session data (conversation histories, lead lists, tender lists). Vector search is a different pattern — that's what `knowledge_base` is for. Keeping them separate is the clean separation of concerns.
