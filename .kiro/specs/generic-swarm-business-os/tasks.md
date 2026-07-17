# Implementation Plan: Generic Swarm Business OS

## Overview

Implement a new, deterministic Python/FastAPI Host solely in `C:\Project\common-agent-swarm-ops`, starting from the CASOPS-only scaffold. `structure.md` is the architecture and product-bar authority; `requirements.md` is the acceptance baseline. All application code, test fixtures, evidence, and validation commands remain under this target workspace. `C:\Project\generic-swarm-ops` is excluded: do not read, execute, modify, copy, or adopt it without separately recorded human approval.

Every phase uses local deterministic adapters, bounded execution, and durable evidence before later capabilities. Do not add live SaaS/media calls, credentials, automatic promotion, production Host-code rewrites, unbounded orchestration, deployment, or speculative scope. Use pinned, reviewed project-local dependencies only; do not use global installation or remote installers. Commands below are implementation-time evidence commands, not permission for production operations.

## Tasks

- [ ] 1. Establish the target-only Python Host foundation
  - [ ] 1.1 Create the minimal Python/FastAPI project scaffold, pinned project-local dependency configuration, strict static-check configuration, and deterministic test layout.
    - Target areas: `backend/pyproject.toml`, `backend/app/`, `backend/tests/`, `.gitignore` additions only as needed.
    - Do not install globally, contact external services, or create a second public control plane.
    - _Requirements: 1.2, 1.5, 10.1, 10.2_
  - [ ] 1.2 Implement target-root confinement, recorded-adoption authorization, and architecture-decision rendering that names the target workspace and `structure.md`.
    - Target areas: `backend/app/core/boundary.py`, `backend/app/core/decisions.py`, `backend/app/core/errors.py`.
    - Refuse outside-root access, writes, execution, and unapproved adoption without mutation.
    - _Requirements: 1.1–1.5_
  - [ ] 1.3 Define versioned shared records, identifiers, typed error/result contracts, and repository protocols with optimistic-transition seams.
    - Target areas: `backend/app/models/`, `backend/app/repositories/protocols.py`.
    - Include correlation IDs, redaction-safe projections, and immutable audit/evidence record shapes.
    - _Requirements: 4.1–4.4, 5.3–5.4, 6.1–6.3_
  - [ ]* 1.4 Write Hypothesis property test for architecture-decision authority.
    - **Property 1: Architecture decisions declare their authority**; at least 100 examples.
    - Target area: `backend/tests/properties/test_property_01_authority.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_01_authority.py`.
    - **Validates: Requirements 1.1**
  - [ ]* 1.5 Write Hypothesis property test for target-workspace and adoption fail-closed behavior.
    - **Property 2: Workspace and adoption authorization is fail-closed**; generate bounded paths and approval states only.
    - Target area: `backend/tests/properties/test_property_02_boundary.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_02_boundary.py`.
    - **Validates: Requirements 1.2–1.5**
  - [ ]* 1.6 Write focused unit tests for path traversal, mutation-free refusals, redaction, and typed error contracts.
    - Target area: `backend/tests/unit/core/`; validate with `cd backend && python -m pytest -q tests/unit/core`.
    - _Requirements: 1.2–1.5, 10.4–10.5_

