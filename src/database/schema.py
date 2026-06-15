from psycopg import Connection


def create_tables(conn: Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id        SERIAL PRIMARY KEY,
                content   TEXT NOT NULL,
                embedding vector(1024) NOT NULL,
                metadata  JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding
            ON knowledge_base
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_store (
                key        TEXT PRIMARY KEY,
                value      JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
