from typing import Optional
from src.database.connection import DatabaseManager


def insert_knowledge(
    content: str,
    embedding: list[float],
    metadata: Optional[dict] = None,
) -> int:
    conn = DatabaseManager.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO knowledge_base (content, embedding, metadata) VALUES (%s, %s, %s) RETURNING id",
            (content, embedding, metadata or {}),
        )
        row = cur.fetchone()
        return row[0] if row else -1


def search_knowledge(
    embedding: list[float],
    top_n: int = 5,
) -> list[dict]:
    conn = DatabaseManager.get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content, metadata, created_at,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (embedding, embedding, top_n),
        )
        return [
            {
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
                "similarity": float(row[4]),
            }
            for row in cur.fetchall()
        ]
