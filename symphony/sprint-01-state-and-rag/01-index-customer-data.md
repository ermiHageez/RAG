# Sprint 1.1 — Index Customer & ERP Documents into FAISS

**Status:** 🔴 Pending

---

## Objective

Upload and index eTech's target customer list, existing client success profiles, and ERP system feature sheets into the FAISS vector database. This grounds the agent in structured knowledge about who eTech sells to and what eTech's products do.

---

## Tasks

- [ ] Collect and place into `./data/`:
  - Target customer list (CSV/Excel) — company names, sectors, contacts
  - Client success profiles (PDF/DOCX) — past implementations, testimonials
  - ERP feature sheets (PDF/DOCX) — core modules, HR, inventory, compliance
- [ ] Run the existing RAG pipeline to rebuild the FAISS index with new data
- [ ] Verify that queries like _"What ERP features does eTech offer for manufacturing?"_ return relevant chunks
- [ ] Ensure the index persists correctly in `./faiss_store/`

---

## Acceptance Criteria

- [ ] `data/` contains at least 3 new structured files (customer list, client profile, ERP sheets)
- [ ] FAISS index rebuilds without errors
- [ ] Vector search returns relevant results for eTech-specific queries
- [ ] Metadata is correctly stored (source file, page number)

---

## Dependencies

- ✅ Existing RAG pipeline (`data_loader.py`, `embedding.py`, `vectorstore.py`, `search.py`)
- ❌ Source data files (need to be collected/created)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `data/customer-list.csv` | **Create** | Ideal customer profiles with sectors, size, location |
| `data/client-profiles/` | **Create** | Success stories, case studies |
| `data/erp-features/` | **Create** | Feature specs per module |
