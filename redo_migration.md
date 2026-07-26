# Redo Migration Plan: self-contained video agents in common-agent-swarm-ops

**Version:** 2.0  
**Date:** 2026-07-26  
**Status:** **AGENT PHASE COMPLETE** (self-contained 114 agents; pack corpus not required)  
**Destination host:** `C:\Project\common-agent-swarm-ops`  
**Primary controlled source (already migrated pack):** `C:\Project\generic-swarm-ops`  
**Original design corpus (historical upstream):** `C:\Project\va-agent-swarm`  
**Related plans:** `migration.md` (common pack ownership), `docs/migration_redesign/migration_redesign.md` (workflow/blueprint gates)

### Execution evidence (agent phase)

| Item | Result |
|------|--------|
| Common SHA (at write) | `5460c4b4a33c15286f9fd84b1bc764d755f5bab0` |
| Generic SHA (enrichment) | `8f61e2889fb5a750cc24ee319e7e6a655c0f02f5` |
| VA SHA (provenance) | `41fdbef87a2b5fe63a960b3bd5242a98081b04db` |
| `AGENT_SOURCE_MAP.json` | 114 reviewed entries |
| `SPEC.md` | 114 / 114 |
| `README.md` + `sources/` per agent | Present |
| Pack `corpus/` | **Absent (not required)** |
| `python scripts/business/build_common_video_agent_folders.py --write` | pass |
| `python scripts/business/check_common_video_agents_standalone.py` | `AGENTS STANDALONE PASS` |
| `python scripts/business/check_video_domain_standalone.py --network-disabled --upstreams-unavailable` | `STANDALONE PASS` |
| Deferred | Workflow DNA A–J, knowledge seeds, special skills, pack corpus |

---

## 0. Lineage (what “original migration” was)

| Stage | Path | What it produced | Status |
|-------|------|------------------|--------|
| **Original migration** | `va-agent-swarm` → `generic-swarm-ops` | Full video Domain Pack: 114 agents with **self-contained folders**, shared `corpus/`, DNA workflows, provenance | **COMPLETE** in generic (see generic `redo_migration.md` / `MIGRATION_COMPLETE.md` history) |
| **This redo** | generic (+ optional va excerpts) → **`common-agent-swarm-ops`** | Make the **common** video pack usable without external repos, under **common agent IDs** and host contracts | **THIS DOCUMENT** |

The original plan (`redo_migration.md` v1.x in generic lineage) treated a shared **`business/video/corpus/`** tree as the pack knowledge SoT and then linked SPECs into it.

### 0.1 Policy change for this redo (mandatory)

| Topic | Original (va → generic) | **This redo (→ common)** |
|-------|-------------------------|---------------------------|
| Shared pack `corpus/` | Required Tier C end state | **Not required for implementation.** Do **not** block completion on copying 300+ corpus files into common. |
| Agent knowledge | SPEC + optional links into `corpus/study/...` | **Each agent is self-contained under `agents/<common_agent_id>/`.** Role text, quality, tools design, and any excerpts live **in that folder**. |
| Shared pack corpus | SoT for offline design | Optional later convenience only; **not** an acceptance gate. Prefer per-agent `sources/` over a monorepo dump. |
| Agent IDs | generic taxonomy (`video.director`, `video.creativedirector`, …) | **Common inventory IDs only** (`video.creative_director`, `video.orchestrator`, …). Do not overwrite common directories with generic folder names. |

**Non-negotiable outcome:** a developer can open **one** agent directory under `business/video/agents/<id>/` and understand/run-design that agent without opening `va-agent-swarm`, `generic-swarm-ops`, or a pack-level `corpus/` tree.

---

## 1. Problem statement

`common-agent-swarm-ops` already has:

- 114 **common-taxonomy** agent directories with `agent_spec.json`
- Pack `manifest.json`, `inventory.json`, policies, schemas
- Safe stub workflow only: `workflows/pack_spine.json`

It **does not** have:

- Any `SPEC.md` (0/114 measured 2026-07-26)
- Per-agent `sources/`, prompts, rubrics, or README
- Adapted DNA workflows A–J (only pack spine stub)
- Shared corpus (and **must not require** one to declare migration complete)

