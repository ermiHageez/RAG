# Sprint 6.5 — Memory Layer

> Add persistent memory for conversations, leads, and tenders to enable stateful agent behavior.

---

## Goal

Create an abstract storage layer that supports local JSON (immediate) and SQLite/PostgreSQL (future) without code changes.

---

## Structure

```
src/memory/
├── __init__.py
├── base.py                # Abstract storage interface
├── conversation_memory.py # Interaction history
├── lead_memory.py         # Previously discovered leads
└── tender_memory.py       # Previously discovered tenders
```

---

## Storage Abstraction (`src/memory/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any, List, Optional

class MemoryStore(ABC):
    @abstractmethod
    def save(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def load(self, key: str) -> Optional[Any]: ...

    @abstractmethod
    def list_keys(self) -> List[str]: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...


class JSONMemoryStore(MemoryStore):
    """Local JSON file storage — default implementation."""

    def __init__(self, path: str = "memory_store/"):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def save(self, key: str, value: Any) -> None:
        filepath = os.path.join(self.path, f"{key}.json")
        with open(filepath, "w") as f:
            json.dump(value, f, indent=2, default=str)

    def load(self, key: str) -> Optional[Any]:
        filepath = os.path.join(self.path, f"{key}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath) as f:
            return json.load(f)

    def list_keys(self) -> List[str]:
        return [f.replace(".json", "") for f in os.listdir(self.path) if f.endswith(".json")]

    def delete(self, key: str) -> None:
        filepath = os.path.join(self.path, f"{key}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
```

Future: `SQLiteMemoryStore(MemoryStore)`, `PostgresMemoryStore(MemoryStore)`

---

## Conversation Memory (`src/memory/conversation_memory.py`)

```python
class ConversationMemory:
    def __init__(self, store: MemoryStore):
        self.store = store

    def add_interaction(self, session_id: str, query: str, response: dict) -> None:
        history = self.store.load(session_id) or []
        history.append({"query": query, "response": response, "timestamp": datetime.now().isoformat()})
        self.store.save(session_id, history)

    def get_history(self, session_id: str) -> list:
        return self.store.load(session_id) or []

    def clear(self, session_id: str) -> None:
        self.store.delete(session_id)
```

## Lead Memory (`src/memory/lead_memory.py`)

```python
class LeadMemory:
    def __init__(self, store: MemoryStore):
        self.store = store

    def save_leads(self, leads: list[dict]) -> None:
        existing = self.store.load("leads") or []
        existing.extend(leads)
        self.store.save("leads", existing)

    def get_leads(self) -> list[dict]:
        return self.store.load("leads") or []

    def deduplicate(self) -> list[dict]:
        """Remove duplicate leads by company name."""
        leads = self.get_leads()
        seen = set()
        unique = []
        for lead in leads:
            name = lead.get("company_name", "").lower().strip()
            if name and name not in seen:
                seen.add(name)
                unique.append(lead)
        return unique
```

## Tender Memory (`src/memory/tender_memory.py`)

Same pattern as LeadMemory for storing previously seen tenders.

---

## Integration with LangGraph

Memory instances are initialized in the graph and passed to agents:

```python
def build_agent(memory_store: MemoryStore | None = None):
    store = memory_store or JSONMemoryStore()
    conv_memory = ConversationMemory(store)
    lead_memory = LeadMemory(store)
    tender_memory = TenderMemory(store)
    # ... graph building with memory-aware nodes
```

---

## Files Changed

| File | Change |
|---|---|
| `src/memory/__init__.py` | **NEW** |
| `src/memory/base.py` | **NEW** |
| `src/memory/conversation_memory.py` | **NEW** |
| `src/memory/lead_memory.py` | **NEW** |
| `src/memory/tender_memory.py` | **NEW** |

---

## Future Migration Path

| Storage | When |
|---|---|
| `JSONMemoryStore` | Now (v3) |
| `SQLiteMemoryStore` | High-volume single-user |
| `PostgresMemoryStore` | Multi-user / production deployment |

No agent code changes needed — swap the injected store.
