# Agent detail — step-by-step user guide

**Screen:** Agent & Pattern Detail  
**Route:** `/registry/agents/<agent-id>`  
**Who it’s for:** Operators reviewing one pack agent’s history, config, and playground.

---

## 1. Open agent detail

1. From **Registry**, click **Detail** on an agent card.  
2. Or open `/registry/agents/<agent-id>` (example: `/registry/agents/video.orchestrator`).
3. Confirm header shows agent name, version badge, status, and opaque id.

---

## 2. Use quick actions

1. **Propose Improvement** — requires authorized proposal action (fail-closed otherwise).
2. Other header buttons follow the same rule: honest fail-closed when no action ref.
3. Use status/feedback region for results.

---

## 3. Tabs

1. Switch tabs (History, Config, Playground, Knowledge, Ops — as projected).
2. Active tab is highlighted.

### History

1. Use history filter chips to filter usage rows locally.
2. Click usage note / replay controls as labeled.
3. Replay without host checkpoint authority fails closed.

### Config

1. Read version timeline and config summary cards.
2. **Save as proposal** / **Compare versions** require host authority when mutating.

### Playground

1. Cycle **Model override** (local session only).
2. Toggle **Enable Tools** / **Stream** (local preview flags).
3. Enter a prompt and submit; playground execution needs authorized action ref.

### Knowledge / Ops

1. Search knowledge if the tab provides it.
2. Ops actions announce fail-closed host requirements when unauthorized.

---

## 4. Return to registry

1. Use browser back or menu **Registry Hub**.
2. Help for detail falls back to this guide after stripping the agent id segment.

---

## 5. Safety notes

- Pack agent settings are projections from self-contained folders.
- No production activation or secret fields in the UI.
