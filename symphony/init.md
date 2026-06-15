# eTech Marketing & Sales Agent — Symphony v3

> Master orchestration document for building an AI-powered marketing and sales agent for eTech, grounded in company data with RAG, LangGraph orchestration, MCP tooling, n8n automation — now fully local with Ollama.

---

## Progress Overview

| Sprint | Status | Steps Done | Total Steps |
|--------|--------|-----------|-------------|
| **Sprint 1** — State Setup & RAG Grounding | 🟢 Complete | 2 | 2 |
| **Sprint 2** — MCP Server Tools | 🟢 Complete | 3 | 3 |
| **Sprint 3** — Orchestration & Graph Routing | 🟢 Complete | 2 | 2 |
| **Sprint 4** — Sales & Marketing Alignment | 🟢 Complete | 2 | 2 |
| **Sprint 5** — Infrastructure Deployment | 🟢 Complete | 2 | 2 |
| **Sprint 6** — Local Multi-Agent (v3) | 🔴 Pending | 0 | 7 |
| **Total** | **—** | **11** | **18** |

---

## Sprint Index

### [Sprint 1: State Setup & RAG Knowledge Base Grounding](./sprint-01-state-and-rag/)
| # | Step | File | Status |
|---|------|------|--------|
| 1.1 | Index Customer & ERP Documents into FAISS | [01-index-customer-data.md](./sprint-01-state-and-rag/01-index-customer-data.md) | 🟢 Complete |
| 1.2 | Establish LangGraph Agent State | [02-langgraph-agent-state.md](./sprint-01-state-and-rag/02-langgraph-agent-state.md) | 🟢 Complete |

### [Sprint 2: Building the Active MCP Server Tools](./sprint-02-mcp-tools/)
| # | Step | File | Status |
|---|------|------|--------|
| 2.1 | Web Search & Directory Tool | [01-web-search-tool.md](./sprint-02-mcp-tools/01-web-search-tool.md) | 🟢 Complete |
| 2.2 | Tender (ጨረታ) Monitor Tool | [02-tender-monitor-tool.md](./sprint-02-mcp-tools/02-tender-monitor-tool.md) | 🟢 Complete |
| 2.3 | n8n Hook Transmitter Tool | [03-n8n-hook-tool.md](./sprint-02-mcp-tools/03-n8n-hook-tool.md) | 🟢 Complete |

### [Sprint 3: Orchestration & Graph Routing Loops](./sprint-03-orchestration/)
| # | Step | File | Status |
|---|------|------|--------|
| 3.1 | Tender Identification Loop | [01-tender-identification.md](./sprint-03-orchestration/01-tender-identification.md) | 🟢 Complete |
| 3.2 | Corporate Lead Discovery Loop | [02-lead-discovery.md](./sprint-03-orchestration/02-lead-discovery.md) | 🟢 Complete |

### [Sprint 4: Sales & Marketing Alignment](./sprint-04-sales-marketing/)
| # | Step | File | Status |
|---|------|------|--------|
| 4.1 | Sales Force Intelligence Delivery | [01-sales-intelligence.md](./sprint-04-sales-marketing/01-sales-intelligence.md) | 🟢 Complete |
| 4.2 | Tailored Content Drafting via RAG | [02-content-drafting.md](./sprint-04-sales-marketing/02-content-drafting.md) | 🟢 Complete |

### [Sprint 5: Infrastructure Deployment](./sprint-05-deployment/)
| # | Step | File | Status |
|---|------|------|--------|
| 5.1 | MCP Host + Docker Deployment | [01-mcp-host-config.md](./sprint-05-deployment/01-mcp-host-config.md) | 🟢 Complete |
| 5.2 | End-to-End n8n + Docker Test Suite | [02-e2e-n8n-testing.md](./sprint-05-deployment/02-e2e-n8n-testing.md) | 🟢 Complete |

### [Sprint 6: Local Multi-Agent Migration (v3)](./sprint-06-local-multi-agent/)
| # | Step | File | Status |
|---|------|------|--------|
| 6.1 | LLM Factory & Embedding Migration | [01-llm-factory-and-embedding.md](./sprint-06-local-multi-agent/01-llm-factory-and-embedding.md) | 🔴 Pending |
| 6.2 | RAG Layer Refactor | [02-rag-layer-refactor.md](./sprint-06-local-multi-agent/02-rag-layer-refactor.md) | 🔴 Pending |
| 6.3 | Multi-Agent Architecture | [03-multi-agent-architecture.md](./sprint-06-local-multi-agent/03-multi-agent-architecture.md) | 🔴 Pending |
| 6.4 | LangGraph Workflow & State | [04-langgraph-workflow-and-state.md](./sprint-06-local-multi-agent/04-langgraph-workflow-and-state.md) | 🔴 Pending |
| 6.5 | Memory Layer | [05-memory-layer.md](./sprint-06-local-multi-agent/05-memory-layer.md) | 🔴 Pending |
| 6.6 | Evaluation Layer | [06-evaluation-layer.md](./sprint-06-local-multi-agent/06-evaluation-layer.md) | 🔴 Pending |
| 6.7 | Dependency Cleanup & Testing | [07-dependency-cleanup-and-testing.md](./sprint-06-local-multi-agent/07-dependency-cleanup-and-testing.md) | 🔴 Pending |

---

## Legend

| Icon | Meaning |
|------|---------|
| 🔴 Pending | Not started |
| 🟡 In Progress | Actively being worked on |
| 🟢 Complete | Finished and verified |
| ⚠️ Blocked | Waiting on a dependency |
| 🟣 Planned | Scheduled for future |

---

## Architecture (v3)

```
User Query
    ↓
SUPERVISOR AGENT (gemma3:4b)
    ↓
CONDITIONAL ROUTER
┌──────┼──────┐
▼      ▼      ▼
LEAD   TENDER KNOWLEDGE
AGENT  AGENT  AGENT
(MCP)  (MCP)  (FAISS/RAG)
└──────┼──────┘
       ▼
SALES INTELLIGENCE AGENT (qwen3:8b)
       ▼
CONTENT GENERATION AGENT (llama3.1:8b)
       ▼
APPROVAL AGENT (rule-based)
       ▼
N8N PIPELINE
```

## Quick Reference

- **Project Root:** `/home/ermi/Desktop/RGA/RAG`
- **Data Directory:** `./data/`
- **FAISS Index:** `./faiss_store/`
- **Source Code:** `./src/`
- **Python:** 3.11
- **LLM:** Ollama (gemma3:4b, qwen3:8b, llama3.1:8b)
- **Embedding:** Ollama `qwen3-embedding:4b`
- **RAG Framework:** LangChain + FAISS (refactored: `src/rag/`)
- **Agent Framework:** LangGraph (refactored: `src/agents/`)
- **MCP Protocol:** FastMCP SDK
- **Automation:** n8n webhooks
- **Memory:** JSON local store (abstracted for SQL/Postgres)
- **Containerization:** Docker + docker-compose (3 services: MCP, agent, n8n)
