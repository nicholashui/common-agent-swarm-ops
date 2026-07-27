# Special skill integration — `coding_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** host_infra  
**Plan:** [`planning/special/coding_agent.md`](../../../planning/special/coding_agent.md)  
**Summary:** Host engineering agent capability (not video business logic)

## Host binding

### Agents
- _None (host-infra skill)_

### Workflow DNA
- _None_

### Host modules
- `backend/app/runtime.py` [OK]
- `.grok/skills/workflow-dna/SKILL.md` [OK]
- `backend/app/infrastructure/llm/base.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
