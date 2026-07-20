# NN UI 07: Common Registry Hub Spec (Star Feature for common-agent-swarm-ops)

**UI ID:** nn_ui_07_registry_hub  
**Version:** 1.0 (New central hub — aligned to v2.0 redesign)  
**Related Main Doc Section:** Ui7+ (Registry Hub as the heart of "common")  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation — prioritize early for product identity

## Purpose & Goals
- **The discovery, governance, and contribution heart** of common-agent-swarm-ops.
- Make reusable Common Agents and Common Swarm Patterns feel like a living, collectively improved library (think "Hugging Face for Agent Swarms + npm for Patterns" with ops depth).
- Drive adoption of commons, surface improvement opportunities, and lower friction for contribution/proposals.
- Provide governance tools (proposals review, impact analysis, rollout) so commons can be safely evolved at scale.
- Complement Canvas/Composer (drag from here) and Agent Detail (deeper dive).

## Layout & Structure (Dashboard-like hub, desktop-optimized with rich cards)

**Header (persistent + hub-specific):**
- Title "Common Registry" + subtitle "Battle-tested, versioned, collectively improved agents & swarm patterns".
- Search bar (prominent, semantic + facets) — "Search agents, patterns, or describe what you need...".
- Filters / Facets row (chips or sidebar): Domain tags (Trading, Content, Education/DSE, DevOps/Legacy, Distributed/Moltbot, General), Success rate >X, Token efficiency tier, Last improved, "Used in my active swarms", Verification support, Cost tier, Compatibility.
- View toggle: Cards (rich grid) | Table (compact) | Graph viz (future — knowledge or usage graph).
- Actions: "My Contributions & Forks", "Pending Proposals (for me / all)", "Suggest New from Goal" (opens composer-like flow), "Bulk Eval / Improvement Campaign".

**Main Content — Rich Card Grid (default, masonry or responsive columns):**

**Common Agent Cards (primary content):**
- Icon + Name + "Common vX.Y" badge.
- Short description / role.
- Key aggregate metrics row (with sparklines or deltas): Success % (global + trend), Avg tokens/run, Latency, Improvement velocity (e.g. "+7% efficiency last month").
- Usage stats: "Used in 1,248 swarms globally • 23 of yours • Last used 2h ago".
- Badges: Domain tags, "High Verification", "Parallel Optimized", "Moltbot Compatible", "Recently Improved (meta-critic)".
- Mini preview or "Preview in Pattern" (small graph snippet if often used in specific patterns).
- Actions row: Primary "Add to Swarm / Instantiate" (opens composer or canvas with this agent), "Fork & Customize", "Propose Improvement" (even if not using), "View Full Detail (nn_ui_05)", "View Usage & Impact".
- Hover: Subtle lift + quick stats expansion or mini eval report.

**Common Swarm Pattern Cards (secondary section or tab/filter):**
- Similar treatment but focused on structure: Mini visual preview (small React Flow or SVG/Mermaid of the pattern — e.g. parallel BIG ROWs with verification cycle, supervisor hub, debate nodes).
- "When to use" summary.
- Aggregate metrics from real instantiations.
- "Instantiate in Canvas" (pre-wires the pattern groups + placeholder slots) or "Fork as Custom Pattern".
- "Used as base in X swarms".

**Curated / Sections below grid:**
- "Core Patterns" (Parallel Independent, Hierarchical Supervisor, Verification/Iteration Loop, Debate & Consensus, Dynamic Router Graph, Map-Reduce).
- "Domain Specialists" (Trading Analyst vX, Content Director for cinematic/YouTube, DSE ICT Tutor with assessment, Legacy Modernizer, Distributed Data Agent for Moltbot-style).
- "Recently Improved" or "High Impact" (sorted by recent meta-critic proposals that delivered measurable gains).
- "My Forks & Contributions" (personal section with status: proposed / merged / rejected + impact).

**Governance / Admin Section (visible to maintainers or when proposals exist):**
- Pending Proposals Queue (table or cards): Proposal title, target Common Agent/Pattern, proposer (user or meta-critic), supporting traces count, expected impact, "Review & Merge" flow (opens diff viewer + meta-critic rationale + approve/reject/request changes buttons + auto impact analysis on affected swarms).
- "Auto-proposals from meta-critic this week" highlight.

