# Handoff

**As of:** 2026-07-26  
**State:** ui_00_menu frontend implementation reviewed, corrected, and tested.

## Latest work (ui_00_menu + destination unlock)

- Menu: `application-menu.ts` + `ShellNavigation.tsx` + light-rail CSS
- All menu destinations unlocked with local previews (no UnavailableScreen gates)
- Shared fixtures: `frontend/src/lib/projections/local-preview.ts`
- Operational routes use real renderers; secondary routes use `LocalDestinationPreview`
- Canvas: `/canvas` + `/swarms/[swarmId]/canvas` render `Canvas` (no invented swarm id)
- Operations: Monitoring + ApprovalGate local stack
- Tests: routes + menu + local-preview — pass; `tsc --noEmit` pass

## Resume here

1. Dogfood full menu navigation in browser (`.\start_all.ps1`).
2. Replace local previews with generated `/api/v1` projections as contracts land.
3. Wire shell projection for live freshness / authorized VA / correlation copy.
4. Unrelated WIP: `start_all.ps1` / `stop_all.ps1`, `.gitignore` `.run/`, bat helpers.

## Do not forget

- Constitution: Kiro + Claude Code only; no Gemini; no executing untrusted downloads.
- Architecture SoT: `structure.md`. Browser never owns authority.
- Video pack: 114 agents retained; spine-first activation order in `agent_implement_order_list.md`.
- `status.md` is stale relative to full platform code (still bootstrap-era wording).

## Validation checklist (when shipping)

- [ ] Focused tests for changed behavior
- [ ] `npm run sdd:check` (if SDD artifacts touched or gate required)
- [ ] `npm run sync:check` (if rules/skills/adapters changed)
- [ ] Frontend: `npm test` / typecheck / api:check as scope requires
- [ ] Backend: `pytest` as scope requires
- [ ] Update `status.md` after major work
