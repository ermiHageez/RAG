<div align="center">
  <h1>eTech RAG — Marketing & Sales Agent</h1>
  <p><strong>Fully local, AI-powered B2B sales pipeline for Ethiopian enterprises</strong></p>
</div>

## Overview

eTech RAG automates the end-to-end B2B sales pipeline using a multi-agent LangGraph system with Retrieval-Augmented Generation (RAG) over internal company documents. It discovers leads, scores tenders, drafts personalized outreach emails, and delivers them via n8n workflow automation — all running locally with Ollama.

## Features

- **ML Training Pipeline** — 5-stage factory assembly line: data collection → processing → quality checks → model registry → deployment, with automatic PII redaction, deduplication, archival, and Prometheus metrics
- **Multi-Agent Pipeline** — 6 specialized LangGraph agents (supervisor, lead discovery, tender scoring, knowledge retrieval, sales intelligence, content drafting) + rule-based approval gate
- **RAG over Documents** — FAISS vector search across PDF, PPTX, XLSX, CSV, DOCX, TXT, JSON with OCR fallback for scanned content
- **Lead Discovery** — Web search (DuckDuckGo / Google fallback) to find Ethiopian companies by sector
- **Tender Scraping** — Fetch active procurement tenders from Ethiopian PPA, eGP, 2merkato, and AddisBiz
- **Email Drafting** — Personalized B2B outreach emails generated via local LLMs
- **n8n Integration** — Deliver email payloads to n8n for Gmail delivery + Google Sheets tracking
- **Sales Assistant** — 4-phase conversational sales flow (Discovery → Research → Generation → Complete)
- **Marketing Pipeline** — Template engine, campaign tracking, follow-up automation, analytics dashboard
- **Dual Vector Stores** — FAISS (documents) + pgvector (chat-derived knowledge)
- **MCP Server** — Model Context Protocol server exposing search, tender, directory, and n8n tools
- **React UI** — TypeScript frontend with MUI 6
- **Docker Support** — Multi-container deployment (API server, MCP server, n8n)
- **Evaluation Framework** — RAG precision, routing accuracy, and content quality benchmarks

## Architecture

```
User Query
    │
    ▼
Supervisor (gemma3:4b) ── routes to:
    ├── Lead Agent (qwen3:8b)      → discovers + deduplicates enterprises via MCP web search
    ├── Tender Agent (qwen3:8b)    → fetches + scores tenders via MCP tender scraper
    └── Knowledge Agent            → RAG retrieval from FAISS + pgvector
    │
    ▼
Sales Intelligence (qwen3:8b)  → cross-references leads / tenders / knowledge
    │
    ▼
Content Agent (llama3.1:8b)   → drafts personalized email
    │
    ▼
Approval Gate (rule-based)    → checks draft quality
    │
    ▼
N8N Payload ──► n8n webhook ──► Google Sheets ──► Gmail
```

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) running locally
- (Optional) [n8n](https://n8n.io) for email delivery

### Installation

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd RAG

# 2. Install dependencies (uv recommended)
uv sync
# OR: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env as needed (OLLAMA_BASE_URL defaults to http://localhost:11434)

# 4. Pull Ollama models (≈16 GB total)
ollama pull qwen3-embedding:4b
ollama pull gemma3:4b
ollama pull qwen3:8b
ollama pull llama3.1:8b

# 5. Place documents in data/ and build the FAISS index
uv run python ingest.py

# 6. Start the API server
uv run uvicorn src.api:app --host 0.0.0.0 --port 8001
```

### Test the Agent

```bash
curl -X POST http://localhost:8001/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"find bank leads and security tenders"}'
```

### Run with Docker

```bash
docker compose up -d
# Services: mcp-server (:8000), agent-api (:8001), n8n (:5678)
```

### Run the Frontend

```bash
cd ui && npm run dev
```

## API Overview

The FastAPI server exposes 40+ endpoints:

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Health | `/health`, `/config` | Server status and configuration |
| Agent | `/agent/*` (8) | Run pipeline, inspect per-agent state |
| RAG | `/rag/*` (5) | Upload, query, rebuild index, chat |
| MCP | `/mcp/*` (4) | List tools, search, tenders, directory |
| Memory | `/memory/*` (2) | Get and save conversation memory |
| Evaluation | `/evaluate/*` (3) | RAG, routing, content quality eval |
| Sales Assistant | `/sales/*` (5) | 4-phase conversational flow |
| Marketing | `/marketing/*` (11) | Campaigns, templates, analytics |

Full API docs available at `/docs` (Swagger UI) when the server is running.

## Ollama Models

| Model | Size | Role |
|-------|------|------|
| `qwen3-embedding:4b` | 2.5 GB | Embedding generation |
| `gemma3:4b` | 3.3 GB | Supervisor / router |
| `qwen3:8b` | 5.2 GB | Lead, tender, sales reasoning |
| `llama3.1:8b` | 4.9 GB | Content / email drafting |

## Environment Variables

See `.env.example` for all options. Key variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `GROQ_API_KEY` | — | Groq fallback (optional) |
| `GOOGLE_API_KEY` | — | Google Custom Search (fallback) |
| `N8N_WEBHOOK_URL` | — | n8n email delivery webhook |
| `DB_HOST` | `localhost` | PostgreSQL (pgvector) host |
| `DATASET_BUILD_INTERVAL` | `3600` | ML pipeline scheduler interval (seconds) |
| `ALERT_WEBHOOK_URL` | — | Slack webhook for pipeline alerts |
| `HNSW_EF_CONSTRUCTION` | `200` | FAISS HNSW index build quality |
| `HNSW_EF_SEARCH` | `50` | FAISS HNSW search depth |
| `VECTOR_CACHE_TTL` | `60` | Vector query cache TTL (seconds) |

## Running Tests

```bash
# All 92+ tests (mock Ollama, no external deps needed)
uv run pytest -v

# Specific test file
uv run pytest tests/test_agent_state.py -v

# With coverage
uv run pytest --cov=src tests/ -v
```

## Project Structure

```
├── src/               Python source — API, agents, RAG, memory, marketing
├── ui/                React TypeScript frontend
├── mcp_server/        MCP protocol server (stdio / SSE)
├── tests/             Test suite (16 files, 92+ tests)
├── data/              Source documents for RAG ingestion
├── faiss_store/       Built FAISS vector index
├── n8nemail/          n8n workflow and HTML email templates
├── docs/              API documentation
├── symphony/          Sprint planning and progress tracking
├── ml/                ML pipeline — data collection, processing, registry, model building
├── Dockerfile         Multi-stage Docker build
└── docker-compose.yml 3-service deployment
```

## Dependencies

- **LangGraph** — Agent orchestration
- **FAISS** — Vector similarity search
- **Ollama** — Local LLM inference
- **FastAPI** — REST API server
- **n8n** — Workflow automation (email delivery)
- **pgvector** — PostgreSQL vector extension (optional production store)

## License

MIT
