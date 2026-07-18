# Frontend Redesign for common-agent-swarm-ops

**Version:** 2.1 (Complete UI Inventory Added for Full System Control & Visibility)  
**Date:** July 18, 2026  
**Prepared for:** Nicholas (@n1ch01as_ai / nicholashui) – N1ch01as Architect, Moltbot & common agent swarm ecosystem  
**Repo Alignment:** Fully matched to `common-agent-swarm-ops` (common/reusable agent & swarm pattern primitives + production ops layer).  
**Research Basis:** 2026 trends (graphs, verification loops, collective improvement), xAI/Grok, your YouTube (Moltbot, templates, AI dev), best of n8n/Langflow/Dify + common patterns from AutoGen/CrewAI/etc.

**Core Vision (Rethought):** The frontend is the complete control plane and visibility layer for a living ecosystem of **Common Agents** and **Common Swarm Patterns**. It enables users to discover, compose, run, monitor, govern, improve collectively, audit, integrate, and optimize at scale — all while maintaining deep provenance, real-time observability, and safe evolution of the commons.

---

## 1–7. Core UIs (Already Detailed in Per-Screen Specs)

See the companion files created alongside this document:
- `nn_ui_01_login.md`
- `nn_ui_02_dashboard.md` (Common Health + Fleet Ops)
- `nn_ui_03_swarm_composer.md`
- `nn_ui_04_canvas.md` (Graph-native + BIG ROWs + live common-linked ops)
- `nn_ui_05_agent_detail.md`
- `nn_ui_06_activity.md`
- `nn_ui_07_registry_hub.md` (Star discovery & governance hub)

These 7 form the foundation for building, running, and improving swarms on the common layer.

---

## 8. Complete UI Inventory for Full Control & Visibility

To ensure users can **fully control and view every aspect** of the system (commons governance, fleet operations, knowledge, evaluation, costs, security, integrations, auditing, collaboration, and extensibility), the following additional UIs are required. They close all gaps for production use, self-hosting, and collective improvement at scale.

Each is described with purpose, key capabilities, layout highlights, data needs, and how it ties into the common + ops vision. These should be implemented as dedicated routes/pages (or advanced drawers/modals where appropriate) with consistent design system (shadcn, React Flow where visual, real-time WS, TanStack Query, bilingual support).

### Ui8: Global Settings & Configuration (`/settings`)
**Purpose:** Central control for all backend integrations, policies, and defaults so users can fully configure the platform to their infrastructure and governance needs.

**Key Capabilities:**
- LLM Providers & Models: Add/edit/test connections (xAI/Grok, DeepSeek, Ollama, vLLM, OpenAI-compatible, etc.). Model tier defaults (fast/cheap vs reasoning). Rate limits, fallbacks.
- Credentials & Secrets Vault: Secure storage (encrypted) for API keys, DB creds, trading exchange keys, YouTube/Remotion, Strapi, Jenkins, ESP32, etc. Scoped to business or global. Audit of access. Never plaintext after save.
- Integrations: Manage Slack/Discord/Telegram (notifs + agent tools), Email, Webhooks, Git (knowledge sync), external vector DBs, hardware fleets. OAuth where possible + health checks.
- Policies & Defaults: Global retry/timeout/cost caps, logging verbosity, human-approval matrix for high-impact actions (trading exec, code changes, external API calls). Common version pinning policy ("always latest safe" vs manual approve). Data retention for history/logs.
- Workflow/Swarm Defaults: Default common knowledge collections, notification channels on complete/fail/cost threshold, orchestration mode preferences.
- UI Preferences: Theme (dark default), language (EN/繁體中文), canvas snap/grid defaults, notification prefs, keyboard shortcuts help, feature flags (live collab, advanced tracing).
- Business/Workspace Management: Create/edit workspaces, member invites/roles (Owner, Editor, Runner, Viewer), access control to commons vs private.

**Layout:** Tabbed or accordion sections (Providers, Secrets, Integrations, Policies, Defaults, UI, Workspaces). Forms with validation + test buttons. Secrets never shown after save (reveal on explicit action with audit log). Impact warnings when changing policies that affect running swarms.