`generic-swarm-ops` has the **completed** va→generic migration result and is the preferred content source for distillation:

- 114 self-contained agent folders (`SPEC.md`, `agent_spec.json`, `README.md`, `prompts/`, `rubrics/`, `sources/…`)
- Shared `corpus/` (usable as **read-only input**, not a required common destination)
- 14 workflow DNA files (IDs need remapping)

Exact agent-id overlap between common and generic is **~3 of 114**. Equal counts are **not** semantic equivalence. Mapping is mandatory.

---

## 2. Requirements and acceptance criteria

### 2.1 Requirements

1. **Common IDs authoritative.** Preserve all 114 `business/video/agents/*/agent_spec.json` identities from `inventory.json`. Never replace common dirs with generic folder names.
2. **Self-contained agents.** Every agent folder must stand alone (see §4 layout). No *required* primary content path outside that folder (and pack policies/schemas at pack root).
3. **No corpus implementation gate.** Pack-level `business/video/corpus/` is **out of scope for completion**. Import scripts may read generic/va corpus as **sources** while building per-agent folders; they must not treat a destination corpus tree as DoD.
4. **Provenance retained** on distilled content (original repo, commit, path) inside each agent folder (e.g. SPEC provenance section and/or `sources/PROVENANCE.json`).
5. **Fail-closed runtime.** Migration does not enable providers, credentials, network access, or production activation. Keep `status: registered`, local deterministic model policy, empty/allow-listed tools only as already defined.
6. **Host stays domain-neutral.** Video knowledge stays under `business/video/`. Do not dump corpus into `.kiro/`, `.claude/`, `rules/`, or host `skills/`.
7. **Dry-run, no traversal, no silent delete.** Import/generate tools support `--dry-run`, reject `..` / absolute escapes, never delete existing common contracts without explicit approve.
8. **Workflow adaptation is separate maturity.** Self-contained agents can complete without full A–J DNA; `pack_spine.json` remains the only safe stub until workflow phases pass their own gates (`migration.md` / redesign).

### 2.2 Acceptance criteria (agent-self-contained complete)

Migration **agent phase** is complete only when all of the following are evidenced **inside this repo alone**:

| # | Criterion |
|---|-----------|
| A1 | Exactly 114 inventory entries; each directory exists; each has `agent_spec.json`. |
| A2 | Each agent directory has substantive **`SPEC.md`** (identity, responsibility, boundaries, quality/critique, runtime binding, local sources, provenance). |
| A3 | Each agent directory has **`README.md`** listing folder contents and how to use the agent offline. |
| A4 | Each agent directory has **`sources/`** with at least one of: distilled excerpts, mapping note, or provenance index that makes the SPEC claims auditable **without** a pack corpus. |
| A5 | Optional but recommended when material exists: `prompts/`, `rubrics/` (may be `.gitkeep` + stub if host still uses prompt_reference only). |
| A6 | **Zero required** references to `C:\Project\va-agent-swarm`, `C:\Project\generic-swarm-ops`, or pack `corpus/` as primary content in `SPEC.md` (historical provenance footnotes OK). |
| A7 | Human-reviewed **`AGENT_SOURCE_MAP.json`**: 114 common IDs → source agent id(s) and/or va table rows (`exact|composite|related|common_only`). |
| A8 | Standalone checker passes with **both** source trees unavailable (or mocked absent): agents-only rules; **must not** require `business/video/corpus/`. |
| A9 | Focused inventory/schema/security tests still pass; no production activation. |
| A10 | Pack README states: agents are self-contained; corpus is not required; upstream repos are optional update inputs only. |

**Explicitly not required for this redo’s agent completion bar:**

- `business/video/corpus/**` present or complete  
- 14 DNA workflows adapted  
- Knowledge seeds / special_skills import  
- Media provider wiring  

Those remain later phases (see §8).

---

## 3. Measured baseline (2026-07-26)

### 3.1 Destination — common-agent-swarm-ops

