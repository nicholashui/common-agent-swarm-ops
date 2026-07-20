# Implementation Plan: Backend Redesign

## Overview

Implement the additive Python/FastAPI control-plane façade in dependency order. Build typed, organization-scoped control-plane services around the existing `common-agent-swarm-ops` library; expose them exclusively through `/api/v1`; and use the existing pinned Hypothesis, pytest, ruff, and mypy tooling. Each property-test task uses deterministic fakes, `@settings(max_examples=100)`, and a preceding `Feature: backend-redesign, Property N` traceability comment.

## Tasks

- [ ] 1. Establish shared public-contract and durable control-plane foundations
  - [ ] 1.1 Create strict Python domain models, typed error/result values, repository protocols, transactional unit-of-work ports, and deterministic in-memory fakes for public envelopes, provenance, work/task, evidence, event/outbox, import, and deployment records.
    - Keep protected repository lookups organization-scoped and durable transition records append-only.
    - _Requirements: 3.1, 3.2, 5.2, 6.2, 7.1, 8.3, 9.1, 10.3, 12.5_
  - [ ] 1.2 Implement the shared `PublicResponse`/`PublicError` serializers, correlation propagation, redaction-safe exception mapper, and FastAPI response helpers; migrate documented `/api/v1` route errors away from framework-default bodies.
    - Preserve empty successful statuses without a body and stable typed error codes with retryability.
    - _Requirements: 1.2, 1.3, 12.5, 12.6, 13.5_
  - [ ]* 1.3 Write focused deterministic unit tests for public response/error serialization, correlation propagation, safe validation/conflict responses, and empty-success behavior.
    - Mock no external systems; include one representative successful and error envelope per documented status class.
    - _Requirements: 1.2, 1.3_

- [ ] 2. Enforce trusted request context, authorization, and idempotency before protected work
  - [ ] 2.1 Extend `api/v1/dependencies.py` with immutable server-derived trusted context, context-conflict guards, and an `AuthorizationService` invoked before every protected read, mutation, aggregate, topic, replay, artifact reference, and tool operation.
    - Make absent, foreign, hidden, and unauthorized resources indistinguishable externally and prohibit client-supplied authority fields in route schemas.
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 10.2, 10.6_
  - [ ] 2.2 Add an atomic `IdempotencyService` to the state-changing command pipeline that reserves actor/key/digest, persists a response reference before success, replays matching requests, and safely rejects changed-digest key reuse.
    - Ensure duplicate dispatch uses the same governed outcome rather than mutating the subject twice.
    - _Requirements: 2.5, 2.6, 2.7, 5.8_
  - [ ]* 2.3 Write the deterministic Hypothesis test for **Property 3: Trusted-context authorization is non-disclosing**.
    - Use tenant/visibility matrices and lookup spies to prove conflict and inaccessible paths perform no protected lookup/delivery and share one authorization outcome.
    - **Validates: Requirements 2.2, 2.3, 2.4, 10.2, 10.6**
  - [ ]* 2.4 Write the deterministic Hypothesis test for **Property 4: State-changing commands are idempotent**.
    - Generate blank keys, duplicate actor/key/digest combinations, and duplicate dispatches; assert no extra mutation and stored-response replay.
    - **Validates: Requirements 2.5, 2.6, 2.7, 5.8**
  - [ ]* 2.5 Add FastAPI integration tests for server-side identity derivation, client-authority conflicts, enumeration-safe failures, and idempotency response replay.
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.7_

- [ ] 3. Implement immutable common-contract registry management
  - [ ] 3.1 Build `RegistryService` and organization-safe repository adapters to publish complete agent/pattern snapshots, write-protect published versions, allow separately identified mutable drafts, and create migration targets for vulnerabilities.
    - Persist canonical fields, content digests, compatibility/risk/verification rules, and provenance without mutating published history.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [ ]* 3.2 Write the deterministic Hypothesis test for **Property 5: Common-contract publication preserves immutable history**.
    - Generate valid contracts, later edits, and vulnerability records; assert complete snapshot equality and distinct draft/fork/patch identities.
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8**
  - [ ]* 3.3 Add focused registry unit tests for authorized draft updates, rejected published mutations, and vulnerability migration records.
    - _Requirements: 3.3, 3.4, 3.5, 3.6_

