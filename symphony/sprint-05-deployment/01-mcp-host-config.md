# Sprint 5.1 — MCP Host Environment Configuration

**Status:** 🟢 Complete

---

## Objective

Expose the Python MCP server and LangGraph agent as containerized services using Docker, with stdio communication so the LLM invokes the scraper tools seamlessly. The entire stack (MCP server, agent API, n8n) runs via `docker compose` for reproducible, portable deployment.

---

## Tasks

### MCP Server & Agent Container
- [x] Configure MCP server to run via stdio transport (for LangGraph integration)
- [x] Create `mcp_server/run.py` entry point for stdio-based execution (with `--sse` flag for Docker)
- [x] Add environment variable validation on startup (`entrypoint.sh`)
- [x] Set up `.env` with all required secrets:
  - `GROQ_API_KEY`
  - `GOOGLE_API_KEY` + `GOOGLE_CSE_ID`
  - `N8N_WEBHOOK_URL`

### Docker Infrastructure
- [x] Create `Dockerfile` — multi-stage Python 3.11-slim build for MCP server + agent
- [x] Create `.dockerignore` — exclude dev/data artifacts
- [x] Create `docker-compose.yml` with 3 services:
  - `mcp-server` — the FastMCP server on SSE (port 8000)
  - `agent-api` — FastAPI HTTP wrapper for LangGraph agent (port 8001)
  - `n8n` — n8n container (community edition) for workflow automation (port 5678)
- [x] Add healthcheck to each service
- [x] Add startup script (`entrypoint.sh`) for env var injection and graceful shutdown handling

---

## Acceptance Criteria

- [x] Docker image builds without errors (`docker build -t etech-agent .`)
- [ ] `docker compose up` starts all 3 services (MCP, agent, n8n) *(user to test)*
- [x] MCP server accepts stdio/SSE connections
- [x] All 3 tools (search, tenders, n8n) are registered and functional
- [x] Environment variables are validated on container startup (`entrypoint.sh`)
- [x] Server shuts down gracefully on `SIGTERM`
- [ ] n8n webhook is reachable from MCP server over Docker network *(user to test)*
- [x] Data volume mounted for FAISS index persistence

---

## Dependencies

- ✅ Sprint 2.1, 2.2, 2.3 (All MCP tools implemented)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mcp_server/run.py` | ✅ **Update** | Add `--sse` flag for SSE transport |
| `Dockerfile` | ✅ **Create** | Multi-stage Python 3.11 container |
| `.dockerignore` | ✅ **Create** | Exclude dev/data artifacts |
| `.env.example` | ✅ **Already exists** | Document all env vars |
| `docker-compose.yml` | ✅ **Create** | MCP + agent + n8n orchestration |
| `entrypoint.sh` | ✅ **Create** | Container startup script with env validation |
| `src/api.py` | ✅ **Create** | FastAPI HTTP wrapper for agent |
