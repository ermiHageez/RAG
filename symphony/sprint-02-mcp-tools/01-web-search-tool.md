# Sprint 2.1 — Web Search & Directory Tool

**Status:** 🟢 Complete

---

## Objective

Create a FastMCP-based MCP tool `discover_ethiopian_enterprises` that wraps a web search API. The LLM instructs it to construct search queries pairing Ethiopian industry sectors (Logistics, Manufacturing, Commodities) with keywords like "Addis Ababa corporate office" or "ERP requirements".

---

## Tasks

- [ ] Create `mcp_server/` directory for the MCP server
- [ ] Install `fastmcp` SDK
- [ ] Implement `discover_ethiopian_enterprises(query: str) -> List[Dict]`:
  - Accept natural-language sector + keyword combo from LLM
  - Call web search API (SerpAPI / DuckDuckGo / Google Custom Search)
  - Parse results into structured format: company name, sector, location, description
- [ ] Register tool with FastMCP server
- [ ] Test tool invocation with example queries

---

## Acceptance Criteria

- [ ] FastMCP server starts and registers the tool
- [ ] Tool returns structured company data for Ethiopian sectors
- [ ] Results are JSON-serializable
- [ ] Error handling for failed search requests

---

## Dependencies

- ❌ `fastmcp` package (needs to be added)
- ❌ Web search API key (SerpAPI / Google Custom Search)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mcp_server/__init__.py` | **Create** | Package init |
| `mcp_server/server.py` | **Create** | FastMCP server with tool registration |
| `mcp_server/tools/search.py` | **Create** | Web search implementation |
| `requirements.txt` | **Modify** | Add `fastmcp`, `httpx` |
