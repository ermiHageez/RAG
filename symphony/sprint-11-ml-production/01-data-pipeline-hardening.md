# Sprint 11 — ML Production: Data Pipeline Hardening

## Goal
Harden the dataset collection pipeline with schema validation, PII detection, duplicate prevention, and data quality checks so the training data is clean, safe, and reliable.

## Steps

### 1.1 Add Pydantic Schema Validation to `record_training_event`

**File:** `app/ml/training_sink.py`

- Define a `TrainingEvent` Pydantic model:
  - `event_type: str` (e.g., `"mcp.search"`, `"rag.chat"`, `"agent.run"`)
  - `input: dict`
  - `output: Any`
  - `source: str`
  - `metadata: dict = {}`
  - `timestamp: datetime = Field(default_factory=datetime.utcnow)`
  - `session_id: str | None = None`
- Replace the bare `**kwargs` signature with the typed model
- Validate inside `_worker_loop` before writing; reject malformed records with a logged warning

### 1.2 Upgrade PII / Sensitive-Key Redaction

**File:** `app/ml/training_sink.py`

- Replace the hardcoded `_SENSITIVE_KEYS` set with:
  - Regex-based patterns for Ethiopian phone numbers (`+251\d{9}`, `09\d{8}`), email addresses, credit cards, SSN-like patterns
  - A configurable blocklist loaded from `settings.py` or env var `SENSITIVE_PATTERNS`
  - Entropy-based high-entropy string detection (passwords, API keys)
- Add a `_redact_value()` function that replaces matched patterns with `"[REDACTED]"` instead of skipping the whole record

### 1.3 Add Duplicate Detection

**File:** `app/ml/training_sink.py`

- Before writing a record, compute a hash of `(event_type, input, output, source)` using `hashlib.sha256`
- Maintain a bounded LRU set of recent hashes (last 10,000 records) in memory
- If a duplicate is detected, increment a counter and skip the write (do not log as error — duplicates are normal for retries)
- Periodically (every 500 records) scan the JSONL file on disk to rebuild the LRU set on restart

### 1.4 Add Input Size Limits & Quotas

**File:** `app/ml/training_sink.py`

- Reject records where `json.dumps(input)` exceeds 50 KB (prevents context-dump abuse)
- Reject records where `output` string exceeds 100 KB
- Add a configurable per-session rate limit: max 100 records / minute per `session_id`
- Log a warning when limits are exceeded but do not raise exceptions to callers

### 1.5 Add Data Quality Hooks

**File:** `app/ml/dataset_builder.py`

- Add a `quality_check(record: dict) -> tuple[bool, list[str]]` function that:
  - Checks minimum field length (already exists: 4 chars) — keep but make configurable
  - Checks language consistency (both query and response in same language via `langdetect`)
  - Checks response relevance (response contains at least some words from query)
  - Flags empty or templated responses (e.g., "I cannot answer that")
- Results are written to a `quality_report.jsonl` alongside the processed dataset
- Records that fail quality checks are placed in a `quarantine/` subdirectory instead of being dropped

### 1.6 Add Dataset Archival & Rotation

**File:** `app/ml/training_sink.py` + new script `app/ml/archive.py`

- When `raw_interactions.jsonl` exceeds 50 MB, auto-rotate:
  - Rename to `raw_interactions-{YYYY-MM-DD}.jsonl.gz` (gzip compress)
  - Start a fresh `raw_interactions.jsonl`
  - Keep last 30 rotated files; delete older ones
- Add a new script `archive.py` that can be run manually or via cron
- Store archive path in `settings.py` with env var override `TRAINING_DATA_ARCHIVE_DIR`

## Acceptance Criteria
- [ ] Every call to `record_training_event()` validates input against a Pydantic schema
- [ ] PII patterns (Ethiopian phones, emails, high-entropy strings) are redacted, not just blocked by key name
- [ ] Duplicate records are silently skipped (tracked via counter, not error log)
- [ ] Records exceeding size limits are rejected with a logged warning
- [ ] Built dataset has a `quality_report.jsonl` alongside it
- [ ] Raw dataset auto-rotates at 50 MB
