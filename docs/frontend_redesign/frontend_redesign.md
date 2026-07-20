# Frontend Redesign for common-agent-swarm-ops

**Version:** 2.2 (Deep Redesign — Common-First, Ops-Centric, Graph-Native; Backend v1.2 Aligned)
**Date:** July 19, 2026
**Prepared for:** Nicholas (@n1ch01as_ai / nicholashui) – N1ch01as Architect, Moltbot & common agent swarm ecosystem  
**Repo Alignment:** Fully matched to `common-agent-swarm-ops` (common/reusable agent & swarm pattern primitives + production ops layer for swarms built on them).  
**Research Basis:** Deep rethink incorporating 2026 trends (graphs over simple loops for agent organizations, verification/iteration loops, token-efficient multi-agent patterns from LangGraph/Slate discussions & arXiv multi-agent papers), xAI/Grok capabilities (strong reasoning/meta-critique, tool use), your YouTube content (Moltbot distributed AI agents, template-driven AI dev, AI-driven development workflows), and best features from n8n, Langflow, Dify, Flowise, plus common patterns from AutoGen/CrewAI/MetaGPT/AgentVerse.

## Backend v1.2 frontend integration contract (v2.2 alignment)

This binding addendum aligns the frontend design with [`../backend_redesign/backend_redesign.md`](../backend_redesign/backend_redesign.md) v1.2 and the approved frontend-redesign requirements. It makes production operability visible to users while preserving the browser as an untrusted presentation and command client. This addendum supersedes earlier WebSocket-first, direct-upload, inferred-status, browser-authority, raw-data, and assumed-backend language in this document: the normative browser interface is generated `/api/v1` REST contracts plus authorized Server-Sent Events (SSE).

### Document-wide interpretation

All UI labels, examples, and future-facing concepts below are illustrative only until a generated `/api/v1` projection or action contract supports them. The browser renders only authorized redacted projections, evidence references, and action references; it neither chooses tenant/actor authority nor derives eligibility, governance, execution, approval, retry, or recovery decisions. Every mutation is one server-governed, idempotent command intent. SSE is observation-only: it may update an already-authorized projection only after sequence validation, and a gap, replay failure, authorization change, or schema mismatch requires REST resynchronization before incremental updates resume. A stale projection is visibly stale, cannot claim live state, and cannot invoke a freshness-critical action.

Untrusted upload content, import URLs, remote content, tool suggestions, and model output are inert data. The browser submits imports only to an authorized ingestion contract; it never fetches, navigates to, embeds, or executes an untrusted import URL or its content. Any export, collaboration, integration, administration, or developer experience below is similarly limited to server-authorized generated contracts and redacted projections.

### Requirements

#### Requirement 8.1: Generated, versioned API client

The frontend shall consume generated or schema-checked TypeScript types from `/api/v1/openapi.json`, including the standard success/error envelope. Screens must not hand-copy backend DTO shapes, call unversioned paths, or depend on engine/provider/queue implementation details. An API removal or semantic response change is not exposed in the UI until the backend compatibility window and generated client migration are complete.

#### Requirement 8.2: Recovery-aware commands

Every state-changing UI action shall submit a server-authorized, idempotent command with a stable `Idempotency-Key` for its pending user intent. The UI disables duplicate submissions, preserves the pending command state across a recoverable navigation/reconnect, and reconciles the final response or a fresh projection before offering another action. It does not retry a mutation with a new key after an ambiguous network failure, rate limit, authorization error, or approval/policy failure.

#### Requirement 8.3: Ordered, recoverable live state

The frontend shall use the authorized `/api/v1/events/stream` SSE transport for operational updates. It stores each authorized `Last-Event-ID` per scoped subscription, applies only sequence-valid events to local state, and displays a visible reconnecting/stale indicator while disconnected. If replay is bounded, expired, denied, or contains a sequence gap, the UI stops applying incremental updates, fetches the authoritative REST projection, replaces local state, and reconnects; it must never silently continue from an unknown state.

#### Requirement 8.4: Truthful operational status

Dashboard, activity, canvas, and mobile-ops screens shall distinguish live, delayed, reconnecting, degraded, unavailable, and stale projections using text and iconography in addition to color. They render server-provided `as_of`, freshness, and degraded-state fields. Only authorized operations views query the redacted `/api/v1/health` summary; browser features must not use liveness/readiness endpoints to reveal infrastructure or tenancy details.

#### Requirement 8.5: Safe artifact and knowledge ingress

Upload/import interfaces shall present server-defined file type, size, ownership, and retention requirements before submission, then show asynchronous states such as `validating`, `quarantined`, `processing`, `indexed`, `rejected`, or `archived`. Client-side checks improve feedback but are never treated as authorization or security validation. The UI sends content only to authorized ingestion endpoints, displays opaque artifact/document references and redacted scan/indexing results, and never turns a pasted URL, document text, tool suggestion, or model output into executable authority.

#### Requirement 8.6: Least-privilege observability

The frontend shall display redacted event summaries, digests, provenance references, correlation IDs, recovery eligibility, and authorized evidence links only. It must not render raw prompts, credentials, protected retrieval content, raw tool arguments/results, object-store locations, queue names, provider errors, or internal trace payloads. A correlation ID is copyable for support but does not grant resource access.

### API client, command, and error behavior

The frontend's API layer has one responsibility: validate client inputs, attach the current authenticated session and correlation/idempotency headers as allowed by the server, serialize generated request types, and map the standard response envelope to view state. It must not implement governance, calculate authorization, decide retry eligibility, construct tool calls, or infer completion from optimistic UI alone.

| Situation | Required UI behavior |
|---|---|
| `202` / queued command | Render a server-confirmed pending state with resource/run reference; observe via REST/SSE rather than treating it as execution success. |
| Ambiguous command result | Retain the same idempotency key, query the command/resource projection when permitted, and show “status being reconciled”; do not submit a duplicate command. |
| `429` rate limit | Show the public message and `Retry-After` countdown; preserve unsent user input where safe; do not automatically resubmit a mutation. |
| Authorization, policy, or approval failure | Show the stable redaction-safe error and allowed next action (for example, request review); never disclose hidden resource state or offer a client-side bypass. |
| `manual_recovery_required` / dead-letter projection | Show an operational recovery status, failure summary, correlation ID, and authorized escalation link. Recovery remains a separate server-governed action. |
| Projection degraded or stale | Preserve last known redacted data with `as_of`/freshness labels, disable actions that need current state, and provide a refresh/reconnect affordance. |
| SSE gap or replay retention expiry | Fetch the corresponding REST snapshot, replace local incremental state, then resubscribe from the returned sequence context. |

