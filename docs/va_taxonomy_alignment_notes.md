# VA taxonomy alignment notes

**Date:** 2026-07-27  
**Scripts:**
- `scripts/business/align_video_ids_to_va_taxonomy.py`
- `scripts/business/rebuild_va_aligned_specs_valid.py`
- `scripts/business/convert_design_dna_to_host_graphs.py`

**Record:** `business/video/VA_TAXONOMY_ALIGNMENT.json`

## Goal

Improve Common toward Generic’s Pure VA Domain Pack strengths on:

1. Pure VA Domain Pack **content & naming**
2. **SPEC depth**
3. **Agent IDs ≈ VA tables** (generic pack IDs / VA roster tables)

## Result (measured)

| Item | Status |
|------|--------|
| 114 agent folders | **Exact ID match** vs generic (`video.creativedirector`, `video.director`, …) |
| `inventory.json` / `manifest.json` / `ROSTER.json` IDs | VA/generic taxonomy |
| SPECs | VA Identity table (`va_id`, category, upstream name) + lifted VA table sections + full generic body under Provenance |
| SPEC average size | **~124,270 B** (generic ~123,215 B) |
| `agent_spec.json` | Fail-closed + `va_id` / `va_name` / `va_category` metadata (114/114) |
| Critique bus | Defaults to VA `video.critic` → `video.judge` |
| Host DNA + process_coverage | 14/14 host-valid graphs; critique loops use VA IDs |
| Runtime compliance | `COMPLIANCE_AGENT_ID = video.compliance` (matches pack_spine) |
| UI export | **133** agents (114 video + 19 specials), VA-style video IDs |
| Gates | agents standalone **PASS**, specials **PASS**, full **STANDALONE PASS** |

## Examples

| Previous common ID | VA / generic pack ID | va_id (generic) |
|--------------------|----------------------|-----------------|
| `video.creative_director` | `video.creativedirector` | 30 |
| `video.compliance_agent` | `video.compliance` | (per generic meta) |
| `video.brief_intake` | `video.planner` | (per generic meta) |
| `video.orchestrator` | `video.orchestrator` | (unchanged) |
| `video.quality_controller` | `video.critic` | (per generic meta) |
| `video.qc_l3_reviewer` | `video.judge` | (per generic meta) |

## Runtime safety

- `agent_spec.json` remains fail-closed (no network, no production activation).
- Design body is **historical and non-binding** for activation.
- Host graphs keep empty tool allow-lists except spine `media.stub` where declared.
- Host DNA critique loops use inventory-resident VA IDs only.

## Residual notes

- Historical docs (`migration.md`, older `redo_migration.md` ID examples) may still show pre-alignment snake_case IDs; pack runtime authority is `business/video/inventory.json` + agent folders.
- Live media vendors remain stubs in both Common and Generic.
