# ML Pipeline — Complete Guide

## Overview

The ML pipeline is a **factory assembly line** with 5 stages:

```
Data Collection → Processing → Quality Check → Training → Deployment
```

Every user interaction with the chatbot or MCP tools is automatically collected, cleaned, and prepared for fine-tuning the AI model.

---

## Stage 1: Data Collection

**File:** `app/ml/training_sink.py`

**What it does:** Every time a user chats with the AI or runs an MCP tool (search, tenders, directory), the interaction is automatically saved to `ml/datasets/raw_interactions.jsonl`.

### How to see it working

```bash
# After using the chat, check what was collected:
wc -l ml/datasets/raw_interactions.jsonl
head -n 1 ml/datasets/raw_interactions.jsonl | python -m json.tool
```

### Key concepts

- **Async worker** — writes happen in a background thread so the API never waits
- **PII redaction** — phone numbers (`+251...`), emails, credit cards are auto-redacted
- **Deduplication** — identical records are silently skipped using SHA256 hashes
- **Archival** — when the file hits 50MB, it auto-rotates to `archive/raw_interactions-2026-06-24.jsonl`
- **Rate limiting** — max 100 records per minute per session
- **Validation** — records over 50KB input / 100KB output are rejected

### Two ways to save data

```python
# 1. From chatbot interactions (called automatically)
from app.ml.training_sink import append_to_training_dataset
append_to_training_dataset("session-123", "What is eTech?", {"answer": "ERP company"})

# 2. From tool calls (also automatic)
from app.ml.training_sink import record_training_event
record_training_event("mcp.search", input={"query": "bank"}, output=[...], source="mcp")
```

### Record format

Each record looks like:

```json
{
  "event_type": "mcp.search",
  "source": "mcp",
  "origin": "discover_ethiopian_enterprises",
  "session_id": "session-123",
  "query": "bank",
  "response": [{"name": "Commercial Bank of Ethiopia", ...}],
  "input": {...},
  "output": {...},
  "metadata": {"tool": "discover_ethiopian_enterprises"},
  "timestamp": "2026-06-24T12:00:00Z"
}
```

### PII Redaction

The following patterns are automatically redacted:

| Pattern | Example | Replaced With |
|---------|---------|---------------|
| Ethiopian phone numbers | `+251911234567`, `0911234567` | `[REDACTED-PHONE]` |
| Email addresses | `user@example.com` | `[REDACTED-EMAIL]` |
| Credit card numbers | `1234 5678 9012 3456` | `[REDACTED-CARD]` |
| High-entropy strings | `ghp_xxxxxxxxxxxxxxxxxxxx` | `[REDACTED-HIGH-ENTROPY]` |
| Sensitive keys | `api_key`, `password`, `secret` | `***REDACTED***` |

---

## Stage 2: Processing

**File:** `app/ml/dataset_builder.py`

**What it does:** Converts the raw interactions into a clean **chat-format** dataset suitable for fine-tuning an LLM.

### How to run it

```bash
python -m app.ml.dataset_builder
```

### Or let it run automatically

The scheduler checks every hour if new data exists and runs the build automatically:

```python
from app.ml.scheduler import start_scheduler
start_scheduler(interval=3600)  # runs every hour
```

Or from cron:

```bash
0 * * * * cd /home/ermi/Desktop/RGA/RAG && python -m app.ml.dataset_builder
```

### What happens during processing

1. Reads `raw_interactions.jsonl` line by line
2. Runs **quality checks** on each record
3. **Good records** → written to `processed_training.jsonl`
4. **Bad records** → moved to `quarantine/quarantine.jsonl`
5. A `quality_report.jsonl` is generated with stats

### Before → After conversion

```json
// Raw (before):
{"query": "What stock is low?", "response": {"answer": "Review SKU A"}}

// Processed (after):
{"messages": [
  {"role": "user", "content": "What stock is low?"},
  {"role": "assistant", "content": "Review SKU A"}
]}
```

This chat format is what **Ollama** and **Llama-Factory** expect for fine-tuning.

### Quality Checks

| Check | Description | Trigger |
|-------|-------------|---------|
| `query_too_short` | Query has fewer than 4 characters | Rejected |
| `response_too_short` | Response has fewer than 4 characters | Rejected |
| `template_response` | Response contains "I cannot answer", etc. | Quarantined |
| `response_unrelated_to_query` | Response shares zero content words with query (only triggered for 5+ significant query words) | Quarantined |

