from src.agent.state import AgentState
from mcp_server.tools.tenders import fetch_active_tenders
import src.agent.store


def _score_relevance(tender: dict, vectorstore) -> float:
    text = f"{tender.get('title', '')} {tender.get('description', '')} {tender.get('procurement_category', '')}"
    results = vectorstore.query(text, top_k=1)
    if not results:
        return 0.0
    distance = results[0].get("distance", 999)
    return max(0.0, 1.0 - distance / 10.0)


def identify_tenders(state: AgentState) -> dict:
    tenders = fetch_active_tenders()

    vectorstore = src.agent.store.get_vectorstore()
    if vectorstore.index is None:
        print("[TenderNode] No FAISS index available, returning all tenders unscored")
        return {"active_tender_listings": tenders}

    scored = []
    for tender in tenders:
        score = _score_relevance(tender, vectorstore)
        scored.append({
            "title": tender.get("title", ""),
            "description": tender.get("description", ""),
            "deadline": tender.get("deadline", ""),
            "url": tender.get("url", ""),
            "category": tender.get("procurement_category", ""),
            "source": tender.get("source", ""),
            "relevance_score": round(score, 2),
        })

    scored.sort(key=lambda t: t["relevance_score"], reverse=True)
    qualified = [t for t in scored if t["relevance_score"] >= 0.3]
    print(f"[TenderNode] Found {len(tenders)} tenders, {len(qualified)} qualified (score >= 0.3)")

    return {"active_tender_listings": qualified}
