# Nested Swarm Canvas — test scenarios

**Route:** `/swarms/<swarmId>/canvas`

| ID | Priority | Given | When | Then |
|----|----------|-------|------|------|
| TS-NSC-001 | P0 | Auth | Open nested canvas URL | Canvas UI renders; no crash |
| TS-NSC-002 | P1 | Help open | Help → User guide | Loads `/docs/swarms/canvas/userguide.md` (stripped) |
| TS-NSC-003 | P1 | Help | Func spec / Test scenarios | Matching files in `/docs/swarms/canvas/` |
| TS-NSC-004 | P0 | Run | Click Run | Same fail-closed/runtime rules as `/canvas` |
