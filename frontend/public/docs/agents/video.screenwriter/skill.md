---
name: video-screenwriter
description: Role harness for video.screenwriter — Treatment → screenplay; dialogue; structure
version: 1.0.0
agent_id: video.screenwriter
---

# Skill — `video.screenwriter`

## When to use
Load this skill when the host routes a task to `video.screenwriter` or when composing a swarm step that requires this craft role.

## Instructions
1. Load prompt `video.prompt.screenwriter.v1` from `../prompts/`.
2. Load rubric `video.rubric.screenwriter.v1` from `../rubrics/`.
3. Ground only on `../sources/` and host memory namespaces.
4. Execute architecture patterns: Reflexion, Agent Skills.
5. Emit the JSON output schema from the prompt; fail closed without tools/credentials.
6. On critique: refine ≤ max_refinement_count then escalate.

## Harness
- **Runner kind:** graph-node | tool-loop (host decides)
- **Entry:** pack agent `video.screenwriter` via host agent runner
- **Timeouts:** host default unless agent_spec budget_policy overrides
- **Network:** only if model_policy.network_access and production flags allow

## Bindings
Shared pack special_skills (optional): screenwriter_strategic_goal_achievement_agent

## Research patterns
- **Reflexion**: Shinn et al. — verbal RL + episodic memory of failures
- **Agent Skills**: Anthropic Agent Skills standard — SKILL.md frontmatter + harness

## Tests
- Offline golden: `business/video/evals/agents/video.screenwriter/golden.json`
- Must not require live network for L1 pass when tools are mocked.
