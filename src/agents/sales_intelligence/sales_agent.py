from datetime import datetime
from src.agents.llm import get_reasoning_llm
from src.agents.state import AgentState


def _days_until_deadline(deadline_str: str) -> int:
    if not deadline_str:
        return 999
    try:
        deadline = datetime.fromisoformat(deadline_str)
        delta = deadline - datetime.now()
        return max(0, delta.days)
    except (ValueError, TypeError):
        return 999


def _urgency_label(days: int) -> str:
    if days < 7:
        return "red"
    if days < 30:
        return "amber"
    return "green"


def sales_intelligence_agent(state: AgentState) -> dict:
    leads = state.get("qualified_leads", [])
    tenders = state.get("qualified_tenders", [])
    knowledge = state.get("knowledge_context", [])

    insights = []

    for lead in leads:
        matching = [
            t for t in tenders
            if t.get("category", "").lower() in lead.get("sector", "").lower()
        ]
        insights.append({
            "type": "lead",
            "company_name": lead.get("company_name", ""),
            "sector": lead.get("sector", ""),
            "location": lead.get("location", ""),
            "contact": lead.get("contact", ""),
            "description": lead.get("description", ""),
            "matching_tenders": [t.get("title", "") for t in matching],
            "priority": "high" if matching else "low",
            "qualification_score": lead.get("qualification_score", 0.0),
        })

    for tender in tenders:
        days = _days_until_deadline(tender.get("deadline", ""))
        insights.append({
            "type": "tender",
            "title": tender.get("title", ""),
            "description": tender.get("description", ""),
            "deadline": tender.get("deadline", ""),
            "days_remaining": days,
            "urgency": _urgency_label(days),
            "url": tender.get("url", ""),
            "category": tender.get("category", ""),
            "source": tender.get("source", ""),
            "relevance_score": tender.get("relevance_score", 0.0),
        })

    llm = get_reasoning_llm()
    context_summary = (
        f"Leads: {len(leads)}, Tenders: {len(tenders)}, "
        f"Knowledge chunks: {len(knowledge)}"
    )
    prompt = (
        f"Summarize the current sales intelligence context.\n{context_summary}\n\n"
        f"Provide: 1) Key insights 2) Recommended actions 3) Priority opportunities."
    )
    try:
        response = llm.invoke(prompt)
        analysis = str(response.content)
    except Exception as e:
        print(f"[SalesIntel] LLM analysis failed ({e}), using fallback")
        analysis = f"Found {len(leads)} leads and {len(tenders)} tenders with {len(knowledge)} knowledge chunks."

    sales_intel = {
        "summary": analysis,
        "insights": insights,
        "total_leads": len(leads),
        "total_tenders": len(tenders),
        "total_knowledge": len(knowledge),
    }

    print(f"[SalesIntel] Compiled {len(insights)} insights")
    return {"sales_intelligence": sales_intel}
