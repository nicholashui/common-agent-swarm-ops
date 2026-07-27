# Monitoring / Operations — functional specification

**Route:** `/operations` · **Auth:** required · **Component:** `MonitoringHome`

## Functional requirements

### FR-OPS-001 Fleet cards
- SHALL display projected fleet metric cards with tones.

### FR-OPS-002 Search
- Local filter over traces/alerts text fields.

### FR-OPS-003 Sidebar filters
- Filter buttons cycle local values; announce selection.

### FR-OPS-004 Tabs
- Traces / Alerts (etc.) switch panels.

### FR-OPS-005 Trace tree
- Node select updates selection; expand evidence fails closed without host.

### FR-OPS-006 Alerts / recovery
- New rule, test notify, rollback, investigate fail closed without ops action refs.

### FR-OPS-007 Help
- `/docs/operations/{userguide,func_spec,test_scenario}.md`

## Out of scope
- Fabricated health probes for tenancy disclosure.