**Data:** Strong integration with Keycloak for users/roles. Backend secrets manager (e.g., Vault or encrypted DB). Real-time health checks on integrations.

**Full Control Enabled:** Users can lock down the system, connect all their existing tools (your stack: FastAPI, Strapi, OpenWebUI, Jenkins, trading APIs, hardware), set safety guardrails, and customize defaults for their HK/creative/trading/education workflows.

### Ui9: Advanced Monitoring, Tracing & Alerts (`/monitoring`)
**Purpose:** Deep observability and alerting so users can fully view system health, performance bottlenecks, distributed traces, and set proactive controls.

**Key Capabilities:**
- Real-time Fleet Dashboard: Live running swarms (mini canvas thumbnails or status), resource usage (if containerized: CPU/mem/queue), LLM-specific (tokens/sec, rate limit queues).
- Distributed Tracing Explorer: Tree view (like LangSmith/Phoenix/Jaeger) for any run — every LLM call, tool call, agent step, verifier iteration, with timings, tokens, errors, common version used. Clickable to nn_ui_05 or canvas. Search/filter traces.
- Alerts & Notifications Center: Rule builder (e.g., "if CommonReportAgent success < 90% last hour or cost > $X → Slack #alerts + email + pause affected swarms"). History of fired alerts. One-click actions (rollback, investigate).
- Metrics Explorer: Custom queries on executions (p95 latency per common agent/version, cost by business/pattern, error rate after version change). Export to Prometheus/Grafana or built-in dashboards. Heatmaps, histograms.
- Anomaly Detection: Auto or rule-based detection of version-related issues, cost spikes, latency regressions tied to specific common changes.
- Resource & Cost Governance: Token burn rate, projected monthly cost, budget alerts per business/common component. "What-if" simulator for common version updates.

**Layout:** Dashboard with live cards + tabs (Traces, Alerts, Metrics, Anomalies). Tracing view is expandable tree + timeline. Alert rules in table with create/edit modal (condition builder + action selector).

**Data:** OpenTelemetry or custom tracing from orchestrator. WS for live metrics. Efficient time-series storage (ClickHouse or Postgres + Timescale).

**Full Visibility Enabled:** Users can see exactly what every common agent and swarm is doing at any moment, trace issues to specific versions or patterns, and set automated controls — essential for production fleets and safe commons evolution.

### Ui10: Knowledge Management Hub (`/knowledge`)
**Purpose:** Full control and visibility over all knowledge (common + scoped) that powers RAG agents, with easy contribution from verified swarm runs.

**Key Capabilities:**
- Global + Common Collections Browser: Cards or table of collections/namespaces (per business or shared commons). Stats (chunks, last sync, usage by agents, contribution volume). Health indicators.
- Per-Collection Deep View: Sources list (MD, PDF, web, Git, Strapi, manual), chunking strategy config, metadata, reindex controls. Search test with filters (hybrid, metadata, score threshold). Relevance feedback.
- Contribution Pipeline: From successful/verified runs (nn_ui_05 playground or activity) → "Contribute distilled insight / verified output to Common Knowledge" with provenance, auto or human review step, deduping.
- Sync & Ingestion: Git folder/repo sync (perfect for your ~52k–60k MD corpora), URL crawl, Strapi/CMS connector, bulk upload with AI classification/tagging. Scheduled jobs management.
- Advanced RAG Controls: Chunking strategies (recursive, semantic, agentic), embedding model choice per collection, hybrid search, reranker, graph RAG extraction (entities/relations viz if supported). Usage analytics (which agents query what, common failure queries → improvement suggestions).
- Knowledge Graph Viz (optional advanced): Force-directed or hierarchical view of extracted entities/relations across collections. Click entity → "Which common agents use this?" or "Run targeted query".

**Layout:** Hub with search + filters. Collection cards → detail drawer/page with tabs (Sources, Search Test, Config, Contribution History, Analytics).

