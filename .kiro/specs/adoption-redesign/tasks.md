# Implementation Plan: Adoption Redesign

## Overview

Implement the approved domain-neutral Adoption_Platform in the existing Python 3.12/FastAPI backend. Work proceeds from shared contracts and persistence through fail-closed domain services, verification evidence, and final API composition. Domain_Packs remain declarative and immutable, `va-agent-swarm` remains the canonical VA owner, and automated tests use isolated repositories plus authorized mock Provider_Adapters. Each Hypothesis property test uses `@settings(max_examples=100, deadline=None)`, bounded strategies, deterministic fakes, and the comment `Feature: adoption-redesign, Property N: <property title>`.

## Tasks

- [x] 1. Establish shared contracts and durable evidence foundations
  - [x] 1.1 Add versioned declarations, identifiers, and typed command outcomes
    - Extend `backend/app/models/contracts.py`, `identifiers.py`, and `common.py` with independently versioned Host_Contract, Pack_Contract, ALC, Domain_Pack, compatibility-range, and correlation-aware identifier models.
    - Define exhaustive `Allowed`, `Denied`, `Blocked`, and `FailedRecoverable` outcomes so callers cannot interpret missing evidence or unavailable dependencies as authorization.
    - _Requirements: 1.1, 1.2, 8.1_

  - [x] 1.2 Add immutable registration, execution, learning, release, recovery, and maturity models
    - Extend `backend/app/models/control_plane.py`, `evidence.py`, and `runs.py` with registration, invocation association, authorization, Artifact_Handoff, lifecycle, Retrieval_Record, Learning_Episode, Lesson, proposal, migration, verification, recovery, and per-agent Maturity_State records.
    - Enforce reference-only evidence, correlation metadata, immutable-version identity, one terminal episode per attempt, and distinct cataloged/registered/active/production-proven states in model validation.
    - _Requirements: 1.7, 1.8, 1.11, 3.9, 4.7, 4.10, 5.9, 6.1, 7.12, 9.7_

  - [x] 1.3 Add repository protocols, persistence constraints, and deterministic fakes
    - Extend `backend/app/repositories/protocols.py` and focused repository modules; add `backend/migrations/0003_adoption_control_plane.sql` for pack-version uniqueness, terminal-episode uniqueness, immutable evidence, and terminal release-decision constraints.
    - Add deterministic repositories and mock Provider_Adapters under `backend/tests/fakes/`; expose configurable persistence and audit failures without external services or production storage.
    - _Requirements: 1.7, 1.11, 3.9, 4.7, 4.10, 5.4–5.6, 6.10, 7.5, 7.6, 9.4–9.6_

  - [x] 1.4 Write deterministic contract and persistence tests
    - Add `backend/tests/unit/test_adoption_evidence_foundations.py` for schema validation, immutability, uniqueness, reference-only storage, correlation propagation, and independently configurable audit-write failures.
    - _Requirements: 1.5–1.7, 1.10, 2.5, 2.6, 3.3, 3.4, 4.9–4.11, 5.4–5.6, 7.5, 7.6, 9.2_

