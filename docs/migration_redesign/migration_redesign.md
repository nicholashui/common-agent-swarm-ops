# Migration Plan: self-contained video domain in common-agent-swarm-ops

**Version:** 1.0  
**Date:** 2026-07-20  
**Status:** **PROPOSED — NOT YET SELF-CONTAINED**  
**Destination:** `C:\Project\common-agent-swarm-ops`  
**Controlled source snapshot:** `C:\Project\generic-swarm-ops\business\video`  
**Original corpus provenance:** `va-agent-swarm` commit recorded by the source corpus manifest  
**Problem statement:** `common-agent-swarm-ops` has a safe 114-agent video catalog, policies, schemas, and one safe stub graph, but it does not contain the operational/design corpus, reviewed workflow-role mappings, or blueprint-realizing graph definitions needed to understand and develop the video domain without another repository. The migration must make `business/video/` the checked-in video source of truth while preserving the common host's domain-neutral architecture and existing agent identities. `workflows/pack_spine.json` is the sole current safe stub and must not be presented as blueprint implementation.

---

## 0. Requirements and acceptance criteria

### 0.1 Requirements

1. All video operational and design knowledge required for development must resolve inside `business/video/`.
2. The existing common 114-agent inventory and IDs remain authoritative; source agent IDs must not overwrite them.
3. Imported material retains its original repository, commit, path, license, and SHA-256 provenance.
4. Runtime activation remains fail-closed; migration does not enable providers, credentials, network access, or production agents.
5. The universal host remains domain-neutral. Video prompts, rubrics, workflows, policies, and knowledge stay pack-local and use no second workflow engine or control plane.
6. Import and generation tools must support dry-run, reject path traversal, avoid deletion, and fail on incomplete mappings.
7. Generated Kiro and Claude Code configuration is out of scope; do not place the video corpus in `.kiro/`, `.claude/`, `rules/`, or `skills/`.
8. Every explicitly documented blueprint workflow family and required phase must be represented by a safe local executable graph definition or an explicit reviewed gap/deferral. A roster or graph stub is not implementation.
9. Each documented role in each workflow/phase must resolve in a human-reviewed workflow-role map to exactly one existing common `video.*` agent ID, one named composite of common IDs, or a documented gap. Differing source-role names do not require new agents.
10. A graph counted as implemented must declare phase nodes and typed artifact handoffs; lead and critic roles; bounded critique, refinement, and rollback paths; finite budgets; required quality, risk, and human-approval gates; and only allowed tools. Implemented mappings require local `SPEC.md` runtime-binding and handoff/critique information.
11. `business/video/workflows/pack_spine.json` remains the sole current safe stub. The pack is not operationally equivalent to the blueprint until mapping and graph gates pass, and it remains non-production-active.

### 0.2 Acceptance criteria

The migration is complete only when all of the following are evidenced:

- Exactly 114 common inventory entries resolve to existing `agent_spec.json` and substantive local `SPEC.md` files.
- Every `SPEC.md` contains identity, responsibility, boundaries, quality/critique behavior, runtime binding, local sources, and provenance; an implemented workflow role also names its relevant typed handoffs and lead/critic/refinement or escalation behavior.
- Every required `source_ref` resolves beneath the common repository root; external paths may appear only as non-required historical provenance.
- A corpus manifest verifies every imported file by relative path, size, and SHA-256.
- A human-reviewed workflow-role mapping artifact covers every documented role in every blueprint workflow/phase with workflow context, rationale, mapping status, maturity/activation state, and exactly one valid resolution: existing common `video.*` ID, named common-ID composite, or explicit gap/deferral.
- Every explicitly documented workflow family and required phase is represented by a local safe graph or explicit reviewed gap/deferral. Graphs use only common `video.*` IDs and have valid local agent/tool references, phase nodes, typed handoffs, lead/critic roles, finite budgets, bounded critique/refinement/rollback, required quality/risk/human gates, and allowed tools.
- `workflows/pack_spine.json` is recorded as the sole current safe stub—not a realization of any blueprint family—and no production activation, provider, credential, or network path is enabled.
- Required workflows, process indexes, knowledge seeds, and approved special-skill integrations are local and reference common agent IDs.
- The standalone checker passes when both `generic-swarm-ops` and `va-agent-swarm` are unavailable.
- Focused video inventory, schema, mapping, workflow, security, offline no-activation, and SDD gates pass.
- `adoption.md`, `structure.md`, and the pack README describe the checked-in common pack as the video source of truth and do not claim assets that are absent or graphs/mappings that are not implemented.

