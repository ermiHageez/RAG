# AI Intelligence Platform — Version 3.0

> **From a single-company AI tool to the intelligence platform Ethiopian businesses build on.**
>
> Custom local AI models + Sector-specific RAG + MCP tools + Multi-tenant architecture.
> Not just for eTech. For every sector. Every business. Every scale.

---

## 1. The Vision

v2.0 was a **marketing & sales agent for eTech** — a single-company AI tool.

v3.0 is an **intelligence platform** — a foundation that Ethiopian businesses across every sector will build their AI on top of.

### Core Shift

| v2.0 (eTech Tool) | v3.0 (Platform) |
|---|---|
| One company (eTech) | Any business, any sector |
| Fixed RAG data | Sector-swappable data modules |
| Pre-built agents | Custom agent builders |
| Single tenant | Multi-tenant with isolation |
| Off-the-shelf Ollama models | **Custom fine-tuned local AI models** |
| One graph pipeline | Per-tenant, per-sector agent orchestration |
| Data in `data/` | Data marketplace per sector |

### The Platform Pillars

1. **Custom Local AI Models** — Fine-tune Ollama models on sector-specific data. Generate your own model.
2. **Sector-Specific RAG** — Swap `data/` per sector (banking, health, agriculture, logistics, education, government).
3. **MCP Tool Ecosystem** — Open MCP server that any business can connect to.
4. **Multi-Tenant Architecture** — Isolated tenants, shared infrastructure, massive scale.

---

## 2. What's Done (v2.0 Foundation) ✅

### RAG Pipeline
- Document loading: PDF (with OCR fallback), TXT, XLSX, CSV, DOCX, JSON, PPT
- Chunking: RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
- Embedding: Ollama `qwen3-embedding:4b` with LRU cache + async support
- Vector Store: FAISS IndexHNSWFlat with configurable efSearch/efConstruction, query caching
- Retriever: Two-stage merging FAISS + optional pgvector results with deduplication
- Reranker: Abstract interface with NoOpReranker + CrossEncoderReranker

### Multi-Agent LangGraph Pipeline (8 Agents)
| Agent | Model | Role |
|---|---|---|
| Supervisor | `gemma3:4b` | Query routing → [lead/tender/knowledge] |
| Lead | `qwen3:8b` | Ethiopian company discovery via MCP search |
| Tender | `qwen3:8b` | Tender scraping + FAISS relevance scoring |
| Knowledge | `qwen3-embedding:4b` | RAG retrieval from vector store |
| Sales Intelligence | `qwen3:8b` | Cross-reference leads/tenders, urgency labels |
| Content | `llama3.1:8b` | Personalized B2B email drafting |
| Approval | Rule-based | Quality gate before sending |
| Format | Rule-based | n8n payload packaging |

### MCP Server (Model Context Protocol)
- Web Search: DuckDuckGo + Google organic scrape fallback, sector/contact extraction
- Tender Scraper: 2merkato.com + addisbiz.com tender scraping
- Directory Scraper: 2merkato, addisbiz, ethyp company directory (3 sources)
- n8n Hook: Payload delivery with retry (3 attempts), validation, mock fallback

### API Server (41+ Endpoints)
- Health, Config, Metrics
- Agent pipeline (8 endpoints)
- RAG query, status, rebuild, upload, chat
- MCP search, tenders, directory
- Memory get/save
- Evaluation (RAG, routing, content)
- Sales Assistant (4-phase conversational flow)
- Document Generation (HTML proposals)
- Marketing Pipeline (templates, campaigns, follow-ups, analytics)
- Co-Pilot (human-in-the-loop review pipeline)

### Sales Assistant
- 4-phase state machine: DISCOVERY → RESEARCH → GENERATION → COMPLETE
- HTML proposal generator with professional CSS
- Approval gate before email delivery

