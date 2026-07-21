# Implementation Plan: Migration Redesign

## Overview

Implement the local-only Migration Management System in Python by extending `backend/app/video/` with a `migration/` package and the three designed CLI seams under `scripts/business/`. The plan keeps common contracts and the existing L0/non-active runtime posture immutable, treats reviewed source material as inert corpus data, and produces deterministic machine-readable reports and append-only migration evidence. Human approvals are supplied as reviewed local records; tooling validates and enforces them but never invents them.

## Tasks

- [ ] 1. Establish deterministic migration contracts and protected common boundaries
  - [ ] 1.1 Create canonical migration records and safe local-path utilities
    - Add `backend/app/video/migration/contracts.py`, `canonical.py`, and `paths.py` with frozen, explicitly typed records for source snapshots, approved import sets, reports, manifest entries, map/spec/workflow reviews, and migration evidence.
    - Normalize forward-slash relative paths, canonicalize JSON and digest inputs, sort findings deterministically, and reject absolute, traversal, escaping-link, unreadable, and out-of-root paths without leaking secrets or corpus bodies.
    - _Requirements: 1.3, 1.4, 1.6, 3.1, 3.2, 3.8, 3.9, 4.2, 8.12_

  - [ ] 1.2 Implement immutable Common Pack Contract snapshots and activation-request rejection
    - Add `backend/app/video/migration/common_contracts.py` to compare inventory, manifest, agent runtime bindings, policies, schemas, and `workflows/pack_spine.json` before and after migration; require an explicit compatible-review record for an allowed common-contract change.
    - Reject imported provider, credential, network, production-activation, and human-gate-bypass requests as configuration changes; never load corpus paths into configuration contexts.
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 4.8, 4.9, 4.10_

  - [ ]* 1.3 Write deterministic unit tests for canonical records, path containment, result ordering, and contract snapshots
    - Add `backend/tests/unit/video/test_migration_contracts.py` using fixed roots, fixed timestamps, and fixed digest fixtures; assert redaction-safe stable diagnostic codes and byte-identical canonical JSON.
    - _Requirements: 1.3, 1.4, 2.1, 2.2, 2.5, 2.6, 2.7, 2.8, 3.2, 3.8, 3.9_

  - [ ]* 1.4 Write property test for local required references and non-binding provenance
    - Add `backend/tests/properties/test_migration_redesign_property_01_local_authority.py` with bounded safe/unsafe path graphs and explicit minimal regression examples.
    - **Property 1: Required references are local and provenance remains non-binding.**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 6.1, 6.4, 6.8, 8.7.**

  - [ ]* 1.5 Write property test for immutable common contracts and runtime restrictions
    - Add `backend/tests/properties/test_migration_redesign_property_02_contract_safety.py` with generated import/spec mutations and explicit provider, credential, network, activation, and gate-bypass examples.
    - **Property 2: Common contracts and runtime restrictions cannot be weakened by import.**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14.**

