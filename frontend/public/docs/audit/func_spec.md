# Audit — functional specification

**Route:** `/audit` · **Auth:** required · **Component:** `AuditHome`

## Functional requirements

### FR-AUD-001 Append-only projection
- Rows are redacted audit projections; UI cannot mutate history.

### FR-AUD-002 Search
- Filters actor/action/target/correlation/summary locally.

### FR-AUD-003 Filters
- Time range and actor cycle local options; action-type chips toggle filters.

### FR-AUD-004 Detail drawer
- Selecting row shows redacted detail, hashes, opaque links only.

### FR-AUD-005 Export / integrity / reports
- Require authorized compliance actions; fail closed otherwise.

### FR-AUD-006 Help
- `/docs/audit/{userguide,func_spec,test_scenario}.md`

## Out of scope
- Display of private tool parameters or secrets.