- [ ] 2. Implement domain-pack registration and safe agent lifecycle
  - [ ] 2.1 Implement JSON schemas and a root-confined `DomainPackValidator` that atomically records valid non-active packs or inactive invalid outcomes.
    - Target areas: `business/schemas/`, `backend/app/registry/pack_validator.py`, `backend/app/repositories/pack_repository.py`.
    - Enforce canonical unique pack/agent IDs, 1–100 agents, draft/registered status, and no production-activation request.
    - _Requirements: 2.1–2.4_
  - [ ] 2.2 Implement `AgentActivationService` with an atomic ALC/learning-contract transition and draft-production denial.
    - Target areas: `backend/app/registry/activation.py`, `backend/app/models/agents.py`.
    - Preserve prior state on every invalid learning contract; never partially activate.
    - _Requirements: 2.5–2.7_
  - [ ]* 2.3 Write Hypothesis property test for atomic manifest validation and registration.
    - **Property 3: Domain manifest validation and registration are atomic**.
    - Target area: `backend/tests/properties/test_property_03_manifest.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_03_manifest.py`.
    - **Validates: Requirements 2.2–2.4**
  - [ ]* 2.4 Write Hypothesis property test for agent lifecycle and learning activation safety.
    - **Property 4: Lifecycle and learning activation preserve safety**.
    - Target area: `backend/tests/properties/test_property_04_activation.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_04_activation.py`.
    - **Validates: Requirements 2.5–2.7**
  - [ ]* 2.5 Write schema/edge unit tests for invalid IDs, boundary agent counts, duplicate canonical IDs, and production activation requests.
    - Target area: `backend/tests/unit/registry/`; validate with `cd backend && python -m pytest -q tests/unit/registry`.
    - _Requirements: 2.1–2.7_

  - [ ] 2.6 Checkpoint — Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise. Record target-local command results and immutable evidence only; do not perform production operations.

- [ ] 3. Build deterministic workflow definition, run durability, and LegacyEngine behavior
  - [ ] 3.1 Implement data-only WorkflowDNA/pack-graph schemas and validators for bounded patterns, registered references, scoped memory/tool declarations, rollback, and engine selection.
    - Target areas: `business/schemas/workflow-dna.schema.json`, `backend/app/workflows/validator.py`, `backend/app/workflows/graph_validator.py`.
    - Reject invalid definitions before any run, compile, dispatch, adapter call, or effect.
    - _Requirements: 4.1–4.2, 4.5, 10.3–10.4_
  - [ ] 3.2 Implement durable queued `RunRecord` creation, idempotent dispatch-attempt state, status transitions, and target-local JSON seed/backup repository.
    - Target areas: `backend/app/runs/service.py`, `backend/app/repositories/run_repository.py`, `backend/data/` seed-only files.
    - Persist selected engine and queued status before dispatch; local JSON must not claim production durability.
    - _Requirements: 4.1–4.2, 6.1–6.3_
  - [ ] 3.3 Implement bounded `LegacyEngine` execution and durable failure processing with completed-effect preservation, stopped unstarted steps, and operator-visible failure state.
    - Target areas: `backend/app/engines/legacy.py`, `backend/app/runs/failure_processing.py`.
    - Use only Host services and declared compensation; never rerun ambiguous effects.
    - _Requirements: 4.3–4.4, 4.9_
  - [ ]* 3.4 Write Hypothesis property test for definition validation, unique queued run creation, and persistence-before-dispatch.
    - **Property 8: Definition validation controls run creation and dispatch ordering**.
    - Target area: `backend/tests/properties/test_property_08_run_creation.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_08_run_creation.py`.
    - **Validates: Requirements 4.1–4.2, 6.1**
  - [ ]* 3.5 Write Hypothesis property test for failure processing completeness and terminal safety.
    - **Property 9: Failure processing is terminally safe and evidence-complete**.
    - Target area: `backend/tests/properties/test_property_09_failure.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_09_failure.py`.
    - **Validates: Requirements 4.3–4.4**
  - [ ]* 3.6 Write Hypothesis property test for successful completion effect retention.
    - **Property 12: Successful execution preserves effects at completion**.
    - Target area: `backend/tests/properties/test_property_12_completion.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_12_completion.py`.
    - **Validates: Requirements 4.9**
  - [ ]* 3.7 Write unit tests for invalid definitions, dispatch-failure persistence ordering, legacy bounded linear execution, and safe failure projections.
    - Target area: `backend/tests/unit/workflows/`; validate with `cd backend && python -m pytest -q tests/unit/workflows`.
    - _Requirements: 4.1–4.4, 6.1–6.3_