### Marketing Pipeline
- 5 product-specific HTML email templates (Ehealth, ERP, SCCO, eShare, General)
- Campaign tracker: New → Sent → Opened → Replied → Meeting Booked
- Follow-up automation: configurable delay, cadence, max count
- Analytics dashboard: summary, product breakdown, timeline, CSV/JSON export

### ML Pipeline (Data → Model)
- Data collection: async writer, PII redaction, SHA256 dedup, rate limiting, file rotation
- Dataset builder: raw → chat-format conversion, quality checks, quarantine
- Model registry: version tracking, promote, rollback, eval score tracking
- Pipeline automation: build → quality → register → evaluate → promote → alert
- Prometheus metrics + Slack alerting

### Memory System
- JSONMemoryStore (dev) / PostgresMemoryStore (production)
- Conversation memory with knowledge base integration
- Lead deduplication, tender cache

### Database (pgvector)
- `knowledge_base` table: content, embedding vector(1024), metadata, timestamp
- `memory_store` table: key-value JSONB
- Cosine similarity search with IVFFlat index

### Evaluation Framework
- RAGPrecisionEvaluator: LLM-based relevance scoring
- RoutingAccuracyEvaluator: Precision/Recall/F1
- ContentQualityEvaluator: hallucination detection, format checks
- BenchmarkSuite: multi-evaluator runner with summary statistics

### UI (React + TypeScript)
- 25+ components: Copilot, AgentHub, AiHub, LeadReview, TenderReview, IntelReview
- CampaignTracker, AnalyticsDashboard, DealWorkspace, RagConsole
- Full API proxy configuration

### Testing
- 92+ tests across 16 files, all passing
- Mock Ollama — runs without external dependencies

---

## 3. What's Left from v2.0 ⏳

| Item | Status | Notes |
|---|---|---|
| pgvector Docker container | 🔴 Not started | `docker run pgvector/pgvector:pg16` |
| pgvector tests (5) | 🔴 Not started | insert, search, memory, retriever merge, graph wiring |
| Docker compose build | ⚠️ Blocked | Network timeout downloading torch (~2GB) |
| Docker deploy | 🔴 Pending | Build → compose up → verify 3 services |
| Live Google CSE keys | 🔴 Missing | `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` from Tech Lead |
| Live tender scraping | ⚠️ SSL issue | PPA/eGP scraping fails cert validation |
| n8n workflow import | 🔴 Pending | Import `AI email Automation.json` into n8n |
| Customer list XLSX | 🔴 Missing | `customer_list.xlsx` (105 records) not in `data/` |
| FAISS rebuild | 🔴 Pending | After adding customer data |
| PDF quality | ⚠️ Slow OCR | Scanned PDFs/PPTXs very slow on CPU |

---

## 4. v3.0 Architecture

```
                          ┌─────────────────────────────┐
                          │     PLATFORM ORCHESTRATOR    │
                          │  Multi-Tenant Router + Auth  │
                          └─────────────────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
    ┌───────────▼───────────┐ ┌─────▼──────┐ ┌──────────▼───────────┐
    │   SECTOR MODULES      │ │   MODEL    │ │   TOOL ECOSYSTEM     │
    │                       │ │  FACTORY   │ │                      │
    │  Banking/Finance      │ │            │ │  MCP Search          │
    │  Health/Hospital      │ │  Fine-tune │ │  MCP Tenders         │
    │  Agriculture/Farming  │ │  Custom AI │ │  MCP Directory       │
    │  Education/Schools    │ │  from RAG  │ │  MCP n8n             │
    │  Logistics/Transport  │ │  data      │ │  MCP Custom (plugin) │
    │  Government/PPA       │ │            │ │                      │
    │  Insurance            │ │  Generate  │ │  + Community MCP     │
    │  Telecom              │ │  Local LLM │ │  Marketplace         │
    │  ...                  │ │            │ │                      │
    └───────────────────────┘ └─────┬──────┘ └──────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
        ┌───────────▼───────────┐       ┌───────────▼───────────┐
        │   RAG LAYER (per      │       │   MODEL REGISTRY     │
        │   sector)             │       │                      │
        │                       │       │  Base: gemma3:4b     │
        │  FAISS (documents)    │       │  Base: qwen3:8b      │
        │  pgvector (knowledge) │       │  Base: llama3.1:8b   │
        │  Hybrid retriever     │       │  Fine-tuned: banking │
        │  Cross-encoder rerank │       │  Fine-tuned: health  │
        └───────────────────────┘       │  Fine-tuned: agri    │
                                        │  ...                 │
                                        └───────────────────────┘
```

