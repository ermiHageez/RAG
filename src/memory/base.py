import os
import json
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
    def __init__(self, path: str = "memory_store"):
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
        if not os.path.exists(self.path):
            return []
        return [f.replace(".json", "") for f in os.listdir(self.path) if f.endswith(".json")]

    def delete(self, key: str) -> None:
        filepath = os.path.join(self.path, f"{key}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
