# Plan: implement remaining VA study/*.md capabilities in Common

**Generated:** 2026-07-27T03:00:49Z
**Goal:** Make common-agent-swarm-ops capable of operating the system described in `va-agent-swarm/study/*.md` (excluding locale `_hk`/`_zh`).

## Principles

1. **Corpus first** — every study `.md` exact in `business/video/corpus/study/`.
2. **Pack before live** — agents, graphs, process/role maps before full vendor automation.
3. **Fail-closed production** — live media only via env credentials + production profile.
4. **One work package at a time** — each phase has artifacts + exit gate.
5. **Do not claim COMPLETE runtime** until phase exit gates pass with evidence.

## Phase 0 — Knowledge lock (DONE when all corpus exact)

| Step | Action | Exit gate |
|------|--------|-----------|
| 0.1 | Sync all study `*.md` excluding locales | `STUDY_CAPABILITY_INDEX.json` corpus_status exact/synced for all |
| 0.2 | Publish status + plan docs | `docs/va_study_implementation_status.md` exists |

## Phase 1 — Core video production workflow (from `ai_agent_video_production_workflow.md` + `human_…`)

| Step | Action | Exit gate |
|------|--------|-----------|
| 1.1 | Keep 114 agent pack + VA IDs | inventory 114 |
| 1.2 | A–J DNA host graphs with role map coverage | 10 arch DNA + WORKFLOW_ROLE_MAP |
| 1.3 | Shared skeleton phases in process_coverage | process rows include spine/phases/A–J |
| 1.4 | Critique bus defaults (critic/judge) | DNA critique_loops + agent critique_edges |
| 1.5 | LQR overview DNA + golden eval | lqr DNA + evals/golden |

**Status now:** largely complete as partial_runtime (graphs exist; full crew tables per phase still thin).

## Phase 2 — Media & generation stack (`video_generation_techology…`, podcast, pipeline tools)

| Step | Action | Exit gate |
|------|--------|-----------|
| 2.1 | Host adapters media.sora/veo/runway/elevenlabs | adapters registered |
| 2.2 | Production profile + credentials template | production/profile.json |
| 2.3 | Wire media agents tool allow-lists | agent_spec allowed_tools |
| 2.4 | Optional: Kling / additional vendors | new adapters + env keys |
| 2.5 | Optional: DCC bridges (Resolve/Nuke) | out-of-band MCP; not default |

**Status now:** 2.1–2.3 done; 2.4–2.5 open.

## Phase 3 — Special-skill functional specs → executable skills

| Step | Action | Docs covered | Exit gate |
|------|--------|--------------|-----------|
| 3.1 | Keep skill SKILL.md + integration.json | aesthetics, coding, creative, intent, optimization, research, etc. | special_skills/index.json |
| 3.2 | Bind specials pack agents (19) to skills | specials.aesthetics-agent, … | 19 agents standalone |
| 3.3 | Host runners for high-value skills (RAG, research, intent) | agentic_rag, research, knowledge_router | API + tests |
| 3.4 | Evaluation harness per skill | evals/ | golden cases |

**Status now:** 3.1–3.2 data-level; 3.3–3.4 open (partial memory/retrieve only).

## Phase 4 — Agent loop & thinking models

| Step | Action | Exit gate |
|------|--------|-----------|
| 4.1 | Package agent_loop_v3 skill | special_skills/agent_loop_v3 |
| 4.2 | Host graph loop pattern (plan→act→critique→refine) | pack_graph critique_loops |
| 4.3 | Thinking model skill hooks | thinking_model skill + optional graph node |

**Status now:** skill data + graph critique loops; not full autonomous v3 product.

## Phase 5 — UI study surfaces

| Step | Action | Docs | Exit gate |
|------|--------|------|-----------|
| 5.1 | Registry + agent detail for all pack agents | agent_management_ui | 133 UI export |
| 5.2 | Canvas/composer run path | project_creation_flow | createAndDispatchRun |
| 5.3 | Blueprints gallery vs archetypes | video_remake / production_scale | A–J listed |
| 5.4 | Close redesign gaps from RETHINK_100 | RETHINK_100_IMPROVEMENTS | prioritized backlog |

**Status now:** 5.1–5.3 partial; 5.4 backlog.

## Phase 6 — Continuous distillation & QC mesh (§ from workflow docs)

| Step | Action | Exit gate |
|------|--------|-----------|
| 6.1 | L1/L2/L3 QC agents in graphs | critic/judge/aiqaconsistency nodes |
| 6.2 | Eval campaigns via host evaluations API | run_evaluation path |
| 6.3 | Provenance/C2PA style gates | c2pa/deepfake agents as design + optional tools |

## Phase 7 — Evidence & claim hygiene

| Step | Action | Exit gate |
|------|--------|-----------|
| 7.1 | Refresh STUDY_CAPABILITY_INDEX after each phase | index timestamp |
| 7.2 | Standalone PASS with upstreams unavailable | check_video_domain_standalone |
| 7.3 | Honest status language in README/handoff | no overclaim full VA runtime |

## Recommended order (one by one)

1. Phase 0 (this sync)  
2. Phase 1.x gap fill (thicker archetype crews / typed handoffs)  
3. Phase 2.4 optional vendors as needed  
4. Phase 3.3 skill runners (start with agentic_rag + research)  
5. Phase 4.2 deepen critique loops  
6. Phase 5.4 UI backlog  
7. Phase 6 QC mesh  
8. Phase 7 evidence refresh  

## Non-goals (until explicitly scheduled)

- Full Kling/DCC MCP production suite
- Bit-for-bit CrewAI/AutoGen topology from study prose
- Locale `_hk`/`_zh` study variants (excluded by request)
