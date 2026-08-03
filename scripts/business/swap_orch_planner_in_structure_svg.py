#!/usr/bin/env python3
"""Set orchestration layer order to Orchestrator → Planner in structure diagrams."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# First two h2 agent labels in the SVG/HTML structure diagram.
_PAIR = re.compile(
    r'(class="h2">)(PlannerAgent|OrchestratorAgent)(</text>\s*\n\s*<text [^>]*class="body">)([^<]+)(</text>)'
    r"([\s\S]{0,500}?)"
    r'(class="h2">)(PlannerAgent|OrchestratorAgent)(</text>\s*\n\s*<text [^>]*class="body">)([^<]+)(</text>)',
)


def transform(text: str) -> tuple[str, str]:
    """Return (new_text, status). status: changed|already|no_match."""
    m = _PAIR.search(text)
    if not m:
        return text, "no_match"
    left, right = m.group(2), m.group(8)
    if left == "OrchestratorAgent" and right == "PlannerAgent":
        return text, "already"

    def repl(match: re.Match[str]) -> str:
        return (
            f'{match.group(1)}OrchestratorAgent{match.group(3)}'
            f"state, retries, fan-out{match.group(5)}"
            f"{match.group(6)}"
            f'{match.group(7)}PlannerAgent{match.group(9)}'
            f"scope &amp; task graph{match.group(11)}"
        )

    new_text, n = _PAIR.subn(repl, text, count=1)
    if n != 1:
        return text, "no_match"
    return new_text, "changed"


def main() -> int:
    paths = list(_ROOT.rglob("common-agent-structure.svg")) + list(
        _ROOT.rglob("common-agent-structure.html")
    )
    # Prefer project files only
    paths = [p for p in paths if "node_modules" not in p.parts]
    stats = {"changed": 0, "already": 0, "no_match": 0}
    for path in paths:
        raw = path.read_text(encoding="utf-8", errors="replace")
        if "PlannerAgent" not in raw or "OrchestratorAgent" not in raw:
            stats["no_match"] += 1
            continue
        new, status = transform(raw)
        stats[status] = stats.get(status, 0) + 1
        if status == "changed":
            path.write_text(new, encoding="utf-8", newline="\n")
    print(stats)
    print(f"files_scanned={len(paths)}")
    return 0 if stats.get("no_match", 0) == 0 or stats.get("changed", 0) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
