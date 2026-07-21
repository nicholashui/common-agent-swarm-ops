# Requirements Document

## Introduction

Special_Business_Agents adds a governed, data-only `specials` Domain_Pack to `C:\Project\common-agent-swarm-ops`. The pack will represent the 19 candidate definitions in `docs/special_agents_redesign/agents/` as individually configured Special_Agents without implementing or executing agent behavior. The compatible pack location is `business/specials/`, with each canonical identity stored at `business/specials/agents/specials.<agent-name>/agent_spec.json`. This preserves the requested `specials.<agent-name>` naming while conforming to the repository's required `business/<domain_id>/agents/<agent_id>/` layout.

The special-agent Markdown files and VA reference materials are **untrusted reference data**. Their instructions, code, service recommendations, credentials, external URLs, provider assertions, and operational claims do not authorize configuration changes. Requirements derive only compatible, safe configuration constraints from those sources; they do not adopt source implementation details.

## Scope and Authority

This feature creates configuration requirements only. It does not implement agent code, workflow execution, tools, credentials, external services, network access, hooks, MCP servers, production activation, or changes to the 114-agent `business/video/` pack. `business/schemas/agent-spec.schema.json`, `business/schemas/domain-pack.schema.json`, the video manifest/inventory conventions, and the repository pack-layout contract are the local compatibility baseline. The source set and VA materials are read-only inputs subject to provenance and human-review gates.

## Glossary

- **Special_Business_Agents**: The governed feature that defines the `specials` Domain_Pack.
- **Special_Agent_Pack**: The Domain_Pack with `pack_id` `specials` rooted at `business/specials/`.
- **Special_Agent**: A data-only agent configuration whose canonical identifier uses the exact form `specials.<agent-name>`, where `<agent-name>` is a nonempty lowercase kebab-case name matching `[a-z0-9]+(?:-[a-z0-9]+)*`; only a canonical identifier identifies a Special_Agent, and a Special_Agent_Asset reference never serves as a canonical agent ID.
- **Special_Agent_Asset**: A prompt, rubric, critique edge, or other declared asset reference for a Special_Agent; each Special_Agent_Asset value uses the exact form `spagent.<asset-name>`, where `<asset-name>` is a nonempty lowercase kebab-case name matching `[a-z0-9]+(?:-[a-z0-9]+)*`, and is distinct from every canonical Special_Agent identifier.
- **Special_Source_Set**: The 19 Markdown files enumerated in the Source Inventory.
- **Source_Record**: Immutable provenance metadata that identifies one untrusted source file, its repository-relative path, SHA-256 digest, and review decision.
- **Canonical_Agent_Name**: The kebab-case transformation of a Special_Source_Set file stem, used after the `specials.` prefix.
- **Agent_Specification**: The JSON configuration at `agents/specials.<agent-name>/agent_spec.json`.
- **Special_Manifest**: `business/specials/manifest.json`, the authoritative list of configured Special_Agents.
- **Special_Inventory**: An optional pack-local inventory record used only when a registration or validation contract requires an inventory.
- **Validation_Report**: A deterministic, machine-readable result for one validation run.
- **Risk_Assessment**: A review record that classifies a proposed Special_Agent's data sensitivity, external-effect potential, and requested authority.
- **Approval_Record**: An immutable human decision that identifies the reviewed configuration digest, Risk_Assessment, and allowed scope.
- **Offline_Validator**: A deterministic validator that reads only allowlisted local files and makes no network request.

## Source Inventory

The Special_Source_Set contains exactly these repository-relative files. Canonical IDs are intentionally derived from the file stem rather than from untrusted document instructions.

| Source file | Canonical agent ID |
|---|---|
| `aesthetics_agent.md` | `specials.aesthetics-agent` |
| `agent_loop_creator.md` | `specials.agent-loop-creator` |
| `agentic_rag_agent.md` | `specials.agentic-rag-agent` |
| `autotelic_agent.md` | `specials.autotelic-agent` |
| `complex_problem_solution_process_model.md` | `specials.complex-problem-solution-process-model` |
| `docs/special_agents_redesign/agents/controller_agent.md` | `specials.controller-agent` |
| `general_creative_agent.md` | `specials.general-creative-agent` |
| `intent_analysis_agent.md` | `specials.intent-analysis-agent` |
| `knowledge_router_agent.md` | `specials.knowledge-router-agent` |
| `llm_usage.md` | `specials.llm-usage` |
| `optimization_agent.md` | `specials.optimization-agent` |
| `planner_agent.md` | `specials.planner-agent` |
| `podcast_agent.md` | `specials.podcast-agent` |
| `psychological_profile_agent.md` | `specials.psychological-profile-agent` |
| `psychological_recommendation_agent.md` | `specials.psychological-recommendation-agent` |
| `research_agent.md` | `specials.research-agent` |
| `screenwriter_strategic_goal_achievement_agent.md` | `specials.screenwriter-strategic-goal-achievement-agent` |
| `strategic_goal_achievement_agent.md` | `specials.strategic-goal-achievement-agent` |
| `techology_advisor_agent.md` | `specials.techology-advisor-agent` |