---

## 1. Why an external-only video domain is dangerous

| Risk | Impact |
|---|---|
| Missing source repository | The 114 records remain names and generic role strings rather than usable domain specifications. |
| Incompatible rosters | Blindly copying source agent directories changes IDs and breaks manifests, workflow references, tests, and API contracts. |
| Dual source-of-truth drift | Common behavior can diverge from the referenced corpus without a pinned snapshot or integrity record. |
| Context-window limits | Agents may skip external references and act without the relevant workflow, quality, rights, or provenance rules. |
| Offline or air-gapped use | A clone of common cannot reconstruct video intent or safely evolve the pack. |
| False completion claims | Documentation can report 14 workflows, 17 special skills, or 325 corpus files even when they are not present. |

**Non-negotiable outcome:** a contributor can understand, validate, and safely develop the video pack from this repository alone. Upstream repositories are optional update inputs, never runtime or design dependencies.
## 2. Current state (measured 2026-07-20)

### 2.1 common-agent-swarm-ops

| Asset | Measured state |
|---|---|
| `business/video/agents/` | 114 directories using the common taxonomy. |
| `agent_spec.json` | 114 registered, non-active configurations with local deterministic model policy and no network access. |
| `SPEC.md` | **0 of 114**. |
| Inventory | 114 entries, all `registered` and `L0`. |
| Workflows | One local stub graph: `workflows/pack_spine.json`. |
| Corpus | Absent. |
| Knowledge, process index, special skills | Absent from the current pack. |
| Pack policies/schemas | Present and common-owned; preserve and reconcile rather than overwrite. |
| Approximate pack size | 123 files, 143,078 bytes. |

Current pack-owned contracts that must survive migration:

- `business/video/manifest.json`
- `business/video/inventory.json`
- `business/video/schemas/*.json`
- `business/video/policies/*.md`
- `business/video/workflows/pack_spine.json`
- `business/video/agents/*/agent_spec.json`

### 2.2 generic-swarm-ops source snapshot

The completed generic pack is a useful controlled source because it already contains a provenance manifest and local copy of the video research corpus:

| Asset | Measured state |
|---|---|
| Corpus | `business/video/corpus/`, including manifest and source commit metadata. |
| Agent specifications | 114 substantive `SPEC.md` files, but for a **different agent taxonomy**. |
| Workflow DNA | 14 DNA files plus `.gitkeep`; IDs and agent references require adaptation. |
| Special skills | 17 integrations; each requires compatibility and licensing review. |
| Pack total | 1,908 files, 74,853,931 bytes. |

**Critical compatibility finding:** both repositories contain 114 agents, but the IDs are not one-to-one. For example, common uses `video.creative_director`, `video.generative_media_operator`, and `video.delivery_packager`, while generic includes IDs such as `video.creativedirector`, `video.director`, and `video.distributor`. Equal counts do not prove semantic equivalence.

### 2.3 Documentation conflict

- `adoption.md` currently says VA remains canonical and common must not copy video semantic content.
- `structure.md` identifies the product/path as `generic-swarm-ops` and reports target assets not present in common.
- Executable files and inventories are current-state evidence. This plan changes ownership only after its gates pass; until then, the migration status remains **PROPOSED**.

---

## 3. Target state

