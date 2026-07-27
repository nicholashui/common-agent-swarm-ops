# Swarm Canvas — test scenarios

**Route:** `/canvas`

| ID | Priority | Given | When | Then |
|----|----------|-------|------|------|
| TS-CAN-001 | P0 | Anonymous | Open `/canvas` | Redirect login |
| TS-CAN-002 | P0 | Auth | Open canvas | Board/palette/inspector regions present |
| TS-CAN-003 | P1 | Modes | Click Run mode | Mode pressed=run |
| TS-CAN-004 | P1 | Palette search | Type query | Palette list filters |
| TS-CAN-005 | P1 | Nodes | Click node | Inspector shows selection |
| TS-CAN-006 | P1 | Zoom | Click + | Status shows zoom % |
| TS-CAN-007 | P0 | Run without host | Click Run | Runtime path or fail-closed; no silent success |
| TS-CAN-008 | P1 | Export | Click Export | Fail-closed authorized export message |
| TS-CAN-009 | P1 | Help | Func spec / Test tabs | Markdown loads for `/docs/canvas/*` |
