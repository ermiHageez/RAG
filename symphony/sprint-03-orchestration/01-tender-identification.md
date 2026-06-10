# Sprint 3.1 — Tender Identification Loop

**Status:** 🟢 Complete

---

## Objective

Build the LangGraph agent loop that: wakes (on schedule or user command) → triggers MCP `fetch_active_tenders` → scrapes PPA portal → extracts tenders → queries RAG "Does this procurement align with eTech's ERP features?" → stores qualified tenders in agent state.

---

## Tasks

- [ ] Create `tender_identification` LangGraph node:
  - Calls `fetch_active_tenders` MCP tool
  - Iterates over returned tenders
  - For each tender, queries FAISS: "What eTech ERP features match this requirement?"
  - Scores relevance (high/medium/low) based on vector similarity
- [ ] Store qualified tenders in `active_tender_listings` in agent state
- [ ] Create conditional edge: if tenders found → proceed to content drafting node
- [ ] Add logging for each tender evaluation
- [ ] Test with mock tender data

---

## Acceptance Criteria

- [ ] Node triggers tender scraping via MCP tool
- [ ] Each tender is evaluated against RAG with a relevance score
- [ ] High-scoring tenders are stored in agent state
- [ ] Graph routes correctly based on whether tenders were found
- [ ] Full loop completes in under 60 seconds for ~20 tenders

---

## Dependencies

- ✅ Sprint 1.1 (FAISS populated with eTech ERP features)
- ✅ Sprint 2.2 (MCP tender scraping tool)
- ✅ Sprint 1.2 (LangGraph agent state with `active_tender_listings`)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/agent/nodes/tender_identification.py` | **Create** | Tender identification node logic |
| `src/agent/nodes/__init__.py` | **Create** | Package init |
| `src/agent/graph.py` | **Modify** | Add tender loop edges |