**Data:** Vector DB (Qdrant/Pinecone/Weaviate/Chroma) + metadata store. Contribution workflow state machine. Graph DB optional (Neo4j or simple).

**Full Control Enabled:** Users can manage the "brain" of all agents (your large MD corpora, trading strategies, DSE materials, legacy docs, creative lore), ensure high-quality RAG via testing/contribution loops, and grow the shared commons knowledge layer.

### Ui11: Eval & Self-Improvement Dashboard (`/eval`)
**Purpose:** Visibility into collective performance of commons + tools to run improvement campaigns and review proposals at scale — closing the self-refinement loop for the entire ecosystem.

**Key Capabilities:**
- Harness Results Overview: Aggregate scores across Common Agents/Patterns (task success, token efficiency, latency, groundedness, human preference, verifier pass rate). Trends and regressions after version changes.
- Proposal Campaigns: "Run batch eval on selected/underperforming commons" → generates improvement proposals automatically (meta-critic powered). Review queue with impact estimates.
- Improvement History & Impact: Timeline of merged proposals with before/after metrics (global and per-business). "Your runs contributed to X improvements".
- Custom Eval Rubrics: Create/edit rubrics (for domain-specific like trading P&L simulation, content quality, tutor assessment accuracy). Apply to agents or patterns.
- A/B & Canary Results: Dedicated view of ongoing/ past experiments with statistical significance, winner recommendation, auto-promote or rollback.
- Meta-Critic Insights: Top failure modes across commons, suggested common pattern tweaks, token waste hotspots.

**Layout:** Dashboard with scorecards + charts. Proposal queue (table with diff links, approve buttons). Campaign launcher (select commons → run harness → generate proposals). History timeline with metric deltas.

**Data:** Eval results stored with run provenance. Meta-critic endpoint that can analyze aggregate traces. A/B framework in orchestrator.

**Full Control Enabled:** Users (and the system) can systematically measure, improve, and govern the quality of the entire common layer — turning usage data into better agents and patterns for everyone.

### Ui12: Notifications Center (`/notifications` or advanced drawer)
**Purpose:** Centralized, actionable alert and update hub so users never miss critical ops events, improvement opportunities, or governance tasks.

**Key Capabilities:**
- Unified Inbox: Swarm complete/fail, cost thresholds, common version updates available, new proposals affecting your swarms, rollout impacts, integration health issues, eval regressions.
- Smart Grouping & Priority: Group by swarm/business/common component. Priority scoring (high-impact commons changes first).
- One-Click Actions: From notification → open canvas with context, approve rollout, review proposal, replay with latest commons, contribute signals.
- Preferences: Per-type, per-business, delivery (in-app, email, Slack/Telegram/Discord, push for PWA). Quiet hours, digest mode.
- History & Search: Full searchable log of all notifications.

**Layout:** Clean list or kanban (To Do / In Progress / Done) with filters. Rich notifications with embedded actions or deep links. Badge count on global header bell (already in dashboard/header).

**Data:** Notification service (triggered by orchestrator, registry, eval, etc.). User preference store. Read/unread + action-taken state.

**Full Control Enabled:** Users stay on top of the living system without constant manual checking — critical for production ops and active commons participation.

### Ui13: User Profile & Preferences (`/profile`)
**Purpose:** Personal control center for identity, usage insights, API access, and preferences.

**Key Capabilities:**
- Account & Security: Profile info, password/magic link management, connected SSO (Keycloak, Google, GitHub), API tokens (create/revoke for programmatic swarm runs, with scopes).
- Usage Dashboard (Personal): Your swarms run count, cost, contribution impact (improvements helped, knowledge contributed), favorite commons, recent activity.
- Preferences: Language, theme, default business/workspace, notification settings (detailed), canvas defaults, demo mode controls.
- API & Integration Tokens: Manage personal access tokens with fine-grained permissions (run specific swarms, read registry, propose improvements). Usage logs.
- Contribution Stats & Badges (light gamification): "Top contributor in Trading domain this month", impact numbers.

**Layout:** Clean profile page with sections/tabs. Token management with copy + revoke. Personal impact cards with sparklines.