- [x] 2. Implement pack admission, VA preservation, and compatibility controls
  - [x] 2.1 Implement complete Pack_Contract admission and VA declaration validation
    - Add `backend/app/registry/admission.py` and integrate it with `pack_validator.py` and `pack_repository.py`; validate all required manifest fields, digest, signer, evaluation references, declarative-only content, and applicable Registration_Policies before persisting a decision.
    - Store only validated VA asset references and digests, reject executable VA package code during validation with best-effort audit, preserve an already-succeeded registration when code is detected later, and retain superseded versions plus reproduction contract references.
    - _Requirements: 1.2–1.7, 1.11, 2.1–2.7_

  - [x] 2.2 Implement compatibility evaluation and activation/invocation guards
    - Add `backend/app/registry/compatibility.py`; record compatible only when declared ranges intersect supported Host_Contract and ALC ranges, and expose guards that deny activation and every invocation submission while incompatible.
    - Record designated supported combinations for the Verification_Suite and require Pack_Contract validity plus evaluation references before a new domain can become activation-eligible.
    - _Requirements: 7.12, 8.1–8.5, 8.12_

  - [x] 2.3 Write property test for complete, fail-closed admission
    - Add `backend/tests/properties/test_adoption_redesign_property_01_admission.py`.
    - **Property 1: Admission is a complete, fail-closed decision.** Generate contract and policy vectors; assert approval and record preservation if and only if all required checks pass.
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.7**

  - [x] 2.4 Write property test for VA declarative, reference-only safety
    - Add `backend/tests/properties/test_adoption_redesign_property_03_va_safety.py`.
    - **Property 3: VA packages retain declarative, reference-only safety.** Generate VA assets, executable-code signals, and metadata extensions; assert rejection/reference-only registration/schema-gated acceptance.
    - **Validates: Requirements 2.2, 2.4, 2.8, 2.9**

  - [x] 2.5 Write property test for intersection-based compatibility guards
    - Add `backend/tests/properties/test_adoption_redesign_property_20_compatibility.py`.
    - **Property 20: Compatibility is intersection-based and blocks use when incompatible.** Generate independent version ranges; assert status recording, activation/invocation denial, and compatibility-matrix evidence.
    - **Validates: Requirements 7.12, 8.2, 8.3, 8.4, 8.5**

  - [x] 2.6 Write property test for new-domain onboarding evidence
    - Add `backend/tests/properties/test_adoption_redesign_property_23_onboarding.py`.
    - **Property 23: Domain onboarding requires admission evidence.** Generate onboarding declarations; assert activation eligibility only for Pack_Contract-valid packs with declared evaluation references.
    - **Validates: Requirements 8.12**

  - [x] 2.7 Write deterministic admission, audit, and VA ownership tests
    - Add `backend/tests/unit/registry/test_adoption_admission.py` for the shared Pack_Contract, canonical VA ownership, policy/executable-code rejection audits and audit failures, late code detection, superseded-version reproduction, and new-domain eligibility.
    - _Requirements: 1.1, 1.5, 1.6, 1.11, 2.1, 2.3, 2.5–2.7, 8.12_

- [x] 3. Enforce governed invocation, access, and Artifact_Handoff execution
  - [x] 3.1 Implement invocation association and declared workflow-policy barriers
    - Extend `backend/app/runs/service.py` and `backend/app/workflows/` so the complete invocation association persists before node start and compatibility is checked before submission.
    - Enforce budget, rollback, approval, memory-read, and memory-write policies at every action boundary; return typed denial/block outcomes and emit the required association-failure audit.
    - _Requirements: 1.8–1.10, 3.15, 8.4, 8.5_

  - [x] 3.2 Implement data, tool, and outbound authorization
    - Extend `backend/app/governance/authorization.py` and `tool_broker.py` to evaluate organization, domain, supported pack range, agent, memory scope, declared tool IDs, and declared outbound destinations before access or dispatch.
    - Keep denials effective when a requirement explicitly permits the corresponding Audit_Record write to fail.
    - _Requirements: 3.1–3.8_

  - [x] 3.3 Implement immutable Artifact_Handoff lineage and availability barriers
    - Extend `backend/app/repositories/artifact_repository.py` and add `backend/app/artifacts/handoff_service.py`; validate complete metadata and acyclic lineage before persistence.
    - Make internal handoffs available only at completed creation, keep external handoffs unavailable until persistence confirmation, revoke premature availability with audit, and enforce the registered VA metadata-extension schema before acceptance.
    - _Requirements: 2.8–2.10, 3.9–3.14, 7.1, 7.3_

  - [x] 3.4 Write property test for invocation association as an execution barrier
    - Add `backend/tests/properties/test_adoption_redesign_property_02_invocation_barrier.py`.
    - **Property 2: Invocation association is an execution barrier.** Generate association writes and failures; assert no agent node starts before successful persistence.
    - **Validates: Requirements 1.8, 1.9**

  - [x] 3.5 Write property test for complete-scope data access
    - Add `backend/tests/properties/test_adoption_redesign_property_04_data_scope.py`.
    - **Property 4: Data access remains within every declared scope.** Mutate approved scopes across organization, domain, pack range, agent, and memory scope; assert every boundary escape is denied.
    - **Validates: Requirements 3.1, 3.2, 7.3**

  - [x] 3.6 Write property test for undeclared capability containment
    - Add `backend/tests/properties/test_adoption_redesign_property_05_capability_governance.py`.
    - **Property 5: Undeclared capabilities cannot escape governance.** Generate tool and destination allow-lists; assert absent identifiers and destinations are denied.
    - **Validates: Requirements 3.5, 3.7**

  - [x] 3.7 Write property test for handoff evidence and availability
    - Add `backend/tests/properties/test_adoption_redesign_property_06_handoff_availability.py`.
    - **Property 6: Artifact availability follows complete, acyclic evidence.** Generate bounded lineages, metadata, and persistence events; assert metadata completeness, DAG enforcement, availability barriers, and revocation.
    - **Validates: Requirements 3.9, 3.10, 3.11, 3.12, 3.13, 7.1, 7.3**

  - [x] 3.8 Write property test for declared workflow-policy enforcement
    - Add `backend/tests/properties/test_adoption_redesign_property_07_workflow_policy.py`.
    - **Property 7: Declared workflow policies are enforced at every action.** Generate policy-breaching actions; assert they cannot complete as authorized and declared rollback behavior executes where applicable.
    - **Validates: Requirements 3.15**

  - [x] 3.9 Write deterministic governance and handoff resilience tests
    - Add `backend/tests/unit/governance/test_adoption_execution.py` for denial Audit_Record shapes, allowed audit-write failure paths, association denial, VA extension rejection, external-handoff revocation, and cyclic-lineage rejection.
    - _Requirements: 1.10, 2.8–2.10, 3.3, 3.4, 3.6, 3.8, 3.14_