- [ ] 4. Implement validated swarm revisions and immutable run provenance
  - [ ] 4.1 Build `GraphService` for organization-owned `Swarm_Instance` revisions, optimistic revision checks, custom-node justification, category-complete validation, version resolution, and library-compatible workflow-definition persistence.
    - Store field-safe failures and eligibility so only fully successful validation can mark a revision runnable.
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8_
  - [ ] 4.2 Extend run creation to snapshot graph revision, workflow definition, and every resolved common-version identifier before any dispatch, retaining immutable historical provenance.
    - Refuse run creation for unvalidated or failed revisions without creating a partial run.
    - _Requirements: 3.7, 3.8, 4.5, 4.7_
  - [ ]* 4.3 Write the deterministic Hypothesis test for **Property 6: Run provenance is a pre-dispatch immutable snapshot**.
    - Generate later graph/common-contract edits and verify every retained run remains equal to its original pre-dispatch snapshot.
    - **Validates: Requirements 3.7, 3.8**
  - [ ]* 4.4 Write the deterministic Hypothesis test for **Property 7: Graph revision validation gates runs and preserves concurrency**.
    - Generate custom nodes, stale expected revisions, and per-category outcomes; assert eligibility and run creation are exact.
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8**
  - [ ]* 4.5 Add focused unit tests for field-safe validation reports, custom-node origin/reason requirements, and optimistic-version conflicts.
    - _Requirements: 4.2, 4.4, 4.5, 4.8_

- [ ] 5. Add durable asynchronous work coordination and recovery
  - [ ] 5.1 Implement `CommandService` work creation and transactional work-transition persistence with organization, immutable subject, attempts, idempotency, correlation, schedule, cancellation, claim, audit, and outbox records committed before dispatch/publication.
    - Support runs, evaluations, contributions/indexing, and rollout requests through the same durable command boundary.
    - _Requirements: 5.1, 5.2, 5.3, 10.1_
  - [ ] 5.2 Add `WorkRecoveryService` claim-expiry, worker-stop, retry, cancellation, reclaim/manual/dead-letter, failure-precedence, and governed duplicate-dispatch decisions from validated deployment policy.
    - Treat validation, authorization, policy, rights/consent, schema, and non-idempotent ambiguity as non-automatic-retryable, including combined transient/terminal classifications.
    - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.8_
  - [ ]* 5.3 Write the deterministic Hypothesis test for **Property 8: Durable work transitions commit before dispatch/publication**.
    - Exercise every asynchronous work kind and transactional failure point with a transactional/outbox fake; assert the work item precedes dispatch and mutation/audit/delivery commit together or not at all.
    - **Validates: Requirements 5.1, 5.2, 5.3, 10.1**
  - [ ]* 5.4 Write the deterministic Hypothesis test for **Property 9: Work recovery is bounded and fail-closed**.
    - Generate claim expiry, cancellation, retry plans, duplicate dispatch, and combined transient/terminal classifications.
    - **Validates: Requirements 5.4, 5.5, 5.6, 5.7, 5.8**
  - [ ]* 5.5 Add focused unit tests for recovery-decision selection, cancellation-before-retry, bounded attempts, and dead-letter/manual-recovery persistence.
    - _Requirements: 5.4, 5.5, 5.6, 5.7_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement the explicit Agent_Task coordination lifecycle
  - [ ] 7.1 Build `TaskCoordinator` to prepare pinned tasks from valid graph revisions, enforce the complete lifecycle enum and optimistic task versions, queue only satisfied prerequisites, retain audit/outbox transitions, apply finite or negative-unlimited limits, and create replay lineage.
    - Preserve a later-ineligible task in `queued` state with an unclaimable execution marker; retain machine-readable failures and prohibit automatic redispatch after terminal/exhausted failure.
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_
  - [ ]* 7.2 Write the deterministic Hypothesis test for **Property 10: Task lifecycle honors pins, prerequisites, versions, and limits**.
    - Generate task graphs, expected versions, gates, finite/negative limits, retries, replays, and lost eligibility; assert exact state, transition evidence, and claimability.
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9**
  - [ ]* 7.3 Add focused unit tests for lifecycle membership, stale transition conflicts, prerequisite queueing, replay lineage, and queued-but-ineligible tasks.
    - _Requirements: 6.2, 6.3, 6.4, 6.8, 6.9_

