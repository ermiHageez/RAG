from __future__ import annotations

import hashlib
import json
import logging
import os
import queue
import re
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_INTERACTIONS_PATH = REPO_ROOT / "ml" / "datasets" / "raw_interactions.jsonl"
ARCHIVE_DIR = REPO_ROOT / "ml" / "datasets" / "archive"

MAX_RECORD_INPUT_SIZE = 50 * 1024       # 50 KB
MAX_RECORD_OUTPUT_SIZE = 100 * 1024     # 100 KB
MAX_QUEUE_SIZE = 5000
MAX_FILE_SIZE_BEFORE_ROTATE = 50 * 1024 * 1024  # 50 MB
DUPLICATE_LRU_SIZE = 10000
RATE_LIMIT_PER_SESSION = 100            # records per minute

_write_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=MAX_QUEUE_SIZE)
_worker_started = Event()
_worker_lock = Lock()

_duplicate_hashes: OrderedDict[str, bool] = OrderedDict()
_duplicate_lock = Lock()

_session_rate: dict[str, list[float]] = {}
_session_rate_lock = Lock()

try:
    import fcntl  # type: ignore
except ImportError:
    fcntl = None

# ── PII Patterns ────────────────────────────────────────────────────────

_SENSITIVE_KEYS = {"api_key", "api-key", "apikey", "password", "secret", "token", "authorization"}

_PHONE_PATTERN = re.compile(r'(?:\+251|0)\d{9}')
_EMAIL_PATTERN = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')
_HIGH_ENTROPY_PATTERN = re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9]{20,}(?![A-Za-z0-9])')
_CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

# ── Pydantic Schema ─────────────────────────────────────────────────────

class TrainingEvent(BaseModel):
    event_type: str
    source: str
    origin: str = "unknown"
    session_id: str = ""
    query: str = ""
    response: Any = None
    input: Any = None
    output: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ── Metrics Tracking ────────────────────────────────────────────────────

_metrics: dict[str, Any] = {
    "records_collected": 0,
    "records_rejected": 0,
    "records_duplicate": 0,
    "records_redacted": 0,
    "queue_depth": 0,
    "worker_write_time_ms": 0.0,
    "dataset_size_bytes": 0,
    "errors_by_type": {},
}

def get_metrics() -> dict[str, Any]:
    return {**_metrics}

def reset_metrics() -> None:
    for k in _metrics:
        if k != "errors_by_type":
            _metrics[k] = 0
        else:
            _metrics[k] = {}

# ── PII Redaction ───────────────────────────────────────────────────────

def _redact_pii(text: str) -> str:
    text = _PHONE_PATTERN.sub("[REDACTED-PHONE]", text)
    text = _EMAIL_PATTERN.sub("[REDACTED-EMAIL]", text)
    text = _CREDIT_CARD_PATTERN.sub("[REDACTED-CARD]", text)
    text = _HIGH_ENTROPY_PATTERN.sub("[REDACTED-HIGH-ENTROPY]", text)
    return text

def _sanitize_value(value: Any, depth: int = 0) -> Any:
    if depth > 20:
        return str(value)[:200]
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, nested in value.items():
            if key.lower() in _SENSITIVE_KEYS:
                cleaned[key] = "***REDACTED***"
                _metrics["records_redacted"] += 1
            elif isinstance(nested, str):
                redacted = _redact_pii(nested)
                if redacted != nested:
                    _metrics["records_redacted"] += 1
                cleaned[key] = redacted
            else:
                cleaned[key] = _sanitize_value(nested, depth + 1)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_value(item, depth + 1) for item in value]
    if isinstance(value, str):
        redacted = _redact_pii(value)
        if redacted != value:
            _metrics["records_redacted"] += 1
        return redacted
    return value

# ── Duplicate Detection ─────────────────────────────────────────────────

