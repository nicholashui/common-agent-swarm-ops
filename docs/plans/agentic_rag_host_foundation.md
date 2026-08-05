# Agentic RAG Host foundation (offline)

**Spec:** `va-agent-swarm/study/agentic_rag_functional_specification.md`  
**Date:** 2026-08-05  

## Implemented (Host offline slice)

| Surface | Path |
|---------|------|
| Hierarchical local index (parent/child MD split) | `backend/app/rag/index.py` |
| Agentic pipeline (analyze→plan→retrieve→grade→generate→critic + reflect ≤3) | `backend/app/rag/pipeline.py` |
| Facade + seeded baseline corpus | `backend/app/rag/service.py` |
| Critique bus `rag_feedback` | `backend/app/rag/bus.py` |
| API | `GET/POST /api/v1/rag/*` |
| Host tools | `rag.query`, `rag.ingest` in `tool_activation.py` |
| Pack prompt + L2 | `business/specials/agents/specials.agentic-rag-agent/prompts|rubrics` |
| FE client | `frontend/src/lib/api/product-agentic-rag.ts` |
| Tests | `backend/tests/unit/api/test_rag.py` |

**Fail-closed:** `allow_live_web` / `allow_chroma` / `allow_lightrag` → 403.

## Explicitly still missing (production scope)

- Chroma / embedding clusters  
- Commercial LightRAG + OpenSearch  
- 65k MD full ingest pipeline  
- Tavily / live web  
- Streamlit + Typer product surface  
- LangSmith + RAGAS ≥0.92 gates  
- Pack leave `draft` / live tool allowlists  

Pack `specials.agentic-rag-agent` remains **draft**; Host API is the executable foundation.