### 4.1 Sector Module System

Instead of a single `data/` folder, v3.0 introduces **Sector Modules**:

```
data/
├── banking/          # NBE directives, bank profiles, loan products
│   ├── documents/
│   ├── faiss_index/
│   └── metadata.json
├── health/           # MOH standards, hospital directories, pharma
│   ├── documents/
│   ├── faiss_index/
│   └── metadata.json
├── agriculture/      # MoA data, crop prices, farming cooperatives
│   ├── documents/
│   ├── faiss_index/
│   └── metadata.json
├── education/        # University lists, curriculum, ministry data
├── logistics/
├── government/
├── telecom/
└── default/          # Generic fallback
```

Each sector module is self-contained:
- **Documents**: Sector-specific PDFs, spreadsheets, databases
- **FAISS Index**: Pre-built vector index for that sector
- **Metadata**: Sector config, model preferences, tool permissions
- **Agent Config**: Custom prompt templates, tool sets per sector

### 4.2 Custom Local AI Model Generation

The ML pipeline evolves from tracking interactions to **generating production models**:

```
User Interactions (all tenants)
        │
        ▼
┌──────────────────┐
│  Data Collection  │  ← training_sink.py (already built)
│  PII Redaction    │
│  Dedup + Validate │
│  per sector       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Dataset Builder  │  ← dataset_builder.py (already built)
│  Raw → Chat format│
│  Quality checks   │
│  Sector tagging   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│  MODEL GENERATION PIPELINE       │  ← NEW in v3.0
│                                  │
│  1. Modelfile Generator          │  ← generate_modelfile.py (built)
│  2. Ollama Model Build           │  ← build_model.sh (built)
│  3. Eval: RAG Precision          │
│  4. Eval: Routing Accuracy       │
│  5. Eval: Content Quality        │
│  6. Promote to Registry          │
│  7. Deploy to Production         │
│  8. A/B Test vs Previous         │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  MODEL REGISTRY   │  ← model_registry.py (built)
│                   │
│  banking-v1       │  ← fine-tuned on banking data
│  banking-v2       │  ← improved with more data
│  health-v1        │
│  default-v3       │
└──────────────────┘
```

**Key innovation**: Every sector gets its own fine-tuned local model. A bank uses a model that understands NBE directives, collateral requirements, and loan products. A hospital uses a model trained on MOH standards, pharmaceutical catalogs, and medical equipment specs.

### 4.3 Multi-Tenant Architecture

```
┌─────────────────────────────────────────────────┐
│                   API GATEWAY                    │
│           tenant-id → sector routing             │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐   ┌─────▼─────┐   ┌─────▼────┐
│ Tenant A │   │ Tenant B  │   │ Tenant C  │
│ (Bank)   │   │ (Health)  │   │ (Agri)    │
└────┬────┘   └─────┬─────┘   └─────┬────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
        ┌────────────▼────────────┐
        │  SHARED INFRASTRUCTURE    │
        │                          │
        │  • Ollama (4 models)     │
        │  • PostgreSQL/pgvector   │
        │  • FAISS indices         │
        │  • MCP Server            │
        │  • Model Registry        │
        │  • Evaluation Framework  │
        └──────────────────────────┘
```

Each tenant gets:
- Isolated FAISS index
- Isolated pgvector schema/table
- Custom agent configuration
- Sector-specific model
- Usage quotas and monitoring

### 4.4 MCP Tool Marketplace

v3.0 introduces an **MCP plugin system** where anyone can build and share tools:

