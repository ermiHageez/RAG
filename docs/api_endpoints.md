# eTech Multi-Agent API — Postman Collection

**Base URL:** `http://0.0.0.0:8001`

---

## 1. Health & Config

### `GET /health`
Check if server is running.

**Response:**
```json
{
    "status": "ok",
    "timestamp": "2026-06-13T10:30:00"
}
```

### `GET /config`
Show configured models and service status.

**Response:**
```json
{
    "models": {
        "router": "gemma3:4b",
        "reasoning": "qwen3:8b",
        "content": "llama3.1:8b",
        "embedding": "qwen3-embedding:4b"
    },
    "data_dir": "data",
    "faiss_dir": "faiss_store",
    "google_cse_configured": false,
    "n8n_configured": false
}
```

---

## 2. MCP Tool Endpoints (Data Sources)

### `GET /mcp/tools`
List all available MCP tools.

### `POST /mcp/search`
Search Ethiopian companies via DuckDuckGo web search.

**Body (raw JSON):**
```json
{
    "query": "bank Ethiopia",
    "max_results": 5
}
```

**Response:**
```json
{
    "success": true,
    "results": [
        {
            "name": "Commercial Bank of Ethiopia",
            "sector": "Finance",
            "location": "Ethiopia",
            "description": "...",
            "contact": "",
            "link": "https://..."
        }
    ],
    "total": 5
}
```

### `POST /mcp/tenders`
Scrape business opportunities and tenders from 2merkato.com and addisbiz.com.

**Body (raw JSON):**
```json
{
    "query": "",
    "max_results": 5
}
```

Keyword filter (searches title + description, falls back to all results if no match):
```json
{
    "query": "bank",
    "max_results": 5
}
```

**Response:**
```json
{
    "success": true,
    "results": [
        {
            "title": "Ethiopia: ECMA Licenses United Capital...",
            "description": "The Ethiopian Capital Market Authority...",
            "deadline": "",
            "url": "https://www.2merkato.com/news/...",
            "procurement_category": "General",
            "source": "2merkato.com"
        }
    ],
    "total": 20
}
```

### `POST /mcp/directory`
Scrape company directory listings from 2merkato.com, addisbiz.com, and ethyp.com. Returns company name, sector, location, phone, link.

**Body (raw JSON):**
```json
{
    "query": "tech",
    "max_results": 5
}
```

**Response:**
```json
{
    "success": true,
    "results": [
        {
            "name": "Marakisoft Technologies PLC",
            "sector": "Technology",
            "location": "Addis Ababa, Ethiopia",
            "description": "Leading Ethiopian software development...",
            "phone": "+251 115 54 4...",
            "link": "https://www.ethyp.com/company/...",
            "source": "ethyp.com"
        }
    ],
    "total": 5
}
```

---

## 3. Agent Pipeline Endpoints

All agent endpoints accept the same body format:

**Body (raw JSON):**
```json
{
    "query": "find banks in Ethiopia"
}
```

### `POST /agent/supervisor`
Route a query to the appropriate agent (lead/tender/knowledge).

### `POST /agent/leads`
Run lead search agent — discovers Ethiopian companies via web search.

### `POST /agent/tenders`
Run tender search agent — finds relevant tenders from scraped data.

### `POST /agent/knowledge`
Run knowledge retrieval agent — queries the RAG vector store.

### `POST /agent/sales-intel`
Generate sales intelligence from collected leads and tenders.

### `POST /agent/content`
Draft personalized email content for a lead.

### `POST /agent/approval`
Check if content requires human approval before sending.

### `POST /agent/run`
Run the full agent pipeline end-to-end (supervisor → agents → sales intel → content → approval → n8n payload).

**Body:**
```json
{
    "query": "find banks and tender opportunities in Ethiopia for ERP systems"
}
```

