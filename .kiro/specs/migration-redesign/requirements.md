# Requirements Document

## Introduction

The Migration Management System makes `business/video/` a self-contained, pinned Video Pack in the Common Repository. The migration retains the Common Repository's domain-neutral architecture, the authoritative common video-agent identities, its non-active runtime posture, and human release controls. Completion requires local, offline-verifiable content and evidence; upstream repositories remain historical update inputs rather than runtime or design dependencies.

## Glossary

- **Migration Management System**: The capability that imports, validates, reconciles, evidences, and maintains the Video Pack.
- **Common Repository**: The `common-agent-swarm-ops` repository.
- **Video Pack**: Checked-in video-domain content beneath `business/video/`.
- **Authoritative Common Video Inventory**: The checked-in common inventory containing the 114 Common Agent IDs.
- **Common Agent ID**: An identity listed in the Authoritative Common Video Inventory.
- **Common Pack Contract**: A current common-owned manifest, inventory, schema, policy, agent specification, or safe baseline workflow.
- **Required Local Reference**: A reference required to understand, validate, register, or operate the Video Pack that resolves beneath the Common Repository root.
- **Historical Provenance**: Non-binding metadata recording an upstream repository, commit, path, license, or source relationship.
- **Source Snapshot**: A human-approved immutable upstream video-corpus revision selected for import.
- **Approved Import Set**: The reviewed source files, hashes, byte count, license and provenance metadata, and destination paths approved for one import.
- **Unsafe Source Path**: An absolute path, parent-directory traversal path, or source link that resolves outside the source root.
- **Prohibited Source Material**: A cache, virtual environment, dependency directory, build output, log, IDE metadata, credential, provider secret, generated media, personal data, or unreviewed binary asset.
- **Imported Corpus**: Approved source material copied under `business/video/corpus/` as inert, untrusted reference data.
- **Corpus Manifest**: The destination record of an Imported Corpus file's relative path, size, SHA-256 digest, and Historical Provenance.
- **Agent Source Map**: The reviewed local record associating every Common Agent ID with zero or more source-agent IDs and a relationship rationale.
- **Substantive Agent Specification**: A local `SPEC.md` containing identity, responsibility, boundaries and escalation, inputs and outputs, quality and critique, runtime binding, local knowledge sources, and provenance.
- **Adapted Workflow**: A local video workflow using Common Agent IDs and complying with Common Pack Contracts.
- **Special-Skill Integration**: A proposed pack-local integration requiring compatibility, security, overlap, and license review.
- **Human Import Gate**: Recorded human approval of an exact Approved Import Set before write mode changes the Video Pack.
- **Migration Evidence**: An immutable record of commands, results, commits, manifest digest, mapping review, and residual risks.
- **Standalone Verification**: Deterministic validation performed with both upstream repositories unavailable and network access disabled.
- **Documentation-Integrity Failure**: A documentation claim about a Video Pack asset that is absent from the Common Repository.
- **Migration Completion**: The state reached only after all required release gates pass.

## Requirements

### Requirement 1: Establish local video-pack authority

**User Story:** As a video-pack contributor, I want one checked-in local source of truth, so that the video domain can be understood and evolved without a sibling repository.

#### Acceptance Criteria

1. WHEN Migration Completion is reached, THE Migration Management System SHALL retain the checked-in Video Pack as the authoritative source for the pinned Video Pack version.
2. IF recording the authority designation fails, THEN THE Migration Management System SHALL record the authority-designation failure without blocking Migration Completion.
3. WHEN the Video Pack contains a Required Local Reference, THE Migration Management System SHALL resolve the Required Local Reference beneath the Common Repository root.
4. IF a Required Local Reference resolves outside the Common Repository root or cannot be resolved, THEN THE Migration Management System SHALL report a standalone-validation failure.
5. WHEN a checked-in specification uses an upstream repository or upstream path as a required source reference, THEN THE Migration Management System SHALL report a standalone-validation failure.
6. THE Migration Management System SHALL retain upstream repository, commit, path, and license information only as Historical Provenance.
7. THE Migration Management System SHALL keep video prompts, rubrics, workflows, policies, and knowledge within the Video Pack.

### Requirement 2: Preserve common contracts and runtime safety

