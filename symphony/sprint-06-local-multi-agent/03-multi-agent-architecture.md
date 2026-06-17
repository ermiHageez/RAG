# Sprint 6.3 — Multi-Agent Architecture

> Build the core multi-agent system with six specialized agents orchestrated by a Supervisor.

---

## Goal

Create a modular, extensible agent system under `src/agents/` where each agent has a single responsibility and communicates via LangGraph state.

---

## Agent Directory Structure

```
src/agents/
├── __init__.py
├── llm.py                    # Model factory (Sprint 6.1)
├── state.py                  # Strongly typed AgentState
├── graph.py                  # LangGraph workflow compilation
│
├── supervisor/
│   ├── __init__.py
│   └── supervisor.py         # Intent classification, route planning
│
├── lead/
│   ├── __init__.py
│   └── lead_agent.py         # MCP search + lead qualification
│
├── tender/
│   ├── __init__.py
│   └── tender_agent.py       # MCP tender search + qualification
│
├── knowledge/
│   ├── __init__.py
│   └── knowledge_agent.py    # RAG retrieval
│
├── sales_intelligence/
│   ├── __init__.py
│   └── sales_agent.py        # Merge + analyze
│
├── content/
│   ├── __init__.py
│   └── content_agent.py      # Email generation
│
└── approval/
    ├── __init__.py
    └── approval_agent.py     # Human-in-the-loop gate
```

---

## Agent Specifications

### 1. Supervisor Agent (`src/agents/supervisor/supervisor.py`)

**Model:** `get_router_llm()` (gemma3:4b)

**Responsibility:** Classify user query → determine which sub-agents to activate.

**Logic:**
```python
def supervisor_agent(state: AgentState) -> dict:
    llm = get_router_llm()
    prompt = f"""Classify this sales/marketing query and determine required agents.

Query: {state['query']}

Available agents: lead, tender, knowledge
Respond with a JSON object: {{"route": ["agent1", "agent2", ...]}}
"""
    response = llm.invoke(prompt)
    route = parse_json(response.content)  # extract route list
    return {"route": route}
```

**Route options:**
- `["lead"]` — Lead discovery only
- `["tender"]` — Tender discovery only
- `["knowledge"]` — RAG retrieval only
- `["lead", "knowledge"]` — Combined
- `["tender", "knowledge"]` — Combined
- `["lead", "tender", "knowledge"]` — Full pipeline

### 2. Lead Agent (`src/agents/lead/lead_agent.py`)

**Model:** `get_router_llm()` (gemma3:4b)

**Responsibility:** Discover Ethiopian enterprises via MCP search, then qualify/scoring.

**Output:**
```python
{
    "qualified_leads": [
        {
            "company_name": "...",
            "sector": "...",
            "location": "...",
            "contact": "...",
            "description": "...",
            "qualification_score": 0.85,
            "reasoning": "..."
        }
    ]
}
```

### 3. Tender Agent (`src/agents/tender/tender_agent.py`)

**Model:** `get_router_llm()` (gemma3:4b)

**Responsibility:** Fetch active tenders from PPA/eGP, score relevance against company RAG context.

**Output:**
```python
{
    "qualified_tenders": [
        {
            "title": "...",
            "description": "...",
            "deadline": "...",
            "url": "...",
            "category": "...",
            "relevance_score": 0.92
        }
    ]
}
```

### 4. Knowledge Agent (`src/agents/knowledge/knowledge_agent.py`)

**Model:** None (RAG only)

**Responsibility:** Retrieve relevant context from FAISS vector store using the new `Retriever` class.

**Output:**
```python
{
    "knowledge_context": [
        {"text": "...", "source": "...", "relevance": 0.95},
        ...
    ]
}
```

### 5. Sales Intelligence Agent (`src/agents/sales_intelligence/sales_agent.py`)

**Model:** `get_reasoning_llm()` (qwen3:8b)

**Responsibility:** Merge lead + tender + knowledge outputs, analyze opportunities, produce insights.

**Output:**
```python
{
    "sales_intelligence": {
        "summary": "...",
        "opportunities": [...],
        "recommendations": [...]
    }
}
```

### 6. Content Agent (`src/agents/content/content_agent.py`)

**Model:** `get_content_llm()` (llama3.1:8b)

**Responsibility:** Generate personalized outreach emails based on sales intelligence.

**Output:**
```python
{
    "draft_email": {
        "to": "...",
        "subject": "...",
        "body": "..."
    }
}
```

### 7. Approval Agent (`src/agents/approval/approval_agent.py`)

**Model:** None (rule-based)

**Responsibility:** Determine if human approval is needed based on confidence thresholds.

**Output:**
```python
{
    "requires_human_approval": False,
    "approval_reason": "All confidence scores above threshold"
}
```

---

## Files Changed

| File | Change |
|---|---|
| `src/agents/__init__.py` | **NEW** |
| `src/agents/supervisor/supervisor.py` | **NEW** |
| `src/agents/lead/lead_agent.py` | **NEW** |
| `src/agents/tender/tender_agent.py` | **NEW** |
| `src/agents/knowledge/knowledge_agent.py` | **NEW** |
| `src/agents/sales_intelligence/sales_agent.py` | **NEW** |
| `src/agents/content/content_agent.py` | **NEW** |
| `src/agents/approval/approval_agent.py` | **NEW** |
| `src/agent/` | **DEPRECATED** — old single-agent structure |

---

## Verification

```python
from src.agents.supervisor.supervisor import supervisor_agent

state = {"query": "Find government tenders for security systems"}
result = supervisor_agent(state)
print(result["route"])
# Expected: ["tender", "knowledge"]
```
