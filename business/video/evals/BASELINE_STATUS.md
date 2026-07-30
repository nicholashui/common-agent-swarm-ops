# Human baseline fleet status (Q5)

**Agents with protocols:** 114  
**Claimable surpass (gate.met & !synthetic):** **0**  
**Still need real human trials:** **114**  
**Ready for raters (agent measured, human pending/synthetic):** **114**  

### Status histogram

| status | count |
|--------|------:|
| `measured` | 114 |

### Priority band 0 — spine (rate first)

| agent | metric | human_n | agent_mean | gate | claim_ok |
|-------|--------|--------:|-----------:|------|----------|
| `video.critic` | accuracy_or_coverage | 0 | 90.0 | not_run | False |
| `video.gatekeeper` | craft_score | 0 | 90.0 | not_run | False |
| `video.judge` | agreement_kappa | 0 | 90.0 | not_run | False |
| `video.memory` | craft_score | 0 | 90.0 | not_run | False |
| `video.orchestrator` | time_to_delivery | 0 | 90.0 | not_run | False |
| `video.planner` | cost_efficiency | 0 | 90.0 | not_run | False |
| `video.router` | craft_score | 0 | 90.0 | not_run | False |

\* = includes synthetic human trials (CI only)

### Priority band 1 — ATL

| agent | metric | human_n | agent_mean | gate | claim_ok |
|-------|--------|--------:|-----------:|------|----------|
| `video.casting` | time_to_delivery | 0 | 90.0 | not_run | False |
| `video.director` | pairwise_win_rate | 0 | 90.0 | not_run | False |
| `video.producer` | cost_efficiency | 0 | 90.0 | not_run | False |
| `video.screenwriter` | pairwise_win_rate | 0 | 90.0 | not_run | False |
| `video.showrunner` | accuracy_or_coverage | 0 | 90.0 | not_run | False |

### Next rater actions

1. Clear synthetic spine humans before real sessions (or use new protocol revision).
2. Run interactive sessions:
   `python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate`
3. Or fill CSV template and import.
4. Re-run `python scripts/business/audit_agent_capability_status.py` after real gates MET.

