# Agent Improvement Plan — Implementation Completion

**Generated:** 2026-07-30T14:45:36Z  
**Plans:** `agent_improvement_plan_v1.md` / `agent_improvement_plan_v1_hk.md`  
**Agents:** 114  

## Complete % (headline)

| Metric | % |
|--------|--:|
| **Plan composite (recommended)** | **95.71%** |
| Maturity weighted (YES=1, PARTIAL=0.5) | 95.45% |
| Strict YES only | 90.91% |
| Avg maturity 0–11 | 10.5 |
| Automatable (all Q except Q5) | 100.0% |
| Platform workstreams P0–P4 | 100.0% |
| Universal U1–U18 | 88.89% |
| Q5 claimable surpass | 0.0% |

> **Headline: 95.71% complete.** Automatable engineering path is **100.0%**. Remaining gap is almost entirely **real human baselines** for Q5 (114 agents still need non-synthetic gate.met).

## Capability questions (fleet)

| Q | YES | PARTIAL | NO | YES% |
|---|---:|---:|---:|----:|
| Q1 Responsibility | 114 | 0 | 0 | 100.0% |
| Q2 Knowledge distill plan | 114 | 0 | 0 | 100.0% |
| Q3 Sources | 114 | 0 | 0 | 100.0% |
| Q4 Self-eval | 114 | 0 | 0 | 100.0% |
| Q5 Surpass human (measured) | 0 | 114 | 0 | 0.0% |
| Q6 Execution | 114 | 0 | 0 | 100.0% |
| Q7 Skills/harness | 114 | 0 | 0 | 100.0% |
| Q8 Self-improve | 114 | 0 | 0 | 100.0% |
| Q9 Research/improve | 114 | 0 | 0 | 100.0% |
| Q10 Collab instructions | 114 | 0 | 0 | 100.0% |
| Q11 Conflict resolve | 114 | 0 | 0 | 100.0% |

## Platform workstreams

| ID | Item | Done |
|----|------|------|
| P0.1 | Prompt factory ×114 | **YES** |
| P0.2 | Rubric factory ×114 | **YES** |
| P0.3 | Source catalog factory ×114 | **YES** |
| P0.4 | Golden task scaffold ×114 | **YES** |
| P0.5 | Skills harness scaffold ×114 | **YES** |
| P0.6 | Capability audit regen | **YES** |
| P1.1 | Host loads prompt_reference | **YES** |
| P1.2 | Tool allowlist + offline mock path | **YES** |
| P1.3 | Graph/golden binding per agent | **YES** |
| P1.4 | Evidence / run result bundle | **YES** |
| P1.5 | Fail-closed production/network | **YES** |
| P2.1 | L1 validators in runner | **YES** |
| P2.2 | L2 rubric scoring in runner | **YES** |
| P2.3 | L3/pairwise protocol fields | **YES** |
| P2.4 | Human baseline capture kit | **YES** |
| P2.5 | Surpass gate dashboard | **YES** |
| P3.1 | CritiqueMessage APIs (in-process) | **YES** |
| P3.2 | critique_edges expanded | **YES** |
| P3.3 | Delivery/ack routing | **YES** |
| P3.4 | Judge dispute + severity | **YES** |
| P3.5 | HiTL confirm for blockers | **YES** |
| P4.1 | Distillation plan schema | **YES** |
| P4.2 | Source acquisition SOP (ACQUIRE.md) | **YES** |
| P4.3 | Research path scaffolds | **YES** |
| P4.4 | Refine loop max_refinement_count | **YES** |
| P4.5 | Memory namespace ids in distill plan | **YES** |

## Universal checklist U1–U18 (fleet %)

| ID | % agents complete |
|----|-------------:|
| U1 | 100.0% |
| U2 | 100.0% |
| U3 | 100.0% |
| U4 | 100.0% |
| U5 | 100.0% |
| U6 | 100.0% |
| U7 | 100.0% |
| U8 | 100.0% |
| U9 | 100.0% |
| U10 | 100.0% |
| U11 | 100.0% |
| U12 | 100.0% |
| U13 | 100.0% |
| U14 | 100.0% |
| U15 | 100.0% |
| U16 | 100.0% |
| U17 | 0.0% |
| U18 | 0.0% |

## Phases

| Phase | % | Note |
|-------|--:|------|
| Phase 0 Honesty & gates | 100.0% | Audit + no false surpass (synthetic blocked) |
| Phase 1 Artifacts (P0) | 100.0% | prompts/rubrics/catalogs/skills/goldens |
| Phase 2 Spine runtime | 100.0% | pack_runtime + spine golden 7/7 |
| Phase 3 Craft execution | 100.0% | offline runner for all agents |
| Phase 4 Collab+conflict | 100.0% | CritiqueBus edges + HiTL blockers |
| Phase 5 Human baselines | 50.0% | protocols+agent measure done; claimable MET=0/114 |
| Phase 6 Full mark lock | 0.0% | 11/11 YES for every agent |

## Remaining work

1. Run rater sessions for spine then ATL (`evals/rater_sessions/SESSION_INDEX.md`).
2. Record real human trials (not synthetic).
3. `evaluate_gate` until `met=true` per agent → Q5 YES → full 11/11.

```bash
python scripts/business/baseline_status.py
python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate
python scripts/business/audit_agent_capability_status.py
python scripts/business/report_improvement_plan_completion.py
```

