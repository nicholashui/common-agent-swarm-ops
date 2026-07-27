# Comparison report: which repo implements **va-agent-swarm** better?

**Report date:** 2026-07-27  
**Question:** Between **common-agent-swarm-ops** and **generic-swarm-ops**, which implements **va-agent-swarm** better—and on which aspects?

---

## Repos compared

| Repo | Path | Short SHA (measured) | Role vs VA |
|------|------|----------------------|------------|
| **VA (source)** | `C:\Project\va-agent-swarm` | `41fdbef` | Design corpus only (`study/`, `plan/`, materials). **No product host.** |
| **Generic** | `C:\Project\generic-swarm-ops` | `8f61e28` | First full migration of VA → video Domain Pack (`MIGRATION_COMPLETE.md`, 2026-07-13). |
| **Common** | `C:\Project\common-agent-swarm-ops` | `f3bb469` | Domain-neutral host + video/specials packs; VA taxonomy IDs; Registry UI; production media path. |

### Lineage

```text
va-agent-swarm  (design-only source of truth for roles, tables, DNA intent)
      │
      ▼
generic-swarm-ops   (first complete VA → Domain Pack migration)
      │
      ▼
common-agent-swarm-ops  (host + UI + specials + VA IDs + deep SPECs
                         + host DNA + production media adapters)
```

Both product repos implement VA **offline** (no need for `va-agent-swarm` on disk for pack design). They differ in **host/UI productization**, **specials**, and **live media production readiness**.

---

## 1. Executive scorecard (tables)

### 1.1 Overall winners by goal

| If your goal is… | Prefer | Why |
|------------------|--------|-----|
| Closest **first clone** of VA Domain Pack knowledge (historical migration record) | **generic-swarm-ops** | Original `MIGRATION_COMPLETE.md` (2026-07-13); native DNA shape; process index **33** rows |
| Closest **current** VA table IDs + deep SPECs + operate/govern + media path | **common-agent-swarm-ops** | Exact ID match **114/114**; SPEC avg ≥ generic; host gates; UI 133; specials 19; live media adapters |
| **Operate / browse / govern** VA-style agents | **common-agent-swarm-ops** | FastAPI host, isolation STANDALONE, Registry, production profile |
| Offline design **without** VA on disk | **Either** | Both ship full corpus + 114 SPECs + excerpts |
| Single daily repo after parity work | **common-agent-swarm-ops** | Content parity + stronger product shell |

### 1.2 Aspect winners (implementing VA)

| Aspect (for implementing VA) | Better repo | Why (measured / observed) |
|------------------------------|-------------|---------------------------|
| **Overall VA content pack (knowledge)** | **Tie** | Both: **114** agents, **~335** corpus files, deep SPECs, 14 DNA, 114 excerpts |
| **Overall product to run/browse/govern VA agents** | **Common** | Host validators, Registry UI (133), specials (19), fail-closed + production media path |
| Offline VA study/plan corpus | **Tie** | Both **335** files under `business/video/corpus/` |
| Agent count (video 114) | **Tie** | Both **114** folders |
| Agent IDs ≈ VA tables | **Tie** | Exact ID overlap gen↔com **114 / 114**; both carry `va_id` |
| SPEC depth | **Tie** (Common slight avg) | Common avg **~124,273 B**; Generic avg **~123,214 B**; Generic max still higher (**~566 KB** vs **~417 KB**) |
| SPEC native VA table shape | **Generic** (slight) | Native body as primary sections; Common wraps full body under Provenance + host Identity table |
| Workflow DNA A–J / LQR / e2e present | **Tie** | Both **14** `workflows/*.dna.json` |
| DNA as **host-validated** graphs | **Common** | `definition_type: pack_graph`, budgets, critique loops, human gates |
| DNA as **native VA/generic step DNA** | **Generic** | Original `steps` / `owner` / preconditions shape closer to design DNA |
| DNA **`production_ready: true`** | **Common** | Common **14/14 true**; Generic **all false** |
| Process coverage breadth (design index) | **Generic** (slight) | Generic **33** process rows; Common **27** host + **33** design catalog |
| Workflow-role map / coverage ledger | **Common** | `WORKFLOW_ROLE_MAP.json` + `workflow_coverage.json` present |
| Safe baseline spine graph | **Common** | `pack_spine.json` (Generic has no equivalent pack_spine) |
| Fail-closed host / isolation tests | **Common** | STANDALONE PASS with isolation claims; large pytest surface |
| UI: all agents + settings | **Common** | Generated catalog **133** (114 video + 19 specials) |
| Specials / meta agents | **Common** | **19** self-contained specials; Generic has **no** `business/specials` pack |
| Live media (Sora / Veo / Runway / ElevenLabs) | **Common** | Host adapters `media.sora|veo|runway|elevenlabs` + env credentials; Generic still stubs |
| Production activation path | **Common** | Pack `production/profile.json` enabled; media agents allow-listed; dual env flags |
| First complete VA migration record | **Generic** | Historical first DoD (2026-07-13) |
| Official redesign COMPLETE certificate (this host) | **Common** | `MIGRATION_COMPLETE.md` + redesign evidence (self-contained + production path) |

