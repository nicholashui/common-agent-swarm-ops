# NN UI 02: Dashboard Spec (Common Health + Ops Fleet Overview)

**UI ID:** nn_ui_02_dashboard  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0)  
**Related Main Doc Section:** Ui2 (rethought as Common Health + Fleet Ops)  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
- Primary landing page after login/demo.
- Give immediate sense of **living commons** (health, improvement velocity, pending proposals) + **personal fleet ops** (running swarms, recent activity, impact of common updates).
- Drive users to Common Registry Hub and Composer/Canvas.
- Real-time feel via WebSocket for running swarms and common health signals.
- Bilingual + mobile-friendly for quick ops checks.

## Layout & Structure (Desktop 3-column responsive grid; Mobile stacked)

**Persistent Global Header** (across most pages):
- Left: Logo + Business/Workspace switcher (dropdown or pills: "Trading Lab" | "Content Studio" | "DSE DeepTutor" | "+ New Business"). Searchable if >5.
- Center: Global Command Palette trigger (Cmd/Ctrl+K — "search commons", "update my swarms to latest safe commons", etc.).
- Right: Notifications bell (common improvement proposals, rollout impacts, swarm failures) + User avatar (profile, settings, logout, language, theme).

**Main Content (max-w-7xl, mx-auto, pt-6):**

1. **Hero / Common Health Row** (4–6 stat cards, horizontal scroll on mobile, real-time):
   - Card 1: "Common Agents Active" — big number (e.g. 87 versions) + "across 142 swarms" + sparkline trend + "↑ 4 new improvements this week".
   - Card 2: "Global Success Rate" — 91.4% (↑1.2%) with mini chart.
   - Card 3: "Pending Improvement Proposals" — 3 (click opens Registry proposals tab) — color accent if urgent.
   - Card 4: "Your Fleet Health" — Avg success of your active swarms + "12 swarms using latest commons".
   - Card 5: "Est. Monthly Savings from Commons" — $XX (from token efficiency gains).
   - Optional 6th: "Top Improved Common This Week" — link to specific agent in Registry.

2. **Quick Common Actions** (prominent row or grid of large cards/buttons):
   - Primary: "Explore Common Registry Hub" (biggest, indigo accent) → /registry.
   - "Compose New Swarm from Common Patterns" → /composer or canvas with pattern picker.
   - "Review Improvement Proposals" (if any pending for commons you use).
   - "Run Eval on My Custom Forks" (contribute back flow).

3. **Your Swarms Fleet Ops** (two sub-sections side-by-side on wide, stacked on narrow):
   - **Running Now** (live section, WS updates):
     - Horizontal cards or compact list: Swarm name + linked Common Pattern badge + "X/Y agents on latest common" + live progress or status pills + elapsed + cost rate + "View Live Canvas" / "Pause" buttons.
     - Empty state: "No swarms running. Start one from Common Patterns →".
   - **Recent Activity** (last 8–10 runs):
     - TanStack Table or card list: Time, Swarm (clickable), Common Agents/Versions used, Status badge, Duration, Cost, "Replay with latest commons" action.
     - "View all activity →" links to nn_ui_06.

4. **Common Impact Insights** (AI-powered collapsible panel or dedicated section):
   - One or two smart cards generated from Ops service:
     - "Updating CommonReportAgent v2.1 → v2.2 would improve 19 of your active swarms (+15% latency, -$47/mo est.). Affected: [expand list]. [Approve Rollout for my swarms] [A/B Test First] [View Diff & Rationale]".
     - "Your usage data helped improve 4 common agents this month — view collective impact".
   - Powered by meta-critic + aggregate data. "Ask AI about my commons usage" quick prompt that opens command palette or chat.

5. **Pinned / Favorites** (optional, collapsible):
   - User-starred Common Agents, Patterns, or Swarms for one-click access.

**Footer / Subtle:** Last synced commons timestamp + "Contribute to the commons by running & verifying swarms".

## Components (Detailed)

- **Stat Cards**: shadcn Card + big number (text-4xl font-mono), trend sparkline (Recharts or lightweight), subtle live pulse on updating numbers.
- **Common Health Cards**: Use indigo/violet accents for "common" items. Success % in green.
- **Running Swarm Cards**: Status pill (Running with spinner, Success green, Error rose), Common Pattern badge (pill with version), "X common / Y total agents" indicator.
- **Table (Recent)**: @tanstack/react-table with virtual rows if many. Columns: Timestamp, Swarm Name + Pattern badge, Commons Used (avatars or count + tooltip), Status, Metrics (duration, cost, tokens), Actions (replay, view canvas, contribute signals).
- **Impact Insight Cards**: Border-left accent (amber for opportunity, green for positive). Buttons use shadcn variants. "View Diff" opens modal with side-by-side spec diff + meta-critic explanation.
- **Command Palette Integration**: Heavy use — pre-populate with dashboard-relevant actions.