- [ ] 2. Build the approved, transactional corpus-intake pipeline
  - [ ] 2.1 Implement offline source discovery and deterministic dry-run planning
    - Add `backend/app/video/migration/intake.py` and `scripts/business/import_video_corpus.py` dry-run support to record the pinned snapshot, classify every candidate, compute size/SHA-256, map destinations, detect collisions/prohibited material/secrets/license-provenance gaps, and emit a canonical JSON report without mutations or network capability.
    - Keep dry-run reports complete and sorted, return non-zero with a machine-readable failure summary on any failed validation, and retain source instructions as untrusted bytes only.
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 3.8, 3.9, 3.10, 3.11, 4.8, 4.9, 4.10_

  - [ ] 2.2 Implement exact Human Import Gate verification for write mode
    - Add `backend/app/video/migration/approval.py` to recompute and compare the snapshot revision, ordered file paths, destinations, sizes, digests, license/provenance values, and total bytes against the recorded Approved Import Set and approval identity.
    - Block all writes on drift, scope expansion, approval mismatch, or undeclared destination; report `blocked` with stable diagnostics and no partial mutation.
    - _Requirements: 3.3, 3.7, 3.8, 3.9, 4.1, 4.2_

  - [ ] 2.3 Implement staged corpus writes, manifest generation, and integrity verification
    - Add `backend/app/video/migration/corpus.py` and complete `scripts/business/import_video_corpus.py --write` to stage only verified files under `business/video/corpus/`, re-hash destinations, atomically publish canonical manifest/provenance records, and never delete an existing pack file.
    - Implement idempotent reapplication (`no_change`), immediate path/size/digest mismatch reporting, and configuration-context exclusion for every imported corpus path.
    - _Requirements: 3.3, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12_

  - [ ]* 2.4 Write deterministic unit tests for dry-run classification and approval comparison
    - Add `backend/tests/unit/video/test_migration_intake.py` with local fixtures for path/link escapes, caches/secrets/binaries, license gaps, collisions, digest drift, and frozen JSON reports; assert dry-run leaves the destination tree unchanged.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11_

  - [ ]* 2.5 Write property test for deterministic, bounded, non-mutating dry runs
    - Add `backend/tests/properties/test_migration_redesign_property_03_dry_run.py` with bounded generated source trees, fixed clocks, and explicit passing/failing fixtures.
    - **Property 3: Dry-run source intake is deterministic, bounded, and non-mutating.**
    - **Validates: Requirements 3.1, 3.2, 3.8, 3.9, 3.10.**

  - [ ]* 2.6 Write property test for fail-before-write unsafe, prohibited, and colliding intake
    - Add `backend/tests/properties/test_migration_redesign_property_04_intake_rejection.py` covering absolute/traversal/escaping paths, prohibited content, secret findings, and destination collisions against a preserved tree digest.
    - **Property 4: Unsafe, prohibited, or colliding imports fail before pack mutation.**
    - **Validates: Requirements 3.4, 3.5, 3.6, 3.7.**

  - [ ]* 2.7 Write property test for exact approval-gated writes
    - Add `backend/tests/properties/test_migration_redesign_property_05_approval.py` using generated one-field approval mismatches plus an explicit exact-match example.
    - **Property 5: Write-mode imports exactly match human approval.**
    - **Validates: Requirements 3.3, 4.1, 4.2.**

  - [ ]* 2.8 Write property test for reproducible manifests, rehashing, and idempotence
    - Add `backend/tests/properties/test_migration_redesign_property_06_corpus_integrity.py` with bounded approved sets and deliberate path, size, and digest corruption examples.
    - **Property 6: Corpus manifests are complete, reproducible, and integrity-preserving.**
    - **Validates: Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11.**

  - [ ]* 2.9 Write property test for corpus exclusion from executable configuration contexts
    - Add `backend/tests/properties/test_migration_redesign_property_07_corpus_boundary.py` with executable-looking corpus inputs and activation configuration candidates.
    - **Property 7: Imported corpus cannot enter configuration contexts.**
    - **Validates: Requirements 4.8, 4.9, 4.10, 2.10, 2.11, 2.12, 2.13, 2.14.**

- [ ] 3. Validate the complete common-agent taxonomy and substantive local specifications
  - [ ] 3.1 Implement exact reviewed Agent Source Map validation and local projections
    - Add `backend/app/video/migration/agent_mapping.py` to compare `AGENT_SOURCE_MAP.json` against the authoritative inventory’s exact 114 Common Agent IDs, validate statuses, source-document locality, rationale, reviewer, timestamp, `common_only` semantics, ambiguity, and reused-source distinct rationale.
    - Generate or validate `ROSTER.json` and `MAP.md` solely from the reviewed map using Common Agent IDs; block every write-mode specification output when any mapping prerequisite fails.
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

  - [ ] 3.2 Implement local-only SPEC drafting, validation, and controlled write mode
    - Add `backend/app/video/migration/specifications.py` and `scripts/business/build_video_agent_specs.py` to read only local contracts, approved mappings, and local corpus/pack assets; enforce all eight required headings, concrete video responsibility, local knowledge references, historical-only provenance, runtime-binding preservation, and required critical-role reviews.
    - Accumulate every invalid specification in one deterministic result, write exactly one `SPEC.md` per inventory ID only after complete map validation, and retain all common agent configuration unchanged.
    - _Requirements: 1.3, 1.4, 1.5, 2.1, 2.5, 2.6, 2.7, 2.8, 5.5, 5.6, 5.7, 5.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [ ]* 3.3 Write deterministic unit tests for map and SPEC failure aggregation
    - Add `backend/tests/unit/video/test_migration_mapping_specs.py` using 114-ID fixtures and focused missing, duplicate, ambiguous, unreviewed, invalid-`common_only`, generic-responsibility, missing-heading, external-link, and critical-review cases.
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [ ]* 3.4 Write property test for exact, reviewed, taxonomy-preserving maps
    - Add `backend/tests/properties/test_migration_redesign_property_08_agent_mapping.py` with bounded mutations of a fixed 114-ID inventory and explicit invalid mapping examples.
    - **Property 8: Agent mapping is exact, reviewed, and taxonomy-preserving.**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8.**

  - [ ]* 3.5 Write property test for complete, substantive, local specifications
    - Add `backend/tests/properties/test_migration_redesign_property_09_specs.py` with generated heading/responsibility/reference mutations and multi-error expected results.
    - **Property 9: Every specification is local, complete, and substantive.**
    - **Validates: Requirements 5.9, 6.1, 6.2, 6.3, 6.4, 6.6, 6.7, 6.8, 6.9.**

  - [ ]* 3.6 Write property test for safety-critical specification review gates
    - Add `backend/tests/properties/test_migration_redesign_property_10_critical_reviews.py` with generated critical/noncritical role classifications and explicit missing-review examples.
    - **Property 10: Safety-critical specifications require human review.**
    - **Validates: Requirements 6.5.**

