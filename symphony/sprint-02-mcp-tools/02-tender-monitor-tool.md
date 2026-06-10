# Sprint 2.2 — Tender (ጨረታ) Monitor Tool

**Status:** 🟢 Complete

---

## Objective

Create a specialized MCP tool `fetch_active_tenders` that scrapes or parses RSS feeds from the Ethiopian PPA (Public Procurement Authority) and eGP (Electronic Government Procurement) systems. It looks for procurement requests containing target Amharic/English strings like ጨረታ (Tender), "ERP Implementation", "System Modernization", "Database Management".

---

## Tasks

- [ ] Research PPA and eGP portal structure (URLs, RSS feeds, HTML layout)
- [ ] Implement `fetch_active_tenders(sector: str = None) -> List[Dict]`:
  - Scrape PPA/eGP portals using httpx + BeautifulSoup
  - Parse HTML/RSS for tender titles, descriptions, deadlines
  - Filter by keywords: ጨረታ, ERP, System Modernization, Database
  - Return structured: title, description, deadline, url, procurement_category
- [ ] Register tool with FastMCP server
- [ ] Add rate limiting and caching to avoid overloading portals
- [ ] Test with known tender listings

---

## Acceptance Criteria

- [ ] Tool connects to PPA/eGP and returns real tender data
- [ ] Tool correctly filters by English and Amharic keywords
- [ ] Results include deadline dates for urgency sorting
- [ ] Tool handles network errors gracefully

---

## Dependencies

- ❌ PPA/eGP portal URLs (need to be collected)
- ❌ `beautifulsoup4`, `httpx`, `lxml` (need to be added)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mcp_server/tools/tenders.py` | **Create** | PPA/eGP scraping implementation |
| `mcp_server/config.py` | **Create** | Portal URLs, keyword lists |
| `requirements.txt` | **Modify** | Add `beautifulsoup4`, `httpx`, `lxml` |