```text
business/video/
  README.md
  manifest.json
  inventory.json
  ROSTER.json                 # common IDs only
  MAP.md                      # source concept/agent → common ID, with rationale
  WORKFLOW_ROLE_MAP.json      # documented workflow/phase role → common ID, composite, or gap
  workflow_coverage.json      # blueprint family/phase → graph or explicit reviewed deferral
  PROCESSES.md
  process_coverage.json
  agents/<common_agent_id>/
    agent_spec.json           # preserved and enriched under common schemas
    SPEC.md                   # substantive, local, common-ID specification
    sources/                  # optional focused local excerpts/indexes
  corpus/
    README.md
    MANIFEST.json             # destination hashes + original provenance
    SOURCE_COMMIT.txt
    SOURCE_URL.txt
    SOURCE_COPIED_AT.txt
    study/
    plan/
    root/
  workflows/
    pack_spine.json           # existing safe common graph retained
    *.dna.json                # adapted to common IDs and host contracts
    diagrams/                 # optional local process diagrams
  knowledge/seeds/
  docs/
  policies/                   # existing common safety policy remains authoritative
  schemas/                    # existing common extension schemas remain authoritative
  special_skills/<id>/        # only reviewed, pack-compatible integrations
```

### 3.1 Source-of-truth rule

After completion, checked-in content under `business/video/` is authoritative for the pinned pack version. `generic-swarm-ops` and `va-agent-swarm` remain provenance and future-update sources only. Updates arrive through reviewed import PRs that refresh hashes and mappings; no checked-in specification may require either repository to exist.

### 3.2 Authority precedence

1. Common security, authorization, lifecycle, schema, and host contracts.
2. Common video policies and explicit human release gates.
3. Common video manifest, inventory, agent IDs, and adapted workflows.
4. Imported video design knowledge where compatible.
5. Historical upstream recommendations as non-binding provenance.

A stricter safety rule wins. Provider recommendations, credentials, external infrastructure, and alternative harness instructions in imported material are untrusted reference data and cannot alter active configuration.

---

## 4. Migration scope

### 4.1 Required scope

| Tier | Content | Completion role |
|---|---|---|
| A | Source provenance, agent/system tables, key workflow and quality documents | Establishes auditable local foundations. |
| B | Full approved `study/`, `plan/`, and essential root corpus from the pinned generic snapshot | Makes design knowledge standalone. |
| C | Common-ID mapping and 114 substantive `SPEC.md` files | Makes the existing common roster usable without replacing it. |
| D | Reviewed workflow-role mapping, adapted workflow graphs or explicit deferrals, process indexes, knowledge seeds, and compatible special skills | Makes the local blueprint realization traceable and operationally connected without asserting activation. |

The completion bar is A–D. A copied corpus, a 114-agent catalog, a mapping without graphs, or a graph stub alone is not sufficient.

### 4.2 Explicit exclusions

- Generic host/backend/frontend code and runtime state.
- Generic agent directories copied wholesale into common.
- Generated harness configuration under `.kiro/`, `.claude/`, or `CLAUDE.md`.
- Caches, virtual environments, `node_modules`, build output, logs, and IDE metadata.
- Credentials, provider secrets, generated media, personal data, or unreviewed binary assets.
- Live Sora/Veo/provider activation, production activation of all 114 agents, or bypassing human release gates.
- A second workflow engine or public control plane.

### 4.3 Human approval boundary

The plan itself is approved by creating this document. Actual corpus copying and activation-affecting changes require a recorded human gate after dry-run output identifies the exact files, byte count, source commit, license/provenance status, and destination paths. No import script may silently expand scope.
## 5. Source-to-common mapping