- [ ] 4. Add fail-closed tool governance, approval gates, and production-operation guards
  - [ ] 4.1 Implement the Host-only tool broker, local adapter allow-list, complete authorization intersection, independent-call evaluation, and denial audit behavior.
    - Target areas: `backend/app/governance/tool_broker.py`, `backend/app/governance/authorization.py`, `backend/app/audit/`.
    - Never accept arbitrary callables, shell commands, credentials, or URLs; a denial produces no adapter effect even when audit is unavailable.
    - _Requirements: 5.1–5.5_
  - [ ] 4.2 Implement `GovernanceService` and immutable approval submissions with pause-before-effect, safe previews, decision validity, and resume-time reauthorization.
    - Target areas: `backend/app/governance/approvals.py`, `backend/app/repositories/approval_repository.py`.
    - Retain invalid submissions; valid denials remain paused; only a valid approval may trigger a fresh broker check.
    - _Requirements: 5.6–5.11, 6.5–6.6_
  - [ ]* 4.3 Write Hypothesis property test for complete, independent, fail-closed tool authorization.
    - **Property 13: Tool authorization is complete, independent, and fail-closed**.
    - Target area: `backend/tests/properties/test_property_13_authorization.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_13_authorization.py`.
    - **Validates: Requirements 5.1–5.3, 5.5**
  - [ ]* 4.4 Write Hypothesis property test for approval retention, pausing, and resume-time reauthorization.
    - **Property 14: Approval gates retain submissions and reauthorize effects**.
    - Target area: `backend/tests/properties/test_property_14_approvals.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_14_approvals.py`.
    - **Validates: Requirements 5.6–5.7, 5.9–5.11**
  - [ ] 4.5 Implement per-operation prohibited-operation classification and an atomic production-change block latch.
    - Target areas: `backend/app/governance/operation_guard.py`, `backend/app/models/operations.py`.
    - Prohibit automatic promotion, Host-code rewrites, unbounded orchestration, and orchestration without recorded authorization; preserve independently authorized safe operation handling.
    - _Requirements: 10.3–10.6_
  - [ ]* 4.6 Write Hypothesis property test for atomic multi-operation guard behavior.
    - **Property 22: Multi-operation production guard is atomic yet isolates safe operations**.
    - Target area: `backend/tests/properties/test_property_22_operation_guard.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_22_operation_guard.py`.
    - **Validates: Requirements 10.3–10.4, 10.6**
  - [ ]* 4.7 Write focused unit tests for denied-call audit failure, decision reason boundaries (0/1/1,000/1,001), invalid values, and failed prohibited-error delivery.
    - Target area: `backend/tests/unit/governance/`; validate with `cd backend && python -m pytest -q tests/unit/governance`.
    - _Requirements: 5.4, 5.8, 10.5_

- [ ] 5. Expose the bounded FastAPI control plane and deterministic local execution path
  - [ ] 5.1 Create the single in-process FastAPI application, authenticated request context, versioned router, and public-route enforcement.
    - Target areas: `backend/app/main.py`, `backend/app/api/v1/router.py`, `backend/app/api/v1/dependencies.py`.
    - Expose only `/api/v1/*`; derive actor and organization from trusted request state, never from workflow payloads.
    - _Requirements: 1.2, 6.5–6.6, 10.1_
  - [ ] 5.2 Implement definition, run, dispatch, observation, approval, and topology/graph-state endpoints with organization-filtered redacted projections and stable error codes.
    - Target areas: `backend/app/api/v1/routes/`, `backend/app/api/v1/schemas/`.
    - Action/recommendation/approval/failure responses include required human-centered fields and pre-effect previews.
    - _Requirements: 2.3, 4.1–4.4, 5.6–5.11, 6.5–6.6_
  - [ ] 5.3 Implement deterministic versioned local adapters for contract parsing, policy lookup, CRM, billing, email, audit, and no-network media stubs.
    - Target areas: `backend/app/adapters/`, `backend/tests/fakes/`.
    - Require invocation through the broker; emit durable `ToolEffect` data and do not use external resources.
    - _Requirements: 4.3, 4.9, 5.1–5.4, 10.2_
  - [ ]* 5.4 Write Hypothesis property test for visible actionable state and mandatory pre-effect previews.
    - **Property 15: Operator-visible executable state is actionable before effect**.
    - Target area: `backend/tests/properties/test_property_15_operator_view.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_15_operator_view.py`.
    - **Validates: Requirements 6.5–6.6**
  - [ ]* 5.5 Write isolated FastAPI integration tests for `/api/v1/*` exclusivity, authenticated tenancy, redaction, queue/dispatch, observations, and denied external adapter access.
    - Target area: `backend/tests/integration/api/`; validate with `cd backend && python -m pytest -q tests/integration/api`.
    - _Requirements: 2.1, 4.1–4.4, 6.1–6.3, 10.1–10.2_
  - [ ]* 5.6 Write the deterministic local LegacyEngine E1 evidence test, retaining run/configuration/adapter hashes and command result.
    - Target areas: `backend/tests/evidence/test_e1_legacy.py`, `business/evidence/` runtime output ignored from source control as appropriate.
    - Validate with `cd backend && python -m pytest -q tests/evidence/test_e1_legacy.py`; no deployment or live integration.
    - _Requirements: 4.1–4.4, 8.6–8.7_

  - [ ] 5.7 Checkpoint — Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise. Run only focused target-local checks plus `npm run sdd:check`; retain results as evidence and leave production unchanged.

