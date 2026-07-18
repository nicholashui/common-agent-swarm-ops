# Implementation Plan: Generic Swarm Business OS

## Overview

This canonical task plan preserves the approved deterministic, target-local scope in `C:\Project\common-agent-swarm-ops`. `structure.md` remains the architecture/product-bar authority, `requirements.md` remains the acceptance baseline, and `design.md` defines implementation and Properties 1–22. Do not access, execute, modify, copy, or adopt material outside the Target Workspace. Do not add live SaaS/media dependencies, network access, deployment/provisioning, automatic promotion, production mutation, production-canary activation, or video-artifact release.

## Tasks

- [x] 1. Restore the strict deterministic target-local quality baseline
  - [x] 1.1 Repair and rerun Hypothesis **Property 1: Architecture decisions declare their authority**.
    - In `backend/tests/properties/test_property_01_authority.py`, add the exact Feature/Property source comment, generate non-blank bounded title/rationale text, and retain focused whitespace-only rejection examples.
    - **Validates: Requirements 1.1.**
  - [x] 1.2 Correct the bounded GraphEngine budget execution path exercised by Property 10.
    - Reconcile `backend/app/engines/graph.py`, `compiler.py`, and `backend/tests/properties/test_property_10_graph_budget.py` so each generated definition is valid, reaches its designated first breach, records the correct pre-breach metrics/effects, and schedules no post-breach work. Keep all execution local and Host-brokered.
    - _Requirements: 4.3–4.5, 10.1–10.2_
  - [x] 1.3 Repair and rerun Hypothesis **Property 10: Graph budget enforcement stops at the first breached limit**.
    - Retain at least 100 bounded node/handoff/tool/wall-clock cases, explicit first-breach examples, and strict `Literal`/mapping types.
    - **Validates: Requirements 4.5.**
  - [x] 1.4 Repair and rerun Hypothesis **Property 14: Approval gates retain submissions and reauthorize effects**.
    - Replace the invalid identity check in `backend/tests/properties/test_property_14_approvals.py` with a type-safe membership/equality assertion; retain reason-length boundaries, invalid values, denials, and changed-authorization cases.
    - **Validates: Requirements 5.6–5.11.**
  - [x] 1.5 Resolve every current Ruff and mypy finding without weakening strict settings.
    - Repair the current engine protocol variance/import issues; source comments, formatting, and types in Properties 3, 10, 14, 19, and 20; and all reported compiler, graph, Product-Bar, inventory, and unit-test diagnostics. Preserve existing public behavior and bounded Hypothesis settings.
    - _Requirements: 1.1, 2.2–2.7, 4.1–4.5, 5.6–5.11, 8.6–8.7, 9.1_
  - Completion evidence: run `npm run sdd:check` from the workspace root, then `python -m pytest --tb=short -q`, `python -m ruff check app tests`, and `python -m mypy app tests` from `backend/`. All must exit 0 before replacing the stale target-local quality-evidence record with commands, exit statuses, timestamps, hashes, and resolved counterexamples.

