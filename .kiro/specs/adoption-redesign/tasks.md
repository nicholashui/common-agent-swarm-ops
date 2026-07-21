# Implementation Plan: Adoption Redesign

## Overview

Implement the approved domain-neutral Adoption_Platform in the existing Python 3.12/FastAPI backend. The work builds typed immutable evidence, fail-closed controllers, durable repositories, API wiring, and automated verification without changing VA business semantics or using real providers. Every generated property test uses Hypothesis with `@settings(max_examples=100, deadline=None)`, deterministic fakes, bounded strategies, and the required `Feature: adoption-redesign, Property N: ...` comment.

## Tasks

- [ ] 1. Establish shared adoption contracts and durable evidence foundations
  - [ ] 1.1 Add immutable typed Adoption_Platform contracts and typed outcomes
    - Extend `backend/app/models/contracts.py`, `evidence.py`, `runs.py`, and `identifiers.py` with independently versioned Host_Contract, Pack_Contract, ALC, Domain_Pack, registration, compatibility, invocation, lifecycle, handoff, learning, release, recovery, and maturity models.
    - Define explicit `Allowed`, `Denied`, `Blocked`, and `FailedRecoverable` results plus correlation-linked immutable-record invariants; preserve references rather than sensitive payload copies.
    - _Requirements: 1.1, 1.7, 1.11, 3.9, 4.7, 4.10, 5.9, 7.12, 8.1, 9.7_

  - [ ] 1.2 Add adoption repositories, uniqueness constraints, and deterministic fakes
    - Extend `backend/app/repositories/protocols.py` and implementation modules; add migrations for composite pack-version uniqueness, unique terminal Learning_Episode per attempt, release-decision uniqueness, immutable evidence, and acyclic handoff persistence.
    - Add isolated fake repositories and provider adapters in `backend/tests/fakes/` so tests never use production storage or external providers.
    - _Requirements: 1.7, 1.11, 3.9, 4.7, 4.10, 5.4, 6.10, 7.5, 7.6, 9.4–9.6_

  - [ ]* 1.3 Write deterministic contract, repository, and audit-resilience tests
    - Test schema validity, immutability/uniqueness, required Audit_Record payloads, and explicitly permitted audit-write failures without weakening the primary denial or rejection.
    - _Requirements: 1.5, 1.6, 1.10, 2.5, 2.6, 3.3, 3.4, 3.6, 3.8, 3.14, 4.9, 5.4, 8.10, 9.2, 9.10_

- [ ] 2. Implement pack admission, VA preservation, and compatibility controls
  - [ ] 2.1 Implement Pack_Contract admission and Compatibility Registry services
    - Add admission and compatibility services under `backend/app/registry/`; validate declarative-only packs, identity/version/digest/signer/agents/workflows/capabilities/classifications/ALC/evaluations, policies, VA reference-only assets, extension schemas, and range intersections.
    - Persist registration and Compatibility_Status decisions; retain superseded approved versions and reproduction contracts, and keep operations available if executable code is detected only after a prior successful VA registration.
    - _Requirements: 1.2–1.7, 1.11, 2.1–2.7, 2.8–2.10, 8.1–8.5, 8.12_

  - [ ]* 2.2 Write property test for complete, fail-closed admission
    - **Property 1: Admission is a complete, fail-closed decision.** Generate valid/invalid declarations and policy vectors; assert approval/record preservation iff every contract and policy check passes.
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.7**

  - [ ]* 2.3 Write property test for VA declarative, reference-only safety
    - **Property 3: VA packages retain declarative, reference-only safety.** Generate VA assets, executable-code signals, and handoff extensions; assert rejection/reference-only records/schema-gated acceptance.
    - **Validates: Requirements 2.2, 2.4, 2.8, 2.9**

  - [ ]* 2.4 Write property test for intersection-based compatibility guards
    - **Property 20: Compatibility is intersection-based and blocks use when incompatible.** Generate independent version ranges; assert recorded status, activation/invocation denial, and compatibility-matrix recording.
    - **Validates: Requirements 7.12, 8.2, 8.3, 8.4, 8.5**

  - [ ]* 2.5 Write deterministic admission and VA ownership tests
    - Cover one shared Pack_Contract, canonical VA source ownership, shared extension/lifecycle patterns, rejection/block audits, superseded-version reproducibility, and new-domain activation eligibility.
    - _Requirements: 1.1, 1.5, 1.10, 1.11, 2.1, 2.3, 2.5–2.7, 2.10, 8.12_

