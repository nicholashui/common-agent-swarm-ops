# NN UI 04: Visual Swarm Graph Canvas Spec

**UI ID:** nn_ui_04_canvas  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0 — Graph-Native + Common-Linked + BIG ROWs)  
**Related Main Doc Section:** Ui4 (core visual editor, deeply enhanced)  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation (highest effort UI)

## Purpose & Goals
- The main visual workspace for composing, editing, and running **Common Pattern-based swarms** with linked Common Agents.
- Make "common" provenance, live status, and collective improvement visible and actionable directly on the graph.
- Support modern graph features: parallel BIG ROW groups, verification/iteration cycles, dynamic routers, hierarchical nesting, consensus.
- Real-time execution visualization + ops actions (rollouts, A/B, partial replay) without leaving canvas.
- Frictionless contribution back to commons from the graph.
- Desktop power tool (large canvas) with keyboard-first + AI co-pilot.

## Layout & Structure (Desktop-heavy, large canvas area)

**Top Sticky Toolbar (full width, high density but clean):**
- Left: Swarm name (inline editable) + linked Common Pattern badge (clickable → opens pattern detail or update to latest) + version pill.
- Center: View mode toggle (Design / Run / Compare versions) + Common Agents status summary ("12/14 on latest common • 2 forks").
- Right: AI Co-Pilot button (dropdown or modal: "Optimize tokens", "Add verification where missing", "Propose as new Common Pattern", "Suggest dynamic router") + Auto Layout + Validate + Export (JSON/YAML/Python) + Run controls (Run / Run with params / Schedule / A/B test this swarm) + Share / More menu.
- When running: Prominent live status bar (overall progress, total cost so far, pause/cancel whole swarm) + streaming logs toggle.

**Left Sidebar (collapsible, resizable ~280px):**
- **Tabs or segmented:** "Common Registry" (default) | "Custom / Local" | "Patterns & Macros".
  - Common Registry: Searchable list/grid of Common Agents (compact cards or rows with version, success %, "drag to add linked version"). Click opens quick preview or nn_ui_05 in side panel/modal.
  - Custom: Local agents or forks (visually dashed/different accent).
  - Patterns: Draggable Common Pattern macros that expand into pre-wired sub-graph groups.
- "AI Suggest Node" input at top of palette.

**Main Canvas Area (flex-1, large, @xyflow/react powered):**
- Infinite pan/zoom grid background.
- **Nodes (highly custom, status-aware, provenance-clear):**
  - **Common Agent Node** (primary type): 
    - Header: Icon + Name + "Common vX.Y" badge (indigo accent, clickable to Registry or detail).
    - Body: Short role/goal snippet or current output preview (when running). Collapsible details (tools, attached common knowledge count).
    - Status strip (live or last): Color pill (Idle / Running pulsing amber with spinner or % or elapsed / Success green check + duration / Error rose) + key metrics (tokens, cost, last eval score).
    - Ports: Left input(s), right output(s). Standardized schema on hover.
    - Quick actions (hover or always compact): "Open Detail (nn_ui_05)", "Propose Improvement", "Replace with newer common version", "Isolate test in playground".
    - Visual: Border color = status, subtle glow/pulse for running, provenance "linked" indicator (chain icon or lock).
  - **Custom/Fork Node**: Similar but dashed border or different accent (violet), "Fork of Common vX.Y", "Contribute changes to Commons" prominent action.
  - **Sub-Swarm / BIG ROW Group Node** (key for parallel patterns):
    - Expandable/collapsible container with stronger visual treatment (tinted bg or thicker border, pattern name + version in header).
    - Header actions: "Update all internal commons to latest", "Add parallel shard", "Add verifier to this group".
    - When expanded: Contains child agent nodes arranged in rows or clusters (auto or manual layout for "BIG ROWs" parallel independent branches).
    - Aggregated status and metrics for the whole group.
    - Ports on group boundary for data handoff in/out of the sub-swarm.
  - Special Pattern Nodes: Supervisor (hub + spokes), Router (diamond/cloud icon, dynamic), Verifier (check + cycle back edge with iteration badge), Consensus (multi-input → vote output), Map/Reduce (fan icons).
- **Edges**: Animated when data/state flowing (in run mode). Different styles/colors for data vs control vs cycle. Labels with variable/schema. Click for details or delete.
- **Overlays / Helpers:** Mini-map (toggle), zoom controls, fit-view, search/highlight nodes (by name or common id), undo/redo stack, snap-to-grid toggle.

**Right Contextual Sidebar (resizable, contextual to selection):**
- Nothing selected: Swarm-level settings (description, tags, global retry/timeout, cost cap, notification channels, orchestration mode selector, linked common pattern info + "Update pattern" or "Contribute swarm as new pattern").
- Common Agent node selected: Registry info (current version stats, aggregate eval from all swarms, improvement history with meta-critic rationales) + quick "Update to latest safe", "Pin version for this swarm", "Propose improvement from this run's traces".
- Group selected: Pattern details, bulk actions on contained commons.
- During run: Live inspector (selected node output streaming, tool calls, token burn rate).

**Bottom Bar (optional, toggleable during run):** Streaming logs (filterable by node/agent/common), overall metrics, partial replay controls ("replay from this verifier failure").

## Components & Tech (Core is React Flow)