- [ ] 4. Validate local operational assets without creating an alternate runtime
  - [ ] 4.1 Implement adapted-workflow, process, knowledge-seed, and special-skill validation
    - Add `backend/app/video/migration/operational_assets.py` to validate Common Agent IDs, finite node/handoff/time/tool budgets, allow-listed tools, risk gates, compensation behavior, critique loops, human interrupts, and preservation of `pack_spine.json` until a workflow passes.
    - Validate process coverage only against passing local workflows and known IDs; require local provenance and consumer references for knowledge seeds; keep special skills absent unless compatibility, security, overlap, license, reviewer, timestamp, and local consumer checks pass.
    - _Requirements: 2.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 8.14, 8.15_

  - [ ]* 4.2 Write deterministic unit tests for operational asset rejection and safe registration
    - Add `backend/tests/unit/video/test_migration_operational_assets.py` with fixed workflow/process/seed/skill fixtures for unknown agents, disallowed tools, unbounded graphs, absent gates, invalid consumers, incomplete reviews, and baseline-spine retention.
    - _Requirements: 2.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 8.14, 8.15_

  - [ ]* 4.3 Write property test for constrained local operational assets
    - Add `backend/tests/properties/test_migration_redesign_property_11_operational_assets.py` with bounded generated workflows, process references, seeds, and special-skill reviews.
    - **Property 11: Operational assets are constrained to local common contracts.**
    - **Validates: Requirements 2.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 8.14, 8.15.**

