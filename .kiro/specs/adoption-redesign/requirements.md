# Requirements Document

## Introduction

The Adoption_Platform will provide a domain-neutral control plane for independently owned multi-agent Domain_Packs. `va-agent-swarm` will remain the canonical owner and releaser of the VA_Domain_Pack while the Adoption_Platform supplies governed registration, execution, learning, migration, verification, compatibility, provider, and recovery controls for video and non-video domains.

## Glossary

- **Adoption_Platform**: The shared multi-agent host and control plane.
- **Domain_Pack**: A versioned declarative package describing one domain’s agents, workflows, policies, knowledge references, evaluations, and optional UI metadata.
- **VA_Domain_Pack**: The Domain_Pack owned and released by `va-agent-swarm` that defines canonical video-domain behavior.
- **Pack_Contract**: The versioned, domain-neutral registration format for a Domain_Pack.
- **Host_Contract**: The versioned host interface supported by the Adoption_Platform.
- **Invocation**: One requested execution of a registered workflow.
- **Agent_Learning_Contract (ALC)**: An agent-specific policy for memory, retrieval, reflection, evaluation, retention, and human promotion.
- **Retrieval_Record**: A durable record of the knowledge retrieval performed before one agent-node action.
- **Learning_Episode**: An immutable record of one terminal agent-node attempt outcome.
- **Lesson**: A versioned, assessed, agent-scoped knowledge item derived from Learning_Episodes.
- **Improvement_Proposal**: A sandbox-only candidate change supported by assessment evidence.
- **Artifact_Handoff**: An immutable, traceable artifact exchange between agents or workflows.
- **Governance_Controller**: The Adoption_Platform capability that enforces authorization, approval, audit, retention, risk, and provider policies.
- **Migration_Controller**: The Adoption_Platform capability that enforces migration evidence gates and rollback.
- **Verification_Suite**: The automated and reviewable release evidence produced for a stated pack and contract version set.
- **Provider_Adapter**: A capability-scoped interface to an external provider.
- **Source_Index**: The immutable inventory of VA source assets and their migration disposition.
- **Recovery_Action**: An approved restoration of a designated immutable Domain_Pack version.
- **Audit_Record**: A durable record of a governed decision, its inputs by reference, its outcome, and its correlation identifier.
- **Registration_Policy**: A documented host admission rule applied to a Domain_Pack after Pack_Contract validation.
- **Agent_Node_Attempt**: One execution attempt of an agent node with exactly one terminal outcome.
- **Compatibility_Status**: The recorded result of comparing a Domain_Pack compatibility range with supported Host_Contract and ALC ranges.
- **Release_Readiness_Decision**: A recorded decision that a defined workflow version is blocked or eligible for release.
- **Maturity_State**: One of the cataloged, registered, active, or production-proven operational evidence levels.
- **Activation_Eligible**: The lifecycle status assigned to a VA workflow that has satisfied all non-approval conditions required before an active-status transition.
- **Release_Policy**: The documented rule that authorizes a Release_Readiness_Decision.

## Requirements

### Requirement 1: Domain-neutral pack registration and invocation association

**User Story:** As a platform owner, I want one domain-neutral pack contract, so that unrelated multi-agent domains can use shared control-plane capabilities without custom host behavior.

#### Acceptance Criteria

