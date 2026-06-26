# Sprint 11 — ML Production: Monitoring & Observability

## Goal
Add metrics, structured logging, health checks, and alerting to the ML pipeline so operators can see what's happening in production and detect issues before users do.

## Steps

### 2.1 Add Metrics Counters

**File:** `app/ml/metrics.py` (new)

- Create a lightweight in-process metrics collector using `collections.Counter` and `time.perf_counter` (no external dependency)
- Track:
  - `records_collected` — total records written to JSONL
  - `records_rejected` — schema/invalid records rejected
  - `records_duplicate` — duplicates skipped
  - `records_redacted` — records containing PII that was redacted
  - `queue_depth` — current size of the async queue
  - `worker_write_time_ms` — histogram of file write latency (p50, p95, p99 stored as floats)
  - `dataset_size_bytes` — current JSONL file size
  - `errors_by_type` — counter per exception type (e.g., `OSError`, `JSONDecodeError`)
- Expose via `get_metrics()` → plain dict, and `reset_metrics()`

### 2.2 Expose Metrics via API Endpoint

**File:** `src/api.py`

- Add `GET /metrics` endpoint that returns `app/ml/metrics.get_metrics()` as JSON
- Add `GET /health/deep` endpoint that:
  - Pings Ollama (`GET /api/tags`) and reports status
  - Checks FAISS index exists and has vectors
  - Checks pgvector connectivity (if configured)
  - Returns a `{"status": "healthy" | "degraded" | "unhealthy", "checks": {...}}` response
  - Sets HTTP status code to 200, 503, or 503 based on status

### 2.3 Add Structured Logging

**File:** `app/ml/training_sink.py` + `app/ml/dataset_builder.py`

- Switch from bare `print()` to a structured logger using `logging.Logger` with JSON formatting
- Add `loguru` or `python-json-logger` to `requirements.txt` (prefer `loguru` for simplicity)
- Each log event includes: `timestamp`, `level`, `module`, `event_type`, `duration_ms`, `record_count`
- Log rotation: 10 MB per file, keep 5 backups → `logs/training_sink.log`

### 2.4 Add Prometheus Endpoint (Optional)

**File:** `app/ml/metrics.py` + `src/api.py`

- If the infrastructure supports Prometheus, add an optional `GET /metrics/prometheus` endpoint
- Use the `/metrics` dict to generate Prometheus text format output
- Guarded by `PROMETHEUS_ENABLED` env var (default `False`)
- Add `prometheus-client` to extras in `pyproject.toml`

### 2.5 Add Health Dashboard to UI

**File:** `ui/src/components/MlHealthDashboard.tsx` (new)

- Add a new nav item "ML Health" in the sidebar under a "System" section
- Shows:
  - Dataset stats (total records, file size, last rotation date)
  - Queue health (depth, processed rate)
  - LLM status (Ollama reachable, model loaded)
  - FAISS index status (vector count, last rebuild)
  - Recent errors (last 20 from the structured log)
- Fetches from `GET /metrics` and `GET /health/deep`
- Auto-refresh every 30 seconds

### 2.6 Add Alert Webhook

**File:** `app/ml/alerts.py` (new)

- Define a `send_alert(message: str, severity: str)` function
- If `ALERT_WEBHOOK_URL` env var is set, POST to it:
  ```json
  {"text": "[ML Pipeline] {severity}: {message}", "channel": "#ml-alerts"}
  ```
- Call from:
  - `training_sink.py` when queue depth exceeds 1000
  - `dataset_builder.py` when build fails
  - `api.py` health check when any component is unhealthy
- Support Slack-compatible webhook format by default; make format configurable

## Acceptance Criteria
- [ ] `GET /metrics` returns counters, timings, and dataset size
- [ ] `GET /health/deep` checks Ollama, FAISS, and pgvector
- [ ] Logs are structured with JSON format and rotated
- [ ] UI has an ML Health dashboard showing live pipeline status
- [ ] Alerts fire to a webhook when critical thresholds are breached
- [ ] All metrics reset on server restart
