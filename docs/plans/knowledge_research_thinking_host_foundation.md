# Knowledge · Research · Thinking Host foundation (offline)

**Date:** 2026-08-05  
**Plan refs:** va study phase 3.3 (RAG/research/router) + 4.3 (thinking hooks)

## Implemented

| Surface | Path |
|---------|------|
| Knowledge Router (keyword hybrid-lite) | `backend/app/knowledge/` + `GET/POST /api/v1/knowledge/*` |
| Research (plan→route→RAG→synthesize→critic) | `backend/app/research/` + `/api/v1/research/*` |
| Thinking catalog + cognitive recommend | `backend/app/thinking/` + `/api/v1/thinking/*` |
| Host tools | `knowledge.route`, `research.query`, `thinking.recommend` |
| Loop integration | `AgentLoopService` applies thinking recommend into v3 defaults |
| FE clients | `product-knowledge.ts`, `product-research.ts`, `product-thinking.ts`, agent-loop v3 helpers |

## Fail-closed

- Live web / Tavily / GNN embeddings denied  
- Research gathers via offline RAG only  

## Still missing (production)

- Metadata frontmatter corpus over 5k MD  
- Learned / GNN router  
- Live web research  
- Full 40-model live metacognition LLM engine  
