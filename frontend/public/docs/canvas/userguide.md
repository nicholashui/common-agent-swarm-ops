# Swarm Canvas — step-by-step user guide

**Screen:** Swarm Canvas  
**Route:** `/canvas` (also nested `/swarms/<id>/canvas`)  
**Who it’s for:** Operators inspecting topology, layout, and run intents.

---

## 1. Open Canvas

1. Sign in.
2. Menu **BUILD** → **Swarm Canvas**, or open `/canvas`.
3. Confirm three-region layout when available: palette, graph board, inspector.

---

## 2. Set view mode

1. Use **Design / Run / Compare** mode controls in the toolbar.
2. Active mode shows pressed/highlighted state.
3. Mode is local UI until a host run contract is invoked.

---

## 3. Name the swarm

1. Edit the swarm name field in the toolbar.
2. Name is presentation state for this session.

---

## 4. Palette and search

1. Switch palette tabs (e.g. common / custom) if shown.
2. Use palette search to filter agents/nodes.
3. Click a palette item to preview add intent; without host graph mutation authority you get fail-closed feedback.

---

## 5. Select and inspect nodes

1. Click a node on the board to select it.
2. Inspector panel shows node metadata, task lifecycle, provenance when projected.
3. Do not expect raw secrets or protected tool payloads in the inspector.

---

## 6. Layout and focus

1. **Auto layout** applies local layout only (no host mutation).
2. **Focus** toggles focus mode for denser work.
3. Zoom **+ / − / expand** adjust local board scale.

---

## 7. Run and recovery controls

1. **Run** requests create/dispatch through the interaction runtime when available.
2. **Cancel**, **Partial replay**, **Export**, **A/B Test**, and pin/update controls fail closed without authorized action references.
3. Watch the run bar / status region for busy, success, or error.

---

## 8. Logs and co-pilot

1. Toggle **logs** to expand local log strip when present.
2. Co-pilot assist actions announce host requirements if not authorized.

---

## 9. Help

1. **Help** drawer loads docs for `/canvas` (and stripped `/swarms/canvas` fallback).
2. **Documents** opens full-page guide.

---

## 10. Safety notes

- Graph edges/nodes from projections are display data; browser does not invent topology.
- Run/dispatch requires host APIs; ineligible controls stay fail-closed.
