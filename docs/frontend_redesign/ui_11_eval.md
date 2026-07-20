# NN UI 11: Eval & Self-Improvement Dashboard Spec

**UI ID:** nn_ui_11_eval  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui11  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Systematic visibility into commons quality + tools to run improvement campaigns and review proposals at scale — powering collective self-refinement.

## Layout & Structure
Dashboard with scorecards + trend charts. Main area: Proposal queue + Campaign launcher. Side: Meta-critic insights.

## Key Components
- Scorecards: Global/common-specific success, efficiency, verifier pass rate with trends.
- Proposal Queue: Table (target common, expected impact, supporting traces, approve/reject/review).
- Campaign Launcher: Select underperforming commons → "Run Batch Eval" → auto-generate proposals.
- History Timeline: Merged proposals with before/after metrics and impact.
- A/B Results: Ongoing/past experiments with statistical winner recommendation.
- Insights Panel: Top failure modes, token waste hotspots, suggested pattern improvements.

## Data & API
- Eval results aggregate + per common.
- Proposal CRUD + merge workflow.
- Batch eval trigger.
- A/B framework results.
- Meta-critic analysis endpoint.

## Interactions
- Proposal row → opens diff viewer + traces + impact table → Approve (triggers merge + notifications).
- Campaign → progress modal + results feed into proposal queue.
- "Promote winner" from A/B results.

## Polish & Accessibility
Clear metric visualization (green for improvements). Accessible tables and modals. Bilingual proposal rationales where possible.

## Wireframe Summary
Top: Score trend charts. Left: Proposal queue. Center: Campaign controls + insights. Right: History timeline.

**Implementation Notes:** Meta-critic integration is core value. Batch eval and proposal generation are high-leverage for commons quality. Diff viewer shared with Registry Hub.


## VA-Agent-Swarm Evaluation Alignment

Evaluation must render the evidence-based L1/L2/L3 model in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md): L1 schema/format/required-field validation is an all-required-fields pass; L2 is a role-specific rubric with score, threshold, evidence, and critic/Judge result; L3 is stakeholder or audience preference against a named baseline. Aggregate scores must not hide a failed lower-layer gate.

Each result identifies Common Agent/Pattern version, graph revision, task/artifact references, model/tool configuration, benchmark case, input provenance, retry/iteration count, and held-out versus development classification. Support pairwise comparisons, regressions, red-team evidence, and corrective recommendations as versioned proposal inputs. A passing evaluation does not publish a common version or authorize rollout without the defined proposal, approval, canary, and rollback stages.