## Requirements

### Requirement 1: Special Agent Pack Identity and Location

**User Story:** As a platform owner, I want canonical Special_Agent identities and locations, so that the new configurations integrate with the domain-pack architecture without creating a schema exception.

#### Acceptance Criteria

1. THE Special_Agent_Pack SHALL use exactly `specials` as its `pack_id` and exactly `business/specials/` as its configuration root.
2. WHEN the Special_Agent_Pack represents a Special_Source_Set file listed in the Source Inventory, THE Special_Agent_Pack SHALL assign only the Canonical_Agent_Name and canonical agent ID that exactly match that file’s Source Inventory entry.
3. WHEN an Agent_Specification is added to the Special_Agent_Pack, THE Special_Agent_Pack SHALL store the Agent_Specification only at `business/specials/agents/specials.<agent-name>/agent_spec.json`, where `specials.<agent-name>` exactly equals the Agent_Specification `agent_id`, matches the canonical-ID form defined in the Glossary, and exactly matches a Source Inventory canonical agent ID.
4. IF an Agent_Specification path is absolute, contains a `..` path segment, resolves outside `business/specials/`, does not exactly equal `business/specials/agents/<agent_id>/agent_spec.json`, has an `<agent_id>` path segment that differs from the Agent_Specification canonical agent ID, has a canonical agent ID that does not exactly match a Source Inventory canonical agent ID, has an `agent_id` outside the `specials.<agent-name>` form, or uses a Special_Agent_Asset reference as an `agent_id`, THEN THE Offline_Validator SHALL reject the Agent_Specification, report `INVALID_PATH` for an invalid path or `INVALID_AGENT_ID` for an invalid agent ID, register zero Special_Agents for the attempted change, and leave the previously accepted Special_Agent_Pack configuration and registration state unchanged.
5. THE Special_Agent_Pack SHALL contain only configuration data and none of the following: executable agent implementations, workflows, tool definitions, credentials, network endpoints, hooks, or MCP-server configurations.

### Requirement 2: Safe, Schema-Valid Agent Specifications

**User Story:** As a security owner, I want every Special_Agent configuration to conform to the local data-only schema and least-privilege defaults, so that untrusted reference material cannot grant execution authority.

#### Acceptance Criteria

1. WHEN an Agent_Specification is validated, THE Offline_Validator SHALL accept it only if it conforms to local Agent_Specification schema version `1.0`, its `agent_id` uses the exact `specials.<agent-name>` form defined in the Glossary, its `agent_id` exactly equals the containing agent directory identifier, and its `agent_id` exactly equals the corresponding Special_Manifest entry identifier.
2. THE Special_Agent_Pack SHALL configure each newly proposed or unapproved Special_Agent with `schema_version` `1.0`, `status` `draft`, `allowed_tools` as an empty array containing zero entries, `max_tool_requests` `0`, `production_activation_requested` `false`, `model_policy.provider` `local_deterministic`, and `model_policy.network_access` `false`.
3. WHEN any Agent_Specification is validated, THE Offline_Validator SHALL evaluate every declared Special_Agent_Asset value against the Agent_Specification schema, require each Special_Agent_Asset value to use the exact `spagent.<asset-name>` form defined in the Glossary, and reject the Agent_Specification after evaluating every declared Special_Agent_Asset value when any Special_Agent_Asset value is used as a canonical agent ID.
4. IF an Agent_Specification contains an unsupported field; an `agent_id` outside the `specials.<agent-name>` form; a Special_Agent_Asset value outside the `spagent.<asset-name>` form; a Special_Agent_Asset value used as an `agent_id`; an invalid budget, critique edge, or declared value; a duplicate allowed tool; a manifest value inconsistent with its `agent_id`; `production_activation_requested` set to `true`; `max_tool_requests` greater than `0`; or another required Agent_Specification validation failure, THEN THE Offline_Validator SHALL reject the Agent_Specification, return a single validation failure identifying every failed condition, register zero Special_Agents for the attempted change, and leave the previously accepted registration state unchanged.
5. WHILE a Special_Agent has `status` `draft`, THE Special_Agent_Pack SHALL deny each production-activation request, leave its `status` as `draft`, leave `production_activation_requested` as `false`, and return an indication that draft status prevents production activation.

