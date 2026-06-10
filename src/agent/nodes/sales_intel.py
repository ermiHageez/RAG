from datetime import datetime
from src.agent.state import AgentState


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


def _format_sales_report(intel: list) -> str:
    lines = ["=== eTech Sales Intelligence Report ===", ""]
    leads = [i for i in intel if i.get("type") == "lead"]
    tenders = [i for i in intel if i.get("type") == "tender"]
    if leads:
        lines.append(f"--- Cold Leads ({len(leads)}) ---")
        for lead in leads:
            name = lead.get("company_name", "")
            sector = lead.get("sector", "")
            contact = lead.get("contact", "N/A")
            priority = lead.get("priority", "low")
            lines.append(f"  [{priority.upper()}] {name} | {sector} | {contact}")
        lines.append("")
    if tenders:
        lines.append(f"--- Priority Tenders ({len(tenders)}) ---")
        for tender in tenders:
            lines.append(f"  [{tender['urgency'].upper()}] {tender['title']}")
            lines.append(f"    Deadline: {tender['deadline']} ({tender['days_remaining']} days)")
            lines.append(f"    URL: {tender['url']}")
            lines.append(f"    Relevance: {tender.get('relevance_score', 'N/A')}")
        lines.append("")
    lines.append("--- End of Report ---")
    return "\n".join(lines)


def build_sales_intel(state: AgentState) -> dict:
    leads = state.get("found_leads", [])
    tenders = state.get("active_tender_listings", [])
    intel = []

    for lead in leads:
        matching = [
            t for t in tenders
            if t.get("category", "").lower() in lead.get("sector", "").lower()
        ]
        intel.append({
            "type": "lead",
            "company_name": lead.get("name", ""),
            "sector": lead.get("sector", ""),
            "location": lead.get("location", ""),
            "contact": lead.get("contact", ""),
            "description": lead.get("description", ""),
            "matching_tenders": [t.get("title", "") for t in matching],
            "priority": "high" if matching else "low",
            "source": lead.get("source", "web_search"),
        })

    for tender in tenders:
        days = _days_until_deadline(tender.get("deadline", ""))
        intel.append({
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

    report = _format_sales_report(intel)
    print(f"[SalesIntel] Compiled {len(leads)} leads and {len(tenders)} tenders")
    return {"sales_intel": intel, "sales_report": report}
