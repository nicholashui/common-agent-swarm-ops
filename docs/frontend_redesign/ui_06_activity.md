# NN UI 06: Big Activity History & Ops Intelligence Spec

**UI ID:** nn_ui_06_activity  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0 — Fleet + Common Component View)  
**Related Main Doc Section:** Ui6 (enhanced with common version filters, impact, rollout opportunities)  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
- Comprehensive, filterable history of all agent/swarm executions with strong emphasis on **common component versions** and their impact.
- Support both individual swarm debugging and **fleet/common ops intelligence** (which commons are healthy/improving/degrading, rollout opportunities, anomalies tied to version changes).
- "One big column per subworkflow" board view + powerful table + timeline/Gantt.
- Enable bulk actions, replays with latest commons, and contribution of signals back to commons.
- Real-time updates for active runs.

## Layout & Structure (Header + Filters + Multi-View Main Area + Insights Sidebar)

**Header:**
- Title "Activity & Ops Intelligence".
- Date range picker (Today / Last 7d / 30d / Custom) + quick presets.
- Business / Workspace multi-filter.
- Prominent search (run ID, swarm name, common agent name/version, error keywords, output snippets).
- View mode segmented control: Board (columns per subworkflow/pattern) | Table | Timeline/Gantt.
- "Live Update" toggle (WS push new rows/ cards).

**Filters Row (below header, collapsible or always visible chips):**
- Common Agent / Version multi-select (from Registry, with search).
- Common Pattern filter.
- Status multi (success, error, running, paused).
- "Only show runs using outdated common versions" toggle (powerful for ops).
- "Has contributed to commons?" toggle.
- More advanced filters drawer (duration >X, cost >Y, specific business, has downstream impact, etc.).

**Main Content Area (flex-1):**

**View 1: Board / Column View (default for overview — your "one big column for one subworkflow")**
- Horizontal scrollable (or responsive grid) columns.
- Each column header: Subworkflow / Common Pattern name + version + (runs in period | success % | avg duration | est. cost) + health indicator.
- Vertical stack of **Execution Cards** below:
  - Card: Agent name + "Common vX.Y" badge (or custom), Timestamp or relative, Status badge + duration, Key metrics (tokens, cost), Input/output teaser (click expands full or opens detail), Error teaser if any.
  - Color accent left border by status or by common health.
  - Hover/click: Opens nn_ui_05 for that agent instance or the full SwarmInstance in canvas/activity context.
  - Quick actions on card: "Replay with latest commons", "Contribute signals", "View in Canvas".
- This view excels at spotting bottlenecks or version-specific issues across parallel branches at a glance.

**View 2: Detailed Table View (power user)**
- TanStack Table (virtualized, server-side pagination/sorting/filtering for scale).
- Columns: Timestamp, Run/Swarm ID (clickable), Business, Common Pattern + version, Agent (with common version badge), Status, Duration, Tokens In/Out, Cost, Error (expandable), Downstream Impact?, Actions (replay, debug in playground, contribute, open canvas).
- Bulk select + toolbar: "Replay selected with latest commons", "Export CSV/JSON", "Create improvement proposal from these failures", "Bulk contribute signals to commons".

**View 3: Timeline / Gantt (for performance & version impact analysis)**
- For selected SwarmInstance(s) or aggregated view: Horizontal time-based visualization.
- Lanes/rows = Subworkflows / Agents / Common Components.
- Bars = execution spans, color by status or common version.
- Overlaps show true parallelism. Cycle/iteration shown as repeated or extended bars with count.
- Hover/click bar → details + link to nn_ui_05 or canvas.
- Zoomable time scale, play animation of historical run if recorded.
- Useful for seeing serialization points, version change impact over time (e.g. after a rollout, did latency improve globally?).

**Right / Collapsible Insights Sidebar (Ops Intelligence — always valuable):**
- Summary KPIs for current filters: Total runs, success rate trend, total cost, top failing/slowest commons, common version distribution.
- Charts (Recharts): Runs over time, Success % trend, Cost breakdown by common agent/version, Latency distribution.
- "Rollout Opportunities & Anomalies":
  - "CommonVerifierAgent v1.8 shows +12% pass rate. Safe to rollout to your  swarms on v1.6?"
  - Anomaly cards: "Error spike on CommonReportAgent after v2.1 in 3 swarms — investigate or auto-rollback?"
- "Collective Improvement Impact" (for the period): How much your runs contributed to commons improvements, token/cost savings realized.
- Bulk action buttons tied to current filter/selection.

**Empty / Loading States:** Skeleton table or cards. Friendly empty with "No activity yet — start a swarm from Common Patterns".

## Components & Tech

- **Board Columns & Cards**: shadcn Card or custom, draggable? (future for reordering views), responsive (wrap or horizontal scroll with snap).
- **Table**: @tanstack/react-table + virtualizer. Custom cell renderers for Common Version Badge (clickable to nn_ui_05), Status (with icon + color), Expandable JSON/Output.
- **Timeline/Gantt**: react-calendar-timeline, vis-timeline, or custom SVG/canvas with d3-scale for performance. Support for groups (subworkflows) and dependencies.
- **Charts**: Recharts or Tremor (clean, dark-theme friendly).
- **Filters**: shadcn Combobox / MultiSelect for commons (searchable, with version pills), Date picker (react-day-picker or shadcn), Toggle chips.
- **Real-time**: WS subscription to new activity (pushes new cards/rows or updates running ones). Optimistic UI for replays.

