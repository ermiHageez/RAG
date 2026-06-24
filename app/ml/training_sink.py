from __future__ import annotations

import json
import logging
import os
import queue
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_INTERACTIONS_PATH = REPO_ROOT / "ml" / "datasets" / "raw_interactions.jsonl"

_write_queue: queue.Queue[dict[str, Any]] = queue.Queue()
_worker_started = Event()
_worker_lock = Lock()

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore


_SENSITIVE_KEYS = {"api_key", "api-key", "apikey", "password", "secret", "token", "authorization"}


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("query", "message", "content", "response", "text", "answer", "output", "reply", "body"):
            nested = value.get(key)
            if nested is not None:
                text = _coerce_text(nested)
                if text:
                    return text
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    if isinstance(value, list):
        parts = [_coerce_text(item) for item in value]
        joined = " ".join(part for part in parts if part)
        return joined.strip() or json.dumps(value, ensure_ascii=False, default=str)
    return str(value).strip()


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, nested in value.items():
            if key.lower() in _SENSITIVE_KEYS:
                cleaned[key] = "***REDACTED***"
            else:
                cleaned[key] = _sanitize_value(nested)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _normalize_response_for_record(response: Any) -> Any:
    return _sanitize_value(response)


def _write_record(record: dict[str, Any]) -> None:
    RAW_INTERACTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, separators=(",", ":"), default=str)
    with RAW_INTERACTIONS_PATH.open("a", encoding="utf-8") as handle:
        if fcntl is not None:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except OSError:
                logger.warning("Could not acquire file lock for %s", RAW_INTERACTIONS_PATH)
        try:
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            logger.info(
                "Dataset updated: source=%s origin=%s event=%s session=%s query=%s path=%s",
                record.get("source", "unknown"),
                record.get("origin", record.get("metadata", {}).get("endpoint", "")),
                record.get("event_type", "interaction"),
                record.get("session_id", ""),
                str(record.get("query", ""))[:120],
                RAW_INTERACTIONS_PATH,
            )
        finally:
            if fcntl is not None:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    logger.warning("Could not release file lock for %s", RAW_INTERACTIONS_PATH)


def _worker_loop() -> None:
    while True:
        record = _write_queue.get()
        try:
            _write_record(record)
        except Exception:
            logger.exception("Failed to append training interaction to %s", RAW_INTERACTIONS_PATH)
        finally:
            _write_queue.task_done()


def _ensure_worker_started() -> None:
    if _worker_started.is_set():
        return
    with _worker_lock:
        if _worker_started.is_set():
            return
        thread = Thread(target=_worker_loop, name="training-dataset-writer", daemon=True)
        thread.start()
        _worker_started.set()


def append_to_training_dataset(session_id: str, query: str, response: Any) -> None:
    record = {
        "event_type": "interaction",
        "source": "memory",
        "origin": "src.memory.conversation_memory",
        "session_id": session_id,
        "query": query,
        "response": _normalize_response_for_record(response),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    record["input"] = record["query"]
    record["output"] = record["response"]
    try:
        _ensure_worker_started()
        _write_queue.put_nowait(record)
        logger.info(
            "Dataset enqueue: source=%s origin=%s event=%s session=%s",
            record["source"],
            record["origin"],
            record["event_type"],
            record["session_id"],
        )
    except Exception:
        logger.exception("Unable to enqueue training interaction for %s", RAW_INTERACTIONS_PATH)


def record_training_event(
    event_type: str,
    *,
    session_id: str | None = None,
    input: Any = None,
    output: Any = None,
    source: str = "api",
    metadata: dict[str, Any] | None = None,
    origin: str | None = None,
) -> None:
    metadata_clean = _sanitize_value(metadata or {})
    record = {
        "event_type": event_type,
        "source": source,
        "origin": origin or metadata_clean.get("endpoint") or metadata_clean.get("tool") or metadata_clean.get("product") or source,
        "session_id": session_id or "",
        "query": _coerce_text(input),
        "response": _normalize_response_for_record(output),
        "input": _sanitize_value(input),
        "output": _sanitize_value(output),
        "metadata": metadata_clean,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _ensure_worker_started()
        _write_queue.put_nowait(record)
        logger.info(
            "Dataset enqueue: source=%s origin=%s event=%s session=%s",
            record["source"],
            record["origin"],
            record["event_type"],
            record["session_id"],
        )
    except Exception:
        logger.exception("Unable to enqueue training event for %s", RAW_INTERACTIONS_PATH)
