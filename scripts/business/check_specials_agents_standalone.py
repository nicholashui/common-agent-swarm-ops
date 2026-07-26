#!/usr/bin/env python3
"""Verify specials agents are self-contained like video agents (no corpus required)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.registry.specials_validator import SPECIAL_AGENT_IDS, SPECIALS_PACK_ROOT  # noqa: E402

REQUIRED_HEADINGS = (
    "Identity",
    "Responsibility",
    "Boundaries and escalation",
    "Inputs and outputs",
    "Quality and critique",
    "Runtime binding",
    "Local knowledge sources",
    "Provenance",
)
_EXTERNAL_REQUIRED = re.compile(
    r"(?is)(?:required|must\s+(?:read|resolve|use|load)|depends?\s+on).{0,100}"
    r"(?:https?://|generic-swarm-ops|va-agent-swarm|C:\\\\Project)"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_REPOSITORY_ROOT)
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    pack = root / SPECIALS_PACK_ROOT
    findings: list[str] = []

    if not pack.is_dir():
        print("FAIL: missing business/specials")
        return 1

    for agent_id in SPECIAL_AGENT_IDS:
        agent_dir = pack / "agents" / agent_id
        for rel in (
            "agent_spec.json",
            "SPEC.md",
            "README.md",
            "sources/PROVENANCE.json",
            "sources/MAPPING.md",
        ):
            if not (agent_dir / rel).is_file():
                findings.append(f"missing {agent_id}/{rel}")
        for d in ("prompts", "rubrics", "sources"):
            if not (agent_dir / d).is_dir():
                findings.append(f"missing dir {agent_id}/{d}")

        spec_path = agent_dir / "SPEC.md"
        if spec_path.is_file():
            text = spec_path.read_text(encoding="utf-8")
            for heading in REQUIRED_HEADINGS:
                if f"## {heading}" not in text:
                    findings.append(f"{agent_id}: missing heading {heading}")
            if agent_id not in text:
                findings.append(f"{agent_id}: SPEC missing agent id")
            if _EXTERNAL_REQUIRED.search(text):
                findings.append(f"{agent_id}: SPEC has required external dependency language")

        binding_path = agent_dir / "agent_spec.json"
        if binding_path.is_file():
            binding = json.loads(binding_path.read_text(encoding="utf-8"))
            if binding.get("status") != "draft":
                findings.append(f"{agent_id}: status is not draft")
            if binding.get("production_activation_requested") is True:
                findings.append(f"{agent_id}: production activation requested")
            if binding.get("allowed_tools"):
                findings.append(f"{agent_id}: allowed_tools not empty")
            model = binding.get("model_policy") or {}
            if isinstance(model, dict) and model.get("network_access") is not False:
                findings.append(f"{agent_id}: network_access not false")

    for pack_file in (
        "manifest.json",
        "AGENT_SOURCE_MAP.json",
        "ROSTER.json",
        "MAP.md",
        "README.md",
    ):
        if not (pack / pack_file).is_file():
            findings.append(f"missing pack file {pack_file}")
    # inventory.json is optional/forbidden when inventory_required=false
    if (pack / "inventory.json").is_file():
        findings.append(
            "unexpected inventory.json (specials pack sets inventory_required=false)"
        )

    if findings:
        print("SPECIALS AGENTS STANDALONE FAIL")
        for line in findings[:40]:
            print(line)
        if len(findings) > 40:
            print(f"... and {len(findings) - 40} more")
        return 1

    print(
        json.dumps(
            {
                "result": "SPECIALS AGENTS STANDALONE PASS",
                "agents": len(SPECIAL_AGENT_IDS),
                "corpus_required": False,
                "layout": "matches video self-contained agent folders",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
