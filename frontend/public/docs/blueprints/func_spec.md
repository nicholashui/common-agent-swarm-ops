# Blueprints — functional specification

**Route:** `/blueprints` · **Auth:** required · **Component:** `BlueprintsHome`

## Functional requirements

### FR-BP-001 Gallery
- SHALL render projected blueprint cards with titles/summaries/safety notes.

### FR-BP-002 Search
- Local text filter over gallery fields.

### FR-BP-003 Instantiate
- Instantiate CTA SHALL require host action eligibility; otherwise fail-closed.
- SHALL NOT treat pack_spine as blueprint realization.

### FR-BP-004 Help
- `/docs/blueprints/{userguide,func_spec,test_scenario}.md`

## Out of scope
- Silent production agent activation from gallery.