| Asset | State |
|-------|--------|
| Root | `C:\Project\common-agent-swarm-ops` @ `5460c4b4…` (record at execution) |
| `business/video/agents/` | **114** directories (common taxonomy) |
| `agent_spec.json` | **114** registered, non-active, local deterministic, no network |
| `SPEC.md` | **0 / 114** |
| Per-agent `sources/`, `README.md`, prompts, rubrics | **Absent** |
| Workflows | `pack_spine.json` only |
| Pack corpus | **Absent** (and not required) |
| Policies / schemas / inventory / manifest | Present — preserve |

Example common ID shape: `video.creative_director`, `video.orchestrator`, `video.accessibility_qc_reviewer`.

### 3.2 Primary source — generic-swarm-ops

| Asset | State |
|-------|--------|
| Root | `C:\Project\generic-swarm-ops` @ `8f61e288…` (record at execution) |
| `business/video/agents/` | **114** self-contained folders |
| Per agent | `SPEC.md`, `agent_spec.json`, `README.md`, `prompts/`, `rubrics/`, `sources/{excerpts,study}/…` |
| Pack corpus | Present (~335 files) — **read input only** for this redo |
| Workflow DNA | 14 `*.dna.json` — later phase |

Example generic ID shape: `video.creativedirector`, `video.director`, `video.distributor`.

**Generic self-contained agent pattern (copy the *shape*, not the IDs):**

```text
business/video/agents/video.director/
  README.md
  SPEC.md                 # full embedded definition
  agent_spec.json
  prompts/                # may be .gitkeep until host binds
  rubrics/
  sources/
    excerpts/             # focused docs used by this agent
    study/                # related study slices (not full corpus dump)
```

### 3.3 Historical upstream — va-agent-swarm

| Asset | State |
|-------|--------|
| Root | `C:\Project\va-agent-swarm` @ `41fdbef8…` (record at execution) |
| `study/agents.md` | Authoritative 114-agent tables (original) |
| `study/*` workflows, SYSTEM_REFERENCE, deep specs | Design knowledge |

Use va when generic SPEC/sources are thin or mapping needs original table text. Prefer generic (already distilled) when content is already self-contained.

### 3.4 ID compatibility

| Metric (measured 2026-07-26) | Value |
|------------------------------|-------|
| Common agent dirs | 114 |
| Generic agent dirs | 114 |
| Exact folder-name overlap | **~3** |
| Implication | **Semantic map required**; never bulk-rename common agents to generic names |

---

## 4. Target state (common) — agent-first, no corpus DoD

```text
business/video/
  README.md
  manifest.json                 # preserve
  inventory.json                # preserve (common IDs)
  AGENT_SOURCE_MAP.json         # NEW: common_id → source id(s) + rationale
  ROSTER.json                   # optional convenience index of common IDs
  MAP.md                        # human-readable mapping summary
  agents/<common_agent_id>/     # 114 — EACH SELF-CONTAINED
    README.md
    SPEC.md                     # substantive, local, common ID
    agent_spec.json             # preserved common runtime contract (enrich only)
    prompts/                    # optional stubs or distilled prompts
    rubrics/                    # optional stubs or distilled rubrics
    sources/
      PROVENANCE.json           # commits/paths used for this agent
      excerpts/                 # only what this agent needs
      study/                    # optional focused study slices for this agent
  workflows/
    pack_spine.json             # keep as sole safe stub until workflow phase
  policies/                     # preserve
  schemas/                      # preserve

  # NOT required for agent-phase completion:
  # corpus/   ← deliberately omitted from DoD
  # knowledge/seeds/  ← later
  # special_skills/   ← later
```

### 4.1 Per-agent folder contract (self-contained)

Every `agents/<common_agent_id>/` MUST satisfy:

