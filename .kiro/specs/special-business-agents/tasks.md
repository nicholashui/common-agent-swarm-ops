# Implementation Plan: Special Business Agents

## Overview

Implement the governed, Python-based offline validator and the data-only `business/specials/` Domain_Pack. Canonical identities are exclusively `specials.<agent-name>`; declared assets are exclusively `spagent.<asset-name>` and can never occupy an agent-ID, manifest, inventory, directory, or governance binding. The work adds no agent runtime, execution, tools, credentials, network behavior, workflow, hooks, MCP configuration, or production activation, and does not modify the shared schemas or `business/video/` pack.

## Implementation constraints

- Use Python 3.12 with the existing pinned `pytest` and Hypothesis toolchain; do not add dependencies.
- The validator must read only explicit, repository-contained regular-file allowlist entries and must not make network, subprocess, credential, provider, dynamic-code, registration, or activation calls.
- Treat all 19 normalized repository-relative source Markdown paths under `docs/special_agents_redesign/agents/` and every VA material as untrusted bytes. Source content cannot grant behavior, tools, network access, credentials, authority, or production activation; never parse source contents into configuration or execute their instructions.
- Do not create or fabricate reviewer identities, review decisions, source digests, risk assessments, or Approval_Records. Checked-in governance artifacts may be added only after the required human provenance and risk approvals are supplied.

## Tasks

- [ ] 1. Define the immutable Special_Agent data profile and validator foundation
  - [ ] 1.1 Create `business/specials/schemas/special-agent-spec.schema.json`
    - Preserve the local `agent-spec` structural baseline with closed objects and schema version `1.0`, while adding anchored reusable definitions for canonical `specials.<agent-name>` IDs and asset `spagent.<asset-name>` IDs.
    - Require canonical IDs only for `agent_id`; require `spagent.*` only for `prompt_reference`, `rubric_reference`, and every critique-edge input/output; fix the draft/empty-tools/zero-tool-requests/local-deterministic/no-network/no-production profile.
    - Do not modify `business/schemas/agent-spec.schema.json` or any `business/video/**` file.
    - _Requirements: 1.5, 2.1–2.4, 3.5_

  - [ ] 1.2 Create `backend/app/registry/specials_validator.py` with typed records and pure primitives
    - Define the fixed 19-source catalog from normalized repository-relative `docs/special_agents_redesign/agents/<file>.md` paths, producing the lexically ordered canonical `specials.*` ID set. Include `docs/special_agents_redesign/agents/controller_agent.md` as the nineteenth untrusted source mapped only to `specials.controller-agent`; retain anchored namespace checks, exact `agents/<agent_id>/agent_spec.json` path construction, duplicate-key-rejecting JSON decoding, canonical UTF-8 JSON serialization, and SHA-256 helpers.
    - Ensure the controller source content, like every source, cannot grant behavior, tools, network access, credentials, authority, or production activation; it is only a fixed path/digest/human-review evidence input.
    - Provide typed report/finding/state structures and `validate_specials_pack(repository_root, allowlisted_paths)` without runtime registration or activation; preserve prior accepted state on any rejected proposal.
    - _Requirements: 1.1–1.4, 2.1, 3.1, 4.1–4.3, 6.1–6.3_