1. THE Adoption_Platform SHALL expose one Pack_Contract for every Domain_Pack.
2. WHEN a Domain_Pack is submitted, THE Adoption_Platform SHALL validate the Domain_Pack identity, immutable version, Host_Contract compatibility range, content digest, signer identity, declared agents, declared workflows, capabilities, data classifications, required ALC version, and evaluation references against the Pack_Contract.
3. IF Pack_Contract validation fails, THEN THE Adoption_Platform SHALL reject the Domain_Pack registration.
4. IF a Domain_Pack passes Pack_Contract validation but fails an applicable Registration_Policy, THEN THE Adoption_Platform SHALL reject the Domain_Pack registration.
5. WHEN the Adoption_Platform rejects a Domain_Pack registration, THE Adoption_Platform SHALL create one Audit_Record containing the rejected pack identifier, submitted version, failed validation categories, and correlation identifier.
6. IF Audit_Record persistence fails during a Domain_Pack rejection, THEN THE Adoption_Platform SHALL complete the rejection without an Audit_Record.
7. WHEN Pack_Contract validation succeeds and all applicable Registration_Policies have completed, THE Adoption_Platform SHALL persist a registration record containing the Domain_Pack identifier, immutable version, content digest, signer identity, declared compatibility range, validation result, and registration decision.
8. WHEN an agent node is requested for an Invocation, THE Adoption_Platform SHALL persist the organization identifier, domain identifier, pack version, agent identifier, workflow identifier, run identifier, and correlation identifier before starting the agent node.
9. IF required Invocation association persistence fails, THEN THE Adoption_Platform SHALL deny the Invocation before starting an agent node.
10. WHEN the Adoption_Platform denies an Invocation because association persistence failed, THE Adoption_Platform SHALL create an Audit_Record for the denial.
11. WHEN an approved Domain_Pack version is superseded, THE Adoption_Platform SHALL retain the prior approved Domain_Pack version and the Host_Contract and ALC versions needed to reproduce prior Invocations.


### Requirement 2: VA canonical ownership and video-domain preservation

**User Story:** As a VA domain owner, I want `va-agent-swarm` to remain the authority for video behavior, so that reuse of the Adoption_Platform does not alter video business semantics.

#### Acceptance Criteria

1. THE VA_Domain_Pack SHALL be the canonical released source for video agent roles, prompts, rubrics, workflow definitions, knowledge sources, provider selections, media policies, evaluations, and UI terminology.
2. WHEN the Adoption_Platform registers a VA_Domain_Pack, THE Adoption_Platform SHALL store only validated, versioned references and content digests for VA_Domain_Pack assets in the registration record.
3. THE Adoption_Platform SHALL apply the same Pack_Contract, authorization, lifecycle, and extension patterns to each mechanism used by the VA_Domain_Pack as to the corresponding mechanism used by non-video Domain_Packs.
4. IF executable package code is detected in a VA_Domain_Pack at any validation stage, THEN THE Adoption_Platform SHALL reject the registration.
5. WHEN the Adoption_Platform rejects executable package code, THE Adoption_Platform SHALL create an Audit_Record identifying the package identifier, version, code location reference, and correlation identifier.
6. IF Audit_Record persistence fails during executable-package-code rejection, THEN THE Adoption_Platform SHALL complete the rejection without an Audit_Record.
7. WHERE executable package code is detected after a VA_Domain_Pack registration has succeeded, THE Adoption_Platform SHALL allow registered Domain_Pack operations under the succeeded registration.
8. WHERE a VA_Domain_Pack declares an Artifact_Handoff metadata extension, THE Adoption_Platform SHALL validate the extension against the registered VA_Domain_Pack extension schema before accepting the Artifact_Handoff.
9. IF a VA_Domain_Pack Artifact_Handoff metadata extension fails schema validation, THEN THE Adoption_Platform SHALL block the Artifact_Handoff.
10. WHEN the Adoption_Platform blocks an Artifact_Handoff for VA_Domain_Pack extension validation failure, THE Adoption_Platform SHALL create an Audit_Record for the blocked handoff.

### Requirement 3: Domain isolation and governed execution

**User Story:** As an organization administrator, I want domain execution and data access to be isolated and governed, so that one domain cannot affect another domain’s data or capabilities.

#### Acceptance Criteria

