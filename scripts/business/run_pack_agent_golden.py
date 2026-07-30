#!/usr/bin/env python3
"""CLI: run offline pack-agent golden suite (spine or all).

Uses host pack_runtime — no live providers.
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

from app.video.pack_runtime.golden import PackGoldenRunner  # noqa: E402
from app.video.pack_runtime.paths import SPINE_AGENT_IDS  # noqa: E402
from app.video.pack_runtime.runner import PackAgentRunner  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spine", action="store_true", help="Run 7 spine agents only")
    parser.add_argument("--all", action="store_true", help="Run all agents with golden.json")
    parser.add_argument("--agent", action="append", dest="agents", help="Agent id (repeatable)")
    parser.add_argument(
        "--collab-demo",
        action="store_true",
        help="Demo critique edge orchestrator→judge with HiTL resolve",
    )
    parser.add_argument("--json-out", type=Path, help="Write suite JSON report")
    args = parser.parse_args()

    if args.collab_demo:
        runner = PackAgentRunner()
        bus = runner.critique_bus
        # critic sends major to orchestrator path is inputs; demo orchestrator → judge
        orch = runner.run(
            "video.orchestrator",
            goal="Coordinate offline spine demo",
            correlation_id="demo_collab_1",
            emit_self_critique_to="video.judge",
            constraints={"network": False, "production": False},
        )
        print("orchestrator", orch.status, "critiques", len(orch.critiques_emitted))
        inbox = bus.receive(
            correlation_id="demo_collab_1",
            to_id="video.judge",
            allowed_inputs=("video.orchestrator", "video.critic", "video.producer"),
        )
        print("judge inbox", len(inbox))
        if inbox:
            # blockers need HiTL
            for msg in inbox:
                if msg.requires_hitl:
                    res = bus.resolve_dispute(
                        correlation_id="demo_collab_1",
                        judge_id="video.judge",
                        target_message_id=msg.message_id,
                        resolution="Accepted with HiTL confirm (demo)",
                        confirm_hitl=True,
                    )
                    print("resolved", res.message_id, res.claim)
                else:
                    bus.ack(msg.message_id, "video.judge")
                    print("acked", msg.message_id, msg.severity.value)
        return 0

    runner = PackGoldenRunner()
    if args.agents:
        suite = runner.run_many(args.agents)
    elif args.all:
        suite = runner.run_all_with_goldens()
    else:
        # default spine
        suite = runner.run_spine()

    print(f"Pack golden suite: passed={suite.passed}/{suite.total} failed={suite.failed}")
    for case in suite.results:
        mark = "OK" if case.passed else "FAIL"
        print(f"  [{mark}] {case.agent_id}")
        if not case.passed:
            for err in case.errors:
                print(f"       - {err}")
    if args.json_out:
        args.json_out.write_text(
            json.dumps(suite.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        print(f"Wrote {args.json_out}")

    if not args.agents and not args.all and not args.spine:
        print(f"(default spine set: {', '.join(SPINE_AGENT_IDS)})")
    return 0 if suite.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
