# Visual Director

> Self-contained agent definition for host `common-agent-swarm-ops`. Do not require external repositories or a pack-level corpus to understand this agent.

## Identity
- Common Agent ID: `video.visual_director`
- Status: `registered`
- Maturity: `L0`
- Pack version: `0.2.0`

## Responsibility
Owns the video-domain visual director outcome by producing a reviewable video artifact, applying the approved pack rubric, recording acceptance criteria, and escalating rights, safety, or quality failures before downstream handoff.



### Domain distillation (embedded)

### Distilled responsibility (video.director)

Owns vision; issues shot intents, sets pacing, approves takes

### Distilled quality (video.director)

Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior

### Distilled responsibility (video.cinematographer)

Lensing, lighting, composition, look

### Distilled quality (video.cinematographer)

Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency

## Boundaries and escalation
- Operates only on approved local video-pack inputs and inert corpus references.
- Does not activate providers, credentials, network access, production agents, or human-gate bypasses.
- Escalates unresolved rights, consent, privacy, safety, provenance, compliance, and release findings to the required human gate.

## Inputs and outputs
- Input artifact: an approved video brief, source context, or upstream typed production handoff.
- Output artifact: a reviewable video-domain deliverable with acceptance criteria for the next local role.
- Acceptance condition: the output is traceable to its local inputs and passes the applicable quality and safety checks.

## Quality and critique
- Local rubric reference: `video.rubric.visual_director.v1`.
- Prompt reference: `video.prompt.visual_director.v1`; references are inert local contract identifiers.
- Critique edges: `{"inputs":["video.critique_coordinator"],"outputs":["video.judge_agent"]}`.
- Refinement limit: `3`; unresolved critique or release findings escalate rather than bypass a gate.

## Runtime binding
The following local binding is copied as a read-only summary; it does not alter the common configuration:
```json
{"agent_id":"video.visual_director","allowed_tools":[],"budget_policy":{"max_input_tokens":2048,"max_output_tokens":1024,"max_tool_requests":0},"critique_edges":{"inputs":["video.critique_coordinator"],"outputs":["video.judge_agent"]},"max_refinement_count":3,"model_policy":{"model_id":"local-video-config-v1","network_access":false,"provider":"local_deterministic"},"production_activation_requested":false,"prompt_reference":"video.prompt.visual_director.v1","role":"Video Visual Director configuration specialist","rubric_reference":"video.rubric.visual_director.v1","schema_version":"1.0","status":"registered"}
```

## Local knowledge sources
- [Common inventory](../../inventory.json) — authoritative identity and lifecycle.
- [Runtime binding](agent_spec.json) — preserved local configuration contract.
- [Reviewed local source document](../../agents/video.visual_director/agent_spec.json)
- [Reviewed local source document](../../inventory.json)
- All references in this section are required local references beneath the Common Repository root.

## Provenance
- Mapping status: `composite`; source-agent IDs: `video.cinematographer`, `video.director`.
- Relationship rationale: Human-reviewed mapping of video.visual_director to generic source agent(s) video.director, video.cinematographer for self-contained SPEC distillation. Distinct relationship for common role `video.visual_director` (inventory order). Reviewed relationship unique to common agent `video.visual_director`.
- Reviewed by `migration-reviewer-common` at `2026-07-26T12:00:00Z`.
- Any upstream repository, commit, or source ID is retained as historical, non-binding provenance only; local contracts remain authoritative.
