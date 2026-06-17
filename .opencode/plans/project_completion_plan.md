# eTech Multi-Agent Project — Completion Plan

> Current state: Multi-agent architecture built, Ollama local models ready, needs integration and mock removal
> Last updated: 2026-06-11

---

## Current Project State

### Architecture (Already Built)
```
                        ┌──────────────────┐
                        │   Supervisor      │  gemma3:4b (router)
                        │   Agent           │
                        └────────┬─────────┘
                                 │ route: [lead, tender, knowledge]
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
           ┌────────────┐ ┌──────────┐ ┌──────────────┐
           │ Lead Agent │ │ Tender   │ │ Knowledge    │
           │ (search)   │ │ Agent    │ │ Agent (RAG)  │
           └────────────┘ └──────────┘ └──────────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │ Sales Intelligence     │  qwen3:8b (reasoning)
                    │ Agent                  │
                    └───────────┬────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ Content Agent          │  llama3.1:8b (content)
                    │ (email drafting)       │
                    └───────────┬────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ Approval Agent         │
                    └───────────┬────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ n8n Payload            │
                    └────────────────────────┘
```

### What's Working
| Component | Status | Details |
|-----------|--------|---------|
| `src/agents/llm.py` | ✅ | Uses `ChatOllama` — `qwen3-embedding:4b`, `gemma3:4b`, `qwen3:8b`, `llama3.1:8b` |
| `src/agents/graph.py` | ✅ | Multi-agent LangGraph: supervisor → 3 parallel agents → sales intel → content → approval → n8n |
| `src/agents/supervisor/` | ✅ | Routes queries to lead/tender/knowledge agents via LLM + keyword fallback |
| `src/agents/lead/` | ✅ | Discovers companies via MCP search tool |
| `src/agents/tender/` | ✅ | Fetches + scores tenders via FAISS relevance |
| `src/agents/knowledge/` | ✅ | RAG retrieval with retriever + reranker |
| `src/agents/sales_intelligence/` | ✅ | Cross-references leads + tenders + knowledge, generates summary via qwen3:8b |
| `src/agents/content/` | ✅ | Email drafting via llama3.1:8b with personalization scoring |
| `src/agents/approval/` | ✅ | Confidence gate — flags low-scoring drafts for manual review |
| `src/agents/state.py` | ✅ | AgentState with typed reducers |
| `src/rag/embedding.py` | ✅ | Uses `OllamaEmbeddings(qwen3-embedding:4b)` |
| `src/rag/vectorstore.py` | ✅ | FaissVectorStore with singleton pattern |
| `src/rag/retriever.py` | ✅ | Retriever + Reranker abstraction |
| `src/rag/reranker.py` | ✅ | NoOpReranker (base for future cross-encoder) |
| `src/memory/` | ✅ | JSON-based memory: conversation, lead, tender stores |
| `src/evaluation/` | ✅ | Benchmark suite: RAG precision, routing accuracy, content quality |
| `tests/conftest.py` | ✅ | Mocks `ChatOllama` and `OllamaEmbeddings` for CI |
| `tests/test_graph_execution.py` | ✅ | 5 tests: full graph, leads, tenders, knowledge, approval |
| `tests/test_supervisor_routing.py` | ✅ | 6 tests: route parsing + LLM routing |
| `tests/test_rag_retrieval.py` | ✅ | 2 tests: retriever construction + empty index |
| `api.py` | ✅ | FastAPI: `GET /health`, `POST /agent/run` (uses new `src.agents.graph`) |
| **Ollama models** | ✅ | All 5 models downloaded: `llama3.1:8b`, `qwen3:8b`, `gemma3:4b`, `qwen3-embedding:4b`, `gemma2:2b` |