1. WHEN an agent requests Domain_Pack data access, THE Governance_Controller SHALL evaluate organization identifier, domain identifier, supported pack-version range, agent identifier, and declared memory scope before returning data.
2. IF an agent requests a cross-organization, cross-domain, or undeclared memory scope, THEN THE Governance_Controller SHALL deny the data-access request.
3. WHEN the Governance_Controller denies a data-access request, THE Governance_Controller SHALL create an Audit_Record.
4. IF Audit_Record persistence fails after a denied data-access request, THEN THE Governance_Controller SHALL continue governed operations without an Audit_Record for that request.
5. IF an agent requests an undeclared tool identifier, THEN THE Governance_Controller SHALL deny the tool request.
6. WHEN the Governance_Controller denies an undeclared tool request, THE Governance_Controller SHALL create an Audit_Record.
7. IF an agent requests an undeclared outbound destination, THEN THE Governance_Controller SHALL deny the outbound request.
8. WHEN the Governance_Controller denies an undeclared outbound request, THE Governance_Controller SHALL create an Audit_Record.
9. WHEN the Adoption_Platform creates an Artifact_Handoff, THE Adoption_Platform SHALL start persistence of the handoff lineage, owner, classification, integrity reference, approval reference, and provenance reference.
10. WHEN the Adoption_Platform creates an Artifact_Handoff, THE Adoption_Platform SHALL make the Artifact_Handoff available to downstream nodes when creation completes.
11. WHEN an externally created Artifact_Handoff is submitted to the Adoption_Platform, THE Adoption_Platform SHALL confirm persistence of handoff lineage, owner, classification, integrity reference, approval reference, and provenance reference before making the Artifact_Handoff available through the Adoption_Platform.
12. IF an externally created Artifact_Handoff becomes available through the Adoption_Platform before metadata persistence confirmation completes, THEN THE Adoption_Platform SHALL revoke the Artifact_Handoff availability.
13. WHILE metadata persistence confirmation for an externally created Artifact_Handoff is incomplete, THE Adoption_Platform SHALL prevent downstream availability of the Artifact_Handoff.
14. WHEN the Adoption_Platform revokes an Artifact_Handoff availability for incomplete metadata persistence confirmation, THE Adoption_Platform SHALL create an Audit_Record.
15. WHEN the Adoption_Platform executes a registered workflow, THE Adoption_Platform SHALL enforce the workflow’s declared budget, rollback, approval, memory-read, and memory-write policies.

### Requirement 4: Learning activation, retrieval, and episode capture

**User Story:** As a governance owner, I want every learning-required agent to follow an enforceable individual learning lifecycle, so that learning is observable, safe, and attributable to each agent.

#### Acceptance Criteria

1. WHEN an agent is declared learning-required, THE Adoption_Platform SHALL require exactly one valid effective ALC that names the agent before granting active status.
2. WHEN the Adoption_Platform evaluates activation for a learning-required agent, THE Adoption_Platform SHALL verify approved agent-scoped memory, enabled pre-action retrieval, enabled Learning_Episode capture, an enabled reflection evaluator, a retention policy, and passing required evaluations for the proposed Domain_Pack version.
3. IF activation evaluation for a learning-required agent fails, THEN THE Adoption_Platform SHALL retain the agent in a non-active lifecycle status.
4. WHEN an ALC, workflow, tool capability, Domain_Pack version, or policy changes for an active learning-required agent, THE Adoption_Platform SHALL suspend the agent before applying the change.
5. WHEN a suspended learning-required agent is evaluated after a lifecycle-affecting change, THE Adoption_Platform SHALL grant active status only after the activation evaluation succeeds.
6. IF activation evaluation fails for a suspended learning-required agent after a lifecycle-affecting change, THEN THE Adoption_Platform SHALL retain the agent in a non-active lifecycle status.
7. WHEN a learning-required agent node begins in any lifecycle status, THE Adoption_Platform SHALL persist one Retrieval_Record containing the approved organization-, domain-, pack-version-, agent-, and memory-scope filters and the retrieved Lesson references, including an empty result.
8. IF Retrieval_Record persistence fails for a learning-required agent node, THEN THE Adoption_Platform SHALL block the agent-node action before execution.
9. WHEN the Adoption_Platform blocks an agent-node action for Retrieval_Record persistence failure, THE Adoption_Platform SHALL create an Audit_Record.
10. WHEN a learning-required Agent_Node_Attempt reaches a completed, failed, blocked, retried, or escalated terminal outcome, THE Adoption_Platform SHALL persist exactly one immutable Learning_Episode for that Agent_Node_Attempt.
11. IF Learning_Episode persistence fails for a learning-required Agent_Node_Attempt, THEN THE Adoption_Platform SHALL mark the Agent_Node_Attempt blocked for recovery.