**Right / Collapsible Sidebar (or top stats bar):**
- Registry Stats: Total Commons, Active Versions, Improvement velocity (proposals merged / month), Token/Cost savings realized ecosystem-wide, Top contributors (anonymized or credited).
- "Your Impact": How many improvements your runs helped trigger, savings in your swarms from using commons.
- Quick links: Full Eval Dashboard, Rollout History, Contribution Guidelines.

**Mobile:** Search + filters top. Cards stack vertically (rich but compact). Governance queue as list. "Instantiate" actions prominent. Desktop grid experience is the hero.

## Components (Rich & Interactive)

- **CommonAgentCard / CommonPatternCard**: Custom shadcn Card with embedded mini React Flow preview (lazy or static image fallback for perf), metric sparklines (Recharts tiny), badges, action buttons (primary/secondary sizes).
- **Search + Facets**: shadcn Combobox or Command-like with facets (checkbox groups for domains, sliders for success rate). Semantic search powered by backend (embeddings on descriptions + specs).
- **Mini Graph Preview**: Read-only React Flow (small, no interaction or limited) or pre-rendered SVG/Mermaid for patterns. Shows BIG ROW parallel structure, cycles, hubs clearly.
- **Proposal Review Modal/Drawer**: Side-by-side diff of spec/graph, meta-critic explanation, attached run traces (expandable), impact table ("This merge affects 87 active swarms globally, est. +X% success in Y domains"), approve/merge buttons with confirmation.
- **Diff Viewer**: Custom or library (e.g. for JSON/YAML or structured spec fields) — highlights additions, changes, with before/after metrics.

## Data, State & API

**Fetches:**
- GET /api/commons/agents (searchable, filterable, with aggregate stats, usage, previews).
- GET /api/commons/patterns (similar + graph templates for mini previews).
- GET /api/commons/proposals (pending + my contributions).
- GET /api/commons/stats (ecosystem + personal impact).

**Mutations:**
- Instantiate / Fork (creates draft swarm or custom copy).
- Propose improvement (POST with diff or full new spec + supporting data).
- Merge/approve proposal (governance action, triggers notifications + optional auto-rollout to affected?).
- Bulk actions on selected cards.

**State:** Active filters/search (URL sync for shareable registry views), view mode (cards/table), selected items for bulk, proposal review state.

**Real-time:** WS for new proposals, merged improvements (update cards live with new version/metrics), usage count bumps.

**Backend:** Efficient search (vector + keyword), materialized aggregate stats, proposal workflow with review state machine, impact analysis queries (which swarms use this exact version?).

## Interactions & Flows (Core Value)

**Discovery → Use Flow:**
1. Arrive or search "trading sentiment with verification".
2. See relevant Common Agent + Pattern cards with strong metrics and "used successfully in 312 similar swarms".
3. Click "Instantiate" or drag to canvas (if coming from composer/canvas) → pre-populates linked common version in recommended structure.
4. Or "View Detail" → nn_ui_05 for deep config/playground/eval/ops.

**Contribution & Improvement Flow (Collective Intelligence):**
1. From card or detail: "Propose Improvement" → focused form (current spec + suggested changes from meta-critic based on recent failures/successes across usages) + attach my recent traces option.
2. Submit → appears in Pending Proposals (with your name or "meta-critic assisted").
3. Maintainers/reviewers see in governance queue → review diff + rationale + impact → merge → new version live in Registry, cards update, affected swarms get notification/option to update.

**Governance Flow (for shared commons health):**
1. See pending proposals with high expected impact.
2. Open review → see before/after, meta-critic reasoning ("added verifier reduced hallucinations 18% across 2.1k runs"), affected swarms table.
3. Approve → merge happens, notifications sent, optional "safe rollout campaign" triggered.

**Personal / Ops:**
- "My Forks": See which of your customizations have been merged or have pending proposals.
- "Used in my active swarms": Quick filter to see only commons relevant to you + bulk update actions.
- Impact sidebar: Quantifies value of participating in the commons.

