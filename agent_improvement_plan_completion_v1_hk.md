# Agent 改進計畫 — 實作完成度

**產生時間:** 2026-07-30T14:45:36Z  
**計畫:** `agent_improvement_plan_v1.md` / `agent_improvement_plan_v1_hk.md`  
**Agents:** 114  

## 完成度 %（總覽）

| 指標 | % |
|--------|--:|
| **計畫綜合完成度（建議主指標）** | **95.71%** |
| 成熟度加權（是=1，部分=0.5） | 95.45% |
| 僅「是」嚴格比例 | 90.91% |
| 平均成熟度 0–11 | 10.5 |
| 可自動化（除 Q5 外全部問題） | 100.0% |
| 平台工作流 P0–P4 | 100.0% |
| 通用清單 U1–U18 | 88.89% |
| Q5 可宣稱超越人類 | 0.0% |

> **總覽：已完成 95.71%。** 可自動化工程路徑 **100.0%**。剩餘缺口幾乎全是 **Q5 真實人類基線**（仍有 114 個 agent 未達非合成 gate.met）。

## 能力問題（全艦隊）

| Q | 是 | 部分 | 否 | YES% |
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

## 平台工作流

| ID | 項目 | 完成 |
|----|------|------|
| P0.1 | Prompt factory ×114 | **是** |
| P0.2 | Rubric factory ×114 | **是** |
| P0.3 | Source catalog factory ×114 | **是** |
| P0.4 | Golden task scaffold ×114 | **是** |
| P0.5 | Skills harness scaffold ×114 | **是** |
| P0.6 | Capability audit regen | **是** |
| P1.1 | Host loads prompt_reference | **是** |
| P1.2 | Tool allowlist + offline mock path | **是** |
| P1.3 | Graph/golden binding per agent | **是** |
| P1.4 | Evidence / run result bundle | **是** |
| P1.5 | Fail-closed production/network | **是** |
| P2.1 | L1 validators in runner | **是** |
| P2.2 | L2 rubric scoring in runner | **是** |
| P2.3 | L3/pairwise protocol fields | **是** |
| P2.4 | Human baseline capture kit | **是** |
| P2.5 | Surpass gate dashboard | **是** |
| P3.1 | CritiqueMessage APIs (in-process) | **是** |
| P3.2 | critique_edges expanded | **是** |
| P3.3 | Delivery/ack routing | **是** |
| P3.4 | Judge dispute + severity | **是** |
| P3.5 | HiTL confirm for blockers | **是** |
| P4.1 | Distillation plan schema | **是** |
| P4.2 | Source acquisition SOP (ACQUIRE.md) | **是** |
| P4.3 | Research path scaffolds | **是** |
| P4.4 | Refine loop max_refinement_count | **是** |
| P4.5 | Memory namespace ids in distill plan | **是** |

## 通用清單 U1–U18（全艦隊 %）

| ID | % agents 完成 |
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

## 階段

| 階段 | % | 說明 |
|-------|--:|------|
| Phase 0 Honesty & gates | 100.0% | Audit + no false surpass (synthetic blocked) |
| Phase 1 Artifacts (P0) | 100.0% | prompts/rubrics/catalogs/skills/goldens |
| Phase 2 Spine runtime | 100.0% | pack_runtime + spine golden 7/7 |
| Phase 3 Craft execution | 100.0% | offline runner for all agents |
| Phase 4 Collab+conflict | 100.0% | CritiqueBus edges + HiTL blockers |
| Phase 5 Human baselines | 50.0% | protocols+agent measure done; claimable MET=0/114 |
| Phase 6 Full mark lock | 0.0% | 11/11 YES for every agent |

## 剩餘工作

1. 先跑 spine 再跑 ATL 評分場次（`evals/rater_sessions/SESSION_INDEX.md`）。
2. 記錄真實人類 trials（禁止 synthetic）。
3. 對每 agent `evaluate_gate` 至 `met=true` → Q5 是 → 滿分 11/11。

```bash
python scripts/business/baseline_status.py
python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate
python scripts/business/audit_agent_capability_status.py
python scripts/business/report_improvement_plan_completion.py
```

