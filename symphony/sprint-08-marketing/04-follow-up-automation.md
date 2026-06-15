# Sprint 8.4 — Follow-Up Sequence Automation

**Status:** 🟢 Complete

---

## Objective

Build an automated follow-up scheduler that sends reminder emails to leads who haven't responded after a configurable number of days. Follow-ups are triggered based on campaign status (`Sent` but not `Opened`/`Replied` after N days). Integrates with the template engine and content generator for follow-up-specific messaging.

---

## Tasks

- [ ] Create `src/marketing/follow_up.py`:
  - `FollowUpConfig` dataclass: `enabled`, `initial_delay_days=3`, `max_follow_ups=3`, `cadence_days=7`
  - `check_due_follow_ups() -> List[dict]` — scans campaign tracking for leads that are:
    - Status = `Sent` and `sent_date + initial_delay_days < today`
    - Status = `FollowUp_N` and `last_follow_up_date + cadence_days < today`
    - `follow_up_count < max_follow_ups`
  - `send_follow_up(session_id, follow_up_number) -> bool` — generates follow-up email body (different tone: "just checking in"), renders template, sends via n8n hook
  - `get_follow_up_schedule(session_id) -> dict` — returns past/upcoming follow-ups for a lead
- [ ] Add API endpoints:
  - `POST /marketing/follow-up/check` — trigger manual check for due follow-ups
  - `GET /marketing/follow-up/schedule/{session_id}` — get follow-up schedule for a lead
  - `PUT /marketing/follow-up/config` — update follow-up configuration
- [ ] Follow-up email body uses softer tone: "Checking in...", "Thought this might be relevant...", "Happy to schedule a call..."

---

## Acceptance Criteria

- [ ] Follow-up check correctly identifies leads due for follow-up
- [ ] Max follow-ups cap is enforced (no infinite emails)
- [ ] Follow-up email body has distinct tone from initial outreach
- [ ] Schedule endpoint returns clear timeline of past/future follow-ups
- [ ] Config can be updated via API

---

## Dependencies

- ✅ Sprint 8.1 (template engine — reuses product templates)
- ✅ Sprint 8.2 (content generator — follow-up-specific prompts)
- ❌ Sprint 8.3 (campaign tracking — reads `sent_date`, `follow_up_count`, `last_follow_up_date`)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/marketing/follow_up.py` | **Create** | Follow-up scheduler, check, and send logic |
| `src/api.py` | **Modify** | Add follow-up API endpoints |
