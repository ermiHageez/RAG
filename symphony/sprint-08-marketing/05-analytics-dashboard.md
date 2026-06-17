# Sprint 8.5 — Marketing Analytics & Dashboard

**Status:** 🟢 Complete

---

## Objective

Build a campaign analytics module that aggregates tracking data into actionable metrics for the sales team. Provides exportable reports (JSON/CSV) broken down by product, status, and time period. Serves as the data source for a future frontend dashboard.

---

## Tasks

- [ ] Create `src/marketing/analytics.py`:
  - `get_campaign_summary(start_date=None, end_date=None) -> dict`:
    - Total leads contacted
    - Emails sent, opened, replied
    - Meetings booked
    - Conversion rates: `replied/sent`, `meeting_booked/sent`
  - `get_product_breakdown() -> list[dict]`:
    - Per product: sent, opened, replied, booked, conversion %
  - `get_timeline(days=30) -> list[dict]`:
    - Daily counts of sent, opened, replied events
  - `export_report(format="json") -> str`:
    - Full report in JSON or CSV format
  - `get_top_performing_template() -> dict`:
    - Which template has the highest reply rate
- [ ] Add API endpoints:
  - `GET /marketing/analytics/summary` — campaign summary
  - `GET /marketing/analytics/product-breakdown` — per-product metrics
  - `GET /marketing/analytics/timeline?days=30` — daily event timeline
  - `GET /marketing/analytics/export?format=csv` — download full report

---

## Acceptance Criteria

- [ ] Summary endpoint returns all key metrics
- [ ] Product breakdown shows correct per-product data
- [ ] Timeline returns daily aggregated counts
- [ ] CSV export downloads as properly formatted CSV
- [ ] Top-performing template is correctly identified from reply rates
- [ ] All endpoints work with no data (graceful empty response)

---

## Dependencies

- ✅ Sprint 8.3 (campaign tracking — source of all analytics data)
- ✅ Python standard library (csv, datetime, collections)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/marketing/analytics.py` | **Create** | Analytics aggregation, reporting, export |
| `src/api.py` | **Modify** | Add analytics API endpoints |
