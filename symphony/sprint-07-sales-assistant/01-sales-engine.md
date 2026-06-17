# Sprint 7.1 — Sales Assistant Engine & State Machine

**Status:** 🟢 Complete

---

## Objective

Build a 4-phase conversational state machine (`DISCOVERY → RESEARCH → GENERATION → COMPLETE`) that drives the sales assistant flow. Each phase has clear entry conditions, actions, and transitions. The engine manages per-session state (session ID, current phase, collected data, generated artifacts) and enforces the conversation flow.

---

## Tasks

- [ ] Create `src/sales_assistant/engine.py`:
  - Define `SalesPhase` enum: `DISCOVERY`, `RESEARCH`, `GENERATION`, `COMPLETE`
  - Define `SalesSession` dataclass: `session_id`, `phase`, `customer_info`, `research_data`, `proposal_text`, `proposal_pdf_path`, `email_body`, `approved`
  - Implement `SalesEngine` class:
    - `create_session() -> str` — generates UUID session ID, stores in dict
    - `get_session(session_id) -> SalesSession`
    - `transition(session_id, target_phase) -> bool` — validates legal transitions
    - `reset_session(session_id)` — clears session data
  - Legal transitions: DISCOVERY → RESEARCH → GENERATION → COMPLETE (no skips, no backwards)
- [ ] Create `src/sales_assistant/__init__.py` — export `SalesEngine`, `SalesPhase`, `SalesSession`
- [ ] Implement in-memory session store (dict) with optional JSON persistence path

---

## Acceptance Criteria

- [ ] Engine creates sessions with UUID and default DISCOVERY phase
- [ ] Illegal transitions (e.g. DISCOVERY → GENERATION) are rejected
- [ ] Legal forward transitions succeed and update phase
- [ ] `reset_session` clears state back to DISCOVERY
- [ ] Sessions are isolated (no cross-session data leaks)

---

## Dependencies

- ✅ Python 3.11+ (no external packages needed for state machine)
- ❌ `src/sales_assistant/prompts.py` (Sprint 7.2, needed by GENERATION phase)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/sales_assistant/__init__.py` | **Create** | Package init, exports |
| `src/sales_assistant/engine.py` | **Create** | 4-phase state machine, session store, transitions |
