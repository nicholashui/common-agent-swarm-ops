# Swarm Canvas — functional specification

**Route:** `/canvas` · **Auth:** required · **Component:** `CanvasHome`

## Purpose
Inspect projected swarm graph, palette, inspector; request run/layout only under fail-closed host rules.

## Functional requirements

### FR-CAN-001 Binding
- Authenticated shell; projection via screen parameters / bound home.

### FR-CAN-002 View modes
- Design / Run / Compare modes SHALL toggle local mode state.

### FR-CAN-003 Swarm name
- Editable local name field SHALL bind to component state.

### FR-CAN-004 Palette
- Tabs, search, and item click SHALL filter/select palette locally.
- Add-node without host graph mutation SHALL fail closed / announce preview only.

### FR-CAN-005 Node selection
- Selecting a node SHALL drive inspector content from projection.

### FR-CAN-006 Layout / zoom / focus
- Auto layout → `local.layout` when bridged.
- Zoom clamp 0.5–2; focus mode toggles local CSS/state.

### FR-CAN-007 Run
- Run control SHALL call `canvas.run` / createAndDispatch when runtime available.
- Cancel/export/pin/A-B without refs SHALL fail closed.

### FR-CAN-008 Nested route
- `/swarms/<id>/canvas` SHALL strip param for docs fallback to `/docs/swarms/canvas/*` and `/docs/canvas/*`.

### FR-CAN-009 Help
- `/docs/canvas/{userguide,func_spec,test_scenario}.md`

## Out of scope
- Client-side remote tool execution.
- Inventing edges not in projection.
