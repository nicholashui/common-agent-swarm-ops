# Migration Plan: self-contained video domain in common-agent-swarm-ops

**Version:** 1.0  
**Date:** 2026-07-20  
**Status:** **PROPOSED — NOT YET SELF-CONTAINED**  
**Destination:** `C:\Project\common-agent-swarm-ops`  
**Controlled source snapshot:** `C:\Project\generic-swarm-ops\business\video`  
**Original corpus provenance:** `va-agent-swarm` commit recorded by the source corpus manifest  
**Problem statement:** `common-agent-swarm-ops` has a safe 114-agent video catalog, policies, schemas, and one stub workflow, but it does not contain the operational/design corpus needed to understand and develop the video domain without another repository. The migration must make `business/video/` the checked-in video source of truth while preserving the common host's domain-neutral architecture and existing agent identities.

---

## 0. Requirements and acceptance criteria

### 0.1 Requirements

1. All video operational and design knowledge required for development must resolve inside `business/video/`.
2. The existing common 114-agent inventory and IDs remain authoritative; source agent IDs must not overwrite them.
3. Imported material retains its original repository, commit, path, license, and SHA-256 provenance.
4. Runtime activation remains fail-closed; migration does not enable providers, credentials, network access, or production agents.
5. The universal host remains domain-neutral. Video prompts, rubrics, workflows, policies, and knowledge stay pack-local.
6. Import and generation tools must support dry-run, reject path traversal, avoid deletion, and fail on incomplete mappings.
7. Generated Kiro and Claude Code configuration is out of scope; do not place the video corpus in `.kiro/`, `.claude/`, `rules/`, or `skills/`.

### 0.2 Acceptance criteria

The migration is complete only when all of the following are evidenced:

- Exactly 114 common inventory entries resolve to existing `agent_spec.json` and substantive local `SPEC.md` files.
- Every `SPEC.md` contains identity, responsibility, boundaries, quality/critique behavior, runtime binding, local sources, and provenance.
- Every required `source_ref` resolves beneath the common repository root; external paths may appear only as non-required historical provenance.
- A corpus manifest verifies every imported file by relative path, size, and SHA-256.
- Required workflows, process indexes, knowledge seeds, and approved special-skill integrations are local and reference common agent IDs.
- The standalone checker passes when both `generic-swarm-ops` and `va-agent-swarm` are unavailable.
- Focused video inventory, schema, workflow, security, and SDD gates pass.
- `adoption.md`, `structure.md`, and the pack README describe the checked-in common pack as the video source of truth and do not claim assets that are absent.

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
| D | Adapted workflows, process indexes, knowledge seeds, and compatible special skills | Makes local knowledge navigable and operationally connected. |

The completion bar is A–D. A copied corpus alone is not sufficient.

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

### 5.2 Per-agent SPEC.md target shape

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

1. Generate mapping candidates from common IDs/roles and source tables.
2. Human-review all exact, composite, related, and common-only mappings.
3. Write `AGENT_SOURCE_MAP.json`, `ROSTER.json`, and `MAP.md` using common IDs.
4. Fail closed if the common inventory and map differ by any ID.

**Exit gate:** 114 reviewed common entries, no duplicate common IDs, no silent source substitution.

### Phase M3 — Expand local common agent specifications

1. Generate draft `SPEC.md` files from each common `agent_spec.json`, reviewed mapping, and local corpus sources.
2. Preserve common budgets, model policy, network restrictions, critique edges, refinement limits, and non-active status.
3. Add local deep-document links and provenance.
4. Review safety-critical roles manually: orchestrator, compliance, rights/consent, privacy, legal, safety, provenance, release, judge, and human-review coordination.

**Exit gate:** 114 substantive specs; all local links resolve; no required external source path.

### Phase M4 — Adapt workflows and process coverage

1. Keep `pack_spine.json` as the current safe baseline.
2. Adapt selected source DNA one workflow at a time to common IDs and schemas.
3. Require allow-listed tools, finite graph budgets, risk gates, compensation, critique loops, and human interrupts.
4. Build `PROCESSES.md` and `process_coverage.json` from validated local workflows.

**Exit gate:** workflow references are valid common agents/tools; graph and security checks pass; no production activation is implied.

### Phase M5 — Knowledge and special skills

1. Add small, deterministic retrieval seeds with local provenance.
2. Review each proposed special skill independently for overlap, licensing, security, and compatibility.
3. Keep imported content as data; do not auto-approve tools or alter MCP/hook configuration.

**Exit gate:** all included assets are indexed locally and have an identified consumer; rejected assets remain absent.

### Phase M6 — Standalone verification

Implement `scripts/business/check_video_domain_standalone.py` and focused tests. The checker must:

- validate manifest hashes and reject paths escaping the project root;
- assert exactly 114 inventory, manifest, directory, mapping, and SPEC identities;
- validate all local source references;
- require substantive sections in every SPEC;
- validate workflow agent/tool references and process coverage;
- reject primary dependencies on `generic-swarm-ops` or `va-agent-swarm`;
- run without network access and without reading either source repository.

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
  business/video/corpus/MANIFEST.json

