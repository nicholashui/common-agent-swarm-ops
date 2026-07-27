# Registry Hub — test scenarios

**Route:** `/registry`

---

## TS-REG-001 Auth required (P0)

| Given | When | Then |
|-------|------|------|
| Anonymous | Open `/registry` | Redirect `/login` |

## TS-REG-002 Catalog counts (P0)

| Given | When | Then |
|-------|------|------|
| Authenticated | Open registry | Showing 133 of 133; 114 video + 19 specials present |

## TS-REG-003 Search orchestrator (P0)

| Given | When | Then |
|-------|------|------|
| Full catalog | Type `orchestrator` | Count becomes 1+ matching; names/ids contain orchestrator |

## TS-REG-004 Facet specials (P0)

| Given | When | Then |
|-------|------|------|
| No search | Click facet `specials` | Showing 19 of 133; all specials pack |

## TS-REG-005 Facet video (P0)

| Given | When | Then |
|-------|------|------|
| No search | Click `video` | Showing 114 of 133 |

## TS-REG-006 Domain facets OR (P1)

| Given | When | Then |
|-------|------|------|
| Facets video+specials | Both on | Showing 133 of 133 |

## TS-REG-007 Table mode (P0)

| Given | When | Then |
|-------|------|------|
| Cards view | Click Table | `data-registry-view="table"`; table headers visible |

## TS-REG-008 Graph mode (P0)

| Given | When | Then |
|-------|------|------|
| Any view | Click Graph viz | Graph canvas/nodes; selecting node shows detail |

## TS-REG-009 Clear filters (P1)

| Given | When | Then |
|-------|------|------|
| Search + facets | Clear filters | Showing 133 of 133; search empty |

## TS-REG-010 Detail navigation (P1)

| Given | When | Then |
|-------|------|------|
| Agent card | Click Detail | Navigates `/registry/agents/<id>` |

## TS-REG-011 Governed action fail-closed (P0)

| Given | When | Then |
|-------|------|------|
| No host action ref | Click Add to Swarm | Error/info fail-closed; no fake success mutation |

## TS-REG-012 Help tabs (P1)

| Given | When | Then |
|-------|------|------|
| On `/registry` | Open Help → User guide / Func spec / Test scenarios | Matching markdown loads |
