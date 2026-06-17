# Sprint 2.3 — n8n Hook Transmitter Tool

**Status:** 🟢 Complete

---

## Objective

Create an outbound MCP tool `trigger_n8n_marketing_pipeline` that sends a clean JSON payload to an n8n webhook. The payload contains: Lead Name, Scraped Tender Requirements, Validated Email, and the AI-generated Email Body. This connects the agent's output to n8n's email/messaging automation.

---

## Tasks

- [ ] Implement `trigger_n8n_marketing_pipeline(payload: Dict) -> Dict`:
  - Accept `{lead_name, tender_requirements, validated_email, email_body}`
  - POST JSON to configured n8n webhook URL
  - Handle success/failure response
  - Return webhook acknowledgment
- [ ] Register tool with FastMCP server
- [ ] Add retry logic with exponential backoff
- [ ] Add payload validation before sending
- [ ] Test with mock payload against n8n test webhook

---

## Acceptance Criteria

- [ ] Tool sends HTTP POST with correct payload structure
- [ ] Tool returns the n8n webhook response
- [ ] 3 retry attempts on failure with backoff
- [ ] Payload validation catches missing required fields
- [ ] Configurable webhook URL via environment variable

---

## Dependencies

- ❌ n8n webhook URL (needs to be created in n8n)
- ❌ `httpx` (needs to be added)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mcp_server/tools/n8n_hook.py` | **Create** | n8n webhook transmitter |
| `mcp_server/config.py` | **Modify** | Add webhook URL config |
| `.env.example` | **Create** | Document required env vars |
