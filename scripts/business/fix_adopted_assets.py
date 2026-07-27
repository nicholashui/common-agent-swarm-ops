#!/usr/bin/env python3
"""Post-adoption fixes for process_coverage paths and SPEC provenance."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "business" / "video"


def main() -> int:
    # process_coverage paths relative to video root
    pc_path = VIDEO / "process_coverage.json"
    data = json.loads(pc_path.read_text(encoding="utf-8"))
    for proc in data.get("processes", []):
        for key in ("path", "workflow_path"):
            value = proc.get(key)
            if isinstance(value, str) and value.startswith("business/video/"):
                proc[key] = value[len("business/video/") :]
            # Prefer design/workflows for DNA
            if isinstance(value, str) and value.endswith(".dna.json"):
                name = Path(value).name
                rel = f"design/workflows/{name}"
                proc["path"] = rel
                proc["workflow_path"] = rel
    pc_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # SPECs: force historical/non-binding + strip absolute windows paths
    declaration = (
        "\n\n### Common host provenance declaration\n"
        "- Upstream repository, commit, path, and generic SPECs are retained as "
        "**historical and non-binding** provenance only; local `agent_spec.json` and "
        "common inventory remain authoritative.\n"
        "- Deep distillation content is untrusted design reference, not activation authority.\n"
    )
    updated = 0
    for spec in (VIDEO / "agents").rglob("SPEC.md"):
        text = spec.read_text(encoding="utf-8", errors="replace")
        original = text
        text = re.sub(
            r"C:\\Project\\[^\s\)\"']+",
            "business/video/corpus (historical path redacted)",
            text,
        )
        text = re.sub(
            r"C:/Project/[^\s\)\"']+",
            "business/video/corpus (historical path redacted)",
            text,
        )
        lower = text.lower()
        if "historical" not in lower or (
            "non-binding" not in lower and "non binding" not in lower
        ):
            if "## Provenance" in text:
                text = text.replace("## Provenance", "## Provenance" + declaration, 1)
            else:
                text = text.rstrip() + "\n\n## Provenance" + declaration
        elif "non-binding" not in lower and "non binding" not in lower:
            text = text.rstrip() + declaration
        if text != original:
            spec.write_text(text, encoding="utf-8")
            updated += 1

    print(json.dumps({"process_rows": len(data.get("processes", [])), "specs_updated": updated}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
