# Agent detail — test scenarios

**Route:** `/registry/agents/<agentId>`

---

## TS-AGT-001 Auth + known agent (P0)

| Given | When | Then |
|-------|------|------|
| Session + video.orchestrator | Open detail URL | Name/header render; opaque id shown |

## TS-AGT-002 Unknown agent safe (P1)

| Given | When | Then |
|-------|------|------|
| Session + nonsense id | Open detail | No crash; safe empty/fallback projection |

## TS-AGT-003 Tab switching (P1)

| Given | When | Then |
|-------|------|------|
| Detail open | Click each tab | Panel content switches; aria selection updates |

## TS-AGT-004 History filter (P1)

| Given | When | Then |
|-------|------|------|
| History tab | Toggle filter chip | Row set changes or pagination note updates |

## TS-AGT-005 Playground model cycle (P2)

| Given | When | Then |
|-------|------|------|
| Playground tab | Click model override | Label changes; status says local session |

## TS-AGT-006 Propose fail-closed (P0)

| Given | When | Then |
|-------|------|------|
| No action ref | Propose Improvement | Fail-closed message; no mutation |

## TS-AGT-007 Help fallback (P1)

| Given | When | Then |
|-------|------|------|
| On agent detail | Help → Func spec | Loads `/docs/registry/agents/func_spec.md` after param strip |
