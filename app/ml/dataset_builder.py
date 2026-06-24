from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_INTERACTIONS_PATH = REPO_ROOT / "ml" / "datasets" / "raw_interactions.jsonl"
PROCESSED_TRAINING_PATH = REPO_ROOT / "ml" / "datasets" / "processed_training.jsonl"


class DatasetBuilder:
    def __init__(
        self,
        raw_path: Path | str = RAW_INTERACTIONS_PATH,
        processed_path: Path | str = PROCESSED_TRAINING_PATH,
    ) -> None:
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)

    @staticmethod
    def _coerce_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("content", "response", "text", "answer", "message", "output", "reply"):
                nested = value.get(key)
                if nested is not None:
                    text = DatasetBuilder._coerce_text(nested)
                    if text:
                        return text
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        if isinstance(value, list):
            parts = [DatasetBuilder._coerce_text(item) for item in value]
            joined = " ".join(part for part in parts if part)
            return joined.strip() or json.dumps(value, ensure_ascii=False)
        return str(value).strip()

    def _to_chat_record(self, record: dict[str, Any]) -> dict[str, Any] | None:
        query_source = record.get("query")
        if not query_source:
            query_source = record.get("input")
        response_source = record.get("response")
        if response_source is None:
            response_source = record.get("output")

        query = self._coerce_text(query_source)
        response = self._coerce_text(response_source)
        if len(query) < 4 or len(response) < 4:
            return None
        return {
            "messages": [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response},
            ]
        }

    def build(self) -> int:
        if not self.raw_path.exists():
            raise FileNotFoundError(f"Raw interaction dataset not found: {self.raw_path}")

        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        kept = 0
        with self.raw_path.open("r", encoding="utf-8") as source, self.processed_path.open("w", encoding="utf-8") as target:
            for line in source:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    record = json.loads(stripped)
                except JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                chat_record = self._to_chat_record(record)
                if chat_record is None:
                    continue
                target.write(json.dumps(chat_record, ensure_ascii=False, separators=(",", ":")) + "\n")
                kept += 1
        logger.info(
            "Processed training dataset: %s -> %s (%s records)",
            self.raw_path,
            self.processed_path,
            kept,
        )
        return kept


def main() -> None:
    builder = DatasetBuilder()
    count = builder.build()
    print(f"Processed {count} records into {builder.processed_path}")


if __name__ == "__main__":
    main()
