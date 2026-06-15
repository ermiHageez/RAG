# Sprint 7.5 — Dependencies & Documentation

**Status:** 🟢 Complete

---

## Objective

Ensure all external package dependencies are declared and the API documentation is updated to cover the new sales assistant + doc-gen endpoints.

---

## Tasks

- [ ] Add `fpdf2` to `requirements.txt` with version pin
- [ ] Update `docs/api_endpoints.md` with the 6 new endpoints:
  - `POST /sales/start` — request/response example
  - `POST /sales/chat` — request/response example with phase transitions
  - `POST /sales/generate` — request/response example
  - `POST /sales/approve-send` — request/response example showing n8n trigger
  - `POST /sales/reset` — request/response example
  - `GET /doc-gen/download/{session_id}` — description of file download
- [ ] Run `pip install -r requirements.txt` to verify `fpdf2` installs cleanly

---

## Acceptance Criteria

- [ ] `pip install -r requirements.txt` succeeds with no errors
- [ ] `docs/api_endpoints.md` has complete request/response examples for all new endpoints
- [ ] All existing tests still pass after dependency addition

---

## Dependencies

- ❌ Sprint 7.1 (engine)
- ❌ Sprint 7.2 (prompts)
- ❌ Sprint 7.3 (doc-gen)
- ❌ Sprint 7.4 (API endpoints)
- ✅ Existing `docs/api_endpoints.md`

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `requirements.txt` | **Modify** | Add `fpdf2>=2.7.0` |
| `docs/api_endpoints.md` | **Modify** | Document 6 new endpoints with examples |
