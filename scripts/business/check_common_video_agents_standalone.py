#!/usr/bin/env python3
"""Agents-only standalone check (redo_migration.md §7.2).

Does NOT require business/video/corpus. Verifies 114 self-contained agent folders.
"""

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

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT  # noqa: E402
from app.video.migration.agent_mapping import AgentSourceMapValidator  # noqa: E402
from app.video.migration.specifications import (  # noqa: E402
    REQUIRED_HEADINGS,
    validate_specifications,
)

_EXTERNAL_REQUIRED = re.compile(
    r"(?is)(?:required|must\s+(?:read|resolve|use|load)|depends?\s+on).{0,100}"
    r"(?:https?://|generic-swarm-ops|va-agent-swarm|business/video/corpus)"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_REPOSITORY_ROOT)
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    video = root / "business" / "video"
    findings: list[str] = []

    inventory_path = video / "inventory.json"
    if not inventory_path.is_file():
        print("FAIL: missing inventory.json")
        return 1
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    entries = inventory.get("entries", [])
    if not isinstance(entries, list) or len(entries) != EXPECTED_VIDEO_AGENT_COUNT:
        findings.append(
            f"inventory count {len(entries) if isinstance(entries, list) else 'invalid'} "
            f"!= {EXPECTED_VIDEO_AGENT_COUNT}"
        )
    agent_ids = [
        e["agent_id"]
        for e in entries
        if isinstance(e, dict) and isinstance(e.get("agent_id"), str)
    ]

    map_path = video / "AGENT_SOURCE_MAP.json"
    if not map_path.is_file():
        findings.append("missing AGENT_SOURCE_MAP.json")
        source_map: object = {}
    else:
        source_map = json.loads(map_path.read_text(encoding="utf-8"))

    map_report = AgentSourceMapValidator().validate(
        inventory, source_map, video_root=video, repository_root=root
    )
    if not map_report.is_valid:
        findings.append(f"map invalid ({len(map_report.issues)} issues)")
        for issue in map_report.issues[:10]:
            findings.append(f"  map:{issue.code}:{issue.field}")

    for agent_id in agent_ids:
        agent_dir = video / "agents" / agent_id
        for required in (
            "agent_spec.json",
            "SPEC.md",
            "README.md",
            "sources/PROVENANCE.json",
            "sources/MAPPING.md",
        ):
            path = agent_dir / required
            if not path.is_file():
                findings.append(f"missing {agent_id}/{required}")
        # prompts/rubrics dirs
        for optional_dir in ("prompts", "rubrics", "sources"):
            if not (agent_dir / optional_dir).is_dir():
                findings.append(f"missing dir {agent_id}/{optional_dir}")
        spec_path = agent_dir / "SPEC.md"
        if spec_path.is_file():
            text = spec_path.read_text(encoding="utf-8")
            for heading in REQUIRED_HEADINGS:
                if f"## {heading}" not in text:
                    findings.append(f"{agent_id}: missing heading {heading}")
            if agent_id not in text:
                findings.append(f"{agent_id}: SPEC missing agent id")
            if _EXTERNAL_REQUIRED.search(text):
                findings.append(f"{agent_id}: SPEC has required external/corpus dependency")
            # Fail-closed runtime check unless pack production profile is enabled
            binding = json.loads((agent_dir / "agent_spec.json").read_text(encoding="utf-8"))
            production_profile = False
            profile_path = video / "production" / "profile.json"
            if profile_path.is_file():
                try:
                    production_profile = (
                        json.loads(profile_path.read_text(encoding="utf-8")).get("enabled") is True
                    )
                except (OSError, json.JSONDecodeError):
                    production_profile = False
            if binding.get("production_activation_requested") is True and not production_profile:
                findings.append(f"{agent_id}: production activation requested")
            model = binding.get("model_policy") or {}
            if (
                isinstance(model, dict)
                and model.get("network_access") is True
                and not production_profile
            ):
                findings.append(f"{agent_id}: network_access enabled")

    # Corpus must not be required
    if (video / "corpus").exists():
        # optional; do not fail
        pass

    # Reuse full specification validator when map present
    if map_report.is_valid:
        reviews_path = video / "SPEC_REVIEWS.json"
        reviews = (
            json.loads(reviews_path.read_text(encoding="utf-8"))
            if reviews_path.is_file()
            else None
        )
        spec_report = validate_specifications(
            video,
            repository_root=root,
            inventory=inventory,
            source_map=source_map,
            critical_reviews=reviews,
            use_existing_specs=True,
        )
        if not spec_report.is_valid:
            findings.append(f"specification validator failed ({len(spec_report.issues)})")
            for issue in spec_report.issues[:15]:
                findings.append(
                    f"  spec:{issue.code}:{issue.agent_id}:{issue.field}:{issue.message}"
                )

    if findings:
        print("AGENTS STANDALONE FAIL")
        for line in findings[:50]:
            print(line)
        if len(findings) > 50:
            print(f"... and {len(findings) - 50} more")
        return 1

    print(
        json.dumps(
            {
                "result": "AGENTS STANDALONE PASS",
                "agents": len(agent_ids),
                "corpus_required": False,
                "corpus_present": (video / "corpus").exists(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
