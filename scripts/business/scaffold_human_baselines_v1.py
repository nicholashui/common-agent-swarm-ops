#!/usr/bin/env python3
"""Scaffold Q5 human-baseline protocols for video pack agents.

For each agent:
- Write evals/agents/<id>/human_baseline_protocol.json from agents.md surpass signal
- Optionally measure agent offline trials
- Optionally seed synthetic human trials for CI pipeline check (never claims met)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BACKEND = _REPO / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.video.pack_runtime.baseline import (  # noqa: E402
    HumanBaselineService,
    build_protocol,
    protocol_path,
)
from app.video.pack_runtime.paths import AGENTS_ROOT, EVALS_AGENTS_ROOT, SPINE_AGENT_IDS  # noqa: E402

_VA = Path(r"C:\Project\va-agent-swarm\study\agents.md")
_CORPUS = _REPO / "business" / "video" / "corpus" / "study" / "agents.md"


def parse_va_rows(text: str) -> dict[int, dict]:
    import re

    rows: dict[int, dict] = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not re.match(r"^\d+$", cells[0] or ""):
            continue
        m = re.search(r"\*\*([^*]+)\*\*", cells[1])
        if not m:
            continue
        while len(cells) < 10:
            cells.append("")
        rows[int(cells[0])] = {
            "va_name": m.group(1).strip(),
            "self_quality_criteria": cells[4],
            "surpass_human_signal": cells[5],
        }
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spine", action="store_true", help="Only spine agents")
    parser.add_argument("--agent", action="append", dest="agents")
    parser.add_argument(
        "--measure-agent",
        action="store_true",
        help="Run offline agent measurement trials after scaffolding",
    )
    parser.add_argument(
        "--seed-synthetic-human",
        action="store_true",
        help="Seed synthetic human trials for pipeline check (never sets gate.met claim)",
    )
    parser.add_argument(
        "--evaluate-gate",
        action="store_true",
        help="Evaluate surpass gate after measurements",
    )
    parser.add_argument("--trials", type=int, default=5)
    args = parser.parse_args()

    va_path = _VA if _VA.is_file() else _CORPUS
    va_rows = parse_va_rows(va_path.read_text(encoding="utf-8", errors="replace")) if va_path.is_file() else {}

    if args.agents:
        agent_ids = args.agents
    elif args.spine:
        agent_ids = list(SPINE_AGENT_IDS)
    else:
        agent_ids = sorted(
            p.name
            for p in AGENTS_ROOT.iterdir()
            if p.is_dir() and (p / "agent_spec.json").is_file()
        )

    svc = HumanBaselineService(EVALS_AGENTS_ROOT)
    report = []
    for i, aid in enumerate(agent_ids, start=1):
        spec_path = AGENTS_ROOT / aid / "agent_spec.json"
        if not spec_path.is_file():
            print(f"[{i}/{len(agent_ids)}] SKIP {aid} (no agent_spec)")
            continue
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        va_id = spec.get("va_id")
        va = va_rows.get(va_id) if isinstance(va_id, int) else None
        surpass = (va or {}).get("surpass_human_signal") or ""
        quality = (va or {}).get("self_quality_criteria") or ""
        va_name = str(spec.get("va_name") or (va or {}).get("va_name") or aid)

        proto = build_protocol(
            aid,
            surpass_signal=surpass,
            self_quality=quality,
            va_name=va_name,
        )
        # preserve existing human trials if re-run
        existing_path = protocol_path(aid, EVALS_AGENTS_ROOT)
        if existing_path.is_file():
            try:
                old = json.loads(existing_path.read_text(encoding="utf-8"))
                if isinstance(old, dict):
                    if old.get("human_baseline"):
                        proto["human_baseline"] = old["human_baseline"]
                    if old.get("agent_measurement") and not args.measure_agent:
                        proto["agent_measurement"] = old["agent_measurement"]
                    if old.get("gate") and not args.evaluate_gate:
                        proto["gate"] = old["gate"]
                    if old.get("status") and old["status"] not in {"protocol_ready"}:
                        proto["status"] = old["status"]
            except (OSError, json.JSONDecodeError):
                pass

        path = svc.save(proto)
        print(f"[{i}/{len(agent_ids)}] protocol {aid} -> {path.relative_to(_REPO)}")

        if args.seed_synthetic_human:
            # deterministic synthetic scores around 75 for CI pipeline
            for t in range(args.trials):
                svc.record_human_trial(
                    aid,
                    score=74.0 + (t % 5),
                    rater_id="synthetic_ci_rater",
                    notes="Synthetic human trial for pipeline only — not a real rater",
                    synthetic=True,
                )
            print(f"       seeded {args.trials} synthetic human trials")

        if args.measure_agent:
            svc.measure_agent_offline(aid, trials=args.trials)
            print(f"       measured agent offline x{args.trials}")

        if args.evaluate_gate:
            gate = svc.evaluate_gate(aid)
            print(f"       gate status={gate.status} met={gate.met} :: {gate.detail[:100]}")
            report.append(gate.to_dict())
        else:
            report.append({"agent_id": aid, "status": svc.readiness(aid)})

    out = _REPO / "business" / "video" / "evals" / "human_baseline_scaffold_report.json"
    out.write_text(json.dumps({"count": len(report), "results": report}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