### What's Broken / Missing
| Issue | Severity | Details |
|-------|----------|---------|
| **FAISS index empty** | 🔴 BLOCKING | `faiss_store/` is empty — must rebuild with `qwen3-embedding:4b` |
| **`main.py` uses old code** | 🟡 MEDIUM | Imports old `src.vectorstore` instead of new `src.rag.vectorstore` |
| **Old `src/agent/` (singular) exists** | 🟢 LOW | Dead code from previous single-agent version |
| **Old `src/embedding.py`, `vectorstore.py`, `data_loader.py`, `search.py`** | 🟢 LOW | Dead code — all replaced by `src/rag/` |
| **Google CSE returns 404** | 🔴 BLOCKING | `cx` value is an OAuth client ID, not a valid CSE ID. Google returns 404. |
| **MCP tools have mock fallbacks** | 🟡 MEDIUM | `search.py` falls to mock, `tenders.py` falls to mock, `n8n_hook.py` mocks |
| **PPA tender scrape fails** | 🟡 MEDIUM | SSL certificate verification error |
| **No models running** | 🟡 MEDIUM | `ollama ps` shows empty — `ollama run <model>` needed before use |
| **`langchain-ollama` might be missing** | 🟡 MEDIUM | `src/agents/llm.py` imports `langchain_ollama` — verify in requirements.txt |

---

## Phase 1: Rebuild FAISS Index with Ollama Embeddings

**Goal**: Build a fresh FAISS vector index using `qwen3-embedding:4b` (Ollama) instead of old `all-MiniLM-L6-v2`.

### Files to Change

#### 1.1 `main.py` — Update imports
```python
# OLD (uses old single-agent modules):
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore

# NEW (uses new multi-agent RAG module):
from src.rag.data_loader import load_all_documents
from src.rag.vectorstore import FaissVectorStore
```

#### 1.2 `requirements.txt` — Verify `langchain-ollama` is present
```text
# Already uses:
# langchain-ollama  ← verify this line exists
```

#### 1.3 Commands to rebuild
```bash
# 1. Start the embedding model
ollama run qwen3-embedding:4b

# 2. Remove old index
rm -rf faiss_store/

# 3. Install deps if missing
uv pip install langchain-ollama

# 4. Rebuild FAISS index (now uses src/rag/* with Ollama)
python main.py
```

### Verification
```bash
python -c "
from src.rag.vectorstore import FaissVectorStore
v = FaissVectorStore('faiss_store')
v.load()
print('Index entries:', v.index.ntotal)
results = v.query('eTech ERP solutions for banks', top_k=3)
print('Query results:', len(results))
for r in results:
    text = r.get('metadata', {}).get('text', '')[:80]
    print(f'  [{r[\"distance\"]:.3f}] {text}...')
"
```

---

## Phase 2: Fix Company Search (Google Custom Search API)

**Problem**: The CSE ID is an OAuth client ID (`*.apps.googleusercontent.com`), not a valid 17‑digit Programmable Search Engine ID. Google returns 404.

**Solution**: Use the proper Google Custom Search JSON API with runtime CSE ID format validation. Strip ads/promotional elements from results.

### Files to Change

#### 2.1 `mcp_server/tools/search.py` — Rewrite with validation + ad stripping
```python
import re
import os
import httpx
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ── Runtime validation ──────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

# Must be a 17-digit hex Programmable Search Engine ID
_CSE_ID_PATTERN = re.compile(r"^[a-f0-9]{17}:")

if GOOGLE_API_KEY and GOOGLE_CSE_ID:
    if not _CSE_ID_PATTERN.match(GOOGLE_CSE_ID):
        raise RuntimeError(
            f"GOOGLE_CSE_ID is invalid: '{GOOGLE_CSE_ID}' looks like an OAuth client ID, "
            "not a 17‑digit Programmable Search Engine ID. "
            "Create one at https://programmablesearchengine.google.com/ and use the cx= value."
        )
elif not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise RuntimeError("GOOGLE_API_KEY and GOOGLE_CSE_ID must be set in .env")


def _organic_search(query: str, num: int = 5) -> List[Dict[str, Any]]:
    """Google Custom Search — returns only organic results (no ads/promotions)."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": num}
    resp = httpx.get(url, params=params, timeout=15.0)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        # ── Strip promotions / ads ──────────────────────────────
        # Google CSE sometimes returns "promotion" items or ads
        kind = item.get("kind", "")
        if kind == "customsearch#promotion":
            continue
        # Skip items that look like ads (no snippet, suspicious title)
        snippet = (item.get("snippet") or "").strip()
        title = (item.get("title") or "").strip()
        if not snippet and not title:
            continue
        # Skip labeled ads
        if item.get("htmlSnippet", "").startswith("<div class=\"ads-ad\""):
            continue

        results.append({
            "name": title,
            "sector": _guess_sector(title, snippet),
            "location": _guess_location(snippet, title),
            "description": snippet,
            "contact": "",
            "link": item.get("link", ""),
        })
    return results


def _guess_location(snippet: str, title: str) -> str:
    text = (snippet + " " + title).lower()
    if any(city in text for city in ["addis ababa", "bahir dar", "mekelle", "dire dawa", "hawassa", "gondar"]):
        return next(city for city in ["Addis Ababa", "Bahir Dar", "Mekelle", "Dire Dawa", "Hawassa", "Gondar"] if city.split()[0].lower() in text)
    return "Ethiopia"


def discover_ethiopian_enterprises(query: str) -> List[Dict[str, Any]]:
    return _organic_search(query)
```

