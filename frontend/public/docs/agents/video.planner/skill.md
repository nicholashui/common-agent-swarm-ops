---
name: video-planner
description: Role harness for video.planner — Decomposes brief into phased DAG with assignments + critic gates
version: 1.0.0
agent_id: video.planner
---

# Skill — `video.planner`

## When to use
Load this skill when the host routes a task to `video.planner` or when composing a swarm step that requires this craft role.

## Instructions
1. Load prompt `video.prompt.planner.v1` from `../prompts/`.
2. Load rubric `video.rubric.planner.v1` from `../rubrics/`.
3. Ground only on `../sources/` and host memory namespaces.
4. Execute architecture patterns: ReAct, Agentic Graph, Agent Skills.
5. Emit the JSON output schema from the prompt; fail closed without tools/credentials.
6. On critique: refine ≤ max_refinement_count then escalate.

## Harness
- **Runner kind:** graph-node | tool-loop (host decides)
- **Entry:** pack agent `video.planner` via host agent runner
- **Timeouts:** host default unless agent_spec budget_policy overrides
- **Network:** only if model_policy.network_access and production flags allow

## Bindings
Shared pack special_skills (optional): agent_loop_v3, thinking_model

## Research patterns
- **ReAct**: Yao et al. — reason then act with tools
- **Agentic Graph**: LangGraph/CrewAI/AutoGen style deterministic DAG + handoffs
- **Agent Skills**: Anthropic Agent Skills standard — SKILL.md frontmatter + harness

## Tests
- Offline golden: `business/video/evals/agents/video.planner/golden.json`
- Must not require live network for L1 pass when tools are mocked.