**Keyboard & Command Palette:** Full search/filter keyboard support. Command palette "find common agent for X", "propose improvement for CommonReportAgent", "review pending proposals".

## Accessibility, Polish & i18n

- Rich cards accessible (proper headings, ARIA for metrics/badges, keyboard focus on actions).
- Virtualized or paginated grid for hundreds of commons without lag.
- Dark theme with strong visual hierarchy (metrics prominent, badges clear, previews not distracting).
- Chinese support: Search, descriptions, prompts in proposals all handle 繁體中文 well. Translated UI.
- Perf: Lazy load mini previews or use static images with upgrade on interaction. Optimistic updates on merge/propose.
- Delight: Subtle animations on metric updates after merge, confetti or success state on contribution accepted (optional, tasteful).

## Open Questions / Notes

- Governance model details (who can merge? auto-merge for meta-critic proposals with high confidence + tests passing? org-private vs public commons?).
- How mini graph previews are generated/stored (pre-rendered images vs live small React Flow instances — perf trade-off).
- Semantic search quality (embeddings on what fields? spec + description + usage examples?).
- "Bulk Eval / Improvement Campaign" scope (select many commons → run common harness in batch → generate proposals).
- Credit / gamification for contributors (optional, "top improvers this month" — light).

## Wireframe / Visual (Text)

Top search + facets.

Grid of rich cards:
[TradingSentimentAgent Common v2.3 • 94% success ↑ • 1.2k runs • Used in 23 of your swarms • [Add to Swarm] [Propose Imp.] [Detail]]

[Parallel + Verification Pattern v1.4 • mini BIG ROWs preview • 91% • Instantiate]

Below: Curated sections "Core Patterns", "Recently Improved by meta-critic".

Right sidebar: Stats + "Your Impact: 4 improvements helped this month • est. $XX savings in your swarms".

Proposal review modal: Diff viewer + impact table + Approve button.

**Implementation Notes:** This is the identity UI for the product — invest in beautiful, information-dense cards and smooth proposal/review flows. Reuse PatternCard/AgentCard components across composer, canvas palette, and here. Mini React Flow previews shared with nn_ui_03 and nn_ui_04. Make contribution feel rewarding and low-friction so the commons grow.

Cross-reference main `frontend_redesign.md` for card content details, common pattern examples, proposal workflow, impact analysis, and how this hub integrates with every other UI (drag from here to canvas, link from agent detail, filter activity by commons from here, etc.). Build this early — it makes the "common" in common-agent-swarm-ops tangible and exciting from day one.

---

**Summary of Created UI Specs:**  
All core UIs from the v2.0 redesign now have dedicated, implementation-ready spec files:

- `nn_ui_01_login.md`  
- `nn_ui_02_dashboard.md` (Common Health + Fleet Ops)  
- `nn_ui_03_swarm_composer.md` (Pattern-first + NL)  
- `nn_ui_04_canvas.md` (Graph-native with BIG ROWs, common-linked nodes, live ops)  
- `nn_ui_05_agent_detail.md` (Tabs + cross-swarm ops + contribution)  
- `nn_ui_06_activity.md` (Board + Table + Timeline + common impact insights)  
- `nn_ui_07_registry_hub.md` (The star "common" discovery & governance hub)

These are self-contained, reference the main redesign, use consistent design system language (shadcn, React Flow, WS, etc.), and emphasize the common + ops + graph + collective improvement vision. They are ready for Cursor/Kiro/Claude Code, Figma handoff, or developer implementation.

You can now develop screen-by-screen with high fidelity. Let me know if you want code generation for any of these (e.g., the Registry Hub cards + search, Canvas CommonAgentNode component, proposal diff modal, etc.), visual mockups, or adjustments to any spec! 

This completes a full, actionable UI spec suite for common-agent-swarm-ops. 🚀


## VA-Agent-Swarm Registry Alignment

Registry cards and details must follow the Common Agent and Pattern contracts in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). VA-adapted entries expose category/role, architecture pattern, tool/knowledge summary, rubric and critique compatibility, runtime limits, required artifact schemas, phase/template compatibility, and provenance/release requirements. The 114-agent taxonomy is a domain facet; it does not replace the generic registry taxonomy.