#### 2.2 `requirements.txt` — No new deps needed (httpx already present)
Remove `duckduckgo-search` if previously added:
```text
# REMOVE: duckduckgo-search
```

#### 2.3 `.env` — Fix CSE ID (replace with a real 17‑digit ID)
```env
GOOGLE_API_KEY=AIzaSyDdVzJPhEPLJFEhBLOCZSnLf83DCEqvQ5E
GOOGLE_CSE_ID=YOUR_VALID_17_DIGIT_CX_ID  # Create at https://cse.google.com/cse/
```

### Verification
```bash
python -c "
from mcp_server.tools.search import discover_ethiopian_enterprises
results = discover_ethiopian_enterprises('banking finance Ethiopia')
print('Live results:', len(results))
for r in results:
    print(f'  {r[\"name\"]} | {r[\"sector\"]} | {r[\"location\"]}')
"
```

---

## Phase 3: Remove Mock Fallbacks

### 3.1 `mcp_server/tools/search.py`
- Delete `MOCK_RESPONSES` dict
- Delete `_mock_search()` function
- `discover_ethiopian_enterprises()` always calls `_organic_search()` (no fallback)

### 3.2 `mcp_server/tools/tenders.py`
- Delete `MOCK_TENDERS` list (lines 17-58)
- In `fetch_active_tenders()`: remove the `if not results: use mock data` block (lines 108-116)
- Add alternative scrape target: `EGP_URL` (already configured)
- SSL fix: add `verify=False` or bundle certs, or use `httpx.Client(verify=False)` as temporary workaround

### 3.3 `mcp_server/tools/n8n_hook.py`
- Keep current behavior: when `N8N_WEBHOOK_URL` is not set, return mock ack (this is a valid config state, not mock data)
- No change needed

### 3.4 `src/rag/data_loader.py` — Remove OCR fallback if not needed
- The sample data now uses `sample.txt` (plain text, no OCR)
- If PDF/PPTX are removed from `data/`, OCR code paths won't trigger

---

## Phase 4: Clean Up Dead Code

### 4.1 Files to delete (old single-agent version)
```
src/agent/              # Entire directory — replaced by src/agents/ (multi-agent)
src/embedding.py         # Replaced by src/rag/embedding.py
src/vectorstore.py       # Replaced by src/rag/vectorstore.py
src/data_loader.py       # Replaced by src/rag/data_loader.py
src/search.py            # Replaced by knowledge_agent + retriever
```

### 4.2 Check nothing references old files before deleting
```bash
grep -r "from src.embedding\|from src.vectorstore\|from src.data_loader\|
         from src.search\|from src.agent " src/ tests/ mcp_server/ --include="*.py"
```

### 4.3 Tests that reference old modules
The old `tests/test_e2e_pipeline.py`, `tests/test_content_drafting.py`, `tests/test_lead_node.py`, `tests/test_tender_node.py` may reference old `src.agent.*` modules. Check and either:
- Delete if fully replaced by new tests (`test_graph_execution.py`, `test_supervisor_routing.py`)
- Or update to use new modules

---

## Phase 5: Start Ollama & Test End-to-End

### 5.1 Start all required models
```bash
# Start in background (each takes a few seconds)
ollama run qwen3-embedding:4b &
sleep 2
ollama run gemma3:4b &
sleep 2
ollama run qwen3:8b &
sleep 2
ollama run llama3.1:8b &
sleep 2

# Verify all running
ollama ps
```

### 5.2 Run test suite (mocks Ollama)
```bash
pytest tests/ -v --tb=short
```
Expected: All **13+ tests** pass using mocked `ChatOllama`/`OllamaEmbeddings`.

