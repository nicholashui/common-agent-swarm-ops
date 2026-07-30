# Rater brief — `video.planner`

## Goal
Capture **real human baseline** trials for Q5 surpass evaluation.

## Design surpass signal
Tighter, cheaper plans than EP first pass (blind A/B)

## Metric to score
- **id:** `cost_efficiency`
- **direction:** `lower_is_better`
- **unit:** `relative_cost`
- **threshold:** `agent_mean < human_mean`
- **pairwise min (if any):** None

## Self-quality criteria (context)
Plan validity (no missing gate); cost variance <10%

## Frozen task
Use pack golden fixture only (same inputs every trial):

`business/video/evals/agents/video.planner/golden.json`

Do **not** change the brief between human trials.

## Offline agent reference (not a human substitute)
Current offline agent L2 mean (for context only): **90.0**

## Procedure
1. Read golden input goal/constraints.
2. Produce a human-quality response for this role **or** score a retained human reference package.
3. Assign numeric score **0–100** (unless session lead specifies metric-native scale).
4. Record via CLI:

```bash
python scripts/business/record_human_baseline.py --agent video.planner --score <N> --rater <your_id> --notes "..."
```

5. Repeat until **5** real trials (synthetic forbidden).
6. Evaluate gate:

```bash
python scripts/business/record_human_baseline.py --agent video.planner --score 0 --rater <your_id> --evaluate
```

(Use session mode instead:)

```bash
python scripts/business/record_human_baseline.py --session --agent video.planner --rater <your_id> --evaluate
```

## Pass / claim rule
- `gate.met=true` AND `synthetic=false` required before any “surpasses human” language.
- If not met: keep status honest (`not_met`); improve agent, then re-measure.

## Timebox suggestion
~15–30 minutes for 5 trials depending on craft depth.