- [x] 4. Implement the learning-agent lifecycle and execution evidence
  - [x] 4.1 Implement ALC activation, retrieval, and terminal-episode services
    - Add `backend/app/memory/learning_lifecycle.py` and integrate it through repository protocols; require exactly one effective agent-named ALC and all activation evidence, and suspend active agents before lifecycle-affecting changes.
    - Persist exactly one Retrieval_Record, including empty results, before every learning-required action; block on retrieval-write failure; persist exactly one immutable terminal Learning_Episode or mark the attempt blocked for recovery.
    - _Requirements: 4.1–4.11_

  - [x] 4.2 Write property test for atomic, evidence-complete activation
    - Add `backend/tests/properties/test_adoption_redesign_property_08_learning_activation.py`.
    - **Property 8: Learning-agent activation is atomic and evidence-complete.** Generate ALC sets, lifecycle states, changes, and evidence vectors; assert active status only when every condition passes.
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 7.3**

  - [x] 4.3 Write property test for pre-action retrieval evidence
    - Add `backend/tests/properties/test_adoption_redesign_property_09_retrieval_barrier.py`.
    - **Property 9: Retrieval evidence precedes learning-required execution.** Generate empty/non-empty retrievals and persistence failures; assert one record precedes execution or the action blocks.
    - **Validates: Requirements 4.7, 4.8**

  - [x] 4.4 Write property test for immutable terminal learning episodes
    - Add `backend/tests/properties/test_adoption_redesign_property_10_terminal_episode.py`.
    - **Property 10: Terminal learning outcomes are immutable and recoverable.** Generate repeated terminal notifications and write failures; assert one episode or recovery-blocked status.
    - **Validates: Requirements 4.10, 4.11**

  - [x] 4.5 Write deterministic lifecycle and recovery-edge tests
    - Add `backend/tests/unit/memory/test_adoption_learning_lifecycle.py` for zero/multiple ALCs, suspend-before-change ordering, all terminal outcomes, retrieval block/audit behavior, and idempotent recovery retries.
    - _Requirements: 4.1, 4.4, 4.7–4.11_