- [ ] 3. Enforce governed invocation, access, and artifact handoff execution
  - [ ] 3.1 Implement invocation orchestration, governance decisions, and handoff barriers
    - Extend `backend/app/runs/`, `governance/`, `repositories/artifact_repository.py`, and `workflows/` to persist invocation association before node start; enforce declared workflow budget, rollback, approval, memory-read/write, data scope, tool, outbound, and capacity policies.
    - Implement immutable DAG handoffs: internal availability at completed metadata persistence; external availability only after persistence confirmation, with revocation/audit on premature exposure.
    - _Requirements: 1.8–1.10, 3.1–3.15, 7.1, 7.3, 9.9, 9.10_

  - [ ]* 3.2 Write property test for invocation association as an execution barrier
    - **Property 2: Invocation association is an execution barrier.** Generate association persistence outcomes and assert no node starts on failure.
    - **Validates: Requirements 1.8, 1.9**

  - [ ]* 3.3 Write property test for declared-scope data access
    - **Property 4: Data access remains within every declared scope.** Generate approved scopes and boundary mutations; assert cross-organization, cross-domain, and undeclared-memory requests are denied.
    - **Validates: Requirements 3.1, 3.2, 7.3**

  - [ ]* 3.4 Write property test for undeclared capability containment
    - **Property 5: Undeclared capabilities cannot escape governance.** Generate tool/destination allow-lists and absent requests; assert each is denied.
    - **Validates: Requirements 3.5, 3.7**

  - [ ]* 3.5 Write property test for handoff evidence and availability
    - **Property 6: Artifact availability follows complete, acyclic evidence.** Generate bounded DAGs, metadata, and persistence events; assert required references, barrier behavior, revocation, and no cyclic persistence.
    - **Validates: Requirements 3.9–3.13, 7.1, 7.3**

  - [ ]* 3.6 Write property test for declared workflow policy enforcement
    - **Property 7: Declared workflow policies are enforced at every action.** Generate policy-breaching actions and assert completion is prevented or declared rollback executes.
    - **Validates: Requirements 3.15**

  - [ ]* 3.7 Write deterministic governance and handoff resilience tests
    - Test deny audits and allowed audit-write failure paths, association-denial audit, handoff block/revocation audits, and capacity-action selection/auditing.
    - _Requirements: 1.10, 3.3, 3.4, 3.6, 3.8, 3.14, 9.9, 9.10_

- [ ] 4. Implement the learning-agent lifecycle and execution evidence
  - [ ] 4.1 Implement ALC activation, retrieval, and terminal-episode services
    - Add lifecycle services in `backend/app/memory/` and lifecycle integration in `registry/` and `runs/`; require exactly one effective agent-named ALC and all activation evidence, suspend before lifecycle-affecting changes, persist a retrieval record before execution, and atomically retain one immutable terminal episode or block for recovery.
    - _Requirements: 4.1–4.11_

  - [ ]* 4.2 Write property test for atomic, evidence-complete learning activation
    - **Property 8: Learning-agent activation is atomic and evidence-complete.** Generate ALC sets, lifecycle states, change events, and evaluation vectors; assert active iff all required conditions pass.
    - **Validates: Requirements 4.1–4.6, 7.3**

  - [ ]* 4.3 Write property test for pre-action retrieval evidence
    - **Property 9: Retrieval evidence precedes learning-required execution.** Generate filtered empty/non-empty retrievals and persistence failures; assert exactly one record precedes execution or the action blocks.
    - **Validates: Requirements 4.7, 4.8**

  - [ ]* 4.4 Write property test for immutable terminal learning episodes
    - **Property 10: Terminal learning outcomes are immutable and recoverable.** Generate repeated terminal notifications and write failures; assert exactly one episode or recovery-blocked status.
    - **Validates: Requirements 4.10, 4.11**

  - [ ]* 4.5 Write deterministic lifecycle audit and edge-case tests
    - Cover retrieval persistence denial/audit, zero and multiple ALCs, every terminal outcome, suspend-before-change ordering, and recovery-worker idempotency.
    - _Requirements: 4.1, 4.4, 4.7–4.11_

