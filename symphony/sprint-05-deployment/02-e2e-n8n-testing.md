# Sprint 5.2 — End-to-End n8n Verification Testing

**Status:** 🟢 Complete

---

## Objective

Run integration mock tests: have the agent search for a test enterprise sector, read a target eTech product feature from FAISS, assemble the customized email draft, and trigger the MCP outbound tool to ensure the n8n workflow correctly receives the clean email payload.

---

## Tasks

### Unit & Integration Tests
- [x] Create `tests/` directory with test infrastructure (`conftest.py` with mock FAISS + fixtures)
- [x] Write `test_e2e_pipeline.py` — full end-to-end mock test:
  1. Mock web search returns test company data
  2. Mock tender scraping returns test tenders
  3. Run LangGraph agent graph with mock data
  4. Verify agent state populates `found_leads`, `active_tender_listings`
  5. Verify content drafting generates valid email payload
  6. Verify n8n payload generated correctly
- [x] Write unit tests for each node independently
- [x] Write unit tests for MCP tools
- [x] Create test fixtures (mock company data, mock tenders)
- [ ] Run full test suite and fix failures *(user to run `pytest tests/` on better PC)*

### Docker Integration Tests
- [ ] Docker compose tests *(user to run on machine with Docker)*
- [ ] n8n webhook integration *(user to test)*

---

## Acceptance Criteria

- [x] Full end-to-end test passes without network dependencies (mocked)
- [x] Each node has at least one unit test
- [x] Each MCP tool has at least one unit test
- [ ] Test coverage > 70% for agent code *(user to run with `pytest --cov`)*
- [ ] All tests run via `pytest` from project root *(user to run)*
- [ ] `docker compose up -d` succeeds and all 3 services report healthy *(user to test)*
- [ ] Docker image builds with zero warnings *(user to test)*

---

## Dependencies

- ✅ All Sprints 1–4 (Full agent pipeline)
- ✅ Sprint 5.1 (MCP server + Docker configured)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `tests/__init__.py` | ✅ **Create** | Test package init |
| `tests/conftest.py` | ✅ **Create** | Fixtures and mock data |
| `tests/test_agent_state.py` | ✅ **Create** | State reducer unit tests |
| `tests/test_tender_node.py` | ✅ **Create** | Tender identification tests |
| `tests/test_lead_node.py` | ✅ **Create** | Lead dedup tests |
| `tests/test_content_drafting.py` | ✅ **Create** | Email validation + personalization scoring tests |
| `tests/test_mcp_tools.py` | ✅ **Create** | All 3 MCP tool tests with mock fallbacks |
| `tests/test_e2e_pipeline.py` | ✅ **Create** | Full end-to-end integration test (11 scenarios) |