- [x] 5. Implement Lesson governance, provenance, observability, and improvement promotion
  - [x] 5.1 Implement Lesson assessment, revocation, provenance, and redacted observability
    - Add `backend/app/memory/lesson_service.py`; assess every required criterion, enforce organization/domain/pack-range/agent/memory scope, and exclude a revoked Lesson only after its revocation Audit_Record commits.
    - Link outputs to available Retrieval_Records and source Learning_Episodes without inventing retrieval links; expose exact per-agent counts without Lesson content.
    - _Requirements: 5.1–5.9_

  - [x] 5.2 Implement sandboxed Improvement_Proposal and governed promotion
    - Extend `backend/app/evolution/service.py` with evidence-first proposal creation, sandbox transition failure retention, denial of unapproved live changes, designated-reviewer decisions, immutable replacement/promoted versions, rollback references, and promotion audits.
    - _Requirements: 5.10–5.14_

  - [x] 5.3 Write property test for Lesson assessment and scoped retrieval
    - Add `backend/tests/properties/test_adoption_redesign_property_11_lesson_assessment.py`.
    - **Property 11: Lesson assessment and retrieval enforce complete scope.** Generate criteria and scope vectors; assert retrieval only after all assessments pass and every scope dimension matches.
    - **Validates: Requirements 5.1, 5.2, 5.3**

  - [x] 5.4 Write property test for audit-gated Lesson revocation
    - Add `backend/tests/properties/test_adoption_redesign_property_12_lesson_revocation.py`.
    - **Property 12: Revocation changes retrieval only after auditable commitment.** Generate revocation persistence outcomes; assert retrieval eligibility changes only after audit commitment.
    - **Validates: Requirements 5.5, 5.6**

  - [x] 5.5 Write property test for non-invented output provenance
    - Add `backend/tests/properties/test_adoption_redesign_property_13_output_provenance.py`.
    - **Property 13: Output provenance is complete without inventing retrieval.** Generate outputs with and without Retrieval_Records; assert complete source-episode links and no fabricated retrieval reference.
    - **Validates: Requirements 5.7, 5.8**

  - [x] 5.6 Write property test for redacted learning observability
    - Add `backend/tests/properties/test_adoption_redesign_property_14_learning_observability.py`.
    - **Property 14: Learning observability preserves counts while redacting content.** Generate mixed evidence sets; assert exact required counts and absence of sensitive Lesson content.
    - **Validates: Requirements 5.9**

  - [x] 5.7 Write property test for sandboxed improvement promotion
    - Add `backend/tests/properties/test_adoption_redesign_property_15_improvement_promotion.py`.
    - **Property 15: Improvement remains sandboxed until governed promotion.** Generate failure evidence, transitions, and approvals; assert evidence-first proposals, denied unapproved changes, retained failures, and rollback provenance.
    - **Validates: Requirements 5.10, 5.11, 5.12, 5.14, 7.3**

  - [x] 5.8 Write deterministic Lesson and reviewer-decision tests
    - Add `backend/tests/unit/memory/test_adoption_lessons_and_improvements.py` for revocation Audit_Record payloads, audit failure behavior, reviewer identity/timestamp/evidence/promotion state, and every prohibited live-change target.
    - _Requirements: 5.4–5.6, 5.12, 5.13, 5.14_

- [x] 6. Implement migration, activation eligibility, rollback, and recovery
  - [x] 6.1 Implement migration phases, VA inventory, and activation eligibility
    - Extend `backend/app/engines/migration.py`, `backend/app/evaluation/migration_evidence.py`, and `backend/app/video/inventory.py`; persist phase scope/evidence/exit/rollback/reviews, validate every Source_Index disposition, and require exactly one mapping for each of 114 indexed VA agents.
    - Mark workflows Activation_Eligible only after every declared evidence item passes and prevent active transition until both eligibility and explicit activation approval exist.
    - _Requirements: 6.1–6.7_

  - [x] 6.2 Implement migration rollback, contract-change approval, and Recovery_Action services
    - Add `backend/app/engines/recovery.py`; restore only approved designated immutable versions, apply ALC Lesson retention, and retain migration rollback evidence.
    - Require complete contract-breaking change evidence, and halt Recovery_Action restoration unless prior-version investigation evidence persists; make completed restoration retries idempotent.
    - _Requirements: 6.8–6.10, 8.6, 8.7, 9.4–9.6_

  - [x] 6.3 Write property test for complete frozen VA inventory and roster evidence
    - Add `backend/tests/properties/test_adoption_redesign_property_16_va_inventory.py`.
    - **Property 16: Frozen VA inventory and roster evidence are complete.** Generate inventories and mappings; assert all asset fields/dispositions and one mapping for each of 114 agents.
    - **Validates: Requirements 6.2, 6.3, 6.4**

  - [x] 6.4 Write property test for VA activation evidence and approval
    - Add `backend/tests/properties/test_adoption_redesign_property_17_va_activation.py`.
    - **Property 17: VA activation eligibility cannot bypass evidence or approval.** Generate evidence and approval states; assert eligibility exactly on complete evidence and no active transition without explicit approval.
    - **Validates: Requirements 6.5, 6.6, 6.7**

  - [x] 6.5 Write property test for rollback target and retention behavior
    - Add `backend/tests/properties/test_adoption_redesign_property_18_migration_rollback.py`.
    - **Property 18: Approved rollback restores the designated version and retention outcome.** Generate targets and affected Lessons; assert exact restoration and ALC-selected retention for each Lesson.
    - **Validates: Requirements 6.8, 6.9**

  - [x] 6.6 Write property test for contract-breaking change evidence
    - Add `backend/tests/properties/test_adoption_redesign_property_21_contract_change.py`.
    - **Property 21: Contract-breaking approval requires complete evidence.** Generate complete and incomplete records; assert approval if and only if every required artifact exists.
    - **Validates: Requirements 8.6, 8.7**

  - [x] 6.7 Write property test for evidence-gated, target-exact recovery
    - Add `backend/tests/properties/test_adoption_redesign_property_25_recovery.py`.
    - **Property 25: Recovery is evidence-gated and target-exact.** Generate approved actions and persistence outcomes; assert no restoration before evidence and exact target restoration after it.
    - **Validates: Requirements 9.4, 9.5, 9.6**

  - [x] 6.8 Write deterministic migration and recovery tests
    - Add `backend/tests/unit/engines/test_adoption_migration_recovery.py` for phase-record fields, host/VA reviews, pending approvals, rollback evidence retention, failed evidence persistence, and idempotent completed Recovery_Actions.
    - _Requirements: 6.1, 6.6–6.10, 8.6, 8.7, 9.4–9.6_