- **Custom Node Types** (registered in React Flow): `CommonAgentNode`, `CustomAgentNode`, `SubSwarmGroupNode`, `SupervisorNode`, `VerifierNode`, `RouterNode`, etc. Each with internal state for live updates.
- **Edge Types**: Animated data flow, cycle with iteration counter, conditional/router.
- **Controls & Background**: React Flow built-ins + custom (AI co-pilot floating button, common health mini indicator).
- **Layout Engine**: dagre or ELK.js for initial/auto layout, with special handling for parallel BIG ROW groups and hierarchical.
- **State Sync**: Optimistic for node moves/edits + backend save (debounced). Live run updates via WS push to specific nodes/groups.
- **Performance:** Virtualization or level-of-detail for very large graphs (50+ nodes). Collapse groups by default for overview. Search/filter dims non-matching.

## Data, State & Real-time

**Core Data Model (on load / save):**
- Swarm graph JSON: nodes[] (with position, data: {type: 'common-agent', common_agent_id, version, custom_overrides?}, group parent), edges[].
- Linked common versions pinned at creation or updated via ops actions.

**Fetches:**
- GET /api/swarms/{id}/graph (full definition + current common versions + last run status).
- GET /api/commons/agents (palette data).
- On run: WS subscription to `swarm:{id}:run:{runId}` for per-node status, partial outputs, metrics.

**Mutations:**
- Save graph (nodes/edges/positions + common links).
- Run / partial replay / pause.
- Bulk common version update on selection or group.
- Propose improvement (attaches current traces + local overrides).

**Real-time (critical):**
- Node status + metrics update without full re-render (React Flow node data update + custom internal component re-render).
- Edge animation start/stop based on flow.
- Group aggregate status roll-up.

## Interactions & Power Features

**Common-First Editing:**
- Drag Common Agent from left palette → creates linked node (provenance clear, "vX.Y from Registry").
- Right-click common node → "Update to latest common version" (with impact preview modal) or "A/B test alternative version here".
- Multi-select common nodes → bulk "Update all", "Propose improvements", "View cross-swarm usage".

**Graph Editing:**
- Connect ports (smart type checking if schemas defined).
- Drag nodes into/out of groups (re-parents).
- Keyboard: Delete, copy/paste (preserves common links), undo/redo, nudge with arrows, Cmd/Ctrl+A select all, Cmd/Ctrl+K scoped palette ("add verifier after this agent", "make this branch parallel").
- AI Co-Pilot: Analyzes current graph + goal → suggests additions (verification loop, router, parallelism), token optimizations, or "this structure matches Common Pattern X — link it?".

**Run Mode:**
- Canvas becomes live view (edits limited or in separate "design" tab).
- Nodes pulse/update live. Click running node → right sidebar shows live inspector (output stream, tool calls with timing, current eval score if verifier).
- Cycle nodes show "Iteration 3/5 • Verifier: iterating with feedback '...' ".
- Bottom or side: Global run controls + cost accumulator + "Partial replay from selected failure point".

**Contribution & Ops from Canvas:**
- "Propose this swarm structure as new Common Pattern" (extracts graph template + agent slots).
- During/after run: "Contribute successful outputs / insights to Common Knowledge" (with verification toggle).
- Rollout actions if this swarm uses commons heavily.

**Validation on Save/Run:**
- All critical paths have verification? Commons up to date? Schema compatibility? Cost budget respected? Warnings + auto-fix suggestions.

## Accessibility, Keyboard & Polish

- Full keyboard navigation on canvas (React Flow accessibility + custom).
- Live regions for status changes and run progress (screen reader announcements).
- High contrast status colors + patterns (not only color).
- Dark theme optimized for long canvas sessions. Optional "focus mode" (hide sidebars, larger canvas).
- Smooth animations (Framer Motion) for status changes, edge flow, group expand/collapse — performant.
- i18n: Node labels, tooltips, AI suggestions support Chinese where content allows.

## Open Questions / Implementation Notes (High Priority)

- Exact React Flow version + custom node/edge rendering performance on large graphs (test with 30–80 nodes).
- How to persist group collapse state + layout hints in graph JSON.
- Schema validation depth (frontend vs backend) for port connections and common agent I/O.
- Live streaming output inside nodes (how much detail vs summary to avoid perf hit).
- Conflict resolution if multiple users edit same swarm (Yjs CRDT later? simple last-write for v1).
- Exact AI co-pilot backend endpoint (graph JSON + goal → structured suggestions).

## Wireframe / Visual Key (Text + Description)

Large central canvas area with:
- Top toolbar dense but organized.
- Left palette with Common Registry search + drag.
- Example on canvas: Top-level group "Parallel Data & Analysis (BIG ROW)" containing 3 agent nodes in a row (DataFetcher Common, SentimentAnalyzer Common, Predictor Common). Separate "Synthesis + Verification" group with cycle edge back to a verifier node. Supervisor hub connecting to sub-groups. All common nodes show "Common vX.Y" indigo badges + live status.

**During Run:** Nodes light up with pulsing borders, edges have moving particles, iteration counters on cycle edges increment, right sidebar shows selected node live output.

**Implementation Priority:** Start with static Common Agent nodes + basic groups + drag from palette + save/load. Then add live WS status. Then special nodes (verifier cycles, routers). Then AI co-pilot + bulk common ops. Then performance optimizations.

Cross-reference main `frontend_redesign.md` for full node visual specs, common pattern examples, React Flow recommendations, and ops actions (rollout/A/B from canvas context). This is the highest-leverage UI — make the "common + graph + live ops" experience delightful and unmistakable.