# Sprint 7.2 — Sales Assistant Phase Prompts

**Status:** 🟢 Complete

---

## Objective

Design phase-specific LLM prompts that drive each step of the conversational sales flow. Prompts are templated strings that accept session context (customer info, research results, RAG references) and produce structured outputs (questions, summaries, proposal markdown, email body).

---

## Tasks

- [ ] Create `src/sales_assistant/prompts.py`:
  - `DISCOVERY_PROMPT` — Generates follow-up questions to gather customer info. Input: `{existing_info}`. Output: natural-language questions (max 3).
  - `RESEARCH_PROMPT` — Summarizes MCP directory search results + web data into structured customer profile. Input: `{customer_name}`, `{mcp_results}`. Output: JSON with `company`, `sector`, `size`, `needs`, `contacts`, `source`.
  - `GENERATION_PROMPT` — Writes proposal in markdown using RAG reference docs as style templates. Input: `{customer_profile}`, `{rag_style_refs}`, `{etech_profile}`. Output: full proposal markdown (title page, executive summary, solution, pricing, timeline, next steps).
  - `EMAIL_PROMPT` — Drafts a concise sales email from the proposal. Input: `{proposal}`, `{customer_contact}`. Output: plaintext email body with subject line.

---

## Acceptance Criteria

- [ ] Each prompt is a self-contained template string with clear `{placeholders}`
- [ ] Discovery prompt generates relevant, contextual questions
- [ ] Research prompt produces structured JSON output parseable by the engine
- [ ] Generation prompt produces complete proposal markdown (1000+ words)
- [ ] Email prompt produces a professional sales email under 200 words

---

## Dependencies

- ❌ `src/sales_assistant/engine.py` (Sprint 7.1) — prompts are consumed by engine phases
- ❌ RAG system — `rag_style_refs` comes from `POST /rag/query`

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/sales_assistant/prompts.py` | **Create** | Phase-specific LLM prompt templates |
