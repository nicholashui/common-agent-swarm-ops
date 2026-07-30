---
name: video-legal
description: Role harness for video.legal — Performs final legal review for novel or high-risk publication issues
version: 1.0.0
agent_id: video.legal
---

# Skill — `video.legal`

## When to use
Load this skill when the host routes a task to `video.legal` or when composing a swarm step that requires this craft role.

## Instructions
1. Load prompt `video.prompt.legal.v1` from `../prompts/`.
2. Load rubric `video.rubric.legal.v1` from `../rubrics/`.
3. Ground only on `../sources/` and host memory namespaces.
4. Execute architecture patterns: Constitutional AI, Agent Skills.
5. Emit the JSON output schema from the prompt; fail closed without tools/credentials.
6. On critique: refine ≤ max_refinement_count then escalate.

## Harness
- **Runner kind:** graph-node | tool-loop (host decides)
- **Entry:** pack agent `video.legal` via host agent runner
- **Timeouts:** host default unless agent_spec budget_policy overrides
- **Network:** only if model_policy.network_access and production flags allow

## Bindings
Shared pack special_skills (optional): (none required)

## Research patterns
- **Constitutional AI**: Bai et al. / RLAIF — principles as constitution for self-check
- **Agent Skills**: Anthropic Agent Skills standard — SKILL.md frontmatter + harness

## Tests
- Offline golden: `business/video/evals/agents/video.legal/golden.json`
- Must not require live network for L1 pass when tools are mocked.