- [ ] 8. Implement governed artifact handoffs
  - [ ] 8.1 Add `ArtifactService` and repositories for versioned opaque handoffs, required provenance/rights/quality fields, presence-only dependent validation, blocked-task field reporting, authorized redacted browser projections, and authorized reference-only downstream inputs.
    - Do not retrieve or expose protected artifact content through a public or downstream contract.
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [ ]* 8.2 Write the deterministic Hypothesis test for **Property 11: Artifact handoff is complete, blocked when incomplete, and opaque**.
    - Generate missing-field subsets and sensitive artifact sentinels; verify only required presence governs dispatch and public/downstream outputs remain redacted/reference-only.
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
  - [ ]* 8.3 Add focused artifact service tests for complete handoff acceptance, field-name persistence on blockage, and organization-safe redacted projection reads.
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [ ] 9. Implement directed critique, independent quality evidence, and approval gates
  - [ ] 9.1 Build `EvidenceService` and `GateEvaluator` for published/human-authorized critique directions; independently retained L1/L2/L3/gate evidence; server-owned pending operations; and authorization/policy re-checks before resuming effects.
    - Gate progression only when every applicable evidence category, rights/consent, provenance, and valid decision passes; otherwise retain evidence and leave the gate pending or block the affected subject.
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  - [ ]* 9.2 Write the deterministic Hypothesis test for **Property 12: Directed evidence and approvals gate progression**.
    - Generate critique relationships, category vectors, pending operations, and incomplete/unauthorized decisions; assert no aggregate-score substitution or unauthorized resumption.
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**
  - [ ]* 9.3 Add focused unit tests for directed-critique rejection, independent evidence retention, required decision value/reason, and pending-gate behavior.
    - _Requirements: 8.1, 8.2, 8.3, 8.5, 8.6_

- [ ] 10. Implement proposals and bounded rollout campaigns
  - [ ] 10.1 Build `ProposalService` and `RolloutService` for immutable proposed differences/evidence, source-version preservation, bounded target scope, start-condition checks, per-criterion outcomes, atomic rollback initiation, override denial, and independent campaign validation during another rollback.
    - Route campaign execution through the durable work boundary rather than creating a separate dispatcher.
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  - [ ]* 10.2 Write the deterministic Hypothesis test for **Property 13: Proposal and rollout progression is evidence-bound**.
    - Generate complete/incomplete evidence sets, criterion outcomes, rollback states, and separate campaigns to assert progression and override rules.
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**
  - [ ]* 10.3 Add focused rollout tests for missing start evidence, criterion-failure rollback, immutable source preservation, and a separately evaluated campaign during rollback.
    - _Requirements: 9.2, 9.4, 9.5, 9.6, 9.7_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement redacted operational events, replay, and activity projections
  - [ ] 12.1 Build `OutboxPublisher` and `ProjectionService` to publish only committed redacted events with required metadata and to return authorized projections with `as_of`, freshness, and delayed/degraded indicators.
    - Apply current trusted-context authorization and redaction to connection, topic, subject, and every event/projection payload.
    - _Requirements: 10.1, 10.2, 10.3, 10.7, 10.8, 17.2, 17.3_
  - [ ] 12.2 Add SSE replay handling that delivers the exact authorized contiguous bounded sequence immediately after an allowed cursor, otherwise records the outcome and returns `Recovery_Response` before any replay event.
    - Reject an unauthorized candidate event with the enumeration-safe authorization outcome rather than a partial replay.
    - _Requirements: 10.4, 10.5, 10.6_
  - [ ]* 12.3 Write the deterministic Hypothesis test for **Property 14: Event replay and projections are exact, authorized, and redacted**.
    - Generate event logs, cursors, policies, visibility matrices, bounded/gapped sequences, and sensitive sentinels; assert exactly-once delivery or no-event recovery/error.
    - **Validates: Requirements 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 17.2, 17.3**
  - [ ]* 12.4 Add FastAPI/SSE integration tests for stream authorization, replay framing, contiguous replay, recovery responses, and projection freshness/degraded fields.
    - _Requirements: 10.2, 10.4, 10.5, 10.6, 10.7, 17.2, 17.3_