| File / dir | Required | Rule |
|------------|----------|------|
| `agent_spec.json` | Yes | Keep common schema fields; do not flip to production_active; keep network_access false unless a later approved change. |
| `SPEC.md` | Yes | Full role definition for **this** common ID; embed distilled responsibility/quality/tools/patterns; no required external open. |
| `README.md` | Yes | One-screen index of the folder; offline usage. |
| `sources/` | Yes | At least provenance + enough excerpts that SPEC claims are auditable offline. Prefer **small, role-relevant** copies over whole-corpus clones. |
| `prompts/` | Recommended | May start as `.gitkeep` if only `prompt_reference` exists on host. |
| `rubrics/` | Recommended | Same as prompts. |

**Anti-patterns (reject):**

- SPEC that only says “see `generic-swarm-ops/...`” or “see `va-agent-swarm/study/agents.md`”
- SPEC that only says “see `business/video/corpus/...`” as the sole body of knowledge
- Copying entire generic `sources/study` tree into **every** agent (bloat); share only when a slice is truly needed, or put a short excerpt under that agent
- Replacing common `agent_id` values with generic pack ids

### 4.2 SPEC.md target shape (common)

```markdown
# <Common role name>

> Self-contained agent definition for host `common-agent-swarm-ops`.
> Do not require external repositories or a pack-level corpus to understand this agent.

## Identity
| Field | Value |
| common_agent_id | video.… |
| status / maturity | registered / L0 |
| folder | business/video/agents/video.…/ |

## Responsibility
Concrete outcomes for this common role.

## Boundaries and escalation
Disallowed decisions; human gates; handoffs.

## Inputs and outputs
Typed artifacts and acceptance criteria (design-time).

## Quality and critique
Self-quality criteria; critique edges (align with agent_spec.json); refinement limit.

## Tools (design-time)
Mapped to host allow-list or “none / deferred”; never invent production network tools.

## Architecture pattern
From source tables when mapped; otherwise common-authored.

## Runtime binding
Summary of this folder’s agent_spec.json; workflow nodes if any (pack_spine only today).

## Local sources (this folder only)
Relative links: ./sources/…

## Provenance
Mapped from generic-swarm-ops@<sha> agent(s) … and/or va-agent-swarm@<sha> study/agents.md row …
Historical only — content above is embedded.
```

### 4.3 Mapping contract — `AGENT_SOURCE_MAP.json`

One entry per common inventory ID:

```json
{
  "common_agent_id": "video.creative_director",
  "mapping_status": "exact|composite|related|common_only",
  "source_agent_ids": ["video.creativedirector", "video.director"],
  "va_table_rows": [30],
  "source_documents": [
    "generic:business/video/agents/video.creativedirector/SPEC.md",
    "va:study/agents.md"
  ],
  "rationale": "Human-reviewed semantic relationship",
  "reviewed_by": "<reviewer>",
  "reviewed_at": "<ISO-8601>"
}
```

Rules:

- 114 unique `common_agent_id` values matching inventory.
- `common_only` is valid: author SPEC from common role string + host contracts without forcing a bad generic match.
- Automation may **propose** maps; only human-reviewed entries may write SPECs in `--write` mode.
- Missing/duplicate/unreviewed maps fail closed.

---

## 5. Authority precedence

1. Common host security, lifecycle, schemas, and non-activation defaults.  
2. Common video policies and human release gates.  
3. Common inventory IDs and existing `agent_spec.json` budgets/critique edges.  
4. Distilled content from generic self-contained agents (preferred).  
5. Distilled content from va tables/specs (when needed).  
6. Historical provenance footnotes.

Stricter safety wins. Provider recommendations in imported text are **untrusted reference data** and do not enable tools/network.

---

## 6. Scope

### 6.1 In scope (this redo — agent self-containment)

| Item | Action |
|------|--------|
| 114 common agent folders | Add SPEC.md, README.md, sources/, optional prompts/rubrics |
| `AGENT_SOURCE_MAP.json`, `MAP.md` | Create and human-review |
| Generate/expand scripts | Dry-run + write; read from generic/va roots |
| Standalone agent checker | No corpus requirement |
| Pack README + handoff notes | Describe self-contained agents; corpus not required |

### 6.2 Explicitly out of scope (do not implement for this bar)