## Data, State & Real-time

**Fetches (TanStack Query):**
- GET /api/commons/health (aggregate stats, trends, top improved, pending proposals count).
- GET /api/swarms/running (live list).
- GET /api/activity/recent?limit=10 (with common version info).
- GET /api/insights/common-impact (personalized to business + commons used).

**WebSocket Subscriptions:**
- `commons:health` — push updates to stat cards and insights.
- `swarms:running` — live status, progress, cost for running cards.
- `proposals:pending` — increment pending count badge.

**Client State:**
- Selected business/workspace (sync to URL or localStorage, affects all fetches).
- Demo mode flag + banner.
- Collapsed sections preferences.

**Mutations:**
- Approve rollout (POST /api/commons/rollout with list of swarm_ids or "all my swarms").
- A/B test setup.
- Star/unstar items.

**Backend Needs:** Aggregated queries efficient (materialized views or good indexing on usage + eval tables). Real-time via Redis pub/sub or similar.

## Interactions & Key Flows

**Common Health → Action:**
1. See high pending proposals → Click → Opens Registry with proposals filter.
2. See "Top Improved" card → Click agent name → nn_ui_05 Agent Detail.

**Fleet Ops:**
1. Running card "View Live Canvas" → nn_ui_04 with execution mode + highlighted running nodes.
2. Recent row "Replay with latest commons" → Triggers replay job using current common versions (shows confirmation modal with impact).
3. Insight card "Approve Rollout" → Modal: Impact summary table (swarm, expected delta, risk), confirm button (optimistic update + WS progress).

**Command Palette Examples on Dashboard:**
- "update all my swarms to latest safe common agents"
- "show swarms where CommonReportAgent is outdated"
- "propose improvement for MarketPredictor based on my last 10 runs"

**Empty / Error States:**
- No running swarms: Friendly illustration + "Start from Common Patterns" CTA.
- Commons health fetch fail: Retry button + cached last known.
- Demo mode: Persistent top banner with exit button (clears demo data).

## Accessibility, Responsive & Polish

- Keyboard: All cards/buttons reachable, Enter activates primary action.
- ARIA: Live regions for updating stats/numbers, status announcements for running swarms.
- Mobile: Stats row horizontal scroll-snap, cards stack, tables become cards or have "load more".
- Performance: Skeleton loaders for stats and lists. Debounced WS updates. Prefetch Registry and Composer on hover/intent.
- Visual Polish: Subtle Framer Motion on stat number changes and new running cards entering. Consistent Lucide icons (Activity, TrendingUp, Users, Zap, etc.). Indigo for common-related, violet for proposals/insights.

## Open Questions / Notes

- Exact metrics and aggregation logic for "Common Health" (confirm with backend).
- Personalization depth of "Common Impact Insights" (how much meta-critic vs simple rules).
- How many businesses/workspaces typical user has (affects switcher design).
- Notification center spec (separate but bell opens drawer with common + swarm alerts).
- Demo mode data lifetime and reset behavior.

## Wireframe Summary (Text)

```
Header: [Logo] [Business Switcher]          [Cmd+K]     [🔔] [Avatar]

Common Health
[Card: 87 Common Agents • 142 swarms • ↑4] [91.4% Success ↑] [3 Proposals] [Your Fleet 94%]

Quick Actions
[ Explore Common Registry Hub (big) ] [ Compose from Common Patterns ] [ Review Proposals ]

Your Swarms Fleet
Running Now: [Swarm A - Parallel Pattern v1.4 • 8/8 latest common • Running 12m • View Canvas]
             [Swarm B - ...]

Recent Activity
Table: Time | Swarm + Pattern | Commons Used | Status | Duration/Cost | Actions

Common Impact Insights
[Card: Update CommonReportAgent → improves 19 swarms. Approve | A/B | View Diff]
```

**Implementation Notes:** Build with shadcn/ui + Recharts/Tremor for charts + @tanstack/react-table. Heavy use of shared components from main design system (StatusBadge, CommonVersionPill, ImpactInsightCard). WebSocket hook `useWebSocket` shared across dashboard, canvas, activity.

Cross-reference main `frontend_redesign.md` for color tokens, common component patterns, and global command palette spec. This dashboard makes users feel they are operating on a living, collectively improving commons foundation.