# Sprint 8.1 — Email Template Management Engine

**Status:** 🟢 Complete

---

## Objective

Build a template management engine that maps the `product` field (Ehealth, ERP, SCCO) to the 5 existing HTML email templates in `n8nemail/`. Supports dynamic variable injection (`{{Company Name}}`, `{{AI generated paragraph}}`, `{{sales_rep_name}}`, `{{etech_tagline}}`) and provides a CRUD API for managing templates.

---

## Tasks

- [ ] Create `src/marketing/template_engine.py`:
  - Define `ProductTemplate` enum: `EHEALTH`, `ERP`, `SCCO`, `ESHARE`, `GENERAL`
  - Map each product to its HTML file in `n8nemail/`:
    - `EHEALTH` → `email3.html` (Digital Health Solutions)
    - `ERP` → `email2.html` / `email4.html` (Enterprise Solutions)
    - `SCCO` → `email5.html` (Financial & Share Systems)
    - `ESHARE` → `email.html` (eShare Management)
    - `GENERAL` → `email2.html` (General fallback)
  - `render_template(product: str, variables: dict) -> str` — loads HTML, replaces `{{placeholder}}` tokens
  - `list_templates() -> List[dict]` — returns available templates with product mapping
  - `get_template(product: str) -> str` — returns raw HTML for a product
- [ ] Create `src/marketing/__init__.py` — package init, exports
- [ ] Add API endpoint `GET /marketing/templates` — list all templates
- [ ] Add API endpoint `GET /marketing/templates/{product}` — get specific template HTML
- [ ] Add API endpoint `PUT /marketing/templates/{product}` — update template HTML

---

## Acceptance Criteria

- [ ] `render_template` correctly replaces all `{{placeholder}}` tokens in the HTML
- [ ] Each product maps to the correct HTML file
- [ ] Unknown product returns `GENERAL` fallback
- [ ] API endpoints return templates with correct product mapping
- [ ] Template files are not modified in-place (read-only by default)

---

## Dependencies

- ✅ `n8nemail/` directory with 5 HTML templates (existing)
- ✅ Python standard library (pathlib, string.Template)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/marketing/__init__.py` | **Create** | Package init |
| `src/marketing/template_engine.py` | **Create** | Template loading, product mapping, variable injection |
| `src/api.py` | **Modify** | Add `GET /marketing/templates`, `GET /marketing/templates/{product}`, `PUT /marketing/templates/{product}` |
