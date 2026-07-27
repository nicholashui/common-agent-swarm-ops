# Swarm Composer — test scenarios

**Route:** `/composer`

| ID | Priority | Given | When | Then |
|----|----------|-------|------|------|
| TS-CMP-001 | P0 | Anonymous | Open `/composer` | Redirect login |
| TS-CMP-002 | P0 | Authenticated | Open composer | Name + goal + patterns render |
| TS-CMP-003 | P1 | Patterns list | Select pattern | Selected pressed state |
| TS-CMP-004 | P0 | No host compose ref | Click Send | Fail-closed status; no fake run |
| TS-CMP-005 | P1 | Goal empty | Send | Validation/feedback without host mutation |
| TS-CMP-006 | P2 | Draft name set | Save draft | Session confirmation message |
| TS-CMP-007 | P1 | On `/composer` | Help → Func spec | Loads `/docs/composer/func_spec.md` |
| TS-CMP-008 | P1 | On `/composer` | Help → Test scenarios | Loads `/docs/composer/test_scenario.md` |
