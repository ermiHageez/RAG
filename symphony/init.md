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
| **Sprint 6** — Local Multi-Agent (v3) | 🟢 Complete | 7 | 7 |
| **Sprint 7** — Sales Assistant & Doc-Gen | 🟢 Complete | 6 | 6 |
| **Sprint 8** — Marketing Pipeline | 🟢 Complete | 5 | 5 |
| **Sprint 9** — pgvector Knowledge Base & Postgres Memory | 🟡 In Progress | 0 | 6 |
| **Total** | **—** | **29** | **35** |

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
| 6.1 | LLM Factory & Embedding Migration | [01-llm-factory-and-embedding.md](./sprint-06-local-multi-agent/01-llm-factory-and-embedding.md) | 🟢 Complete |
| 6.2 | RAG Layer Refactor | [02-rag-layer-refactor.md](./sprint-06-local-multi-agent/02-rag-layer-refactor.md) | 🟢 Complete |
| 6.3 | Multi-Agent Architecture | [03-multi-agent-architecture.md](./sprint-06-local-multi-agent/03-multi-agent-architecture.md) | 🟢 Complete |
| 6.4 | LangGraph Workflow & State | [04-langgraph-workflow-and-state.md](./sprint-06-local-multi-agent/04-langgraph-workflow-and-state.md) | 🟢 Complete |
| 6.5 | Memory Layer | [05-memory-layer.md](./sprint-06-local-multi-agent/05-memory-layer.md) | 🟢 Complete |
| 6.6 | Evaluation Layer | [06-evaluation-layer.md](./sprint-06-local-multi-agent/06-evaluation-layer.md) | 🟢 Complete |
| 6.7 | Dependency Cleanup & Testing | [07-dependency-cleanup-and-testing.md](./sprint-06-local-multi-agent/07-dependency-cleanup-and-testing.md) | 🟢 Complete |

### [Sprint 7: Sales Assistant & Doc-Gen](./sprint-07-sales-assistant/)
| # | Step | File | Status |
|---|------|------|--------|
| 7.1 | Sales Engine & State Machine | [01-sales-engine.md](./sprint-07-sales-assistant/01-sales-engine.md) | 🟢 Complete |
| 7.2 | Phase Prompts | [02-sales-prompts.md](./sprint-07-sales-assistant/02-sales-prompts.md) | 🟢 Complete |
| 7.3 | Doc-Gen HTML Proposal Generator | [03-doc-gen-pdf.md](./sprint-07-sales-assistant/03-doc-gen-pdf.md) | 🟢 Complete |
| 7.4 | API Endpoints (6 new) | [04-api-endpoints.md](./sprint-07-sales-assistant/04-api-endpoints.md) | 🟢 Complete |
| 7.5 | Dependencies & Documentation | [05-dependencies-docs.md](./sprint-07-sales-assistant/05-dependencies-docs.md) | 🟢 Complete |
| 7.6 | End-to-End Testing | [06-e2e-testing.md](./sprint-07-sales-assistant/06-e2e-testing.md) | 🟢 Complete |

### [Sprint 8: Marketing Pipeline](./sprint-08-marketing/)
| # | Step | File | Status |
|---|------|------|--------|
| 8.1 | Email Template Engine | [01-template-management.md](./sprint-08-marketing/01-template-management.md) | 🟢 Complete |
| 8.2 | Email Content Generation | [02-email-content-generation.md](./sprint-08-marketing/02-email-content-generation.md) | 🟢 Complete |
| 8.3 | Campaign Status Tracking | [03-campaign-tracking.md](./sprint-08-marketing/03-campaign-tracking.md) | 🟢 Complete |
| 8.4 | Follow-Up Automation | [04-follow-up-automation.md](./sprint-08-marketing/04-follow-up-automation.md) | 🟢 Complete |
| 8.5 | Analytics Dashboard | [05-analytics-dashboard.md](./sprint-08-marketing/05-analytics-dashboard.md) | 🟢 Complete |

### [Sprint 9: pgvector Knowledge Base & Postgres Memory](./sprint-09-pgvector-migration/)
| # | Step | File | Status |
|---|------|------|--------|
| 9.1 | pgvector Connection & Schema | [01-pgvector-connection.md](./sprint-09-pgvector-migration/01-pgvector-connection.md) | 🟡 In Progress |
| 9.2 | Knowledge Base CRUD | [02-knowledge-base.md](./sprint-09-pgvector-migration/02-knowledge-base.md) | 🔴 Pending |
| 9.3 | PostgresMemoryStore | [03-postgres-memory.md](./sprint-09-pgvector-migration/03-postgres-memory.md) | 🔴 Pending |
| 9.4 | RAG Integration | [04-rag-integration.md](./sprint-09-pgvector-migration/04-rag-integration.md) | 🔴 Pending |
| 9.5 | build_agent() Wiring | [05-build-agent-wiring.md](./sprint-09-pgvector-migration/05-build-agent-wiring.md) | 🔴 Pending |
| 9.6 | Testing | [06-testing.md](./sprint-09-pgvector-migration/06-testing.md) | 🔴 Pending |

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
