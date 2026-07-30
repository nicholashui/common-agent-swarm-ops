# Improvement research sources v1

Generated: 2026-07-30T14:45:33Z

This document records **patterns and references** used by
`scripts/business/improve_agents_from_plan_v1.py` to materialize prompts, rubrics,
skills, and distillation scaffolds for video pack agents.

> No third-party code was downloaded into the runtime path. Patterns are encoded
> as pack-local markdown/JSON artifacts under each agent folder.

## Primary design authority (local)

| Source | Use |
|--------|-----|
| `va-agent-swarm/study/agents.md` | Responsibility, knowledge sources, self-quality, surpass signals, critique topology, tools, architecture |
| `va-agent-swarm/study/agents.md` §11 Common Structure | Identity, handoffs, L1/L2/L3 gates, continuous learning, HiTL |
| `agent_capability_status_v1.md` | Gap diagnosis per agent |
| `agent_improvement_plan_v1.md` | Full-mark action lists and platform workstreams |
| `business/video/special_skills/` | Existing pack skills (agent_loop_v3, research_agent, etc.) |

## External research patterns (public literature / standards)

| Pattern | Why used | Typical mapping |
|---------|----------|-----------------|
| **Anthropic Agent Skills** ([agentskills.io](https://agentskills.io), anthropics/skills on GitHub) | Standard for `SKILL.md` frontmatter + harness folders | Every agent `skills/SKILL.md` |
| **Self-Refine** (Madaan et al.) | Iterative self-critique against rubric | Default refine loop in prompts |
| **Reflexion** (Shinn et al.) | Verbal RL + memory of failures | Planner / meta agents |
| **ReAct** (Yao et al.) | Reason → tool act loop | Tool-using craft agents |
| **Constitutional AI / RLAIF** (Bai et al.) | Principles as safety/craft constitution | Safety, drone, continuity-style agents |
| **LLM-as-Judge** (Zheng et al.) | Structured multi-dimension scoring | All `rubrics/*.json` L2 layer |
| **Multi-agent debate** (Du et al.) | Dispute resolution before HiTL | Judge + conflict path |
| **Agentic graphs** (LangGraph / CrewAI / AutoGen style) | Deterministic DAG, handoffs, retries | Orchestrator / workflow DNA |
| **MCP tool bridges** (Model Context Protocol) | Least-privilege tool access concept | agent_spec allowed_tools |

## YouTube / learning channels (operator education, not runtime deps)

Use for human craft grounding when expanding SOURCE_CATALOG (respect licenses):

- Official product channels for tools listed in agents.md (Resolve, Unreal, etc.)
- Conference talks (SIGGRAPH, NAB) referenced as distillation *targets* only
- Prefer written primary sources in pack `sources/` over ephemeral video transcripts

## xAI / Grok related notes

- Prefer **host-local prompts** in pack folders over provider-specific system prompts.
- When using Grok or other LLMs as the host model, inject the pack prompt's System section first
  (responsibility + does_not_own + fail-closed rules).
- Do not embed API keys; use env-gated production flags already in the video production profile.

## GitHub resources consulted (reference-only)

- `anthropics/skills` — Skill folder layout and SKILL.md conventions
- LangGraph / CrewAI / AutoGen documentation patterns (architecture column alignment)
- In-repo `business/video/special_skills/*/SKILL.md` + `integration.json` as local templates

## What this factory deliberately does NOT do

- Install remote plugins into production configuration without human approval
- Claim human-surpass (Q5) without measured baselines
- Enable live media/provider calls without existing fail-closed env gates
- Copy unlicensed third-party corpora into the pack

## Next research-backed upgrades (after Wave A)

1. Wire host eval harness to load `rubrics/*.json` (Wave A/P2).
2. Implement CritiqueMessage bus from expanded `critique_edges` (Wave B/P3).
3. Convert selected public workflows (e.g. LangGraph examples) into **host DNA nodes** only after review — never as a second control plane.