### Requirement 3: Manifest and Conditional Inventory Integrity

**User Story:** As a registry owner, I want a complete, one-to-one Special_Agent configuration catalog, so that registry consumers can discover the intended agents without duplication or hidden substitutions.

#### Acceptance Criteria

1. WHEN the Special_Manifest is evaluated, THE Special_Manifest SHALL contain the exact 19-member set of canonical `agent_id` values listed in the Source Inventory, with each canonical agent ID appearing exactly once and with no additional Special_Agent entry.
2. WHEN the Offline_Validator validates the Special_Manifest, THE Offline_Validator SHALL produce a validation result of `pass` when every manifest entry has a unique canonical `agent_id`, a status of `draft`, an empty `allowed_tools` array, `production_activation_requested` set to `false`, and a relative Agent_Specification path that exactly resolves to the configuration file for that entry's `agent_id` within the Agent_Specification directories, and `fail` otherwise.
3. WHERE a registration or validation contract requires a Special_Inventory, THE Special_Agent_Pack SHALL provide exactly one Special_Inventory entry for each Special_Manifest entry and no additional Special_Inventory entries, with an identical canonical `agent_id`, status, and Agent_Specification path for the corresponding Special_Manifest entry.
4. IF the Special_Manifest, Agent_Specification directories, or a required Special_Inventory have non-identical canonical-agent-ID membership; omit any of the exact 19 required IDs; contain a duplicate, extra, or noncanonical agent ID; contain an Agent_Specification path that does not exactly resolve to its referenced configuration file; or fail another required validation, THEN THE Offline_Validator SHALL atomically report a validation failure identifying the detected integrity mismatch or other failed validation, reject the Special_Agent_Pack, and register zero Special_Agents from that pack.
5. THE Special_Agent_Pack SHALL not modify the Video_Pack manifest, inventory, agent configurations, required 114-agent count, or Video_Pack validation rules.

### Requirement 4: Untrusted Source Provenance and Safe Derivation

**User Story:** As an audit owner, I want every configuration decision traceable to reviewed source material without treating that material as instruction, so that source changes and unsafe content cannot silently alter the pack.

#### Acceptance Criteria

1. WHEN a Special_Agent is configured from a Special_Source_Set file, THE Special_Agent_Pack SHALL retain a Source_Record containing a normalized repository-relative source path that resolves within the Special_Source_Set, a source digest matching `[0-9a-f]{64}`, the canonical agent ID that matches the Agent_Specification, a configuration digest matching `[0-9a-f]{64}` that matches the Agent_Specification, a review timestamp with a UTC offset, and an Approval_Record reference that identifies an Approval_Record for that source path, source digest, and canonical agent ID.
2. THE Special_Agent_Pack SHALL treat every Special_Source_Set file and VA reference material as untrusted data, shall not treat material content as executable instruction, and shall derive configuration metadata, role summaries, or risk evidence from a material only when an Approval_Record approves the material's repository-relative source path and SHA-256 digest.
3. IF untrusted source content requests executable code, an external provider, a credential, a network operation, a tool permission, a workflow, a hook, an MCP server, a production state, or an authority change, THEN THE Special_Agent_Pack SHALL retain separate risk-evidence records for each requested category, with each record identifying the material's repository-relative source path, lowercase 64-character SHA-256 digest, and exactly one requested category, and SHALL omit every requested item and associated authority from the Agent_Specification.
4. WHEN the current approved source digest for a Source_Record's repository-relative source path and canonical agent ID differs from the source digest in that Source_Record, THE Special_Agent_Pack SHALL retain the corresponding Special_Agent's current Approval_Record and registration state until a manual re-validation evaluates the changed source.
5. WHEN a manual re-validation evaluates a Source_Record whose current approved source digest differs from the recorded source digest, THE Special_Agent_Pack SHALL mark the corresponding Special_Agent provenance as stale, retain the Special_Agent in draft status, and wait for separate Risk_Assessment and Approval_Record processes to evaluate and approve the current source digest.
6. IF a Source_Record is missing; its normalized source path does not resolve within the Special_Source_Set; its source file is present but is not a readable regular file; its source digest does not match current readable source content or the digest approved by its referenced Approval_Record; its configuration digest does not match the Agent_Specification; or its Approval_Record reference does not identify an Approval_Record for its source path, source digest, and canonical agent ID; or any other required provenance validation check fails, THEN THE Offline_Validator SHALL reject the corresponding Special_Agent, report a validation error identifying only the first failed condition encountered, leave the Agent_Specification and Source_Record unchanged, and leave any previously accepted registration unchanged.