Read-only requests may follow normal bounded network retry rules. Mutations may be retried only through the same idempotency identity after the client has determined that the server permits reconciliation; browser retry logic never repeats an effectful request solely because a connection closed.

### Live transport and projection rules

SSE is the sole live transport in this redesign for dashboard, activity, approvals, canvas status, rollout, notifications, and any optional composition-assistant observations. WebSocket is not part of the browser contract. Each subscription requests only server-authorized topics and uses opaque resource IDs; tenant, actor, and permission scope are always derived server-side.

The client reconciles REST and SSE as follows:

1. Load an authorized REST projection, including its version, `as_of`, freshness/degraded state, and current event sequence where provided.
2. Subscribe to the narrowest required SSE topic set and ignore events that do not match the selected resource/projection version.
3. Apply a typed event only if it advances the expected event sequence and can be represented by the generated projection schema.
4. On reconnect, authorization change, sequence gap, schema mismatch, or bounded-replay response, discard the affected incremental cache, reload the projection, and restart the subscription.
5. Surface a redacted event/recovery timeline in Activity and Canvas rather than exposing transport or worker internals.

Task lifecycle UI includes the backend recovery states in addition to the VA lifecycle: `queued`, `running`, `self_refine`, `waiting_for_critique`, `blocked`, `failed`, `complete`, `cancelling`, `cancelled`, and `manual_recovery_required` when present in a projection. The UI may offer retry, skip, cancel, or escalation only when the server returns a corresponding authorized action reference and eligibility state.

### Operational UX additions

- **Dashboard:** Add an authorized control-plane health/freshness panel showing redacted API/projection health, delayed-event warning, queue/run backlog summary, approval-expiry alert, and a link to affected swarms. It never displays component credentials, host names, internal queue names, or tenant-external metrics.
- **Canvas and Activity:** Show reconnect state, projection `as_of`, blocked/recovery reason, recovery eligibility, event-sequence resync outcome, and immutable correlation/audit references. A stale canvas cannot claim a task, gate, or rollout is live.
- **Approvals and rollouts:** Disable irreversible controls while their projection is stale or a command is pending. Decision dialogs display the exact server-held evidence revision and expiry; the user must refresh if it changes before decision submission.
- **Registry and Agent Detail:** Read version compatibility, deprecation, and migration status from generated contracts. A deprecated Common Agent version remains inspectable for historical provenance but cannot be presented as a silently safe replacement.
- **Knowledge and artifacts:** Add ingestion status, scan/quarantine result, owner scope, retention state, and safe error guidance to contribution, playground, and artifact panels. “Import from URL” means submit an untrusted reference for server-side policy evaluation; it never causes a browser-side fetch or exposes remote content directly to an agent.
- **Mobile operations:** Use compact but explicit “Live,” “Delayed,” “Reconnecting,” “Recovery required,” and “Unavailable” labels, so status is not communicated by color alone.

### Frontend data and security boundaries

The frontend stores only the minimum session-safe projection cache needed for rendering and event resumption. It does not persist access tokens, tool credentials, raw protected data, or privileged artifacts in local storage. URLs to artifacts, traces, imports, and recovery actions are opaque server-issued references and are reauthorized when opened.

All content received from users, uploads, imported references, backend event payloads, tool summaries, or model-generated text is displayed as data, not executable instructions. Rendering uses safe text/structured components; client routing rejects unsafe external destinations unless explicitly approved by a server-provided allowed-action contract. Frontend filters and validation help users correct input but do not substitute for server-side tenant ACL, malware scanning, content validation, provenance, or governance checks.

### Contract, accessibility, and resilience verification

- Generate/check the TypeScript API client from backend OpenAPI in CI and fail on unreviewed incompatible schema changes.
- Fixture-test successful, queued, rate-limited, authorization-denied, approval-required, stale, degraded, reconnecting, bounded-replay, sequence-gap, cancellation, retry-exhausted, and `manual_recovery_required` projections.
- Test that an SSE reconnect reloads authoritative data before applying events after a gap; that duplicate-click and ambiguous-network flows reuse one idempotency identity; and that no UI retry creates a second governed effect.
- Test artifact/knowledge forms for type/size/ownership/retention feedback, asynchronous scan/index states, safe URL handling, redacted errors, and no client-side fetch of untrusted imports.
- Test responsive and accessibility behavior for health/freshness/recovery states, ensuring labels, icon names, keyboard focus, and live-region announcements do not rely on color or reveal sensitive operational details.

### Delivery alignment

Frontend delivery follows the backend sequence: Phase 1 static mock views remain useful for interaction validation; Phase B introduces generated read contracts; Phase C introduces idempotent commands and REST projections; Phase E introduces task/artifact/critique/quality SSE projections; and backend Phase F enables the health, freshness, recovery, ingestion, OpenAPI compatibility, and resilience contract above. A frontend route may advertise a control only after its generated endpoint and authorized action contract are available. No visual feature is evidence that an underlying command, queue, provider, or policy exists.

**Core Rethink (1000x iterated):**  
The project is **not** just another workflow builder. It is the **common foundational layer** for agent swarms: standardized, versioned, reusable **Common Agents** and **Common Swarm Patterns** (parallel independent, hierarchical supervisor-worker, debate/consensus, map-reduce, verification-loop, dynamic router graphs, etc.) that anyone can discover, fork, compose, and improve collectively. The frontend makes the "common" layer visible, usable, and improvable while providing world-class **ops** (monitoring fleets of swarms, safe rollouts of common component versions, aggregate eval & self-improvement, shared knowledge contributions, A/B testing, cost governance across usages).  

Every agent in a swarm is preferably a linked version from the **Common Registry** (with provenance, usage stats aggregated across all swarms/businesses, eval scores from common harness). Custom agents are possible but encouraged to contribute back. Subworkflows are instantiated from **Common Patterns**. The UI treats the common layer as the source of truth and the ops layer as the control plane.

This delivers reusability at scale, collective improvement (your N1ch01as Architect self-refine loops applied to the commons), and production ops that n8n-style tools lack for pure agent swarms, while going deeper on standardization and shared intelligence than Langflow/Dify.

---

## 1. Design Principles (Rethought for Common + Ops)