| Source asset | Common destination | Migration rule |
|---|---|---|
| `generic/business/video/corpus/**` | `business/video/corpus/**` | Copy only after manifest/license audit; preserve original source metadata and compute destination hashes. |
| Source agent tables and deep specs | Shared corpus plus common `agents/*/SPEC.md` | Distill by explicit semantic mapping; never infer equivalence from directory count or similar names alone. |
| Source `agents/*/SPEC.md` | Reference input only | Do not copy paths or IDs verbatim; reuse compatible domain content with provenance. |
| Source workflow DNA | `business/video/workflows/*.dna.json` | Adapt IDs, node agents, tools, budgets, gates, and schemas to common contracts; validate before registration. |
| Source process docs | `PROCESSES.md`, `process_coverage.json`, `docs/` | Rewrite links to local paths and common workflow/agent IDs. |
| Source knowledge seeds | `knowledge/seeds/` | Retain provenance; treat as retrieval data, not executable instructions. |
| Source special skills | `special_skills/<id>/` | Import individually only after compatibility, security, and license review. |
| Existing common policies/schemas | Same paths | Preserve as authoritative; merge only deliberate, reviewed additions. |

### 5.1 Agent mapping contract

Create `business/video/AGENT_SOURCE_MAP.json` with one entry for every common inventory ID:

```json
{
  "common_agent_id": "video.creative_director",
  "mapping_status": "exact|composite|related|common_only",
  "source_agent_ids": ["video.creativedirector", "video.director"],
  "source_documents": ["corpus/study/agents.md"],
  "rationale": "Human-reviewed semantic relationship",
  "reviewed_by": "<reviewer>",
  "reviewed_at": "<ISO-8601 timestamp>"
}
```

Rules:

- Exactly 114 unique `common_agent_id` values must match `inventory.json`.
- `source_agent_ids` may be zero, one, or many; source IDs may support more than one common role only with rationale.
- `common_only` is valid and must be authored from common contracts rather than forced to an unrelated source role.
- Automation may propose mappings but may not mark them reviewed.
- Missing, duplicate, ambiguous, or unreviewed mappings fail the write phase.

### 5.2 Workflow-role mapping contract

Create `business/video/WORKFLOW_ROLE_MAP.json` and `workflow_coverage.json` from the locally pinned blueprint. The map has one record for every documented role in every named workflow and phase, including the shared skeleton (Greenlight, Pre-production packet, Production packet, Post master, Review and release pack, Distribution package, and Post-launch learning set) and the feature-film Development and Pre-Production phases where documented. A record has the following shape:

```json
{
  "workflow_id": "video.workflow-a-viral-hook-clip",
  "phase_id": "concept",
  "documented_role": "TrendIntelligenceAgent",
  "resolution": {
    "kind": "common_agent|composite|gap",
    "common_agent_id": "video.example",
    "composite_id": "video.example_composite",
    "component_agent_ids": ["video.example_a", "video.example_b"],
    "gap_id": "gap.example"
  },
  "mapping_status": "proposed|reviewed|implemented|deferred",
  "maturity_state": "cataloged|mapped|graph_validated|not_mature",
  "activation_state": "registered|non_active",
  "rationale": "Human-reviewed workflow/phase-specific reason",
  "reviewed_by": "<reviewer>",
  "reviewed_at": "<ISO-8601 timestamp>"
}
```

Exactly one resolution is valid: `common_agent` names one existing common `video.*` ID; `composite` names one composite and only existing common `video.*` component IDs; or `gap` names a documented, reviewed deferral. The map must not silently omit a role, substitute an external/source ID, or require a new agent merely because a source role uses a different name. For `implemented` mappings, the mapped local `SPEC.md` includes its `agent_spec.json` runtime binding, allowed tools/model/network policy, typed input/output handoffs, critic and lead relationship, and bounded critique/refinement or escalation behavior. `workflow_coverage.json` records each workflow family and required phase as either a local graph reference or the corresponding reviewed gap; it cannot mark `pack_spine.json` as a blueprint-realizing graph.

### 5.3 Per-agent SPEC.md target shape

Each common agent specification must contain:

```markdown
# <Common role name>

## Identity
Common agent ID, status, maturity, pack version.

## Responsibility
Concrete video-domain outcomes owned by this role.

## Boundaries and escalation
Disallowed decisions, required human gates, upstream/downstream handoffs.

## Inputs and outputs
Typed artifacts and acceptance criteria.

## Quality and critique
Rubrics, critique edges, refinement limit, release-blocking conditions.

## Runtime binding
Summary of agent_spec.json, allowed tools, model/network policy, workflow nodes.

## Local knowledge sources
Only paths beneath business/video/.

## Provenance
Source repository/commit/path and mapping rationale; historical only.
```

