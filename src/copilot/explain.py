from src.copilot.sanitize import (
    sanitize_input,
    detect_injection,
    SYSTEM_PROMPT_DEFENSE,
    wrap_user_input,
)
from src.agents.llm import get_content_llm, get_reasoning_llm, get_router_llm


def explain_lead_selection(query: str, leads: list[dict]) -> str:
    if not leads:
        return "No leads were found matching your query."
    sectors = set(l.get("sector", "") for l in leads)
    return (
        f"Found {len(leads)} potential {'lead' if len(leads) == 1 else 'leads'} "
        f"in {len(sectors)} sector{'s' if len(sectors) != 1 else ''}: "
        f"{', '.join(s for s in sectors if s)[:200]}. "
        f"The AI searched web directories and company listings matching your query."
    )


def explain_tender_selection(query: str, tenders: list[dict]) -> str:
    if not tenders:
        return "No tenders were found matching your query."
    urgent = sum(1 for t in tenders if t.get("urgency") == "red")
    return (
        f"Found {len(tenders)} tender{'s' if len(tenders) != 1 else ''}. "
        f"{urgent} {'is' if urgent == 1 else 'are'} urgent (deadline within 7 days). "
        f"Each tender was scored against eTech's capabilities using the RAG knowledge base."
    )


def explain_email_draft(draft: dict | None) -> str:
    if not draft:
        return "No email was drafted."
    score = draft.get("personalization_score", 0.0)
    company = draft.get("lead_name", "the prospect")
    level = "good" if score >= 0.7 else "moderate" if score >= 0.3 else "low"
    return (
        f"The email addressed {company} with {level} personalization (score: {score:.2f}). "
        f"{'It references their sector and specific needs.' if score >= 0.5 else 'Consider adding more specific details about their business.'}"
    )


def generate_step_explanation(step: str, data: dict) -> str:
    match step:
        case "supervisor":
            route = data.get("route", [])
            return f"Query classified to use: {', '.join(route) if route else 'knowledge base only'}."
        case "leads":
            return explain_lead_selection(data.get("query", ""), data.get("leads", []))
        case "tenders":
            return explain_tender_selection(data.get("query", ""), data.get("tenders", []))
        case "intel":
            return "Sales intelligence cross-referenced leads with tenders to identify matching opportunities."
        case "email":
            return explain_email_draft(data.get("draft"))
        case _:
            return ""
