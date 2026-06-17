from abc import ABC, abstractmethod
from typing import Any, Optional


class Evaluator(ABC):
    @abstractmethod
    def evaluate(
        self, input_data: Any, output_data: Any, expected: Optional[Any] = None
    ) -> dict: ...

    @abstractmethod
    def name(self) -> str: ...