**Response (QueryResponse):**
```json
{
    "success": true,
    "result": {
        "query": "...",
        "route": ["lead", "tender"],
        "qualified_leads": [...],
        "qualified_tenders": [...],
        "knowledge_context": [...],
        "sales_intelligence": {...},
        "draft_email": "...",
        "requires_human_approval": false,
        "approval_reason": null,
        "n8n_payload": {...}
    }
}
```

---

## 4. RAG Endpoints

### `GET /rag/status`
Check if the FAISS vector store is loaded.

**Response:**
```json
{
    "active": true,
    "entries": 1,
    "dimension": 2560,
    "path": "faiss_store"
}
```

### `POST /rag/query`
Query the RAG vector store for relevant documents.

**Body (raw JSON):**
```json
{
    "query": "what does eTech do",
    "top_k": 5
}
```

### `POST /rag/rebuild`
Rebuild the FAISS index from all documents in the `data/` directory.

**Response:**
```json
{
    "success": true,
    "entries": 5
}
```

---

## 5. Memory Endpoints

### `GET /memory/{memory_type}?session_id=default`
Retrieve conversation or custom memory history.

**Examples:**
- `GET /memory/conversation?session_id=user1`
- `GET /memory/custom?session_id=test`

### `POST /memory/{memory_type}`
Save an interaction to memory.

**Body (raw JSON):**
```json
{
    "session_id": "user1",
    "query": "find banks",
    "response": {"route": ["lead"]}
}
```

---

## 6. Evaluation Endpoints

All evaluation endpoints accept the same format with optional `test_cases`.

### `POST /evaluate/rag`
Evaluate RAG retrieval precision.

**Body (raw JSON):**
```json
{
    "test_cases": [
        {
            "name": "eTech_capabilities",
            "input": "What does eTech do?",
            "output": [{"text": "eTech provides ERP solutions"}],
            "expected": null
        }
    ]
}
```

### `POST /evaluate/routing`
Evaluate agent routing accuracy.

**Body:**
```json
{
    "test_cases": [
        {
            "name": "bank_query",
            "input": "find banks in Ethiopia",
            "output": {"route": ["lead"]},
            "expected": null
        }
    ]
}
```

### `POST /evaluate/content`
Evaluate email content quality.

**Body:**
```json
{
    "test_cases": [
        {
            "name": "email_quality",
            "input": "Write email to Test Corp",
            "output": {"email_body": "Dear Test Corp..."},
            "expected": null
        }
    ]
}
```

---

---

## 7. Sales Assistant Endpoints (Conversational Flow)

### `POST /sales/start`
Create a new sales session. Returns a unique session ID and starts in DISCOVERY phase.

**Response:**
```json
{
    "session_id": "uuid-string",
    "phase": "DISCOVERY"
}
```

### `POST /sales/chat`
Send a message in the current session. Phase-aware: DISCOVERY asks questions, RESEARCH summarizes MCP data, GENERATION/COMPLETE return status.

**Body:**
```json
{
    "session_id": "uuid-string",
    "message": "We are a logistics company in Addis looking for an ERP system"
}
```

**Response (DISCOVERY phase):**
```json
{
    "session_id": "uuid-string",
    "phase": "DISCOVERY",
    "response": "Here are some questions to help me understand your needs better.",
    "questions": [
        "How many employees does your company have?",
        "What are your top 3 pain points in logistics operations?",
        "What is your timeline for implementation?"
    ],
    "customer_info": {
        "last_response": "We are a logistics company..."
    }
}
```

### `POST /sales/generate`
Generate the proposal PDF. Requires session to be in GENERATION phase.

**Body:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "session_id": "uuid-string",
    "phase": "GENERATION",
    "proposal_preview": "# Executive Summary\n\nThis proposal outlines...",
    "proposal_pdf_path": "data/proposals/uuid-string.pdf"
}
```

### `POST /sales/approve-send`
Approve the proposal and trigger the n8n marketing pipeline. Transitions session to COMPLETE.

**Body:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "session_id": "uuid-string",
    "status": "sent",
    "email_body": "Dear Customer, ...",
    "n8n_response": {
        "status": "mock_acknowledged",
        "payload": {...}
    }
}
```