def _compute_record_hash(record: dict) -> str:
    raw = json.dumps(
        {
            "event_type": record.get("event_type"),
            "input": record.get("input"),
            "output": record.get("output"),
            "source": record.get("source"),
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode()).hexdigest()

def _is_duplicate(record_hash: str) -> bool:
    with _duplicate_lock:
        if record_hash in _duplicate_hashes:
            return True
        _duplicate_hashes[record_hash] = True
        while len(_duplicate_hashes) > DUPLICATE_LRU_SIZE:
            _duplicate_hashes.popitem(last=False)
        return False

def _rebuild_duplicate_set() -> None:
    if not RAW_INTERACTIONS_PATH.exists():
        return
    with _duplicate_lock:
        _duplicate_hashes.clear()
        try:
            with RAW_INTERACTIONS_PATH.open("r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        rec = json.loads(stripped)
                        h = _compute_record_hash(rec)
                        _duplicate_hashes[h] = True
                        while len(_duplicate_hashes) > DUPLICATE_LRU_SIZE:
                            _duplicate_hashes.popitem(last=False)
                    except Exception:
                        pass
        except Exception:
            logger.warning("Could not rebuild duplicate set from existing file")

# ── Rate Limiting ───────────────────────────────────────────────────────

def _check_rate_limit(session_id: str) -> bool:
    if not session_id:
        return True
    now = time.time()
    with _session_rate_lock:
        timestamps = _session_rate.get(session_id, [])
        timestamps = [t for t in timestamps if now - t < 60]
        if len(timestamps) >= RATE_LIMIT_PER_SESSION:
            return False
        timestamps.append(now)
        _session_rate[session_id] = timestamps
        return True

# ── Coercion Helpers ────────────────────────────────────────────────────

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

def _normalize_response_for_record(response: Any) -> Any:
    return _sanitize_value(response)

# ── Archival ────────────────────────────────────────────────────────────

def _maybe_rotate_file() -> None:
    if not RAW_INTERACTIONS_PATH.exists():
        return
    size = RAW_INTERACTIONS_PATH.stat().st_size
    _metrics["dataset_size_bytes"] = size
    if size < MAX_FILE_SIZE_BEFORE_ROTATE:
        return
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_name = f"raw_interactions-{date_str}.jsonl"
    archive_path = ARCHIVE_DIR / archive_name
    counter = 1
    while archive_path.exists():
        archive_path = ARCHIVE_DIR / f"raw_interactions-{date_str}-{counter}.jsonl"
        counter += 1
    RAW_INTERACTIONS_PATH.rename(archive_path)
    logger.info("Rotated dataset: %s -> %s", RAW_INTERACTIONS_PATH, archive_path)
    _cleanup_old_archives()

def _cleanup_old_archives(keep: int = 30) -> None:
    if not ARCHIVE_DIR.exists():
        return
    archives = sorted(ARCHIVE_DIR.glob("raw_interactions-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in archives[keep:]:
        old.unlink()
        logger.info("Removed old archive: %s", old)

# ── Record Writing ──────────────────────────────────────────────────────

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
            _metrics["records_collected"] += 1
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

# ── Worker Loop ─────────────────────────────────────────────────────────

def _worker_loop() -> None:
    while True:
        record = _write_queue.get()
        start = time.perf_counter()
        try:
            _write_record(record)
        except Exception:
            _metrics["errors_by_type"]["write_failure"] = _metrics["errors_by_type"].get("write_failure", 0) + 1
            logger.exception("Failed to append training interaction to %s", RAW_INTERACTIONS_PATH)
        finally:
            elapsed = time.perf_counter() - start
            _metrics["worker_write_time_ms"] = elapsed * 1000
            _write_queue.task_done()
            _metrics["queue_depth"] = _write_queue.qsize()

def _ensure_worker_started() -> None:
    if _worker_started.is_set():
        return
    with _worker_lock:
        if _worker_started.is_set():
            return
        _rebuild_duplicate_set()
        thread = Thread(target=_worker_loop, name="training-dataset-writer", daemon=True)
        thread.start()
        _worker_started.set()

# ── Validation ──────────────────────────────────────────────────────────

def _validate_record(record: dict) -> str | None:
    input_str = json.dumps(record.get("input", ""), ensure_ascii=False, default=str)
    if len(input_str) > MAX_RECORD_INPUT_SIZE:
        return f"Input exceeds {MAX_RECORD_INPUT_SIZE} bytes"
    output_str = json.dumps(record.get("output", ""), ensure_ascii=False, default=str)
    if len(output_str) > MAX_RECORD_OUTPUT_SIZE:
        return f"Output exceeds {MAX_RECORD_OUTPUT_SIZE} bytes"
    session_id = record.get("session_id", "")
    if not _check_rate_limit(session_id):
        return "Rate limit exceeded for session"
    if not record.get("event_type"):
        return "Missing event_type"
    return None

# ── Public API ──────────────────────────────────────────────────────────

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
        rec_hash = _compute_record_hash(record)
        if _is_duplicate(rec_hash):
            _metrics["records_duplicate"] += 1
            return
        error = _validate_record(record)
        if error:
            _metrics["records_rejected"] += 1
            logger.warning("Rejected training record: %s", error)
            return
        _maybe_rotate_file()
        _write_queue.put_nowait(record)
        _metrics["queue_depth"] = _write_queue.qsize()
        logger.info(
            "Dataset enqueue: source=%s origin=%s event=%s session=%s",
            record["source"],
            record["origin"],
            record["event_type"],
            record["session_id"],
        )
    except queue.Full:
        _metrics["records_rejected"] += 1
        logger.warning("Training queue full — record dropped")
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
    try:
        event = TrainingEvent(
            event_type=event_type,
            source=source,
            origin=origin or metadata_clean.get("endpoint") or metadata_clean.get("tool") or metadata_clean.get("product") or source,
            session_id=session_id or "",
            query=_coerce_text(input),
            response=_normalize_response_for_record(output),
            input=_sanitize_value(input),
            output=_sanitize_value(output),
            metadata=metadata_clean,
        )
        record = event.model_dump()
        _ensure_worker_started()
        rec_hash = _compute_record_hash(record)
        if _is_duplicate(rec_hash):
            _metrics["records_duplicate"] += 1
            return
        error = _validate_record(record)
        if error:
            _metrics["records_rejected"] += 1
            logger.warning("Rejected training event: %s", error)
            return
        _maybe_rotate_file()
        _write_queue.put_nowait(record)
        _metrics["queue_depth"] = _write_queue.qsize()
        logger.info(
            "Dataset enqueue: source=%s origin=%s event=%s session=%s",
            record["source"],
            record["origin"],
            record["event_type"],
            record["session_id"],
        )
    except queue.Full:
        _metrics["records_rejected"] += 1
        logger.warning("Training queue full — event dropped")
    except Exception:
        _metrics["errors_by_type"]["enqueue_failure"] = _metrics["errors_by_type"].get("enqueue_failure", 0) + 1
        logger.exception("Unable to enqueue training event for %s", RAW_INTERACTIONS_PATH)