- [ ] 5. Implement lesson governance, provenance, observability, and improvement promotion
  - [ ] 5.1 Implement lesson, proposal, observability, and promotion services
    - Extend `backend/app/memory/`, `evolution/`, `audit/`, and `evidence/` to assess scoped Lessons, apply audit-committed revocation, link output provenance, return redacted per-agent counts, preserve failed sandbox evidence, and require reviewer-recorded approval before immutable promotion/rollback auditing.
    - _Requirements: 5.1–5.14_

  - [ ]* 5.2 Write property test for lesson assessment and scoped retrieval
    - **Property 11: Lesson assessment and retrieval enforce complete scope.** Generate assessment criteria and scope vectors; assert only fully assessed Lessons are retrievable in their complete approved scope.
    - **Validates: Requirements 5.1, 5.2, 5.3**

  - [ ]* 5.3 Write property test for audit-gated lesson revocation
    - **Property 12: Revocation changes retrieval only after auditable commitment.** Generate revocation persistence outcomes; assert retrievability changes only after the Audit_Record commits.
    - **Validates: Requirements 5.5, 5.6**

  - [ ]* 5.4 Write property test for non-invented output provenance
    - **Property 13: Output provenance is complete without inventing retrieval.** Generate outputs with and without retrieval records; assert correct episode links without fabricated retrieval links.
    - **Validates: Requirements 5.7, 5.8**

  - [ ]* 5.5 Write property test for redacted learning observability
    - **Property 14: Learning observability preserves counts while redacting content.** Generate mixed lesson/episode sets; assert exact counts and absence of sensitive Lesson content.
    - **Validates: Requirements 5.9**

  - [ ]* 5.6 Write property test for sandboxed improvement promotion
    - **Property 15: Improvement remains sandboxed until governed promotion.** Generate repeated failures, approvals, and transitions; assert evidence-first proposals, denied unapproved live changes, failure preservation, and rollback provenance.
    - **Validates: Requirements 5.10–5.12, 5.14, 7.3**

  - [ ]* 5.7 Write deterministic lesson and reviewer-decision tests
    - Cover revocation Audit_Record payloads, reviewer identity/timestamp/evidence/promotion state, and all prohibited live-change targets before approval.
    - _Requirements: 5.4, 5.12, 5.13_

- [ ] 6. Implement migration, activation-eligibility, and recovery controllers
  - [ ] 6.1 Implement migration phase, VA activation, rollback, and recovery services
    - Extend `backend/app/engines/migration.py`, `evaluation/migration_evidence.py`, `video/inventory.py`, and recovery/evidence repositories to persist phase records; enforce source-index dispositions and 114-agent mappings; gate VA activation; restore approved immutable targets; and halt recovery before restoration if required investigation evidence cannot persist.
    - _Requirements: 6.1–6.10, 8.6, 8.7, 9.4–9.6_

  - [ ]* 6.2 Write property test for complete frozen VA inventory and roster evidence
    - **Property 16: Frozen VA inventory and roster evidence are complete.** Generate inventories and mappings; assert all required asset fields/dispositions and exactly one mapping for each of 114 indexed agents.
    - **Validates: Requirements 6.2, 6.3, 6.4**

  - [ ]* 6.3 Write property test for VA activation evidence and approval gates
    - **Property 17: VA activation eligibility cannot bypass evidence or approval.** Generate workflow evidence and approval states; assert eligibility iff evidence passes and no active transition without explicit approval.
    - **Validates: Requirements 6.5, 6.6, 6.7**

  - [ ]* 6.4 Write property test for migration rollback target and retention behavior
    - **Property 18: Approved rollback restores the designated version and retention outcome.** Generate rollback targets and affected Lessons; assert exact restoration and ALC-selected retention for each Lesson.
    - **Validates: Requirements 6.8, 6.9**

  - [ ]* 6.5 Write property test for contract-breaking change evidence
    - **Property 21: Contract-breaking approval requires complete evidence.** Generate change-evidence records with missing and complete artifact sets; assert approval iff every required artifact exists.
    - **Validates: Requirements 8.6, 8.7**

  - [ ]* 6.6 Write property test for evidence-gated, target-exact recovery
    - **Property 25: Recovery is evidence-gated and target-exact.** Generate approved recovery actions and evidence persistence outcomes; assert no restore before evidence and exact immutable target after it.
    - **Validates: Requirements 9.4, 9.5, 9.6**

  - [ ]* 6.7 Write deterministic migration and recovery evidence tests
    - Cover phase-record fields, host/VA-owner reviews, rollback-evidence retention, pending approval behavior, and idempotent completed Recovery_Actions.
    - _Requirements: 6.1, 6.6–6.10, 9.4–9.6_