## Data & API

**Fetches (with filters applied server-side):**
- GET /api/activity (paginated, filtered by date/business/status/common_agent_version/outdated etc.).
- GET /api/activity/insights (KPIs, charts data, rollout opportunities, anomalies for current filters).
- GET /api/commons/versions (for filter dropdowns and badges).

**Mutations:**
- Replay (single or bulk) — can specify "use latest common versions".
- Contribute signals / knowledge from selected runs.
- Create improvement proposal from failure cluster.
- Rollout / A/B from insight cards (deep links to rollout UI).

**State:** Active view mode (persisted), current filters (URL sync for shareable links), selected rows for bulk, expanded cards/rows, sidebar collapsed state.

**Real-time Channels:** `activity:new`, `swarm:{id}:status` (for running updates in board/table), `commons:health` (for insight updates).

## Interactions & Ops Flows

**Board View Power:**
1. See column for "Synthesis + Verification" subworkflow with several errored cards on older CommonReportAgent.
2. Filter whole page to that common version → Insights sidebar highlights "outdated version with rising errors".
3. Select the errored cards → Bulk "Replay with latest CommonReportAgent" or "Create improvement proposal".
4. Click insight "Rollout opportunity" → Opens rollout modal with impact on these swarms.

**Table + Bulk:**
- Powerful sorting/filtering to find e.g. "all runs of CommonMarketPredictor v2.0 in trading swarms with >5s duration".
- Bulk export for external analysis (your trading notebooks, etc.).

**Timeline:**
- Select a SwarmInstance from recent or search → Gantt shows full execution with common versions labeled on bars.
- Spot that a verification loop iteration count dropped after a common agent update → evidence for improvement.

**Contribution & Improvement:**
- From any run or cluster of failures → "Propose improvement to affected common agents" (pre-fills proposal with traces).
- "Bulk contribute verified outputs to Common Knowledge".

**Keyboard:** Table navigation, Cmd/Ctrl + click for multi-select, Enter to open detail, / to focus search.

## Accessibility, Responsive & Polish

- Virtualized everything for thousands of rows without lag.
- ARIA for table (sortable headers, row actions), live regions for new activity or insight updates.
- Mobile: Board becomes vertical stack of columns or "group by subworkflow" select. Table → infinite scroll cards. Timeline simplified or hidden on small screens (or horizontal scroll).
- Visual: Consistent Common Version Badges (indigo pill with version + health dot). Status colors match global system. Subtle animations for new cards appearing or status changes. Dark theme optimized for data density.
- Performance: Server-side filtering/pagination critical. Prefetch common versions. Debounced filter changes.

## Open Questions / Notes

- Scalability target (how many activity rows typical? 10k? 100k+? — affects virtualization + server design).
- Depth of "anomalies" and "rollout opportunities" detection (rules engine vs ML/meta-critic on backend).
- Gantt library choice vs custom (perf on long timelines with many parallel agents).
- URL state sync for filters (shareable "show me all outdated common runs in trading this week").
- How "contributed to commons" flag is computed and surfaced.

## Wireframe Summary (Text)

Header + Filters (date, business, common agent multi-select with "outdated only" toggle, search).

**Board View:**
[Column: Data Ingestion (Parallel Pattern vX)]          [Column: Analysis + Verification]
  Card1: CommonDataFetcher v2.1 • Success 1.2s          CardA: CommonSentiment v1.9 • Error • "replay latest"
  Card2: CommonCleaner v2.0 • Running pulsing           CardB: CommonPredictor v2.0 • Success
  ...                                                   ...

**Table View:** Dense columns with Common Version badges prominent.

**Insights Sidebar:**
KPIs + Charts
Rollout Opportunities:
[Card: CommonXXX vNew better on X metric. Rollout to my 12 affected swarms? Approve | A/B | Details]

**Implementation Notes:** Build views as separate components (ActivityBoard, ActivityTable, ActivityTimeline) switched by segmented control. Share filter state via URL or context. Heavy reuse of StatusBadge, CommonVersionPill, ExecutionCard from design system. This page is the ops command center for both debugging and steering the commons.

Cross-reference main redesign for exact column meanings, bulk action specs, and how insights tie into rollout/A/B flows. Make filters and common version integration best-in-class so users naturally operate at the "common component" level.


## VA-Agent-Swarm Activity Alignment

Activity records must follow the run/task/artifact/critique/gate projections in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). Board, table, and timeline views show graph revision, pinned Common versions, production/template phase when present, full task lifecycle, iteration, retry, dependency/gate wait reason, checkpoint/replay reference, budget/cost, and redacted metric values.

Add drill-down affordances for artifact lineage and technical/QC/rights/continuity/provenance status; directed critique records with severity, rubric score, evidence, and resolution; and quality-gate results separated into L1 validation, L2 rubric, L3 baseline preference, Judge/GateKeeper evidence, and human decision. Filters must include lifecycle/retry state, gate state, artifact QC/provenance state, critique severity, and phase/template as supported by the domain adapter.

Replay, retry, and skip actions must use server-determined eligibility and show the prior task/run state. They must preserve immutable common-version and artifact provenance rather than silently using the latest version.