**User Story:** As a Common Repository maintainer, I want the migration to retain established identities and safety restrictions, so that imported material cannot regress host behavior or activate production capabilities.

#### Acceptance Criteria

1. THE Migration Management System SHALL preserve every Common Agent ID in the Authoritative Common Video Inventory as the authoritative video-agent identity.
2. THE Migration Management System SHALL preserve each Common Pack Contract as authoritative.
3. WHEN a Common Pack Contract change is proposed, THE Migration Management System SHALL require recorded human review confirming compatibility before applying the change.
4. WHEN imported material contains an upstream agent ID, THE Migration Management System SHALL retain the upstream agent ID only as Historical Provenance or as a source relationship in the Agent Source Map.
5. THE Migration Management System SHALL preserve the non-active status of every common video agent.
6. THE Migration Management System SHALL preserve the existing model policy of every common video agent.
7. THE Migration Management System SHALL preserve the existing network restriction of every common video agent.
8. THE Migration Management System SHALL preserve the existing critique edges and refinement limits of every common video agent.
9. THE Migration Management System SHALL retain `business/video/workflows/pack_spine.json` as the safe baseline workflow until an Adapted Workflow is accepted.
10. WHEN imported material requests provider activation, THE Migration Management System SHALL reject the request as a configuration change.
11. WHEN imported material requests credential access, THE Migration Management System SHALL reject the request as a configuration change.
12. WHEN imported material requests network access, THE Migration Management System SHALL reject the request as a configuration change.
13. WHEN imported material requests production-agent activation, THE Migration Management System SHALL reject the request as a configuration change.
14. WHEN imported material requests a human-gate bypass, THE Migration Management System SHALL reject the request as a configuration change.

### Requirement 3: Authorize safe and bounded source intake

**User Story:** As a migration approver, I want each corpus import to be explicit, inspectable, and bounded, so that the Video Pack receives only reviewed material.

#### Acceptance Criteria

1. WHEN a Source Snapshot is proposed, THE Migration Management System SHALL record the source repository revision before modifying the Video Pack.
2. WHEN a Source Snapshot is evaluated, THE Migration Management System SHALL produce a dry-run report containing every proposed included file, excluded file, destination path, byte count, SHA-256 digest, collision finding, unsafe-path finding, secret finding, and license or provenance finding.
3. WHEN write mode is requested, THE Migration Management System SHALL require a Human Import Gate identifying the exact Approved Import Set.
4. IF a proposed import contains an Unsafe Source Path, THEN THE Migration Management System SHALL reject the proposed import before writing the Video Pack.
5. IF a proposed import contains Prohibited Source Material, THEN THE Migration Management System SHALL reject the proposed import before writing the Video Pack.
6. IF a proposed import contains an undeclared destination collision, THEN THE Migration Management System SHALL reject the proposed import before writing the Video Pack.
7. WHEN a proposed import is rejected, THE Migration Management System SHALL retain the Video Pack state that existed before the proposed import.
8. WHEN import validation fails, THE Migration Management System SHALL return a non-zero result.
9. WHEN import validation fails, THE Migration Management System SHALL emit a machine-readable failure summary.
10. WHEN dry-run mode is requested, THE Migration Management System SHALL not modify the Video Pack.
11. WHEN dry-run mode is requested, THE Migration Management System SHALL operate without network access.

### Requirement 4: Preserve corpus integrity and data boundaries

**User Story:** As a security and provenance reviewer, I want imported knowledge to remain auditable reference data, so that untrusted content cannot alter runtime behavior or lose its origin.

#### Acceptance Criteria