- [ ] 6. Implement process intelligence and provenance-safe scoped memory
  - [ ] 6.1 Implement permitted event-log validation and root-confined process-artifact persistence with source log-set and supporting-record references.
    - Target areas: `backend/app/process_intelligence/`, `business/process-intelligence/`.
    - Do not ingest external sources or write outside the target workspace.
    - _Requirements: 3.1_
  - [ ]* 6.2 Write Hypothesis property test for process-artifact source traceability.
    - **Property 5: Process artifacts retain source traceability**.
    - Target area: `backend/tests/properties/test_property_05_process_artifacts.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_05_process_artifacts.py`.
    - **Validates: Requirements 3.1**
  - [ ] 6.3 Implement scoped-memory storage, provenance validation, primary/alternative audit handling, and durable high-impact audit-unavailable safety latch.
    - Target areas: `backend/app/memory/service.py`, `backend/app/memory/models.py`, `backend/app/audit/health.py`.
    - Keep high-impact writes blocked through critical/recovery paths until audit health is restored.
    - _Requirements: 3.2–3.5_
  - [ ]* 6.4 Write Hypothesis property test for high-impact memory provenance, scope, audit fallback, and latch safety.
    - **Property 6: High-impact memory is provenance-, scope-, and audit-safe**.
    - Target area: `backend/tests/properties/test_property_06_memory_writes.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_06_memory_writes.py`.
    - **Validates: Requirements 3.2–3.3, 3.5**
  - [ ] 6.5 Implement semantic-first scoped retrieval with permitted Tier-1/Tier-2 escalation and provenance-bearing no-result behavior.
    - Target areas: `backend/app/memory/retrieval.py`, `backend/app/memory/indexes/`.
    - Filter scope before every tier and never broaden after an in-scope miss.
    - _Requirements: 3.6–3.7_
  - [ ]* 6.6 Write Hypothesis property test for semantic-first retrieval and cross-scope non-disclosure.
    - **Property 7: Retrieval is semantic-first and cannot disclose across scope**.
    - Target area: `backend/tests/properties/test_property_07_retrieval.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_07_retrieval.py`.
    - **Validates: Requirements 3.6–3.7**
  - [ ]* 6.7 Write focused unit/integration tests for primary-versus-alternate audit behavior, both-sink outage recovery, PI artifact paths, and empty scoped retrieval.
    - Target area: `backend/tests/unit/memory/`, `backend/tests/integration/process_intelligence/`; validate with `cd backend && python -m pytest -q tests/unit/memory tests/integration/process_intelligence`.
    - _Requirements: 3.1–3.7_