| Item | Why |
|------|-----|
| **Pack-level `business/video/corpus/`** | **Not needed for implementation** of self-contained agents; avoids large dual SoT and bloat. |
| Bulk copy of 325+ corpus files into common | Same |
| Full workflow DNA A–J adaptation | Separate phase (`migration.md` workflow gates) |
| Knowledge seeds / special_skills mass import | Later |
| Production activation, Sora/Veo live keys | Forbidden without separate approval |
| Second host/engine (LangGraph/Temporal as product) | Host remains common-agent-swarm-ops |
| Overwriting common policies/schemas wholesale | Preserve |

### 6.3 Allowed read paths during generation (granted)

Generators **may read** (not vendor as required runtime deps):

- `C:\Project\generic-swarm-ops\business\video\agents\**`
- `C:\Project\generic-swarm-ops\business\video\corpus\**` (optional excerpts only)
- `C:\Project\va-agent-swarm\study\**`, `plan\**`, selected root docs

Generators **write only** under:

- `C:\Project\common-agent-swarm-ops\business\video\agents\**`
- mapping/docs at `business/video/` root as listed in §4

---

## 7. Phased execution

### Phase R0 — Freeze & inventory (0.5 day)

1. Record SHAs:
   - `git -C C:\Project\va-agent-swarm rev-parse HEAD`
   - `git -C C:\Project\generic-swarm-ops rev-parse HEAD`
   - `git -C C:\Project\common-agent-swarm-ops rev-parse HEAD`
2. Export common inventory agent_id list (114).
3. Export generic agent_id list (114).
4. Produce **candidate** map (name normalize, role fuzzy) — **unreviewed**.
5. Dry-run report: which common agents have exact/related/common_only proposals.

**Exit:** frozen SHAs; candidate map artifact; no writes.

### Phase R1 — Human-reviewed mapping (1–2 days)

1. Review all 114 rows into `AGENT_SOURCE_MAP.json` + `MAP.md`.
2. Flag safety-critical roles for extra review: orchestrator, compliance, rights/consent, privacy, legal, safety, provenance, release, judge, human-review coordination.
3. Fail closed on unmapped inventory IDs.

**Exit:** 114 reviewed entries; map IDs == inventory IDs.

### Phase R2 — Build self-contained agent folders (2–4 days)

For each common agent:

1. Preserve `agent_spec.json` (only enrich non-authority metadata if needed).
2. Generate `SPEC.md` from:
   - common `agent_spec.json` + inventory role
   - mapped generic `SPEC.md` / sources (preferred)
   - va `agents.md` row and deep specs when mapped
3. Write `README.md`.
4. Populate `sources/PROVENANCE.json` + **minimal** excerpts (role-relevant only).
5. Ensure `prompts/` and `rubrics/` exist (stubs OK).

Script sketch: `scripts/business/build_common_video_agent_folders.py`

```text
args:
  --common-root C:\Project\common-agent-swarm-ops
  --generic-root C:\Project\generic-swarm-ops
  --va-root C:\Project\va-agent-swarm          # optional if map needs it
  --map business/video/AGENT_SOURCE_MAP.json
  --dry-run | --write
  --agent-id video.creative_director           # optional single-agent
behavior:
  never delete agent_spec.json
  never require writing business/video/corpus/
  embed text into SPEC.md; copy only focused sources/*
  fail if map entry missing or unreviewed
```

**Exit:** 114 folders meet §4.1; greps show no required external primary refs.

### Phase R3 — Standalone verification (0.5–1 day)

Implement `scripts/business/check_common_video_agents_standalone.py`:

```text
exit 0 iff:
  inventory count == 114
  each agent has agent_spec.json, SPEC.md (min sections), README.md, sources/
  AGENT_SOURCE_MAP covers all inventory ids
  no SPEC primary-depends on va-agent-swarm|generic-swarm-ops|business/video/corpus absolute paths
  DOES NOT require business/video/corpus to exist
  agent_spec still non-active / network_access false (or pack policy equivalent)
```

Offline smoke: rename/hide access to source roots and re-run checker + open 10 random agent folders.

**Exit:** `STANDALONE AGENTS PASS`.

