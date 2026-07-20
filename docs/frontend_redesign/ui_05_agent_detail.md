# NN UI 05: Common Agent / Instance Detail Spec (4+ Tabs)

**UI ID:** nn_ui_05_agent_detail  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0 — Registry + Cross-Swarm Ops)  
**Related Main Doc Section:** Ui5 (rethought with strong common + ops additions)  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
- Deep, first-class view into any **Common Agent** (or custom fork) — its spec, real collective performance, improvement history, and ops controls.
- Make contribution to / governance of the commons natural from here.
- Support isolated testing (playground) + contextual testing (in specific swarm/pattern).
- Cross-swarm visibility: "Where is this common agent used and how is it performing globally vs in my swarms?"
- Enable safe evolution (versioning, rollout, A/B, deprecation).

## Layout & Structure (Modal, drawer, or dedicated route `/registry/agents/{id}` or from canvas node click)

**Header (sticky):**
- Icon + Agent name + "Common vX.Y" badge (or "Custom Fork of Common vX.Y") + aggregate global stats (total runs, success %, avg tokens/cost, improvement velocity).
- Quick actions row: "Propose Improvement to Commons", "A/B Test this version vs newer in my swarms", "Fork to Custom", "Pin / Update in my active swarms", "Open in Registry Hub", "Run Isolated Playground".

**Tabs (horizontal, scrollable if needed — remember last used):**

**Tab 1: History + Cross-Swarm Usage**
- Filters: This swarm only / All swarms using this Common Agent (specific version or all) / Date range / Status / Has error?
- Powerful table (TanStack, server-side if large): Timestamp, SwarmInstance + Business, Pattern used, Status, Duration/Tokens/Cost, Input/Output summary (expandable), Error, "Replay with latest common" action.
- Insights strip above table: "This version used in 47 active swarms globally • Your business: 8 swarms • Success in your usage: 96% (global 91%)".
- "View full cross-swarm impact" expandable section or chart (performance distribution, bottlenecks downstream).

**Tab 2: Configuration / Spec (Versioned Common)**
- Structured form (React Hook Form + Zod) mirroring standardized CommonAgentSpec:
  - Core Identity (role, goals, backstory/persona).
  - System Prompt (large editable textarea with variable helper + "Improve with AI / meta-critic" button — sends current traces + failures for better version suggestion).
  - Model & Params (provider select, model dropdown from configured, sliders for temp/max_tokens/etc., JSON/structured output toggle + schema editor).
  - Tools (multi-select from standard registry + per-tool config).
  - Memory & RAG (short-term config, Common Knowledge subscriptions multi-select + retrieval params, test retrieval button).
  - Output Schema, Guardrails, Eval Rubric (common metrics + custom).
  - Advanced: Retry/timeout overrides, tags, metadata.
- Sub-sections / accordions: **User Guide** (Markdown editor + preview + "Regenerate from aggregate traces"), **Training Guide** (examples, few-shots, pitfalls + "Generate from history" button that pulls successful/failed runs).
- Versioning UI: Horizontal timeline or list of past versions with key metric deltas + meta-critic rationale for each change. "Compare versions", "Restore / Propose rollback".
- Raw JSON/YAML toggle (synced with form, validated).
- Prominent "Save as new version proposal to Commons" (with optional attached traces from this view or specific runs).

**Tab 3: Playground (Isolated + Contextual + Eval)**
- Main chat area (beautiful streaming chat, like OpenWebUI quality).
  - Options bar: Model/params override (temporary), "Enable Tools", "Stream", attach files for RAG test.
  - "Inject Workflow / Pattern Context" selector (choose a past SwarmInstance or paste upstream outputs) → simulates position in common pattern.
  - Tool call inspector (expandable per message or side panel): which tool, args, result, timing, token cost.
- Side / Bottom panels (tabbed):
  - **Eval Harness**: "Run Common Eval Rubric on this test" → shows scores on standard metrics (task success, groundedness, efficiency, etc.) + custom rubric. Batch test support (upload test cases CSV or from training guide).
  - **Compare Versions**: Side-by-side or batch run same prompt against multiple versions of this common agent → metric comparison table.
  - **Live Metrics for this session**: Tokens, cost, latency, tool usage.
- After good test run: "Mark as high-quality example for Training Guide" + "Contribute distilled insight to Common Knowledge?" (opt-in with provenance).

**Tab 4: Backed Knowledge + Common Contribution**
- Stats cards: Chunks, last indexed, embedding model, query count, contribution stats (how much this agent/version has added to commons via verified runs).
- Search test box + results (chunk text, score, source, metadata, "Add to current prompt" quick action).
- Sources management table: Name, type, status, chunks, added, actions (preview, reindex, remove, force contribute to common?).
- Add sources: Drag-drop upload, paste text, URL import, Git/Strapi sync (your large MD corpora friendly).
- Chunking & indexing config (per agent or inherit global/common defaults).
- "Distill / Synthesize to Common Knowledge" button (runs specialist meta-agent over collection → proposes compact summaries/entities for commons contribution, with verification step).

