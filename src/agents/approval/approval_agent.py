from src.agents.state import AgentState


def approval_agent(state: AgentState) -> dict:
    sales_intel = state.get("sales_intelligence", {})
    draft = state.get("draft_email")
    leads = state.get("qualified_leads", [])
    tenders = state.get("qualified_tenders", [])

    requires_approval = False
    reasons = []

    if not leads and not tenders:
        reasons.append("No leads or tenders found")
        requires_approval = True

    if draft:
        score = draft.get("personalization_score", 0.0)
        if score < 0.3:
            reasons.append(f"Low personalization score: {score:.2f}")
            requires_approval = True

    if sales_intel and isinstance(sales_intel, dict):
        total = sales_intel.get("total_leads", 0) + sales_intel.get("total_tenders", 0)
        if total == 0:
            reasons.append("No actionable opportunities identified")
            requires_approval = True

    approval_reason = "; ".join(reasons) if reasons else "All confidence scores above threshold"
    print(f"[ApprovalAgent] requires_approval={requires_approval}: {approval_reason}")

    return {
        "requires_human_approval": requires_approval,
        "approval_reason": approval_reason,
    }
