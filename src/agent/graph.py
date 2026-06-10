from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from src.agent.state import AgentState
from src.agent.nodes import (
    retrieve_context,
    discover_leads,
    identify_tenders,
    build_sales_intel,
    draft_emails,
    format_n8n_payload,
)


def _check_for_data(state: AgentState) -> str:
    if state.get("found_leads") or state.get("active_tender_listings"):
        return "build_sales_intel"
    return END


def build_agent() -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("discover_leads", discover_leads)
    builder.add_node("identify_tenders", identify_tenders)
    builder.add_node("check_data", lambda state: {})
    builder.add_node("build_sales_intel", build_sales_intel)
    builder.add_node("draft_emails", draft_emails)
    builder.add_node("format_n8n_payload", format_n8n_payload)

    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "discover_leads")
    builder.add_edge("retrieve_context", "identify_tenders")
    builder.add_edge("discover_leads", "check_data")
    builder.add_edge("identify_tenders", "check_data")
    builder.add_conditional_edges("check_data", _check_for_data)
    builder.add_edge("build_sales_intel", "draft_emails")
    builder.add_edge("draft_emails", "format_n8n_payload")
    builder.add_edge("format_n8n_payload", END)

    return builder.compile()
