# eTech Marketing & Sales Agent — Setup & Run Guide

> Full project: **11/11 sprints complete** 🟢

---

## 1. Environment Setup

```bash
python --version              # Must be 3.11+
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest             # dev dependency for tests
```

---

## 2. Configure `.env`

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | **Yes** | Get from https://console.groq.com |
| `GOOGLE_API_KEY` | No | Google Custom Search API key |
| `GOOGLE_CSE_ID` | No | Google Custom Search Engine ID |
| `N8N_WEBHOOK_URL` | No | n8n webhook endpoint |
| `PPA_URL` | No | Default: `https://www.ppa.gov.et` |
| `EGP_URL` | No | Default: `https://www.egp.gov.et` |

Without Google keys, search falls back to mock data. Without n8n URL, the n8n hook returns a mock acknowledgment.

---

## 3. Prepare Data

Place your source files in `data/`:

```
data/
├── customer_list.xlsx           # 105 Ethiopian customer records
├── 2022-2023-Annual-Report.pdf  # eTech annual magazine (scanned)
└── comapny profile 2026.pptx    # eTech company profile (scanned)
```

**Delete stale FAISS index before first run:**

```bash
rm -rf faiss_store/
```

---

## 4. Build the FAISS Index

```bash
python main.py
```

This loads all files from `data/`, chunks them, generates embeddings via `all-MiniLM-L6-v2`, and saves to `faiss_store/`.

**Notes:**
- First run downloads the SentenceTransformer model (~90MB) — takes a minute
- Scanned PDF/PPTX fall back to easyocr — **very slow** on weak PCs. For testing, keep only `customer_list.xlsx` in `data/`
- If OCR hangs or crashes, remove the PDF/PPTX and re-run

---

## 5. Run Tests

### 5a. Test MCP Tools (no LLM, no API keys needed)

```bash
python -c "
from mcp_server.tools.search import discover_ethiopian_enterprises
from mcp_server.tools.tenders import fetch_active_tenders
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline

print('=== Search ===')
print(discover_ethiopian_enterprises('bank'))

print('=== Tenders ===')
print(fetch_active_tenders('Security'))

print('=== n8n Hook ===')
print(trigger_n8n_marketing_pipeline({
    'lead_name': 'TestCorp',
    'tender_requirements': 'Security system installation',
    'validated_email': 'test@corp.et',
    'email_body': 'Dear TestCorp, ...'
}))
"
```

### 5b. Test the Full Agent (needs FAISS + GROQ_API_KEY)

```bash
python -c "
from src.agent.graph import build_agent
agent = build_agent()
result = agent.invoke({'query': 'find bank leads and security tenders'})
print('Leads found:     ', len(result['found_leads']))
print('Tenders found:   ', len(result['active_tender_listings']))
print('Sales intel items:', len(result['sales_intel']))
print('Email drafts:    ', len(result['email_drafts']))
print('n8n batch size:  ', result['n8n_payload']['total'])
print()
print('--- Sales Report ---')
print(result['sales_report'])
"
```

### 5c. Test Individual Nodes

```bash
# Tender identification
python -c "
from src.agent.nodes.tender_identification import identify_tenders
from src.agent.state import AgentState
state = AgentState(query='', rag_context=[], found_leads=[],
    active_tender_listings=[], sales_intel=[], sales_report=None,
    email_drafts=[], n8n_payload=None)
result = identify_tenders(state)
print('Tenders:', len(result['active_tender_listings']))
for t in result['active_tender_listings']:
    print(f'  [{t[\"relevance_score\"]}] {t[\"title\"]}')
"

# Lead discovery
python -c "
from src.agent.nodes.lead_discovery import discover_leads
from src.agent.state import AgentState
state = AgentState(query='', rag_context=[], found_leads=[],
    active_tender_listings=[], sales_intel=[], sales_report=None,
    email_drafts=[], n8n_payload=None)
result = discover_leads(state)
print('Leads:', len(result['found_leads']))
for l in result['found_leads']:
    print(f'  {l[\"name\"]} ({l[\"sector\"]})')
"
```

### 5d. Run the Pytest Suite

```bash
pytest tests/ -v
```

All tests mock external dependencies — **no API keys or network needed**. Expected:

```
tests/test_agent_state.py ......                                       [ 15%]
tests/test_tender_node.py ...                                         [ 23%]
tests/test_lead_node.py ....                                          [ 33%]
tests/test_content_drafting.py ......                                 [ 48%]
tests/test_mcp_tools.py .........                                     [ 71%]
tests/test_e2e_pipeline.py ...........                                [100%]

11 passed
```