| Tool | Type | Built |
|---|---|---|
| Web Search | Core | ✅ |
| Tender Scraper | Core | ✅ |
| Company Directory | Core | ✅ |
| n8n Hook | Core | ✅ |
| Ethiopian Bank Branch Locator | Sector | ❌ |
| Pharmacia / Drug Availability | Sector | ❌ |
| Crop Price Index (Ethiopia) | Sector | ❌ |
| School Directory (MoE) | Sector | ❌ |
| Transport Routes (Ethiopia) | Sector | ❌ |
| Custom MCP Builder | Platform | ❌ |

---

## 5. v3.0 Roadmap

### Phase 1: Platform Foundation (Sprints 12-13)

| Sprint | Tasks |
|---|---|
| **Sprint 12** — Multi-Tenant Auth & Routing | Tenant isolation, JWT auth, per-tenant config, API gateway |
| **Sprint 13** — Sector Module System | `data/` restructuring, sector metadata format, hot-swappable RAG |

### Phase 2: Model Generation Pipeline (Sprints 14-15)

| Sprint | Tasks |
|---|---|
| **Sprint 14** — Automated Fine-Tuning | Ollama Modelfile generation from sector data, build orchestration, eval gates |
| **Sprint 15** — Model Lifecycle | Registry UI, A/B testing, rollback, model metrics dashboard |

### Phase 3: Scale & Ecosystem (Sprints 16-17)

| Sprint | Tasks |
|---|---|
| **Sprint 16** — Performance & Scale | Horizontal scaling, caching layer, async agent queues, GPU scheduling |
| **Sprint 17** — MCP Marketplace | Plugin SDK, community tools, tool discovery, usage analytics |

### Phase 4: Intelligence Layer (Sprints 18-19)

| Sprint | Tasks |
|---|---|
| **Sprint 18** — Cross-Sector Intelligence | Multi-sector queries, data fusion, cross-referencing across sectors |
| **Sprint 19** — Predictive Analytics | Trend prediction, opportunity scoring, automated sector insights |

---

## 6. Technical Requirements

### Hardware (Scale)

| Tier | Users | CPU | RAM | GPU | Storage |
|---|---|---|---|---|---|
| Starter | 1-5 | 8 cores | 32 GB | RTX 3060 (12GB) | 200 GB NVMe |
| Growth | 5-20 | 16 cores | 64 GB | RTX 4090 (24GB) | 500 GB NVMe |
| Enterprise | 20-100 | 32 cores | 128 GB | 2× RTX 4090 / A100 | 1 TB NVMe |
| Platform | 100+ | 64+ cores | 256+ GB | 4× A100 / H100 | 2 TB+ NVMe |

### Software Stack

| Layer | Technology |
|---|---|
| API Server | FastAPI (scalable with workers) |
| Agent Orchestration | LangGraph (per-tenant graphs) |
| Vector Store | FAISS + pgvector |
| Local LLM | Ollama (fine-tuned per sector) |
| Model Format | Ollama Modelfile + GGUF |
| MCP Protocol | FastMCP SDK |
| Database | PostgreSQL 16 + pgvector |
| Workflow | n8n |
| Frontend | React + MUI |
| Container | Docker + Docker Compose |
| Monitoring | Prometheus + Grafana |

### Key Dependencies to Add

```toml
# NEW for v3.0
# Multi-tenant auth
pyjwt = "*"
passlib = "*"
# Model generation
subprocess = "*"  # (stdlib - for Ollama CLI)
# Sector management
importlib = "*"   # (stdlib - dynamic module loading)
# Scale
redis = "*"       # caching + rate limiting
celery = "*"      # async task queue
```

---

## 7. The Big Picture

