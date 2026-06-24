import os
import json
import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.copilot.sanitize import (
    sanitize_input,
    detect_injection,
    sanitize_for_logging,
    SYSTEM_PROMPT_DEFENSE,
    validate_llm_output,
)
from src.copilot.explain import generate_step_explanation
from src.agents.graph import build_agent
from src.agents.state import AgentState
from mcp_server.tools.n8n_hook import trigger_n8n_marketing_pipeline
from app.ml.training_sink import record_training_event

router = APIRouter(prefix="/copilot", tags=["copilot"])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CopilotQuery(BaseModel):
    query: str = Field(max_length=2000, description="The user's request")


class ReviewAction(BaseModel):
    session_id: str
    step: str
    action: str = Field(pattern=r"^(approve|edit|reject|regenerate)$")
    data: dict[str, Any] | None = None


class ApproveSend(BaseModel):
    session_id: str
    email_subject: str | None = None
    email_body: str | None = None
    schedule_at: str | None = None


# In-memory session store (for demo; replace with DB later)
_sessions: dict[str, dict[str, Any]] = {}


def _get_session(session_id: str) -> dict:
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return _sessions[session_id]


@router.post("/run")
def copilot_run(req: CopilotQuery):
    try:
        safe_query = sanitize_input(req.query)
        if not safe_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        injection = detect_injection(safe_query)
        if injection:
            raise HTTPException(status_code=400, detail=f"Input rejected: {injection}")

        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        agent = build_agent()
        result = agent.invoke({"query": safe_query})

        session = {
            "session_id": session_id,
            "query": safe_query,
            "status": "needs_review",
            "steps": {
                "supervisor": {
                    "status": "completed",
                    "route": result.get("route", []),
                    "explanation": generate_step_explanation("supervisor", {"route": result.get("route", [])}),
                },
                "leads": {
                    "status": "pending",
                    "data": result.get("qualified_leads", []),
                    "explanation": generate_step_explanation("leads", {"query": safe_query, "leads": result.get("qualified_leads", [])}),
                },
                "tenders": {
                    "status": "pending",
                    "data": result.get("qualified_tenders", []),
                    "explanation": generate_step_explanation("tenders", {"query": safe_query, "tenders": result.get("qualified_tenders", [])}),
                },
                "intel": {
                    "status": "pending",
                    "data": result.get("sales_intelligence", {}),
                    "explanation": generate_step_explanation("intel", {}),
                },
                "email": {
                    "status": "pending",
                    "data": result.get("draft_email"),
                    "explanation": generate_step_explanation("email", {"draft": result.get("draft_email")}),
                },
                "approval": {
                    "status": "pending",
                    "data": {
                        "requires_approval": result.get("requires_human_approval", False),
                        "reason": result.get("approval_reason", ""),
                    },
                    "explanation": "Final review before sending.",
                },
            },
            "raw_result": sanitize_for_logging(result),
            "created_at": datetime.now().isoformat(),
        }

        _sessions[session_id] = session
        record_training_event(
            "copilot.run",
            session_id=session_id,
            input={"query": safe_query},
            output=session,
            source="copilot",
            metadata={"endpoint": "/copilot/run"},
        )
        return {"session_id": session_id, "steps": session["steps"], "query": safe_query}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
def copilot_review(action: ReviewAction):
    try:
        session = _get_session(action.session_id)
        step_data = session["steps"].get(action.step)
        if not step_data:
            raise HTTPException(status_code=400, detail=f"Unknown step: {action.step}")

        if action.action == "approve":
            step_data["status"] = "approved"
            step_data["human_edits"] = action.data
            _advance_pipeline(session)
        elif action.action == "edit":
            step_data["status"] = "edited"
            step_data["human_edits"] = action.data
            _advance_pipeline(session)
        elif action.action == "reject":
            step_data["status"] = "rejected"
            step_data["human_edits"] = action.data
            session["status"] = "rejected_by_user"
        elif action.action == "regenerate":
            step_data["status"] = "pending"
            step_data["human_feedback"] = action.data

        record_training_event(
            "copilot.review",
            session_id=action.session_id,
            input={"step": action.step, "action": action.action, "data": action.data},
            output={"status": session["status"], "step_status": step_data["status"]},
            source="copilot",
            metadata={"endpoint": "/copilot/review"},
        )

        return {"session_id": action.session_id, "steps": session["steps"], "status": session["status"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-send")
def copilot_approve_send(req: ApproveSend):
    try:
        session = _get_session(req.session_id)
        email_step = session["steps"].get("email")
        if email_step:
            if req.email_subject:
                if isinstance(email_step.get("data"), dict):
                    email_step["data"]["subject"] = req.email_subject
            if req.email_body:
                if isinstance(email_step.get("data"), dict):
                    email_step["data"]["email_body"] = req.email_body
            email_step["status"] = "approved"

        session["status"] = "sent"
        session["sent_at"] = datetime.now().isoformat()

        email_data = email_step.get("data") if email_step else {}
        if isinstance(email_data, dict):
            payload = {
                "lead_name": email_data.get("lead_name", "Unknown"),
                "validated_email": email_data.get("validated_email", ""),
                "tender_requirements": email_data.get("tender_requirements", ""),
                "email_body": req.email_body or email_data.get("email_body", ""),
            }
            n8n_result = trigger_n8n_marketing_pipeline(payload)
        else:
            n8n_result = {"success": False, "error": "No email data in session", "response": None}

        record_training_event(
            "copilot.approve_send",
            session_id=req.session_id,
            input={"email_subject": req.email_subject, "email_body": req.email_body, "schedule_at": req.schedule_at},
            output={"status": "sent", "n8n_response": n8n_result.get("response") or {}},
            source="copilot",
            metadata={"endpoint": "/copilot/approve-send"},
        )
        return {
            "session_id": req.session_id,
            "status": "sent",
            "message": "Email approved and queued for delivery.",
            "n8n_response": n8n_result.get("response") or {},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
def copilot_get_session(session_id: str):
    try:
        return _get_session(session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/{session_id}/{step}")
def copilot_explain(session_id: str, step: str):
    try:
        session = _get_session(session_id)
        step_data = session["steps"].get(step)
        if not step_data:
            raise HTTPException(status_code=404, detail=f"Step '{step}' not found")
        return {
            "session_id": session_id,
            "step": step,
            "explanation": step_data.get("explanation", ""),
            "status": step_data.get("status", "unknown"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _advance_pipeline(session: dict[str, Any]):
    steps = ["leads", "tenders", "intel", "email", "approval"]
    for s in steps:
        step = session["steps"].get(s)
        if step and step.get("status") == "pending":
            step["status"] = "ready_for_review"
            session["status"] = "needs_review"
            return
    if all(session["steps"].get(s, {}).get("status") in ("approved", "edited")
           for s in steps):
        session["status"] = "ready_to_send"