1. **Common Layer First** — Default to reusable, versioned Common Agents & Common Swarm Patterns from central Registry. Custom = fork from common. Every usage feeds back stats/eval/improvement signals to the commons.
2. **Graph-Native Swarm Organizations** (2026 evolution) — Canvas supports stateful graphs (not just DAGs): dynamic routing (LLM routers), cycles/iteration loops with verifiers, parallelism, hierarchical nesting, consensus/voting nodes. "BIG ROWs" as visual for parallel independent sub-swarms or map-reduce shards.
3. **Ops as First-Class Citizen** — Dashboard, activity, and monitoring focus on fleet health of swarms + health/impact/rollout of *common components* across fleets. Safe version rollouts, canary/A/B in production swarms, bulk updates with approval gates.
4. **Collective Self-Improvement** — Every common agent/pattern has aggregate performance (success, tokens, latency, cost, groundedness) from *all* usages. One-click "Propose Improvement to Commons" runs meta-critic (Grok-powered or local) on failures + successes and suggests new version. Training guides/eval rubrics evolve from real runs.
5. **Standardized Interfaces for Interoperability** — Common Agents expose consistent I/O schemas, tool-calling format (OpenAI-compatible), structured outputs, eval metrics (task success, efficiency, human preference, RAG faithfulness). This enables mixing agents from different creators safely in one swarm.
6. **Observable & Replayable at Swarm + Common Level** — Trace any run back to the exact common versions used. See "this common agent v1.3 improved after 847 runs across 23 swarms — view diff & rationale".
7. **Knowledge as Shared Commons Contribution** — Successful/verified outputs or distilled insights from runs can (opt-in) contribute to common knowledge collections. Per-agent RAG + shared commons.
8. **Production Discipline + Cost as Shared Resource** — Token/cost budgets at common-component, swarm-instance, and business level. Estimates before run. Rollout impact analysis ("updating this common agent to v2.0 will affect 14 active swarms, est. +12% token efficiency").
9. **Desktop Power + Mobile Ops** — Rich graph canvas + registry exploration on desktop. Mobile/PWA optimized for ops monitoring, approvals, quick replays, health alerts.
10. **Self-Host + Extensible + Bilingual** — The UI uses the server-derived authenticated session and generated contracts, independent of the selected identity provider or orchestration adapter. Backend/runtime integrations, prompt execution, and export generation are server-governed capabilities exposed only when supported by `/api/v1`. Full 繁體中文 / Cantonese interface and content support remains a product goal; user-provided prompts remain untrusted data.

