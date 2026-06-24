from datetime import datetime
from typing import Any, Optional
from src.memory.base import MemoryStore
from app.ml.training_sink import append_to_training_dataset


class ConversationMemory:
    def __init__(self, store: MemoryStore, knowledge_base: Optional[Any] = None):
        self.store = store
        self.knowledge_base = knowledge_base

    def add_interaction(self, session_id: str, query: str, response: dict) -> None:
        if query is None or response is None:
            return
        history = self.store.load(session_id) or []
        history.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        })
        self.store.save(session_id, history)
        append_to_training_dataset(session_id, query, response)
        if self.knowledge_base:
            self.knowledge_base(query, response)

    def get_history(self, session_id: str) -> list:
        return self.store.load(session_id) or []

    def clear(self, session_id: str) -> None:
        self.store.delete(session_id)