**Data:** User model + preferences in backend/Keycloak. Usage aggregation queries. Token service.

**Full Control Enabled:** Users manage their identity, programmatic access (for Jenkins, scripts, trading bots, etc.), and see their personal value from participating in the commons.

### Ui14: Audit Logs & Compliance (`/audit`)
**Purpose:** Complete visibility and exportable record of all actions for security, compliance, debugging, and governance.

**Key Capabilities:**
- Immutable Log: All config changes (commons, policies, integrations), swarm runs (who, what inputs/outputs at high level, common versions used), secret access, proposal/merge actions, rollout decisions, knowledge contributions.
- Powerful Filters & Search: By user, business, common agent/version, action type, date, success/failure. Export to CSV/JSON/Parquet for external SIEM or analysis.
- Detail View: Expandable entries with before/after diffs (for config changes), linked traces or swarm IDs.
- Compliance Reports: Pre-built or custom (e.g., "All changes to trading-related commons last 90 days", "Who ran high-cost swarms").

**Layout:** Dense table (virtualized) with expandable rows. Filters sidebar or top bar. Export buttons. Detail modal with rich diff + context links (to canvas or agent detail).

**Data:** Append-only audit log table (or service like immutable ledger). Efficient indexing for search/export.

**Full Control Enabled:** Full transparency and accountability — essential for production, shared commons governance, regulated domains (trading, education data), and debugging complex swarm behaviors.

### Ui15: API & Developer Portal (`/api` or `/developers`)
**Purpose:** Programmatic control and extensibility so power users and scripts can fully automate and integrate with the platform.

**Key Capabilities:**
- Interactive API Docs: Auto-generated from OpenAPI (Swagger UI or similar) for all endpoints (registry, swarms, activity, eval, proposals, etc.). Try-it-out with auth.
- SDK / Client Snippets: Generate curl, Python (with common lib), TypeScript, etc. for common actions (run swarm from pattern, update common version, propose improvement).
- Personal Access Tokens Management (link to profile): Create with scopes, usage dashboard, revocation.
- Webhook Management: Configure outgoing webhooks for events (swarm complete, common updated, alert fired) with secret signing + retry.
- Extensibility: Docs for custom node/tool development, adapter for new runtimes (Moltbot distributed, new LLM providers), contribution guidelines for new Common Patterns/Agents.
- Rate Limits & Quotas: Visibility into current usage vs limits.

**Layout:** Clean portal with docs explorer, code samples, token manager, webhook config. "Quick start" guides for common integrations (Jenkins pipeline, trading bot, content pipeline script).

**Data:** OpenAPI spec from backend. Token service. Webhook delivery logs.

**Full Control Enabled:** Developers and automation scripts can treat the entire common + ops system as code — run swarms from CI/CD, sync commons, react to events, extend with custom tools/nodes — while staying within governance guardrails.

### Ui16: Onboarding, Help & Documentation (`/onboarding` or contextual help)
**Purpose:** Lower barrier to full adoption and ensure users quickly understand how to control and benefit from the common layer.

**Key Capabilities:**
- Interactive Product Tour: Step-by-step (first login → explore Registry → compose first swarm from common pattern → run with live view → review improvement proposal).
- Contextual Help: "?" icons everywhere that open relevant docs or short video (your YouTube content, Cantonese + English). AI help chat ("How do I safely rollout a new common agent version?").
- Documentation Hub: Searchable docs (concepts, common patterns explained with visuals, governance model, contribution guide, API reference, troubleshooting). Bilingual.
- Sample Projects: Preloaded demo swarms with guided walkthroughs (Trading Intel with verification, Content Pipeline, DSE Tutor).
- Community / Feedback: Links to GitHub discussions, "Request new common pattern" form, "Report issue with commons" that creates proposal.

**Layout:** Dedicated onboarding flow (modal or page) + persistent help center. In-app guided tours using libraries like Shepherd.js or custom.

**Data:** Docs as MD/MDX or CMS (Strapi friendly). Tour state per user.