- [ ] 2. Preserve and fully validate implemented Host foundations
  - [x] 2.1 Retain target-boundary enforcement, architecture-decision rendering, and the existing Hypothesis **Property 2: Workspace and adoption authorization is fail-closed** coverage.
    - Keep source access, writes, execution, and adoption fail-closed and mutation-free outside the Target Workspace.
    - **Property 2. Validates: Requirements 1.2–1.5.**
  - [x] 2.2 Retain atomic domain-pack registration/activation and existing Hypothesis Properties 3 and 4.
    - Preserve canonical identifiers, 1–100-agent validation, inactive invalid outcomes, draft-production denial, and all-or-nothing Agent Learning Contract activation.
    - **Properties 3–4. Validates: Requirements 2.2–2.7.**
  - [x] 2.3 Retain process-artifact traceability and high-impact memory write controls with existing Hypothesis Properties 5 and 6.
    - Preserve permitted log provenance, scope restrictions, primary/alternate audit behavior, and the durable audit-unavailable latch.
    - **Properties 5–6. Validates: Requirements 3.1–3.5.**
  - [x] 2.4 Retain queued-before-dispatch persistence, bounded LegacyEngine behavior, failure processing, and existing Hypothesis Properties 8, 9, and 12.
    - Preserve terminal evidence/effect retention, stopped unstarted work, and no ambiguous-effect replay.
    - **Properties 8–9 and 12. Validates: Requirements 4.1–4.4, 4.9, 6.1–6.3.**
  - [x] 2.5 Retain fail-closed broker, approval lifecycle, operation guard, and existing Hypothesis Properties 13 and 22.
    - Preserve independent authorization evaluation, audit-unavailable denial, pre-effect approvals, and atomic prohibited-operation blocking.
    - **Properties 13 and 22. Validates: Requirements 5.1–5.5, 10.3–10.6.**
  - [x] 2.6 Retain deterministic evaluation/Product-Bar record services and existing Hypothesis Properties 18 and 19.
    - Preserve ≥20 golden tasks, separate repeat result identities, current-blocker semantics, independent E1–E9 entries, and E1-missing incompleteness.
    - **Properties 18–19. Validates: Requirements 8.1–8.8.**
  - [x] 2.7 Retain 114 data-only Video_Pack agent records, inventory validation, and existing Hypothesis **Property 20: Video inventory is an exact agent-to-entry bijection**.
    - Keep the pack configuration-only and non-active; no external source material, execution loop, or direct adapter access is permitted.
    - **Validates: Requirements 2.1–2.4, 9.1.**

- [ ] 3. Complete scoped semantic retrieval and its target-local control-plane integration
  - [x] 3.1 Implement semantic-first retrieval and a versioned memory route.
    - Add `backend/app/memory/retrieval.py` with deterministic local Tier-0 semantic retrieval, permitted Tier-1 relationship retrieval, and configured Tier-2 synthesis seams. Filter requester scope before every tier, return provenance for every permitted result, and return no knowledge rather than widening scope after an in-scope miss. Add only the required `/api/v1/*` memory schema/route wiring.
    - _Requirements: 3.6–3.7, 6.5–6.6, 10.1_
  - [-] 3.2 Write Hypothesis **Property 7: Retrieval is semantic-first and cannot disclose across scope**.
    - Create `backend/tests/properties/test_property_07_retrieval.py` with at least 100 bounded scoped-corpus/query cases and deterministic local tier fakes; assert ordering, provenance, no-result behavior, and cross-scope non-disclosure.
    - **Validates: Requirements 3.6–3.7.**
  - [x] 3.3 Add focused memory/API tests for audit-outage recovery, empty results, authenticated scope filtering, response redaction, and target-root confinement.
    - Extend `backend/tests/unit/memory/` and target-local API tests only; do not use a live index, network service, or out-of-workspace fixture.
    - _Requirements: 3.1–3.7, 6.5–6.6, 10.1–10.2_

- [ ] 4. Validate the current versioned Host control plane and strict TypeScript operator shell
  - [x] 4.1 Retain existing `/api/v1/*` route composition, authenticated request-context derivation, redacted projections, action previews, and strict TypeScript/Next.js shell source.
    - The operator shell consumes the Host control plane only; it creates no second orchestration API.
    - _Requirements: 2.3, 4.1–4.4, 5.6–5.11, 6.1–6.6, 10.1_
  - [x] 4.2 Retain existing Hypothesis **Property 15: Operator-visible executable state is actionable before effect** coverage.
    - Preserve required human-centered fields and event ordering that emits a preview before an executable effect.
    - **Validates: Requirements 6.5–6.6.**
  - [-] 4.3 Add isolated API, frontend-contract, and LegacyEngine E1 evidence tests.
    - Create target-local API tests and `backend/tests/evidence/test_e1_legacy.py`; cover versioned-route-only exposure, tenancy, redaction, queue/dispatch, observation, approvals, denied adapters, and retained run/definition/configuration/adapter hashes. Run frontend tests through project-local scripts only.
    - _Requirements: 2.1, 4.1–4.4, 5.6–5.11, 6.1–6.6, 8.6–8.7, 10.1–10.2_

