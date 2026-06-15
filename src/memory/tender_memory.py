from src.memory.base import MemoryStore


TENDERS_KEY = "tenders"


class TenderMemory:
    def __init__(self, store: MemoryStore):
        self.store = store

    def save_tenders(self, tenders: list[dict]) -> None:
        existing = self.store.load(TENDERS_KEY) or []
        existing.extend(tenders)
        self.store.save(TENDERS_KEY, existing)

    def get_tenders(self) -> list[dict]:
        return self.store.load(TENDERS_KEY) or []

    def clear(self) -> None:
        self.store.delete(TENDERS_KEY)
