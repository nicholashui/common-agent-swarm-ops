# Activity — functional specification

**Route:** `/activity` · **Auth:** required · **Component:** `ActivityHome`

## Functional requirements

### FR-ACT-001 Modes
- Board / Table / Timeline modes SHALL switch presentation.

### FR-ACT-002 Search & date range
- Search filters cards/rows locally.
- Date range control cycles local ranges and announces.

### FR-ACT-003 Facets & toggles
- Filter chips toggle local multi-select filters.
- Outdated/contributed toggles apply when present.

### FR-ACT-004 Selection
- Multi-select of cards MAY update local selected set.

### FR-ACT-005 Inspect actions
- Inspect/open actions use onAction/classifyAnnounce; governed ops fail closed.

### FR-ACT-006 Live update
- Live toggle is session UX; SSE requires host authorization.

### FR-ACT-007 Help
- `/docs/activity/{userguide,func_spec,test_scenario}.md`