**Full Control Enabled:** New and returning users quickly become proficient at using, governing, and contributing to the system — accelerating collective improvement.

### Ui17: Mobile / PWA Companion Views
**Purpose:** On-the-go visibility and control for ops without full desktop canvas editing.

**Key Capabilities (Read-heavy, action-light):**
- Dashboard summary (common health, running swarms count, critical alerts).
- Activity feed (recent runs, filterable, quick replay or "update to latest commons").
- Notifications center with actions.
- Registry search + quick "add to my favorites" or "propose improvement".
- Agent detail (history, playground limited, ops status).
- Approval flows (rollouts, proposals) with impact summary.
- PWA installable, push notifications for critical events, offline cache for recent activity.

**Layout:** Responsive or dedicated mobile-optimized views (simplified cards, bottom nav, large tap targets). Avoid complex canvas editing on small screens (link to desktop or read-only mini graph).

**Tech:** Next.js PWA (service worker, manifest), responsive Tailwind, touch-friendly components.

**Full Control Enabled:** Users can monitor and act on the live system from phone/tablet (important for HK mobile-first culture and on-call ops).

### Ui18: Collaboration, Sharing & Multi-User Features (Future/Optional)
**Purpose:** Team and cross-business collaboration on swarms and commons.

**Key Capabilities:**
- Sharing: Share swarm links (view or edit permissions), embed read-only canvas or activity.
- Real-time Collaboration: On canvas (multiple cursors, conflict-free via Yjs/CRDT — later phase). Comments/mentions on nodes or proposals.
- Team Workspaces: Role-based access, shared favorites/commons views.
- Proposal Review Workflows: Assignment, discussion threads, approval chains for team/official.
- Public / Community Mode (opt-in): Publish anonymized or credited common patterns/agents for wider ecosystem.

**Layout:** Sharing modals, presence avatars on canvas, comment sidebar, team dashboard widgets.

**Data:** Permissions model, real-time sync (Yjs + backend), discussion storage.

**Full Control Enabled:** Teams can work together on complex swarms and commons governance without losing individual control or auditability.

### Ui19: Cost Governance & Usage Analytics (`/costs` or integrated in dashboard/monitoring)
**Purpose:** Full financial visibility and control over LLM spend (the dominant variable cost in agent swarms).

**Key Capabilities:**
- Usage Breakdown: By business, swarm/pattern, common agent/version, model, time. Trends, forecasts, anomalies.
- Budgets & Alerts: Set soft/hard budgets per business or common component. Actions on breach (warn, throttle new runs, notify).
- What-If & Optimization: Simulator for common version updates or pattern changes ("switching to this cheaper common agent in 12 swarms saves $Y/mo with <2% quality impact").
- Reports & Export: Monthly cost reports, chargeback to businesses, optimization recommendations from meta-critic.
- Token Efficiency Leaderboards: Per common agent/pattern (encourages improvement).

**Layout:** Analytics dashboard with charts, budget cards, recommendation engine output, export buttons.

**Data:** Cost attribution at run/agent level (from orchestrator + LLM provider billing APIs). Forecasting models.

**Full Control Enabled:** Users can run large-scale swarms responsibly, optimize spend through commons improvements, and allocate costs transparently.

### Ui20: Swarm Blueprints & Saved Templates Management
**Purpose:** Easy reuse and governance of known-good compositions built on commons.

**Key Capabilities:**
- Blueprint Gallery: Saved combinations of Common Pattern + specific common agent versions + params + knowledge. Rich previews, metrics from past runs, "Instantiate new swarm from this blueprint".
- Versioning & Governance: Blueprints can be versioned, deprecated, or promoted to "official common blueprint". Approval for production blueprints.
- Personal vs Team vs Common: Private, shared in business, or contributed to global commons.
- Quick Actions: From activity or canvas "Save current configuration as Blueprint".

**Layout:** Gallery with search/filters (domain, success rate, cost, common pattern). Detail page with full graph preview, run history, "Use Blueprint" CTA.

**Data:** Blueprint entity linked to common pattern + pinned agent versions + metadata.

