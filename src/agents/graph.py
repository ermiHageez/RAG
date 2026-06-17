from typing import Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from src.agents.state import AgentState
from src.agents.supervisor import supervisor_agent
from src.agents.lead import lead_agent
from src.agents.tender import tender_agent
from src.agents.knowledge import run_knowledge_agent
from src.agents.sales_intelligence import sales_intelligence_agent
from src.agents.content import content_agent
from src.agents.approval import approval_agent
from src.memory.base import MemoryStore
from src.memory.conversation_memory import ConversationMemory
from src.memory.lead_memory import LeadMemory
from src.memory.tender_memory import TenderMemory


def _route_after_supervisor(state: AgentState) -> list[str]:
    route = state.get("route", [])
    edges = []
    if "lead" in route:
        edges.append("lead_agent")
    if "tender" in route:
        edges.append("tender_agent")
    if "knowledge" in route:
        edges.append("knowledge_agent")
    return edges or ["__end__"]


def _should_continue(state: AgentState) -> str:
    if (
        state.get("qualified_leads")
        or state.get("qualified_tenders")
        or state.get("knowledge_context")
    ):
        return "sales_intelligence_agent"
    return END


def format_n8n_payload(state: AgentState) -> dict:
    return {
        "n8n_payload": {
            "query": state.get("query"),
            "leads": state.get("qualified_leads", []),
            "tenders": state.get("qualified_tenders", []),
            "knowledge": state.get("knowledge_context", []),
            "sales_intelligence": state.get("sales_intelligence"),
            "email_draft": state.get("draft_email"),
            "requires_approval": state.get("requires_human_approval", False),
            "approval_reason": state.get("approval_reason"),
        }
    }


def build_agent(
    memory_store: Optional[MemoryStore] = None,
    knowledge_base: Optional[Any] = None,
) -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    if memory_store:
        conv_memory = ConversationMemory(memory_store, knowledge_base=knowledge_base)
        lead_memory = LeadMemory(memory_store)
        tender_memory = TenderMemory(memory_store)

        original_supervisor = supervisor_agent
        original_lead = lead_agent
        original_tender = tender_agent

        def _memory_aware_supervisor(state: AgentState) -> dict:
            result = original_supervisor(state)
            conv_memory.add_interaction(
                state.get("query", "default"),
                state.get("query", ""),
                {"route": result.get("route", [])},
            )
            return result

        def _memory_aware_lead(state: AgentState) -> dict:
            result = original_lead(state)
            leads = result.get("qualified_leads", [])
            if leads:
                existing = lead_memory.get_leads()
                lead_memory.save_leads(leads)
                result["qualified_leads"] = lead_memory.deduplicate()
            return result

        def _memory_aware_tender(state: AgentState) -> dict:
            result = original_tender(state)
            tenders = result.get("qualified_tenders", [])
            if tenders:
                tender_memory.save_tenders(tenders)
            return result

        builder.add_node("supervisor_agent", _memory_aware_supervisor)
        builder.add_node("lead_agent", _memory_aware_lead)
        builder.add_node("tender_agent", _memory_aware_tender)
    else:
        builder.add_node("supervisor_agent", supervisor_agent)
        builder.add_node("lead_agent", lead_agent)
        builder.add_node("tender_agent", tender_agent)

    builder.add_node("knowledge_agent", run_knowledge_agent)
    builder.add_node("sales_intelligence_agent", sales_intelligence_agent)
    builder.add_node("content_agent", content_agent)
    builder.add_node("approval_agent", approval_agent)
    builder.add_node("format_n8n_payload", format_n8n_payload)

    builder.add_edge(START, "supervisor_agent")

    builder.add_conditional_edges(
        "supervisor_agent",
        _route_after_supervisor,
        ["lead_agent", "tender_agent", "knowledge_agent", "__end__"],
    )

    builder.add_conditional_edges("lead_agent", _should_continue)
    builder.add_conditional_edges("tender_agent", _should_continue)
    builder.add_conditional_edges("knowledge_agent", _should_continue)

    builder.add_edge("sales_intelligence_agent", "content_agent")
    builder.add_edge("content_agent", "approval_agent")
    builder.add_edge("approval_agent", "format_n8n_payload")
    builder.add_edge("format_n8n_payload", END)

    return builder.compile()