### 1.3 One-line verdict

| Dimension | Winner |
|-----------|--------|
| **VA knowledge fidelity (pack content)** | **Tie** |
| **VA naming / IDs** | **Tie** (114/114 match) |
| **VA process index (design rows)** | **Generic** slight |
| **Host runtime + governance of VA pack** | **Common** |
| **UI to explore all VA agents** | **Common** |
| **Production / live media** | **Common** |
| **Daily product for VA work** | **Common** |

---

## 2. Quantitative comparison

| Metric | va-agent-swarm | generic-swarm-ops | common-agent-swarm-ops |
|--------|----------------|-------------------|------------------------|
| Nature | Design docs | Product + video pack | Product + video + specials + production media |
| Video agents | Roles in `study/agents.md` | **114** folders | **114** folders |
| Exact agent-ID overlap gen↔com | n/a | — | **114 / 114** |
| `SPEC.md` count | n/a | **114** | **114** |
| SPEC average size | n/a | **~123,214 B** | **~124,273 B** |
| SPEC max size | n/a | **~566,370 B** | **~416,588 B** |
| Agent `sources/excerpts` | Design only | **114** | **114** |
| Study / corpus files | **277** under `study/` | **335** pack corpus | **335** pack corpus |
| Workflow DNA | Design SVG / process docs | **14** native DNA JSON | **14** host-adapted DNA JSON |
| DNA `production_ready` | n/a | **false** (14) | **true** (14) |
| Safe baseline graph | n/a | Spine DNA only | `pack_spine.json` + DNA graphs |
| Process coverage rows | Design PROCESSES | **33** | **27** host (+ 33 design catalog) |
| `WORKFLOW_ROLE_MAP.json` | n/a | No | **Yes** |
| graphs / tools / evals | Design | Yes | Yes |
| special_skills | In design | **17** skill dirs | **17** reviewed + specials pack |
| Specials redesign agents | Design set | **No** dedicated pack | **19** self-contained |
| Live media adapters (Sora/Veo/Runway/ElevenLabs) | No | Stubs (`video_media_gen_stub`) | **Yes** (`media.*` host adapters) |
| Production profile | n/a | No | **Yes** (`production/profile.json` enabled) |
| UI agent catalog | None | Frontend exists; weaker pack Registry | **133** exported for Registry |
| `MIGRATION_COMPLETE.md` | n/a | **Yes** (first pack DoD) | **Yes** (host redesign + production path) |
| Can develop offline without VA | n/a | **Yes** | **Yes** |

---

## 3. Aspect-by-aspect detail

### 3.1 Content & knowledge (VA fidelity)

| Sub-aspect | generic-swarm-ops | common-agent-swarm-ops | Better for VA content |
|------------|-------------------|------------------------|------------------------|
| Full study/plan corpus in pack | Yes | Yes | **Tie** |
| Corpus integrity / MANIFEST | Yes | Yes | **Tie** |
| 114 agent SPECs offline | Yes (deep native) | Yes (VA Identity + full generic body under Provenance) | **Tie** |
| Per-agent excerpts/study | Yes | Yes | **Tie** |
| External path independence | High | High | **Tie** |
| First migration completion artifact | **`MIGRATION_COMPLETE.md` (2026-07-13)** | Later closeout + host evidence | **Generic** (historical first) |

### 3.2 Agent model

| Sub-aspect | generic-swarm-ops | common-agent-swarm-ops | Better |
|------------|-------------------|------------------------|--------|
| 114 video agents | Yes | Yes | **Tie** |
| Taxonomy ≈ VA names | High (source pack IDs) | **Exact match** to generic/VA pack IDs | **Tie** |
| Self-contained folders | Yes | Yes | **Tie** |
| Fail-closed vs production-capable | Fail-closed L0 / stubs | Dual: fail-closed baseline + **production profile** | **Common** (more complete product ladder) |
| Specials / meta agents | special_skills data only | **19 specials** + special_skills | **Common** |

### 3.3 Workflows & process

