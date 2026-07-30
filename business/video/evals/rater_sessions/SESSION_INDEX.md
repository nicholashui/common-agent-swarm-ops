# Rater session index (spine + ATL)

Priority order: complete **band 0 spine** before ATL.

| band | agent | brief | metric |
|-----:|-------|-------|--------|
| 0 | `video.orchestrator` | [`video.orchestrator/RATER_BRIEF.md`](./video.orchestrator/RATER_BRIEF.md) | time_to_delivery |
| 0 | `video.planner` | [`video.planner/RATER_BRIEF.md`](./video.planner/RATER_BRIEF.md) | cost_efficiency |
| 0 | `video.router` | [`video.router/RATER_BRIEF.md`](./video.router/RATER_BRIEF.md) | craft_score |
| 0 | `video.judge` | [`video.judge/RATER_BRIEF.md`](./video.judge/RATER_BRIEF.md) | agreement_kappa |
| 0 | `video.gatekeeper` | [`video.gatekeeper/RATER_BRIEF.md`](./video.gatekeeper/RATER_BRIEF.md) | craft_score |
| 0 | `video.critic` | [`video.critic/RATER_BRIEF.md`](./video.critic/RATER_BRIEF.md) | accuracy_or_coverage |
| 0 | `video.memory` | [`video.memory/RATER_BRIEF.md`](./video.memory/RATER_BRIEF.md) | craft_score |
| 1 | `video.director` | [`video.director/RATER_BRIEF.md`](./video.director/RATER_BRIEF.md) | pairwise_win_rate |
| 1 | `video.producer` | [`video.producer/RATER_BRIEF.md`](./video.producer/RATER_BRIEF.md) | cost_efficiency |
| 1 | `video.screenwriter` | [`video.screenwriter/RATER_BRIEF.md`](./video.screenwriter/RATER_BRIEF.md) | pairwise_win_rate |
| 1 | `video.showrunner` | [`video.showrunner/RATER_BRIEF.md`](./video.showrunner/RATER_BRIEF.md) | accuracy_or_coverage |
| 1 | `video.casting` | [`video.casting/RATER_BRIEF.md`](./video.casting/RATER_BRIEF.md) | time_to_delivery |

## Before real rating on spine

Spine agents currently may contain **synthetic** human trials from CI.
For real claims, re-scaffold clean human section or manually replace trials with real raters only.

```bash
# Export blank CSV for this cohort
python scripts/business/record_human_baseline.py --export-template business/video/evals/rater_sessions/templates/human_scores_spine_atl.csv --agents video.orchestrator video.planner video.router video.judge video.gatekeeper video.critic video.memory video.director video.producer video.screenwriter video.showrunner video.casting --trials 5 --rater your.name

# Import filled CSV
python scripts/business/record_human_baseline.py --import-csv business/video/evals/rater_sessions/templates/human_scores_spine_atl.csv --evaluate

# Dashboard
python scripts/business/baseline_status.py
```