- [ ] 13. Add secure ingress, import quarantine, and untrusted-content boundaries
  - [ ] 13.1 Implement `IngressGuard` and `ImportGuard` before handlers/storage to validate request size, media type, route/body/filter/pagination bounds, rate limits, declared/detected type, checksum, ownership, normalized names, quarantine, scans, and opaque storage references.
    - Reject invalid input before storage or downstream work; only release a quarantined import after an allowed configured scan.
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_
  - [ ] 13.2 Implement `UntrustedContentGuard` to require every configured protection, record redacted security evidence, and fail complete on prohibited authority/tool/policy/validation/privileged-instruction influence or any protection failure.
    - Ensure untrusted values cannot select a tool, bypass validation, or mutate policy/authority.
    - _Requirements: 11.8, 11.9, 11.10, 11.11, 11.12_
  - [ ]* 13.3 Write the deterministic Hypothesis test for **Property 15: Ingress and import validation precedes effects**.
    - Generate invalid request/import metadata, bounded pagination/filter values, scan outcomes, and storage spies to prove effects occur only after every prerequisite passes.
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**
  - [ ]* 13.4 Write the deterministic Hypothesis test for **Property 16: Untrusted content cannot influence authority and fails complete**.
    - Generate protection vectors, prohibited influence attempts, and security indicators; assert no continuation/mutation on any failed or prohibited case.
    - **Validates: Requirements 11.8, 11.9, 11.10, 11.11, 11.12**
  - [ ]* 13.5 Add deterministic ingress/import unit tests for rate-limit ordering, scan release, rejected storage names, opaque references, and fail-complete evidence redaction.
    - _Requirements: 11.2, 11.4, 11.5, 11.6, 11.7, 11.9, 11.12_

- [ ] 14. Implement safe configuration, health, retention, redaction, and transport controls
  - [ ] 14.1 Build `ConfigurationService` and `HealthService` to schema-validate startup domains, resolve secrets from environment then configured manager, disable only affected components safely, keep liveness dependency-free, and distinguish required/unavailable from optional/`not_configured` readiness.
    - Emit secret-free typed configuration/health failures and include required authorized health fields only when safely available.
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 13.1, 13.2, 13.3, 13.4_
  - [ ] 14.2 Add centralized redaction and retention services that exclude credentials, tokens, raw prompts, protected artifacts, prohibited tool inputs, and deployment secrets from every observability/public surface, and apply validated archival/deletion policy with required provenance preservation.
    - _Requirements: 12.6, 12.7, 12.8, 13.5_
  - [ ] 14.3 Add production transport, restrictive origin, session-appropriate security-header, and rate-limit middleware that requires HTTPS and returns the shared safe error envelope with `Retry-After`.
    - _Requirements: 13.6, 13.7, 13.8_
  - [ ]* 14.4 Write the deterministic Hypothesis test for **Property 17: Operations retain correlation, safe health, and policy-controlled data lifecycle**.
    - Generate dependency/configuration matrices, health snapshots, command records, sensitive payloads, and retention outcomes using deterministic fakes.
    - **Validates: Requirements 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8**
  - [ ]* 14.5 Write the deterministic Hypothesis test for **Property 18: Deployment configuration and transport fail safely**.
    - Generate startup configurations, production transport/origin/session combinations, and rate-limit states; assert affected-component isolation and secret-free resource-independent responses.
    - **Validates: Requirements 13.1, 13.2, 13.6, 13.7, 13.8**
  - [ ]* 14.6 Write the deterministic Hypothesis test for **Property 1: Contract envelope and safe-output invariants**.
    - Generate successful payloads, safe domain errors, sensitive deployment values, and rate-limit outcomes; assert exact envelopes, redaction, correlation, retryability, and `Retry-After` behavior.
    - **Validates: Requirements 1.2, 1.3, 12.6, 13.5, 13.8**
  - [ ]* 14.7 Add focused unit/integration tests for dependency-free liveness, readiness state matrices, safe secret resolution/failure, retention actions, production HTTPS/origin/header enforcement, and rate-limit envelopes.
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.7, 12.8, 13.3, 13.4, 13.6, 13.7, 13.8_