1. WHEN an Approved Import Set is written, THE Migration Management System SHALL copy only Approved Import Set files into `business/video/corpus/`.
2. WHEN an Imported Corpus file is written, THE Migration Management System SHALL record the destination-relative path, size, SHA-256 digest, original repository, original commit, original path, and license status in the Corpus Manifest.
3. WHEN an Imported Corpus file is validated, THE Migration Management System SHALL recompute the SHA-256 digest of the Imported Corpus file.
4. WHEN an Imported Corpus file's SHA-256 digest is recomputed, THE Migration Management System SHALL compare the recomputed SHA-256 digest with the Corpus Manifest entry.
5. IF a recomputed SHA-256 digest differs from the Corpus Manifest entry, THEN THE Migration Management System SHALL immediately report a corpus-integrity failure.
6. IF a Corpus Manifest entry differs from the corresponding Imported Corpus file's relative path, THEN THE Migration Management System SHALL report a corpus-integrity failure.
7. IF a Corpus Manifest entry differs from the corresponding Imported Corpus file's size, THEN THE Migration Management System SHALL report a corpus-integrity failure.
8. THE Migration Management System SHALL classify Imported Corpus as untrusted reference data.
9. WHEN Imported Corpus contains an executable instruction or configuration directive, THE Migration Management System SHALL retain the executable instruction or configuration directive as inert reference content.
10. THE Migration Management System SHALL exclude Imported Corpus from every configuration context.
11. WHEN the same Approved Import Set is applied more than once, THE Migration Management System SHALL produce identical Corpus Manifest content.
12. WHEN the same Approved Import Set is applied more than once, THE Migration Management System SHALL leave every destination file unchanged after the first successful application.

### Requirement 5: Reconcile the complete common-agent taxonomy

**User Story:** As a video-domain owner, I want each existing common video role mapped deliberately, so that equal roster sizes cannot cause incorrect role substitution.

#### Acceptance Criteria

1. THE Migration Management System SHALL create an Agent Source Map containing exactly 114 unique Common Agent IDs that exactly match the Authoritative Common Video Inventory.
2. WHEN an Agent Source Map entry is created, THE Migration Management System SHALL record the Common Agent ID, mapping status, source-agent IDs, source documents, relationship rationale, reviewer identity, and review timestamp.
3. WHERE a Common Agent ID has no semantically suitable source role or has a human-approved `common_only` relationship, THE Migration Management System SHALL record the mapping status as `common_only` with an empty source-agent-ID list.
4. WHEN one source-agent ID supports more than one Common Agent ID, THE Migration Management System SHALL require a distinct human-reviewed rationale for each affected Agent Source Map entry.
5. IF an Agent Source Map omits a Common Agent ID, THEN THE Migration Management System SHALL reject all write-mode Substantive Agent Specification output when validation detects the omission.
6. IF an Agent Source Map contains a duplicate Common Agent ID, THEN THE Migration Management System SHALL reject write-mode generation of the affected Substantive Agent Specification.
7. IF an Agent Source Map entry has an ambiguous relationship, THEN THE Migration Management System SHALL reject write-mode generation of the affected Substantive Agent Specification.
8. IF an Agent Source Map entry lacks recorded human review, THEN THE Migration Management System SHALL reject write-mode generation of the affected Substantive Agent Specification.
9. THE Migration Management System SHALL retain a local roster and a local human-readable mapping document that use Common Agent IDs.

### Requirement 6: Provide substantive local agent specifications

**User Story:** As a video-pack developer, I want a complete local specification for every common video agent, so that each role can be understood without external files.

#### Acceptance Criteria

1. WHEN an Agent Source Map entry is approved, THE Migration Management System SHALL generate or validate a Substantive Agent Specification for the corresponding Common Agent ID using only local files and Historical Provenance.
2. THE Migration Management System SHALL provide exactly 114 Substantive Agent Specifications, one for each Common Agent ID in the Authoritative Common Video Inventory.
3. WHEN a Substantive Agent Specification is validated, THE Migration Management System SHALL require sections for identity, responsibility, boundaries and escalation, inputs and outputs, quality and critique, runtime binding, local knowledge sources, and provenance.
4. WHEN a Substantive Agent Specification identifies a local knowledge source, THE Migration Management System SHALL validate the local knowledge source as a Required Local Reference.
5. WHEN a Substantive Agent Specification covers an orchestrator, compliance, rights and consent, privacy, legal, safety, provenance, release, judge, or human-review coordination role, THE Migration Management System SHALL require recorded human review before accepting the Substantive Agent Specification.
6. IF a Substantive Agent Specification lacks a required section, THEN THE Migration Management System SHALL report a specification-validation failure.
7. IF a Substantive Agent Specification contains only a generic role string in place of a concrete video-domain responsibility, THEN THE Migration Management System SHALL report a specification-validation failure.
8. IF a Substantive Agent Specification contains an external required source path, THEN THE Migration Management System SHALL report a specification-validation failure.
9. WHEN a Substantive Agent Specification has a specification-validation failure, THE Migration Management System SHALL continue validating the remaining Substantive Agent Specifications.

