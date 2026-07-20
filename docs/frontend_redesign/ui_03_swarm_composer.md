# NN UI 03: Swarm Composer / Pattern Composer Spec

**UI ID:** nn_ui_03_swarm_composer  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0)  
**Related Main Doc Section:** Ui3 (rethought as Pattern-first + NL chat)  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
- Primary creation entry point: Turn goals into **Common Pattern + Common Agent** compositions quickly.
- Start from battle-tested **Common Swarm Patterns** (parallel BIG ROWs, verification loops, hierarchical, etc.) rather than blank canvas.
- NL chat powered by strong reasoning (Grok/meta) that recommends patterns + specific common agents, with rationale and metrics.
- Seamless handoff to Canvas (nn_ui_04) with pre-populated linked common items.
- Encourage contribution back to commons.
- Support bilingual input (English or 繁體中文 goals/prompts).

## Layout & Structure (Two-pane desktop; Mobile: Chat primary + bottom sheet or modal for patterns)

**Header (persistent):** Business switcher + Swarm name input (starts as "Untitled Swarm from [Pattern]" — editable) + "Save as Draft" / "Load Template" actions + Close (back to dashboard or previous).

**Main Split (flex, 55/45 or resizable):**

**Left / Main Pane (Chat Composer — 55-60%):**
- Chat interface (like high-quality OpenWebUI or Dify chat, but specialized).
  - System context banner (collapsible): "Common Swarm Architect • Recommends from Registry • Prioritizes verification, parallelism, token efficiency, collective improvement".
  - Message history (user + assistant, streaming).
  - Input area: Rich textarea (multi-line, Cmd/Ctrl+Enter send) + attach file (requirements .md/pdf parsed by backend) + voice input (optional) + model/params quick override (for meta reasoning).
  - Quick chips / examples below input: "Daily market intelligence swarm with verification", "YouTube wuxia cinematic pipeline + quality loop", "DSE ICT adaptive tutor with assessment", "Legacy COBOL analysis swarm (parallel + verifier)", "Moltbot-style distributed data processing".
- Assistant responses: Structured (recommended Common Pattern(s) + why, slot-by-slot Common Agent suggestions with version + rationale + est. metrics, risks, "Load into Canvas" primary CTA, "Fork & Customize Pattern" secondary, "Propose as new Common Pattern" if novel).
- Iteration: User replies "make the verification stricter" or "use cheaper models for initial filter" → assistant updates recommendation live.
- Bottom bar: "Regenerate", "Start from blank graph instead", "Save this conversation as template".

**Right / Side Pane (Common Pattern Browser + Preview — 40-45%):**
- Searchable grid or list of **Common Swarm Patterns** (cards or compact rows).
  - Each Pattern Card: Mini visual preview (small React Flow render or static Mermaid/SVG of structure — e.g. parallel BIG ROWs with 3 sub-groups), Name + version, short "when to use", key aggregate metrics (success, tokens, iterations), "used in X swarms", "Instantiate" button (populates chat recommendation or directly loads canvas), "Fork as Custom".
- When chat recommends a pattern: Auto-highlight / scroll-to in browser + show "Recommended for your goal" badge.
- Filters: Domain tags, Parallelism level, Verification strength, Cost tier, "Compatible with my current commons".
- "Suggest new Common Pattern from my goal" button → triggers meta-agent to draft a new pattern graph JSON for contribution.

**Preview Area (dynamic, in side pane or modal):**
- When pattern selected or recommended: Larger mini interactive (read-only) React Flow preview of the pattern structure with placeholder agent slots highlighted.
- Summary panel below preview: Total agents/slots, parallelism factor, est. aggregate cost/latency/tokens from real usages, verification coverage.

**Mobile Adaptation:** Chat full screen primary. Floating action button or bottom sheet for "Browse Common Patterns". Preview opens as bottom sheet or modal. "Load to Canvas" always prominent.

## Components (Key Custom Ones)

- **Specialized Chat**: Built on shadcn + custom message bubbles. Assistant messages use structured JSON rendering (cards for recommended pattern + agent slots) + markdown for rationale. Streaming via SSE or WS.
- **Common Pattern Card**: shadcn Card with embedded mini React Flow (or image placeholder + upgrade to live). Badges for metrics. "Instantiate" uses primary action style.
- **Mini Graph Preview**: Read-only @xyflow/react instance (smaller nodes, no editing, fit-view, mini-map optional). Shows BIG ROW groups for parallel patterns, cycle edges for verification loops, supervisor hub, etc.
- **Recommendation Cards** (in chat): Clickable to highlight in browser or auto-fill slots.
- **Command Palette tie-in**: "recommend common pattern for [goal]" routes to this composer with prefilled prompt.

## Data, State & API

**Fetches:**
- GET /api/commons/patterns (list with previews, stats, filters).
- GET /api/commons/agents/search (for slot suggestions).
- On chat message: POST /api/composer/recommend (streams structured response: pattern_id, agent_slots[{common_agent_id, version, rationale}], est_metrics, graph_suggestion).

**State (Zustand or local):**
- Current conversation thread (messages + recommendations).
- Selected/recommended pattern + agent slot fillings (linked common versions).
- Preview graph JSON (for mini React Flow).
- Business context (affects recommendations — e.g. trading vs education bias).