### Requirement 5: Lesson assessment, promotion, and learning observability

**User Story:** As a safety reviewer, I want learning changes to be assessed, reversible, and auditable, so that autonomous learning cannot silently modify live behavior.

#### Acceptance Criteria

1. WHEN a Learning_Episode produces a candidate Lesson, THE Governance_Controller SHALL assess the candidate Lesson’s format, source Learning_Episode references, safety policy, domain policy, and configured evaluation threshold.
2. WHEN a candidate Lesson satisfies every required assessment and has a passed assessment outcome, THE Governance_Controller SHALL mark the Lesson retrievable for only the approved organization, domain, pack-version range, agent, and memory scope.
3. IF a candidate Lesson violates any required assessment criterion, THEN THE Governance_Controller SHALL mark the candidate Lesson non-retrievable through the standard Lesson retrieval process.
4. WHEN a Lesson revocation is requested, THE Adoption_Platform SHALL create an Audit_Record containing the revocation reason, actor, timestamp, and source references.
5. WHEN the Adoption_Platform persists an Audit_Record for a Lesson revocation, THE Adoption_Platform SHALL exclude the Lesson from future retrieval.
6. WHILE an Audit_Record for a requested Lesson revocation is not persisted, THE Adoption_Platform SHALL retain the Lesson as retrievable.
7. WHEN an output is produced after a Retrieval_Record, THE Adoption_Platform SHALL link the output to the Retrieval_Record and to the Learning_Episodes that sourced each retrieved Lesson.
8. WHEN an output has source Learning_Episodes but no Retrieval_Record, THE Adoption_Platform SHALL permit linking the output to the source Learning_Episodes.
9. THE Adoption_Platform SHALL expose per-agent counts of Learning_Episodes, assessed Lessons, retrieved Lesson reuse, stale Lessons, revoked Lessons, assessment outcomes, and escalations without exposing sensitive Lesson content.
10. WHEN assessed repeated failure satisfies an ALC improvement policy, THE Adoption_Platform SHALL create an Improvement_Proposal with the supporting Learning_Episode references and assessment results before evaluating a sandbox-state transition.
11. IF an Improvement_Proposal sandbox-state transition fails, THEN THE Adoption_Platform SHALL retain the Improvement_Proposal with the state-transition failure evidence.
12. IF an Improvement_Proposal lacks promotion approval, THEN THE Governance_Controller SHALL deny any requested live change to a prompt, rubric, tool policy, workflow, risk tier, or tool authorization.
13. WHEN a designated reviewer approves an Improvement_Proposal whose required assessment evidence satisfies policy, THE Governance_Controller SHALL record the reviewer identity, decision timestamp, evidence references, promotion state, and rollback reference.
14. WHEN the Adoption_Platform promotes an approved Improvement_Proposal, THE Adoption_Platform SHALL record the replaced immutable version, the promoted immutable version, and the rollback reference in an Audit_Record.


### Requirement 6: Controlled VA migration and multi-domain proof

**User Story:** As an adoption manager, I want phased migration gates with reversible evidence, so that VA adoption proceeds without mistaking a catalog for an operational capability.

#### Acceptance Criteria

