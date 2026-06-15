from src.agents.state import AgentState
from mcp_server.tools.tenders import fetch_active_tenders
from src.rag.vectorstore import get_vectorstore


def _score_relevance(tender: dict, vectorstore) -> float:
    text = (
        f"{tender.get('title', '')} "
        f"{tender.get('description', '')} "
        f"{tender.get('procurement_category', '')}"
    )
    try:
        results = vectorstore.query(text, top_k=1)
        if results:
            distance = results[0].get("distance", 999)
            return max(0.0, 1.0 - distance / 10.0)
    except Exception:
        pass
    return 0.0


def tender_agent(state: AgentState) -> dict:
    tenders = fetch_active_tenders()

    vectorstore = get_vectorstore()
    if vectorstore.index is None:
        print("[TenderAgent] No FAISS index, returning all unscored")
        return {"qualified_tenders": tenders}

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
    print(f"[TenderAgent] {len(tenders)} total, {len(qualified)} qualified")

    return {"qualified_tenders": qualified}