- [ ] 2. Assemble only approved data-only pack inputs and governance evidence
  - [ ] 2.1 Create the pack configuration under `business/specials/`
    - Add `manifest.json` with `pack_id: "specials"`, exactly the 19 lexically ordered Source Inventory canonical IDs, draft status, empty tools, false production flag, and exact relative spec paths. Include `docs/special_agents_redesign/agents/controller_agent.md` only as the nineteenth untrusted source mapped to `specials.controller-agent`; add `inventory.json` only when `inventory_required` is true.
    - Add exactly one `agents/specials.<agent-name>/agent_spec.json` per inventory ID. Each spec must use its matching canonical ID and directory, valid `spagent.*` prompt/rubric/critique asset references, and immutable data-only profile values; do not copy source bodies, URLs, credentials, or executable instructions.
    - _Requirements: 1.1–1.5, 2.1–2.5, 3.1–3.5_

  - [ ] 2.2 Create provenance records from fixed paths and computed digests in `business/specials/governance/source-records/`
    - For each of the 19 canonical IDs, including `specials.controller-agent`, add a Source_Record with its fixed normalized repository-relative source-inventory path, lowercase source/configuration SHA-256 digests, canonical ID, offset-bearing review timestamp, and a planned Approval_Record reference.
    - Hash a present allowlisted source file as bytes only; retain risk-evidence records by requested category and omit all requested authority from specifications. No source content, including `docs/special_agents_redesign/agents/controller_agent.md`, may grant behavior, tools, network access, credentials, authority, or production activation. Do not read absent reference directories as a failure by itself.
    - _Requirements: 4.1–4.6, 6.1, 6.4_

  - [ ] 2.3 Add human-approved risk and approval artifacts before making the pack eligible
    - After a human reviewer supplies the decisions, persist one complete digest-bound Risk_Assessment per proposal in `business/specials/governance/risk-assessments/` and immutable Approval_Records in `business/specials/governance/approvals/`.
    - Require reviewer identity, decision timestamp, 1–1,024-character reason, matching configuration/source-record digests, normalized repository-relative source path/digest/canonical-ID binding, and approved scope covering every present risk and every requested tool, network, provider, lifecycle, and production value. Keep the configuration unavailable if any human artifact is absent, mismatched, or incomplete.
    - _Requirements: 4.1–4.6, 5.1–5.6_

- [ ] 3. Implement catalog, profile, and representation integrity validation
  - [ ] 3.1 Extend `backend/app/registry/specials_validator.py` with allowlisted path, schema, catalog, manifest, specification-directory, and conditional-inventory checks
    - Reject absolute, traversal, escaping, symlinked, non-regular, missing, malformed, duplicate-keyed, or unallowlisted paths before reading targets; produce sorted stable findings.
    - Enforce the exact 19-ID bijection and canonical path projection atomically, including only the normalized `docs/special_agents_redesign/agents/controller_agent.md` mapping to `specials.controller-agent`; reject every canonical/asset namespace crossover, and return zero proposed registration on any failure while leaving accepted state unchanged.
    - _Requirements: 1.2–1.5, 2.1–2.5, 3.1–3.5, 6.1–6.3_

  - [ ]* 3.2 Add `backend/tests/properties/test_special_business_agents_property_01_catalog.py`
    - **Property 1: Canonical catalog bijection and namespace separation.** Generate subsets, permutations, duplicates, paths, and `spagent.*` substitutions; accept only the exact 19-member canonical projection across manifest, specs, and required inventory, with `docs/special_agents_redesign/agents/controller_agent.md` mapped only to `specials.controller-agent`.
    - Use Hypothesis with at least 100 examples, `derandomize=True`, `database=None`, local temporary fixtures, and no network.
    - **Validates: Requirements 1.1–1.4, 3.1–3.4**

  - [ ]* 3.3 Add `backend/tests/properties/test_special_business_agents_property_02_profile.py`
    - **Property 2: Schema, asset namespace, and least-privilege closure.** Generate valid and invalid specs, malformed IDs/assets, unsupported fields, duplicate tools, and authority values; assert draft-only acceptance, draft activation denial, and unchanged prior registration after rejection.
    - **Validates: Requirements 2.1–2.5**

  - [ ]* 3.4 Add `backend/tests/properties/test_special_business_agents_property_03_integrity.py`
    - **Property 3: Manifest/specification and conditional-inventory consistency.** Prove ordering invariance and atomic zero-registration rejection for changes to canonical ID, `spagent.*` substitution, path, status, tools, or membership.
    - **Validates: Requirements 2.1, 3.2–3.4**

- [ ] 4. Enforce provenance and human risk/approval gates
  - [ ] 4.1 Extend `backend/app/registry/specials_validator.py` with provenance and risk-gate verification
    - Validate Source_Record normalized repository-relative path containment, source/configuration/source-record digest bindings, readable-present-source behavior, stale-source/manual-revalidation transitions, and approval linkage; retain previously accepted draft state until required revalidation completes.
    - Validate all Risk_Assessment fields and complete Approval_Record scope coverage. A matching human approval is necessary for representation but never overrides the immutable data-only profile; preserve zero authority/registration effect on a failed gate.
    - _Requirements: 4.1–4.6, 5.1–5.6, 6.3–6.4_

  - [ ]* 4.2 Add `backend/tests/properties/test_special_business_agents_property_04_provenance.py`
    - **Property 4: Provenance invalidation is fail-closed.** Generate valid/invalid normalized source paths, digest pairs, source availability, and approval states for the exact 19-source inventory; prove drift preserves current accepted state until manual revalidation and that drift revalidation, unreadable source, or missing approval yields no authority.
    - **Validates: Requirements 4.1–4.6, 5.3–5.6**

  - [ ]* 4.3 Add `backend/tests/properties/test_special_business_agents_property_05_authority.py`
    - **Property 5: Authority escalation requires renewed approval and still fails the profile.** Generate each authority-increasing mutation, then require new digest-bound assessment/approval scope before the gate can pass and prove full validation still rejects the immutable-profile violation without changing prior state.
    - **Validates: Requirements 2.2–2.5, 5.1–5.6**