1. WHEN a migration phase begins, THE Migration_Controller SHALL create a phase record containing the phase scope, required evidence, exit criteria, rollback procedure, host-owner review, and VA-owner review.
2. WHEN the VA source baseline is frozen, THE Migration_Controller SHALL require a Source_Index entry for every VA source asset containing the asset hash, owner, license-or-consent classification, and disposition.
3. WHEN the VA_Domain_Pack roster is prepared for registration, THE Migration_Controller SHALL require one VA_Domain_Pack agent mapping for each of the 114 indexed VA agents.
4. WHEN the VA_Domain_Pack roster is prepared for registration, THE Migration_Controller SHALL require one disposition for every Source_Index asset.
5. WHEN a VA workflow satisfies its declared domain evaluations, reproducible trace requirement, applicable human approvals, documented maturity level, and designated approval evaluation, THE Migration_Controller SHALL mark the VA workflow Activation_Eligible.
6. WHILE explicit activation approval for an Activation_Eligible VA workflow is absent or pending, THE Migration_Controller SHALL prevent the VA workflow active-status transition.
7. WHILE a VA workflow is not Activation_Eligible, THE Migration_Controller SHALL prevent the VA workflow active-status transition.
8. WHEN a migration rollback is approved, THE Migration_Controller SHALL restore the designated prior immutable VA_Domain_Pack version.
9. WHEN a migration rollback is approved, THE Migration_Controller SHALL apply the ALC retention policy to Lessons affected by the restored VA_Domain_Pack version.
10. WHEN the Migration_Controller completes a migration rollback, THE Migration_Controller SHALL retain the rollback evidence.
11. WHEN the multi-domain proof phase is evaluated, THE Adoption_Platform SHALL register at least two non-video Domain_Packs through the same Pack_Contract, learning lifecycle, and UI-extension contract used for the VA_Domain_Pack.
12. WHEN the load-environment multi-domain proof is evaluated, THE Verification_Suite SHALL produce evidence of isolation, registration, activation, observability, and lifecycle operations for at least 24 concurrently registered Domain_Packs.

### Requirement 7: Verification and release evidence

**User Story:** As a release approver, I want layered automated evidence for adoption behavior, so that production decisions are based on reproducible proof rather than implementation claims.

#### Acceptance Criteria

1. THE Verification_Suite SHALL provide deterministic schema-validation tests for Pack_Contract validation and Artifact_Handoff lineage validation.
2. THE Verification_Suite SHALL provide deterministic unit tests for lifecycle states, ALC validation, Lesson assessment, retention, and Provider_Adapter allow-lists.
3. WHEN the Verification_Suite validates generated valid and invalid inputs through execution, static analysis, or simulation, THE Verification_Suite SHALL test domain isolation, activation atomicity, acyclic Artifact_Handoff lineage, denied cross-domain retrieval, and denied unapproved Improvement_Proposal promotion.
4. WHEN the Verification_Suite executes an integration test for a registered VA_Domain_Pack, THE Verification_Suite SHALL exercise graph compilation, Retrieval_Record creation, Learning_Episode capture, reflection assessment, critique blockers, approval gates, and immutable release validation using only mock Provider_Adapters.
5. IF a verification step following completed integration coverage fails, THEN THE Verification_Suite SHALL record the failure.
6. IF the Verification_Suite cannot persist a verification failure record, THEN THE Verification_Suite SHALL continue the remaining verification steps.
7. IF a verification step following completed integration coverage fails, THEN THE Verification_Suite SHALL produce a failed Release_Readiness_Decision.
8. IF a verification step fails while integration coverage is incomplete, THEN THE Verification_Suite SHALL continue verification without producing a failed Release_Readiness_Decision.
9. WHERE a Release_Policy permits an administrative failure decision, THE Verification_Suite SHALL allow creation of a failed Release_Readiness_Decision without a verification failure.
10. IF a verification step following completed integration coverage fails, THEN THE Verification_Suite SHALL preserve the completed integration-coverage result.
11. WHEN end-to-end coverage for the initial VA vertical workflow completes, THE Verification_Suite SHALL produce a fixed-seed trace bundle, fixture digests, Audit_Records, UI projections, and a Release_Readiness_Decision without requiring integration-coverage completion.
12. WHEN a supported Host_Contract, Pack_Contract, or ALC version combination is designated for release, THE Verification_Suite SHALL validate that combination and record its result in the compatibility matrix.
13. WHEN the Verification_Suite executes its security test set, THE Verification_Suite SHALL record a separate denial-and-audit result for each malicious Domain_Pack, path-traversal attempt, Lesson-poisoning attempt, secret-disclosure attempt, cross-tenant access attempt, and undeclared-tool access attempt.

