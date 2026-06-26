# Sprint 11 — ML Production: Testing & Quality Assurance

## Goal
Add integration tests, data quality validations, and wire the existing evaluation framework into the pipeline so every model update is validated before deployment.

## Steps

### 5.1 Add Integration Tests for the ML Pipeline

**File:** `tests/test_ml_integration.py` (new)

- Test `training_sink.py` end-to-end with a real temp file:
  - Write 10 records → verify they exist in JSONL
  - Verify PII redaction (phone number in input → redacted in output)
  - Verify duplicate detection (same record twice → only one written)
  - Verify queue backpressure (rapid enqueue → graceful drop)
- Test `dataset_builder.py` end-to-end:
  - Create a temp `raw_interactions.jsonl` with 5 records
  - Run `build()` → verify `processed_training.jsonl` has correct chat format
  - Test quality check filtering (record with 2-char response → quarantined)
- Test `archive.py` (if implemented):
  - Write enough records to trigger rotation → verify archive exists and new file is empty

### 5.2 Add Embedding & Vector Store Tests

**File:** `tests/test_rag_embedding.py` and `tests/test_rag_vectorstore.py`

- `test_rag_embedding.py`:
  - Test `EmbeddingPipeline.embed_query("test")` returns a float32 array of expected dimension (768 for nomic-embed-text)
  - Test `embed_documents()` returns correct batch shape
  - Test LRU cache hits and misses
- `test_rag_vectorstore.py`:
  - Test `FaissVectorStore.build_from_documents()` with 5 sample documents
  - Test `query()` returns correct number of results
  - Test `save()` + `load()` round-trip preserves metadata
  - Test HNSW index creation with custom `ef_construction` and `ef_search` params

### 5.3 Add Data Loader Tests

**File:** `tests/test_data_loader.py`

- Test loading a real `.txt` file from a `tests/fixtures/` directory
- Test loading a real `.pdf` file (create a minimal 2-page PDF)
- Test loading a real `.csv` file
- Test loading a real `.json` file
- Test fallback paths (e.g., OCR path for PDF returns same structure as text path)
- Test error handling (malformed file → graceful error message, not crash)

### 5.4 Wire Evaluation Framework into Training Pipeline

**File:** `src/evaluation/benchmarks.py` + `app/ml/pipeline.py`

- The existing `BenchmarkSuite` already has `RAGPrecisionEvaluator`, `ContentQualityEvaluator`, `RoutingAccuracyEvaluator` — but they are never called
- Create a concrete benchmark dataset in `tests/fixtures/eval_queries.jsonl`:
  ```jsonl
  {"query": "Who are the leads in the finance sector?", "expected_routing": "lead_agent", "expected_sources": ["..."]}
  ```
- Add a `run_eval_suite(model_tag: str) -> EvalReport` function that:
  - Loads the eval queries
  - Runs each through the pipeline with the specified model
  - Compares routing decisions, retrieval quality, and content quality against expected values
  - Returns a scored report
- Wire into `pipeline.py` (step 3.6) so evaluation runs after every fine-tune and before model promotion

### 5.5 Add Coverage Tooling

**File:** `pyproject.toml`

- Add `pytest-cov` to dev dependencies
- Create a `.coveragerc` config:
  ```
  [run]
  source = app/ml, src/rag
  omit = */tests/*
  
  [report]
  fail_under = 60
  show_missing = true
  ```
- Add a coverage script in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  addopts = "--cov=app/ml --cov=src/rag --cov-report=term-missing --cov-report=html:coverage_report"
  ```
- Run `pytest` with coverage as part of the CI pipeline

### 5.6 Add Data Quality Monitoring Dashboard

**File:** `ui/src/components/DataQualityDashboard.tsx` (new)

- Sidebar nav item: "Data Quality" under "System"
- Shows:
  - Total records collected vs rejected vs quarantined (line chart over 7 days)
  - Quality score trend (line chart)
  - Recent quarantine entries (table with reason)
  - PII redaction stats (count of redacted fields by pattern type)
- Fetches from `GET /metrics` and `GET /quality/report`

### 5.7 Add Quality Report API Endpoint

**File:** `src/api.py`

- Add `GET /quality/report` that reads the latest `quality_report.jsonl` and returns aggregated stats
- Add `GET /quality/quarantine` that returns quarantine records
- Auth-guarded with the same session-based approach as other endpoints

## Acceptance Criteria
- [ ] Integration tests pass for training_sink, dataset_builder, and archive
- [ ] Embedding and vector store tests verify correctness and caching behavior
- [ ] Data loader tests cover all 7 file formats with real fixture files
- [ ] Evaluation suite runs against benchmark queries and produces a scored report
- [ ] Code coverage is at least 60% for `app/ml/` and `src/rag/`
- [ ] UI has a Data Quality dashboard showing live pipeline health
- [ ] `GET /quality/report` returns aggregated quality metrics