**Color & Visual Language:** Dark-first professional (slate #0f172a). Accent indigo/violet for common/registry items (to distinguish from custom). Status colors consistent. Registry cards have "Common vX.Y • 12.4k runs • 94% success" badges. Graph edges animated for data/state flow; cycles highlighted with iteration count.

---

## 2. Repo Architecture Alignment (How Frontend Uses the Governed Control Plane)

The following are **backend capability projections**, not browser dependencies or implementation commitments. The frontend discovers each only when an implemented generated `/api/v1` contract returns an authorized, redacted projection or action reference:

- **Common Registry capability**: versioned Common Agent/Pattern discovery, provenance, compatible fork/proposal workflows, and aggregate evaluation/usage summaries.
- **Swarm execution capability**: validated Swarm Instance composition, queued execution, graph/task projections, and server-governed verification and approval gates.
- **Operations capability**: redacted fleet health, activity, rollout-impact, recovery, and cost projections with explicit `as_of` and freshness state.
- **Knowledge and artifact capability**: authorized ingestion, contribution, provenance, and asynchronous scan/indexing projections. Imports remain untrusted references until the server validates them.
- **Evaluation and improvement capability**: authorized evaluation evidence and proposal projections; any meta-critic or runtime is a backend implementation choice, never browser authority.
- **Identity and tenancy capability**: server-derived session, organization, actor, and permission context. The UI neither selects nor stores these as authority.

**Frontend Mapping**:
- Registry Hub renders authorized Common Registry projections and submits only returned action references.
- Canvas and Composer render authorized graph/run projections and submit server-governed command intents.
- Dashboard, Activity, and Monitoring render redacted operations projections; SSE observes them but does not establish state or authority.
- Agent Detail renders returned version, evaluation, provenance, and evidence references.
- Knowledge panels submit content or untrusted references only through authorized ingestion contracts and render returned status projections.
- All history and views show only authorized provenance references for the common version used at runtime.

This keeps the frontend a presentation and command client for common primitives and operations rather than a direct control surface for backend services.

---

## 3. Tech Stack (Same Strong Base, with Common/Graph Focus)

Unchanged core (Next.js 15 + TS + Tailwind + shadcn/ui + React Flow/XYFlow for graphs with groups, parent nodes, custom edges for state vs data, cycles). Add:
- Strong emphasis on **Registry components** (searchable grid like Hugging Face models or npm, but with agent graph previews, run stats, "usage in live swarms" indicators).
- Graph enhancements in React Flow: support for cyclic edges (visual loop with iteration badge), dynamic/conditional edges (LLM router node renders as special diamond or cloud icon), sub-swarm nesting (expandable group nodes that can themselves contain patterns).
- State: TanStack Query for session-safe authorized projections only; cache only the minimum redacted fields and event cursors needed for the active session, and clear them when the session, organization, or actor changes. Authorized SSE supplies observation-only live updates for swarm runs and ops events (for example, a redacted rollout-status change) after REST snapshot and sequence validation.
- Storybook stories for CommonAgentCard, SwarmPatternPreview, RegistrySearch, RolloutApprovalModal, and stale/reconnecting/redacted-projection states.

Folder structure similar, with added `components/registry/`, `components/ops/`, and generated or schema-checked API client modules from `/api/v1/openapi.json`; frontend code must not mirror backend Pydantic DTOs by hand.

---

## 4. Page-by-Page Design (Ui1–Ui7+ Deeply Rethought for Common + Ops)

### Ui1: Login (Unchanged, but post-login lands in Registry-aware Dashboard)

### Ui2: Dashboard — Now **Common Health + Ops Fleet Overview**

**Header**: Business/workspace switcher + prominent **"Go to Common Registry Hub"** button (or global nav item) + Command Palette (now includes "search common agents", "propose improvement to commons", "start A/B test on common agent X in my swarms", "rollout common pattern v2").

**Main Sections (rethought)**:

- **Common Components Health** (top hero row, live):
  - Cards or mini stats: "Common Agents in Use: 87 versions across 142 active swarms • Avg success 91.4% (↑ from last week)". "Top Improved This Week: MarketSentimentAgent v2.1 ( +8% token efficiency from 2.3k runs)". Quick links to Registry filtered by "recently improved" or "high impact".
  - "Pending Improvement Proposals": 3 proposals awaiting review (for org admins or community if shared commons).

- **Your Swarms Fleet Ops**:
  - Running Swarms: Live cards with overall status, linked common agents count, cost rate, "View Graph" or "Pause Fleet".
  - Recent Swarm Runs: Table with columns now including "Common Agents Used (versions)", "Deviations from Common Patterns", quick "Replay with current commons" or "Compare to baseline common version".
  - **Common Impact Insights** (AI-generated from Ops service): "Updating CommonReportAgent to v3.0 would improve 19 of your active swarms by est. 15% latency and save ~$47/mo. Affected swarms: [list]. Safe to rollout? [Approve for my swarms] [A/B test first]".

- **Quick Common Actions**:
  - "Explore / Search Common Registry"
  - "Compose New Swarm from Common Patterns"
  - "Review Improvement Proposals for Commons I'm Using"
  - "Run Eval Harness on My Custom Agents (contribute back?)"

- **Business-Scoped + Cross-Common Trends**: Charts showing your usage vs global commons trends (anonymized).

This dashboard makes you feel you are operating on top of a living, improving common foundation rather than isolated workflows.

### Ui3: Swarm Composer / Pattern Composer (Deeply Enhanced from Chat Suggester)

**Layout**: Chat on left (or top), **Common Pattern Palette + Preview** on right or bottom.

**Chat (rethought)**:
- An optional, server-provided composition-assistant projection can recommend Common Swarm Patterns and compatible Common Agents or forks from authorized registry data. It presents returned rationale, aggregate metrics, risks, and mitigations as inert, redacted suggestions—not policy, execution authority, or a direct model/tool channel.
- Users may express goals such as distributed data fetching, a report-quality verification loop, or low-cost operation. The browser submits this as untrusted composition input only through a generated authorized contract.
- Streaming suggestions are observation-only and rendered as inert structured data. “Load Recommended Pattern + Agents into Canvas” is available only as a returned authorized action reference; its command creates or updates a server-governed graph revision.

**Right Panel — Common Pattern Browser**:
- Horizontal or grid of **Common Swarm Pattern Cards** (visual mini-graph preview using small React Flow or static SVG/Mermaid render of the pattern structure).
  - Examples: "Parallel Independent Sub-Swarms (BIG ROWs visual)" — for independent data/analysis/synthesis. "Hierarchical Supervisor + Workers". "Debate & Consensus (multi-agent voting)". "Map-Reduce + Verification Loop". "Dynamic Router Graph (stateful, LLM decides next)". "Iterative Refinement with Verifier (your self-refine style)".
  - Each card: Name, description, when to use, avg metrics from real usages (success, tokens, iterations), "number of swarms using", "last improved", "Instantiate in Canvas", "Fork as Custom Pattern".
- Search/filter patterns by domain, parallelism level, verification strength, cost tier.
- "Suggest Custom Pattern from my goal" → meta-agent proposes new common pattern candidate (with graph JSON) for contribution to registry.

This makes composition start from battle-tested, collectively improved common patterns rather than blank canvas or pure NL (though NL still works and maps to patterns).

### Ui4: Visual Swarm Graph Canvas (Graph-Native, Common-Linked, BIG ROWs for Parallel)

**Top Toolbar Enhancements**:
- Swarm name + linked Common Pattern badge (e.g. "Based on: Parallel Independent + Verification Loop v1.4") with "Update to latest common pattern" or "Fork pattern".
- "Common Agents Used: 8/12 (4 custom forks)" — click to see list + bulk "Update all to latest safe versions" or "A/B test variants".
- Run controls + new **"Rollout / A/B in Production"** (for swarms using commons).
- AI Co-Pilot toolbar: "Optimize for token efficiency (using aggregate commons data)", "Add verification loop where missing", "Suggest dynamic router for this branch", "Propose this entire swarm structure as new Common Pattern".

**Left Palette — Split "Common" vs "Custom"**:
- **Common Registry Tab** (default, searchable): Drag CommonAgent or CommonPatternFragment. Shows live stats badge ("v2.3 • 94% success • used in 312 swarms"). Hover shows mini eval report. Double-click or drag creates **linked instance** in graph (shows provenance pill "Common v2.3").
- **Custom / Local Tab**: Ad-hoc agents or forks (clearly visually distinct, e.g. dashed border or different accent). "Contribute this fork back to Commons as vX proposal" action.
- Categories now include Common Patterns as draggable "macro nodes" that expand into pre-wired sub-graph groups (BIG ROWs or nested structures).

**Main Canvas (React Flow — deeply enhanced for common swarms)**:
- **Nodes**:
  - **Common Agent Node** (primary): Icon + name + "Common vX.Y" badge (color coded by health or your usage). Live status summary (when running). Metrics strip (tokens, cost, last eval score). "Open in Registry" or "Propose Improvement" quick actions. Ports for I/O (standardized schema preview on hover/click). When selected, right sidebar shows "This is linked to Common Registry — changes here are local fork unless contributed".
  - **Custom Agent Node**: Visually distinct (e.g. "Custom Fork of CommonReportAgent v2.1").
  - **Sub-Swarm / Pattern Group Node** (BIG ROWs realized): Expandable/collapsible container representing a Common Pattern instantiation or parallel independent branch. Header shows pattern name + version + aggregate status. Internal nodes (agents) visible when expanded. Supports nesting (hierarchical swarms). Visual treatment: stronger border or background tint for common patterns. "Update internal common agents to latest" bulk action on group.
  - Special nodes for patterns: Supervisor (hub with spokes to workers), Router (diamond, dynamic), Verifier (check icon, cycle back edge), Consensus/Vote (multiple inputs → single output with vote viz), Map (fan-out) / Reduce (fan-in).
- **Edges**: Data flow (solid), State/control flow (dashed or different color), Cycle edges for iteration loops (curved with iteration counter badge when running, e.g. "iter 3/ max 5"). Animated particles for active flow. LLM Router edges can be "suggested by model at runtime".
- **Interactions**:
  - Drag from Common Registry → linked node (immutable link unless fork).
  - Right-click node/group → "Replace with newer Common version", "A/B test alternative common agent here", "View aggregate eval for this common component", "Contribute local changes as improvement proposal".
  - Multi-select groups of common agents → bulk ops (update, propose improvement, view cross-swarm usage).
  - Auto-layout with awareness of common patterns (e.g. nice parallel BIG ROWs for independent sub-swarms, radial for supervisor).
  - Mini-map + search/highlight nodes by common name or status.
  - Live run mode: Nodes render only redacted, sequence-valid status and authorized evidence references from the current REST projection plus SSE observations. Cycle nodes show only returned iteration and verifier-status summaries; a reconnecting, degraded, or stale canvas is labelled accordingly and cannot claim a task, gate, or rollout is live.
  - Validation: On save/run, render only the returned version, schema, tool-policy, budget, verification, rollback, and approval category results; enable a run control only when its current authorized action reference permits it.

**Right Sidebar (contextual, powerful for common)**:
- When common node selected: Registry info (description, current eval scores from *all* usages, improvement history with diffs & rationales from meta-critic, "Propose new version based on this swarm's traces"). Quick "Update to latest common" or "Pin this version for this swarm".
- When group/pattern selected: Pattern details, "Instantiate more parallel shards", "Add verifier to this sub-swarm".
- Workflow-level: Linked common pattern info, "Contribute this composed swarm as new Common Pattern candidate", global cost/token budget, orchestration mode (enforce common pattern rules or allow deviations).

This canvas makes building with commons delightful and makes contributing back frictionless. The "BIG ROWs" for parallel independent subworkflows are a natural visual outcome of instantiating common parallel patterns.

### Ui5: Common Agent / Instance Detail (Now Registry-Centric with Cross-Swarm Ops)

When you click a (common) agent node or from Registry:

**Header**: Common Agent name + current version badge + aggregate stats (total runs across all swarms, global success %, avg tokens/cost, improvement velocity). Quick actions: "Propose Improvement to Commons", "A/B Test this version vs newer in my swarms", "Fork to Custom", "View All Usage Across Swarms".

**Tabs (refined to  your 4 + ops additions)**:

**Tab 1: Instance History + Cross-Swarm Usage**  
- Filters now include "This Swarm only" vs "All Swarms using this Common Agent (vX.Y or all versions)".  
- Table shows provenance (which SwarmInstance + business).  
- New "Impact" column or section: how this agent's performance affects downstream in various patterns.  
- "Replay using latest common version" vs "replay pinned version".

**Tab 2: Configuration / Spec (Common Versioned)**  
- Render the authorized Common Version projection: returned role, goals, policy/model compatibility summaries, output-schema summary, guardrails, evaluation rubric, and allowed provenance/evidence references. Never render raw system prompts, tool schemas or arguments, protected RAG content, credentials, or provider/runtime configuration.
- Version history uses returned redacted diffs and rationale/evidence references. “Edit & Propose as vNext to Commons” is rendered only when its authorized action reference is eligible and submits one idempotent proposal command.
- User and training guides are server-provided, redacted documents. Any suggested improvement or regeneration is an inert proposal or a separately authorized server-governed command.

**Tab 3: Playground (Now with Common Context + Eval)**  
- Chat/test interface same polish.  
- New toggles: "Test against Common Eval Harness" (runs standard metrics + rubric, shows scores), "Simulate in Common Pattern context" (injects typical upstream from the pattern this agent is usually used in).  
- "Compare to other versions of this Common Agent" side-by-side or batch.  
- After test: "This run's output qualifies as high-quality — contribute distilled insight to Common Knowledge?" toggle.

**Tab 4: Backed Knowledge + Common Contribution**  
- Per-agent RAG same as before.  
- New "Common Knowledge Subscriptions": which shared collections this common agent draws from + contribution stats (how much this agent/version has added to commons via verified runs).  
- "Propose new common knowledge chunk from successful runs" (with provenance & verification).

**New Tab or Section: Ops & Rollout (for common agents)**  
- Where used: List of active SwarmInstances + businesses using this exact version. Health indicators.  
- Rollout controls: "Safe rollout to all my swarms" (with impact analysis: expected metric changes, affected count). Canary options, A/B test setup (split traffic or specific swarms to new version). Approval workflow if shared commons.  
- Deprecation warnings, migration helpers for breaking spec changes.

This tab set turns every common agent into a living, collectively improved asset with full ops visibility.

### Ui6: Big Activity History & Ops Intelligence (Fleet + Common Component View)

**Header + Filters**: Date, business, swarm, **Common Agent / Pattern filter** (multi-select from registry), status, "Only show runs using outdated common versions", search.

**Views**:

**A. Subworkflow / Pattern Column Board (your original request, enhanced)**: Columns per instantiated Common Pattern or major sub-swarm phase. Cards now show which common agent versions were active, any deviations/forks, and quick "Update commons in this run's pattern" or "View common component health".

**B. Detailed Table**: Added columns "Common Agents (versions)", "Pattern Deviations", "Contributed to Commons? (knowledge/eval signals)".

**C. Timeline/Gantt per SwarmInstance or aggregated across commons**: Shows execution with common version labels on bars. Useful for seeing impact of version changes over time.

**Insights Panel (rethought as Ops Intelligence)**:
- "Common Component Health Trends": Which common agents/patterns are improving or degrading globally or in your usage.
- "Rollout Opportunities": "CommonVerifierAgent v1.8 shows +12% verification pass rate. Safe to rollout to  your  swarms using older versions?"
- "Collective Improvement Impact": "Your contributions + usage data helped improve 4 common agents this month, saving est. X tokens across the ecosystem."
- Anomaly detection tied to common versions (e.g. "After v2.1 rollout, error rate on ReportAgent increased in 3 swarms — investigate or rollback?").
- Bulk actions: Select runs or affected by specific common version → bulk replay with updated commons, bulk contribute signals, create improvement proposal.

**My Rethought Addition**: "Common Version Timeline" view — for a specific CommonAgent, horizontal timeline of its versions with key metrics at each version (success, tokens) and "what changed / why proposed" from meta-critic. Click version → see which swarms benefited.

This page becomes the command center for both individual swarm debugging *and* steering the commons.

### Ui7+: Additional UIs (Common Registry Hub as Star Feature, Ops Rollouts, Eval Dashboard)

**New/Enhanced: /registry — Common Registry Hub (Discovery + Contribution + Governance)**  
This is the heart of "common-agent-swarm-ops" frontend. Prominent nav item.

- **Search & Discovery**: Generated semantic/facet filters (domain tags, returned success rate, token-efficiency tier, last improved, compatibility, `used_by_me`, and verification support) present rich authorized cards or tables. Cards render only redacted name/version, description, aggregate metrics, usage, returned rationale/evidence references, and Action_References such as “Add to Swarm,” “Fork,” “Propose Improvement,” “View Authorized Eval Summary,” or “Preview in Mini Graph.”
- **Categories & Curated Collections**: "Core Patterns" (parallel, hierarchical, verification loop, debate), "Domain Specialists" (Trading Analyst, Content Director for wuxia/anime/YouTube, DSE ICT Tutor, Legacy Code Modernizer, Distributed Data Fetcher for Moltbot-style), "Experimental / Community".
- **My Contributions / Forks**: Section for your custom forks and proposals.
- **Governance (for maintainers/admins)**: Pending-proposal projections show redacted diffs, authorized evidence references, returned rationale, and impact summaries. Approve, merge, request-change, or evaluation controls appear only as current Action_References; the backend evaluates and applies any transition under its own policy and audit rules.
- **Stats Dashboard for Registry**: Returned common counts, improvement velocity, authorized/anonymized contributor summaries, and cost/efficiency aggregates.

**/ops or enhanced Monitoring**: Dedicated fleet operations view with returned rollout, canary, A/B, approval, and rollback projections. It displays server-governed stop/rollback outcomes and renders only eligible rollout actions. “Swarm Blueprints” are authorized saved pattern-and-version projections.

**/eval — Common Eval & Improvement Dashboard**: Returned harness summaries, proposal/evidence projections, and server-generated improvement candidates for review. Campaign creation or review is available only through an eligible Action_Reference.

**Other Enhancements**:
- Settings: Common Registry sync preferences, contribution defaults (auto-propose knowledge? require human review for agent improvements?), A/B testing defaults, common version pinning policy per business ("always latest safe" vs "pin until I approve").
- Templates Gallery → now "Common Patterns & Swarm Blueprints Gallery" with the rich previews and one-click instantiate + customize.
- Knowledge: Explicit "Contribute to Commons" flow with verification step (run through eval harness or human review).

---

## 5. Key Interactions & Polish (Common & Ops Focused)

- **Command Palette Evolution**: Even more powerful — "update all my swarms to latest safe common agents", "find common patterns good for verification-heavy tasks", "show me swarms where CommonReportAgent underperforms and suggest fixes", "contribute last successful run's insights to commons".
- **Provenance & Lineage Everywhere**: Hover or click any common reference → shows version, when linked, aggregate impact, improvement history link.
- **Safe Evolution of Commons**: Changes to common specs are versioned. Breaking changes trigger migration helpers or deprecation warnings in affected swarms. Rollouts are deliberate ops actions, not silent.
- **Collective Intelligence UI**: "This improvement to CommonMarketPredictor came from analysis of 4,200 runs across 67 swarms (including 12 of yours). Key insight: added X verification step reduced hallucinations by Y%."
- **Mobile Ops**: Push notifications for rollout approvals, common agent health degradation, high-cost anomalies. Quick approve/reject or "view impact".
- **Export/Portability:** Offer a standardized Common Swarm Definition or generated code export only when a server-authorized export action returns a redacted, policy-approved artifact. Import from other tools submits an untrusted reference or content through an authorized server ingestion contract; the browser neither fetches remote sources nor performs mapping itself.
- **Onboarding:** Tour emphasizes “Start by exploring the Common Registry — these are battle-tested building blocks improved by authorized community/organization usage.”

---

## 6. Data Models (Authorized Projection Shapes — Align with Backend)

The browser does not own these backend records or hand-copy their DTOs. It renders generated `/api/v1` authorized projections whose fields may be redacted or omitted for the active session:

- **CommonAgentVersion projection**: immutable ID/version/status, authorized role and policy summaries, output-schema summary, aggregate metrics, and provenance/evidence references—never raw prompts, credentials, tool payloads, or protected retrieval content.
- **CommonSwarmPatternVersion projection**: immutable ID/version, redacted graph/layout representation, description, compatibility, usage, and metric summaries.
- **SwarmInstance and Run projections**: opaque IDs, pinned pattern/agent provenance, returned graph/task lifecycle, freshness, metrics, recovery state, and eligible Action_References. Organization identity remains server-derived.
- **ImprovementProposal and rollout projections**: returned redacted diff/evidence, status, impact, criteria, approval, rollback, and action eligibility—not client-created policy, trace, or rollout data.

Generated contract changes, not this document, define the actual request and response shape.

---

## 7. Implementation Phasing (Common-First Priority)

**Phase 1 (MVP for common-agent-swarm-ops identity)**: Login + Dashboard (common health + fleet), Common Registry Hub (search, cards, basic stats, instantiate), basic Canvas with linked Common Agent nodes + simple groups (BIG ROWs for parallel), basic Agent Detail (history + authorized configuration/evidence summaries + proposal stub), and Activity with common-version filters. Generated REST snapshots plus authorized SSE observation provide status with sequence checking and REST resynchronization. Seed views only from supported generated contracts and authorized example projections.

**Phase 2**: Full graph features (cycles, routers, verification loops, dynamic), cross-swarm usage in Ui5/Ui6, Ops rollout/A/B UI, aggregate insights in dashboard/activity, Common Eval harness integration in playground, knowledge contribution flows. Polish Registry (proposals, diffs, governance).

**Phase 3**: Advanced self-improvement (meta-critic deeply integrated, auto-proposals from aggregate data), A/B and canary at scale, mobile PWA ops views, full i18n + Cantonese examples, export to common lib code, deeper Moltbot/distributed runtime support in canvas/ops, community/shared commons mode.

**Phase 4**: Ecosystem (public registry contributions if desired, integration marketplace for tools/nodes, advanced tracing/visualizations, cost governance campaigns).

---

## 8. Why This Deep Redesign Wins for common-agent-swarm-ops

- **Matches Repo Name & Intent**: "Common" is not an afterthought — it's the core value prop and visible in every major screen (Registry Hub, linked nodes, cross-swarm stats, collective improvement, provenance).
- **Ops Reality**: Production users don't just build once; they run fleets, update components safely, measure aggregate impact, and benefit from collective learning. This UI delivers that.
- **2026 Agent Trends + Your Vision**: Graphs + verification/iteration loops (beyond simple chains), self-refinement applied at commons scale (N1ch01as Architect at ecosystem level), distributed/Moltbot inspiration in patterns and ops, strong HK/creative/trading/education templates.
- **Differentiators vs n8n/Langflow/Dify**: Deeper standardization + reusability (like a "Hugging Face for Agent Swarms" + "npm for patterns"), built-in collective improvement loops, ops/control plane for common components across swarms (rollouts, A/B, impact), graph-native for modern agent organizations.
- **Extensible & Future-Proof**: Adapters for any backend/runtime, exportable standards, contribution workflows that grow the commons.

This version has been rethought extensively for coherence with the repo name, your broader work (Moltbot, templates, self-refining agents, large knowledge corpora, bilingual content), and the evolving multi-agent landscape. It positions **common-agent-swarm-ops** as the go-to self-hosted/common foundation for serious, improvable, observable agent swarm operations.

---

**Next Steps Recommendation**:  
Review this v2.1 against your actual repo structure/code (backend models, existing agents/patterns, Moltbot details). I can then:
- Generate specific code (e.g. RegistrySearch component, CommonAgentNode in React Flow, proposal diff viewer).
- Create visual mockups of the Registry Hub or canvas with common linked nodes + BIG ROW parallel groups.
- Refine data models or add exact TypeScript interfaces matching your backend.
- Seed example Common Patterns/Agents based on your YouTube/videos or specific needs (trading swarm, DSE tutor with verification, content pipeline with verification loop, etc.).
- Create the additional `nn_ui_XX_*.md` spec files for UIs 08–20.
- Iterate further on any section.

The file is ready in `/home/workdir/artifacts/frontend_redesign.md`. This is a living spec — let's make common-agent-swarm-ops exceptional. What would you like to tackle first?

---

## Complete UI Inventory for Authorized Operations & Visibility (Aligned in v2.2)

To give users comprehensive **authorized visibility and permitted operational actions** across commons governance, fleet operations, knowledge, evaluation, costs, security, integrations, auditing, collaboration, and extensibility, the following additional UI concepts are included. Each remains subject to the generated `/api/v1` contract, redacted projections, server-issued action references, and the document-wide browser boundaries above.

### Ui8: Global Settings & Configuration (`/settings`)
**Purpose:** Authorized visibility into supported workspace preferences, policy summaries, and defaults.

**Key Capabilities:** Render server-provided session, workspace, role, policy, version-pinning, budget, and approval summaries; expose preference or administration controls only through returned Action_References. Provider configuration, credentials/secrets, integration connection tests, and backend policy authority remain server-side and are never browser-managed.

**Layout:** Tabbed redacted projections with returned eligibility, freshness, and impact warnings; pending or stale controls remain disabled.

**Authorized Operations:** Users can inspect supported settings and submit only server-governed idempotent changes that their current session is authorized to perform.

### Ui9: Advanced Monitoring, Tracing & Alerts (`/monitoring`)
**Purpose:** Redacted fleet observability, performance awareness, and permitted operational response.

**Key Capabilities:** Authorized real-time status projections, redacted trace/evidence references, alert summaries/history, returned metrics aggregates, and returned anomaly/cost signals. Any alert response, export, or recovery operation appears only as an eligible Action_Reference; the browser cannot author monitoring rules, run arbitrary queries, access raw traces, or enact automated controls.

**Layout:** REST-backed cards and tabs (Activity, Evidence, Alerts, Metrics) enhanced by sequence-checked SSE observations; each labels `as_of`, freshness, and reconnecting/degraded state.

**Authorized Visibility:** Operators can trace returned redacted summaries to versions and patterns, then invoke only supported server-governed actions.

### Ui10: Knowledge Management Hub (`/knowledge`)
**Purpose:** Authorized knowledge and artifact discovery with governed contribution and ingestion.

**Key Capabilities:** Collections and source projections with returned health, provenance, ownership, retention, scan/indexing state, and eligible contribution/reindex actions. Git, Strapi, URL, and bulk sources are submitted as untrusted references or content to server-side ingestion; no browser fetch, remote embed, or client-side sync occurs. Search, chunking, and graph views render only returned redacted results and Action_References.

**Layout:** Hub cards and a detail drawer for returned Sources, Test, Status, Contribution, and Analytics projections.

**Authorized Visibility:** Users can review safe knowledge status and request permitted contribution or maintenance commands without receiving protected source content or bypassing validation.

### Ui11: Eval & Self-Improvement Dashboard (`/eval`)
**Purpose:** Visibility into collective commons performance + tools for systematic improvement campaigns.

**Key Capabilities:** Aggregate harness scores & trends across commons; Proposal campaigns (batch eval → auto proposals); Improvement history with before/after metrics & impact; Custom rubrics; A/B & canary results with stats; Meta-critic insights (failure modes, optimization hotspots).

**Layout:** Scorecards + charts; Proposal queue; Campaign launcher; Timeline with deltas.

**Authorized Improvement:** Review returned performance/evidence projections and submit only eligible, server-governed improvement commands.

### Ui12: Notifications Center (`/notifications`)
**Purpose:** Actionable, centralized alerts and updates hub.

**Key Capabilities:** Unified inbox (swarm events, common updates, proposals, cost/alerts); Smart grouping & priority; One-click actions (deep links to canvas/approval); Preferences & delivery (in-app, email, Slack/Telegram, PWA push); Full history & search.

**Layout:** List/kanban with filters & rich actionable cards. Global bell badge.

**Operational Awareness:** Stay informed through returned redacted notifications and eligible deep links without manually polling.

### Ui13: User Profile & Preferences (`/profile`)
**Purpose:** Session-safe personal preferences, usage insights, and contribution visibility.

**Key Capabilities:** Returned account/SSO session summary, personal usage and contribution projections, and authorized UI preferences such as language, theme, and defaults. The browser does not issue, display, store, or manage API tokens, credentials, or automation access.

**Layout:** Clean returned-profile and impact cards with eligible preference Action_References.

**Authorized Visibility:** Users can review their own authorized account and commons-participation information without acquiring additional authority.

### Ui14: Audit Logs & Compliance (`/audit`)
**Purpose:** Authorized, redacted audit and compliance visibility.

**Key Capabilities:** Immutable authorized audit projections for configuration changes, runs with common versions, proposals, rollouts, and contributions; generated filters, redacted detail/evidence references, and server-authorized export/report actions where supported. Audit views never expose secrets, credential access details, raw payloads, or protected resource state.

**Layout:** Virtualized redacted table with generated filters, eligible export controls, and evidence-reference detail.

**Authorized Visibility:** Provides accountable records within the current session’s permission scope.

### Ui15: API & Developer Portal (`/api` or `/developers`)
**Purpose:** Documentation and integration guidance for the governed public contract.

**Key Capabilities:** Generated OpenAPI reference, generated-client examples, supported extension/contribution guidance, redacted rate-limit status, and only those webhook or integration projections/actions that the server authorizes. Any interactive request uses the generated `/api/v1` contract and session context; this browser view does not issue or manage personal access tokens, credentials, raw webhooks, or unrestricted automation.

**Layout:** Contract-backed docs explorer, generated examples, and authorized integration/evidence projections.

**Governed Automation:** CI/CD, scripts, and bots remain separate authenticated clients subject to the same server contracts, policy, and idempotency requirements.

### Ui16: Onboarding, Help & Documentation (`/onboarding` or contextual)
**Purpose:** Fast adoption and proficiency with the common layer.

**Key Capabilities:** Interactive product tour; Contextual help ("?" + AI chat or your YouTube videos, bilingual); Searchable docs hub (concepts, patterns with visuals, governance, API, troubleshooting); Sample guided projects; Contribution & feedback forms.

**Layout:** Onboarding flow + persistent help center + in-app tours.

**Guided Use:** Users learn how to build, govern, and contribute through authorized product flows.

### Ui17: Mobile / PWA Companion Views
**Purpose:** On-the-go authorized visibility and permitted operations.

**Key Capabilities (read-heavy):** Dashboard summary, activity feed, notifications, Registry search, agent-detail history/operations, and approval views rendered from redacted projections. Replay, update-to-latest, or decision controls are visible only when their server-returned Action_References are eligible and the projection is fresh. PWA/offline storage is limited to a session-safe cache; cached views are explicitly stale and cannot invoke freshness-critical actions.

**Layout:** Responsive or dedicated simplified views (cards, bottom nav, 44px targets). Read-only mini graphs show returned state, freshness, evidence references, and permitted actions.

**Authorized Operations:** Monitor on phone or tablet and submit only the same server-governed idempotent intents available to the current session.

### Ui18: Collaboration, Sharing & Multi-User (Phase 2+)
**Purpose:** Authorized team and cross-workspace collaboration on swarms and commons.

**Key Capabilities:** Server-issued sharing or embedding references, authorized role/workspace projections, comments and mentions, proposal review, and eligible publishing actions. Any collaborative canvas state is a server-governed revision projection observed through authorized REST/SSE; the browser does not establish peer authority, use a direct CRDT channel, or bypass graph revision, governance, and audit checks.

**Layout:** Sharing dialogs, authorized presence/status projections, comment sidebar, and team widgets.

**Authorized Collaboration:** Teams collaborate within returned permissions and retained audit evidence.

### Ui19: Cost Governance & Usage Analytics (`/costs`)
**Purpose:** Financial visibility and optimization of LLM spend.

**Key Capabilities:** Usage breakdown (business, pattern, common agent/version, model); Budgets & alerts with actions; What-if simulators for common updates; Reports/export; Token efficiency leaderboards; Optimization recommendations.

**Layout:** Analytics dashboard with charts, budget cards, simulator, recommendations.

**Authorized Cost Operations:** Review redacted cost projections and invoke only eligible budget or optimization actions.

### Ui20: Swarm Blueprints & Saved Templates Management
**Purpose:** Capture, share, and govern known-good compositions on the common layer.

**Key Capabilities:** Blueprint gallery (Common Pattern + pinned agent versions + params + knowledge, rich previews, past metrics); Versioning, deprecation, promotion to official; Personal/Team/Common visibility; Quick "Save current as Blueprint" from canvas/activity.

**Layout:** Gallery with search/filters + detail with preview + "Use Blueprint" CTA.

**Authorized Blueprint Use:** Discover standardized, governed compositions and invoke only returned blueprint actions.

---

**These 20 UI concepts together provide comprehensive authorized visibility and server-governed action paths** across common-agent-swarm-ops—from commons discovery and collective improvement to fleet operations, security, extensibility, mobile access, and cost governance. Detailed per-screen specifications must consume generated `/api/v1` REST projections and authorized SSE observations; they must never add authority beyond returned Action_References.


---

## VA-Agent-Swarm Structure Compatibility

All screens and backend contracts implementing this redesign must follow [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). The common-first entities are domain-neutral extensions, not replacements for VA's AgentDefinition, task/DAG/lifecycle, artifact handoff, critique, L1/L2/L3 quality, approval, and provenance contracts. The mapping defines the required versioning, redaction, governance, and UI data rules.


## Overview

The frontend is a common-first, graph-native control plane for versioned agents, reusable patterns, governed swarm execution, and fleet operations. VA video-production structures are supported through the domain-adapter rules in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md).