- [ ] 7. Add evaluation, independent Product-Bar evidence, and sandbox-only evolution
  - [ ] 7.1 Add at least 20 deterministic golden JSON tasks and implement named regression, adversarial, historical-replay, cost, latency, safety, and compliance evaluation recording.
    - Target areas: `business/evals/golden-tasks/`, `backend/app/evaluation/`, `backend/app/repositories/evaluation_repository.py`.
    - Retain distinct run records for identical task/configuration executions and continue non-blocking checks after a blocker.
    - _Requirements: 8.1–8.5, 8.8_
  - [ ]* 7.2 Write Hypothesis property test for evaluation execution identity and current-blocker transition semantics.
    - **Property 18: Evaluation results preserve execution identity and current-blocker semantics**.
    - Target area: `backend/tests/properties/test_property_18_evaluations.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_18_evaluations.py`.
    - **Validates: Requirements 8.2, 8.5, 8.8**
  - [ ] 7.3 Implement independent E1–E9 Product-Bar evidence records and incomplete status when E1 lacks a passing result.
    - Target areas: `backend/app/evaluation/product_bar.py`, `backend/app/models/evidence.py`.
    - Evidence stores hashes, IDs, timestamps, test command/results, and supporting references; passing tests remain evidence, not proof.
    - _Requirements: 8.6–8.7_
  - [ ]* 7.4 Write Hypothesis property test for independent Product-Bar completeness.
    - **Property 19: Product-bar evidence is independently complete**.
    - Target area: `backend/tests/properties/test_property_19_product_bar.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_19_product_bar.py`.
    - **Validates: Requirements 8.6**
  - [ ] 7.5 Implement immutable SandboxVariant creation, promotion assessment, scoped canary lifecycle, recorded rollback, and fail-closed non-promotion rules.
    - Target areas: `backend/app/evolution/`, `backend/app/repositories/evolution_repository.py`.
    - Never mutate production workflow/graph/prompt/role/tool configuration or Host code; require exactly one fully evidenced candidate and human approval.
    - _Requirements: 7.1–7.10_
  - [ ]* 7.6 Write Hypothesis property test for isolated variants and exhaustive promotion conditions.
    - **Property 16: Evolution variants are isolated and promotion is exhaustive**.
    - Target area: `backend/tests/properties/test_property_16_evolution.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_16_evolution.py`.
    - **Validates: Requirements 7.1–7.3, 7.6**
  - [ ]* 7.7 Write Hypothesis property test for approved active-canary scope containment.
    - **Property 17: Active canaries enforce approved scope containment**.
    - Target area: `backend/tests/properties/test_property_17_canary.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_17_canary.py`.
    - **Validates: Requirements 7.9**
  - [ ]* 7.8 Write barrier-controlled integration tests for immediate blocking transitions, non-blocking continuation, zero/multiple candidates, delayed canary activation, retention failure, and canary rollback.
    - Target area: `backend/tests/integration/evaluation_evolution/`; validate with `cd backend && python -m pytest -q tests/integration/evaluation_evolution`.
    - _Requirements: 7.4–7.8, 7.10, 8.3–8.4, 8.7_


- [ ] 8. Deliver the constrained, stub-only Video_Pack controls
  - [ ] 8.1 Create the Video_Pack layout, exact 114-agent inventory validator, required handoff/critique schemas, and release-control policy assets.
    - Target areas: `business/video/agents/`, `business/video/manifest.json`, `business/video/schemas/`, `business/video/policies/`, `backend/app/video/inventory.py`.
    - Agent assets remain configuration data under the pack; do not import, copy, or adopt source from the reference workspace.
    - _Requirements: 2.1–2.4, 9.1_
  - [ ]* 8.2 Write Hypothesis property test for the exact video agent-to-inventory-entry bijection.
    - **Property 20: Video inventory is an exact agent-to-entry bijection**.
    - Target area: `backend/tests/properties/test_property_20_video_inventory.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_20_video_inventory.py`.
    - **Validates: Requirements 9.1**
  - [ ] 8.3 Implement the stub-media `pack_spine`/supervisor workflow, durable blocker events, cancellation token, and visible graph-state preservation.
    - Target areas: `business/video/workflows/`, `business/video/graphs/`, `backend/app/video/blockers.py`, `backend/app/adapters/video_stub.py`.
    - Use deterministic no-network stubs; a ComplianceAgent blocker prevents new graph steps in under five seconds.
    - _Requirements: 9.2–9.3, 10.2_
  - [ ] 8.4 Implement copy-on-write video artifact versions, acyclic lineage validation, release-request retention, and complete fail-closed release evaluation.
    - Target areas: `backend/app/video/artifacts.py`, `backend/app/video/release.py`, `backend/app/repositories/artifact_repository.py`.
    - Evaluate rights/consent, provenance/sign-off, named quality/release gates, and unresolved blockers without invoking a media provider.
    - _Requirements: 9.4–9.5_
  - [ ]* 8.5 Write Hypothesis property test for complete fail-closed video release gates.
    - **Property 21: Video release is a complete fail-closed gate**.
    - Target area: `backend/tests/properties/test_property_21_video_release.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_21_video_release.py`.
    - **Validates: Requirements 9.4–9.5**
  - [ ]* 8.6 Write deterministic integration tests for the stub-only end-to-end spine, less-than-five-second blocker stop, retained graph state, release denials, and permitted release.
    - Target area: `backend/tests/integration/video/`; validate with `cd backend && python -m pytest -q tests/integration/video`.
    - _Requirements: 9.2–9.5, 10.2_

  - [ ] 8.7 Checkpoint — Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise. Verify local fixtures and adapters make no network access; retain gate evidence without activating a production canary or release.

