# eTech RAG + MCP + Agent — Setup & Test Summary

## Fixes Applied

### 1. RAG Speed Fix — `src/embedding.py`
Removed `self.documents = load_all_documents("data")` from `EmbeddingPipeline.__init__`.
- **Before**: Every RAG/agent init triggered OCR on scanned PDF (15MB) + PPTX (23MB) — took minutes or hung.
- **After**: Init is ~5s (model load only). The `manifest.needs_rebuild()` check in `RAGSearch` runs before any document loading, so the index is only rebuilt when files change.

### 2. Testability Fix — 3 node files
Changed `from src.agent.store import get_vectorstore` → `import src.agent.store` in:
- `src/agent/nodes/lead_discovery.py`
- `src/agent/nodes/tender_identification.py`
- `src/agent/nodes/content_drafting.py`

This allows pytest's `monkeypatch.setattr` to properly mock the vectorstore in tests.

### 3. Docker Dependency Fix — `requirements.txt`
Added 3 missing packages:
- `mcp` — MCP Python SDK (needed by `mcp_server/server.py`)
- `pandas` — needed by `src/data_loader.py` for Excel reading
- `openpyxl` — needed by `pd.read_excel(engine="openpyxl")`

---

## Test Results

| Service | Test | Result | Notes |
|---------|------|--------|-------|
| **pytest** | `pytest tests/ -v` | **44/44 passed** in 19.7s | Was timing out before fixes |
| **MCP Tools** | `discover_ethiopian_enterprises('bank')` | ✅ 2 mock leads | Mock fallback (no Google API key) |
| **MCP Tools** | `fetch_active_tenders('Security')` | ✅ 1 mock tender | SSL cert fail → mock fallback |
| **MCP Tools** | `trigger_n8n_marketing_pipeline(...)` | ✅ mock ack | Mock (no N8N_WEBHOOK_URL) |
| **RAG Search** | `RAGSearch.search_and_summarize("What does eTech do?")` | ✅ 3 sources (PPTX + PDF p7, p12), accurate Groq summary | ~93s first call (model init), subseq. faster |
| **Agent Pipeline** | `agent.invoke("find bank leads and security tenders")` | ✅ 5 leads, 5 tenders, 10 intel items, 5 email drafts, n8n batch=5 | End-to-end success |
| **FastAPI** | `GET /health` | ✅ `{"status":"ok"}` | — |
| **FastAPI** | `POST /agent/run` | ✅ `success: True`, 5 leads, 5 tenders | — |
| **Docker build** | `docker compose build` | ❌ Network timeout (torch ~2GB download) | Fix applied, needs retry on stable network |

---

## Server Spec Recommendations (Multi-Agent Ready)

### Minimum Viable
| Component | Spec | Why |
|-----------|------|-----|
| **CPU** | 4+ cores x86_64 | SentenceTransformer, FAISS, OCR inference |
| **RAM** | 16 GB | Python + torch + sentence-transformers + FAISS + Docker + n8n |
| **Storage** | 50 GB SSD | Docker images (~5GB), FAISS index, n8n data, source docs |
| **GPU** | Not required | CPU works (~50ms/embedding, ~1s/query) |

### Recommended (Multi-Agent Scale)
| Component | Spec | Why |
|-----------|------|-----|
| **CPU** | 8+ cores (AMD EPYC / Intel Xeon) | Multiple concurrent agents each need CPU for embeddings |
| **RAM** | 32 GB | 8GB base + ~4GB per concurrent agent process |
| **GPU** | NVIDIA T4 / RTX 3060+ (16GB VRAM) | 10-50x faster embeddings + OCR; enables local LLM (Llama 3 via Ollama) |
| **Storage** | 200 GB NVMe SSD | Multiple FAISS indexes, n8n DB, model cache, containers |
| **Network** | 100 Mbps+ stable | Groq API, n8n webhooks, Google CSE, PPA/eGP scraping |

### Why These Specs for Multi-Agent
- Each LangGraph agent runs 5 nodes (retrieve → discover → tender → intel → draft), each doing embedding queries into FAISS (149 chunks currently).
- Agents share the vectorstore singleton (one model load per process), but each query still needs an embedding encode.
- With 10+ concurrent agents on CPU, embedding becomes the bottleneck. A GPU eliminates this.
- To run a local LLM (replacing Groq): need 16GB+ VRAM for Llama 3 70B via vLLM/Ollama.

---

## What's Left

1. **Rebuild Docker images** — `docker compose build` needs a stable internet connection (torch is ~2GB). Try:
   ```bash
   docker compose build --no-cache
   ```
   Or set longer pip timeout:
   ```bash
   docker compose build --build-arg PIP_DEFAULT_TIMEOUT=300
   ```

2. **Verify Docker deployment**:
   ```bash
   docker compose up -d
   curl http://localhost:8001/health
   curl -X POST http://localhost:8001/agent/run \
     -H "Content-Type: application/json" \
     -d '{"query":"find bank leads and security tenders"}'
   ```

3. **Set `.env` values**:
   - `GROQ_API_KEY` — already set
   - `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` — for real company search (instead of mock)
   - `N8N_WEBHOOK_URL` — for real n8n integration
   - `PPA_URL` / `EGP_URL` — for live tender scraping