- [ ] 15. Implement the VA domain adapter as a canonical projection layer
  - [ ] 15.1 Add `VaDomainAdapter` routes/services that expose VA template/phase metadata only through `Public_API`, validate it against published pattern versions, block invalid production actions, map valid actions to canonical commands, and project authorized redacted canonical evidence.
    - Keep non-VA graphs on the same common graph/task/governance/provenance path without VA-only fields.
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_
  - [ ]* 15.2 Write the deterministic Hypothesis test for **Property 19: VA metadata is a validated canonical projection**.
    - Generate VA/non-VA metadata, patterns, viewers, and actions; assert validation, no invalid dispatch, common evidence preservation, and absence of VA requirements for non-VA graphs.
    - **Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6**
  - [ ]* 15.3 Add focused VA adapter tests for public-only metadata routes, invalid-pattern results, canonical command mapping, and redacted projection evidence.
    - _Requirements: 14.1, 14.3, 14.4, 14.6_

- [ ] 16. Add generated-contract lifecycle and compatibility enforcement
  - [ ] 16.1 Implement the release/build code that extracts OpenAPI from implemented `/api/v1` routes, records safe generation warnings without blocking publication, produces typed Browser_Client artifacts, evaluates semantic breaking changes, and persists replacement/deprecation/migration/compatibility and legacy-route mapping/sunset metadata.
    - Keep supported `/workflow-runs/*` routes as canonical-projection adapters and transfer retired mapping/sunset/migration metadata to the configured manual-retention handoff.
    - _Requirements: 1.4, 1.5, 1.6, 15.1, 15.2, 15.3, 15.4_
  - [ ]* 16.2 Write the deterministic Hypothesis test for **Property 2: Breaking contract lifecycle gate**.
    - Generate contract diffs and lifecycle evidence combinations; assert breaking changes are blocked exactly until every required versioned replacement, deprecation, migration, and compatibility condition is met.
    - **Validates: Requirements 1.6, 15.2**
  - [ ]* 16.3 Add integration tests that mount implemented routes for OpenAPI extraction, test safe generation failure warnings, regenerate typed artifacts from a changed document, and verify compatibility mapping/sunset handoff behavior.
    - _Requirements: 1.4, 1.5, 15.1, 15.3, 15.4_

- [ ] 17. Implement the sole governed library-delegation port
  - [ ] 17.1 Add `GovernedLibraryDelegate` and adapter integrations so every run-related create/dispatch/resume/evaluate/evolve/retrieve operation uses the corresponding existing library service with server-held identity, organization, policy, and published-version data.
    - Reject client/graph/adapter/untrusted tool IDs, credentials, URLs, executable instructions, and authority unless tool membership is conclusively present in both the published contract and organization policy; apply this uniformly to local-inline and remote adapters.
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_
  - [ ]* 17.2 Write the deterministic Hypothesis test for **Property 20: Every adapter delegates only allowlisted governed operations**.
    - Use spy library delegates and generated adapter kinds, allowlists, membership outcomes, and prohibited values to prove one governed path and deny indeterminate membership.
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6**
  - [ ]* 17.3 Add focused delegate/adapter tests for server-held context forwarding, allowed/absent/indeterminate tool membership, and local-inline contract preservation.
    - _Requirements: 16.2, 16.3, 16.4, 16.5, 16.6_

