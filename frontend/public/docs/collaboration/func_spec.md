# Collaboration — functional specification

**Route:** `/collaboration` · **Auth:** required · **Component:** `CollaborationHome`

## Functional requirements

### FR-COL-001 List
- Display shared collaboration items from projection.

### FR-COL-002 Share UI
- Share modal open/close is local UX; permissions server-controlled.
- Copy link messaging is local-preview; not ACL grant.

### FR-COL-003 CTAs
- Merge/eval style CTAs fail closed without host stages.

### FR-COL-004 Help
- `/docs/collaboration/{userguide,func_spec,test_scenario}.md`