## Requirements

### Requirement 1.1: Common-first provenance

Every rendered agent, pattern, graph node, run, artifact, and rollout shall resolve to immutable version and provenance references.

### Requirement 1.2: Governed graph operations

Canvas, activity, approval, and rollout experiences shall show task lifecycle, quality/gate evidence, and recovery eligibility while sending all mutations through authorized backend commands.

### Requirement 1.3: Domain-adapter completeness

When VA production data is present, the frontend shall support its agent contract, task lifecycle, artifact handoff, critique, L1/L2/L3 quality, approval, and provenance structures.

## Architecture

The browser consumes only versioned, redacted control-plane REST and event contracts. Shared design components render Common Agent/Pattern/Swarm projections; route-specific views provide registry, composition, graph, operational, knowledge, evaluation, audit, and blueprint experiences. Domain fields are optional for generic entities but mandatory in VA-adapted projections.

## Components and Interfaces

The shared interface surface comprises `CommonAgentVersionSpec`, `CommonSwarmPatternVersion`, `SwarmInstance`, `SwarmTaskProjection`, `ArtifactProjection`, `CritiqueProjection`, `QualityGateStatus`, `ApprovalProjection`, and redacted event envelopes as defined by the mapping document. UI actions carry opaque server-issued resource IDs and idempotency context; they never carry tool credentials, approval operations, or raw privileged input.

