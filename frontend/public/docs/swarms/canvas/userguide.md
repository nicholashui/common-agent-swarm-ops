# Nested Swarm Canvas — step-by-step user guide

**Screen:** Swarm Canvas (scoped swarm)  
**Route:** `/swarms/<swarmId>/canvas`  
**Who it’s for:** Operators opening canvas for a specific swarm id.

---

## 1. Open a scoped canvas

1. Sign in.
2. Navigate from a swarm link or open `/swarms/<swarmId>/canvas`.
3. UI uses the same canvas presentation as `/canvas` with swarm context when projected.

---

## 2. Work the canvas

1. Follow the same steps as the main **Swarm Canvas** guide:
   - modes, palette, select node, layout, run intents.
2. Swarm id in the URL is an opaque resource parameter.

---

## 3. Help resolution

1. Exact doc path would be under the full swarm id (usually absent).
2. Fallback strips the swarm id → this file: `/docs/swarms/canvas/userguide.md`.
3. Root canvas guide also exists at `/docs/canvas/userguide.md`.

---

## 4. Safety notes

- Swarm id is not a secret token; still treat it as non-guessable where host requires.
- Run/mutate still need host action references.
