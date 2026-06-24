Act as a Principal Frontend Engineer specializing in React 19, TypeScript, and MUI v6. Your goal is to build a high-fidelity frontend application for an enterprise AI multi-agent platform called "eTech Sales & Marketing Co-Pilot" that interfaces with an underlying LangGraph, Ollama, and pgvector backend.

### Core System Context
The backend exposes 41 endpoints across two functional pipelines:
1. Sales Assistant (/sales/*): A 4-phase state engine (DISCOVERY → RESEARCH → GENERATION → COMPLETE).
2. Marketing Pipeline (/marketing/*): An analytical campaign workflow engine tracking campaign states (New → Sent → Opened → Replied → Meeting Booked) and automated follow-ups.

### Architecture & Technical Constraints
- Tech Stack: React 19, TypeScript, Vite, Material UI (MUI) v6.
- Styling: Pure CSS Modules (*.module.css). STRICTLY NO TAILWIND CSS.
- Code Standards: Production-ready, strictly typed interfaces for all business entities (Leads, Tenders, CampaignTemplates, PipelineSteps, FeedItems).

### Design & Theme Specifications
- Theme Palette: Implement a unified theme provider supporting deep gray/slate backgrounds (#121214), dark container surfaces (#1a1a1e), clean borders, and crisp typography. Use vibrant accent highlights (e.g., sharp greens/emeralds or tech-blues) sparingly for statuses and metrics.
- Layout Orientation: Use a standard high-efficiency layout grid: a structural 260px left sidebar layout with sticky multi-level navigation lists and a fluid content canvas container featuring responsive spacing parameters.
- Component Elevation & Shadows: Rely entirely on crisp, low-depth borders (e.g., 1px solid rgba(255,255,255,0.08)) rather than heavy standard box shadows to maintain a sleek, clean, modern dark workspace.
- Mode Changes: When switching between Sales and Marketing modes using the global toggle component, make sure the left navigation sidebar options and main content sections refresh immediately with minimal visual popping or jarring layout shifts. Use smooth structural rendering.

### UI Component Specifications
1. CopilotLayout: 
   - Top AppBar showing "eTech Sales & Marketing Co-Pilot" branding.
   - Global Operational Switch: A prominent, clear toggle element selecting between [Sales Mode] and [Marketing Mode].
   - Dynamic Sidebar: Fixed at 260px width. Adapts its tree navigation items instantly based on the active mode:
     * Sales Navigation: Discovery, Research, Generation, Final Review, Operational Feed.
     * Marketing Navigation: Template Designer, Campaign Pipeline, Automation Rules, Telemetry Analytics.
2. QueryInput:
   - A modern input form with a prompt field adapting dynamically based on the operational toggle mode state.
   - Feature an explicit submit action button and a fixed security micro-text notice: "Your input is sanitized for security". Enforce an absolute loading state disabling input while processing is ongoing.
3. PipelineStep:
   - Structured step wrapper displaying step counts, workflow names, status-chip tags (pending / active / completed / rejected), an accordion section for "Why did the AI suggest this?" and quick action controls (Approve, Edit, Reject).
4. Sales-Specific Modules (Visible only when Sales Mode is active):
   - LeadReview: Grid/List of company cards showing Name, Sector, Location, Contact, Description, and AI Score. Supports checkbox multi-selection, inline text editing, manual lead insertion, and a contextual analysis panel.
   - TenderReview: Cards showing title, description, deadlines, and urgency badges (Red/Amber/Green). Includes order manipulation buttons and an explanation of the relevance score.
   - IntelReview: Dual-panel presentation rendering cross-referenced source records beside an open multi-line text input field for manual field note additions.
5. Marketing-Specific Modules (Visible only when Marketing Mode is active):
   - CampaignTemplateEngine: Visual card matrix showing available layouts fetched via /marketing/templates, tracking target product categories and historical effectiveness, alongside inline configuration inputs.
   - CampaignTracker: Kanban pipeline tracking status progression metrics (New → Sent → Opened → Replied → Meeting Booked) with interactive status override controls.
   - FollowUpScheduler: Rule-management view visualizing campaign automation variables (3-day initial delay, 7-day loop cycles, max 3 follow-ups) with quick lead exclusion controls.
6. Unified Content & Action Center:
   - EmailEditor: Form UI containing a subject line text box and variable editing block. In Sales Mode, include a clear secondary action button to download the print-ready HTML proposal document from /doc-gen/download/{id}. Features a visual gauge rendering a Personalization/Quality metric accompanied by real-time low-score error messaging.
   - ApprovalGate: Verification summary card grouping final review properties with quick-action buttons ("Approve & Send", "Reject", "Save as Draft") and an explicit MUI Date/Time schedule tracking picker.
   - ActivityFeed & Performance Metrics: Renders transactional logging timelines alongside high-level KPI dashboard cards. In Sales Mode, chart "Time Saved" and "Acceptance Rate". In Marketing Mode, display active metrics for "Open Rates", "Click-Through Percentages", and "Per-Product Performance".

### Interactive State Machine Simulation Logic
Incorporate a client-side state machine managing state changes for both demonstration flows seamlessly without needing a live, network-connected API:

- Sales Execution Flow Demonstration Sequence:
  * State 0 (Idle): Displays empty dashboard framing only the core query panel tailored for Sales inputs.
  * State 1 (Supervisor Routing): Simulates processing after receiving "Find banking leads and security tenders in Ethiopia". Renders an indeterminate loading animation representing the supervisor model computing the routing path, displaying the status string: "Classified as: lead + tender".
  * State 2 (Leads Isolation): Renders LeadReview containing 5 mock Ethiopian banking institutions. Clicking "Approve Leads" triggers the next state.
  * State 3 (Tender Assessment): Appends TenderReview tracking procurement contracts with calculated deadlines and urgency badge color scales. On approval, advances forward.
  * State 4 (Intel Contextualization): Displays IntelReview to collect user annotations.
  * State 5 (Content Synthesis): Populates EmailEditor with targeted outreach copy alongside an option to simulate download of the HTML proposal document.
  * State 6 (Final Execution Gate): Renders ApprovalGate to capture scheduling inputs.
  * State 7 (Audit Logging): Transitions to display ActivityFeed presenting simulated time-saving summaries.

- Marketing Campaign Workflow Sequence:
  * State 0 (Idle): Displays empty view framing the query panel tailored for Marketing inputs.
  * State 1 (Template Ingestion): Processes request "Create an outreach campaign for eTech cloud hosting...", displaying routing status: "Classified as: marketing template generation".
  * State 2 (Template Composition): Displays CampaignTemplateEngine showing layout cards. Clicking "Select Template" advances the flow.
  * State 3 (Lead Grouping): Displays CampaignTracker listing audience distribution. Clicking "Approve Campaign Pipeline" advances the flow.
  * State 4 (Automation Parameter Selection): Displays FollowUpScheduler displaying sequence timing rules.
  * State 5 (Layout Validation): Opens EmailEditor showing full HTML layout drafts and personalization score metrics.
  * State 6 (Deployment Dispatch): Shows ApprovalGate to handle scheduling tasks before hitting "Approve & Send".
  * State 7 (Telemetry Analytics): Displays the AnalyticsDashboard showing live campaign telemetry charts and product engagement metrics.

Generate the complete front-end codebase architecture starting with domain type definitions (types.ts), clean CSS module files, and the primary app controller layout step-by-step.