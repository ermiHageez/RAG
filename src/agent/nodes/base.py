from src.agent.state import AgentState


def retrieve_context(state: AgentState) -> dict:
    query = state.get("query", "")
    return {
        "rag_context": [f"[placeholder] RAG context for: {query}"],
    }


def format_n8n_payload(state: AgentState) -> dict:
    drafts = state.get("email_drafts", [])
    individual_payloads = []
    for draft in drafts:
        individual_payloads.append({
            "lead_name": draft.get("lead_name", ""),
            "tender_requirements": draft.get("tender_requirements", ""),
            "validated_email": draft.get("validated_email", ""),
            "email_body": draft.get("email_body", ""),
        })
    return {
        "n8n_payload": {
            "batch": individual_payloads,
            "total": len(individual_payloads),
        }
    }
