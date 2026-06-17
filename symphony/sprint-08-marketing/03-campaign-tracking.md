# Sprint 8.3 — Campaign Status Tracking (Google Sheets)

**Status:** 🟢 Complete

---

## Objective

Integrate with Google Sheets to track campaign status across the email pipeline. Mirrors the `Customer Email Status Tracking` sheet that the n8n workflow reads from. Provides API endpoints to read campaign status, update lead progress, and sync with n8n's sheet-based trigger.

---

## Tasks

- [ ] Create `src/marketing/sheets_tracker.py`:
  - `init_sheet()` — validate Google Sheets API access (service account or API key)
  - `add_lead(session_id, customer_name, email, product, status="New")` — add row
  - `update_status(session_id, new_status)` — update status: `New` → `Sent` → `Opened` → `Replied` → `Meeting Booked`
  - `get_campaign_stats() -> dict` — counts by status and product
  - `get_leads_by_status(status: str) -> list` — filter leads
- [ ] Add API endpoints:
  - `GET /marketing/campaign/stats` — campaign statistics
  - `GET /marketing/campaign/leads?status=New` — filter leads by status
  - `PUT /marketing/campaign/leads/{session_id}/status` — update lead status
- [ ] Mock mode: when no Google Sheets credentials, fall back to local JSON store (`data/campaign_tracking.json`)

---

## Acceptance Criteria

- [ ] Leads are written to Google Sheet (or local JSON fallback)
- [ ] Status transitions follow valid sequence (no skips: New→Sent, not New→Meeting Booked)
- [ ] Campaign stats return correct counts
- [ ] Filter by status returns matching leads only
- [ ] Mock mode works without Google API credentials

---

## Dependencies

- ❌ Google Sheets API credentials (optional — mock mode available)
- ✅ Python standard library (json, pathlib for mock mode)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/marketing/sheets_tracker.py` | **Create** | Google Sheets + local JSON campaign tracking |
| `src/api.py` | **Modify** | Add campaign tracking endpoints |
