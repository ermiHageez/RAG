from src.agent.state import AgentState
import src.agent.store
from mcp_server.tools.search import discover_ethiopian_enterprises


DEFAULT_SECTORS = [
    "banking finance Ethiopia",
    "insurance company Ethiopia",
    "logistics transport Ethiopia",
    "manufacturing industry Ethiopia",
    "government ministry Ethiopia",
    "technology ICT Ethiopia",
]


def _extract_sectors_from_rag() -> list[str]:
    try:
        vectorstore = src.agent.store.get_vectorstore()
        if vectorstore.index is None:
            return DEFAULT_SECTORS
        results = vectorstore.query("eTech target customer sectors and industries", top_k=10)
        texts = [r["metadata"].get("text", "") for r in results if r.get("metadata")]
        sectors = set()
        sector_keywords = [
            "bank", "finance", "insurance", "logistics", "transport",
            "manufacturing", "government", "ministry", "tech", "ict",
            "telecom", "agriculture", "commodities", "energy",
        ]
        for text in texts:
            for kw in sector_keywords:
                if kw in text.lower():
                    sectors.add(f"{kw} Ethiopia")
        if sectors:
            return list(sectors)
    except Exception as e:
        print(f"[LeadDiscovery] RAG sector extraction failed: {e}")
    return DEFAULT_SECTORS


def _deduplicate(leads: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for lead in leads:
        key = lead.get("name", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique


def discover_leads(state: AgentState) -> dict:
    sectors = _extract_sectors_from_rag()
    print(f"[LeadDiscovery] Searching across {len(sectors)} sectors: {sectors}")

    all_leads = []
    for sector in sectors:
        results = discover_ethiopian_enterprises(sector)
        all_leads.extend(results)

    unique_leads = _deduplicate(all_leads)
    print(f"[LeadDiscovery] Found {len(unique_leads)} unique leads from {len(all_leads)} raw results")

    return {"found_leads": unique_leads}