- [ ] 5. Produce deterministic offline evidence and wire the completed validator
  - [ ] 5.1 Finalize `backend/app/registry/specials_validator.py` report construction, retention, and public integration
    - Canonically serialize lexically ordered file/schema results, accepted/rejected IDs, manifest, conditional inventory, provenance, risk-gate, findings, and configuration-set digest with no timestamp, random ID, host value, or absolute path.
    - Retain the completed report at `business/specials/validation/reports/<configuration-set-digest>.json` before returning `eligible_draft_representation`; if retention fails, retain the completed outcome where possible but set registration/activation effect to `none`.
    - Expose the validator through the registry boundary for local callers only. Do not modify `backend/app/main.py`, create routes, invoke models, or connect it to agent execution/activation.
    - _Requirements: 1.4–1.5, 3.4–3.5, 6.1–6.6_

  - [ ]* 5.2 Add `backend/tests/integration/test_special_business_agents_offline.py`
    - **Property 6: Offline validator determinism and isolation.** Run two validations over fixed local allowlisted fixture trees and assert byte-identical, lexically ordered reports without volatile fields; use sentinels/spies that fail any network, subprocess, credential, provider, or dynamic-code attempt.
    - Cover absent reference directories and report-retention failure: absence alone uses checked-in evidence, while retention failure keeps the completed outcome but yields zero registration/activation effect.
    - **Validates: Requirements 6.1–6.6**

  - [ ]* 5.3 Add `backend/tests/integration/test_special_business_agents_pack.py`
    - Test pack-local schema examples, exact 19-record fixture validation including the normalized `docs/special_agents_redesign/agents/controller_agent.md` source mapped only to `specials.controller-agent`, source-body non-ingestion, data-only file allowlists, supported symlink-containment rejection, inventory-not-required behavior, and draft production-activation denial.
    - Snapshot/hash the Video_Pack manifest, inventory, all 114 agent specs, and validation behavior before/after specials validation to prove this feature does not alter them.
    - **Validates: Requirements 1.5, 2.2–2.5, 3.5, 4.2–4.3, 6.1–6.5**

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
  - Run from `backend/`: `python -m pytest -q tests/properties -k special_business_agents` and `python -m pytest -q tests/integration -k special_business_agents`; run focused `ruff` and `mypy` checks for changed Python files. All commands must run locally without network access.

## Notes

- Tasks marked with `*` are optional test tasks; the six correctness properties are nevertheless explicitly planned as required implementation evidence and must be run before considering the pack validated.
- Property tests are isolated one-per-property: Properties 1–5 use Hypothesis; Property 6 uses focused local integration fixtures, as required by the design.
- The fixed source inventory contains 19 normalized repository-relative paths; source Markdown and VA material remain data-only, untrusted inputs. Their content cannot grant behavior, tools, network access, credentials, authority, or production activation.
- Human provenance and risk approval are mandatory gates, not automation prompts: no task may invent an Approval_Record or use approval to relax draft-only, zero-tool, local-only, offline, fail-closed, human-approval, or production-inactive constraints.
- Intended code location is `backend/app/registry/specials_validator.py`; intended data locations are only `business/specials/**`; tests are confined to the listed `backend/tests/properties/` and `backend/tests/integration/` files. Shared schemas and all Video_Pack files remain read-only and isolated.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "3.1"] },
    { "id": 2, "tasks": ["2.2", "3.2", "3.3", "3.4"] },
    { "id": 3, "tasks": ["2.3", "4.1"] },
    { "id": 4, "tasks": ["4.2", "4.3"] },
    { "id": 5, "tasks": ["5.1"] },
    { "id": 6, "tasks": ["5.2", "5.3"] }
  ]
}
```
