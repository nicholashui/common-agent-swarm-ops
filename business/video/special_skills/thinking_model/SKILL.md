# Special skill integration — `thinking_model`

**Status:** MVP integrated (2026-07-13)  
**Kind:** host_loop_pattern  
**Plan:** [`planning/special/thinking_model.md`](../../../planning/special/thinking_model.md)  
**Summary:** Thinking models configure loop intensity (orchestrator/planner/judge)

## Host binding

### Agents
- `video.orchestrator` — SPEC 472.9KB, ALC=yes [OK]
- `video.planner` — SPEC 553.1KB, ALC=yes [OK]
- `video.judge` — SPEC 246.7KB, ALC=yes [OK]
- `video.safetyredteam` — SPEC 68.1KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- `backend/app/domain/workflows/archetype_selector.py` [OK]
- `.grok/skills/workflow-dna/SKILL.md` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
