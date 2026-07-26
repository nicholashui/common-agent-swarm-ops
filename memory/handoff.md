# Handoff

**As of:** 2026-07-26  
**State:** ui_00–ui_06 frontend redesign landings implemented; latest is ui_06 activity.

## Latest work

### ui_06_activity (current)
- Presentation activity landing matches `docs/frontend_redesign/ui_06_activity.md` + `.svg`.
- Files: `ActivityHome.tsx`, `activity-landing.ts`, `ActivityHome.test.tsx`, CSS in `globals.css`.
- Route: `/activity` → `ActivityHome`.
- Covered: header (search, date, Board/Table/Timeline, Live Update), filters + outdated/contributed toggles, board columns (Data Ingestion / Analysis+Verification / Synthesis+Report), table with VA lifecycle/checkpoint fields, timeline lanes, Ops Intelligence sidebar (KPIs, rollout opportunity + anomaly, collective impact, bulk actions).
- Actions announce server-determined eligibility; preserve immutable version provenance messaging.
- Tests: `ActivityHome.test.tsx` + route check — pass. `npx tsc --noEmit` — pass.
- Deferred: live activity API, WS live updates, TanStack virtualization, real replay/rollout mutations.

### ui_00–ui_05 (prior)
- Menu, login, dashboard, composer, canvas, agent detail landings complete under redesign presentation bar.

## Resume here

1. Dogfood `/activity` (and dashboard → View all activity).
2. Commit ui_05 + ui_06 when ready (both uncommitted presentation landings).
3. Next redesign screen: registry hub (ui_07).
4. Wire live activity projections + authorized bulk actions when contracts land.
5. Unrelated untracked: `callgrok.bat`, `check_all_ui.bat`, `run_grok.bat`.

## Do not forget

- Constitution: Kiro + Claude Code only; no Gemini; no executing untrusted downloads.
- Architecture SoT: `structure.md`. Browser never owns authority.
- Video pack: 114 agents retained; spine-first activation order in `agent_implement_order_list.md`.
- `status.md` is stale relative to full platform code (still bootstrap-era wording).

## Validation checklist (when shipping)

- [x] Focused tests for ui_06 ActivityHome (pass)
- [x] Frontend typecheck (`npx tsc --noEmit`)
- [ ] Full frontend `npm test` / api:check as scope requires
- [ ] Update `status.md` after major work
