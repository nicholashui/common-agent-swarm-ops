# NN UI 09: Advanced Monitoring, Tracing & Alerts Spec

**UI ID:** nn_ui_09_monitoring  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui9  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Provide deep, real-time observability and proactive alerting so operators can fully see and control fleet health, trace issues to specific common versions/patterns, and set automated responses.

## Layout & Structure
Dashboard layout with live updating cards + tabbed main area (Traces | Alerts | Metrics | Anomalies). Sidebar for filters/time range.

## Key Components
- Live Fleet Cards (running swarms count, common health summary, cost burn rate).
- Distributed Tracing Explorer: Expandable tree + horizontal timeline. Nodes colored by common agent/version. Click → deep link to nn_ui_05 or canvas.
- Alert Rules Table + Builder modal (condition builder with common agent/version selectors + action dropdown: notify Slack/Email/Telegram, pause swarm, create proposal).
- Metrics Explorer: Query builder + charts (Recharts/Tremor). Pre-built dashboards for common version impact.
- Anomaly Cards: Auto or rule-based, with "Investigate" or "Rollback" actions.

## Data & API
- WS for live metrics/status.
- Tracing API (tree data with timings, tokens, common versions, errors).
- Alert rules CRUD + firing history.
- Metrics time-series queries.
- Anomaly detection results.

## Interactions
- Trace node click → opens side panel or modal with full details + links.
- Alert rule create → test notification button.
- Anomaly card "Rollback common version" → impact modal + confirm.
- Time range sync across all views.

## Polish & Accessibility
Live regions for updating numbers/status. Virtualized trace tree for large runs. Keyboard navigation in tree. Bilingual. Dark theme optimized for data density.

## Wireframe Summary
Top: Live stats row. Main: Tabs. Left: Filters. Right (when trace selected): Detail inspector. Bottom or side: Anomaly feed.

**Implementation Notes:** Tracing is the most complex — use efficient tree rendering. WS critical for live feel. Impact analysis on version-related anomalies is high value for commons governance.


## VA-Agent-Swarm Monitoring Alignment

Monitoring subscribes to the redacted event and lifecycle contract in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). It must recognize task-state, artifact-created/updated, critique-created/resolved, approval-requested/resolved, budget, metric, memory, tool-completed, production-phase, and recoverable-error events. Event detail includes sequence, correlation ID, subject IDs, timestamp, and authorized reference data only.

Trace views must correlate a graph revision, task state transition, iteration/retry, checkpoint, common version, tool summary, artifact lineage, critique/gate decision, and quality result. Dashboards distinguish `blocked` by reason, `waiting_for_critique`, bounded `self_refine`, retryable failure, and terminal failure. Alerts for release, rights, consent, or provenance failures are treated as high-risk and link to gate/audit evidence rather than exposing sensitive material.
