# Sprint 6.7 — Dependency Cleanup & Testing

> Remove cloud dependencies, add Ollama support, and update the test suite.

---

## Goal

Clean up `requirements.txt` and `pyproject.toml`, install local-only dependencies, and update all tests to mock Ollama instead of Groq.

---

## Dependency Changes

### Remove

| Package | Reason |
|---|---|
| `sentence-transformers` | Replaced by `langchain-ollama` + Ollama server |
| `langchain-groq` | Cloud dependency — no longer used |
| `langchain-openai` | Cloud dependency — no longer used |

### Add

| Package | Reason |
|---|---|
| `langchain-ollama` | Ollama integration for LangChain |
| `langgraph` | Agent orchestration (preserve) |
| `faiss-cpu` | Vector search (preserve) |

### Updated `requirements.txt`

```txt
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-ollama
langgraph

pypdf
pymupdf
faiss-cpu

python-dotenv

tqdm
tiktoken

unstructured
easyocr
PyMuPDF
fastapi
uvicorn
pydantic
mcp
pandas
openpyxl
httpx
beautifulsoup4
lxml
```

### Updated `pyproject.toml` dependencies

```toml
dependencies = [
    "beautifulsoup4>=4.15.0",
    "fastmcp>=3.4.2",
    "httpx>=0.28.1",
    "lxml>=6.1.1",
    "mcp>=1.27.2",
    "openpyxl>=3.1.5",
    "pandas>=3.0.3",
    "requests>=2.34.2",
    "langchain-ollama>=0.3.0",
    "langgraph>=0.5.0",
    "faiss-cpu>=1.10.0",
]

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=0.25.0",
]
```

---

## Test Updates

### Update `tests/conftest.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage


@pytest.fixture(autouse=True)
def mock_ollama():
    """Mock all Ollama LLM calls to avoid requiring local Ollama server."""
    with patch("src.agents.llm.ChatOllama") as mock_chat, \
         patch("src.agents.llm.OllamaEmbeddings") as mock_emb:

        # Mock ChatOllama invoke
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content='{"route": ["knowledge"]}')
        mock_chat.return_value = mock_llm

        # Mock OllamaEmbeddings
        mock_emb_model = MagicMock()
        mock_emb_model.embed_documents.return_value = [[0.1] * 1024]
        mock_emb_model.embed_query.return_value = [0.1] * 1024
        mock_emb.return_value = mock_emb_model

        yield
```

### Update `tests/test_content_drafting.py`

- Replace `@patch("src.agent.nodes.content_drafting.ChatGroq")` with `@patch("src.agents.content.content_agent.get_content_llm")`
- All other test logic preserved

### Update `tests/test_agent_state.py`

- Update imports from `src.agent.state` → `src.agents.state`
- All reducer tests unchanged

### Add New Tests

**Test file: `tests/test_supervisor_routing.py`**

```python
def test_supervisor_routes_to_tender():
    state = {"query": "Find active tenders for security systems"}
    result = supervisor_agent(state)
    assert "tender" in result["route"]

def test_supervisor_routes_to_lead():
    state = {"query": "Find banking leads in Addis"}
    result = supervisor_agent(state)
    assert "lead" in result["route"]

def test_supervisor_routes_to_knowledge():
    state = {"query": "What does eTech do?"}
    result = supervisor_agent(state)
    assert "knowledge" in result["route"]
```

**Test file: `tests/test_graph_execution.py`**

```python
def test_full_graph_runs():
    agent = build_agent()
    result = agent.invoke({"query": "Find ICT tenders"})
    assert "route" in result
    assert "qualified_tenders" in result
    assert "n8n_payload" in result

def test_conditional_skip_lead():
    agent = build_agent()
    result = agent.invoke({"query": "Find tenders only"})
    # Supervisor should route to tender, not lead
    assert "lead" not in result.get("route", [])
```

**Test file: `tests/test_rag_retrieval.py`**

```python
def test_retriever_returns_results():
    store = FaissVectorStore("faiss_store")
    store.load()
    retriever = Retriever(store)
    results = retriever.retrieve("eTech CEO", top_k=5)
    assert len(results) > 0
    assert all("text" in r for r in results)
```

---

## Testing Strategy

| Test Area | File | Priority |
|---|---|---|
| Supervisor routing | `test_supervisor_routing.py` | High |
| Graph execution | `test_graph_execution.py` | High |
| State transitions | `test_agent_state.py` | High |
| RAG retrieval | `test_rag_retrieval.py` | Medium |
| Content drafting | `test_content_drafting.py` | Medium |
| Lead deduplication | `test_lead_node.py` | Medium |
| Tender scoring | `test_tender_node.py` | Medium |
| N8N payload | `test_mcp_tools.py` | Medium |
| End-to-end | `test_e2e_pipeline.py` | High |

---

## Files Changed

| File | Change |
|---|---|
| `requirements.txt` | Remove `sentence-transformers`, `langchain-groq`, `langchain-openai`; add `langchain-ollama` |
| `pyproject.toml` | Same dep changes |
| `tests/conftest.py` | Mock `ChatOllama` + `OllamaEmbeddings` |
| `tests/test_content_drafting.py` | Update mocks to use `get_content_llm` |
| `tests/test_agent_state.py` | Update imports |
| `tests/test_supervisor_routing.py` | **NEW** |
| `tests/test_graph_execution.py` | **NEW** |
| `tests/test_rag_retrieval.py` | **NEW** |
