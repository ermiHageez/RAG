import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
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
from src.agents.llm import get_content_llm, get_reasoning_llm
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline

app = FastAPI(title="eTech Multi-Agent API", version="0.3.0")

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
    reset: bool = False

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

# ── Health & Config ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/config", response_model=ConfigResponse)
def get_config():
    return ConfigResponse(
        models={
            "router": "gemma3:4b",
            "reasoning": "qwen3:8b",
            "content": "llama3.1:8b",
            "embedding": "qwen3-embedding:4b",
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
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/supervisor", response_model=QueryResponse)
def run_supervisor(req: QueryRequest):
    try:
        from src.agents.supervisor import supervisor_agent
        state = _default_state(query=req.query)
        result = supervisor_agent(state)
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/leads", response_model=QueryResponse)
def run_lead_search(req: QueryRequest):
    try:
        from src.agents.lead import lead_agent
        state = _default_state(query=req.query, route=["lead"])
        result = lead_agent(state)
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/tenders", response_model=QueryResponse)
def run_tender_search(req: QueryRequest):
    try:
        from src.agents.tender import tender_agent
        state = _default_state(query=req.query, route=["tender"])
        result = tender_agent(state)
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/knowledge", response_model=QueryResponse)
def run_knowledge_search(req: QueryRequest):
    try:
        from src.agents.knowledge import run_knowledge_agent
        state = _default_state(query=req.query, route=["knowledge"])
        result = run_knowledge_agent(state)
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/sales-intel", response_model=QueryResponse)
def run_sales_intelligence(req: QueryRequest):
    try:
        from src.agents.sales_intelligence import sales_intelligence_agent
        state = _default_state(query=req.query)
        result = sales_intelligence_agent(state)
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
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/approval", response_model=QueryResponse)
def run_approval(req: QueryRequest):
    try:
        from src.agents.approval import approval_agent
        state = _default_state(query=req.query)
        result = approval_agent(state)
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── RAG Endpoints ─────────────────────────────────────────────────────

@app.get("/rag/status")
def rag_status():
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

@app.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(req: RAGQueryRequest):
    try:
        from src.rag.vectorstore import FaissVectorStore
        store = FaissVectorStore("faiss_store")
        store.load()
        if store.index is None:
            return RAGQueryResponse(success=True, results=[], total=0)
        results = store.query(req.query, top_k=req.top_k)
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
            return {"success": True, "entries": store.index.ntotal if store.index else 0}
        return {"success": False, "error": "No documents loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            if req.query and req.response:
                mem.add_interaction(req.session_id, req.query, req.response)
            history = mem.get_history(req.session_id)
        else:
            data = store.load(f"{memory_type}_{req.session_id}") or []
            data.append({"query": req.query, "response": req.response, "timestamp": datetime.now().isoformat()})
            store.save(f"{memory_type}_{req.session_id}", data)
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
    return SalesStartResponse(session_id=session_id, phase="DISCOVERY")


@app.post("/sales/chat", response_model=SalesChatResponse)
def sales_chat(req: SalesChatRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
            import json as j
            parsed = j.loads(text)
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

        return SalesChatResponse(
            session_id=req.session_id,
            phase=phase.value,
            response=text,
            questions=questions,
            customer_info=session.customer_info,
        )

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
            import json as j
            session.research_data = j.loads(text)
        except Exception:
            session.research_data = {"raw": text}

        session.research_data["mcp_results"] = mcp_results[:5]
        _sales_engine.add_message(req.session_id, "assistant", text)
        _sales_engine.transition(req.session_id, SalesPhase.GENERATION)

        return SalesChatResponse(
            session_id=req.session_id,
            phase=SalesPhase.GENERATION.value,
            response="Research complete. You can now generate the proposal with POST /sales/generate.",
            customer_info=session.customer_info,
        )

    elif phase == SalesPhase.GENERATION:
        return SalesChatResponse(
            session_id=req.session_id,
            phase=phase.value,
            response="Already in generation phase. Use POST /sales/generate to create the proposal.",
            customer_info=session.customer_info,
        )

    elif phase == SalesPhase.COMPLETE:
        return SalesChatResponse(
            session_id=req.session_id,
            phase=phase.value,
            response="This session is complete. Start a new session with POST /sales/start.",
            customer_info=session.customer_info,
        )

    return SalesChatResponse(
        session_id=req.session_id,
        phase=phase.value,
        response="Continuing...",
        customer_info=session.customer_info,
    )


@app.post("/sales/generate", response_model=SalesGenerateResponse)
def sales_generate(req: SalesGenerateRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.phase != SalesPhase.GENERATION:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {session.phase.value}. Must be GENERATION.")

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

    customer_name = session.research_data.get("company", session.customer_info.get("company_name", "Customer"))
    pdf_path = _proposal_gen.generate(req.session_id, proposal_text, customer_name=customer_name)
    session.proposal_pdf_path = pdf_path
    _sales_engine.add_message(req.session_id, "assistant", "Proposal generated successfully.")

    preview = proposal_text[:500]
    return SalesGenerateResponse(
        session_id=req.session_id,
        phase=session.phase.value,
        proposal_preview=preview,
        proposal_pdf_path=pdf_path,
    )


@app.post("/sales/approve-send", response_model=SalesApproveResponse)
def sales_approve_send(req: SalesApproveRequest):
    session = _sales_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.phase != SalesPhase.GENERATION:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {session.phase.value}. Must be GENERATION.")

    llm = get_content_llm()
    customer_name = session.research_data.get("company", session.customer_info.get("company_name", "Customer"))

    email_prompt = EMAIL_PROMPT.format(
        proposal=session.proposal_text[:1500] if session.proposal_text else "",
        customer_contact=json.dumps(session.research_data.get("contacts", {})),
    )
    email_response = llm.invoke(email_prompt)
    email_text = email_response.content.strip()

    try:
        import json as j
        email_data = j.loads(email_text)
        subject = email_data.get("subject", "Proposal from eTech")
        email_body = email_data.get("body", email_text)
    except Exception:
        subject = "Proposal from eTech S.C."
        email_body = email_text

    session.email_body = email_body

    product = "General"
    sector = session.research_data.get("sector", session.customer_info.get("sector", ""))
    if "health" in sector.lower():
        product = "Ehealth"
    elif "bank" in sector.lower() or "finance" in sector.lower():
        product = "SCCO"
    elif "erp" in sector.lower() or "enterprise" in sector.lower():
        product = "ERP"

    email_contact = ""
    if isinstance(session.research_data.get("contacts"), dict):
        email_contact = session.research_data["contacts"].get("email", "")

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

    return SalesApproveResponse(
        session_id=req.session_id,
        status="sent",
        email_body=email_body,
        n8n_response=n8n_result.get("response", {}),
    )


@app.post("/sales/reset", response_model=SalesResetResponse)
def sales_reset(req: SalesGenerateRequest):
    ok = _sales_engine.reset_session(req.session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
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
    return {"templates": _template_engine.list_templates()}

@app.get("/marketing/templates/{product}")
def marketing_get_template(product: str):
    html = _template_engine.get_template_html(product)
    if not html:
        raise HTTPException(status_code=404, detail=f"Template not found for product: {product}")
    return {"product": product, "html": html}

@app.put("/marketing/templates/{product}")
def marketing_update_template(product: str, req: TemplateUpdateRequest):
    ok = _template_engine.update_template_html(product, req.html)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Template not found for product: {product}")
    return {"success": True, "product": product}

# ── Campaign Tracking ─────────────────────────────────────────────────

@app.get("/marketing/campaign/stats")
def marketing_campaign_stats():
    return _tracker.get_campaign_stats()

@app.get("/marketing/campaign/leads")
def marketing_campaign_leads(status: str = ""):
    if status:
        return {"leads": _tracker.get_leads_by_status(status)}
    return {"leads": _tracker.get_all_leads()}

@app.put("/marketing/campaign/leads/{session_id}/status")
def marketing_update_lead_status(session_id: str, req: LeadStatusUpdateRequest):
    ok = _tracker.update_status(session_id, req.status)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Invalid status transition to '{req.status}'")
    return {"success": True, "session_id": session_id, "new_status": req.status}

# ── Follow-Up ─────────────────────────────────────────────────────────

@app.post("/marketing/follow-up/check")
def marketing_follow_up_check():
    due = _follow_up.check_due_follow_ups()
    results = []
    for lead in due:
        result = _follow_up.send_follow_up(lead["session_id"])
        results.append(result)
    return {"due_count": len(due), "results": results}

@app.get("/marketing/follow-up/schedule/{session_id}")
def marketing_follow_up_schedule(session_id: str):
    return _follow_up.get_follow_up_schedule(session_id)

@app.put("/marketing/follow-up/config")
def marketing_follow_up_config(req: FollowUpConfigUpdate):
    kwargs = req.model_dump(exclude_none=True)
    _follow_up.set_config(**kwargs)
    return {"success": True, "config": _follow_up.config}

# ── Analytics ─────────────────────────────────────────────────────────

@app.get("/marketing/analytics/summary")
def marketing_analytics_summary(start_date: str = "", end_date: str = ""):
    return _analytics.get_campaign_summary(
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
    )

@app.get("/marketing/analytics/product-breakdown")
def marketing_analytics_product_breakdown():
    return {"products": _analytics.get_product_breakdown()}

@app.get("/marketing/analytics/timeline")
def marketing_analytics_timeline(days: int = 30):
    return {"timeline": _analytics.get_timeline(days=days)}

@app.get("/marketing/analytics/export")
def marketing_analytics_export(format: str = "json"):
    return _analytics.export_report(format=format)