### Requirement 7: Govern adapted workflows, processes, knowledge, and special skills

**User Story:** As an operator, I want local video-domain operational assets that obey common controls, so that the pack is useful without creating an alternate runtime or control plane.

#### Acceptance Criteria

1. WHEN an upstream workflow is proposed for the Video Pack, THE Migration Management System SHALL adapt the workflow to Common Agent IDs and Common Pack Contracts before registration.
2. WHEN an Adapted Workflow is validated, THE Migration Management System SHALL validate each workflow agent reference against the Authoritative Common Video Inventory.
3. WHEN an Adapted Workflow is validated, THE Migration Management System SHALL require finite graph budgets, allow-listed tools, risk gates, compensation behavior, critique loops, and human interrupts.
4. IF an Adapted Workflow lacks a required graph budget, allow-listed tool, risk gate, compensation behavior, critique loop, or human interrupt, THEN THE Migration Management System SHALL reject the Adapted Workflow.
5. IF an Adapted Workflow references an unknown Common Agent ID, THEN THE Migration Management System SHALL reject the Adapted Workflow.
6. IF an Adapted Workflow references a disallowed tool, THEN THE Migration Management System SHALL reject the Adapted Workflow.
7. WHEN a local process index is created, THE Migration Management System SHALL validate each referenced Adapted Workflow before adding the reference to the local process index.
8. WHEN a local process index is created, THE Migration Management System SHALL validate each referenced Common Agent ID before adding the reference to the local process index.
9. WHEN a knowledge seed is added, THE Migration Management System SHALL store local Historical Provenance for the knowledge seed.
10. WHEN a knowledge seed is added, THE Migration Management System SHALL identify a local consumer for the knowledge seed.
11. WHEN a Special-Skill Integration is proposed, THE Migration Management System SHALL require a recorded compatibility, security, overlap, and license review before inclusion.
12. IF a Special-Skill Integration lacks an identified local consumer, THEN THE Migration Management System SHALL keep the Special-Skill Integration absent from the Video Pack.
13. IF a Special-Skill Integration lacks a completed review record, THEN THE Migration Management System SHALL keep the Special-Skill Integration absent from the Video Pack.

### Requirement 8: Verify standalone completeness and safe registration

**User Story:** As a release reviewer, I want deterministic offline verification of the whole pack, so that a passing migration demonstrates local completeness rather than access to an upstream checkout.

#### Acceptance Criteria

1. WHEN Standalone Verification is requested, THE Migration Management System SHALL verify that network access is disabled before running a validation step.
2. WHEN Standalone Verification is requested, THE Migration Management System SHALL verify that both upstream repositories are unavailable before running a validation step.
3. IF network access is enabled, THEN THE Migration Management System SHALL terminate Standalone Verification without running a validation step.
4. IF an upstream repository is available, THEN THE Migration Management System SHALL terminate Standalone Verification without running a validation step.
5. WHEN Standalone Verification runs, THE Migration Management System SHALL validate Corpus Manifest integrity.
6. WHEN Standalone Verification runs, THE Migration Management System SHALL validate agreement at 114 Common Agent IDs across the Authoritative Common Video Inventory, video manifest, agent directories, Agent Source Map, and Substantive Agent Specifications.
7. WHEN Standalone Verification runs, THE Migration Management System SHALL validate every Required Local Reference.
8. WHEN Standalone Verification runs, THE Migration Management System SHALL validate required Substantive Agent Specification sections and substantive content.
9. WHEN Standalone Verification runs, THE Migration Management System SHALL validate Adapted Workflow agent references, tool authorization, graph budgets, risk gates, human interrupts, and local process coverage.
10. IF a Standalone Verification check fails, THEN THE Migration Management System SHALL report overall Standalone Verification failure.
11. IF a Standalone Verification check fails, THEN THE Migration Management System SHALL return a non-zero result.
12. IF a Standalone Verification check fails, THEN THE Migration Management System SHALL emit a deterministic machine-readable failure summary.
13. WHEN all Standalone Verification checks pass, THE Migration Management System SHALL emit the deterministic result `STANDALONE PASS`.
14. WHEN the Video Pack is registered or dry-run registered, THE Migration Management System SHALL use Common Pack Contracts.
15. WHEN the Video Pack is registered or dry-run registered, THE Migration Management System SHALL use only existing safe workflow paths.