### 5.3 Run full agent with real Ollama
```bash
python -c "
from src.agents.graph import build_agent
agent = build_agent()
result = agent.invoke({'query': 'find bank leads and security tenders in Ethiopia'})
print('Route:', result.get('route'))
print('Leads:', len(result.get('qualified_leads', [])))
print('Tenders:', len(result.get('qualified_tenders', [])))
print('Knowledge:', len(result.get('knowledge_context', [])))
print('Sales summary:', str(result.get('sales_intelligence', {}).get('summary', ''))[:200])
print('Email subject:', result.get('draft_email', {}).get('subject', ''))
print('Approval:', result.get('requires_human_approval'))
"
```

### 5.4 Start API and test endpoints
```bash
# Terminal 1:
uvicorn src.api:app --host 0.0.0.0 --port 8001

# Terminal 2:
curl -s http://localhost:8001/health
curl -s -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"find bank leads and security tenders"}' | python -m json.tool
```

### 5.5 Start MCP server
```bash
python -m mcp_server.run --sse --port 8000
```

### 5.6 Run evaluation benchmarks
```bash
python -c "
from src.evaluation.benchmarks import BenchmarkSuite
from src.evaluation.rag_eval import RAGPrecisionEvaluator
from src.evaluation.agent_eval import RoutingAccuracyEvaluator
from src.evaluation.content_eval import ContentQualityEvaluator

suite = BenchmarkSuite()
suite.add_evaluator(RAGPrecisionEvaluator())
suite.add_evaluator(RoutingAccuracyEvaluator())
suite.add_evaluator(ContentQualityEvaluator())

results = suite.run([
    {'name': 'eTech_capabilities', 'input': 'What does eTech do?',
     'output': [{'text': 'eTech provides ERP solutions for Ethiopian enterprises'}],
     'expected': None},
])
print(results)
"
```

---

## Phase 6: Docker (Final Step)

### 6.1 Update `requirements.txt` (final version)
```
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-ollama          # Replaces langchain-groq
langgraph
pypdf
sentence-transformers     # Still needed? Check — qwen3-embedding replaces this
faiss-cpu
python-dotenv
tqdm
tiktoken
fastapi
uvicorn
pydantic
mcp
pandas
openpyxl
# duckduckgo-search removed — using Google CSE
httpx
beautifulsoup4
lxml
```

### 6.2 Rebuild Docker
```bash
docker compose build --no-cache
docker compose up -d
curl localhost:8001/health
```

---

## Summary: All Changes by File

| File | Action | Reason |
|------|--------|--------|
| `main.py` | Update imports | Point to `src.rag.*` not old modules |
| `requirements.txt` | Add `langchain-ollama` | Ollama LLM |
| `requirements.txt` | Remove `langchain-groq` | Replaced by `langchain-ollama` |
| `mcp_server/tools/search.py` | Fix Google CSE: validate + strip ads | OAuth client ID was invalid; must use proper 17‑digit CSE ID |
| `mcp_server/tools/search.py` | Delete `MOCK_RESPONSES`, `_mock_search()` | Mock data no longer needed |
| `mcp_server/tools/tenders.py` | Delete `MOCK_TENDERS` | No mock fallback |
| `mcp_server/tools/tenders.py` | Fix SSL for PPA scraping | Add `verify=False` or cert bundle |
| `.env` | Replace CSE ID with valid 17‑digit Programmable Search Engine ID | Current OAuth client ID is invalid; create at https://cse.google.com/cse/ |
| `faiss_store/` | Rebuild | Must use `qwen3-embedding:4b` embeddings |
| `src/agent/` | Delete directory | Dead code, replaced by `src/agents/` |
| `src/embedding.py` | Delete file | Replaced by `src/rag/embedding.py` |
| `src/vectorstore.py` | Delete file | Replaced by `src/rag/vectorstore.py` |
| `src/data_loader.py` | Delete file | Replaced by `src/rag/data_loader.py` |
| `src/search.py` | Delete file | Replaced by knowledge_agent |

---

## Time Estimate

| Phase | Time | Depends On |
|-------|------|------------|
| 1. Rebuild FAISS | 15 min (model pull time) | Ollama running |
| 2. Fix search (Google CSE) | 15 min | — |
| 3. Remove mocks | 20 min | Phase 2 |
| 4. Clean up dead code | 10 min | — |
| 5. Test E2E | 30 min | Phases 1-4 |
| 6. Docker | 30 min | Phases 1-5 |
| **Total** | **~2 hours** | |
