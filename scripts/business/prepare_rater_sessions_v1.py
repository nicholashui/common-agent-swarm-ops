#!/usr/bin/env python3
"""Prepare operator rater session packs for spine + ATL agents.

Writes:
  business/video/evals/rater_sessions/
    SESSION_INDEX.md
    templates/human_scores_spine_atl.csv
    <agent_id>/RATER_BRIEF.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BACKEND = _REPO / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT, SPINE_AGENT_IDS  # noqa: E402

ATL = (
    "video.director",
    "video.producer",
    "video.screenwriter",
    "video.showrunner",
    "video.casting",
)
SESSION_ROOT = _REPO / "business" / "video" / "evals" / "rater_sessions"


def brief_for(agent_id: str, proto: dict) -> str:
    metric = proto.get("metric") or {}
    signal = proto.get("surpass_signal_design") or ""
    quality = proto.get("self_quality_criteria") or ""
    min_n = int((proto.get("protocol") or {}).get("n_human_trials_min") or 5)
    agent_mean = ((proto.get("agent_measurement") or {}).get("aggregate") or {}).get("mean")
    return f"""# Rater brief — `{agent_id}`

## Goal
Capture **real human baseline** trials for Q5 surpass evaluation.

## Design surpass signal
{signal}

## Metric to score
- **id:** `{metric.get('id')}`
- **direction:** `{metric.get('direction')}`
- **unit:** `{metric.get('unit')}`
- **threshold:** `{metric.get('threshold_expression')}`
- **pairwise min (if any):** {metric.get('pairwise_win_rate_min')}

## Self-quality criteria (context)
{quality}

## Frozen task
Use pack golden fixture only (same inputs every trial):

`business/video/evals/agents/{agent_id}/golden.json`

Do **not** change the brief between human trials.

## Offline agent reference (not a human substitute)
Current offline agent L2 mean (for context only): **{agent_mean}**

## Procedure
1. Read golden input goal/constraints.
2. Produce a human-quality response for this role **or** score a retained human reference package.
3. Assign numeric score **0–100** (unless session lead specifies metric-native scale).
4. Record via CLI:

```bash
python scripts/business/record_human_baseline.py --agent {agent_id} --score <N> --rater <your_id> --notes "..."
```

5. Repeat until **{min_n}** real trials (synthetic forbidden).
6. Evaluate gate:

```bash
python scripts/business/record_human_baseline.py --agent {agent_id} --score 0 --rater <your_id> --evaluate
```

(Use session mode instead:)

```bash
python scripts/business/record_human_baseline.py --session --agent {agent_id} --rater <your_id> --evaluate
```

## Pass / claim rule
- `gate.met=true` AND `synthetic=false` required before any “surpasses human” language.
- If not met: keep status honest (`not_met`); improve agent, then re-measure.

## Timebox suggestion
~15–30 minutes for {min_n} trials depending on craft depth.
"""


def main() -> int:
    agents = list(SPINE_AGENT_IDS) + list(ATL)
    SESSION_ROOT.mkdir(parents=True, exist_ok=True)
    (SESSION_ROOT / "templates").mkdir(parents=True, exist_ok=True)

    index_lines = [
        "# Rater session index (spine + ATL)",
        "",
        "Priority order: complete **band 0 spine** before ATL.",
        "",
        "| band | agent | brief | metric |",
        "|-----:|-------|-------|--------|",
    ]
    csv_lines = ["agent_id,score,rater_id,notes"]

    for band, aid in [(0, a) for a in SPINE_AGENT_IDS] + [(1, a) for a in ATL]:
        path = EVALS_AGENTS_ROOT / aid / "human_baseline_protocol.json"
        if not path.is_file():
            print(f"missing protocol: {aid}")
            continue
        proto = json.loads(path.read_text(encoding="utf-8"))
        agent_dir = SESSION_ROOT / aid
        agent_dir.mkdir(parents=True, exist_ok=True)
        brief = brief_for(aid, proto)
        (agent_dir / "RATER_BRIEF.md").write_text(brief, encoding="utf-8")
        metric_id = (proto.get("metric") or {}).get("id")
        index_lines.append(
            f"| {band} | `{aid}` | [`{aid}/RATER_BRIEF.md`](./{aid}/RATER_BRIEF.md) | {metric_id} |"
        )
        for _ in range(5):
            csv_lines.append(f"{aid},,,")

    # Clear-synthetic instruction for spine
    index_lines.extend(
        [
            "",
            "## Before real rating on spine",
            "",
            "Spine agents currently may contain **synthetic** human trials from CI.",
            "For real claims, re-scaffold clean human section or manually replace trials with real raters only.",
            "",
            "```bash",
            "# Export blank CSV for this cohort",
            "python scripts/business/record_human_baseline.py --export-template business/video/evals/rater_sessions/templates/human_scores_spine_atl.csv --agents "
            + " ".join(agents)
            + " --trials 5 --rater your.name",
            "",
            "# Import filled CSV",
            "python scripts/business/record_human_baseline.py --import-csv business/video/evals/rater_sessions/templates/human_scores_spine_atl.csv --evaluate",
            "",
            "# Dashboard",
            "python scripts/business/baseline_status.py",
            "```",
            "",
        ]
    )

    (SESSION_ROOT / "SESSION_INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (SESSION_ROOT / "templates" / "human_scores_spine_atl.csv").write_text(
        "\n".join(csv_lines) + "\n", encoding="utf-8"
    )
    print(f"Wrote {SESSION_ROOT / 'SESSION_INDEX.md'}")
    print(f"Wrote templates and {len(agents)} rater briefs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