- [ ] 5. Deliver offline verification, immutable release evidence, and controlled refresh support
  - [ ] 5.1 Implement deterministic standalone verification and the read-only checker CLI
    - Add `backend/app/video/migration/standalone.py` and `scripts/business/check_video_domain_standalone.py` to check disabled-network and unavailable-upstream preconditions before any content validation; terminate non-zero with sorted machine-readable output when either precondition fails.
    - Validate corpus integrity, 114-ID agreement across inventory/manifest/agent directories/map/roster/SPECs, required local references, specification content, workflow/process coverage, and safe registration paths. Print exactly `STANDALONE PASS` only when every local check passes.
    - _Requirements: 1.3, 1.4, 1.5, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.9, 6.2, 6.3, 6.4, 6.6, 6.7, 6.8, 6.9, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11, 8.12, 8.13, 8.14, 8.15_

  - [ ] 5.2 Implement append-only migration evidence, completion gates, and rollback verification
    - Add `backend/app/video/migration/evidence.py` to append canonical phase records containing commands/results, digests, review references, blockers, residual risks, source snapshot, pre-import manifest digest, corpus digest, change-set reference, and release outcomes; make previous records immutable.
    - Implement completion as a conjunction of passing executable gates with no licensing, mapping, workflow, security, or standalone blocker. Record phase completion with blockers as blocked, enforce executable evidence for a claim, and validate authorized Git-revert rollback against the recorded predecessor digest without changing runtime maturity or activation.
    - _Requirements: 1.1, 1.2, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10, 9.11, 9.12, 9.13, 9.14_

  - [ ] 5.3 Implement documentation-integrity checking and reviewed refresh orchestration
    - Add `backend/app/video/migration/documentation.py` and refresh orchestration to validate local asset claims/counts and ownership in `business/video/README.md`, `adoption.md`, and `structure.md`; report absent assets as deterministic non-blocking diagnostics that still fail the completion gate.
    - Route normal and urgent refreshes through the same pinned snapshot, exact-approval, corpus-manifest, changed-map review, standalone, evidence, and provenance steps as initial intake; update the checked-in local documentation only from validated local assets.
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_

  - [ ]* 5.4 Write deterministic integration tests for the complete local migration flow
    - Add `backend/tests/integration/video/test_migration_redesign.py` with fixed temporary pack fixtures to cover dry-run no-mutation, approved import/idempotent re-import, rehash mismatch, 114-ID agreement, multi-error SPEC reporting, workflow/process registration, special-skill exclusion, standalone precondition failures and success, completion blocking, refresh review, and evidence/rollback digest restoration.
    - Execute each CLI with network-disabled and upstream-unavailable fakes only; retain the emitted canonical JSON and command/result assertions as test evidence, not a completion substitute.
    - _Requirements: 1.1, 3.3, 3.7, 3.10, 4.3, 4.5, 4.11, 4.12, 5.1, 6.2, 6.9, 7.7, 7.12, 7.13, 8.1, 8.2, 8.3, 8.4, 8.10, 8.11, 8.12, 8.13, 9.1, 9.9, 9.10, 9.11, 9.13, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_

  - [ ]* 5.5 Write property test for standalone isolation preconditions and aggregate result
    - Add `backend/tests/properties/test_migration_redesign_property_12_standalone.py` with generated precondition and local-validator outcomes plus explicit short-circuit regression examples.
    - **Property 12: Standalone verification checks its isolation preconditions first.**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11, 8.12, 8.13.**

  - [ ]* 5.6 Write property test for completion-gate conjunctions
    - Add `backend/tests/properties/test_migration_redesign_property_13_completion.py` with bounded evidence gate vectors, blocker combinations, and prose-only-claim examples.
    - **Property 13: Completion is a conjunction of executable release gates.**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.13, 9.14.**

  - [ ]* 5.7 Write property test for append-only evidence and rollback restoration
    - Add `backend/tests/properties/test_migration_redesign_property_14_evidence.py` with generated ordered phase evidence and authorized/unauthorized rollback inputs.
    - **Property 14: Evidence is append-only and rollback restores the recorded predecessor.**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.10, 9.11, 9.12.**

  - [ ]* 5.8 Write property test for truthful, operationally isolated documentation checks
    - Add `backend/tests/properties/test_migration_redesign_property_15_documentation.py` with generated local claims and absent-asset mutations.
    - **Property 15: Documentation is truthful but operationally isolated.**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.9.**

  - [ ]* 5.9 Write property test for reviewed normal and urgent refreshes
    - Add `backend/tests/properties/test_migration_redesign_property_16_refresh.py` with bounded refresh deltas, changed-map records, and explicit normal/urgent invalid-review examples.
    - **Property 16: Refreshes are full reviewed migrations.**
    - **Validates: Requirements 10.6, 10.7, 10.8, 10.9, 10.10.**

- [ ] 6. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise. Run focused quiet Python checks from `backend/` (`python -m pytest -q --tb=short tests/unit/video/test_migration_*.py tests/integration/video/test_migration_redesign.py tests/properties/test_migration_redesign_property_*.py --maxfail=1`), then `python -m ruff check app/video tests/unit/video tests/integration/video tests/properties` and strict `python -m mypy app/video tests`.
  - Run `npm run sdd:check` from the repository root before a completion claim. Persist command names, exit codes, canonical checker results, review references, residual risks, and unresolved blockers through the evidence implementation; passing checks do not create human approvals.

## Notes

- Tasks marked with `*` are optional test work. They are intentionally explicit: the design defines 16 universal correctness properties, each mapped to one bounded, deterministic Hypothesis module with fixed regression examples.
- All executable implementation is Python 3.12+ under the existing `backend/app/video/` package and `scripts/business/` CLI seam. Use frozen clocks, local fixtures, canonical UTF-8 JSON, and no network/provider/credential access.
- Human Import Gates, mapping reviews, critical-role SPEC reviews, special-skill reviews, completion decisions, and rollback authorization must be recorded local inputs. Automation verifies their presence and consistency but cannot fabricate them.
- Checkpoints and focused test commands are validation evidence, not standalone completion tasks. Completion remains blocked until the implemented evidence gate finds every required release gate passing and no unresolved blocker.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1", "3.1"] },
    { "id": 2, "tasks": ["1.3", "1.4", "1.5", "2.2", "2.5", "2.6", "3.2", "3.4", "4.1"] },
    { "id": 3, "tasks": ["2.3", "2.4", "2.7", "3.3", "3.5", "3.6", "4.2", "4.3"] },
    { "id": 4, "tasks": ["2.8", "2.9", "5.1", "5.3"] },
    { "id": 5, "tasks": ["5.2", "5.5", "5.8"] },
    { "id": 6, "tasks": ["5.4", "5.6", "5.7", "5.9"] }
  ]
}
```
