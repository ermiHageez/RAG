# eTech Marketing & Sales Agent — Project Status

> Last updated: 2026-06-10

---

## 1. Project Purpose

An AI-powered **marketing & sales agent** for eTech, an Ethiopian technology company. The system automates the end-to-end sales pipeline:

1. **Discover** — Find Ethiopian companies by sector (banking, insurance, logistics, etc.) via Google Custom Search 
2. **Tenders** — Fetch active procurement tenders from Ethiopian PPA/eGP portals
3. **Analyze** — Use RAG (Retrieval-Augmented Generation) over eTech's documents (company profile, annual report, customer list) to score tender relevance and extract context
4. **Draft** — Generate personalized B2B outreach emails using Groq LLM (Llama 3 70B)
5. **Deliver** — Send email payloads to n8n workflow automation for delivery via Gmail

### Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│              FastAPI (port 8001)                 │
│  POST /agent/run   │   GET /health              │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│           LangGraph Agent Pipeline               │
│                                                   │
│  retrieve_context                                 │
│      ├── discover_leads         (MCP: Search)    │
│      └── identify_tenders       (MCP: Tenders)   │
│              │                                    │
│              ▼                                    │
│  build_sales_intel                                 │
│      │                                            │
│      ▼                                            │
│  draft_emails          (Groq LLM + RAG context)   │
│      │                                            │
│      ▼                                            │
│  format_n8n_payload    (MCP: n8n Hook)            │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│   MCP SSE   │  │    n8n       │  │   FAISS      │
│  (port 8000)│  │  (port 5678) │  │  Vector Store│
└─────────────┘  └──────────────┘  └──────────────┘
```

### Services

| Service | Port | Purpose |
|---------|------|---------|
| `mcp-server` | 8000 | MCP tools: search, tenders, n8n (SSE transport) |
| `agent-api` | 8001 | FastAPI wrapper for the LangGraph agent |
| `n8n` | 5678 | Workflow automation (email delivery via Gmail) |

### Agent Graph (LangGraph)

```
START → retrieve_context → discover_leads ──→ check_data ──→ build_sales_intel
                          → identify_tenders ──→                    │
                                                                    ▼
                                                            draft_emails
                                                                    │
                                                                    ▼
                                                          format_n8n_payload → END