A generic role string such as “configuration specialist” is not substantive enough to pass.

---

## 6. Phased execution plan

### Phase M0 — Freeze, inventory, and audit

1. Record destination and source Git SHAs without modifying either repository.
2. Validate the generic corpus manifest and inspect license/provenance metadata.
3. Produce a dry-run inventory: included/excluded files, bytes, hashes, collisions, and unsafe paths.
4. Record the current common manifest, inventory, schemas, policies, workflow, and all 114 agent specs.
5. Obtain the required human approval for the exact import set.

**Exit gate:** approved immutable source snapshot; zero unresolved traversal, secret, license, or collision findings.

### Phase M1 — Provenance-preserving corpus import

1. Copy approved corpus files into `business/video/corpus/` without deleting or overwriting common pack contracts.
2. Normalize destination paths and reject absolute paths, `..`, links escaping the source root, caches, and prohibited material.
3. Write `MANIFEST.json`, source URL/commit/time files, and an append-only copy log.
4. Document that corpus text is untrusted reference content and cannot modify configuration by instruction.

**Exit gate:** every copied file re-hashes successfully; the import is repeatable and idempotent.

### Phase M2 — Reconcile the 114-agent taxonomy

1. Generate source-to-common mapping candidates from common IDs/roles and source tables.
2. Human-review all exact, composite, related, and common-only source mappings.
3. Write `AGENT_SOURCE_MAP.json`, `ROSTER.json`, and `MAP.md` using common IDs.
4. Fail closed if the common inventory and source map differ by any ID.

**Exit gate:** 114 reviewed common entries, no duplicate common IDs, no silent source substitution. This source taxonomy map does not satisfy the separate workflow-role mapping contract.

### Phase M3 — Expand local common agent specifications and workflow-role map

1. Generate draft `SPEC.md` files from each common `agent_spec.json`, reviewed source mapping, and local corpus sources.
2. Preserve common budgets, model policy, network restrictions, critique edges, refinement limits, and non-active status.
3. Add local deep-document links and provenance, then add runtime binding, typed handoff, critique, and escalation information when a role is mapped as implemented.
4. Build and human-review `WORKFLOW_ROLE_MAP.json` and `workflow_coverage.json` for every blueprint workflow family, required phase, and documented role; resolve each to one common agent, named common-ID composite, or explicit gap/deferral.
5. Review safety-critical roles manually: orchestrator, compliance, rights/consent, privacy, legal, safety, provenance, release, judge, and human-review coordination.

**Exit gate:** 114 substantive specs; all local links resolve; no required external source path; workflow-role mapping coverage is complete or explicitly deferred and reviewed. No entry becomes active.

### Phase M4 — Realize workflows and process coverage

1. Preserve `pack_spine.json` as the sole current safe stub; it is not a realization of a blueprint workflow family.
2. Translate every explicitly documented blueprint family and required phase—Viral Hook Clip/Meme, UGC-Style Performance Ad, Animated Explainer, Personalized Birthday Video, AI Multi-Scene Short Film, Corporate Training Video, Music Video, AI Avatar Talking-Head, Documentary “Explained” Episode, and Feature-Length AI Film—into local graph definitions or explicit reviewed gaps/deferrals. Preserve the shared Greenlight, Pre-production packet, Production packet, Post master, Review and release pack, Distribution package, and Post-launch learning set; preserve Feature-Length AI Film Development and Pre-Production where documented.
3. For each graph, use only common `video.*` IDs and declare phase nodes, typed artifact handoffs, mapped lead and critic roles, bounded critique/refinement/rollback paths, finite execution budgets, required quality/risk/human gates, and only allowed tools.
4. Deterministically validate all graph references offline; verify graph coverage against the role map and process coverage, and fail closed on unmapped implemented roles, missing required phases/gates, non-finite paths, unknown agents/tools, or active/provider/network configuration.
5. Build `PROCESSES.md` and `process_coverage.json` from the validated local graphs and reviewed deferrals.

