# Specials pack (`business/specials`)

**Status:** Data-only **draft** catalog — not production-active  
**Layout:** Self-contained agent folders (same configuration set as video agents)  
**Sources:** `docs/special_agents_redesign/agents/*.md` (untrusted design provenance)  
**Host contract:** Domain-neutral common host; specials receive no second control plane, tools, network, or production activation.

## Self-contained agents (19)

Every agent folder is offline-readable without an external repository or pack-level corpus:

```text
agents/<specials.agent-id>/
  README.md                 # folder index
  SPEC.md                   # full offline role definition
  agent_spec.json           # host runtime binding (draft, fail-closed)
  sources/
    PROVENANCE.json         # hashes + mapping provenance
    MAPPING.md              # design-doc relationship (historical)
  prompts/                  # optional stubs (inert prompt_reference)
  rubrics/                  # optional stubs
```

### Pack-root map (mirrors video pack maps; no inventory file)

| File | Purpose |
|------|---------|
| `manifest.json` | Catalog of 19 draft agents (`inventory_required: false`) |
| `AGENT_SOURCE_MAP.json` | Agent ID → design source relationship |
| `ROSTER.json` | Specials IDs only |
| `MAP.md` | Human-readable map |

Note: unlike video, specials intentionally **does not** ship `inventory.json` (host fail-closed inventory gate treats an unexpected inventory as invalid).

## Catalog

| Agent ID | Source document |
|---|---|
| `specials.aesthetics-agent` | `aesthetics_agent.md` |
| `specials.agent-loop-creator` | `agent_loop_creator.md` |
| `specials.agentic-rag-agent` | `agentic_rag_agent.md` |
| `specials.autotelic-agent` | `autotelic_agent.md` |
| `specials.complex-problem-solution-process-model` | `complex_problem_solution_process_model.md` |
| `specials.controller-agent` | `controller_agent.md` |
| `specials.general-creative-agent` | `general_creative_agent.md` |
| `specials.intent-analysis-agent` | `intent_analysis_agent.md` |
| `specials.knowledge-router-agent` | `knowledge_router_agent.md` |
| `specials.llm-usage` | `llm_usage.md` |
| `specials.optimization-agent` | `optimization_agent.md` |
| `specials.planner-agent` | `planner_agent.md` |
| `specials.podcast-agent` | `podcast_agent.md` |
| `specials.psychological-profile-agent` | `psychological_profile_agent.md` |
| `specials.psychological-recommendation-agent` | `psychological_recommendation_agent.md` |
| `specials.research-agent` | `research_agent.md` |
| `specials.screenwriter-strategic-goal-achievement-agent` | `screenwriter_strategic_goal_achievement_agent.md` |
| `specials.strategic-goal-achievement-agent` | `strategic_goal_achievement_agent.md` |
| `specials.techology-advisor-agent` | `techology_advisor_agent.md` (source filename spelling preserved) |

## Invariants

1. Every agent is `status: draft` with `production_activation_requested: false`.
2. `allowed_tools: []`, `network_access: false`, `provider: local_deterministic`.
3. Source Markdown is hashed provenance only — never interpreted as configuration or executable instructions.
4. Registration effect is at most `eligible_draft_representation` (see `backend/app/registry/specials_validator.py`).
5. Frontend presentation (`frontend/src/lib/specials/specials-catalog.ts`) mirrors this fail-closed catalog.
6. Pack-level `corpus/` is **not required**; agent knowledge lives in each agent folder.

## Build / verify

```powershell
# (Re)build self-contained folders
python scripts/business/build_specials_agent_folders.py --write

# Agents-only standalone (video-equivalent layout)
python scripts/business/check_specials_agents_standalone.py

# Governance fail-closed / pack checks
python scripts/business/check_special_business_agents.py
python -m pytest backend/tests/integration/test_special_business_agents_pack.py backend/tests/integration/test_special_business_agents_offline.py -q
cd frontend; npx tsx --test src/lib/specials/specials-alignment.test.ts
```
