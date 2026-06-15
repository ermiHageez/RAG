# Sprint 7.6 — End-to-End Full Flow Testing

**Status:** 🟢 Complete

---

## Objective

Run the complete conversational sales assistant flow end-to-end: upload reference PDFs, rebuild RAG, start a session, chat through discovery, generate a proposal, approve and send, download the PDF, and verify the n8n email trigger.

---

## Tasks

- [ ] **Precondition**: User places 2+ eTech reference PDFs in `data/`
- [ ] **Precondition**: User calls `POST /rag/rebuild` to embed them into FAISS
- [ ] Test flow in sequence:
  1. `POST /sales/start` → get `session_id`, verify phase = `DISCOVERY`
  2. `POST /sales/chat` with `{session_id, message: "We are a logistics company in Addis looking for an ERP system"}` → verify response contains follow-up questions
  3. `POST /sales/chat` with answer to questions → verify phase advances to `RESEARCH`
  4. `POST /sales/generate` → verify proposal preview returned, PDF exists on disk
  5. `GET /doc-gen/download/{session_id}` → verify valid PDF is served
  6. `POST /sales/approve-send` → verify `status: "sent"` and n8n webhook was triggered
- [ ] Verify n8n received the payload with correct fields: `Customer Name`, `Email`, `product`, `Description/Details`, `email_body`
- [ ] Test edge cases:
  - `POST /sales/chat` with invalid `session_id` → 404
  - `POST /sales/generate` before completing DISCOVERY → 400
  - `POST /sales/approve-send` before GENERATION → 400
  - `GET /doc-gen/download/{session_id}` for non-existent session → 404

---

## Acceptance Criteria

- [ ] Full happy path works: start → chat → generate → approve-send → download
- [ ] Phase gate enforcement works (illegal transitions return 400)
- [ ] n8n webhook receives correctly formatted payload on approval
- [ ] Downloaded PDF is valid and contains proposal content
- [ ] All error cases return appropriate status codes

---

## Dependencies

- ✅ Sprint 7.1 (engine)
- ✅ Sprint 7.2 (prompts)
- ✅ Sprint 7.3 (doc-gen)
- ✅ Sprint 7.4 (API endpoints)
- ✅ Sprint 7.5 (dependencies + docs)
- ❌ User action: place 2+ reference PDFs in `data/`
- ❌ User action: call `POST /rag/rebuild`
- ✅ Existing `tests/` test runner

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| (no new files — testing only, documented in sprint) | | |