### Requirement 5: Risk Assessment and Human Approval Gates

**User Story:** As a risk owner, I want explicit review before source-derived configurations gain representation or greater authority, so that sensitive profiles, recommendations, research, and automation concepts remain governed.

#### Acceptance Criteria

1. WHEN a Special_Agent configuration is proposed, THE Special_Agent_Pack SHALL associate the configuration with a Risk_Assessment that identifies the configuration digest and Source_Record digest; records each of the following potential risks as present or absent: sensitive personal data, psychological profiling or recommendation, legal, medical, financial, external-service, credential, external-write, and production-release; records external-effect potential as none or as one or more of external-service, external-write, and production-release; records every requested tool authority, requested network access, requested provider, and requested production activation, including none; and records exactly one requested lifecycle state.
2. IF a Risk_Assessment records one or more potential risks as present, THEN THE Special_Agent_Pack SHALL not mark or retain the configuration representation as reviewed unless an Approval_Record records an approval whose configuration digest exactly equals the Risk_Assessment configuration digest and whose Source_Record digest exactly equals the Risk_Assessment Source_Record digest, and whose approved risk scope includes every present potential risk, requested tool authority, requested network access, requested provider, requested production activation, and requested lifecycle state.
3. WHEN human review approves a Special_Agent configuration after a Risk_Assessment that satisfies criterion 1 exists for the configuration, THE Special_Agent_Pack SHALL retain an Approval_Record containing the approving reviewer identity, decision timestamp, matching configuration digest, matching Source_Record digest, approved risk scope, and a decision reason containing 1 to 1,024 characters.
4. IF a proposed Special_Agent configuration lacks a Risk_Assessment that satisfies criterion 1 and matches its configuration digest and Source_Record digest, or lacks an Approval_Record that records an approval under criterion 3 and whose approved risk scope includes every present potential risk, requested tool authority, requested network access, requested provider, requested production activation, and requested lifecycle state, THEN THE Special_Agent_Pack SHALL retain no configuration-derived authority for the proposal, keep the Special_Agent unavailable for registration, preserve any configuration registered before the proposal unchanged, and provide an indication that the proposal is unavailable because its Risk_Assessment or Approval_Record is missing or does not apply.
5. WHEN a proposed change adds a tool, network access, a non-local provider, a non-draft lifecycle state, or a production activation request, THE Special_Agent_Pack SHALL accept the proposed change only after associating the changed configuration with a new Risk_Assessment and a new Approval_Record, each matching the changed configuration digest and Source_Record digest, where the Approval_Record records human approval and its approved risk scope includes every added or changed requested tool authority, network access, lifecycle state, provider, and production activation request.
6. WHEN a proposed Special_Agent configuration has a Risk_Assessment and Approval_Record that satisfy criteria 1 through 3, THE Special_Agent_Pack SHALL record that the proposal satisfies the risk-and-approval gate and SHALL require all remaining validation and registration criteria to pass before the Special_Agent becomes available for registration.

### Requirement 6: Deterministic Offline Validation and Evidence

**User Story:** As a maintainer, I want a reproducible local validation result, so that the pack can be reviewed and verified without relying on external services or source repositories.

#### Acceptance Criteria

1. WHEN the Offline_Validator validates the Special_Agent_Pack, THE Offline_Validator SHALL read only explicitly allowlisted regular files whose resolved paths are within the repository root and SHALL perform no network request, subprocess execution, credential lookup, external-provider call, or source-code execution.
2. WHEN the Offline_Validator receives identical byte sequences for the same explicitly allowlisted regular files and the same configuration set, THE Offline_Validator SHALL produce a byte-for-byte identical Validation_Report containing accepted IDs and rejected IDs in ascending lexical order, per-file digest and schema results in ascending lexical order, the manifest result, the inventory result when the Special_Manifest requires inventory validation, the provenance result, the risk-gate result, and one overall pass or fail outcome; the Validation_Report SHALL contain no run-dependent timestamp, randomly generated identifier, host-specific field, absolute path, or other volatile field.
3. IF an explicitly allowlisted file is missing, malformed, unreadable, resolves outside the repository root, is not a regular file, or fails a required schema, integrity, provenance, approval, or membership check, THEN THE Offline_Validator SHALL produce a failing Validation_Report that identifies the affected file and failed check category, SHALL preserve the input files without modification, and SHALL produce zero registration or activation effect.
4. WHILE the Special_Source_Set or VA reference directories are unavailable, WHEN the Offline_Validator validates the Special_Agent_Pack, THE Offline_Validator SHALL determine the validation outcome solely from the checked-in Special_Manifest, Agent_Specifications, Source_Records, Risk_Assessments, and Approval_Records and SHALL not fail solely because either unavailable directory cannot be accessed.
5. WHEN the Offline_Validator completes a validation run, THE Special_Agent_Pack SHALL retain the completed Validation_Report, including the validated Special_Manifest digest and configuration-set digest, as local review evidence before producing any registration or activation effect.
6. IF the Special_Agent_Pack cannot retain a completed Validation_Report required by criterion 5, THEN THE Offline_Validator SHALL report the report-retention failure without changing the validation outcome determined by the completed validation checks and SHALL produce zero registration or activation effect.

