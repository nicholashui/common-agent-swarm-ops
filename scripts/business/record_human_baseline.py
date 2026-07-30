#!/usr/bin/env python3
"""Record real human baseline trials for pack agents (Q5).

Modes:
  --score           append one trial
  --import-csv      bulk import (agent_id,score,rater_id,notes)
  --session         guided multi-trial session for one agent
  --evaluate        run surpass gate after recording

Never set synthetic=true for real raters.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BACKEND = _REPO / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.video.pack_runtime.baseline import HumanBaselineService  # noqa: E402
from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT  # noqa: E402


def _svc() -> HumanBaselineService:
    return HumanBaselineService(EVALS_AGENTS_ROOT)


def cmd_score(args: argparse.Namespace) -> int:
    svc = _svc()
    if args.synthetic:
        print("ERROR: refuse --synthetic for record_human_baseline (use scaffold for CI only)")
        return 2
    proto = svc.record_human_trial(
        args.agent,
        score=float(args.score),
        rater_id=args.rater,
        notes=args.notes or "",
        synthetic=False,
    )
    hb = proto.get("human_baseline") or {}
    agg = hb.get("aggregate") or {}
    print(
        f"Recorded {args.agent}: score={args.score} rater={args.rater} "
        f"n={agg.get('n')} mean={agg.get('mean')} status={hb.get('status')}"
    )
    if args.evaluate:
        gate = svc.evaluate_gate(args.agent)
        print(f"Gate: status={gate.status} met={gate.met} :: {gate.detail}")
    return 0


def cmd_import_csv(args: argparse.Namespace) -> int:
    svc = _svc()
    path = Path(args.import_csv)
    if not path.is_file():
        print(f"CSV not found: {path}")
        return 1
    count = 0
    agents: set[str] = set()
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        required = {"agent_id", "score"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            print("CSV must have headers: agent_id,score[,rater_id,notes]")
            return 1
        for row in reader:
            aid = (row.get("agent_id") or "").strip()
            if not aid:
                continue
            score = float(row["score"])
            rater = (row.get("rater_id") or args.rater or "human_rater").strip()
            notes = (row.get("notes") or "").strip()
            svc.record_human_trial(
                aid, score=score, rater_id=rater, notes=notes, synthetic=False
            )
            agents.add(aid)
            count += 1
    print(f"Imported {count} trials across {len(agents)} agents from {path}")
    if args.evaluate:
        for aid in sorted(agents):
            gate = svc.evaluate_gate(aid)
            print(f"  {aid}: {gate.status} met={gate.met}")
    return 0


def cmd_session(args: argparse.Namespace) -> int:
    svc = _svc()
    try:
        proto = svc.load(args.agent)
    except FileNotFoundError:
        print(f"No protocol for {args.agent}. Run scaffold_human_baselines_v1.py first.")
        return 1
    metric = proto.get("metric") or {}
    signal = proto.get("surpass_signal_design") or ""
    min_n = int((proto.get("protocol") or {}).get("n_human_trials_min") or 5)
    print("=" * 60)
    print(f"Human baseline session — {args.agent}")
    print(f"VA: {proto.get('va_name')}")
    print(f"Surpass signal: {signal}")
    print(f"Metric: {metric.get('id')} ({metric.get('direction')}) unit={metric.get('unit')}")
    print(f"Threshold: {metric.get('threshold_expression')}")
    print(f"Target trials: {min_n} (score 0–100 craft scale unless metric says otherwise)")
    print("Task fixture:", (proto.get("protocol") or {}).get("task_fixture"))
    print("=" * 60)
    print("Instructions for rater:")
    print("  1. Open the frozen golden task brief for this agent.")
    print("  2. Produce/score a human baseline output on the SAME inputs.")
    print("  3. Enter a numeric score (0-100) or metric-native value.")
    print("  4. Type 'q' to finish early.")
    print()

    rater = args.rater
    recorded = 0
    while recorded < (args.trials or min_n):
        raw = input(f"Trial {recorded+1}/{args.trials or min_n} score (or q): ").strip()
        if raw.lower() in {"q", "quit"}:
            break
        try:
            score = float(raw)
        except ValueError:
            print("  invalid number")
            continue
        notes = input("  notes (optional): ").strip()
        svc.record_human_trial(
            args.agent,
            score=score,
            rater_id=rater,
            notes=notes,
            synthetic=False,
        )
        recorded += 1
        print(f"  saved (total this session {recorded})")

    if args.evaluate or recorded:
        gate = svc.evaluate_gate(args.agent)
        print()
        print(f"Gate: status={gate.status} met={gate.met}")
        print(f"Detail: {gate.detail}")
    return 0


def cmd_clear_synthetic(args: argparse.Namespace) -> int:
    svc = _svc()
    agents = args.agents or ([args.agent] if args.agent else [])
    if not agents:
        print("Provide --agent or --agents")
        return 1
    for aid in agents:
        proto = svc.clear_human_trials(aid, only_synthetic=not args.clear_all_human)
        hb = proto.get("human_baseline") or {}
        print(
            f"Cleared {'all human' if args.clear_all_human else 'synthetic'} trials for {aid}; "
            f"remaining n={(hb.get('aggregate') or {}).get('n') or 0}"
        )
    return 0


def cmd_export_template(args: argparse.Namespace) -> int:
    out = Path(args.export_template)
    out.parent.mkdir(parents=True, exist_ok=True)
    agents = args.agents or []
    lines = ["agent_id,score,rater_id,notes"]
    for aid in agents:
        for _ in range(args.trials or 5):
            lines.append(f"{aid},,{args.rater},")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote blank template {out} ({len(agents)} agents × {args.trials or 5})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", help="Agent id e.g. video.orchestrator")
    parser.add_argument("--score", type=float, help="Single trial score")
    parser.add_argument("--rater", default="human_rater", help="Rater identifier")
    parser.add_argument("--notes", default="", help="Trial notes")
    parser.add_argument("--import-csv", help="CSV path to import")
    parser.add_argument("--session", action="store_true", help="Interactive multi-trial session")
    parser.add_argument("--trials", type=int, help="Session/template trial count")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate gate after write")
    parser.add_argument("--export-template", help="Write blank CSV template path")
    parser.add_argument(
        "--agents",
        nargs="*",
        help="Agent ids for --export-template",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Rejected for this CLI (CI only via scaffold)",
    )
    parser.add_argument(
        "--clear-synthetic",
        action="store_true",
        help="Remove synthetic human trials (keep real ones)",
    )
    parser.add_argument(
        "--clear-all-human",
        action="store_true",
        help="With --clear-synthetic: remove ALL human trials",
    )
    args = parser.parse_args()

    if args.export_template:
        return cmd_export_template(args)
    if args.clear_synthetic:
        return cmd_clear_synthetic(args)
    if args.import_csv:
        return cmd_import_csv(args)
    if args.session:
        if not args.agent:
            print("--agent required for --session")
            return 1
        return cmd_session(args)
    if args.agent and args.score is not None:
        return cmd_score(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
