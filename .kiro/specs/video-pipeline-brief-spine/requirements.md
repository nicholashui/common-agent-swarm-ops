# Requirements — Video pipeline brief → spine (product path)

## Context

CASOPS product façade turns a production **user brief** into a **Phase-1-capable draft**, a **stub video spine** (`wf_video_spine_v1`), and a **package human gate**. Real media generation and full `agents.md` / SYSTEM_REFERENCE production are non-goals. Profile: R2. Risk: medium (fail-closed Host, process-local state).

**Plan:** `docs/plans/video_pipeline_brief_spine_plan.md`  
**Evidence:** `docs/plans/video_pipeline_epic_e_evidence.md`

## Acceptance Criteria

- REQ-1: When materialize is called with non-empty goal text, the system shall persist a UserBriefV1 snapshot on the swarm draft (no secrets).
- REQ-2: When the goal looks like a video production brief, materialize shall bind Phase-1 agents (`video.orchestrator`, `video.planner`, `video.producer`) plus spine-capable catalog agents only (closed world).
- REQ-3: When a video draft is materialized, the system shall attach spine `wf_video_spine_v1` with `production_ready: false` and stub step status.
- REQ-4: When an eligible `run_spine_step` action is consumed, the system shall advance one stub step and emit an opaque artifact ref (stub · not production media).
- REQ-5: When the package step runs, the system shall open a human gate with a real façade `approval_id` and never auto-approve.
- REQ-6: When a human denies package with a reason, the system shall fail closed (spine status denied) and record activity.
- REQ-7: Dashboard and Activity shall surface spine/package signals when present with honesty copy “stub run · not production media”.
- REQ-8: Agent Workflow shall expose Host product spine template id `wf_video_spine_v1`.
- REQ-9: When persistence is enabled, the system shall retain swarm drafts, brief, spine, package gates, and append-only audit across process restarts (local durable store).
- REQ-10: When a spine step emits an artifact, the system shall apply ArtifactHandoffV1 L1 validation (fail closed on missing fields or production_media=true for stubs).
- REQ-11: When spine steps run for spine pack agents, the system shall execute offline Plan→Act→Self-Review via Host AgentLoopService where the pack loads, record critiques, and fail closed if the loop does not pass (no production tools / network).
- REQ-12: Host shall expose fleet agent-loop inventory and run APIs so any loadable `video.*` pack agent can execute offline Plan→Act→Self-Review; production media/network activation remains denied.

## Non-goals

- Full 114-agent live production per `agents.md`
- Real Sora/Veo/Runway/ElevenLabs execution
- DIA production activation
- Multi-tenant cloud DB (local durable store under `.data/product_facade` is the accepted Host-local durability)

## Approval

Implemented under product plan A–E; open questions frozen in the plan doc (2026-08-04).