## Data Models

Common Agents and Patterns are immutable semantic versions. Swarm Instances are revisioned graphs containing pinned versions or explicit fork provenance. Runs preserve graph revision, task lifecycle, checkpoints, artifact lineage, critique/gate evidence, costs, and quality results. Artifacts retain parent lineage, technical requirements, rights/consent, continuity, QC, targets, and provenance references.

## Correctness Properties

### Property 1: Reproducible common execution

Every execution view identifies the graph revision, pinned Common versions, and applicable artifact/checkpoint references.

**Validates: Requirements 1.1**

### Property 2: Governed action visibility

The UI renders quality, approval, retry, and rollout state from server-authorized projections and cannot manufacture privileged action payloads.

**Validates: Requirements 1.2**

### Property 3: VA adapter fidelity

VA-specific screens preserve required agent, workflow, artifact, critique, gate, and provenance information when it exists in the projection.

**Validates: Requirements 1.3**

## Error Handling

The UI renders redaction-safe, correlation-aware API errors and distinguishes validation, authorization, missing input, critique wait, approval block, retryable failure, and terminal failure. It does not expose internal tool errors, credentials, raw prompts, or private artifact data.

## Testing Strategy

Contract-test frontend types against versioned API/event schemas. Test graph/task lifecycle, artifact handoff validation, critique relationship rules, L1/L2/L3 display, approval blocking, pinned-version replay, and VA-adapter fixtures. Run focused component tests, frontend typecheck/build, and the SDD gate for implementation changes.
