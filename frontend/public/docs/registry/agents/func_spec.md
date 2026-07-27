# Agent detail — functional specification

**Route:** `/registry/agents/[agentId]`  
**Shell:** Authenticated  
**Component:** `AgentDetailHome` via `BoundAgentDetailHome`

---

## 1. Purpose

Present pack-backed agent settings, history, config, playground, and ops tabs for one opaque agent id.

## 2. Functional requirements

### FR-AGT-001 Route param
- `agentId` path param SHALL be required and treated as opaque resource id.
- View SHALL resolve from pack agent record when known; safe fallback when unknown.

### FR-AGT-002 Header
- SHALL show name, version badge, status, velocity, header stats, opaque id when provided.

### FR-AGT-003 Tabs
- Tabs SHALL switch History / Config / Playground / Knowledge / Ops (as defined by projection constants).
- Only one primary panel visible at a time.

### FR-AGT-004 History filters
- History filter chips SHALL filter usage rows locally.
- Usage note control SHALL announce session display message.

### FR-AGT-005 Playground controls
- Model override SHALL cycle local labels only.
- Enable Tools / Stream SHALL be controlled checkboxes with session feedback.
- Submit playground prompt SHALL fail closed without authorized playground action.

### FR-AGT-006 Mutations
- Propose / save proposal / replay / inject context SHALL fail closed without host action refs.

### FR-AGT-007 Help
- Candidates: exact agent path docs, then `/docs/registry/agents/{userguide|func_spec|test_scenario}.md`.

## 3. Out of scope

- Live provider execution without host.
- Editing pack source files from the UI.