- [x] 7. Implement provider governance and operational containment
  - [x] 7.1 Implement Provider_Adapter authorization and fail-closed execution
    - Extend `backend/app/governance/adapter_execution.py` and `operation_guard.py`; authorize only complete capability/cost/retention/residency/safety declarations and deny missing declarations, timeouts, unsafe results, budget excess, or unavailability.
    - Preserve denial when audit persistence fails and expose only authorized mock Provider_Adapters to verification workflows.
    - _Requirements: 8.8–8.11, 9.1, 9.2_

  - [x] 7.2 Implement video release gates, independent maturity, and capacity actions
    - Add `backend/app/governance/operational_containment.py`; block video release when any mandatory handoff gate is absent, report four distinct Maturity_State values, retain per-agent maturity during pack disablement, and apply the declared throttle-or-disable action with audit.
    - _Requirements: 9.3, 9.7–9.10_

  - [x] 7.3 Write property test for provider authorization and faults
    - Add `backend/tests/properties/test_adoption_redesign_property_22_provider_governance.py`.
    - **Property 22: Provider authorization and failures fail closed.** Generate declarations and provider outcomes; assert authorization only with all fields and denial for every required fault.
    - **Validates: Requirements 8.8, 8.9, 9.1**

  - [x] 7.4 Write property test for mandatory video release gates
    - Add `backend/tests/properties/test_adoption_redesign_property_24_video_release.py`.
    - **Property 24: Video releases fail closed on every mandatory gate.** Generate gate sets; assert omission of any required gate returns a blocked Release_Readiness_Decision.
    - **Validates: Requirements 9.3**

  - [x] 7.5 Write property test for capacity containment and independent maturity
    - Add `backend/tests/properties/test_adoption_redesign_property_26_operational_containment.py`.
    - **Property 26: Operational containment preserves independent maturity evidence.** Generate limits, actions, failures, and maturity states; assert exact containment and unchanged per-agent maturity.
    - **Validates: Requirements 9.8, 9.9**

  - [x] 7.6 Write deterministic provider and operational-audit tests
    - Add `backend/tests/unit/governance/test_adoption_provider_containment.py` for provider-denial audits and audit failures, authorized mocks, distinct maturity states, capacity-action audits, and each video gate.
    - _Requirements: 8.10, 8.11, 9.1–9.3, 9.7–9.10_