```
               ┌──────────────────────────────────────┐
               │     ETHIOPIAN AI ECOSYSTEM            │
               │                                      │
               │  "Not an AI tool.                    │
               │   An intelligence platform            │
               │   that Ethiopian businesses           │
               │   build on top of."                   │
               │                                      │
               └──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ BANKING  │     │ HEALTH   │     │  AGRI    │
   │          │     │          │     │          │
   │ Custom   │     │ Custom   │     │ Custom   │
   │ AI Model │     │ AI Model │     │ AI Model │
   │ + RAG    │     │ + RAG    │     │ + RAG    │
   │ + MCP    │     │ + MCP    │     │ + MCP    │
   └──────────┘     └──────────┘     └──────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
               ┌───────────▼───────────┐
               │    PLATFORM CORE       │
               │                       │
               │  • Model Factory      │
               │  • RAG Engine         │
               │  • MCP Server         │
               │  • Agent Orchestrator │
               │  • Tenant Manager     │
               │  • Evaluation Suite   │
               └───────────────────────┘
```

### What This Means

- **For a Bank**: Deploy the banking module. It already understands NBE directives, knows Ethiopian banking regulations, can score loan applications, and generate personalized offers — all running locally.

- **For a Hospital**: Deploy the health module. It knows MOH standards, pharmaceutical supply chains, medical equipment catalogs, and can automate patient outreach — all running locally, no internet needed.

- **For the Government**: Deploy the public sector module. It understands procurement laws, can monitor tenders across all agencies, and automate supplier communication.

- **For a Farmer Cooperative**: Deploy the agriculture module. It tracks crop prices across Ethiopian markets, knows MOA programs, and generates market intelligence reports.

**Each sector gets its own custom local AI model, generated from its own data, served through its own MCP tools, orchestrated by its own agents — all on the same platform.**

---

## 8. Immediate Next Steps

### Right Now
1. ✅ v2.0 is complete with 92+ passing tests, 41 API endpoints, 8 agents, ML pipeline, and full UI
2. ✅ Run `pytest -v` to verify current test suite
3. ⏳ Start pgvector container for Sprint 9 completion

### This Week
4. Complete pgvector migration (Sprint 9) — 5 remaining tests
5. Docker compose build (once network is stable)

### This Month (v3.0 Phase 1)
6. Design tenant isolation model
7. Restructure `data/` into sector modules
8. Build multi-tenant auth system
9. Implement hot-swappable sector RAG

### Next Quarter (v3.0 Phase 2)
10. Automate model fine-tuning pipeline
11. Build model registry UI
12. Launch with 3 pilot sectors (banking, health, agriculture)

---

## 9. Architecture Diagrams

### Current v2.0 Architecture
```
User Query → FastAPI → LangGraph (8 agents) → FAISS/pgvector → MCP Tools → n8n → Email
```

### Target v3.0 Architecture
```
Tenant Request → API Gateway → Auth → Tenant Context
    → Sector Router (banking/health/agri/...)
        → Sector-Specific FAISS Index
        → Sector-Specific Fine-Tuned Model
        → Sector-Specific MCP Tools
        → Sector-Specific Agent Graph
            → Output (email/proposal/report/alert)
```

---

## 10. Success Metrics

| Metric | v2.0 | v3.0 Target |
|---|---|---|
| Tenants | 1 (eTech) | 10+ pilot, 100+ at scale |
| Sectors | 1 (tech) | 10+ (banking, health, agri, edu, gov...) |
| Custom Models | 0 | 1 per sector, fine-tuned & registered |
| Tests | 92 | 200+ |
| API Endpoints | 41 | 100+ |
| MCP Tools | 4 | 20+ (core + community) |
| Users Supported | 1-5 | 100+ concurrent |
| Data Scale | ~150 chunks | Millions of documents across sectors |

---

> **v3.0 is not an upgrade. It's a transformation.**
>
> We're removing the generic RAG/data folder and replacing it with sector-specific intelligence.
> We're generating custom local AI models, not just using off-the-shelf ones.
> We're building the platform that powers Ethiopian businesses — in every sector, at every scale.
>
> *No cloud. No API keys. No vendor lock-in. Just pure, local, sovereign AI.*
