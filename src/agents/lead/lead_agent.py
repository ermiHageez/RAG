from src.agents.llm import get_router_llm
from src.agents.state import AgentState
from mcp_server.tools.search import discover_ethiopian_enterprises

DEFAULT_SECTORS = [
    "banking finance Ethiopia",
    "insurance company Ethiopia",
    "logistics transport Ethiopia",
    "manufacturing industry Ethiopia",
    "government ministry Ethiopia",
    "technology ICT Ethiopia",
]


def _deduplicate(leads: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for lead in leads:
        key = lead.get("name", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique


def lead_agent(state: AgentState) -> dict:
    query = state.get("query", "")

    sectors = DEFAULT_SECTORS
    if "sector" in query.lower() or "industry" in query.lower():
        llm = get_router_llm()
        prompt = f"Extract the target sector from this query. Return only one word: '{query}'"
        try:
            resp = llm.invoke(prompt)
            sector = str(resp.content).strip().lower()
            if sector:
                sectors = [f"{sector} Ethiopia"]
        except Exception:
            pass

    print(f"[LeadAgent] Searching sectors: {sectors}")
    all_leads = []
    for sector in sectors:
        try:
            results = discover_ethiopian_enterprises(sector)
            all_leads.extend(results)
        except Exception as e:
            print(f"[LeadAgent] Search failed for {sector}: {e}")

    unique_leads = _deduplicate(all_leads)
    print(f"[LeadAgent] Found {len(unique_leads)} unique leads")

    qualified = []
    for lead in unique_leads:
        qualified.append({
            "company_name": lead.get("name", ""),
            "sector": lead.get("sector", ""),
            "location": lead.get("location", ""),
            "contact": lead.get("contact", ""),
            "description": lead.get("description", ""),
            "source": lead.get("source", "web_search"),
            "qualification_score": 0.7,
        })

    return {"qualified_leads": qualified}
