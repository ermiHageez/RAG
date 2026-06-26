import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.sales_assistant.engine import SalesEngine, SalesPhase
from src.sales_assistant.prompts import DISCOVERY_PROMPT, RESEARCH_PROMPT, GENERATION_PROMPT, EMAIL_PROMPT
from src.doc_gen.generator import ProposalGenerator
from src.marketing.template_engine import TemplateEngine
from src.marketing.content_generator import ContentGenerator
from src.marketing.sheets_tracker import SheetsTracker
from src.marketing.follow_up import FollowUpManager
from src.marketing.analytics import Analytics
from src.agents.llm import get_content_llm, call_content_llm_with_fallback
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline
from app.ml.training_sink import append_to_training_dataset, record_training_event, get_metrics as get_sink_metrics
from app.ml.metrics import get_metrics as get_pipeline_metrics, format_prometheus
from app.ml.alerts import send_alert
from src.copilot.routes import router as copilot_router

app = FastAPI(title="eTech Multi-Agent API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot_router)

# ── Shared Instances ───────────────────────────────────────────────────

_sales_engine = SalesEngine()
_proposal_gen = ProposalGenerator()
_template_engine = TemplateEngine()
_content_gen = ContentGenerator()
_tracker = SheetsTracker()
_follow_up = FollowUpManager()
_analytics = Analytics()

# ── Request / Response Models ─────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    result: dict | None = None
    error: str | None = None

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5

class RAGQueryResponse(BaseModel):
    success: bool
    results: list[dict] = []
    total: int = 0

class RagChatRequest(BaseModel):
    session_id: str
    message: str
    history: list[dict] = []

class RagChatResponse(BaseModel):
    session_id: str
    response: str
    sources: list[dict] = []

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResponse(BaseModel):
    success: bool
    results: list[dict] = []
    total: int = 0

class MemoryRequest(BaseModel):
    session_id: str
    query: str | None = None
    response: dict | None = None

class MemoryResponse(BaseModel):
    session_id: str
    history: list[dict] = []
    count: int = 0

class EvaluateRequest(BaseModel):
    test_cases: list[dict] = []

class EvaluateResponse(BaseModel):
    success: bool
    results: dict = {}
    total_cases: int = 0

class ConfigResponse(BaseModel):
    models: dict[str, str] = {}
    data_dir: str = "data"
    faiss_dir: str = "faiss_store"
    google_cse_configured: bool = False
    n8n_configured: bool = False

# ── Sales Assistant Models ────────────────────────────────────────────

class SalesStartResponse(BaseModel):
    session_id: str
    phase: str = "DISCOVERY"

class SalesChatRequest(BaseModel):
    session_id: str
    message: str

class SalesChatResponse(BaseModel):
    session_id: str
    phase: str
    response: str
    questions: list[str] = []
    customer_info: dict = {}

class SalesGenerateRequest(BaseModel):
    session_id: str

class SalesGenerateResponse(BaseModel):
    session_id: str
    phase: str
    proposal_preview: str = ""
    proposal_pdf_path: str = ""

class SalesApproveRequest(BaseModel):
    session_id: str

class SalesApproveResponse(BaseModel):
    session_id: str
    status: str = ""
    email_body: str = ""
    n8n_response: dict = {}

class SalesResetResponse(BaseModel):
    session_id: str
    phase: str = "DISCOVERY"
    reset: bool = True

# ── Marketing Models ──────────────────────────────────────────────────

class TemplateUpdateRequest(BaseModel):
    html: str

class LeadStatusUpdateRequest(BaseModel):
    status: str

class FollowUpConfigUpdate(BaseModel):
    enabled: bool | None = None
    initial_delay_days: int | None = None
    max_follow_ups: int | None = None
    cadence_days: int | None = None

# ── Helper ────────────────────────────────────────────────────────────

def _default_state(query: str = "", route: list[str] | None = None) -> dict:
    return {
        "query": query,
        "route": route or [],
        "qualified_leads": [],
        "qualified_tenders": [],
        "knowledge_context": [],
        "sales_intelligence": None,
        "draft_email": None,
        "requires_human_approval": None,
        "approval_reason": None,
        "n8n_payload": None,
    }

def _read_etech_profile() -> str:
    path = "data/sample.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()[:3000]
    return "eTech is an Ethiopian technology company providing ERP, eHealth, eShare, and other enterprise solutions."


def _log_event(
    event_type: str,
    *,
    session_id: str | None = None,
    input: object = None,
    output: object = None,
    source: str = "api",
    metadata: dict | None = None,
    origin: str | None = None,
) -> None:
    try:
        record_training_event(
            event_type,
            session_id=session_id,
            input=input,
            output=output,
            source=source,
            metadata=metadata,
            origin=origin,
        )
    except Exception:
        logger.exception("Failed to record training event %s", event_type)

# ── Health & Config ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health/deep")
def deep_health():
    checks: dict[str, str | dict] = {}
    overall = "healthy"

    ollama_ok = False
    try:
        import httpx
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        r = httpx.get(f"{base}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            checks["ollama"] = {"status": "ok", "models": models}
            ollama_ok = True
        else:
            checks["ollama"] = {"status": "degraded", "detail": f"HTTP {r.status_code}"}
            overall = "degraded"
    except Exception as e:
        checks["ollama"] = {"status": "unhealthy", "detail": str(e)}
        overall = "degraded"

    try:
        from src.rag.vectorstore import get_vectorstore
        store = get_vectorstore()
        if store.index:
            checks["faiss"] = {"status": "ok", "vectors": store.index.ntotal}
        else:
            checks["faiss"] = {"status": "degraded", "detail": "No index loaded"}
    except Exception as e:
        checks["faiss"] = {"status": "unhealthy", "detail": str(e)}
        overall = "degraded"

    try:
        from app.ml.training_sink import RAW_INTERACTIONS_PATH
        if RAW_INTERACTIONS_PATH.exists():
            checks["dataset"] = {"status": "ok", "size_bytes": RAW_INTERACTIONS_PATH.stat().st_size}
        else:
            checks["dataset"] = {"status": "ok", "detail": "No dataset yet"}
    except Exception as e:
        checks["dataset"] = {"status": "unhealthy", "detail": str(e)}
        overall = "degraded"

    status_code = 200 if overall == "healthy" else 503
    from fastapi import HTTPException
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={"status": overall, "checks": checks, "timestamp": datetime.now().isoformat()},
        status_code=status_code,
    )

@app.get("/metrics")
def metrics_endpoint():
    sink = get_sink_metrics()
    pipeline = get_pipeline_metrics()
    return {"sink": sink, "pipeline": pipeline}

@app.get("/metrics/prometheus")
def metrics_prometheus():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(format_prometheus())

@app.get("/quality/report")
def quality_report():
    try:
        from app.ml.dataset_builder import DatasetBuilder
        return DatasetBuilder.get_quality_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quality/quarantine")
def quality_quarantine(limit: int = 50):
    from app.ml.dataset_builder import QUARANTINE_DIR
    q_path = QUARANTINE_DIR / "quarantine.jsonl"
    if not q_path.exists():
        return {"records": [], "total": 0}
    records = []
    with q_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            stripped = line.strip()
            if stripped:
                try:
                    records.append(json.loads(stripped))
                except Exception:
                    pass
    return {"records": records, "total": len(records)}

@app.get("/config", response_model=ConfigResponse)
def get_config():
    return ConfigResponse(
        models={
            "router": "gemma3:4b",
            "reasoning": "qwen3:8b",
            "content": "llama3.1:8b",
            "embedding": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
        },
        data_dir="data",
        faiss_dir="faiss_store",
        google_cse_configured=bool(os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CSE_ID")),
        n8n_configured=bool(os.getenv("N8N_WEBHOOK_URL")),
    )

# ── Agent Endpoints ───────────────────────────────────────────────────

@app.post("/agent/run", response_model=QueryResponse)
def run_agent(req: QueryRequest):
    try:
        from src.agents.graph import build_agent
        agent = build_agent()
        result = agent.invoke({"query": req.query})
        _log_event(
            "agent.run",
            input={"query": req.query},
            output=result,
            metadata={"endpoint": "/agent/run"},
        )
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/supervisor", response_model=QueryResponse)
def run_supervisor(req: QueryRequest):
    try:
        from src.agents.supervisor import supervisor_agent
        state = _default_state(query=req.query)
        result = supervisor_agent(state)
        _log_event("agent.supervisor", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/supervisor"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/leads", response_model=QueryResponse)
def run_lead_search(req: QueryRequest):
    try:
        from src.agents.lead import lead_agent
        state = _default_state(query=req.query, route=["lead"])
        result = lead_agent(state)
        _log_event("agent.leads", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/leads"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/tenders", response_model=QueryResponse)
def run_tender_search(req: QueryRequest):
    try:
        from src.agents.tender import tender_agent
        state = _default_state(query=req.query, route=["tender"])
        result = tender_agent(state)
        _log_event("agent.tenders", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/tenders"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/knowledge", response_model=QueryResponse)
def run_knowledge_search(req: QueryRequest):
    try:
        from src.agents.knowledge import run_knowledge_agent
        state = _default_state(query=req.query, route=["knowledge"])
        result = run_knowledge_agent(state)
        _log_event("agent.knowledge", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/knowledge"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/sales-intel", response_model=QueryResponse)
def run_sales_intelligence(req: QueryRequest):
    try:
        from src.agents.sales_intelligence import sales_intelligence_agent
        state = _default_state(query=req.query)
        result = sales_intelligence_agent(state)
        _log_event("agent.sales_intel", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/sales-intel"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/content", response_model=QueryResponse)
def run_content_drafting(req: QueryRequest):
    try:
        from src.agents.content import content_agent
        state = _default_state(query=req.query)
        state["sales_intelligence"] = {"insights": []}
        result = content_agent(state)
        _log_event("agent.content", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/content"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/approval", response_model=QueryResponse)
def run_approval(req: QueryRequest):
    try:
        from src.agents.approval import approval_agent
        state = _default_state(query=req.query)
        result = approval_agent(state)
        _log_event("agent.approval", input={"query": req.query}, output=result, metadata={"endpoint": "/agent/approval"})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── RAG Endpoints ─────────────────────────────────────────────────────

@app.post("/rag/upload")
def rag_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    os.makedirs("data", exist_ok=True)
    content = file.file.read()
    path = os.path.join("data", file.filename)
    with open(path, "wb") as f:
        f.write(content)
    return {"success": True, "path": path, "size": len(content)}

@app.get("/rag/status")
def rag_status():
    try:
        from src.rag.vectorstore import FaissVectorStore
        store = FaissVectorStore("faiss_store")
        store.load()
        if store.index is None:
            return {"active": False, "entries": 0, "dimension": 0, "path": "faiss_store"}
        return {
            "active": True,
            "entries": store.index.ntotal,
            "dimension": store.index.d,
            "path": "faiss_store",
        }
    except Exception as e:
        return {"active": False, "entries": 0, "dimension": 0, "path": "faiss_store", "error": str(e)}

@app.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(req: RAGQueryRequest):
    try:
        from src.rag.vectorstore import FaissVectorStore
        store = FaissVectorStore("faiss_store")
        store.load()
        if store.index is None:
            _log_event("rag.query", input={"query": req.query, "top_k": req.top_k}, output=[], metadata={"endpoint": "/rag/query", "empty": True})
            return RAGQueryResponse(success=True, results=[], total=0)
        results = store.query(req.query, top_k=req.top_k)
        _log_event("rag.query", input={"query": req.query, "top_k": req.top_k}, output=results, metadata={"endpoint": "/rag/query", "total": len(results)})
        return RAGQueryResponse(success=True, results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/rebuild")
def rag_rebuild():
    try:
        from src.rag.data_loader import load_all_documents
        from src.rag.vectorstore import FaissVectorStore
        import shutil
        if os.path.exists("faiss_store"):
            shutil.rmtree("faiss_store")
        docs = load_all_documents("data")
        store = FaissVectorStore("faiss_store")
        ok = store.build_from_documents(docs)
        if ok:
            store.load()
            _log_event("rag.rebuild", input={"data_dir": "data"}, output={"entries": store.index.ntotal if store.index else 0}, metadata={"endpoint": "/rag/rebuild"})
            return {"success": True, "entries": store.index.ntotal if store.index else 0}
        _log_event("rag.rebuild", input={"data_dir": "data"}, output={"success": False, "error": "No documents loaded"}, metadata={"endpoint": "/rag/rebuild"})
        return {"success": False, "error": "No documents loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/chat", response_model=RagChatResponse)
def rag_chat(req: RagChatRequest):
    try:
        from src.rag.vectorstore import get_vectorstore
        from src.rag.retriever import Retriever
        from src.rag.reranker import NoOpReranker
        from src.agents.llm import get_content_llm

        store = get_vectorstore()
        retriever = Retriever(vectorstore=store, reranker=NoOpReranker())
        rag_results = retriever.retrieve(req.message, top_k=10, rerank_top_k=5)

        context_parts = []
        sources = []
        for r in rag_results:
            meta = r.get("metadata", {})
            text = meta.get("text", "") if isinstance(meta, dict) else r.get("text", "")
            source = meta.get("source", {}) if isinstance(meta, dict) else r.get("source", {})
            if text:
                context_parts.append(text)
                sources.append({
                    "title": source.get("title", source.get("source", "RAG source")) if isinstance(source, dict) else "RAG source",
                    "snippet": text[:200],
                    "url": source.get("url", "") if isinstance(source, dict) else "",
                })

        context = "\n\n---\n\n".join(context_parts[:5]) if context_parts else ""

        history_lines = []
        for h in req.history[-6:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            history_lines.append(f"{'User' if role == 'user' else 'Assistant'}: {content}")
        history_str = "\n".join(history_lines)

        system_prompt = (
            "You are eTech Ethiopia's AI assistant for sales intelligence and market research. "
            "Answer concisely and accurately using the provided context. "
            "If the context doesn't contain the answer, say so politely "
            "and offer to search for more information. "
            "Keep responses informative but brief (2-4 paragraphs max)."
        )

        if context:
            full_prompt = (
                f"{system_prompt}\n\n"
                f"Relevant context from knowledge base:\n{context}\n\n"
                f"Conversation history:\n{history_str}\n\n"
                f"User: {req.message}\n\nAssistant:"
            )
        else:
            full_prompt = (
                f"{system_prompt}\n\n"
                f"Conversation history:\n{history_str}\n\n"
                f"User: {req.message}\n\nAssistant:"
            )

        text = call_content_llm_with_fallback(full_prompt, ollama_timeout=15)
        _log_event(
            "rag.chat",
            session_id=req.session_id,
            input={"message": req.message, "history": req.history, "context_count": len(context_parts)},
            output={"response": text, "sources": sources},
            metadata={"endpoint": "/rag/chat", "source_count": len(sources), "status_code": 200},
            origin="/rag/chat",
        )
        logger.info(
            "AI chat 200 OK: endpoint=/rag/chat session=%s source_count=%s dataset=queued",
            req.session_id,
            len(sources),
        )

        return RagChatResponse(
            session_id=req.session_id,
            response=text,
            sources=sources,
        )
    except Exception:
        logger.exception("rag_chat failed — both Ollama and Groq fallback exhausted")
        raise HTTPException(
            status_code=503,
            detail="LLM unavailable — local Ollama and Groq fallback both failed. "
                   "Check that Ollama is running or GROQ_API_KEY is valid.",
        )


# ── MCP Tool Endpoints ────────────────────────────────────────────────

@app.get("/mcp/tools")
def list_mcp_tools():
    return {
        "tools": [
            {"name": "discover_ethiopian_enterprises", "description": "Search for Ethiopian companies via web search"},
            {"name": "fetch_active_tenders", "description": "Scrape active tenders and business opportunities from 2merkato.com and addisbiz.com"},
            {"name": "discover_companies", "description": "Scrape company directory listings from 2merkato.com, addisbiz.com, and ethyp.com"},
            {"name": "trigger_n8n_marketing_pipeline", "description": "Send payload to n8n webhook"},
        ],
        "count": 4,
    }

@app.post("/mcp/search", response_model=SearchResponse)
def mcp_search(req: SearchRequest):
    try:
        from mcp_server.tools.search import discover_ethiopian_enterprises
        results = discover_ethiopian_enterprises(req.query)
        return SearchResponse(success=True, results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/tenders", response_model=SearchResponse)
def mcp_tenders(req: SearchRequest):
    try:
        from mcp_server.tools.tenders import fetch_active_tenders
        results = fetch_active_tenders(sector=req.query if req.query else None)
        return SearchResponse(success=True, results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/directory", response_model=SearchResponse)
def mcp_directory(req: SearchRequest):
    try:
        from mcp_server.tools.directory import discover_companies
        results = discover_companies(sector=req.query if req.query else None, max_per_source=req.max_results)
        return SearchResponse(success=True, results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Memory Endpoints ──────────────────────────────────────────────────

@app.get("/memory/{memory_type}", response_model=MemoryResponse)
def get_memory(memory_type: str, session_id: str = "default"):
    try:
        from src.memory.base import JSONMemoryStore
        store = JSONMemoryStore("memory_store")
        if memory_type == "conversation":
            from src.memory.conversation_memory import ConversationMemory
            mem = ConversationMemory(store)
            history = mem.get_history(session_id)
        else:
            data = store.load(f"{memory_type}_{session_id}")
            history = data if isinstance(data, list) else ([data] if data else [])
        return MemoryResponse(session_id=session_id, history=history, count=len(history))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/{memory_type}", response_model=MemoryResponse)
def save_memory(memory_type: str, req: MemoryRequest):
    try:
        from src.memory.base import JSONMemoryStore
        store = JSONMemoryStore("memory_store")
        if memory_type == "conversation":
            from src.memory.conversation_memory import ConversationMemory
            mem = ConversationMemory(store)
            if req.query is not None and req.response is not None:
                mem.add_interaction(req.session_id, req.query, req.response)
            history = mem.get_history(req.session_id)
        else:
            key = f"{memory_type}_{req.session_id}"
            data = store.load(key) or []
            if req.query is not None and req.response is not None:
                data.append({
                    "query": req.query,
                    "response": req.response,
                    "timestamp": datetime.now().isoformat(),
                })
                store.save(key, data)
                append_to_training_dataset(req.session_id, req.query, req.response)
            history = data
        return MemoryResponse(session_id=req.session_id, history=history, count=len(history))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Evaluation Endpoints ──────────────────────────────────────────────

@app.post("/evaluate/rag", response_model=EvaluateResponse)
def evaluate_rag(req: EvaluateRequest):
    try:
        from src.evaluation.rag_eval import RAGPrecisionEvaluator
        from src.evaluation.benchmarks import BenchmarkSuite
        suite = BenchmarkSuite()
        suite.add_evaluator(RAGPrecisionEvaluator())
        results = suite.run(req.test_cases or [
            {"name": "eTech_capabilities", "input": "What does eTech do?",
             "output": [{"text": "eTech provides ERP solutions"}], "expected": None},
        ])
        return EvaluateResponse(success=True, results=results, total_cases=len(req.test_cases or [1]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/routing", response_model=EvaluateResponse)
def evaluate_routing(req: EvaluateRequest):
    try:
        from src.evaluation.agent_eval import RoutingAccuracyEvaluator
        from src.evaluation.benchmarks import BenchmarkSuite
        suite = BenchmarkSuite()
        suite.add_evaluator(RoutingAccuracyEvaluator())
        results = suite.run(req.test_cases or [
            {"name": "bank_query", "input": "find banks in Ethiopia",
             "output": {"route": ["lead"]}, "expected": None},
        ])
        return EvaluateResponse(success=True, results=results, total_cases=len(req.test_cases or [1]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/content", response_model=EvaluateResponse)
def evaluate_content(req: EvaluateRequest):
    try:
        from src.evaluation.content_eval import ContentQualityEvaluator
        from src.evaluation.benchmarks import BenchmarkSuite
        suite = BenchmarkSuite()
        suite.add_evaluator(ContentQualityEvaluator())
        results = suite.run(req.test_cases or [
            {"name": "email_quality", "input": "Write email to Test Corp",
             "output": {"email_body": "Dear Test Corp..."}, "expected": None},
        ])
        return EvaluateResponse(success=True, results=results, total_cases=len(req.test_cases or [1]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════
# ── SALES ASSISTANT ENDPOINTS (Sprint 7) ──────────────────────────────
# ══════════════════════════════════════════════════════════════════════

@app.post("/sales/start", response_model=SalesStartResponse)
def sales_start():
    session_id = _sales_engine.create_session()
    _log_event("sales.start", session_id=session_id, input={}, output={"phase": "DISCOVERY"}, metadata={"endpoint": "/sales/start"})
    return SalesStartResponse(session_id=session_id, phase="DISCOVERY")


@app.post("/sales/chat", response_model=SalesChatResponse)
def sales_chat(req: SalesChatRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        _sales_engine.add_message(req.session_id, "user", req.message)
        llm = get_content_llm()
        phase = session.phase

        if phase == SalesPhase.DISCOVERY:
            existing = json.dumps(session.customer_info) if session.customer_info else "Nothing yet"
            prompt = DISCOVERY_PROMPT.format(existing_info=existing, user_message=req.message)
            response = llm.invoke(prompt)
            text = response.content.strip()

            session.customer_info["last_response"] = req.message
            questions = []
            try:
                parsed = json.loads(text)
                questions = parsed.get("questions", [])
                text = "Here are some questions to help me understand your needs better."
            except Exception:
                questions = []

            _sales_engine.add_message(req.session_id, "assistant", text)

            if not questions and len(session.messages) >= 4:
                _sales_engine.transition(req.session_id, SalesPhase.RESEARCH)
                phase = SalesPhase.RESEARCH
                text = "Great, I have enough information. Let me research your company and needs."
                _sales_engine.add_message(req.session_id, "assistant", text)

            result = SalesChatResponse(
                session_id=req.session_id,
                phase=phase.value,
                response=text,
                questions=questions,
                customer_info=session.customer_info,
            )
            _log_event(
                "sales.chat",
                session_id=req.session_id,
                input={"message": req.message},
                output={"phase": result.phase, "response": result.response, "questions": questions},
                metadata={"endpoint": "/sales/chat", "stage": "discovery"},
            )
            return result

        elif phase == SalesPhase.RESEARCH:
            try:
                from mcp_server.tools.directory import discover_companies
                sector = session.customer_info.get("sector", "")
                mcp_results = discover_companies(sector=sector if sector else None, max_per_source=3)
            except Exception:
                mcp_results = []

            research_prompt = RESEARCH_PROMPT.format(
                customer_name=session.customer_info.get("company_name", "Customer"),
                mcp_results=str(mcp_results[:5]),
            )
            response = llm.invoke(research_prompt)
            text = response.content.strip()
            try:
                session.research_data = json.loads(text)
            except Exception:
                session.research_data = {"raw": text}

            session.research_data["mcp_results"] = mcp_results[:5]
            _sales_engine.add_message(req.session_id, "assistant", text)
            _sales_engine.transition(req.session_id, SalesPhase.GENERATION)

            result = SalesChatResponse(
                session_id=req.session_id,
                phase=SalesPhase.GENERATION.value,
                response="Research complete. You can now generate the proposal with POST /sales/generate.",
                customer_info=session.customer_info,
            )
            _log_event(
                "sales.chat",
                session_id=req.session_id,
                input={"message": req.message},
                output={"phase": result.phase, "response": result.response, "mcp_results": len(mcp_results)},
                metadata={"endpoint": "/sales/chat", "stage": "research"},
            )
            return result

        elif phase == SalesPhase.GENERATION:
            result = SalesChatResponse(
                session_id=req.session_id,
                phase=phase.value,
                response="Already in generation phase. Use POST /sales/generate to create the proposal.",
                customer_info=session.customer_info,
            )
            _log_event(
                "sales.chat",
                session_id=req.session_id,
                input={"message": req.message},
                output={"phase": result.phase, "response": result.response},
                metadata={"endpoint": "/sales/chat", "stage": "generation"},
            )
            return result

        elif phase == SalesPhase.COMPLETE:
            result = SalesChatResponse(
                session_id=req.session_id,
                phase=phase.value,
                response="This session is complete. Start a new session with POST /sales/start.",
                customer_info=session.customer_info,
            )
            _log_event(
                "sales.chat",
                session_id=req.session_id,
                input={"message": req.message},
                output={"phase": result.phase, "response": result.response},
                metadata={"endpoint": "/sales/chat", "stage": "complete"},
            )
            return result

        result = SalesChatResponse(
            session_id=req.session_id,
            phase=phase.value,
            response="Continuing...",
            customer_info=session.customer_info,
        )
        _log_event(
            "sales.chat",
            session_id=req.session_id,
            input={"message": req.message},
            output={"phase": result.phase, "response": result.response},
            metadata={"endpoint": "/sales/chat", "stage": "fallback"},
        )
        return result
    except Exception as e:
        _log_event(
            "sales.chat",
            session_id=req.session_id,
            input={"message": req.message},
            output={"error": str(e)},
            metadata={"endpoint": "/sales/chat", "stage": "error"},
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales/generate", response_model=SalesGenerateResponse)
def sales_generate(req: SalesGenerateRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.phase != SalesPhase.GENERATION:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {session.phase.value}. Must be GENERATION.")

    try:
        llm = get_content_llm()
        etech_profile = _read_etech_profile()

        try:
            from src.rag.vectorstore import FaissVectorStore
            store = FaissVectorStore("faiss_store")
            store.load()
            rag_results = store.query("software documentation proposal template", top_k=3) if store.index else []
            rag_style_refs = "\n".join([r.get("text", "") for r in rag_results])
        except Exception:
            rag_style_refs = ""

        gen_prompt = GENERATION_PROMPT.format(
            customer_profile=json.dumps(session.research_data, indent=2) if session.research_data else "{}",
            etech_profile=etech_profile,
            rag_style_refs=rag_style_refs or "Standard business proposal format.",
        )

        response = llm.invoke(gen_prompt)
        proposal_text = response.content.strip()
        session.proposal_text = proposal_text

        research = session.research_data or {}
        customer_name = research.get("company", session.customer_info.get("company_name", "Customer"))
        pdf_path = _proposal_gen.generate(req.session_id, proposal_text, customer_name=customer_name)
        session.proposal_pdf_path = pdf_path
        _sales_engine.add_message(req.session_id, "assistant", "Proposal generated successfully.")
        _log_event(
            "sales.generate",
            session_id=req.session_id,
            input={"phase": session.phase.value, "customer_name": customer_name},
            output={"proposal_preview": proposal_text[:500], "proposal_pdf_path": pdf_path},
            metadata={"endpoint": "/sales/generate"},
        )

        preview = proposal_text[:500]
        return SalesGenerateResponse(
            session_id=req.session_id,
            phase=session.phase.value,
            proposal_preview=preview,
            proposal_pdf_path=pdf_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales/approve-send", response_model=SalesApproveResponse)
def sales_approve_send(req: SalesApproveRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.phase != SalesPhase.GENERATION:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {session.phase.value}. Must be GENERATION.")

    try:
        llm = get_content_llm()
        research = session.research_data or {}
        customer_name = research.get("company", session.customer_info.get("company_name", "Customer"))

        email_prompt = EMAIL_PROMPT.format(
            proposal=session.proposal_text[:1500] if session.proposal_text else "",
            customer_contact=json.dumps(research.get("contacts", {})),
        )
        email_response = llm.invoke(email_prompt)
        email_text = email_response.content.strip()

        try:
            email_data = json.loads(email_text)
            subject = email_data.get("subject", "Proposal from eTech")
            email_body = email_data.get("body", email_text)
        except Exception:
            subject = "Proposal from eTech S.C."
            email_body = email_text

        session.email_body = email_body

        product = "General"
        sector = research.get("sector", session.customer_info.get("sector", ""))
        if "health" in sector.lower():
            product = "Ehealth"
        elif "bank" in sector.lower() or "finance" in sector.lower():
            product = "SCCO"
        elif "erp" in sector.lower() or "enterprise" in sector.lower():
            product = "ERP"

        email_contact = ""
        if isinstance(research.get("contacts"), dict):
            email_contact = research["contacts"].get("email", "")

        payload = {
            "lead_name": customer_name,
            "validated_email": email_contact or f"{customer_name.lower().replace(' ', '.')}@example.com",
            "tender_requirements": f"Proposal generated via sales assistant. Product: {product}",
            "email_body": email_body,
        }

        n8n_result = trigger_n8n_marketing_pipeline(payload)
        session.approved = True
        _sales_engine.transition(req.session_id, SalesPhase.COMPLETE)

        _tracker.add_lead(
            session_id=req.session_id,
            customer_name=customer_name,
            email=email_contact or "unknown@example.com",
            product=product,
            status="Sent",
        )
        _log_event(
            "sales.approve_send",
            session_id=req.session_id,
            input={"customer_name": customer_name, "product": product},
            output={"status": "sent", "email_body": email_body, "n8n_response": n8n_result.get("response") or {}},
            metadata={"endpoint": "/sales/approve-send"},
        )

        return SalesApproveResponse(
            session_id=req.session_id,
            status="sent",
            email_body=email_body,
            n8n_response=n8n_result.get("response") or {},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales/reset", response_model=SalesResetResponse)
def sales_reset(req: SalesGenerateRequest):
    ok = _sales_engine.reset_session(req.session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    _log_event("sales.reset", session_id=req.session_id, input={"session_id": req.session_id}, output={"reset": True}, metadata={"endpoint": "/sales/reset"})
    return SalesResetResponse(session_id=req.session_id, phase="DISCOVERY", reset=True)


@app.get("/doc-gen/download/{session_id}")
def doc_gen_download(session_id: str):
    session = _sales_engine.get_session(session_id)
    if not session or not session.proposal_pdf_path:
        raise HTTPException(status_code=404, detail="Proposal not found for this session")
    file_path = session.proposal_pdf_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Proposal file not found on disk")
    ext = os.path.splitext(file_path)[1].lower()
    media_type = "application/pdf" if ext == ".pdf" else "text/html"
    return FileResponse(file_path, media_type=media_type, filename=f"proposal_{session_id[:8]}{ext}")


# ══════════════════════════════════════════════════════════════════════
# ── MARKETING ENDPOINTS (Sprint 8) ────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════

# ── Templates ─────────────────────────────────────────────────────────

@app.get("/marketing/templates")
def marketing_list_templates():
    try:
        return {"templates": _template_engine.list_templates()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/templates/{product}")
def marketing_get_template(product: str):
    try:
        html = _template_engine.get_template_html(product)
        if not html:
            raise HTTPException(status_code=404, detail=f"Template not found for product: {product}")
        return {"product": product, "html": html}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/marketing/templates/{product}")
def marketing_update_template(product: str, req: TemplateUpdateRequest):
    try:
        ok = _template_engine.update_template_html(product, req.html)
        if not ok:
            raise HTTPException(status_code=404, detail=f"Template not found for product: {product}")
        _log_event(
            "marketing.template.update",
            input={"product": product},
            output={"success": True},
            metadata={"endpoint": "/marketing/templates/{product}", "product": product},
        )
        return {"success": True, "product": product}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Campaign Tracking ─────────────────────────────────────────────────

@app.get("/marketing/campaign/stats")
def marketing_campaign_stats():
    try:
        return _tracker.get_campaign_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/campaign/leads")
def marketing_campaign_leads(status: str = ""):
    try:
        if status:
            return {"leads": _tracker.get_leads_by_status(status)}
        return {"leads": _tracker.get_all_leads()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/marketing/campaign/leads/{session_id}/status")
def marketing_update_lead_status(session_id: str, req: LeadStatusUpdateRequest):
    try:
        ok = _tracker.update_status(session_id, req.status)
        if not ok:
            raise HTTPException(status_code=400, detail=f"Invalid status transition to '{req.status}'")
        _log_event(
            "marketing.campaign.lead_status",
            session_id=session_id,
            input={"status": req.status},
            output={"success": True},
            metadata={"endpoint": "/marketing/campaign/leads/{session_id}/status"},
        )
        return {"success": True, "session_id": session_id, "new_status": req.status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Follow-Up ─────────────────────────────────────────────────────────

@app.post("/marketing/follow-up/check")
def marketing_follow_up_check():
    try:
        due = _follow_up.check_due_follow_ups()
        results = []
        for lead in due:
            result = _follow_up.send_follow_up(lead["session_id"])
            results.append(result)
        _log_event(
            "marketing.follow_up.check",
            input={"due_count": len(due)},
            output={"results": results},
            metadata={"endpoint": "/marketing/follow-up/check"},
        )
        return {"due_count": len(due), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/follow-up/schedule/{session_id}")
def marketing_follow_up_schedule(session_id: str):
    try:
        return _follow_up.get_follow_up_schedule(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/follow-up/config")
def marketing_follow_up_get_config():
    try:
        config = _follow_up.config
        return {
            "enabled": config.enabled,
            "initial_delay_days": config.initial_delay_days,
            "max_follow_ups": config.max_follow_ups,
            "cadence_days": config.cadence_days,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/marketing/follow-up/config")
def marketing_follow_up_config(req: FollowUpConfigUpdate):
    try:
        kwargs = req.model_dump(exclude_none=True)
        _follow_up.set_config(**kwargs)
        _log_event(
            "marketing.follow_up.config",
            input=kwargs,
            output={"config": _follow_up.config.__dict__},
            metadata={"endpoint": "/marketing/follow-up/config"},
        )
        return {"success": True, "config": _follow_up.config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Analytics ─────────────────────────────────────────────────────────

@app.get("/marketing/analytics/summary")
def marketing_analytics_summary(start_date: str = "", end_date: str = ""):
    try:
        result = _analytics.get_campaign_summary(
            start_date= start_date if start_date else None,
            end_date= end_date if end_date else None,
        )
        _log_event(
            "marketing.analytics.summary",
            input={"start_date": start_date, "end_date": end_date},
            output=result,
            metadata={"endpoint": "/marketing/analytics/summary"},
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/analytics/product-breakdown")
def marketing_analytics_product_breakdown():
    try:
        return {"products": _analytics.get_product_breakdown()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/analytics/timeline")
def marketing_analytics_timeline(days: int = 30):
    try:
        return {"timeline": _analytics.get_timeline(days=days)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/marketing/analytics/export")
def marketing_analytics_export(format: str = "json"):
    try:
        return _analytics.export_report(format=format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