**Exit gate:** each blueprint family/phase has a valid common-ID graph or explicit reviewed gap; graph-reference integrity, mapping completeness, gate coverage, and deterministic offline validation pass; no production activation is implied or enabled.

### Phase M5 — Knowledge and special skills

1. Add small, deterministic retrieval seeds with local provenance.
2. Review each proposed special skill independently for overlap, licensing, security, and compatibility.
3. Keep imported content as data; do not auto-approve tools or alter MCP/hook configuration.

**Exit gate:** all included assets are indexed locally and have an identified consumer; rejected assets remain absent.

### Phase M6 — Standalone verification

Implement `scripts/business/check_video_domain_standalone.py` and focused tests. The checker must:

- validate manifest hashes and reject paths escaping the project root;
- assert exactly 114 inventory, manifest, directory, source-map, and SPEC identities;
- validate workflow-role-map completeness: every documented workflow/phase role has exactly one reviewed common-ID, named-composite, or explicit-gap resolution with rationale and maturity/activation status;
- validate all local source references and required `SPEC.md` runtime-binding, typed-handoff, and critique information for implemented mappings;
- require substantive sections in every SPEC;
- validate workflow coverage and graph-reference integrity using only common `video.*` agents and allowed tools; require phase nodes, typed handoffs, lead/critic roles, finite budgets, bounded critique/refinement/rollback, quality/risk/human gates, and reviewed deferrals for any unimplemented required phase;
- assert `pack_spine.json` is the sole safe stub and is not counted as blueprint realization;
- reject primary dependencies on `generic-swarm-ops` or `va-agent-swarm`, production activation, credentials, live providers, and network requirements;
- run deterministically without network access and without reading either source repository.

**Exit gate:** deterministic `STANDALONE PASS` with both upstream paths unavailable.

### Phase M7 — Documentation, ownership, and evidence

1. Update `business/video/README.md` with local entry points and update policy.
2. Rewrite conflicting ownership statements in `adoption.md`.
3. Correct common product/path identity and as-built counts in `structure.md`.
4. Record commands, results, source/destination commits, manifest digest, mapping review, and residual risks in immutable evidence.
5. Change this document to `COMPLETE` only in the same change set as passing evidence.

**Exit gate:** docs match checked-in assets and tests; no completion claim relies on prose alone.
## 7. Automation contracts

### 7.1 `scripts/business/import_video_corpus.py`

```text
required args:
  --source-root <generic-swarm-ops/business/video/corpus>
  --source-commit <sha>
  --destination business/video/corpus
  --dry-run | --write

behavior:
  resolve and validate both roots
  reject traversal, escaping links, prohibited files, and undeclared collisions
  copy only the approved allow-list
  preserve provenance and compute SHA-256
  never delete destination files
  produce deterministic manifest and copy report
```

### 7.2 `scripts/business/build_video_agent_specs.py`

```text
required inputs:
  business/video/inventory.json
  business/video/agents/*/agent_spec.json
  business/video/AGENT_SOURCE_MAP.json
  business/video/WORKFLOW_ROLE_MAP.json
  business/video/corpus/MANIFEST.json

behavior:
  validate exactly 114 reviewed source mappings
  consume workflow-role mappings only to enrich implemented local runtime-binding and handoff/critique sections
  generate drafts only from local files
  preserve common IDs and runtime restrictions
  refuse missing, duplicate, ambiguous, unreviewed, or external primary refs
  support --dry-run and --write
```

### 7.3 `scripts/business/check_video_domain_standalone.py`

