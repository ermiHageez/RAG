# Sprint 8.2 — Email Body Content Generation

**Status:** 🟢 Complete

---

## Objective

Build product-specific LLM prompts that generate the personalized email body paragraph for each template. This is the dynamic `{{AI generated paragraph}}` section that appears after "eTech S.C.," in the emails — currently filled by n8n's Gemini node. We replace that with our own LLM (llama3.1:8b) for full local control.

---

## Tasks

- [ ] Create `src/marketing/content_generator.py`:
  - `generate_email_body(product: str, customer_name: str, customer_needs: str, etech_products: list) -> str`
  - Product-specific prompt templates:
    - **EHEALTH**: Focus on EHR, ambulance tracking, pharmacy POS, patient records
    - **ERP**: Focus on finance, inventory, HR, procurement automation
    - **SCCO/ESHARE**: Focus on share registry, dividend processing, banking integrations
    - **GENERAL**: Focus on eTech's full ecosystem
  - Each prompt includes: customer context, eTech capabilities, call-to-action
  - Output: 2–3 sentence paragraph (matching the n8n Gemini slot)
- [ ] Integrate with Ollama `llama3.1:8b` via existing LLM factory
- [ ] Add `generate_email_body` call in the sales assistant approval flow (`POST /sales/approve-send`)

---

## Acceptance Criteria

- [ ] Generated paragraph is 2–3 sentences, professional tone
- [ ] Content references both customer needs AND eTech product features
- [ ] Product-specific prompts produce relevant output for each category
- [ ] Output fits naturally into the `{{AI generated paragraph}}` slot in HTML templates
- [ ] LLM call uses existing Ollama infrastructure (no new dependencies)

---

## Dependencies

- ✅ Existing Ollama + LLM factory in project
- ❌ Sprint 8.1 — `template_engine.py` (the rendered template includes the generated body)
- ❌ Sprint 7.4 — sales assistant approval endpoint (integration point)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/marketing/content_generator.py` | **Create** | Product-specific LLM prompts for email body generation |
| `src/api.py` | **Modify** | Integrate content generation into approval flow |