- [x] 8. Build Verification_Suite evidence and automated integration coverage
  - [x] 8.1 Implement Verification_Suite orchestration and immutable release evidence
    - Add `backend/app/evaluation/verification_suite.py` and `backend/app/evidence/release_evidence.py`; record schema/unit/property/integration outcomes, coverage state, fixed seeds, fixture digests, compatibility results, audits, UI projections, failure records, and terminal release decisions.
    - Continue remaining checks when failure-record persistence fails, preserve completed integration coverage, distinguish pre/post-coverage failure semantics, and support Release_Policy-authorized administrative failure decisions.
    - _Requirements: 7.1–7.12_

  - [x] 8.2 Write property test for coverage-aware release decisions
    - Add `backend/tests/properties/test_adoption_redesign_property_19_release_decisions.py`.
    - **Property 19: Release decisions respect coverage state and preserve evidence.** Generate result sequences and persistence outcomes; assert post-coverage failures create failed decisions while pre-coverage failures continue without one.
    - **Validates: Requirements 7.7, 7.8, 7.10**

  - [x] 8.3 Write deterministic Verification_Suite schema, unit, and policy tests
    - Add `backend/tests/unit/evaluation/test_adoption_verification_suite.py` for Pack_Contract and handoff schemas, lifecycle/ALC/Lesson/provider branches, failure persistence resilience, coverage preservation, and administrative failure authorization.
    - _Requirements: 7.1, 7.2, 7.5–7.10_

  - [x] 8.4 Write mock-provider integration tests for shared adoption patterns
    - Add `backend/tests/integration/test_adoption_shared_patterns.py`; cover superseded-pack reproduction, the VA graph/retrieval/episode/reflection/critique/approval/immutable-release path, and at least two non-video packs using the same registration, learning, and UI-extension contracts.
    - _Requirements: 1.11, 2.3, 6.11, 7.4, 8.11_

  - [x] 8.5 Write load, initial-vertical, and named security-fixture tests
    - Add `backend/tests/integration/test_adoption_release_evidence.py`; verify evidence for 24 concurrently registered packs, fixed-seed initial VA trace/digests/audits/UI/release output, and a separate denial-and-audit result for each required malicious fixture.
    - _Requirements: 6.12, 7.11, 7.13_

  - [x] 8.6 Write automated verification-evidence manifest tests
    - Add `backend/tests/evidence/test_adoption_verification_manifest.py` and test-only manifest generation for exact focused pytest, Ruff, and mypy commands, exit statuses, fixed seeds, artifact digests, and verification IDs.
    - Assert command failures are recorded without exposing Lesson content or discarding independently persisted coverage evidence.
    - _Requirements: 5.9, 7.5, 7.6, 7.10–7.13_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Wire adoption services into the FastAPI host
  - [x] 10.1 Compose repositories, controllers, and typed outcomes into authorized routes
    - Extend `backend/app/api/v1/` and `backend/app/main.py` to expose pack registration, invocation submission, governance decisions, lifecycle operations, redacted observability, compatibility evidence, and release evidence.
    - Inject all services through FastAPI dependencies; preserve correlation identifiers and ensure route handlers never convert denied, blocked, failed-recoverable, unavailable, or incomplete-evidence outcomes into an allow.
    - _Requirements: 1.1, 1.8–1.10, 3.1–3.15, 4.1–4.11, 5.9, 7.11, 8.4, 8.5, 9.7_

  - [x] 10.2 Write FastAPI integration tests for fail-closed public behavior
    - Add `backend/tests/integration/test_adoption_api.py`; exercise registration rejection, incompatible activation/invocation, access/tool/outbound denial, handoff barriers, learning preconditions, provider failure, redacted observability, and release projections using fakes only.
    - _Requirements: 1.3–1.5, 3.2, 3.5, 3.7, 3.11–3.14, 4.1–4.9, 5.9, 7.11, 8.4, 8.5, 9.1–9.3_

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Implementation language: **Python 3.12**, selected by the completed design and existing backend. Existing pinned pytest, Hypothesis, Ruff, and mypy dependencies are sufficient; no dependency installation is part of this plan.
- Tasks marked with `*` are optional automated-test tasks and may be skipped for a deliberate MVP. Core implementation and wiring tasks are never optional.
- Property tests are one task and one file per design property. Unit, property, and integration tests are complementary evidence, not substitutes for requirement review.
- Use non-networked, quiet validation from `backend/`: `python -m pytest --tb=short -q`, `python -m ruff check app tests`, and `python -m mypy app tests`; the focused command/result set is captured by Task 8.6.
- The plan preserves canonical VA ownership, shared domain-neutral contracts, isolated fakes, authorized mock Provider_Adapters, reference-only evidence, and redacted projections.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3"] },
    { "id": 3, "tasks": ["1.4", "2.1", "2.2", "3.2", "3.3", "4.1", "7.1"] },
    { "id": 4, "tasks": ["2.3", "2.4", "2.5", "2.6", "2.7", "3.1", "3.5", "3.6", "3.7", "4.2", "4.3", "4.4", "4.5", "5.1", "6.1", "7.2"] },
    { "id": 5, "tasks": ["3.4", "3.8", "3.9", "5.2", "5.3", "5.4", "5.5", "5.6", "6.2", "6.3", "6.4", "7.3", "7.4", "7.5", "7.6"] },
    { "id": 6, "tasks": ["5.7", "5.8", "6.5", "6.6", "6.7", "6.8", "8.1"] },
    { "id": 7, "tasks": ["8.2", "8.3", "8.4", "8.5", "8.6"] },
    { "id": 8, "tasks": ["10.1"] },
    { "id": 9, "tasks": ["10.2"] }
  ]
}
```
