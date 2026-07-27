# Video Roster Retention Policy (N3)

**Effective:** 2026-07-12  
**Non-negotiable:** N3 — **all 114 agents retained forever** in this pack.

## Rules

1. **Never delete** a `ROSTER.json` pack_id or `business/video/agents/<pack_id>/` directory to “simplify” the host.
2. Inventory CI (`scripts/business/inventory_check.py`) **must fail** if count ≠ 114 or MAP/standby incomplete.
3. Agents may be `draft` / `registered` / `active` / standby-routed; **retirement ≠ deletion**. Deprecate via status only.
4. Upstream va-agent-swarm updates land as pack PRs with provenance — not as justification to drop agents.
5. Other domain packs (`example_*`) must not reduce video inventory.

## Evidence

- `business/video/ROSTER.json`
- `business/video/standby_pool.json`
- `business/video/MAP.md`
- GitHub workflow `n3-inventory.yml`