- [ ] 7. Implement provider governance and operational containment
  - [ ] 7.1 Implement Provider_Adapter authorization, fault containment, maturity, and capacity controls
    - Extend `backend/app/adapters/`, `governance/adapter_execution.py`, `governance/operation_guard.py`, and status/evidence models to require complete provider declarations, deny faults without relying on audit success, retain independent agent maturity during pack disablement, and apply auditable throttle-or-disable decisions.
    - _Requirements: 8.8–8.11, 9.1, 9.2, 9.7–9.10_

  - [ ]* 7.2 Write property test for fail-closed provider authorization and faults
    - **Property 22: Provider authorization and failures fail closed.** Generate provider declarations and outcomes; assert authorization only with all fields and denial for missing declarations, timeout, unsafe, over-budget, or unavailable results.
    - **Validates: Requirements 8.8, 8.9, 9.1**

  - [ ]* 7.3 Write property test for new-domain onboarding admission evidence
    - **Property 23: Domain onboarding requires admission evidence.** Generate onboarding declarations; assert activation eligibility only for Pack_Contract-valid packs with evaluation references.
    - **Validates: Requirements 8.12**

  - [ ]* 7.4 Write property test for mandatory video release gates
    - **Property 24: Video releases fail closed on every mandatory gate.** Generate video handoff gate sets; assert omission of any required gate returns a blocked release decision.
    - **Validates: Requirements 9.3**

  - [ ]* 7.5 Write property test for capacity containment and independent maturity
    - **Property 26: Operational containment preserves independent maturity evidence.** Generate limits, capacity actions, provider failures, and agent maturity states; assert exact containment and unchanged per-agent maturity.
    - **Validates: Requirements 9.8, 9.9**

  - [ ]* 7.6 Write deterministic provider and operational audit tests
    - Cover provider-denial Audit_Record behavior when audit persistence fails, authorized mocks only, separate maturity states, and capacity-action audit payloads.
    - _Requirements: 8.10, 8.11, 9.1, 9.2, 9.7–9.10_

- [ ] 8. Build Verification_Suite evidence production and automated integration coverage
  - [ ] 8.1 Implement the Verification_Suite and immutable release-evidence projection
    - Add verification services under `backend/app/evidence/` and `evaluation/` that store deterministic schema/unit/property/integration outputs, fixed seeds, fixture digests, compatibility-matrix results, Audit_Records, UI projections, coverage state, failure records, and terminal Release_Readiness_Decisions.
    - Keep failure-record persistence independent so remaining verification continues, retain completed coverage evidence, and allow policy-authorized administrative failure decisions.
    - _Requirements: 7.1–7.13_

  - [ ]* 8.2 Write property test for coverage-aware release decisions
    - **Property 19: Release decisions respect coverage state and preserve evidence.** Generate verification result sequences and persistence outcomes; assert post-coverage failures create failed decisions while pre-coverage failures continue without one.
    - **Validates: Requirements 7.7, 7.8, 7.10**

  - [ ]* 8.3 Write deterministic Verification_Suite schema, unit, and release-policy tests
    - Test Pack_Contract and handoff-lineage schemas, lifecycle/ALC/lesson/provider branches, failure recording, completed-coverage preservation, and administrative failure-decision authorization.
    - _Requirements: 7.1, 7.2, 7.5–7.10_

  - [ ]* 8.4 Write isolated mock-provider integration tests for shared adoption patterns
    - Add dedicated integration modules for superseded-pack reproduction, the registered VA graph/retrieval/episode/reflection/critique/approval/immutable-release path, and two non-video packs using the same contract, learning lifecycle, and UI-extension rules.
    - _Requirements: 1.11, 2.3, 6.11, 7.4_

  - [ ]* 8.5 Write deterministic load, vertical-workflow, and named security-fixture tests
    - Test the 24 concurrently registered pack proof and evidence set; add a fixed-seed initial VA vertical fixture asserting trace bundle, digests, audits, UI projections, and release decision; assert separate denial-and-audit outcomes for every required malicious fixture.
    - _Requirements: 6.12, 7.11, 7.13_

  - [ ]* 8.6 Add automated verification-evidence manifest tests
    - Implement test-only evidence-manifest generation that records the exact focused pytest, Ruff, and mypy commands; exit status; fixed seeds; artifact digests; and verification identifiers without exposing sensitive Lesson content.
    - Assert the manifest reports command failure without discarding independently persisted coverage evidence.
    - _Requirements: 5.9, 7.5, 7.6, 7.10–7.13_

