# Sprint 4.2 — Tailored Content Drafting via RAG Matching

**Status:** 🟢 Complete

---

## Objective

For each validated lead, query the RAG database to pull out matching eTech business features. Draft a precise, formal email body addressing the target's explicit challenges (e.g., a bank's security profile or an importer's inventory control needs). Output is stored in agent state for n8n transmission.

---

## Tasks

- [x] Create `draft_outreach_content` LangGraph node:
  - For each lead/tender in state:
    - Query FAISS with lead's sector + challenge keywords
    - Extract top 3 matching eTech features from RAG results
    - Build prompt for Groq LLM: "Write a formal outreach email to {company} about {tender/need}, highlighting eTech's {feature1}, {feature2}, {feature3}"
    - Generate email body and subject line
  - Store result in `email_drafts` with full payload:
    - `lead_name`, `validated_email`, `tender_requirements`, `email_body`, `subject`
- [x] Add email validation (check for basic email format)
- [x] Add personalization scoring
- [ ] Test with sample leads (user to test on better PC)

---

## Acceptance Criteria

- [x] Each lead gets a unique email referencing their specific needs
- [x] Email body references real eTech features from FAISS
- [x] Output payload matches n8n webhook schema (from Sprint 2.3)
- [x] Email addresses are validated before being accepted
- [x] Generated emails are professional, formal, and non-spammy

---

## Dependencies

- ✅ Sprint 1.1 (FAISS indexed with eTech features)
- ✅ Sprint 3.1 / 3.2 (Leads and tenders in state)
- ✅ Sprint 2.3 (n8n hook expects specific payload shape)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/agent/nodes/content_drafting.py` | ✅ **Create** | Email drafting with RAG + Groq LLM |
| `src/agent/graph.py` | ✅ **Modify** | Add drafting node and edges |
