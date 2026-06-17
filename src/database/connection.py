import os
from typing import Optional
import psycopg
from psycopg import Connection
from pgvector.psycopg import register_vector
from src.database.schema import create_tables


class DatabaseManager:
    _connection: Optional[Connection] = None

    @classmethod
    def get_connection(cls) -> Connection:
        if cls._connection is None or cls._connection.closed:
            cls._connection = psycopg.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("DB_NAME", "postgres"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "ermi@0716"),
                autocommit=True,
            )
            register_vector(cls._connection)
        return cls._connection

    @classmethod
    def init_db(cls) -> None:
        conn = cls.get_connection()
        create_tables(conn)

    @classmethod
    def close(cls) -> None:
        if cls._connection is not None and not cls._connection.closed:
            cls._connection.close()
        cls._connection = None