- [ ] 5. Complete sandbox-only evolution validation
  - [x] 5.1 Retain existing immutable SandboxVariant, promotion assessment, canary, rollback, and versioned evaluation/evolution service code.
    - Proposals remain sandbox-only; no task may mutate production workflows, graphs, prompts, roles, tool policy, Host code, or activate a production canary.
    - _Requirements: 7.1–7.10, 8.1–8.8, 10.1_
  - [x] 5.2 Write Hypothesis **Property 16: Evolution variants are isolated and promotion is exhaustive**.
    - Create `backend/tests/properties/test_property_16_evolution.py` with deterministic local fakes and every candidate-cardinality/promotion-condition combination, including evidence-retention failures.
    - **Validates: Requirements 7.1–7.3, 7.6.**
  - [x] 5.3 Write Hypothesis **Property 17: Active canaries enforce approved scope containment**.
    - Create `backend/tests/properties/test_property_17_canary.py` with bounded organization/workflow/case scope-containment cases; test decisions only and never activate a real canary.
    - **Validates: Requirements 7.9.**
  - [-] 5.4 Add barrier-controlled evaluation/evolution integration tests.
    - Create `backend/tests/integration/evaluation_evolution/` with deterministic local fakes for immediate blocking, non-blocking continuation, E1 absence, zero/multiple candidates, evidence-retention failure, delayed canary activation, rollback, and API tenancy.
    - _Requirements: 7.4–7.8, 7.10, 8.3–8.4, 8.7, 10.1_

- [ ] 6. Deliver the remaining constrained, stub-only Video_Pack controls
  - [x] 6.1 Implement the data-only `pack_spine`/supervisor workflow, durable blocker events, cancellation token, and graph-state preservation.
    - Add pack configuration below `business/video/` and `backend/app/video/blockers.py`. Use only the registered deterministic stub-media adapter through the Host broker; a ComplianceAgent blocker must stop new graph steps in under five seconds using a local monotonic scheduler.
    - _Requirements: 9.2–9.3, 10.2_
  - [-] 6.2 Implement immutable video artifact versions, acyclic lineage validation, retained release requests, fail-closed release decisions, and only the necessary versioned video routes.
    - Add `backend/app/video/artifacts.py`, `release.py`, an artifact repository, and target-local route/schema modules. Do not call a media provider or release an artifact during implementation or testing.
    - _Requirements: 9.4–9.5, 6.5–6.6, 10.1–10.2_
  - [x] 6.3 Write Hypothesis **Property 21: Video release is a complete fail-closed gate**.
    - Create `backend/tests/properties/test_property_21_video_release.py` with bounded lineage, rights/consent, quality, provenance, sign-off, and blocker combinations; assert request retention and all unmet conditions on denial.
    - **Validates: Requirements 9.4–9.5.**
  - [x] 6.4 Add deterministic video integration tests for the stub-only spine and release controls.
    - Create `backend/tests/integration/video/`; cover blocker stopping time, retained graph state, tenant filtering, release denials, and permitted simulated decisions. Do not access external resources or perform a real release.
    - _Requirements: 9.2–9.5, 6.5–6.6, 10.1–10.2_