- [ ] 9. Wire adoption services into the FastAPI host and validate external behavior
  - [ ] 9.1 Compose controllers, repositories, and typed outcomes into FastAPI dependencies and routes
    - Extend `backend/app/main.py` and `api/v1/` to expose Pack_Contract registration, invocation submission, governance outcomes, lifecycle/observability projections, and release/compatibility evidence through authorized, redacted responses.
    - Ensure route handlers never convert a denied, blocked, unavailable, or incomplete-evidence result into an allow.
    - _Requirements: 1.1, 1.8–1.10, 3.1–3.15, 4.1–4.11, 5.9, 7.11, 8.4, 8.5, 9.7_

  - [ ]* 9.2 Write FastAPI integration tests for fail-closed public behavior
    - Exercise registration rejection, incompatible activation/invocation, access/tool/outbound denial, incomplete external handoffs, learning preconditions, provider failure, redacted observability, and verification/release projections using fakes only.
    - _Requirements: 1.3–1.5, 3.2, 3.5, 3.7, 3.11–3.14, 4.1–4.9, 5.9, 7.11, 8.4, 8.5, 9.1–9.3_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Implementation language: **Python 3.12**, selected by the completed design and existing backend configuration; no new dependency is required because Hypothesis, pytest, Ruff, and mypy are pinned in `backend/pyproject.toml`.
- Tasks marked with `*` are optional test tasks. They must remain in the plan and may be skipped only for a deliberate MVP; core implementation tasks are not optional.
- Execute focused, non-networked evidence commands from `backend/`: `python -m pytest tests/properties -q`, targeted `python -m pytest tests/integration -q`, `python -m ruff check app tests`, and `python -m mypy app tests`. The automated manifest from Task 8.6 preserves command/result evidence.
- Requirement coverage: Tasks 1–2 cover Requirements 1–2 and 8.1–8.5/8.12; Task 3 covers Requirement 3; Task 4 covers Requirement 4; Task 5 covers Requirement 5; Task 6 covers Requirement 6, 8.6–8.7, and 9.4–9.6; Task 7 covers 8.8–8.11 and 9.1–9.10; Tasks 8–9 cover Requirement 7 and end-to-end integration/wiring. Properties 1–26 are each represented by one dedicated test sub-task.
- The plan preserves the approved scope: `va-agent-swarm` remains the VA authority; tests use only isolated fakes and authorized mock Provider_Adapters; evidence stores references and redacted projections instead of sensitive Lesson content.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "2.1"] },
    { "id": 3, "tasks": ["2.2", "2.3", "2.4", "2.5", "3.1"] },
    { "id": 4, "tasks": ["3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "4.1"] },
    { "id": 5, "tasks": ["4.2", "4.3", "4.4", "4.5", "5.1"] },
    { "id": 6, "tasks": ["5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "6.1"] },
    { "id": 7, "tasks": ["6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3", "7.4", "7.5", "7.6", "8.1"] },
    { "id": 9, "tasks": ["8.2", "8.3", "8.4", "8.5", "8.6", "9.1"] },
    { "id": 10, "tasks": ["9.2"] }
  ]
}
```
