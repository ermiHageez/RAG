import json
from typing import Any, Optional
from src.memory.base import MemoryStore
from src.database.connection import DatabaseManager


class PostgresMemoryStore(MemoryStore):
    def save(self, key: str, value: Any) -> None:
        conn = DatabaseManager.get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory_store (key, value)
                VALUES (%s, %s)
                ON CONFLICT (key)
                DO UPDATE SET value = %s, updated_at = NOW()
                """,
                (key, json.dumps(value), json.dumps(value)),
            )

    def load(self, key: str) -> Optional[Any]:
        conn = DatabaseManager.get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT value FROM memory_store WHERE key = %s", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def list_keys(self) -> list[str]:
        conn = DatabaseManager.get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT key FROM memory_store ORDER BY key")
            return [row[0] for row in cur.fetchall()]

    def delete(self, key: str) -> None:
        conn = DatabaseManager.get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM memory_store WHERE key = %s", (key,))
