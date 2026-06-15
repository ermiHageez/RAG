# Sprint 6.4 — LangGraph Workflow & State

> Define the strongly typed AgentState and compile the multi-agent LangGraph with conditional execution.

---

## Goal

Create a production LangGraph that routes through sub-agents conditionally based on the Supervisor's plan, supports parallel execution, and terminates cleanly into the N8N payload formatter.

---

## Agent State (`src/agents/state.py`)

```python
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
import operator


def _merge_lists(left: List | None, right: List | None) -> List:
    return (left or []) + (right or [])


def _override(val: Any | None, new_val: Any | None) -> Any | None:
    return new_val if new_val is not None else val


class AgentState(TypedDict):
    # Input
    query: str

    # Supervisor output
    route: Annotated[List[str], _merge_lists]

    # Sub-agent outputs
    qualified_leads: Annotated[List[Dict[str, Any]], _merge_lists]
    qualified_tenders: Annotated[List[Dict[str, Any]], _merge_lists]
    knowledge_context: Annotated[List[Dict[str, Any]], _merge_lists]

    # Sales intelligence
    sales_intelligence: Annotated[Optional[Dict[str, Any]], _override]

    # Content generation
    draft_email: Annotated[Optional[Dict[str, Any]], _override]

    # Approval
    requires_human_approval: Annotated[Optional[bool], _override]
    approval_reason: Annotated[Optional[str], _override]

    # N8N payload
    n8n_payload: Annotated[Optional[Dict[str, Any]], _override]
```

---

## Graph Structure

```
                    START
                      │
                      ▼
              SUPERVISOR AGENT
              (classify intent)
                      │
                      ▼
              CONDITIONAL ROUTER
              ┌─────────┼─────────┐
              ▼         ▼         ▼
         LEAD AG  TENDER AG  KNOWLEDGE AG
         (MCP)    (MCP)      (RAG/FAISS)
              └─────────┼─────────┘
                        ▼
              CONDITIONAL JOIN
              (skip if no route matched)
                        ▼
              SALES INTELLIGENCE AGENT
              (qwen3:8b analysis)
                        ▼
              CONTENT GENERATION AGENT
              (llama3.1:8b email)
                        ▼
              APPROVAL AGENT
              (rule-based gate)
                        ▼
              N8N PAYLOAD FORMATTER
                        ▼
                       END
```

---

## Graph Compilation (`src/agents/graph.py`)

```python
from langgraph.graph import StateGraph, START, END

def _route_after_supervisor(state: AgentState) -> list[str]:
    """Return list of nodes to execute in parallel."""
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
    """After parallel agents, decide next step."""
    if state.get("qualified_leads") or state.get("qualified_tenders") or state.get("knowledge_context"):
        return "sales_intelligence_agent"
    return END


def build_agent() -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    # Add nodes
    builder.add_node("supervisor_agent", supervisor_agent)
    builder.add_node("lead_agent", lead_agent)
    builder.add_node("tender_agent", tender_agent)
    builder.add_node("knowledge_agent", knowledge_agent)
    builder.add_node("sales_intelligence_agent", sales_intelligence_agent)
    builder.add_node("content_agent", content_agent)
    builder.add_node("approval_agent", approval_agent)
    builder.add_node("format_n8n_payload", format_n8n_payload)

    # Edges
    builder.add_edge(START, "supervisor_agent")
    builder.add_conditional_edges(
        "supervisor_agent",
        _route_after_supervisor,
        ["lead_agent", "tender_agent", "knowledge_agent", "__end__"]
    )
    builder.add_conditional_edges(
        "lead_agent", _should_continue
    )
    builder.add_conditional_edges(
        "tender_agent", _should_continue
    )
    builder.add_conditional_edges(
        "knowledge_agent", _should_continue
    )
    builder.add_edge("sales_intelligence_agent", "content_agent")
    builder.add_edge("content_agent", "approval_agent")
    builder.add_edge("approval_agent", "format_n8n_payload")
    builder.add_edge("format_n8n_payload", END)

    return builder.compile()
```

---

## N8N Payload Formatter

Port from `src/agent/nodes/base.py`:

```python
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
        }
    }
```

---

## Files Changed

| File | Change |
|---|---|
| `src/agents/state.py` | **NEW** — Strongly typed AgentState |
| `src/agents/graph.py` | **NEW** — LangGraph compilation with conditional routing |
| `src/agents/approval/approval_agent.py` | `format_n8n_payload` integration |

---

## Verification

```python
from src.agents.graph import build_agent

agent = build_agent()
result = agent.invoke({"query": "Find ICT tenders and generate outreach"})
print(result.keys())
# Expected: route, qualified_tenders, knowledge_context, draft_email, n8n_payload, ...
```
