# NN UI 14: Audit Logs & Compliance Spec

**UI ID:** nn_ui_14_audit  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui14  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Immutable, searchable, exportable record of all system actions for security, compliance, debugging, and commons governance.

## Layout & Structure
Dense virtualized table as primary view + expandable detail rows or side panel. Filters sidebar. Export toolbar.

## Key Components
- Audit Table: Timestamp, User, Action Type, Target (common agent/version, swarm, policy, etc.), Before/After summary, Status.
- Filters: User, business, common component, action category, date, success/failure.
- Detail Modal: Full diff (JSON or structured), linked traces/swarms, context.
- Export: CSV/JSON/Parquet with current filters.
- Pre-built Reports: Dropdown for common compliance queries.

## Data & API
- Append-only audit log queries (paginated, filtered, searchable).
- Diff generation for config changes.
- Export job (background for large results).

## Interactions
- Row click → detail modal with rich diff viewer.
- Filter changes update table live.
- Export button → progress + download link.

## Polish & Accessibility
Virtualized table for scale. Accessible sortable headers and expandable rows. High contrast for diffs. Bilingual action labels.

## Wireframe Summary
Top filters + export. Main virtualized table. Click row → side panel or modal with full diff and links.

**Implementation Notes:** Performance on large audit volumes is critical (indexing, pagination, background export). Diff viewer shared component with proposals. Essential for production and shared commons trust.


## VA-Agent-Swarm Audit Alignment

Audit views must retain the immutable lineage required by [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md): Common Agent/Pattern version, graph revision, task/dependency/gate transition, lifecycle iteration/retry, tool summary, artifact parent chain, technical/QC/rights/consent/continuity state, C2PA/provenance reference, critique record, quality evidence, human decision/comment, and correlation ID.

The audit timeline differentiates observation events from authoritative state transitions and signatures. Artifact and approval details are accessed through authorization-checked references. Users can inspect diffs and evidence but cannot mutate historical records, replace a C2PA/provenance reference, or infer private tool parameters from the audit projection.