### Requirement 8: Compatibility and provider governance

**User Story:** As a platform maintainer, I want explicit compatibility and change-control rules, so that host and Domain_Packs can evolve safely over time.

#### Acceptance Criteria

1. THE Adoption_Platform SHALL version Host_Contract APIs, Pack_Contract versions, ALC versions, and each Domain_Pack version independently.
2. WHEN a Domain_Pack declares a compatibility range that intersects the supported Host_Contract and ALC ranges, THE Adoption_Platform SHALL record the Domain_Pack Compatibility_Status as compatible.
3. WHEN a Domain_Pack declares a compatibility range that does not intersect the supported Host_Contract or ALC ranges, THE Adoption_Platform SHALL record the Domain_Pack Compatibility_Status as incompatible.
4. WHILE a Domain_Pack Compatibility_Status is incompatible, THE Adoption_Platform SHALL deny the Domain_Pack active-status transition.
5. WHILE a Domain_Pack Compatibility_Status is incompatible, THE Adoption_Platform SHALL prevent submission of every Invocation request for the Domain_Pack.
6. WHEN a contract-breaking change is proposed, THE Migration_Controller SHALL require a change-evidence record containing an architecture decision record, migration plan, consumer compatibility evidence, deprecation window, and rollback plan.
7. WHEN a contract-breaking change-evidence record contains every required artifact, THE Migration_Controller SHALL approve the contract-breaking change.
8. THE Governance_Controller SHALL authorize a Provider_Adapter only when a Domain_Pack declaration includes explicit capability, cost, retention, residency, and safety declarations.
9. IF a Provider_Adapter lacks a Domain_Pack declaration or any required provider declaration, THEN THE Governance_Controller SHALL deny Provider_Adapter authorization.
10. WHEN the Governance_Controller denies a Provider_Adapter authorization, THE Governance_Controller SHALL create an Audit_Record.
11. WHEN the Verification_Suite executes a workflow requiring a Provider_Adapter, THE Adoption_Platform SHALL use an authorized mock Provider_Adapter.
12. WHEN a new multi-agent domain is onboarded, THE Adoption_Platform SHALL require a Pack_Contract-valid Domain_Pack and declared evaluation references before the Domain_Pack becomes eligible for activation.

### Requirement 9: Operational risk safeguards and recovery

**User Story:** As an operations owner, I want fail-closed safety controls and recovery evidence, so that adoption risks are contained and reversible.

#### Acceptance Criteria

1. WHEN a Provider_Adapter times out, returns an unsafe result, exceeds an approved budget, or becomes unavailable, THE Governance_Controller SHALL deny the affected external action.
2. IF Audit_Record persistence fails after a Provider_Adapter action denial, THEN THE Governance_Controller SHALL retain the denial.
3. WHEN a video Artifact_Handoff lacks any required rights, consent, continuity, media-quality, channel, or approval gate, THE Adoption_Platform SHALL produce a blocked Release_Readiness_Decision.
4. WHEN a Recovery_Action is approved, THE Adoption_Platform SHALL retain the prior-version investigation evidence before restoration.
5. WHEN required Recovery_Action evidence is retained, THE Adoption_Platform SHALL restore the designated immutable Domain_Pack version.
6. IF required Recovery_Action evidence persistence fails before restoration, THEN THE Adoption_Platform SHALL halt the Recovery_Action.
7. THE Adoption_Platform SHALL report cataloged, registered, active, and production-proven Maturity_State values as distinct operational status values.
8. WHEN the Adoption_Platform disables a Domain_Pack because of a Provider_Adapter failure, THE Adoption_Platform SHALL retain each agent’s Maturity_State independently of the Domain_Pack operational status.
9. WHEN capacity controls identify a Domain_Pack as exceeding its approved load limit, THE Governance_Controller SHALL apply the approved throttle-or-disable capacity action to the affected Domain_Pack.
10. WHEN the Governance_Controller applies a capacity action to a Domain_Pack, THE Governance_Controller SHALL create an Audit_Record.