**Mutations:**
- "Load to Canvas": POST /api/swarms (create draft with graph from pattern + linked agents) → redirect to nn_ui_04 with id.
- "Propose new pattern": POST /api/commons/patterns/proposals with graph JSON + description.
- File upload → backend parses → enriches prompt context.

**Real-time:** Optional streaming of recommendation generation. WS for live registry updates if new patterns/agents added mid-session.

**Backend:** Strong structured output from LLM (Pydantic/ Zod validated). Pattern graph templates stored as JSON with placeholders. Meta-critic for quality of recommendations.

## Interactions & Flows

**Primary "Goal → Recommended Composition" Flow:**
1. User types goal (or selects quick chip) in chat.
2. Assistant streams structured rec: "Best starting Common Pattern: Parallel Independent + Verification Loop v1.4 (why: independent data/analysis branches benefit from parallel + final verifier reduces hallucinations. Est. 23% token saving vs sequential from aggregate data)."
   + Agent slot recommendations with versions + "used successfully in 312 similar swarms".
3. User can accept all, tweak ("use cheaper model for data agents"), or ask for alternatives.
4. Prominent "Load Recommended into Canvas" → creates SwarmInstance draft pre-wired with linked common agents in the pattern structure → opens nn_ui_04 (canvas shows groups for BIG ROWs, verification cycles, etc., ready to run or edit).
5. Optional: "Save as my Custom Pattern fork" or "Propose to Commons".

**Pattern Browser Flow:**
1. Browse / filter patterns.
2. Click "Instantiate" → populates chat with "Start with this pattern for [goal]" or directly loads canvas with empty agent slots (user then fills from registry or lets chat recommend).
3. Hover card → updates live mini preview.

**Iteration & Refinement:**
- Chat supports multi-turn: "Add a human approval gate before trading execution", "Optimize for lowest cost", "Make it Moltbot distributed for data fetchers".
- Assistant maintains context of current recommendation and updates it.

**Handoff to Canvas:**
- Graph JSON includes `linked_common_pattern_id`, `linked_common_agent_versions` per node, positions for nice BIG ROW layout.
- Canvas opens in "design mode" with provenance pills visible on every common node.

**Error / Edge States:**
- No good matching pattern: Assistant proposes "Custom graph starting point" or "Contribute a new common pattern?".
- Low confidence rec: Shows alternatives + "Why this recommendation?" expandable (meta reasoning trace).
- Demo mode: All recommendations use demo commons; "Contribute" disabled or points to signup.

## Accessibility, i18n & Polish

- Full keyboard in chat (arrows for history, Esc to blur input).
- Structured responses have proper headings/landmarks for screen readers.
- Chinese input fully supported (IME friendly textarea). Assistant responses bilingual or match user language preference where possible.
- Loading states: Skeleton for pattern cards, streaming dots + partial structured cards appearing.
- Visual: Indigo for recommended/common items, clear visual hierarchy in chat (user right-aligned, assistant left with structured cards). Subtle animation when recommendation updates.

## Open Questions / Implementation Notes

- Exact structured output schema for /recommend endpoint (align with CommonPattern + slots).
- Depth of meta-critic in recommendations (simple vs full trace reasoning).
- Mini React Flow perf (many pattern cards — use static images or lazy-load live previews?).
- How much file parsing (PDF/MD requirements) happens client vs backend.
- "Voice input" priority (browser SpeechRecognition + send transcript).
- Saving partial conversations / branching recommendations.

## Wireframe / Key Screens (Text)

**Desktop Split:**
```
Header: [Business] [Swarm Name input]          [Save Draft] [Close]

┌──────────────────────────────┬──────────────────────────────┐
│ Chat Composer                │ Common Pattern Browser       │
│                              │                              │
│ User: Build daily trading... │ [Search patterns]            │
│                              │                              │
│ Assistant: Recommended:      │ ┌─ Parallel + Verification ─┐│
│ Parallel + Verification v1.4 │ │ [mini graph preview]      ││
│ Why: ... Est. metrics...     │ │ Parallel BIG ROWs visual  ││
│                              │ │ 94% success • 1.2k runs   ││
│ [Load into Canvas] [Fork]    │ │ [Instantiate] [Fork]      ││
│                              │ └───────────────────────────┘│
│ (more messages...)           │ (other pattern cards...)     │
│                              │                              │
│ Input: ___________________   │ Filters / "Suggest new..."   │
│ [Send]                       │                              │
└──────────────────────────────┴──────────────────────────────┘
```

**Mobile:** Chat dominant, "Browse Patterns" FAB → bottom sheet with cards + preview.

**Implementation Notes:** Use streaming (fetch + readableStream or tRPC subscription). Structured response rendering with React components for recommendation cards. Shared `MiniGraphPreview` component (read-only React Flow wrapper). Heavy reuse of Registry components (CommonAgentCard, PatternCard).

This composer makes starting with high-quality, collectively improved common building blocks the default, delightful path. Cross-reference main redesign for chat system prompt details, common pattern examples, and canvas handoff spec.


## VA-Agent-Swarm Composer Alignment

Composer recommendations and pattern templates must satisfy the Common Agent, graph/task, artifact handoff, critique, quality, and gate contracts in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). For VA patterns, recommend role slots/category, required artifacts, phase/template, dependencies, task constraints, peer-critique paths, quality thresholds, and human gates—not only agent names. Canvas handoff creates a revision with pinned versions and required validations.