---

## Stage 3: Monitoring & Metrics

**File:** `app/ml/metrics.py`

**Live visibility into the pipeline's health.**

### Check it in real-time

```bash
# Pipeline metrics
curl http://localhost:8001/metrics | python -m json.tool

# Deep health check (Ollama, FAISS, dataset)
curl http://localhost:8001/health/deep | python -m json.tool

# Quality report
curl http://localhost:8001/quality/report | python -m json.tool

# Quarantine records
curl http://localhost:8001/quality/quarantine | python -m json.tool

# Prometheus format
curl http://localhost:8001/metrics/prometheus
```

### Available metrics

| Metric | Description |
|--------|-------------|
| `records_collected` | Total records written to JSONL |
| `records_rejected` | Records rejected by validation |
| `records_duplicate` | Duplicate records skipped |
| `records_redacted` | Records containing PII that was redacted |
| `queue_depth` | Current size of the async write queue |
| `worker_write_time_ms` | File write latency |
| `dataset_size_bytes` | Current JSONL file size |
| `latency_p50/p95/p99_ms` | Write latency percentiles |
| `errors_by_type` | Counter per exception type |
| `embedding_query_count` | Total embedding queries |
| `llm_call_count` | Total LLM calls |
| `llm_fallback_count` | Fallback to Groq count |

### Alerting

If `ALERT_WEBHOOK_URL` env var is set (Slack-compatible webhook), alerts fire when:

- Queue depth exceeds 1000 items
- Dataset build fails
- Pipeline completes successfully
- Health check detects any component as unhealthy

Example alert payload:

```json
{"text": "[ML Pipeline] ERROR: Dataset build failed: File not found", "channel": "#ml-alerts"}
```

---

## Stage 4: Model Registry

**File:** `app/ml/registry/model_registry.py`

**Tracks every model version so you can always roll back.**

### Usage

```python
from app.ml.registry import model_registry

# Register a new version
model_registry.register(
    tag="etech-agent:v2",
    base_model="gemma2:2b",
    training_data="processed_training-2026-06-24.jsonl",
    record_count=1500
)

# Promote to active
model_registry.promote("etech-agent:v2")

# Rollback if something breaks
model_registry.rollback()

# List all versions
model_registry.list_versions()

# Get currently active version
model_registry.get_active()
```

### Registry file format

Stored in `ml/registry/model_registry.json`:

```json
{
  "versions": [
    {
      "tag": "etech-agent:v1",
      "base_model": "gemma2:2b",
      "training_data": "processed_training-2026-06-23.jsonl",
      "training_date": "2026-06-23T10:00:00Z",
      "record_count": 500,
      "eval_score": 0.82,
      "status": "archived"
    },
    {
      "tag": "etech-agent:v2",
      "base_model": "gemma2:2b",
      "training_data": "processed_training-2026-06-24.jsonl",
      "training_date": "2026-06-24T10:00:00Z",
      "record_count": 1500,
      "eval_score": 0.91,
      "status": "active"
    }
  ],
  "active": "etech-agent:v2"
}
```

---

## Stage 5: Full Automation Pipeline

**File:** `app/ml/pipeline.py`

**The end-to-end script** — run it whenever you want the full cycle:

```bash
python -m app.ml.pipeline
```

### Step-by-step execution

1. **Build processed dataset** from raw data
2. **Run quality checks** — if pass rate < 50%, abort
3. **Register** the new dataset version in model registry
4. **Run evaluation benchmarks** against the current model
5. **Promote** the new version
6. **Send notification** via alert webhook

### Build the custom Ollama model

```bash
# Basic build
bash app/ml/registry/build_model.sh

# Build with training data injected
bash app/ml/registry/build_model.sh \
  etech-agent:v2 \
  ml/datasets/processed_training-2026-06-24.jsonl
```

The Modelfile in `app/ml/registry/Modelfile` controls the base model, temperature, and system prompt.

---

## Performance Upgrades

### FAISS HNSW Index

**File:** `src/rag/vectorstore.py`

- **Old:** `IndexFlatL2` (brute force, O(n) search)
- **New:** `IndexHNSWFlat` (hierarchical navigable small world, O(log n) search)
- **Result:** 5-10x faster at 10K+ vectors

Configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HNSW_EF_CONSTRUCTION` | `200` | Build quality (higher = better recall, slower build) |
| `HNSW_EF_SEARCH` | `50` | Search depth (higher = better recall, slower search) |
| `VECTOR_CACHE_TTL` | `60` | Cache TTL in seconds for repeated queries |

### Caching

| Cache | Location | Effect |
|-------|----------|--------|
| Embedding query | `src/rag/embedding.py` | Repeated queries hit LRU cache (1024 entries) |
| Vector search | `src/rag/vectorstore.py` | Same query from different users cached for 60s |

### Async Offloading

Embedding and LLM calls now run in `ThreadPoolExecutor` — they don't block the web server event loop:

```python
# Old (blocking):
result = llm.invoke(prompt)

# New (non-blocking):
result = await llm.async_invoke(prompt)
```

---

## Testing

### Run all tests

```bash
python -m pytest tests/ -v
```

### New tests added

| Test file | What it covers |
|-----------|----------------|
| `tests/test_ml_integration.py` | PII redaction, duplicate detection, metrics, quality checks |
| `tests/test_rag_vectorstore.py` | HNSW roundtrip, caching, empty index handling |
| `tests/test_rag_embedding.py` | Chunking, LRU cache, async embedding, document cleaning |
| `tests/test_data_loader.py` | TXT, CSV, JSON loading, empty directories |
| `tests/fixtures/eval_queries.jsonl` | 4 benchmark queries for routing evaluation |

---

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `python -m app.ml.dataset_builder` | Process raw interactions into training format |
| `python -m app.ml.pipeline` | Run full pipeline (build → eval → promote) |
| `bash app/ml/registry/build_model.sh` | Build custom Ollama model |
| `curl http://localhost:8001/metrics` | View pipeline metrics |
| `curl http://localhost:8001/health/deep` | Deep health check |
| `python -m pytest tests/` | Run all tests |

### Directory Structure

```
ml/
├── ML_PIPELINE.md                  ← This file
├── datasets/
│   ├── raw_interactions.jsonl      ← Live data collected from users
│   ├── processed_training.jsonl    ← Cleaned training data
│   ├── quality_report.jsonl        ← Quality check results
│   ├── quarantine/                 ← Failed quality checks
│   │   └── quarantine.jsonl
│   ├── archive/                    ← Rotated historical data
│   │   └── raw_interactions-2026-06-24.jsonl
│   └── .scheduler_state.json       ← Tracks last build state
└── registry/
    ├── Modelfile                   ← Ollama model configuration
    ├── build_model.sh              ← Model build script
    ├── model_registry.py           ← Version tracking
    └── model_registry.jsonl        ← Version data

app/ml/
├── training_sink.py                ← Data collection (auto-runs)
├── dataset_builder.py              ← Raw → processed converter
├── scheduler.py                    ← Periodic builder
├── pipeline.py                     ← End-to-end automation
├── metrics.py                      ← Metrics counters
└── alerts.py                       ← Webhook alerting
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATASET_BUILD_INTERVAL` | `3600` | Scheduler interval in seconds |
| `ALERT_WEBHOOK_URL` | (empty) | Slack webhook for alerts |
| `HNSW_EF_CONSTRUCTION` | `200` | FAISS HNSW build quality |
| `HNSW_EF_SEARCH` | `50` | FAISS HNSW search depth |
| `VECTOR_CACHE_TTL` | `60` | Vector query cache TTL (seconds) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |

---

## Verification Checklist

```bash
# 1. Check data is being collected
wc -l ml/datasets/raw_interactions.jsonl

# 2. Build the processed dataset
python -m app.ml.dataset_builder

# 3. Check quality
python -c "
from app.ml.dataset_builder import DatasetBuilder
print(DatasetBuilder.get_quality_summary())
"

# 4. Check metrics endpoint
curl http://localhost:8001/metrics

# 5. Build the custom model
bash app/ml/registry/build_model.sh

# 6. Register and promote
python -c "
from app.ml.registry import model_registry
model_registry.register('etech-agent:v1', 'gemma2:2b', record_count=1500)
model_registry.promote('etech-agent:v1')
print(model_registry.get_active())
"

# 7. Run the full pipeline
python -m app.ml.pipeline

# 8. Run all tests
python -m pytest tests/ -v
```

---

**Key insight:** The pipeline is designed to be **fully automatic** once set up. Data gets collected as users interact with the chat. The scheduler processes it hourly. When enough data accumulates, the pipeline builds a new model. Just run `python -m app.ml.pipeline` (or let cron do it) to trigger the full cycle.
