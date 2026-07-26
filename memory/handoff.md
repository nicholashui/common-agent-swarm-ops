# Handoff

**As of:** 2026-07-26  
**State:** ui_00–ui_09 frontend redesign landings implemented; latest is ui_09 monitoring.

## Latest work

### ui_09_monitoring (current)
- Presentation monitoring matches `docs/frontend_redesign/ui_09_monitoring.md` + `.svg`.
- Files: `MonitoringHome.tsx`, `monitoring-landing.ts`, `MonitoringHome.test.tsx`, CSS in `globals.css`.
- Route: `/operations` → `MonitoringHome` (+ `ApprovalGateScreen` still for shared approvals menu item).
- Covered: live fleet cards, filters, Traces/Alerts/Metrics/Anomalies tabs, distributed trace tree, span inspector, alert rules, anomaly feed (incl. high-risk provenance), metrics bars.
- Safety: no host/queue/raw internals; high-risk → audit evidence only.
- Deferred: live SSE, real tracing API, alert CRUD, metrics query engine.

### ui_00–ui_08 (prior)
- Menu through settings landings complete under redesign presentation bar.
- Uncommitted since last commit may include ui_07–ui_09 work.

## Resume here

1. Dogfood `/operations`.
2. Commit ui_07–ui_09 when ready.
3. Next: knowledge (ui_10), eval (ui_11), …
4. Wire live monitoring projections when contracts land.

## Do not forget

- Constitution: Kiro + Claude Code only; no Gemini.
- Browser never owns authority; redacted events only.

## Validation checklist

- [x] Focused tests for ui_09 MonitoringHome
- [x] Frontend typecheck
- [ ] Full frontend `npm test` as needed