---

## 6. Run the MCP Server

```bash
# stdio mode (for IDE/LangGraph integration)
python -m mcp_server.run

# SSE mode (for Docker / network access)
python -m mcp_server.run --sse --port 8000
```

Registered tools:
| Tool | Description |
|------|-------------|
| `discover_ethiopian_enterprises` | Search Ethiopian companies by sector |
| `fetch_active_tenders` | Fetch PPA/eGP procurement tenders |
| `trigger_n8n_marketing_pipeline` | Send email payload to n8n |

---

## 7. Docker Deployment

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

Volumes persist FAISS index (`faiss_data`) and n8n data (`n8n_data`).

---

## 8. n8n Workflow Integration

1. Open `http://localhost:5678` in browser
2. Create account (first-run setup)
3. **Import workflow:** `n8nemail/AI email Automation.json`
4. Set `N8N_WEBHOOK_URL` in `.env` to your n8n webhook URL
5. When the agent runs, `format_n8n_payload` sends email payloads to n8n

The n8n workflow reads customer data from Google Sheets, generates personalized HTML emails via Gemini, and sends via Gmail.

---

## 9. Quick Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `sentence-transformers` slow/hangs | First-run model download | Wait ~1 minute |
| OCR too slow / crashes | Scanned PDF/PPTX on weak PC | Remove them, keep only XLSX |
| `faiss_store/` has stale data | Index built with different files | `rm -rf faiss_store/` then `python main.py` |
| All MCP results are mock | Missing API keys | Set `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` in `.env` |
| `pytest` not found | pytest not installed | `pip install pytest` |
| Docker healthcheck failing | Service not ready | Wait 30s, check `docker compose logs` |
| LangGraph import error | Missing langchain packages | `pip install langgraph langchain-groq langchain-core` |
| `n8n_payload` is `None` | No email drafts generated | Check GROQ_API_KEY is set and FAISS has data |

---

## File Reference

```
├── RUN.md                         ← You are here
├── .env.example                   ← Template for secrets
├── requirements.txt               ← Python dependencies
├── Dockerfile                     ← Multi-stage build
├── docker-compose.yml             ← 3-service orchestration
├── entrypoint.sh                  ← Container startup
├── .dockerignore                  ← Build exclusions
├── main.py                        ← Index builder script
│
├── data/                          ← Your source documents
│   ├── customer_list.xlsx
│   ├── 2022-2023-Annual-Report.pdf
│   └── comapny profile 2026.pptx
│
├── src/
│   ├── api.py                     ← FastAPI HTTP wrapper
│   ├── data_loader.py             ← Document loader (XLSX/PDF/PPTX)
│   ├── vectorstore.py             ← FAISS index
│   ├── embedding.py               ← SentenceTransformer pipeline
│   ├── search.py                  ← RAG search + summarizer
│   ├── ocr_loader.py              ← OCR fallback for scanned docs
│   └── agent/
│       ├── state.py               ← AgentState TypedDict
│       ├── graph.py               ← LangGraph compiled graph
│       ├── store.py               ← Singleton vectorstore
│       └── nodes/
│           ├── base.py            ← retrieve_context + format_n8n_payload
│           ├── tender_identification.py
│           ├── lead_discovery.py
│           ├── sales_intel.py     ← Sprint 4
│           └── content_drafting.py ← Sprint 4
│
├── mcp_server/
│   ├── run.py                     ← Entry point (stdio/SSE)
│   ├── server.py                  ← FastMCP tool registrations
│   └── tools/
│       ├── search.py              ← Google CSE + mock fallback
│       ├── tenders.py             ← PPA/eGP scraper + mock data
│       └── n8n_hook.py            ← POST with retry + validation
│
├── tests/
│   ├── conftest.py                ← Mock FAISS + fixtures
│   ├── test_agent_state.py        ← Reducer unit tests
│   ├── test_tender_node.py        ← Tender identification tests
│   ├── test_lead_node.py          ← Lead dedup tests
│   ├── test_content_drafting.py   ← Email validation + scoring
│   ├── test_mcp_tools.py          ← All 3 MCP tool tests
│   └── test_e2e_pipeline.py       ← 11 full pipeline scenarios
│
├── n8nemail/
│   └── AI email Automation.json   ← Importable n8n workflow
│
└── faiss_store/                   ← Generated (delete to rebuild)
```