behavior:
  validate exactly 114 reviewed mappings
  generate drafts only from local files
  preserve common IDs and runtime restrictions
  refuse missing, duplicate, ambiguous, or external primary refs
  support --dry-run and --write
```

### 7.3 `scripts/business/check_video_domain_standalone.py`

```text
exit 0 iff:
  corpus manifest integrity passes
  inventory/manifest/directories/map/SPECs agree at 114
  every required local reference exists beneath the project root
  every SPEC passes content and section checks
  every workflow references valid common agents and allowed tools
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
| Inventory identity | 114 common IDs agree across manifest, inventory, directories, mapping, and specs. |
| Corpus integrity | File count, bytes, path, and SHA-256 match the destination manifest. |
| Local-reference integrity | Every required source, workflow, prompt, rubric, and process reference resolves locally. |
| Security | Traversal/symlink escapes, secrets, network access, broad tools, and silent activation are rejected. |
| Workflow validity | Common agent IDs, finite budgets, allow-listed tools, risk gates, and human interrupts validate. |
| Offline proof | Checker/tests pass with source repositories unavailable and network disabled. |
| Documentation | As-built counts and ownership statements match the filesystem and executable checks. |

Passing tests are evidence, not proof. Unreviewed semantic mappings, licensing uncertainty, or incomplete workflow adaptation remain explicit blockers.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong agent mapping | Human-reviewed mapping statuses and rationale; fail closed on ambiguity. |
| Common contract regression | Preserve common schemas, policies, IDs, and safe stub workflow; adapt source assets rather than overwrite. |
| Repository growth | Record measured size and approved scope; deduplicate shared documents instead of copying them per agent. |
| Stale corpus | Pin source commit and hashes; updates use reviewed manifest-diff PRs. |
| Malicious or irrelevant instructions in corpus | Treat corpus as untrusted data; never execute embedded commands or generate active configuration from instructions. |
| License/provenance loss | Preserve metadata and headers; block import until review is recorded. |
| Secret or personal-data import | Pre-copy scanning and allow-list; no credentials or generated media. |
| False N3/production claims | Keep maturity and activation unchanged until separate runtime evidence exists. |
| Rollback complexity | Migration is additive; retain pre-import manifest digest and revert the migration change set rather than deleting ad hoc. |

---

## 10. Definition of done

The video domain is self-contained only when a clean clone of `common-agent-swarm-ops`, with no sibling repositories and no network access, can:

1. Explain every common video agent's responsibility and boundaries from local files.
2. Validate all 114 configurations and their local source mappings.
3. Read system, workflow, quality, rights, safety, and provenance design from the local pack.
4. Register or dry-run the pack through common host contracts without external content.
5. Validate local workflow/process references and execute only existing safe stub paths.
6. Recompute the corpus manifest and reproduce the standalone pass.

Self-contained does **not** mean all agents are active, all workflows are production-ready, or live media providers are configured.

---

## 11. Out of scope

- Enabling credentials or credentialed MCP servers.
- Installing dependencies or running remote installers.
- Activating production media providers or removing human approval gates.
- Replacing common's host architecture with generic or VA host code.
- Treating imported research as executable instructions.
- Hand-editing generated Kiro or Claude Code output.
- Claiming production maturity based only on agent count, file count, or copied prose.

---

## 12. Recommended next action

1. Review and approve the exact Phase M0 dry-run import set and provenance report.
2. Implement the import/check tooling before copying corpus files.
3. Import the pinned corpus snapshot.
4. Complete and review the 114-entry common-ID mapping.
5. Generate/review specs, then adapt workflows incrementally.
6. Run M6 gates with both source repositories unavailable.
7. Reconcile `adoption.md` and `structure.md`; only then mark this migration complete.

Do not copy generic agent directories wholesale and do not retain “see another repository” as the permanent video-domain design.

---

## 13. Traceability

| Concern | Local evidence / planned artifact |
|---|---|
| Current 114-agent authority | `business/video/manifest.json`, `business/video/inventory.json` |
| Common runtime restrictions | `business/video/agents/*/agent_spec.json` |
| Current safe graph | `business/video/workflows/pack_spine.json` |
| Common safety contracts | `business/video/policies/`, `business/video/schemas/` |
| Migration requirements and acceptance criteria | This document §0 |
| Source provenance and integrity | Planned `business/video/corpus/MANIFEST.json` and `SOURCE_*` files |
| Taxonomy reconciliation | Planned `AGENT_SOURCE_MAP.json`, `ROSTER.json`, and `MAP.md` |
| Standalone proof | Planned checker, focused tests, and evidence record |
| Architecture/ownership reconciliation | Planned updates to `adoption.md`, `structure.md`, and pack README |

---

*End of migration plan v1.0. Status remains PROPOSED until the import, mapping, validation, and documentation gates are evidenced.*