### Requirement 9: Govern rollout, reversibility, and completion claims

**User Story:** As a migration sponsor, I want staged release gates and reversible migration evidence, so that the pack cannot be declared complete or activated without defensible proof.

#### Acceptance Criteria

1. WHEN Migration Completion is evaluated, THE Migration Management System SHALL require successful source intake, corpus integrity, agent mapping, agent specifications, workflow adaptation, local knowledge, Standalone Verification, documentation, and Migration Evidence release gates.
2. WHEN a migration phase completes, THE Migration Management System SHALL record the phase result in Migration Evidence.
3. WHEN a migration phase completes with an unresolved blocker, THE Migration Management System SHALL allow the migration phase to be reported as completed.
4. WHEN a migration phase completes with an unresolved blocker, THE Migration Management System SHALL record the unresolved blocker status in Migration Evidence.
5. IF licensing uncertainty remains, THEN THE Migration Management System SHALL report Migration Completion as blocked.
6. IF an unreviewed semantic mapping remains, THEN THE Migration Management System SHALL report Migration Completion as blocked.
7. IF incomplete workflow adaptation remains, THEN THE Migration Management System SHALL report Migration Completion as blocked.
8. IF a security finding remains, THEN THE Migration Management System SHALL report Migration Completion as blocked.
9. IF Standalone Verification fails, THEN THE Migration Management System SHALL report Migration Completion as blocked.
10. WHEN a migration change set is prepared, THE Migration Management System SHALL retain the pre-import Video Pack manifest digest in Migration Evidence.
11. WHEN a rollback is authorized, THE Migration Management System SHALL restore the pre-import Video Pack state by reverting the recorded migration change set.
12. THE Migration Management System SHALL leave runtime maturity and runtime activation unchanged when Migration Completion is reached.
13. WHEN a completion claim is published, THE Migration Management System SHALL require successful executable-check results as a prerequisite.
14. IF a completion claim relies only on documentation prose, THEN THE Migration Management System SHALL reject the completion claim.

### Requirement 10: Maintain truthful documentation and controlled updates

**User Story:** As a long-term Video Pack maintainer, I want documentation and refreshes to remain synchronized with validated local assets, so that future changes preserve safety, provenance, and source-of-truth clarity.

#### Acceptance Criteria

1. WHEN Migration Completion is reached, THE Migration Management System SHALL document local Video Pack entry points, update policy, and checked-in source-of-truth ownership in the Video Pack README.
2. WHEN Migration Completion is reached, THE Migration Management System SHALL update `adoption.md` to match the Common Repository identity and Video Pack ownership.
3. WHEN Migration Completion is reached, THE Migration Management System SHALL update `structure.md` to match the Common Repository identity and as-built Video Pack asset counts.
4. IF documentation claims a Video Pack asset that is absent from the Common Repository, THEN THE Migration Management System SHALL report a Documentation-Integrity Failure.
5. WHEN a Documentation-Integrity Failure is reported, THE Migration Management System SHALL allow unrelated migration operations to continue.
6. WHEN a Video Pack refresh is proposed, including an urgent refresh, THE Migration Management System SHALL process the refresh as a reviewed import using a pinned Source Snapshot and an Approved Import Set.
7. WHEN a Video Pack refresh changes Imported Corpus, THE Migration Management System SHALL update the Corpus Manifest with the refreshed Imported Corpus data.
8. WHEN a Video Pack refresh changes an Agent Source Map entry, THE Migration Management System SHALL require review of the changed Agent Source Map entry.
9. WHEN a Video Pack refresh is prepared for completion, THE Migration Management System SHALL require Standalone Verification and Migration Evidence.
10. WHEN a Video Pack refresh is accepted, THE Migration Management System SHALL preserve Historical Provenance for the refresh.

## Requirement Quality Notes

- Each acceptance criterion uses one EARS pattern and states one observable outcome.
- Unsafe source intake, validation, path escape, credential access, runtime activation, and corpus-integrity failures fail closed.
- Documentation-Integrity Failures remain non-blocking for unrelated migration operations, but successful documentation remains a Migration Completion gate.
- The existing non-active runtime posture and human approval boundary are constraints that Migration Completion preserves; they do not constitute runtime activation evidence.
