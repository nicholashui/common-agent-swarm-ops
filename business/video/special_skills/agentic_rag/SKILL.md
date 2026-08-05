# Special skill integration — `agentic_rag`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** research_retrieval  
**Plan:** [`docs/plans/agentic_rag_host_foundation.md`](../../../../docs/plans/agentic_rag_host_foundation.md)  
**Summary:** Offline Agentic RAG (plan/retrieve/reflect/cite) + research agent bindings

## Host binding

### Agents
- `video.webresearch` — SPEC 147.4KB, ALC=yes [OK]
- `video.archiveresearch` — SPEC 152.8KB, ALC=yes [OK]
- `video.citation` — SPEC 190.2KB, ALC=yes [OK]
- `video.memory` — SPEC 293.1KB, ALC=yes [OK]
- `specials.agentic-rag-agent` — draft pack + Host API [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- `backend/app/rag/` — offline agentic pipeline + hierarchical index [OK]
- `backend/app/api/v1/rag.py` — `/api/v1/rag/*` [OK]
- `backend/app/memory/retrieval.py` — scoped memory retrieve [OK]

## Runtime contract

- Entry: `POST /api/v1/rag/query` (offline) or agent-loop tools `rag.query` / `rag.ingest`.
- Fail-closed: no live web, Chroma, or commercial LightRAG.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
