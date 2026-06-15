from datetime import datetime
from src.memory.base import MemoryStore


class ConversationMemory:
    def __init__(self, store: MemoryStore):
        self.store = store

    def add_interaction(self, session_id: str, query: str, response: dict) -> None:
        history = self.store.load(session_id) or []
        history.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        })
        self.store.save(session_id, history)

    def get_history(self, session_id: str) -> list:
        return self.store.load(session_id) or []

    def clear(self, session_id: str) -> None:
        self.store.delete(session_id)
