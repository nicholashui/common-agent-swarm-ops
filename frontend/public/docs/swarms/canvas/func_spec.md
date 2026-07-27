# Nested Swarm Canvas — functional specification

**Route:** `/swarms/[swarmId]/canvas` · **Auth:** required

## Purpose
Same canvas capabilities as `/canvas`, with opaque swarm id in the path.

## Functional requirements

### FR-NSC-001 Param
- `swarmId` is opaque; MUST NOT be treated as a secret grant by itself.

### FR-NSC-002 Behavior parity
- UI behaviors SHALL match canvas FR-CAN-* for modes, palette, run fail-closed rules.

### FR-NSC-003 Docs resolution
- Exact path docs optional; stripped path `/swarms/canvas` SHALL map to this folder’s docs.
- Further fallback to `/docs/canvas/*` and root docs.

## Out of scope
- Client-side authorization elevation based on guessing swarmId.