**Full Control Enabled:** Users can capture, share, and standardize successful swarm configurations built on the common layer — accelerating reliable operations.

---

## Summary: How These UIs Enable Full Control & Visibility

Together with the core 7, this inventory covers:
- **Build & Compose** (Composer, Canvas, Blueprints)
- **Discover & Govern Commons** (Registry Hub, Agent Detail, Eval Dashboard, Settings)
- **Run & Monitor** (Dashboard, Activity, Monitoring/Tracing, Notifications)
- **Improve Collectively** (Agent Detail contribution, Eval, Knowledge Hub, Improvement flows)
- **Control & Secure** (Settings, Policies, Audit, Cost Governance, API Portal)
- **Adopt & Collaborate** (Onboarding, Profile, Mobile, Collaboration)
- **Extend** (API Portal, custom nodes via docs)

Every major function of common-agent-swarm-ops is visible and controllable through an intuitive, consistent, real-time interface that reinforces the common layer and collective improvement.

---

## List of All UIs to Be Created / Implemented

Here is the complete prioritized list of UIs for the system. Core ones (01–07) already have detailed spec files (`nn_ui_XX_*.md`). The rest are described in this document and can have dedicated spec files created next if needed.

### Core (Detailed Specs Already Created)
1. **nn_ui_01_login.md** — Login + Demo access
2. **nn_ui_02_dashboard.md** — Common Health + Fleet Ops Overview
3. **nn_ui_03_swarm_composer.md** — Pattern-first NL Swarm Composer
4. **nn_ui_04_canvas.md** — Graph Canvas (BIG ROWs, common-linked, live ops)
5. **nn_ui_05_agent_detail.md** — Agent Detail (4+ tabs + ops)
6. **nn_ui_06_activity.md** — Activity History & Ops Intelligence
7. **nn_ui_07_registry_hub.md** — Common Registry Hub (discovery + governance)

### Additional Recommended (Described in Section 8 Above — Create Specs Next)
8. **nn_ui_08_settings.md** — Global Settings & Configuration
9. **nn_ui_09_monitoring.md** — Advanced Monitoring, Tracing & Alerts
10. **nn_ui_10_knowledge.md** — Knowledge Management Hub
11. **nn_ui_11_eval.md** — Eval & Self-Improvement Dashboard
12. **nn_ui_12_notifications.md** — Notifications Center
13. **nn_ui_13_profile.md** — User Profile & Preferences
14. **nn_ui_14_audit.md** — Audit Logs & Compliance
15. **nn_ui_15_api_portal.md** — API & Developer Portal
16. **nn_ui_16_onboarding.md** — Onboarding, Help & Documentation
17. **nn_ui_17_mobile.md** — Mobile / PWA Companion Views
18. **nn_ui_18_collaboration.md** — Collaboration, Sharing & Multi-User (phase 2+)
19. **nn_ui_19_costs.md** — Cost Governance & Usage Analytics
20. **nn_ui_20_blueprints.md** — Swarm Blueprints & Saved Templates Management

**Recommended Implementation Order (after core 01–07):**
- 08 Settings (foundational for control)
- 09 Monitoring + 12 Notifications (ops visibility)
- 10 Knowledge + 11 Eval (commons improvement loop)
- 14 Audit + 15 API Portal (governance & extensibility)
- 13 Profile + 16 Onboarding (adoption)
- 17 Mobile + 19 Costs (practical production)
- 20 Blueprints (reuse acceleration)
- 18 Collaboration (team scaling)

This complete inventory ensures the frontend provides **full control and complete visibility** over every function of common-agent-swarm-ops, from commons discovery to collective self-improvement, fleet ops, security, extensibility, and mobile access.

The updated `frontend_redesign.md` (v2.1) + the 7 existing per-UI spec files now form a complete, actionable frontend specification suite ready for implementation. All specs are ready for development. Let me know which additional `nn_ui_XX_*.md` spec files you want created next, or if you'd like code generation, mockups, or further refinements!

This positions the project for complete, production-grade implementation. ✅