- [ ] 9. Implement bounded in-process GraphEngine migration and durable checkpoint recovery
  - [ ] 9.1 Add the shared `WorkflowEngine` seam and in-process bounded GraphEngine compiler/executor for permitted patterns.
    - Target areas: `backend/app/engines/protocol.py`, `backend/app/engines/graph.py`, `backend/app/engines/compiler.py`.
    - Enforce 100 node visits, 12 handoffs, 900 seconds, and 50 tool requests; graph nodes use only narrow Host services and the broker.
    - _Requirements: 4.5, 4.8, 10.1_
  - [ ]* 9.2 Write Hypothesis property test for stopping at the first GraphEngine budget breach.
    - **Property 10: Graph budget enforcement stops at the first breached limit**.
    - Target area: `backend/tests/properties/test_property_10_graph_budget.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_10_graph_budget.py`.
    - **Validates: Requirements 4.5**
  - [ ] 9.3 Implement the configured-Postgres checkpoint repository, `{organization_id}:{run_id}` thread construction, same-org resume checks, and fail-closed durable-transition handling.
    - Target areas: `backend/app/repositories/postgres_checkpoint.py`, `backend/app/runs/checkpoints.py`, `backend/migrations/`.
    - Keep in-memory checkpoints limited to tests; do not provision databases, run migrations against shared environments, or claim durability without configured Postgres.
    - _Requirements: 6.4, 10.1_
  - [ ]* 9.4 Write isolated Postgres integration tests for restart recovery, same-organization checkpoint resume, cross-organization denial before lookup, and outage fail-closed behavior.
    - Target area: `backend/tests/integration/checkpoints/`; validate with `cd backend && python -m pytest -q tests/integration/checkpoints`.
    - **Validates: Requirements 6.4**
  - [ ] 9.5 Implement migration-gate assessment and atomic LegacyEngine retirement that disables new work and terminates active legacy runs with evidence when all gates are current.
    - Target areas: `backend/app/engines/migration.py`, `backend/app/runs/service.py`, `backend/app/evaluation/migration_evidence.py`.
    - Legacy remains available until every required proof passes; retirement is a reviewed capability change, never an automatic deployment.
    - _Requirements: 4.6–4.8_
  - [ ]* 9.6 Write Hypothesis property test for all-evidence dual-engine migration gate satisfaction.
    - **Property 11: Migration gate satisfaction is an all-evidence conjunction**.
    - Target area: `backend/tests/properties/test_property_11_migration_gate.py`; validate with `cd backend && python -m pytest -q tests/properties/test_property_11_migration_gate.py`.
    - **Validates: Requirements 4.8**
  - [ ]* 9.7 Write deterministic integration tests for two-specialist handoffs, graph topology/interrupt visibility, approval resume, LegacyEngine availability/retirement, cross-org denial, and graph E1 evidence.
    - Target area: `backend/tests/integration/graph_engine/`; validate with `cd backend && python -m pytest -q tests/integration/graph_engine`.
    - _Requirements: 4.5–4.9, 5.6–5.11, 6.4–6.6, 8.6–8.7_

