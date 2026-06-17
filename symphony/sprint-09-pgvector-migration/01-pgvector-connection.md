# Sprint 9.1 — pgvector Connection & Schema

> Create the database layer for PostgreSQL + pgvector: connection management, `.env` config, and the `knowledge_base` table.

---

## Files to Create

### `src/database/__init__.py`
Empty package marker.

### `src/database/connection.py`
Connection manager class `DatabaseManager`:
- Initializes lazily (first call to `get_connection()`)
- Reads from environment variables:
  - `DB_HOST` (default: `localhost`)
  - `DB_PORT` (default: `5432`)
  - `DB_NAME` (default: `postgres`)
  - `DB_USER` (default: `postgres`)
  - `DB_PASSWORD` (default: `ermi@0716`)
- Uses `psycopg` with `pgvector.psycopg.register_vector()` to register vector type
- Provides:
  - `get_connection() -> psycopg.Connection` — returns singleton connection
  - `close()` — close and reset the connection
  - `init_db()` — calls `create_tables()` from schema module

### `src/database/schema.py`
Single function `create_tables()`:
- `CREATE EXTENSION IF NOT EXISTS vector`
- `CREATE TABLE IF NOT EXISTS knowledge_base` with:
  - `id SERIAL PRIMARY KEY`
  - `content TEXT NOT NULL`
  - `embedding vector(1024) NOT NULL`
  - `metadata JSONB DEFAULT '{}'`
  - `created_at TIMESTAMPTZ DEFAULT NOW()`
- `CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding` using `ivfflat` with `vector_cosine_ops` (lists = 100)

### `src/database/__init__.py`
Public exports:
- `DatabaseManager` (singleton class)
- `create_tables()` from schema

---

## Dependencies

Add to `pyproject.toml`:
```
psycopg[binary]>=3.2
pgvector>=0.3
python-dotenv>=1.0
```

---

## Env Config

Add to `.env` and `.env.example`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=ermi@0716
```
