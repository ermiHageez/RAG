# eTech Marketing & Sales Agent — Setup & Run Guide

> Local multi-agent system with Ollama, LangGraph, MCP, FAISS, N8N

---

## 1. Environment Setup

```bash
python --version              # Must be 3.11+
uv sync                       # Installs from pyproject.toml/uv.lock
```

Dependencies managed via `uv` (no pip). Key packages:
- `langgraph`, `langchain-ollama`, `langchain-community`
- `faiss-cpu`, `langchain-text-splitters`
- `fastapi`, `uvicorn`, `pydantic`
- `httpx`, `beautifulsoup4`, `lxml`

---

## 2. Configure `.env`

Copy `.env.example` to `.env` (minimal — Ollama needs no key):

| Variable | Required | Description |
|----------|----------|-------------|
| `OLLAMA_BASE_URL` | No | Default: `http://localhost:11434` |
| `GOOGLE_API_KEY` | No | Google Custom Search API key |
| `GOOGLE_CSE_ID` | No | Google Custom Search Engine ID |
| `N8N_WEBHOOK_URL` | No | n8n webhook endpoint |
| `PPA_URL` | No | Default: `https://www.ppa.gov.et` |
| `EGP_URL` | No | Default: `https://www.egp.gov.et` |

Without Google keys, search falls back to mock data. Without n8n URL, the n8n hook returns a mock acknowledgment.

---

## 3. Pull Ollama Models (Required)

All inference runs locally through Ollama:

```bash
ollama pull qwen3-embedding:4b   # 2.5 GB — embedding
ollama pull gemma3:4b            # 3.3 GB — router (supervisor)
ollama pull qwen3:8b             # 5.2 GB — reasoning (lead/tender/sales)
ollama pull llama3.1:8b          # 4.9 GB — content drafting

# Verify
ollama list
```

Stop Ollama if already running to free RAM for other models.

---

## 4. Build the FAISS Index

The index is now built with `qwen3-embedding:4b` (1024-dim). If a legacy 384-dim index exists, back it up:

```bash
mv faiss_store faiss_store_backup   # backup legacy (384-dim)
```

Then rebuild:

```bash
uv run python ingest.py
```

This loads files from `data/`, chunks them, generates embeddings via `get_embedding_model()`, and saves to `faiss_store/`. Place source files in `data/`:

```
data/
├── customer_list.xlsx
├── 2022-2023-Annual-Report.pdf
└── comapny profile 2026.pptx
```

---

## 5. Run Tests (No API Keys, No Network)

All tests mock Ollama responses — run offline:

```bash
uv run pytest -v
```

Expected: **52 passed**

| File | Tests | What it covers |
|------|-------|----------------|
| `test_agent_state.py` | 10 | Merge/override reducers, TypedDict defaults |
| `test_content_drafting.py` | 4 | Email validation, personalization scoring |
| `test_e2e_pipeline.py` | 7 | Full graph end-to-end with all mocks |
| `test_graph_execution.py` | 5 | Graph routing, parallel nodes, approval gate |
| `test_lead_node.py` | 4 | Lead deduplication (case-insensitive, empty, etc.) |
| `test_mcp_tools.py` | 10 | Search, tenders, n8n hook with validation |
| `test_rag_retrieval.py` | 2 | Retriever construction, empty index fallback |
| `test_supervisor_routing.py` | 6 | Route parsing (JSON, plain text, empty) |
| `test_tender_node.py` | 2 | Relevance scoring with/without FAISS index |

---

## 6. Validate with Real Models (Phase 4.5)

> **Before production use**, validate against actual Ollama models.

### 6a. Model Layer

```bash
uv run python -c "
from src.agents.llm import (
    get_embedding_model, get_router_llm,
    get_reasoning_llm, get_content_llm
)
print(get_embedding_model().embed_query('construction tender'))
print(get_router_llm().invoke('Classify: find tenders'))
print(get_reasoning_llm().invoke('Analyze this lead'))
print(get_content_llm().invoke('Write a sales email'))
"
```

### 6b. RAG Layer (after rebuilding FAISS index)

```bash
uv run python -c "
from src.rag.vectorstore import FaissVectorStore
store = FaissVectorStore('faiss_store')
store.load()
print(store.query('construction company'))
"
```

### 6c. Full Agent

```bash
uv run python -c "
from src.agents.graph import build_agent
agent = build_agent()
result = agent.invoke({'query': 'Find construction companies interested in industrial generators'})
print('Leads:', len(result['qualified_leads']))
print('Tenders:', len(result['qualified_tenders']))
print('Knowledge chunks:', len(result['knowledge_context']))
print('Sales intel:', result['sales_intelligence'])
print('Email drafted:', result['draft_email']['subject'] if result['draft_email'] else 'No')
print('Approval:', result['approval']['status'])
print('N8N payload keys:', list(result['n8n_payload'].keys()))
"
```

### 6d. MCP Tools

```bash
uv run python -c "
from mcp_server.tools.search import discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline
print('Search:', discover_ethiopian_enterprises('bank'))
print('Tenders:', fetch_active_tenders('Security'))
print('n8n:', trigger_n8n_marketing_pipeline({
    'lead_name': 'TestCorp', 'tender_requirements': 'Security system',
    'validated_email': 'test@corp.et', 'email_body': 'Dear TestCorp, ...'
}))
"
```

---

## 7. Run the API Server

```bash
uv run uvicorn src.api:app --host 0.0.0.0 --port 8001
```

```bash
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"find bank leads and security tenders"}'
```

Expected response shape:

```json
{
  "success": true,
  "result": {
    "query": "...",
    "qualified_leads": [...],
    "qualified_tenders": [...],
    "knowledge_context": [...],
    "sales_intelligence": {...},
    "draft_email": {...},
    "approval": {"status": "pending", ...},
    "n8n_payload": {...}
  }
}
```

---

## 8. Run the MCP Server

```bash
# stdio mode (for IDE/LangGraph integration)
uv run python -m mcp_server.run

# SSE mode (for Docker / network access)
uv run python -m mcp_server.run --sse --port 8000
```

Registered tools:

| Tool | Description |
|------|-------------|
| `discover_ethiopian_enterprises` | Search Ethiopian companies by sector |
| `fetch_active_tenders` | Fetch PPA/eGP procurement tenders |
| `trigger_n8n_marketing_pipeline` | Send email payload to n8n |

---

## 9. Docker Deployment

```bash
# Build the image
docker compose build

# Start all 3 services
docker compose up -d

# Check status
docker compose ps

# Test the agent API
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"find bank leads and security tenders"}'

# View logs
docker compose logs -f

# Stop everything
docker compose down
```

### Docker Services

| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| `mcp-server` | 8000 | SSE transport | MCP tools |
| `agent-api` | 8001 | `POST /agent/run` | LangGraph agent via FastAPI |
| `n8n` | 5678 | `http://localhost:5678` | n8n workflow automation |

---

## 10. n8n Workflow Integration

1. Open `http://localhost:5678` in browser
2. Create account (first-run setup)
3. **Import workflow:** `n8nemail/AI email Automation.json`
4. Set `N8N_WEBHOOK_URL` in `.env` to your n8n webhook URL
5. When the agent runs, `format_n8n_payload` sends email payloads to n8n

The n8n workflow reads customer data from Google Sheets, generates personalized HTML emails via Gemini, and sends via Gmail.

---

## 11. Quick Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|------|
| `uv run pytest` fails | Missing deps or lockfile stale | `uv sync` |
| Ollama connection refused | Ollama not running | `ollama serve` in another terminal |
| Dimension mismatch in FAISS | Index built with old model | `mv faiss_store faiss_store_backup && uv run python ingest.py` |
| All MCP results are mock | Missing Google API keys | Set `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` in `.env` |
| API returns 500, `sentence_transformers` error | Old `src/api.py` still imports legacy | Verify import is `from src.agents.graph import build_agent` |
| Models too slow | Too many loaded at once | Run only needed models, use smaller quantizations |
| Docker healthcheck failing | Service not ready | Wait 30s, check `docker compose logs` |

---

## Architecture Overview

```
User Query
    │
    ▼
Supervisor (gemma3:4b) — routes query to:
    ├── Lead Agent (qwen3:8b) — discovers + deduplicates enterprises
    ├── Tender Agent (qwen3:8b) — fetches + scores tenders
    └── Knowledge Agent (qwen3-embedding:4b) — RAG retrieval
    │
    ▼
Sales Intelligence (qwen3:8b) — cross-references leads/tenders/knowledge
    │
    ▼
Content Agent (llama3.1:8b) — drafts personalized email
    │
    ▼
Approval Gate — checks draft quality
    │
    ▼
N8N Payload → n8n webhook → Google Sheets → Gemini → Gmail
```

All model assignments in `src/agents/llm.py` — the only place model names are configured.

---

## File Reference

```
├── RUN.md                         ← You are here
├── .env.example                   ← Ollama-based config
├── pyproject.toml                 ← uv dependencies
├── ingest.py                      ← FAISS index builder
├── Dockerfile
├── docker-compose.yml
│
├── data/                          ← Source documents
│
├── src/
│   ├── api.py                     ← FastAPI (uses src.agents.graph)
│   ├── search.py                  ← RAG search + summarizer (new)
│   ├── agents/
│   │   ├── llm.py                 ← Model factory (single source of truth)
│   │   ├── state.py               ← AgentState TypedDict
│   │   ├── graph.py               ← LangGraph compiled graph
│   │   ├── supervisor.py          ← Route parser
│   │   ├── lead/                  ← Lead discovery + dedup
│   │   ├── tender/                ← Tender scoring
│   │   ├── knowledge/             ← RAG retrieval
│   │   ├── sales_intelligence/    ← Cross-ref analysis
│   │   ├── content/               ← Email drafting + validation
│   │   └── approval/              ← Approval gate
│   ├── rag/
│   │   ├── embedding.py           ← OllamaEmbeddings pipeline
│   │   ├── vectorstore.py         ← FAISS load/save/query
│   │   ├── retriever.py           ← Two-stage retrieval + rerank
│   │   └── reranker.py            ← Abstract + NoOpReranker
│   └── evaluation/
│       ├── base.py                ← Evaluator ABC
│       ├── rag_eval.py            ← RAG precision evaluator
│       ├── agent_eval.py          ← Routing accuracy evaluator
│       ├── content_eval.py        ← Content quality evaluator
│       └── benchmarks.py          ← Benchmark suite
│
├── mcp_server/
│   ├── run.py                     ← Entry point (stdio/SSE)
│   ├── server.py                  ← FastMCP registrations
│   └── tools/
│       ├── search.py              ← Google CSE + mock fallback
│       ├── tenders.py             ← PPA/eGP scraper + mock data
│       └── n8n_hook.py            ← POST with retry + validation
│
├── tests/
│   ├── conftest.py                ← mock_ollama fixture (384-dim)
│   ├── 16 test files              ← 52 total tests
│
└── faiss_store/                   ← Generated (1024-dim qwen3-embedding)
```
