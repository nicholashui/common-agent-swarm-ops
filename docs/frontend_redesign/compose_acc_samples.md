# Compose ACC — sample requirements (reference)

**In the UI:** open **`/composer`** → section **Sample requirements (load into UI)** → **Load** or **Load + AI plan**.  
Source list: `frontend/src/lib/projections/composer-landing.ts` (`COMPOSER_SAMPLES`).

You can also paste the bodies below manually. Flow: **AI plan** → diagram → **Accept AI → Canvas**.

**Product rules**

- Human supplies **requirements / short spec** only.
- AI binds **available catalog agents** (closed world).
- Human only if **needs_hitl** (conflicts / missing capability).
- Output: crew **workflow diagram** + draft swarm (fail-closed).

---

## Sample A — YouTube wuxia short (happy path)

**Paste into Compose**

```text
Wuxia short for YouTube:
- 90s cinematic opening + strong hook in first 3 seconds
- verification loop before publish
- social cut + captions
- mid-tier cost band
Domain: video production
```

| Expect | Detail |
|--------|--------|
| Decision | `ai_resolved` (no HITL) |
| Pattern bias | Hierarchical + verification |
| Likely core | `video.orchestrator`, `video.planner` |
| Likely craft | screenwriter / director / editor (+ a11y or sound) |
| Gate | judge / gate-style agent when available |
| Next | Accept AI → Canvas |

---

## Sample B — Market intelligence + quality gate

**Paste**

```text
Build a daily market intelligence swarm with a report-quality verification loop.
Prefer parallel research branches, then a final critic before the brief is published.
Keep token cost reasonable.
```

| Expect | Detail |
|--------|--------|
| Decision | `ai_resolved` |
| Pattern bias | Parallel research and/or verification-loop |
| Binding | Catalog agents matching research / analysis / verify terms |
| Note | Domain may lean video pack unless specials score higher |

---

## Sample C — Short-form social under budget

**Paste**

```text
Short-form social video crew under budget.
Fast turnaround for 15–30s clips, captions, light music bed.
Prefer cost-efficient crew; still need a minimum quality check.
```

| Expect | Detail |
|--------|--------|
| Decision | usually `ai_resolved` |
| Pattern | lean hierarchy or parallel |
| Crew | smaller slot count when cost language is strong |

---

## Sample D — Requirement conflict (HITL demo)

**Paste**

```text
Lowest cost AND premium quality cinematic film with no compromise.
Either we ship same-day ASAP or we do a thorough multi-phase feature pipeline —
I cannot decide which priority wins.
```

| Expect | Detail |
|--------|--------|
| Decision | **`needs_hitl`** |
| Why | Cost vs quality and/or speed vs depth signals conflict |
| Human does | Pick **one** option per open question (not pick agents) |
| Then | AI re-plans and draws workflow |

**Example human answers**

| Question kind | Choose to continue |
|---------------|--------------------|
| Cost vs quality | `prefer_cost` **or** `prefer_quality` **or** `balanced` |
| Speed vs depth | `prefer_speed` **or** `prefer_depth` **or** `phased` |

---

## Sample E — Full feature hierarchy

**Paste**

```text
Full feature film production hierarchy.
Need Orchestrator → Planner → departments: story, direction, picture, sound, and final QC gate.
Video domain. Multi-phase, thorough.
```

| Expect | Detail |
|--------|--------|
| Decision | `ai_resolved` |
| Pattern | hierarchical-supervisor |
| Core | orchestrator + planner pinned when in catalog |
| Diagram | CONTROL → CRAFT → VERIFY phases |

---

## Sample F — Software / legacy signal (specials bias)

**Paste**

```text
Legacy COBOL analysis swarm for a migration assessment.
Software implementation planning, API inventory, risk register.
Prefer specials / software-oriented agents when available.
```

| Expect | Detail |
|--------|--------|
| Decision | usually `ai_resolved` |
| Inventory bias | specials pack scoring higher on software terms |
| Note | If video + software both strong without resolution → possible domain HITL |

---

## Sample G — Explicit conflict keyword

**Paste**

```text
There is a contradiction in scope: we want either a cheap UGC pipeline
or a broadcast-quality drama series. Trade-off undecided. Conflict.
```

| Expect | Detail |
|--------|--------|
| Decision | **`needs_hitl`** |
| Human | Resolve trade-off or rewrite spec |

---

## Quick chip mapping (UI)

If chips are present on Compose, they map roughly to:

| Chip | Sample |
|------|--------|
| YouTube wuxia short | A |
| Market intel + verify | B |
| Short-form social under budget | C |
| Lowest cost and premium quality… (conflict demo) | D |
| Full feature film hierarchy | E |

---

## How to read the workflow diagram

| Node type | Meaning |
|-----------|---------|
| **PHASE · CONTROL** | Meta crew (Orchestrator / Planner) |
| **PHASE · CRAFT** | Specialist agents bound from catalog |
| **PHASE · VERIFY** | Judge / gate / critic |
| **agent** card | Catalog `agent_id` |
| **GATE** card | Verification / quality |
| **refine ≤3** | Critic cycle (design-time / fail-closed) |

---

## Copy-paste checklist

1. Open `/composer`.
2. Paste a sample above (or pick a chip).
3. Click **AI plan** (⌘/Ctrl+Enter).
4. If HITL: answer options only.
5. Confirm diagram + slots look closed-world.
6. **Accept AI → Canvas** → `/swarms/{id}/canvas`.
7. Remember: Host drafts are **process-local** (restart clears them).

---

## Related mock

- UI mock: `docs/frontend_redesign/ui_03_swarm_composer_acc_preview.svg`
