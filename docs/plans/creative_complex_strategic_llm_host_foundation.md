# Creative · Complex-Problem · Strategic · LLM-Usage Host foundation (offline)

**Date:** 2026-08-05  
**Updated:** 2026-08-05 — Host consumer surfaces (patterns API + next-agent handoff)

## Implemented

| Surface | API | Module |
|---------|-----|--------|
| GCA SSOR-lite ideation / direction / handoff | `/api/v1/creative/ideate` | `backend/app/creative/` |
| Process-local learned patterns (lean) | `/api/v1/creative/patterns` | same |
| Complex problem process | `/api/v1/complex-problem/*` | `backend/app/complex_problem/` |
| Strategic goals / milestones | `/api/v1/strategic/*` | `backend/app/strategic/` |
| LLM usage policy ledger | `/api/v1/llm-usage/*` | `backend/app/llm_usage/` |

Host tools: `creative.ideate`, `creative.patterns`, `complex_problem.solve`, `strategic.plan`, `llm_usage.record`  
FE: `ideateCreative` (SSOR-lite + handoff summary), `listCreativePatterns` (process-local motifs)

### GCA offline SSOR-lite (present)

- Multi-POV mapping; sparse outliers ≤4; value-gate → `overall_cr` (`ssor` alias)
- `phase_trace` including **integration_refinement** before **output**
- Per-candidate **risks_mitigations** + **refinement_note**
- **handoff** package: best_candidate_id, concept, prompt_steer, creative_direction essentials, next_agents, recommended_tools
- **learned_patterns** process-local on ideate (prior runs) + lean **GET /patterns**
- Domain weights; deterministic IDs for same brief+domain+n
- Fail-closed when `allow_live_generation=true`

## Fail-closed / honesty

- No live generation / MCTS / durable creative memory / FAISS / NLAE / CreativeAgentFactory product  
- Patterns are process-local only  

## Still missing (production — not claimed)

- Full GCA technical stack (live LLM phases, vector stores, Plotly UIs)
- NLAE AI-native POV generation; CreativeAgentFactory product
- Durable long-term creative memory / cross-process model update
- Autonomous CPS / enterprise strategy OS / real provider cost APIs  
