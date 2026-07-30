# Human baseline & surpass gate (Q5)

## Honesty rule

**Never claim “surpasses human” in product UI unless:**

1. `human_baseline_protocol.json` exists  
2. `gate.met == true`  
3. `gate.synthetic == false`  
4. Evidence file `human_baseline_evidence.json` is present  

Synthetic CI raters (`synthetic=true`) may exercise the pipeline only (`status=synthetic_checked`) and **never** set `gate.met` for claims.

## Files per agent

```
business/video/evals/agents/<agent_id>/
  golden.json
  human_baseline_protocol.json   # metric, protocol, trials, gate
  human_baseline_evidence.json   # snapshot after evaluate_gate
```

## Workflow

```bash
# 1) Scaffold protocols for all agents (from agents.md surpass signals)
python scripts/business/scaffold_human_baselines_v1.py

# 2) Measure agent offline (L2 scores from pack_runtime)
python scripts/business/scaffold_human_baselines_v1.py --measure-agent --trials 5

# 3) Record real human trials (API-style via Python)
python -c "
from app.video.pack_runtime.baseline import HumanBaselineService
svc = HumanBaselineService()
for score in [72, 75, 70, 78, 74]:
    svc.record_human_trial('video.orchestrator', score=score, rater_id='rater.alice', synthetic=False)
print(svc.evaluate_gate('video.orchestrator'))
"

# 4) Spine CI pipeline check only (synthetic humans)
python scripts/business/scaffold_human_baselines_v1.py --spine --seed-synthetic-human --measure-agent --evaluate-gate

# 5) Re-audit capability status
python scripts/business/audit_agent_capability_status.py
```

## Metric inference

`agents.md` Surpass-Human Signal text is parsed into a metric:

| Signal cue | Metric |
|------------|--------|
| Wins ≥N% / pairwise / arena | `pairwise_win_rate` |
| TTD / faster / turnaround | `time_to_delivery` (lower better) |
| cheaper / cost | `cost_efficiency` (lower better) |
| κ / kappa | `agreement_kappa` |
| default | `craft_score` vs human mean |

## Host module

`backend/app/video/pack_runtime/baseline.py` — `HumanBaselineService`

## Operator tools (go-live path)

```bash
# Dashboard
python scripts/business/baseline_status.py
# → business/video/evals/BASELINE_STATUS.md

# Rater session packs (spine + ATL briefs)
python scripts/business/prepare_rater_sessions_v1.py
# → business/video/evals/rater_sessions/SESSION_INDEX.md

# Clear CI synthetic humans before real sessions
python scripts/business/record_human_baseline.py --clear-synthetic --agents video.orchestrator video.planner video.router video.judge video.gatekeeper video.critic video.memory

# Interactive rater session
python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater alice --evaluate

# Single score
python scripts/business/record_human_baseline.py --agent video.director --score 78 --rater bob --notes "pass1" --evaluate

# CSV template + import
python scripts/business/record_human_baseline.py --export-template business/video/evals/rater_sessions/templates/batch.csv --agents video.orchestrator video.planner --trials 5 --rater team
python scripts/business/record_human_baseline.py --import-csv business/video/evals/rater_sessions/templates/batch.csv --evaluate
```

## Current fleet posture

- Protocols: all 114 agents  
- Offline agent measurements: filled by scaffold  
- Real human trials: **pending** (operators) — claimable surpass = 0 until real gates MET  
- Ready for raters: **114** (agent side measured)  
- Spine cleaned of synthetic humans for real sessions  
- Session briefs: `evals/rater_sessions/` (12 agents: spine + ATL)  

