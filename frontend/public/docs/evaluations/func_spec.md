# Evaluations — functional specification

**Route:** `/evaluations` · **Auth:** required · **Component:** `EvalHome`

## Functional requirements

### FR-EVAL-001 Campaign list
- Display projected evaluation campaigns and results.

### FR-EVAL-002 Run campaign
- Primary run SHALL invoke `eval.run_campaign` via action bridge when available.

### FR-EVAL-003 Governance CTAs
- Approve/merge/promote/reject SHALL fail closed without proposal+approval+canary authority.
- Eval pass alone SHALL NOT publish.

### FR-EVAL-004 Review panel
- Review shows redacted diff/impact only.

### FR-EVAL-005 Help
- `/docs/evaluations/{userguide,func_spec,test_scenario}.md`
