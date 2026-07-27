# Settings — functional specification

**Route:** `/settings` · **Auth:** required · **Component:** `SettingsHome`

## Functional requirements

### FR-SET-001 Sections
- Section nav switches preference groups from projection.

### FR-SET-002 Edits
- Field edits are local until save intent; save uses onAction/session prefs rules.

### FR-SET-003 Prohibitions
- MUST NOT enable production activation solely from settings.
- MUST NOT collect raw provider secrets in generic fields.

### FR-SET-004 Help
- `/docs/settings/{userguide,func_spec,test_scenario}.md`
