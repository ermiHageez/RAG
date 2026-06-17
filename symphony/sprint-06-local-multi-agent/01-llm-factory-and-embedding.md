# Sprint 6.1 — LLM Factory & Embedding Migration

> Migrate from cloud-based Groq/SentenceTransformers to a fully local Ollama-powered model factory.

---

## Goal

Eliminate all hardcoded model references across the codebase. Establish a single source of truth for model initialization in `src/agents/llm.py`.

---

## Steps

### 1. Create `src/agents/llm.py`

Centralized model factory with four model tiers:

| Function | Model | Purpose |
|---|---|---|
| `get_embedding_model()` | `qwen3-embedding:4b` | FAISS vector embeddings |
| `get_router_llm()` | `gemma3:4b` | Supervisor routing, lead/tender qualification |
| `get_reasoning_llm()` | `qwen3:8b` | Sales intelligence, analysis |
| `get_content_llm()` | `llama3.1:8b` | Email/content generation |

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings

OLLAMA_BASE_URL = "http://localhost:11434"

def get_embedding_model():
    return OllamaEmbeddings(
        model="qwen3-embedding:4b",
        base_url=OLLAMA_BASE_URL
    )

def get_router_llm():
    return ChatOllama(
        model="gemma3:4b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.1
    )

def get_reasoning_llm():
    return ChatOllama(
        model="qwen3:8b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.2
    )

def get_content_llm():
    return ChatOllama(
        model="llama3.1:8b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.3
    )
```

### 2. Migrate `src/embedding.py`

**Before:**
```python
from sentence_transformers import SentenceTransformer
self.model = SentenceTransformer("all-MiniLM-L6-v2")
```

**After:**
```python
from src.agents.llm import get_embedding_model
self.embeddings = get_embedding_model()
```

Key changes:
- Remove `SentenceTransformer` import entirely
- Replace `self.model.encode(texts)` with `self.embeddings.embed_documents(texts)`
- Handle async vs sync — OllamaEmbeddings.embed_documents returns a list of lists
- Convert to `np.ndarray` for FAISS compatibility

### 3. Migrate `src/vectorstore.py`

- Update `FaissVectorStore.__init__` to use `get_embedding_model()`
- Ensure `embed_chunks()` passes `page_content` properly to `embed_documents()`
- The FAISS index build/search logic stays unchanged

### 4. Migrate `src/agent/store.py`

- The singleton vectorstore loader uses the new embedding model
- No structural changes needed

### 5. Remove cloud dependencies from all node files

- `src/agent/nodes/content_drafting.py` — Replace `ChatGroq` with `get_content_llm()`
- `src/search.py` — Replace `ChatGroq` with `get_reasoning_llm()`

---

## Files Changed

| File | Change |
|---|---|
| `src/agents/llm.py` | **NEW** — Central model factory |
| `src/embedding.py` | Swap `SentenceTransformer` → `OllamaEmbeddings` |
| `src/vectorstore.py` | Use factory for embeddings |
| `src/agent/store.py` | Use factory for embeddings |
| `src/agent/nodes/content_drafting.py` | `ChatGroq` → `get_content_llm()` |
| `src/search.py` | `ChatGroq` → `get_reasoning_llm()` |

---

## Verification

```bash
python -c "
from src.agents.llm import get_embedding_model
emb = get_embedding_model()
vecs = emb.embed_documents(['test document'])
print(f'Embedding dim: {len(vecs[0])}')
"
```

Expect: `Embedding dim: 1024` (qwen3-embedding:4b output dimension)
