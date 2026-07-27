# Registry Hub — functional specification

**Route:** `/registry`  
**Shell:** Authenticated  
**Component:** `RegistryHome` via `BoundRegistryHome`

---

## 1. Purpose

Discover pack agents (video + specials) and patterns with local search/facets/views; never activate production from the browser.

## 2. Functional requirements

### FR-REG-001 Auth gate
- Anonymous users SHALL be redirected to login before viewing registry.

### FR-REG-002 Catalog completeness
- Agents SHALL include all pack catalog entries (133: 114 video + 19 specials) from slim catalog projection.
- Demo/market-sentiment style non-pack agents SHALL NOT appear.

### FR-REG-003 Search
- Search input SHALL filter agents by multi-token AND against id, name, description, badges, domains, usage, version, category, architecture.
- Result meta SHALL show `Showing X of Y agents`.
- Search SHALL update on each change (controlled input).

### FR-REG-004 Facets
- Facet chips from projection (`video`, `specials`, `draft`, `registered`, `self-contained`, `no-network`, …) SHALL toggle.
- Domain facets SHALL combine with OR; other facets with AND.
- Soft match on badge/domain/category/id prefix/usage.

### FR-REG-005 Clear filters
- Clear control SHALL reset search and facets when any filter active.

### FR-REG-006 View modes
- Modes: `cards` | `table` | `graph`.
- Cards: agent card grid with actions.
- Table: tabular rows with Add/Detail.
- Graph: local layout up to 48 nodes; selection shows detail summary.

### FR-REG-007 Agent actions
- Add to Swarm / Propose SHALL fail closed without host action refs.
- Detail SHALL navigate to `/registry/agents/<id>` (encoded).

### FR-REG-008 Patterns
- Pattern cards SHALL list projected patterns; search also filters patterns.
- Instantiate/Fork follow host eligibility rules.

### FR-REG-009 Specials panel
- Embedded specials catalog SHALL remain draft/non-active; no production activation control.

### FR-REG-010 Help panel
- Docs: `/docs/registry/userguide.md`, `func_spec.md`, `test_scenario.md`.

## 3. Non-functional

| ID | Requirement |
|----|-------------|
| NFR-REG-001 | Slim client island (BoundRegistryHome) to keep hydration workable. |
| NFR-REG-002 | No full raw SPEC dumps required for list cards. |

## 4. Out of scope

- Production activation of specials/video providers.
- Host registry write without action references.
