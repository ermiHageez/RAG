# Sprint 10 — Testing Plan

## Frontend Tests
- Component rendering tests (React Testing Library)
- Form submission and validation
- Prompt injection display behavior

## Backend Tests
- `test_sanitize.py` — injection patterns are blocked, legitimate queries pass
- `test_explain.py` — explanation generation works with known inputs
- `test_copilot_routes.py` — API endpoints accept/reject correctly

## Demo Checklist
- [ ] UI loads on first visit
- [ ] User can type query and submit
- [ ] Pipeline steps render sequentially
- [ ] Approve/Edit/Reject buttons work
- [ ] Email editor allows text changes
- [ ] Final approval shows summary
- [ ] Activity feed updates
- [ ] Prompt injection attempts are blocked with user-friendly message
- [ ] Mobile-responsive (for tablet demos)
