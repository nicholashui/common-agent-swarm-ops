# Special skill integration — `agentic_rag`

**Status:** MVP integrated (2026-07-13)  
**Kind:** research_retrieval  
**Plan:** [`planning/special/agentic_rag.md`](../../../planning/special/agentic_rag.md)  
**Summary:** Agentic RAG via research agents + host knowledge/memory

## Host binding

### Agents
- `video.webresearch` — SPEC 147.4KB, ALC=yes [OK]
- `video.archiveresearch` — SPEC 152.8KB, ALC=yes [OK]
- `video.citation` — SPEC 190.2KB, ALC=yes [OK]
- `video.memory` — SPEC 293.1KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- `backend/app/domain/knowledge/retrieval.py` [OK]
- `backend/app/domain/memory/retrieval.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
