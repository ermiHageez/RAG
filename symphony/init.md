# eTech Marketing & Sales Agent — Symphony

> Master orchestration document for building an AI-powered marketing and sales agent for eTech, grounded in company data with RAG, LangGraph orchestration, MCP tooling, and n8n automation.

---

## Progress Overview

| Sprint | Status | Steps Done | Total Steps |
|--------|--------|-----------|-------------|
| **Sprint 1** — State Setup & RAG Grounding | 🟡 In Progress | 2 | 2 |
| **Sprint 2** — MCP Server Tools | 🟢 Complete | 3 | 3 |
| **Sprint 3** — Orchestration & Graph Routing | 🟢 Complete | 2 | 2 |
| **Sprint 4** — Sales & Marketing Alignment | 🟢 Complete | 2 | 2 |
| **Sprint 5** — Infrastructure Deployment | 🟢 Complete | 2 | 2 |
| **Total** | **🟢 100%** | **11** | **11** |

---

## Sprint Index

### [Sprint 1: State Setup & RAG Knowledge Base Grounding](./sprint-01-state-and-rag/)
| # | Step | File | Status |
|---|------|------|--------|
| 1.1 | Index Customer & ERP Documents into FAISS | [01-index-customer-data.md](./sprint-01-state-and-rag/01-index-customer-data.md) | 🔴 Pending |
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

---

## Legend

| Icon | Meaning |
|------|---------|
| 🔴 Pending | Not started |
| 🟡 In Progress | Actively being worked on |
| 🟢 Complete | Finished and verified |
| ⚠️ Blocked | Waiting on a dependency |

---

## Quick Reference

- **Project Root:** `/home/ermi/Desktop/RGA/RAG`
- **Data Directory:** `./data/`
- **FAISS Index:** `./faiss_store/`
- **Source Code:** `./src/`
- **Python:** 3.11
- **LLM:** Groq `llama-3.3-70b-versatile`
- **Embedding:** `all-MiniLM-L6-v2`
- **RAG Framework:** LangChain + FAISS
- **Agent Framework:** LangGraph
- **MCP Protocol:** FastMCP SDK
- **Automation:** n8n webhooks
- **Containerization:** Docker + docker-compose (3 services: MCP, agent, n8n)
