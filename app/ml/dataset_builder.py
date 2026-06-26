from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import JSONDecodeError
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_INTERACTIONS_PATH = REPO_ROOT / "ml" / "datasets" / "raw_interactions.jsonl"
PROCESSED_TRAINING_PATH = REPO_ROOT / "ml" / "datasets" / "processed_training.jsonl"
QUARANTINE_DIR = REPO_ROOT / "ml" / "datasets" / "quarantine"
QUALITY_REPORT_PATH = REPO_ROOT / "ml" / "datasets" / "quality_report.jsonl"

BATCH_SIZE = 100
QUALITY_WORKERS = 2


class DatasetBuilder:
    def __init__(
        self,
        raw_path: Path | str = RAW_INTERACTIONS_PATH,
        processed_path: Path | str = PROCESSED_TRAINING_PATH,
        min_chars: int = 4,
    ):
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)
        self.min_chars = min_chars

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

    @staticmethod
    def quality_check(record: dict) -> tuple[bool, list[str]]:
        issues: list[str] = []
        query = record.get("query", "") or record.get("input", "")
        response = record.get("response", "") or record.get("output", "")
        q_text = DatasetBuilder._coerce_text(query)
        r_text = DatasetBuilder._coerce_text(response)
        if len(q_text) < 4:
            issues.append("query_too_short")
        if len(r_text) < 4:
            issues.append("response_too_short")
        templates = [
            "i cannot answer",
            "i cannot provide",
            "i don't have access",
            "unable to process",
        ]
        if any(t in r_text.lower() for t in templates):
            issues.append("template_response")
        import re
        query_words = set(re.sub(r'[^\w\s]', '', q_text.lower()).split())
        response_words = set(re.sub(r'[^\w\s]', '', r_text.lower()).split())
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "can", "could",
                      "shall", "should", "may", "might", "in", "on", "at", "by", "with", "to",
                      "for", "of", "and", "or", "not", "no", "this", "that", "these", "those",
                      "i", "you", "he", "she", "it", "we", "they", "what", "who", "which", "how"}
        content_words = query_words - stop_words
        overlap = (content_words) & (response_words - stop_words)
        if len(content_words) >= 5 and len(overlap) == 0:
            issues.append("response_unrelated_to_query")
        return len(issues) == 0, issues

    def _to_chat_record(self, record: dict[str, Any]) -> dict[str, Any] | None:
        query_source = record.get("query")
        if not query_source:
            query_source = record.get("input")
        response_source = record.get("response")
        if response_source is None:
            response_source = record.get("output")
        query = self._coerce_text(query_source)
        response = self._coerce_text(response_source)
        if len(query) < self.min_chars or len(response) < self.min_chars:
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
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

        records: list[dict] = []
        with self.raw_path.open("r", encoding="utf-8") as source:
            for line in source:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    record = json.loads(stripped)
                except JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    records.append(record)

        kept = 0
        quality_results: list[dict] = []
        quarantine_records: list[dict] = []

        for record in records:
            passed, issues = self.quality_check(record)
            chat_record = self._to_chat_record(record) if passed else None
            quality_results.append({
                "query": self._coerce_text(record.get("query") or record.get("input", "")),
                "passed": passed,
                "issues": issues,
            })
            if chat_record and passed:
                kept += 1
            elif not passed:
                quarantine_records.append({
                    "record": record,
                    "issues": issues,
                })

        with self.processed_path.open("w", encoding="utf-8") as target:
            for record in records:
                chat_record = self._to_chat_record(record)
                if chat_record:
                    target.write(json.dumps(chat_record, ensure_ascii=False, separators=(",", ":")) + "\n")

        self._write_quality_report(quality_results, records)
        self._write_quarantine(quarantine_records)

        logger.info(
            "Processed training dataset: %s -> %s (%s records)",
            self.raw_path,
            self.processed_path,
            kept,
        )
        return kept

    def _write_quality_report(self, quality_results: list[dict], records: list[dict]) -> None:
        QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        passed_count = sum(1 for q in quality_results if q["passed"])
        with QUALITY_REPORT_PATH.open("w", encoding="utf-8") as f:
            for qr in quality_results:
                f.write(json.dumps(qr, ensure_ascii=False, separators=(",", ":")) + "\n")
        logger.info(
            "Quality report: %d/%d passed, written to %s",
            passed_count,
            len(quality_results),
            QUALITY_REPORT_PATH,
        )

    def _write_quarantine(self, quarantine_records: list[dict]) -> None:
        if not quarantine_records:
            return
        q_path = QUARANTINE_DIR / "quarantine.jsonl"
        with q_path.open("w", encoding="utf-8") as f:
            for item in quarantine_records:
                f.write(json.dumps(item, ensure_ascii=False, separators=(",", ":"), default=str) + "\n")
        logger.info("Quarantined %d records to %s", len(quarantine_records), q_path)

    @staticmethod
    def get_quality_summary() -> dict[str, Any]:
        if not QUALITY_REPORT_PATH.exists():
            return {"total": 0, "passed": 0, "failed": 0, "issues": {}}
        total = 0
        passed = 0
        issue_counts: dict[str, int] = {}
        with QUALITY_REPORT_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entry = json.loads(stripped)
                    total += 1
                    if entry.get("passed"):
                        passed += 1
                    for issue in entry.get("issues", []):
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1
                except Exception:
                    pass
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total, 3) if total else 0.0,
            "issue_breakdown": issue_counts,
        }


def build() -> int:
    builder = DatasetBuilder()
    return builder.build()


def main() -> None:
    count = build()
    print(f"Processed {count} records")
    summary = DatasetBuilder.get_quality_summary()
    print(f"Quality summary: {summary}")


if __name__ == "__main__":
    main()
