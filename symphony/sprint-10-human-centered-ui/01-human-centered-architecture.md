# Sprint 10 — Human-Centered Co-Pilot UI

## Goal
Transform the eTech Agent from an automated pipeline into a **human-centered co-pilot** — AI recommends, humans decide. Build a React + MUI demo UI for stakeholder review.

## Philosophy
| Old (Auto-Pilot) | New (Co-Pilot) |
|---|---|
| AI runs end-to-end | AI recommends, human approves |
| Output is final | Output is a draft, human edits |
| Black box decisions | Every suggestion includes an explanation |
| Replace the team | Augment the team |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React + MUI UI                     │
│  Query Input → Step-by-step review → Final approve  │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP (fetch/axios)
                   ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI (port 8001)                      │
│  POST /copilot/run        → starts pipeline          │
│  POST /copilot/review     → human feedback per step  │
│  POST /copilot/approve    → final sign-off           │
│  GET  /copilot/explain    → why did AI decide this   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            LangGraph Copilot Pipeline                 │
│  supervisor → leads → tenders → intel → draft → send │
│      ↑human    ↑human     ↑human    ↑human   ↑human  │
│      review    review     review    edit     approve │
└─────────────────────────────────────────────────────┘
```

## Human-in-the-Loop Flow

```
User Query
    │
    ▼
[Step 1: Supervisor] → AI classifies query → Human confirms/re-routes
    │
    ▼
[Step 2: Leads] → AI finds companies → Human reviews, edits, approves
    │
    ▼
[Step 3: Tenders] → AI fetches tenders → Human reviews, re-ranks
    │
    ▼
[Step 4: Sales Intel] → AI cross-references → Human adds own insights
    │
    ▼
[Step 5: Email] → AI drafts → Human edits in-editor, approves
    │
    ▼
[Step 6: Send] → Final approval → Human clicks Send or Schedule
```

## New Backend Modules
- `src/copilot/explain.py` — explanation generator for each step
- `src/copilot/sanitize.py` — input sanitization + prompt injection detection
- `src/copilot/routes.py` — new FastAPI routes for co-pilot flow
- Updates to `state.py`, `graph.py` — interrupt/resume pattern
