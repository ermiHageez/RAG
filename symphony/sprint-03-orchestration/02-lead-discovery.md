# Sprint 3.2 — Corporate Lead Discovery Loop

**Status:** 🟢 Complete

---

## Objective

Build the LangGraph agent loop that: reads ideal target customer personas from RAG → prompts MCP web search tool to find similar, active operating companies in Ethiopia → outputs structured leads (company name, sector, location, contact) → stores them in agent state.

---

## Tasks

- [ ] Create `lead_discovery` LangGraph node:
  - Queries FAISS: "What are eTech's ideal customer profiles and target sectors?"
  - Extracts sectors (Logistics, Manufacturing, Commodities, Banking, etc.)
  - For each sector, calls `discover_ethiopian_enterprises` MCP tool
  - Aggregates results, deduplicates
- [ ] Store discovered leads in `found_leads` in agent state
- [ ] Add validation: filter out already-known customers
- [ ] Create conditional edge: if new leads found → proceed to content drafting
- [ ] Test with mock persona data

---

## Acceptance Criteria

- [ ] Node reads target personas from RAG correctly
- [ ] Web search tool is called with sector-specific queries
- [ ] Results are structured, deduplicated, and stored in state
- [ ] Graph routes correctly based on lead discovery
- [ ] Output includes company name, sector, location, and source URL

---

## Dependencies

- ✅ Sprint 1.1 (FAISS populated with customer profiles)
- ✅ Sprint 2.1 (MCP web search tool)
- ✅ Sprint 1.2 (LangGraph agent state with `found_leads`)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/agent/nodes/lead_discovery.py` | **Create** | Lead discovery node logic |
| `src/agent/graph.py` | **Modify** | Add lead discovery edges |