**Additional / Ops Tab or Prominent Section (for Common Agents):**
- **Where Used & Rollout Controls**:
  - Table or cards: Active SwarmInstances + businesses using this exact version + health indicators.
  - Rollout panel: "Safe rollout to all my swarms using older versions" with impact analysis table (expected metric deltas, affected count, risk flags). Canary / A/B test setup (select specific swarms or traffic split). Approval workflow if shared commons.
  - Deprecation / migration notes if newer version has breaking changes.
- **Improvement History & Proposals**: Timeline of past improvements (with diffs, rationales, before/after metrics). Link to pending proposals for this agent. "Create new proposal from current traces/failures".

## Data, State & API

**Fetches (per tab, cached where possible):**
- GET /api/commons/agents/{id}/versions/{version} (full spec + stats + history).
- GET /api/commons/agents/{id}/usage (cross-swarm + your business).
- GET /api/commons/agents/{id}/evals (aggregate + per-run samples).
- GET /api/commons/agents/{id}/knowledge (sources + stats).
- Playground runs: POST /api/playground/test-agent (with optional swarm_context, eval flag).

**Mutations:**
- Propose new version (POST /api/commons/agents/{id}/proposals with diff + supporting data).
- Rollout / A/B (POST /api/commons/rollouts).
- Knowledge contribution.
- Eval run (triggers common harness).

**State:** Active tab, current version being viewed (switchable), playground conversation state (exportable), filters in history tab, form dirty state with save prompt.

**Real-time:** Optional WS for live usage count or new eval results while viewing.

## Interactions & Polish

**Version Switching:** Dropdown or timeline click in header/tab2 instantly reloads spec + stats for that version (optimistic + background fetch).
**Propose Improvement Flow:** From Tab2 or Ops section → opens focused form (pre-filled with current + suggested changes from meta-critic) → attach specific run traces or "use all recent failures" → submit with impact preview.
**Playground → Contribution:** After high-quality or verified run, non-intrusive prompt or button to contribute.
**Cross-Swarm Navigation:** Click any swarm in Tab1 usage table → opens that SwarmInstance in canvas or activity (deep link with highlight on this agent).
**Keyboard & Accessibility:** Full form keyboard nav, shortcuts in playground (send, regenerate), ARIA for tabs/status, high contrast metrics.

**Visual:** Indigo/violet for common-specific elements. Clear "Common vs Custom" visual language. Version badges consistent across app. Loading skeletons per tab. Sonner toasts for successful proposals/rollouts.

**Mobile:** Tabs become accordion or swipeable. History table → card list. Playground chat excellent on mobile. Ops/rollout section prominent but collapsible.

## Open Questions / Notes

- Depth of meta-critic suggestions in "Improve with AI" (how much context from aggregate vs single run?).
- Eval harness implementation details (which standard metrics always included, how custom rubrics defined/stored).
- Rollout UI complexity (simple "apply to my swarms" vs full canary/A/B with traffic % and monitoring duration).
- How much of the spec form is auto-generated vs manual (e.g. tools list from central registry).
- Caching strategy for large history/eval data (virtualized table + server pagination).

## Wireframe Summary (Text)

Header with stats + quick actions.

Tabs: History | Config | Playground | Knowledge | Ops (for common)

**Tab 2 example (Config):** Form sections for Identity / Prompt / Model / Tools / RAG / Eval. Version timeline on side or top. "Propose vNext to Commons" big button at bottom. "This change in v2.1 improved token efficiency +7% across 1.8k runs — meta-critic: added X verification step."

**Tab 3 (Playground):** Chat on left, Eval/Compare/Inspector panels on right. "Inject Pattern Context" dropdown. After run: metric scores + contribution prompt.

This detail view turns every Common Agent into a transparent, improvable, governable asset with full ops visibility. It is the primary place users interact with the "common" layer deeply.

Cross-reference main redesign for standardized spec fields, eval metrics, contribution flows, and how this integrates with Registry Hub and Canvas. Implement tabs with shadcn Tabs or custom for persistence. Form heavy — use React Hook Form + Zod for validation + nice UX (collapsible sections, live preview for prompt).


## VA-Agent-Swarm Agent Contract Alignment

This detail view is the complete UI for the `CommonAgentVersionSpec` in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). The Configuration tab must add canonical name, category, in-scope/out-of-scope boundaries, escalation targets, approval authority, architecture pattern, model fallback policy, runtime limits (iteration, cost, concurrency, timeout, retries), and input/output schema references.

Tools must show allowed purpose/scope and audit requirement. Relationships must separately render `accepts_critique_from` and `comments_on`; invalid peer-critique links must be rejected by the backend. Quality displays the agent rubric and the L1/L2/L3 contract, not only a generic evaluation score.

The History/usage tab must show graph revision, task state, iteration/retry, artifact and critique references, gate outcomes, and pinned agent version. Playground supports task/artifact context, mock critique, bounded self-refine, cost estimate, tool trace summaries, quality results, and saved benchmark cases. Knowledge must distinguish RAG sources, few-shot examples, correction memory, constitutional rules, and evaluation benchmarks. Provenance/rights/continuity data are displayed when an output artifact or release decision is involved.