### `POST /sales/reset`
Reset a session back to DISCOVERY phase, clearing all collected data.

**Body:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "session_id": "uuid-string",
    "phase": "DISCOVERY",
    "reset": true
}
```

### `GET /doc-gen/download/{session_id}`
Download the generated proposal PDF.

**Response:** `application/pdf` file download.

---

## 8. Marketing Endpoints

### Template Management

#### `GET /marketing/templates`
List all available email templates with product mapping.

**Response:**
```json
{
    "templates": [
        {"product": "Ehealth", "filename": "email3.html", "exists": true},
        {"product": "ERP", "filename": "email2.html", "exists": true},
        {"product": "SCCO", "filename": "email5.html", "exists": true},
        {"product": "eShare", "filename": "email.html", "exists": true},
        {"product": "General", "filename": "email4.html", "exists": true}
    ]
}
```

#### `GET /marketing/templates/{product}`
Get the raw HTML of a specific product template.

#### `PUT /marketing/templates/{product}`
Update the HTML template for a product.

**Body:**
```json
{
    "html": "<!DOCTYPE html><html>..."
}
```

### Campaign Tracking

#### `GET /marketing/campaign/stats`
Get campaign statistics (total leads, by-status breakdown, by-product breakdown, conversion rate).

#### `GET /marketing/campaign/leads?status=Sent`
List leads, optionally filtered by status.

#### `PUT /marketing/campaign/leads/{session_id}/status`
Update a lead's campaign status.

**Body:**
```json
{
    "status": "Sent"
}
```

Valid statuses: `New`, `Sent`, `Opened`, `Replied`, `Meeting Booked`, `FollowUp_1`, `FollowUp_2`, `FollowUp_3`

### Follow-Up Automation

#### `POST /marketing/follow-up/check`
Check for leads due for follow-up and send follow-up emails automatically.

#### `GET /marketing/follow-up/schedule/{session_id}`
Get the follow-up schedule for a specific lead.

#### `PUT /marketing/follow-up/config`
Update follow-up configuration.

**Body:**
```json
{
    "enabled": true,
    "initial_delay_days": 3,
    "max_follow_ups": 3,
    "cadence_days": 7
}
```

### Analytics

#### `GET /marketing/analytics/summary?start_date=&end_date=`
Get campaign summary metrics (sent, opened, replied, booked, rates).

#### `GET /marketing/analytics/product-breakdown`
Get per-product performance metrics.

#### `GET /marketing/analytics/timeline?days=30`
Get daily event timeline for the last N days.

#### `GET /marketing/analytics/export?format=json`
Export full report as JSON or CSV.

---

## Quick Test Order (Postman)

| # | Method | Endpoint | Body |
|---|--------|----------|------|
| 1 | `GET` | `/health` | — |
| 2 | `GET` | `/config` | — |
| 3 | `POST` | `/mcp/search` | `{"query": "bank Ethiopia"}` |
| 4 | `POST` | `/mcp/tenders` | `{"query": ""}` |
| 5 | `POST` | `/mcp/directory` | `{"query": "tech"}` |
| 6 | `GET` | `/rag/status` | — |
| 7 | `POST` | `/agent/leads` | `{"query": "tech companies Ethiopia"}` |
| 8 | `POST` | `/agent/run` | `{"query": "find banks in Ethiopia"}` |
| 9 | `GET` | `/memory/conversation` | — |
| 10 | `POST` | `/sales/start` | — |
| 11 | `POST` | `/sales/chat` | `{"session_id": "...", "message": "We need an ERP"}` |
| 12 | `POST` | `/sales/generate` | `{"session_id": "..."}` |
| 13 | `POST` | `/sales/approve-send` | `{"session_id": "..."}` |
| 14 | `GET` | `/doc-gen/download/{session_id}` | — |
| 15 | `GET` | `/marketing/templates` | — |
| 16 | `GET` | `/marketing/campaign/stats` | — |
| 17 | `GET` | `/marketing/analytics/summary` | — |