## Executable Correctness Properties

The implementation plan must turn the following properties into deterministic executable tests. Properties 1 through 5 are suitable for property-based tests over generated valid and invalid configurations; Property 6 is suitable for focused integration tests using local fixtures. Tests must run without network access.

### Property 1: Canonical catalog bijection

For every generated subset, permutation, or duplicate-containing arrangement of the Source Inventory, pack validation passes exactly when the manifest, agent directories, and required inventory each contain the same set of all 19 canonical IDs exactly once, every specification path is the exact canonical path for its ID, and no `spagent.<asset-name>` value substitutes for a canonical ID.

**Validates: Requirements 1.1–1.4, 3.1–3.4**

### Property 2: Schema and least-privilege closure

For every generated Agent_Specification, validation accepts the specification only when every required schema constraint holds, the `agent_id` uses the exact `specials.<agent-name>` form, every declared asset value uses the exact `spagent.<asset-name>` form without serving as an `agent_id`, and each newly proposed or unapproved Special_Agent has draft status, empty tools, zero tool requests, local deterministic provider, disabled network access, and disabled production activation; a provider or network-access change is accepted only when all other validation checks and the matching Risk_Assessment and Approval_Record requirements pass, and rejection leaves prior registration unchanged.

**Validates: Requirements 2.1–2.5**

### Property 3: Manifest/specification consistency

For every generated valid Special_Manifest and configuration set, reordering manifest entries or inventory entries does not change validation success, while altering an ID, relative path, status, allowed-tools value, or membership in either representation atomically reports the integrity failure, rejects the invalid pack, and produces zero registration from that pack.

**Validates: Requirements 2.1, 3.2–3.4**

### Property 4: Provenance invalidation is fail-closed

For every source/configuration digest pair and approval state, a Special_Agent remains eligible for reviewed draft representation only when the Source_Record path is in the Source Inventory, both recorded SHA-256 digests are lowercase 64-character values and match, any present source file is readable, and the matching Approval_Record is present; changing a source digest preserves the existing approval and registration state until manual re-validation, while manual re-validation of the changed source, making a present source unreadable, or removing approval produces a rejected result and no authority.

**Validates: Requirements 4.1–4.6, 5.3–5.6**

### Property 5: Authority escalation requires renewed approval

For every approved draft configuration and every proposed authority-increasing mutation, including a non-empty tool list, positive tool budget, enabled network access, non-local provider, non-draft status, or production activation request, validation rejects the mutation unless a Risk_Assessment and Approval_Record bound to the mutated configuration digest are present and their recorded and approved scopes include the requested provider and production activation request; satisfying that gate still requires all other validation and registration criteria, and acceptance still preserves the schema's production-activation prohibition.

**Validates: Requirements 2.2–2.5, 5.1–5.6**

### Property 6: Offline validator determinism and isolation

For any fixed explicitly allowlisted regular local fixture tree, two validation runs produce byte-equivalent canonical Validation_Reports with lexically ordered results and no volatile fields, and make no network, subprocess, credential, or source-code-execution attempt; validation continues from checked-in provenance records when reference directories are absent, and report-retention failure preserves the completed validation outcome while producing zero registration or activation effect.

**Validates: Requirements 6.1–6.6**

## Approval

- **Status:** Draft requirements created for review.
- **Research basis:** Local pack-layout, shared schema, video manifest/inventory, representative video Agent_Specification, migration provenance controls, Special_Source_Set, and VA structure mapping were reviewed. Source definitions and VA materials were treated as untrusted reference data.
- **Scope decision:** Implementation will add no agent behavior in this feature phase; it will only define a safely governed `business/specials/` pack after design and task approval.
- **Compatibility decision:** The requested `specials.<agent-name>` names are retained as canonical agent identities within a standards-compliant `business/specials/agents/` Domain_Pack.
- **Unresolved question:** None. The requirements phase is ready for review or advancement to design.