| Sub-aspect | generic-swarm-ops | common-agent-swarm-ops | Better |
|------------|-------------------|------------------------|--------|
| A–J archetype workflows | DNA present | Host graphs present | **Tie** |
| DNA agent IDs | VA/generic taxonomy | **Same taxonomy** | **Tie** |
| Host graph contracts | DNA-shaped | pack_graph + budgets/critique/gates | **Common** |
| `production_ready` | false | **true** on DNA | **Common** |
| Process index rows | **33** | **27** host (+ design 33) | **Generic** / **Tie** |
| Role map + coverage ledger | Not present as host artifacts | **Present** | **Common** |
| Safe spine | Spine DNA | **`pack_spine.json`** | **Common** |

### 3.4 Platform / productization / media

| Sub-aspect | generic-swarm-ops | common-agent-swarm-ops | Better |
|------------|-------------------|------------------------|--------|
| Domain-neutral host | Strong Domain Pack host | Strong + redesign gates | **Common** |
| Isolation standalone | Corpus standalone gates | STANDALONE PASS (isolation flags) | **Common** |
| Frontend agent registry | Frontend exists | Full **133** + process stats | **Common** |
| Live media vendors | Design stubs | **Sora/Veo/Runway/ElevenLabs host adapters** | **Common** |
| Credentials model | Not productized as host media path | **Env-only** keys + dual enable flags | **Common** |
| Browser never holds secrets | n/a | Yes (UI claim fail-closed) | **Common** |

---

## 4. Strengths / gaps summary

### generic-swarm-ops — strengths

| Strength | Note |
|----------|------|
| First complete VA pack migration | `MIGRATION_COMPLETE.md` historical DoD |
| Native DNA + process index | 14 DNA + **33** process rows |
| Native deep SPECs | Full VA table sections as primary body |

### generic-swarm-ops — gaps vs Common

| Gap | Note |
|-----|------|
| Specials pack | No 19-agent specials pack |
| Host Registry of 133 agents | Weaker pack-agent settings export |
| Live media production path | Still stub tools |
| DNA production_ready | Remains false |
| Workflow-role map artifact | Not present as host redesign artifact |

### common-agent-swarm-ops — strengths

| Strength | Note |
|----------|------|
| VA IDs = generic pack IDs | **114/114** |
| SPEC depth | Avg ≥ generic |
| Host + UI + specials | Fail-closed host + 133 Registry + 19 specials |
| Process/role maps | Host + design coverage |
| Production media | Live adapters + profile + env credentials |
| DNA production_ready | **true** on 14 host DNA graphs |

### common-agent-swarm-ops — residual honesty

| Residual | Note |
|----------|------|
| Live calls still need operator secrets | Env keys not shipped; without keys adapters fail closed |
| Vendor API shapes may need endpoint overrides | `CASOPS_MEDIA_*_ENDPOINT` supported |
| SPEC section hierarchy | Full VA body often under Provenance fence (host validators) |
| Historical “first migration” | Generic still owns the original 2026-07-13 certificate |

---

## 5. Recommendation matrix

| Use case | Choose | Rationale |
|----------|--------|-----------|
| Audit original VA→pack migration history | **Generic** | First `MIGRATION_COMPLETE.md` |
| Implement/extend VA agents offline with maximum product tooling | **Common** | Host, UI, specials, maps, production media |
| Compare agent IDs to VA tables | **Either** | Same 114 IDs |
| Run live Sora/Veo/Runway/ElevenLabs from host | **Common** | Only Common has host adapters + production profile |
| Expand design process catalog | Prefer Generic process index as audit source | Broader design row naming historically |

---

## 6. Measurement notes

| Item | Method |
|------|--------|
| Agent folders | Directory count under `business/video/agents` |
| ID overlap | Sorted set equality of folder names |
| SPEC sizes | Byte length of each `SPEC.md` |
| Corpus | Recursive file count under `business/video/corpus` |
| DNA | `business/video/workflows/*.dna.json` + `production_ready` field |
| Process rows | `process_coverage.json` → `processes` length |
| SHAs | `git rev-parse --short HEAD` at report time |

**Not claimed:** perfect vendor SDK parity for every media API revision; production success without configuring secrets; absence of all latent defects outside automated gates.

---

## 7. Conclusion

| Question | Answer |
|----------|--------|
| Who implements **va-agent-swarm content** better? | **Tie** — both ship the VA Domain Pack (114 agents, corpus, DNA A–J family, deep SPECs, excerpts) offline. |
| Who implements **va-agent-swarm as a product** better? | **common-agent-swarm-ops** — host, UI, specials, maps, isolation, production media path. |
| Who was first pure VA pack migration? | **generic-swarm-ops** (historical). |
| Practical daily choice now | **common-agent-swarm-ops**. |

### Bottom line

**For almost every practical VA implementation goal today, common-agent-swarm-ops is better.**  
Generic remains the **original migration provenance** and still slightly leads on **native SPEC presentation** and **design process-row count (33)**. Common matches VA content and leads on **host, UI, specials, workflow maps, DNA production_ready, and live media**.

---

*End of report.*
