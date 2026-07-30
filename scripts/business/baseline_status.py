#!/usr/bin/env python3
"""Fleet Q5 human-baseline status dashboard (markdown + JSON)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BACKEND = _REPO / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT, SPINE_AGENT_IDS  # noqa: E402

PRIORITY = {
    0: set(SPINE_AGENT_IDS),
    1: {
        "video.director",
        "video.producer",
        "video.screenwriter",
        "video.showrunner",
        "video.casting",
    },
}


def priority_band(agent_id: str) -> int:
    if agent_id in PRIORITY[0]:
        return 0
    if agent_id in PRIORITY[1]:
        return 1
    return 2


def load_all() -> list[dict]:
    rows = []
    for path in sorted(EVALS_AGENTS_ROOT.glob("*/human_baseline_protocol.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        aid = str(doc.get("agent_id") or path.parent.name)
        hb = doc.get("human_baseline") or {}
        am = doc.get("agent_measurement") or {}
        gate = doc.get("gate") or {}
        h_agg = hb.get("aggregate") or {}
        a_agg = am.get("aggregate") or {}
        rows.append(
            {
                "agent_id": aid,
                "band": priority_band(aid),
                "status": doc.get("status"),
                "metric_id": (doc.get("metric") or {}).get("id"),
                "surpass_signal": (doc.get("surpass_signal_design") or "")[:80],
                "human_n": int(h_agg.get("n") or 0),
                "human_mean": h_agg.get("mean"),
                "human_synthetic": bool(h_agg.get("synthetic_any")),
                "agent_n": int(a_agg.get("n") or 0),
                "agent_mean": a_agg.get("mean"),
                "gate_status": gate.get("status"),
                "gate_met": bool(gate.get("met")),
                "gate_synthetic": bool(gate.get("synthetic")),
                "claim_ok": bool(gate.get("met")) and not bool(gate.get("synthetic")),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md-out", type=Path, default=_REPO / "business" / "video" / "evals" / "BASELINE_STATUS.md")
    parser.add_argument("--json-out", type=Path, default=_REPO / "business" / "video" / "evals" / "BASELINE_STATUS.json")
    parser.add_argument("--band", type=int, help="Filter 0=spine 1=ATL 2=rest")
    args = parser.parse_args()

    rows = load_all()
    if args.band is not None:
        rows = [r for r in rows if r["band"] == args.band]

    status_c = Counter(r["status"] for r in rows)
    claimable = sum(1 for r in rows if r["claim_ok"])
    need_human = sum(1 for r in rows if r["human_n"] == 0 or r["human_synthetic"])
    ready_for_raters = sum(
        1
        for r in rows
        if r["agent_n"] >= 5 and (r["human_n"] == 0 or r["human_synthetic"])
    )

    lines: list[str] = []
    a = lines.append
    a("# Human baseline fleet status (Q5)")
    a("")
    a(f"**Agents with protocols:** {len(rows)}  ")
    a(f"**Claimable surpass (gate.met & !synthetic):** **{claimable}**  ")
    a(f"**Still need real human trials:** **{need_human}**  ")
    a(f"**Ready for raters (agent measured, human pending/synthetic):** **{ready_for_raters}**  ")
    a("")
    a("### Status histogram")
    a("")
    a("| status | count |")
    a("|--------|------:|")
    for k, v in sorted(status_c.items(), key=lambda x: (-x[1], x[0])):
        a(f"| `{k}` | {v} |")
    a("")
    a("### Priority band 0 — spine (rate first)")
    a("")
    a("| agent | metric | human_n | agent_mean | gate | claim_ok |")
    a("|-------|--------|--------:|-----------:|------|----------|")
    for r in sorted((x for x in rows if x["band"] == 0), key=lambda x: x["agent_id"]):
        a(
            f"| `{r['agent_id']}` | {r['metric_id']} | {r['human_n']}"
            f"{'*' if r['human_synthetic'] else ''} | {r['agent_mean']} | "
            f"{r['gate_status']} | {r['claim_ok']} |"
        )
    a("")
    a("\\* = includes synthetic human trials (CI only)")
    a("")
    a("### Priority band 1 — ATL")
    a("")
    a("| agent | metric | human_n | agent_mean | gate | claim_ok |")
    a("|-------|--------|--------:|-----------:|------|----------|")
    for r in sorted((x for x in rows if x["band"] == 1), key=lambda x: x["agent_id"]):
        a(
            f"| `{r['agent_id']}` | {r['metric_id']} | {r['human_n']}"
            f"{'*' if r['human_synthetic'] else ''} | {r['agent_mean']} | "
            f"{r['gate_status']} | {r['claim_ok']} |"
        )
    a("")
    a("### Next rater actions")
    a("")
    a("1. Clear synthetic spine humans before real sessions (or use new protocol revision).")
    a("2. Run interactive sessions:")
    a("   `python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate`")
    a("3. Or fill CSV template and import.")
    a("4. Re-run `python scripts/business/audit_agent_capability_status.py` after real gates MET.")
    a("")

    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    args.json_out.write_text(
        json.dumps(
            {
                "count": len(rows),
                "claimable": claimable,
                "need_human": need_human,
                "ready_for_raters": ready_for_raters,
                "status_histogram": dict(status_c),
                "rows": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.md_out}")
    print(f"Wrote {args.json_out}")
    print(f"claimable={claimable} need_human={need_human} ready_for_raters={ready_for_raters}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