### Phase R4 — Docs & status (0.5 day)

1. Update `business/video/README.md`: self-contained agents; corpus not required.  
2. Align `migration.md` / adoption notes so they do not claim corpus or DNA assets that are absent.  
3. Set this document to **COMPLETE** only with evidence (commands + digests).  
4. Leave workflow DNA and pack corpus as **explicitly deferred**.

---

## 8. Deferred phases (after agents self-contained)

| Phase | Work | Depends on |
|-------|------|------------|
| W1 | Adapt selected DNA workflows to common IDs | Agents + map stable |
| W2 | Process coverage / blueprint role maps | Redesign migration gates |
| K1 | Optional small knowledge seeds (not full corpus tree) | Retrieval product need |
| S1 | Special skills one-by-one security review | Explicit approval |

Optional pack `corpus/` may be added later for human browsing; it must **never** become the only place agent knowledge lives. Agents remain self-contained.

---

## 9. Automation contracts

### 9.1 `build_common_video_agent_folders.py`

- Reads map + generic/va  
- Writes only under common `business/video/agents/<id>/` and map docs  
- `--dry-run` default-safe  
- No pack corpus destination  

### 9.2 `check_common_video_agents_standalone.py`

- Agents-only DoD (§2.2)  
- **Must not** fail solely because `corpus/` is missing  

### 9.3 Do **not** implement for this redo

- `import_video_corpus.py` as a completion blocker  
- Any gate that requires `MANIFEST.json` under pack corpus  

(If a corpus import script exists for optional later use, keep it **optional** and unlinked from agent DoD.)

---

## 10. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Wrong ID mapping | Human-reviewed map; composite/common_only allowed; fail closed |
| Repo bloat from full sources per agent | Cap excerpts; prefer embedded SPEC paragraphs over multi-MB clones |
| Dual SoT with generic | Common pack becomes SoT for common IDs after R3; upstream optional |
| Safety text enabling tools | agent_spec remains allow-list empty / local; SPEC tools are design-time only |
| Claiming workflow completeness | pack_spine only; docs forbid “14 workflows done” until W-phases |
| Corpus regression pressure | This plan v2 explicitly drops corpus from DoD |

---

## 11. Success criteria (redo complete — agent phase)

1. `C:\Project\va-agent-swarm` and `C:\Project\generic-swarm-ops` can be unmounted and every common agent folder still explains itself.  
2. **No pack-level corpus is required** to develop or validate agents.  
3. 114 self-contained agent folders under common taxonomy.  
4. Map + standalone checker green; inventory still 114 registered L0.  
5. Runtime remains fail-closed.

---

## 12. Recommended next actions

1. Approve this **v2.0** policy (self-contained agents; **no corpus implementation requirement**).  
2. Run Phase R0 SHA freeze + candidate map dry-run.  
3. Complete human map (R1).  
4. Generate agent folders (R2) and standalone check (R3).  
5. Only then schedule workflow DNA adaptation as a separate workstream.

---

## 13. Traceability

| Concern | Location |
|---------|----------|
| This redo plan | `redo_migration.md` (this file, v2.0) |
| Broader pack/workflow migration | `migration.md`, `docs/migration_redesign/migration_redesign.md` |
| Original va→generic migration (historical) | generic-swarm-ops `redo_migration.md` / `MIGRATION_COMPLETE.md` / `migration_plan.md` |
| Source (completed pack) | `C:\Project\generic-swarm-ops` |
| Source (original design corpus) | `C:\Project\va-agent-swarm` |
| Destination | `C:\Project\common-agent-swarm-ops\business\video\` |

---

## 14. Changelog

| Version | Date | Notes |
|---------|------|-------|
| 1.x | 2026-07-13 | Original plan: va-agent-swarm → generic-swarm-ops with **shared corpus** Tier C as SoT |
| **2.0** | **2026-07-26** | **Redo for common-agent-swarm-ops:** corpus **not** required; each agent **self-contained** in its folder; sources generic + va granted read access; common IDs preserved |

---

*End of redo migration plan v2.0 — execute only after explicit GO on phases R0+.*
