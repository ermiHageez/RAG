# Sprint 9.6 — Testing

> Start pgvector Docker container, install deps, run tests.

---

## Setup

```bash
# Start pgvector (if not running)
docker run --name local-pgvector \
  -e POSTGRES_PASSWORD=ermi@0716 \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16

# Install new deps
uv add psycopg[binary] pgvector python-dotenv

# Verify connection
python -c "from src.database.connection import DatabaseManager; db = DatabaseManager(); db.init_db(); print('OK')"
```

## Test Cases

| Test | What It Verifies |
|------|-----------------|
| `test_insert_knowledge` | Insert 2 rows, verify IDs returned |
| `test_search_knowledge` | Insert 3 rows with known embeddings, search for closest |
| `test_search_empty` | `search_knowledge()` returns `[]` with no rows |
| `test_postgres_memory_store` | Save → Load → List → Delete cycle |
| `test_retriever_with_pgvector` | `Retriever` with `pgvector_source` returns merged results |

## Expected Result

All 92 existing tests + 5 new = **97 tests passing**.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `connection refused` | Docker not running: `docker start local-pgvector` |
| `cannot import pgvector` | `uv add pgvector` |
| `column is of type vector but expression is of type text` | `register_vector()` not called before insert |