- [ ] 10. Wire evidence gates and target-local automated verification
  - [ ] 10.1 Implement a deterministic evidence-gate runner that assembles independent E1–E9 records from retained evaluation, run, video, and migration evidence without mutating production.
    - Target areas: `backend/app/evidence/gates.py`, `backend/app/evidence/records.py`, `backend/tests/evidence/`.
    - Gate failures block only the next configured transition and retain diagnostics; never treat a prior pass as a substitute for current evidence.
    - _Requirements: 7.2–7.7, 8.1–8.8, 9.1–9.5_
  - [ ]* 10.2 Write final target-local evidence integration tests for E1–E9, all 22 properties, named checks, route-only exposure, stub-only adapters, and blocked unsafe operations.
    - Target area: `backend/tests/evidence/test_product_bar.py`; validate with `cd backend && python -m pytest -q tests/evidence`.
    - _Requirements: 1.1–10.6_
  - [ ]* 10.3 Add automated SDD/static evidence verification for the final implementation manifest, test command metadata, and no-reference-workspace invariant.
    - Target areas: `scripts/verify_generic_swarm_evidence.py`, `tests/`; validate with `npm run sdd:check` and the focused test command documented by the script.
    - Do not scan, read, execute, or copy `C:\Project\generic-swarm-ops`.
    - _Requirements: 1.2–1.5, 8.6–8.7, 10.1–10.5_

  - [ ] 10.4 Final checkpoint — Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise. Run `npm run sdd:check` and focused, quiet target-local backend suites; retain commands/results as evidence. Do not deploy, provision infrastructure, activate a production canary, release video artifacts, or perform any unsafe production operation.

## Notes

- Tasks marked with `*` are optional test tasks. Property tests use Hypothesis with at least 100 bounded examples and the required `Feature: generic-swarm-business-os, Property N: …` source comment.
- Test tasks use deterministic fakes, local fixtures, and isolated databases only. Postgres restart validation is permitted only against an explicitly isolated local test fixture; no shared or production database may be touched.
- Each implementation task is constrained to the target workspace. The reference workspace is outside scope and is not a source of code, fixtures, execution, or implementation truth.
- Evidence gates are code/test artifacts: record IDs, hashes, timestamps, command/results, and supporting references. They never authorize deployment, automatic promotion, or a bypass of audit, authorization, approval, or release controls.
- Validation commands assume the scaffold created in Task 1.1. Use `-q` to keep test output focused; run only the affected paths while implementing each task.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["1.4", "1.5", "1.6", "2.1", "3.1", "4.5"] },
    { "id": 3, "tasks": ["2.2", "2.3", "2.5", "3.2", "4.6"] },
    { "id": 4, "tasks": ["2.4", "3.3", "3.4", "4.1"] },
    { "id": 5, "tasks": ["3.5", "3.6", "3.7", "4.2", "4.3"] },
    { "id": 6, "tasks": ["4.4", "4.7", "5.1", "6.1"] },
    { "id": 7, "tasks": ["5.2", "5.3", "6.2", "6.3"] },
    { "id": 8, "tasks": ["5.4", "5.5", "6.4", "6.5", "7.1"] },
    { "id": 9, "tasks": ["5.6", "6.6", "6.7", "7.2", "7.3"] },
    { "id": 10, "tasks": ["7.4", "7.5", "8.1"] },
    { "id": 11, "tasks": ["7.6", "7.7", "7.8", "8.2", "8.3"] },
    { "id": 12, "tasks": ["8.4", "9.1"] },
    { "id": 13, "tasks": ["8.5", "9.2", "9.3"] },
    { "id": 14, "tasks": ["8.6", "9.4", "9.5"] },
    { "id": 15, "tasks": ["9.6", "9.7"] },
    { "id": 16, "tasks": ["10.1"] },
    { "id": 17, "tasks": ["10.2", "10.3"] }
  ]
}
```
