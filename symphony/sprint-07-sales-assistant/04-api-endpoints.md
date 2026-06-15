# Sprint 7.4 — Sales & Doc-Gen API Endpoints

**Status:** 🟢 Complete

---

## Objective

Add 6 new endpoints to `src/api.py` that expose the sales assistant flow and PDF download over HTTP. Endpoints follow REST conventions and integrate with the sales engine (Sprint 7.1), prompts (Sprint 7.2), and doc-gen (Sprint 7.3).

---

## Tasks

- [ ] Add endpoints to `src/api.py`:
  - `POST /sales/start` — Creates a new session, returns `{session_id, phase: "DISCOVERY"}`
  - `POST /sales/chat` — Accepts `{session_id, message}`, runs current phase logic, returns `{phase, response, questions?, customer_info?, research_data?}`
  - `POST /sales/generate` — Accepts `{session_id}`, transitions to GENERATION, runs LLM proposal generation with RAG context, returns `{phase, proposal_preview (first 500 chars)}`
  - `POST /sales/approve-send` — Accepts `{session_id}`, marks approved, triggers n8n via MCP `trigger_n8n_marketing_pipeline`, returns `{status: "sent", email_body}`
  - `POST /sales/reset` — Accepts `{session_id}`, resets session to DISCOVERY
  - `GET /doc-gen/download/{session_id}` — Returns the generated PDF file as `application/pdf`
- [ ] Wire each endpoint to the corresponding engine method + LLM call
- [ ] Add error handling: 404 for unknown session, 400 for invalid transitions, 500 for LLM failures

---

## Acceptance Criteria

- [ ] All 6 endpoints return correct HTTP status codes (200, 404, 400)
- [ ] `/sales/start` returns a unique session ID
- [ ] `/sales/chat` advances through DISCOVERY questions
- [ ] `/sales/generate` produces proposal preview text
- [ ] `/sales/approve-send` triggers n8n webhook and returns confirmation
- [ ] `/sales/reset` clears session back to DISCOVERY
- [ ] `/doc-gen/download/{session_id}` serves a valid PDF

---

## Dependencies

- ❌ `src/sales_assistant/engine.py` (Sprint 7.1)
- ❌ `src/sales_assistant/prompts.py` (Sprint 7.2)
- ❌ `src/doc_gen/generator.py` (Sprint 7.3)
- ✅ FastAPI (already in project)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/api.py` | **Modify** | Add 6 new endpoints for sales flow + doc-gen download |
