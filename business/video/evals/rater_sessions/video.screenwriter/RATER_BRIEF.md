# Rater brief — `video.screenwriter`

## Goal
Capture **real human baseline** trials for Q5 surpass evaluation.

## Design surpass signal
Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)

## Metric to score
- **id:** `pairwise_win_rate`
- **direction:** `higher_is_better`
- **unit:** `fraction`
- **threshold:** `agent_pairwise_win_rate >= 0.5`
- **pairwise min (if any):** 0.5

## Self-quality criteria (context)
Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta

## Frozen task
Use pack golden fixture only (same inputs every trial):

`business/video/evals/agents/video.screenwriter/golden.json`

Do **not** change the brief between human trials.

## Offline agent reference (not a human substitute)
Current offline agent L2 mean (for context only): **90.0**

## Procedure
1. Read golden input goal/constraints.
2. Produce a human-quality response for this role **or** score a retained human reference package.
3. Assign numeric score **0–100** (unless session lead specifies metric-native scale).
4. Record via CLI:

```bash
python scripts/business/record_human_baseline.py --agent video.screenwriter --score <N> --rater <your_id> --notes "..."
```

5. Repeat until **5** real trials (synthetic forbidden).
6. Evaluate gate:

```bash
python scripts/business/record_human_baseline.py --agent video.screenwriter --score 0 --rater <your_id> --evaluate
```

(Use session mode instead:)

```bash
python scripts/business/record_human_baseline.py --session --agent video.screenwriter --rater <your_id> --evaluate
```

## Pass / claim rule
- `gate.met=true` AND `synthetic=false` required before any “surpasses human” language.
- If not met: keep status honest (`not_met`); improve agent, then re-measure.

## Timebox suggestion
~15–30 minutes for 5 trials depending on craft depth.
