# Video Domain Pack (common-agent-swarm-ops)

**Status:** Agent self-containment **complete** (redo_migration.md v2.0 agent phase)  
**Pack ID:** `video`  
**Inventory:** 114 agents (registered, L0, non-active)

## Source of truth

Checked-in content under `business/video/` is authoritative for this host. Upstream repositories are **optional update inputs only**:

| Upstream | Role |
|----------|------|
| `generic-swarm-ops` | Completed va→generic pack; used as distillation source during migration |
| `va-agent-swarm` | Original design corpus; historical provenance only |

**Pack-level `corpus/` is not required.** Agent knowledge lives in each agent folder.

## Self-contained agents

Every agent is offline-readable from its folder alone:

```text
agents/<common_agent_id>/
  README.md              # folder index
  SPEC.md                # full role definition (no required external open)
  agent_spec.json        # host runtime binding (fail-closed)
  sources/
    PROVENANCE.json      # commits + mapping provenance
    MAPPING.md           # human mapping note
  prompts/               # optional stubs
  rubrics/               # optional stubs
```

### Map and projections

| File | Purpose |
|------|---------|
| `AGENT_SOURCE_MAP.json` | Reviewed common ID → source agent relationship |
| `ROSTER.json` | Common IDs only |
| `MAP.md` | Human-readable mapping projection |
| `SPEC_REVIEWS.json` | Critical-role specification reviews |

### Workflows

- `workflows/pack_spine.json` — **sole current safe stub graph**
- Full A–J DNA adaptation is **deferred** (not part of agent-phase DoD)

### Policies and schemas

- `policies/` — common-owned safety / lifecycle
- `schemas/` — pack extension schemas

## Fail-closed runtime

- Agents remain `registered` / non-production-active
- Local deterministic model policy; `network_access: false`
- Empty tool allow-lists unless a later approved change

## Verification

```bash
# Agents-only (no corpus required)
python scripts/business/check_common_video_agents_standalone.py

# Full standalone (isolation claims required)
python scripts/business/check_video_domain_standalone.py --network-disabled --upstreams-unavailable

# Rebuild agent folders (optional; needs upstream paths for enrichment)
python scripts/business/build_common_video_agent_folders.py --dry-run
python scripts/business/build_common_video_agent_folders.py --write
```

## Update policy

1. Prefer editing common `agents/<id>/SPEC.md` and `agent_spec.json` in-repo.  
2. Upstream pulls: map review → distill into agent folders → refresh provenance.  
3. Do not treat a shared corpus tree as the only place agent knowledge lives.  
4. Do not enable production activation or network tools without a separate human gate.

## Related docs

- `redo_migration.md` — redo plan v2.0 (self-contained agents, no corpus DoD)
- `migration.md` — broader pack/workflow migration
- `docs/migration_redesign/migration_redesign.md` — blueprint/workflow gates
