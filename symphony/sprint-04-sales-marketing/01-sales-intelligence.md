# Sprint 4.1 — Sales Force Intelligence Delivery

**Status:** 🟢 Complete

---

## Objective

Design a compilation node that formats the agent's output specifically for the eTech sales force: separating cold business leads from high-priority public tenders (ጨረታ) that have hard legal submission deadlines. Output is structured for easy consumption (spreadsheet or formatted report).

---

## Tasks

- [x] Create `compile_sales_intel` LangGraph node:
  - Reads `found_leads` and `active_tender_listings` from agent state
  - Separate into two streams:
    - **Cold Leads** — company name, sector, contact info, source
    - **Priority Tenders** — title, deadline, requirements, PPA link, urgency score
  - Add urgency scoring: days until deadline (red < 7 days, amber < 30 days)
  - Format output as structured JSON ready for spreadsheet export
- [x] Generate a formatted text report suitable for sales team review
- [x] Store compiled output in state for downstream use

---

## Acceptance Criteria

- [x] Leads and tenders are correctly separated into categories
- [x] Tenders have urgency scores based on deadline proximity
- [x] Output is structured as valid JSON with clear field names
- [x] Human-readable summary is also generated
- [x] Format is compatible with Google Sheets / Excel import

---

## Dependencies

- ✅ Sprint 3.1 (Tender identification loop)
- ✅ Sprint 3.2 (Lead discovery loop)
- ✅ Sprint 1.2 (Agent state with both lead and tender lists)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/agent/nodes/sales_intel.py` | ✅ **Create** | Sales intelligence compilation node |
| `src/agent/graph.py` | ✅ **Modify** | Add sales intel node + barrier sync for parallel branches |
