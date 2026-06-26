# Sprint 11 — ML Production: Performance & Scalability

## Goal
Upgrade the vector store, offload blocking I/O, and prepare the pipeline to handle 10x the current data volume without degrading response times.

## Steps

### 4.1 Upgrade FAISS Index from Flat to HNSW

**File:** `src/rag/vectorstore.py`

- Replace `faiss.IndexFlatL2` with `faiss.IndexHNSWFlat(d, 32)` (HNSW with 32 neighbors)
  - HNSW provides O(log n) search vs O(n) for Flat
  - Add `hnsw_ef_construction` and `hnsw_ef_search` parameters (configurable, defaults: `ef_construction=200`, `ef_search=50`)
- Keep backward compatibility: if an existing Flat index is loaded, rebuild it as HNSW on first query
- Add a `index_type` field to the manifest so we know what type was saved
- Benchmark: query latency should drop from ~5ms (Flat at 10K vectors) to <1ms at 100K vectors

### 4.2 Add Async Offloading for Embeddings

**File:** `src/rag/embedding.py` + `src/api.py`

- Move embedding calls to a thread pool executor:
  ```python
  from concurrent.futures import ThreadPoolExecutor
  _embed_executor = ThreadPoolExecutor(max_workers=2)
  ```
- Expose async wrappers:
  - `async_embed_documents(docs)` → `await loop.run_in_executor(_embed_executor, self.embed_documents, docs)`
  - `async_embed_query(query)` → same pattern
- Update `POST /rag/chat`, `POST /rag/query`, and `POST /mcp/search` to use the async versions
- This prevents the embedding step from blocking other requests on the FastAPI event loop

### 4.3 Add Async Offloading for LLM Calls

**File:** `src/agents/llm.py`

- Same thread pool pattern for LLM `invoke()` calls:
  ```python
  _llm_executor = ThreadPoolExecutor(max_workers=1)
  ```
- Wrap `_FallbackLLM.invoke()` to run in the executor
- This allows concurrent request handling while one request is waiting for an LLM response

### 4.4 Add Batch Processing for Dataset Builder

**File:** `app/ml/dataset_builder.py`

- Process records in batches of 100 instead of line-by-line:
  - Read 100 lines into memory, process the batch, write 100 lines
  - Reduces I/O overhead by 100x
- Use `concurrent.futures` to parallelize quality checks across 2-4 worker threads
- Add a progress bar via `tqdm` (optional, auto-detects terminal)

### 4.5 Add Caching for Embeddings

**File:** `src/rag/embedding.py`

- Add an in-memory LRU cache for `embed_query()` results:
  ```python
  from functools import lru_cache
  
  @lru_cache(maxsize=1024)
  def _cached_embed(text: str) -> np.ndarray:
      return self._model.embed_query(text)
  ```
- This dramatically speeds up repeated queries (e.g., same question asked by different users)
- Add a `clear_cache()` method for when the embedding model is updated

### 4.6 Add Read-Through Cache for Vector Search

**File:** `src/rag/vectorstore.py`

- Add a `@lru_cache` on `query()` keyed by `(query_text, top_k)`
  - Cache TTL: 60 seconds (configurable via `VECTOR_CACHE_TTL` env var)
  - Cache is invalidated when `rebuild()` is called
- This prevents redundant vector searches when multiple users ask the same question in quick succession

### 4.7 Set Bounded Queue Size

**File:** `app/ml/training_sink.py`

- Change `queue.Queue()` to `queue.Queue(maxsize=5000)`
- When the queue is full, `record_training_event()` blocks for up to 1 second, then drops the record with a warning
- Monitor `queue_depth` metric to tune the limit

## Acceptance Criteria
- [ ] FAISS index uses HNSW and is 5-10x faster than Flat at 10K+ vectors
- [ ] Embedding calls do not block the FastAPI event loop
- [ ] LLM calls do not block the FastAPI event loop
- [ ] Dataset builder processes records in batches with parallel quality checks
- [ ] Repeated embedding queries hit the LRU cache (sub-millisecond)
- [ ] Repeated vector searches hit the read-through cache
- [ ] Training queue is bounded at 5000 items and drops gracefully when full