- [ ] 18. Implement traceable operational alerting
  - [ ] 18.1 Add `AlertService` evaluation and persistence for configured readiness, queue-age, terminal run-failure-rate, replay-gap, outbox-lag, approval-expiry, and rollback conditions; attach a safe correlation identifier or subject reference.
    - Feed delayed/degraded dashboard state through the projection service without overwriting the underlying data freshness state.
    - _Requirements: 17.1, 17.2, 17.3_
  - [ ]* 18.2 Write the deterministic Hypothesis test for **Property 21: Configured degradation creates traceable safe alerts**.
    - Generate each configured condition with correlation/subject combinations and sensitive sentinel values; assert one redacted persisted alert with the proper trace reference.
    - **Validates: Requirements 17.1**
  - [ ]* 18.3 Add focused alert/projection tests for every trigger kind and for delayed delivery with current underlying freshness.
    - _Requirements: 17.1, 17.2, 17.3_

- [ ] 19. Wire all control-plane components into the versioned FastAPI application
  - [ ] 19.1 Compose configuration, trusted-context middleware, guards, repositories, transactional outbox, services, library delegate, routers, SSE endpoint, and compatibility adapters in `app/main.py` and `api/v1/router.py` so browser routes exist only under `/api/v1`.
    - Ensure all state-changing routes use the common authorization/idempotency/work/audit/outbox pipeline and all read routes use authorized redacted projections.
    - _Requirements: 1.1, 2.1, 2.3, 5.1, 10.1, 14.1, 16.1_
  - [ ]* 19.2 Add final isolated FastAPI integration and smoke tests for mounted public-only routes, composed command/query pipelines, generated OpenAPI artifacts, SSE headers, and component activation after configuration validation.
    - Use fakes or deployment-selected isolated adapters only; do not require external network services.
    - _Requirements: 1.1, 1.4, 2.1, 5.1, 10.2, 13.1, 14.1, 15.1, 16.1_

- [ ] 20. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for a narrower implementation increment; every non-test task is required.
- Keep every property test in `backend/tests/properties/` with one numbered property per test module, deterministic clocks/fakes, exact design traceability comment, and `@settings(max_examples=100)`.
- Keep deterministic unit/integration tests isolated from external identity providers, queues, secret managers, storage, and tool adapters. Validate implemented increments from `backend` with focused `python -m pytest -q` subsets, `ruff check app tests`, and `mypy app tests`.
- The plan intentionally adds no execution engine, no client-derived authority path, and no new test framework; all governed execution remains delegated to existing common-agent-swarm-ops services.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "2.1", "3.1", "14.1"] },
    { "id": 2, "tasks": ["2.2", "4.1", "8.1", "9.1", "13.1", "14.2", "16.1"] },
    { "id": 3, "tasks": ["3.2", "3.3", "4.2", "5.1", "8.2", "9.2", "10.1", "13.2", "14.3", "15.1", "17.1"] },
    { "id": 4, "tasks": ["2.3", "2.4", "2.5", "4.3", "4.4", "4.5", "5.2", "7.1", "8.3", "9.3", "10.2", "12.1", "13.3", "13.4", "15.2", "16.2", "17.2"] },
    { "id": 5, "tasks": ["5.3", "5.4", "5.5", "7.2", "7.3", "10.3", "12.2", "12.3", "12.4", "13.5", "14.4", "14.5", "14.6", "14.7", "15.3", "16.3", "17.3", "18.1"] },
    { "id": 6, "tasks": ["18.2", "18.3", "19.1"] },
    { "id": 7, "tasks": ["19.2"] }
  ]
}
```