```

---

## 2. What's Done ✅

### Core Features (11/11 Sprints)
- **RAG pipeline** — Document loading (PDF/PPTX/XLSX), chunking, FAISS vector store, embedding with `all-MiniLM-L6-v2`
- **RAG search** — `RAGSearch.search_and_summarize()` with Groq LLM summarization
- **MCP tools** — `discover_ethiopian_enterprises`, `fetch_active_tenders`, `trigger_n8n_marketing_pipeline`
- **Agent pipeline** — Full LangGraph graph with 6 nodes: retrieve → discover → tender → intel → draft → n8n
- **Agent state** — TypedDict with custom reducers for merging lists and overriding values
- **Email drafting** — Personalized B2B emails via Groq with validation and scoring
- **Sales intel** — Cross-references leads with tenders, urgency labels (red/amber/green)
- **OCR fallback** — easyocr for scanned PDFs/PPTXs
- **n8n integration** — Payload delivery to n8n webhook with retry logic
- **Test suite** — 44 tests covering all nodes, MCP tools, state management, and e2e pipeline
- **Docker** — Multi-stage build with 3 services

### Bugs Fixed (this session)
| Fix | Files | Issue |
|-----|-------|-------|
| RAG speed | `src/embedding.py` | `load_all_documents("data")` in `__init__` triggered slow OCR on every init |
| Test mocking | 3 node files | `from X import get_vectorstore` prevented monkeypatch from working |
| Missing deps | `requirements.txt` | Added `mcp`, `pandas`, `openpyxl` (missing for Docker) |

### Test Results (44/44 passed)
```
tests/test_agent_state.py .........         (9 tests)  ✅
tests/test_content_drafting.py ......       (6 tests)  ✅
tests/test_e2e_pipeline.py ...........      (11 tests) ✅
tests/test_lead_node.py ....                (4 tests)  ✅
tests/test_mcp_tools.py .........           (9 tests)  ✅
tests/test_tender_node.py ...               (3 tests)  ✅
----------------------------------------
Total: 44 passed in 19.7s
```

---

## 3. What's Left ❌

### High Priority
| Item | Detail | Blocked By |
|------|--------|------------|
| **Docker build** | `docker compose build` fails with network timeout downloading torch (~2GB) | Stable internet connection |
| **Docker deploy** | Build + `docker compose up -d` + verify all 3 services healthy | Docker build |
| **Live MCP tools** | Set `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` in `.env` for real company search | API keys from Tech Lead |
| **Live tenders** | PPA/eGP scraping fails (SSL cert), falls to mock — may need cert bundle or proxy | SSL config or VPN |
| **n8n workflow** | Import `n8nemail/AI email Automation.json` into n8n, set webhook URL | Running n8n instance |

### Medium Priority
| Item | Detail |
|------|--------|
| **Customer list XLSX** | `customer_list.xlsx` (105 Ethiopian customer records) is missing from `data/` — needed for RAG context |
| **FAISS rebuild** | After adding customer list, run `rm -rf faiss_store/ && python main.py` to rebuild index |
| **PDF quality** | Scanned PDF/PPTX OCR is very slow on CPU — consider replacing with text-based versions or pre-processing |
| **Multi-agent** | Current design has one graph. For multi-agent (e.g., per-sector agents), need LangGraph `parallel` branching or separate agent instances per sector |

### Low Priority / Nice-to-Have
| Item | Detail |
|------|--------|
| **GPU acceleration** | SentenceTransformer + OCR 10-50x faster with GPU |
| **Local LLM** | Replace Groq with local Llama 3 via Ollama/vLLM (needs GPU) |
| **Email delivery** | Configure Gmail API in n8n for actual email sending |
| **Monitoring** | Add logging, metrics, and dashboards for agent runs |
| **Auth** | Add API key auth to FastAPI endpoints for production |

---

## 4. Current State of Each File

```
src/
├── api.py                     ✅ FastAPI wrapper (health + /agent/run)
├── data_loader.py             ✅ Loads XLSX/PDF/PPTX/TXT/CSV/DOCX/JSON
├── embedding.py               ✅ Fixed — removed OCR trigger from __init__
├── manifest.py                ✅ Manifests for detecting file changes
├── ocr_loader.py              ✅ OCR fallback for scanned documents
├── search.py                  ✅ RAG search + Groq summarization
├── vectorstore.py             ✅ FAISS index (build, load, query)
├── agent/
│   ├── graph.py               ✅ LangGraph compiled graph (6 nodes)
│   ├── state.py               ✅ AgentState TypedDict with reducers
│   ├── store.py               ✅ Singleton vectorstore accessor
│   └── nodes/
│       ├── base.py            ✅ retrieve_context + format_n8n_payload
│       ├── lead_discovery.py  ✅ Fixed import for testability
│       ├── tender_identification.py  ✅ Fixed import for testability
│       ├── sales_intel.py     ✅ Cross-references leads + tenders
│       └── content_drafting.py ✅ Fixed import, Groq email generation

mcp_server/
├── run.py                     ✅ MCP entry point (stdio / SSE)
├── server.py                  ✅ FastMCP tool registrations
└── tools/
    ├── search.py              ✅ Google CSE + mock fallback
    ├── tenders.py             ✅ PPA/eGP scraper + mock data
    └── n8n_hook.py            ✅ POST with retry + validation

tests/
├── conftest.py                ✅ Mock FAISS + fixtures
├── test_agent_state.py        ✅ 9 tests for reducers
├── test_content_drafting.py   ✅ 6 tests for email logic
├── test_e2e_pipeline.py       ✅ 11 tests for full pipeline
├── test_lead_node.py          ✅ 4 tests for lead dedup
├── test_mcp_tools.py          ✅ 9 tests for all MCP tools
└── test_tender_node.py        ✅ 3 tests for tender scoring

