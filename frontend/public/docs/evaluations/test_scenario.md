# Evaluations — test scenarios

| ID | Priority | Given | When | Then |
|----|----------|-------|------|------|
| TS-EVAL-001 | P0 | Auth | Open `/evaluations` | Campaigns render |
| TS-EVAL-002 | P1 | Run | Click run campaign | Runtime eval or busy/error status |
| TS-EVAL-003 | P0 | Approve merge | Click without ref | Fail-closed governance message |
| TS-EVAL-004 | P1 | Promote | Click | Fail-closed canary/rollback message |
| TS-EVAL-005 | P1 | Help | Three tabs | Docs under `/docs/evaluations/` |