```text
exit 0 iff:
  corpus manifest integrity passes
  inventory/manifest/directories/source-map/SPECs agree at 114
  every documented workflow/phase role has exactly one human-reviewed common-ID, named-composite, or explicit-gap mapping with context, rationale, and maturity/activation state
  every required local reference exists beneath the project root
  every SPEC passes content, section, and implemented-role runtime-binding/handoff/critique checks
  every blueprint workflow family and required phase has a valid local graph or explicit reviewed deferral
  every graph uses valid common video.* agents and allowed tools and passes phase, typed-handoff, lead/critic, finite-budget, bounded-path, quality/risk/human-gate, and rollback validation
  pack_spine.json is the sole safe stub and is not counted as blueprint realization
  production activation, credential, live-provider, and network requirements are absent
  no source repository is accessed
```

All tools must emit concise machine-readable summaries and non-zero exit codes on failure. Dry-run behavior must be covered without network access.

---

## 8. Verification gates

Run focused checks from `C:\Project\common-agent-swarm-ops`:

```powershell
python scripts/business/check_video_domain_standalone.py
python -m pytest --tb=short -q backend/tests -k "video or domain or corpus" --maxfail=1
npm run sdd:check
npm run sync:check
npm test -- --silent
```

Where a project command differs, use the repository's locked environment and equivalent quiet mode. Do not run a live provider or transmit corpus content externally.

| Gate | Required evidence |
|---|---|
| Inventory and source-map identity | 114 common IDs agree across manifest, inventory, directories, source map, and specs. |
| Workflow-role mapping completeness | Every blueprint workflow/phase role has one reviewed existing `video.*` ID, named common-ID composite, or explicit gap, with rationale, status, and maturity/activation state. |
| Corpus integrity | File count, bytes, path, and SHA-256 match the destination manifest. |
| Local-reference and SPEC integrity | Every required source, workflow, prompt, rubric, process, and implemented-role runtime-binding/handoff/critique reference resolves locally. |
| Graph validity | Every blueprint family/phase has a local graph or reviewed gap; graphs use common IDs and allowed tools and validate phase nodes, typed handoffs, lead/critic roles, finite budgets, bounded critique/refinement/rollback, quality/risk/human gates, and references. |
| Security and no-activation proof | Traversal/symlink escapes, secrets, network access, broad tools, live providers, credentials, production activation, and silent activation are rejected; `pack_spine.json` remains the sole safe stub. |
| Offline proof | Deterministic checker/tests pass with source repositories unavailable and network disabled. |
| Documentation | As-built counts, ownership, stub status, mapping/graph maturity, and explicit gaps match the filesystem and executable checks. |

Passing tests are evidence, not proof. Unreviewed semantic or workflow-role mappings, licensing uncertainty, an uncovered workflow/phase, an invalid graph reference/gate/path, or any production-activation signal remains an explicit blocker.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong source-to-common or workflow-role mapping | Separate human-reviewed source and workflow-role maps; require phase context, rationale, exact-one resolution, and fail-closed ambiguity checks. |
| Missing blueprint phase or role is concealed by a catalog or stub | Workflow coverage ledger requires every documented family/phase to name a valid graph or explicit reviewed gap; `pack_spine.json` cannot count as realization. |
| Invalid or unsafe graph is treated as mature | Deterministic offline validation of common IDs, allowed tools, typed handoffs, lead/critic roles, finite budgets, bounded critique/refinement/rollback, gates, and references. |
| Common contract regression | Preserve common schemas, policies, IDs, and the safe stub workflow; adapt source assets rather than overwrite. |
| Repository growth | Record measured size and approved scope; deduplicate shared documents instead of copying them per agent. |
| Stale corpus | Pin source commit and hashes; updates use reviewed manifest-diff PRs. |
| Malicious or irrelevant instructions in corpus | Treat corpus as untrusted data; never execute embedded commands or generate active configuration from instructions. |
| License/provenance loss | Preserve metadata and headers; block import until review is recorded. |
| Secret or personal-data import | Pre-copy scanning and allow-list; no credentials or generated media. |
| False maturity or production claims | Keep all 114 agents registered/non-active; require mapping/graph gates and no-activation proof before any maturity claim. |
| Rollback complexity | Migration is additive; retain pre-import manifest digest and revert the migration change set rather than deleting ad hoc. |