data/                          ❌ Only scanned PDF + PPTX (no customer_list.xlsx)
faiss_store/                   ✅ Built index (149 chunks, 384-d embeddings)
├── faiss.index                ✅ 229 KB FAISS index
├── metadata.pkl               ✅ 97 KB metadata pickle
└── manifest.json              ✅ Tracks files: PDF + PPTX

requirements.txt               ✅ Updated with mcp, pandas, openpyxl
Dockerfile                     ✅ Multi-stage build
docker-compose.yml             ✅ 3 services
entrypoint.sh                  ✅ Container startup
.env                          ⚠️ Has GROQ_API_KEY, missing other keys
```

---

## 5. How to Run

### Locally
```bash
# 1. Setup
python -m venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Build FAISS index
python main.py

# 3. Test MCP tools (no API keys needed)
python -c "
from mcp_server.tools.search import discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline
print('Search:', discover_ethiopian_enterprises('bank'))
print('Tenders:', fetch_active_tenders('Security'))
print('n8n:', trigger_n8n_marketing_pipeline({'lead_name':'Test','tender_requirements':'Test','validated_email':'t@t.et','email_body':'Hi'}))
"

# 4. Run agent (needs GROQ_API_KEY in .env)
python -c "
from src.agent.graph import build_agent
agent = build_agent()
result = agent.invoke({'query': 'find bank leads and security tenders'})
print('Leads:', len(result['found_leads']))
print('Tenders:', len(result['active_tender_listings']))
print('Drafts:', len(result['email_drafts']))
"

# 5. Start API server
uvicorn src.api:app --host 0.0.0.0 --port 8001

# 6. Run tests
pytest tests/ -v
```

### Docker
```bash
docker compose build        # Fails currently — needs stable network
docker compose up -d
curl http://localhost:8001/health
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"find bank leads and security tenders"}'
```

---

## 6. Environment Variables

| Variable | Required | Current | Purpose |
|----------|----------|---------|---------|
| `GROQ_API_KEY` | Yes | ✅ Set | LLM for email drafting + RAG summarization |
| `GOOGLE_API_KEY` | No | ❌ Missing | Google Custom Search for real company discovery |
| `GOOGLE_CSE_ID` | No | ❌ Missing | Google Custom Search Engine ID |
| `N8N_WEBHOOK_URL` | No | ❌ Missing | n8n webhook for email delivery |
| `PPA_URL` | No | Default | Ethiopian Procurement Portal URL |
| `EGP_URL` | No | Default | Ethiopian e-Procurement Portal URL |

---

## 7. Server Specs (for Tech Lead)

### Minimum (single agent, dev/testing)
| Component | Spec |
|-----------|------|
| CPU | 4 cores x86_64 |
| RAM | 16 GB |
| Storage | 50 GB SSD |
| GPU | Not required |
| OS | Ubuntu 22.04+ / Debian 12 |

### Recommended (multi-agent, production)
| Component | Spec | Reason |
|-----------|------|--------|
| CPU | 8+ cores (AMD EPYC / Intel Xeon) | Multiple concurrent agents + embeddings |
| RAM | 32 GB | 8GB base + ~4GB per concurrent agent process |
| GPU | NVIDIA T4 / RTX 3060+ (16GB VRAM) | 10-50x faster embeddings; enables local LLM |
| Storage | 200 GB NVMe SSD | Docker images, FAISS indexes, n8n DB, model cache |
| Network | 100 Mbps+ stable | Groq API, Google CSE, PPA/eGP scraping |
| Docker | 24+ | Required for compose |

The main constraint is **torch + sentence-transformers** — 2GB download + ~4GB RAM at runtime. Without GPU, embedding each query takes ~50ms CPU. With 10 concurrent agents, CPU becomes the bottleneck.
