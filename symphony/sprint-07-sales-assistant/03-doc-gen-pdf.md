# Sprint 7.3 — Doc-Gen: HTML Proposal Generator

**Status:** 🟢 Complete

---

## Objective

Build a proposal generation module that takes LLM-written proposal markdown and renders it to a professional HTML document with print-friendly CSS. Output can be downloaded and printed to PDF from any browser. When `fpdf2` is available, native PDF generation can be added as a drop-in alternative.

---

## Tasks

- [x] Create `src/doc_gen/__init__.py` — package init
- [x] Create `src/doc_gen/generator.py`:
  - `generate(session_id: str, markdown_text: str, customer_name: str) -> str`
  - Parses markdown headings (`#`, `##`, `###`), paragraphs, bullet lists (`-` or `*`)
  - Renders to full HTML page with title page, styled sections, eTech branding
  - Title page: "Sales Proposal", customer name, date, eTech tagline
  - Footer: "Confidential — eTech S.C."
  - Saves to `data/proposals/{session_id}.html`
  - Returns file path
- [ ] (Optional) When `fpdf2` is installable: swap to native PDF generation via `fpdf2.FPDF`

---

## Acceptance Criteria

- [x] HTML generates without errors for valid markdown input
- [x] Title page shows customer name and eTech branding
- [x] Headings are styled distinctly by level
- [x] Bullet lists render correctly
- [x] Output is valid HTML (opens in any browser, printable to PDF)
- [x] Download endpoint serves with correct content type

---

## Dependencies

- ✅ Python standard library (pathlib, re for markdown parsing)
- ❌ `src/sales_assistant/prompts.py` (Sprint 7.2) — provides proposal markdown input

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/doc_gen/__init__.py` | **Create** | Package init |
| `src/doc_gen/generator.py` | **Create** | Markdown-to-HTML rendering engine |
| `src/doc_gen/templates.py` | **Create** | Stub (ready for fpdf2 when available) |