---

## 10. Definition of done

The video domain is self-contained only when a clean clone of `common-agent-swarm-ops`, with no sibling repositories and no network access, can:

1. Explain every common video agent's responsibility and boundaries from local files.
2. Validate all 114 configurations and their reviewed local source mappings.
3. Read system, workflow, quality, rights, safety, and provenance design from the local pack.
4. Validate the complete human-reviewed workflow-role map: every documented workflow/phase role resolves exactly once to an existing common ID, named common-ID composite, or explicit reviewed gap.
5. Register or dry-run the pack through common host contracts without external content.
6. Deterministically validate every documented workflow family and required phase as a local common-ID graph or explicit reviewed deferral, including graph-reference integrity, typed handoffs, lead/critic roles, bounded paths, finite budgets, gates, and allowed tools.
7. Prove `pack_spine.json` remains the sole safe stub and that no provider, credential, network path, or production activation is configured or implied.
8. Recompute the corpus manifest and reproduce the standalone pass.

Self-contained does **not** mean all agents are active, all workflows are production-ready, or live media providers are configured. A workflow is not mature merely because individual agents are cataloged, a mapping exists, or a stub graph runs.

---

## 11. Out of scope

- Enabling credentials or credentialed MCP servers.
- Installing dependencies or running remote installers.
- Activating production media providers or removing human approval gates.
- Replacing common's host architecture with generic or VA host code.
- Treating imported research as executable instructions.
- Hand-editing generated Kiro or Claude Code output.
- Claiming workflow or production maturity based only on agent count, file count, copied prose, a role map, or a graph stub.
- Treating external VA/generic repositories as runtime/design dependencies or adding a second workflow engine or control plane.

---

## 12. Recommended next action

1. Review and approve the exact Phase M0 dry-run import set and provenance report.
2. Implement the import/check tooling before copying corpus files.
3. Import the pinned corpus snapshot.
4. Complete and review the 114-entry common-ID source mapping.
5. Complete and review the workflow-role map and coverage ledger for every blueprint workflow/phase role.
6. Generate/review specs, then realize graphs incrementally or record explicit reviewed deferrals.
7. Run M6 deterministic offline gates with both source repositories unavailable and no activation-capable configuration.
8. Reconcile `adoption.md` and `structure.md`; only then mark this migration complete.

Do not copy generic agent directories wholesale, retain “see another repository” as the permanent video-domain design, or present the safe stub as a realized workflow.

---

## 13. Traceability

| Concern | Local evidence / planned artifact |
|---|---|
| Current 114-agent authority | `business/video/manifest.json`, `business/video/inventory.json` |
| Common runtime restrictions | `business/video/agents/*/agent_spec.json` |
| Current safe graph | `business/video/workflows/pack_spine.json` — sole safe stub, not blueprint realization |
| Common safety contracts | `business/video/policies/`, `business/video/schemas/` |
| Migration requirements and acceptance criteria | This document §0 |
| Source provenance and integrity | Planned `business/video/corpus/MANIFEST.json` and `SOURCE_*` files |
| Source taxonomy reconciliation | Planned `AGENT_SOURCE_MAP.json`, `ROSTER.json`, and `MAP.md` |
| Workflow realization and role mapping | Planned `WORKFLOW_ROLE_MAP.json`, `workflow_coverage.json`, local graph definitions/explicit deferrals, and implemented-role `SPEC.md` bindings |
| Standalone proof | Planned checker, focused tests, deterministic offline graph validation, no-activation evidence, and immutable evidence record |
| Architecture/ownership reconciliation | This document and `docs/adoption_redesign/adoption_redesign.md`; future pack documentation updates when implementation is approved |

---

*End of migration plan v1.0. Status remains PROPOSED until the import, mapping, validation, and documentation gates are evidenced.*