- [ ] 7. Complete GraphEngine checkpoint recovery and dual-engine migration safety
  - [x] 7.1 Complete and validate configured-Postgres checkpoint persistence and same-organization resume handling.
    - Refine the existing `backend/app/repositories/postgres_checkpoint.py`, `backend/app/runs/checkpoints.py`, and migration seam as necessary. Use `{organization_id}:{run_id}` thread IDs, deny cross-organization resume before lookup, and fail closed if durable persistence is unavailable.
    - _Requirements: 6.4, 10.1_
  - [x] 7.2 Add isolated local Postgres integration tests for restart recovery, same-organization resume, pre-lookup cross-organization denial, and outage behavior.
    - Create `backend/tests/integration/checkpoints/` with a pinned isolated local fixture; do not provision, migrate, or contact any shared/remote database.
    - _Requirements: 6.4_
  - [-] 7.3 Implement migration-gate assessment and atomic LegacyEngine retirement.
    - Add `backend/app/engines/migration.py` and `backend/app/evaluation/migration_evidence.py`. Keep LegacyEngine available until every current gate passes; when they do, disable new and active legacy execution with durable evidence, never through automatic deployment.
    - _Requirements: 4.6–4.8_
  - [-] 7.4 Write Hypothesis **Property 11: Migration gate satisfaction is an all-evidence conjunction**.
    - Create `backend/tests/properties/test_property_11_migration_gate.py` covering both engines, multi-specialist handoffs, visible graph/interrupt, stubbed gated video spine, cross-organization-resume denial, and fail-closed allow-list proof.
    - **Validates: Requirements 4.8.**
  - [x] 7.5 Add deterministic GraphEngine integration and graph-E1 evidence tests.
    - Create `backend/tests/integration/graph_engine/`; exercise bounded handoffs, topology/interrupt visibility, approval resume, retirement, cross-organization denial, and target-local E1 evidence through Host-owned fakes only.
    - _Requirements: 4.5–4.9, 5.6–5.11, 6.4–6.6, 8.6–8.7_

- [ ] 8. Wire target-local Product-Bar evidence gates and final automated verification
  - [~] 8.1 Implement the deterministic evidence-gate runner.
    - Add `backend/app/evidence/gates.py`, `records.py`, and local fixtures that assemble independent E1–E9 records from current target-local run, evaluation, video, and migration evidence. Every record retains local IDs, hashes, adapter/schema versions, timestamps, command result, and supporting references; a failure blocks only its next configured transition and never mutates production.
    - _Requirements: 7.2–7.7, 8.1–8.8, 9.1–9.5_
  - [~] 8.2 Add final target-local evidence tests.
    - Create `backend/tests/evidence/test_product_bar.py`; assert E1–E9 independence, all Properties 1–22, named checks, `/api/v1/*`-only exposure, stub-only adapters, and rejected unsafe operations. Retain reproducible local results without deployment, automatic promotion, canary activation, or artifact release.
    - _Requirements: 1.1–10.6_

- [~] 9. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise. Run `npm run sdd:check` from the workspace root; from `backend/`, run focused quiet tests while implementing and then `python -m pytest --tb=short -q`, `python -m ruff check app tests`, and `python -m mypy app tests`. Record commands, exit statuses, timestamps, hashes, and counterexamples/results in target-local evidence. Do not run a development server, use a network service, deploy, provision infrastructure, activate a production canary, or release a video artifact.

## Notes

- Task IDs are canonical numeric identifiers. The completed items retain their original `[x]` state; all remaining items retain their original `[ ]` state. Optional test work retains the task-tool optional marker `*` immediately after the checkbox.
- The approved design uses concrete Python/FastAPI implementation and strict TypeScript/Next.js frontend code, so no implementation-language selection is required.
- Every new or repaired property test uses Hypothesis with at least 100 bounded examples and the exact source-comment form `Feature: generic-swarm-business-os, Property N: <property title>`. Repositories, adapters, schedulers, and indexes are deterministic target-local fakes unless a task explicitly calls for an isolated local Postgres fixture.
- Completed checklist items record implemented source presence and previously established focused behavior. They do not override Task 1's current failed suite or authorize Product-Bar claims; the final evidence gate must pass.
- All paths, fixtures, evidence, writes, and validations remain inside `C:\Project\common-agent-swarm-ops`. This plan never permits reference-workspace access, external services, credentials, global installation, remote installers, deployment, automatic promotion, Host-code rewrite, unbounded orchestration, or action without recorded authorization.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.4"] },
    { "id": 1, "tasks": ["1.3"] },
    { "id": 2, "tasks": ["1.5"] },
    { "id": 3, "tasks": ["3.1", "5.2", "5.3", "6.1", "7.1"] },
    { "id": 4, "tasks": ["3.2", "5.4", "6.2", "7.2", "7.3"] },
    { "id": 5, "tasks": ["3.3", "6.3", "7.4"] },
    { "id": 6, "tasks": ["4.3", "6.4", "7.5"] },
    { "id": 7, "tasks": ["8.1"] },
    { "id": 8, "tasks": ["8.2"] }
  ]
}
```