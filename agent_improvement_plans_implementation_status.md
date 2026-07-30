# Agent Improvement Plans — Implementation Status & Complete %

**Generated:** 2026-07-30 (post re-apply)  
**Plans implemented:**
- `agent_improvement_plan_v1.md`
- `agent_improvement_plan_v2.md`  
(HK mirrors: `*_hk.md`)

**Evidence:** `AGENT_CAPABILITY_AUDIT.json`, pack artifacts ×114, `pack_runtime`, spine golden 7/7, tests 7/7

---

## Headline complete %

| Metric | % | Notes |
|--------|--:|-------|
| **Overall plan composite** | **95.71%** | Recommended headline for “plans done” |
| **Maturity weighted** (YES=1, PARTIAL=0.5) | **95.45%** | 1140 YES + 114 PARTIAL cells |
| **Strict YES only** | **90.91%** | 1140 / 1254 cells |
| **Avg maturity 0–11** | **10.5** | Target full mark = 11.0 |
| **Automatable work (all Q except Q5)** | **100.0%** | Engineering path complete |
| **Platform workstreams P0–P4** | **100.0%** | Factories + host runtime + bus |
| **Q5 claimable surpass** | **0.0%** | Needs real human `gate.met` |

---

## Plan v1 complete %

| Workstream | Target | Status | Complete |
|------------|--------|--------|----------|
| **P0** Artifact factories | prompts/rubrics/catalogs/skills/goldens ×114 | Done | **100%** |
| **P1** Execution runtime | host load + offline path | Done (`pack_runtime`) | **100%** |
| **P2** Eval / baseline kit | L1/L2/L3 + protocols | Protocol+runner done; human MET pending | **~85%** |
| **P3** Critique bus | send/receive/ack/HiTL | Done | **100%** |
| **P4** Distill / improve | plans + refine loop | Done | **100%** |
| **Q1–Q4 fleet YES** | responsibility/distill/sources/self-eval | Done | **100%** |
| **Q6–Q11 fleet YES** | exec/skills/improve/research/collab/conflict | Done | **100%** |
| **Q5 measured surpass** | gate.met && !synthetic | Not done | **0%** |

### v1 overall

| View | % |
|------|--:|
| **v1 automatable** | **100%** |
| **v1 full mark (incl. Q5)** | **~95.5%** (weighted) / **~90.9%** strict YES |

**v1 re-applied this run:** `improve_agents_from_plan_v1.py` → Improved **114/114**

---

## Plan v2 complete %

v2 assumes v1 green and focuses on full mark (11/11), mainly Q5.

| Workstream | Target | Status | Complete |
|------------|--------|--------|----------|
| **W0** Protect green | spine golden + no false surpass | Done (7/7 golden, tests green) | **100%** |
| **W1.1** Protocols ×114 | human_baseline_protocol | Done | **100%** |
| **W1.2** Clear synthetic ops | CLI available | Done (tooling) | **100%** |
| **W1.3** Rater session packs | spine+ATL briefs | Done | **100%** |
| **W1.4** Real human trials n≥5 | operators | **Pending humans** | **0%** of agents |
| **W1.5** Gate MET non-synthetic | claimable surpass | **0/114** | **0%** |
| **W1.6** Dashboard | BASELINE_STATUS | Done | **100%** |
| **W1.7** Audit/completion loop | scripts | Done | **100%** |
| **W2** Optional harden (mocks, licenses, promote) | not required for Q5 YES | Optional | N/A |

### v2 overall

| View | % |
|------|--:|
| **v2 tooling / ops scaffolding** | **~100%** |
| **v2 full-mark outcome (11/11 all agents)** | **~95.5%** weighted (same as fleet) |
| **v2 Q5 human delivery** | **0%** claimable (114 agents still need real raters) |

**v2 re-applied this run:** baselines re-measured offline ×5 for all 114; plans regenerated EN+HK

---

## Capability questions (shared outcome of both plans)

| Q | YES | PARTIAL | NO | Complete (YES%) |
|---|----:|--------:|---:|----------------:|
| Q1 Responsibility | 114 | 0 | 0 | **100%** |
| Q2 Distill plan | 114 | 0 | 0 | **100%** |
| Q3 Sources | 114 | 0 | 0 | **100%** |
| Q4 Self-eval | 114 | 0 | 0 | **100%** |
| **Q5 Surpass human** | **0** | **114** | **0** | **0% YES** (100% protocol PARTIAL) |
| Q6 Execution | 114 | 0 | 0 | **100%** |
| Q7 Skills/harness | 114 | 0 | 0 | **100%** |
| Q8 Self-improve | 114 | 0 | 0 | **100%** |
| Q9 Research/improve | 114 | 0 | 0 | **100%** |
| Q10 Collab | 114 | 0 | 0 | **100%** |
| Q11 Conflict | 114 | 0 | 0 | **100%** |

---

## What was executed just now

```text
improve_agents_from_plan_v1.py          → 114/114 improved
scaffold_human_baselines_v1.py --measure-agent → 114 protocols + offline measures
run_pack_agent_golden.py --spine        → 7/7 OK
audit_agent_capability_status.py        → maturity 10.5
report_improvement_plan_completion.py   → 95.71% composite
render_agent_improvement_plan_v2(.py/_hk) → plans refreshed
pytest test_pack_runtime.py             → 7 passed
```

---

## Path to 100%

Only remaining full-mark work:

1. Real human trials (≥5 per agent, `synthetic=false`)
2. `evaluate_gate` → `gate.met=true`
3. Re-audit → maturity **11.0**, composite **100%**

```bash
python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate
python scripts/business/audit_agent_capability_status.py
python scripts/business/report_improvement_plan_completion.py
```

---

## Summary

| Plan | Automatable implemented | Full-mark complete % |
|------|-------------------------|---------------------:|
| **v1** | **Yes (100%)** | **~95.7%** composite |
| **v2** | **Yes (tooling 100%)** | **~95.5%** weighted / **0%** Q5 claimable |
| **Combined engineering** | **Done** | **95.71%** |
| **True 11/11 fleet** | Blocked on human raters | **+4.3%** left |

**Bottom line: Both plans are implemented for everything code/automation can do. Complete ≈ 95.7%. Last 4.3% = real human baselines (Q5).**
