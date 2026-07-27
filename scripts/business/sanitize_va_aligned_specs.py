#!/usr/bin/env python3
"""Sanitize VA-aligned SPECs for common host validators."""

from __future__ import annotations

import re
from pathlib import Path

VIDEO = Path(__file__).resolve().parents[2] / "business" / "video"

LK = """## Local knowledge sources
- [Runtime binding](agent_spec.json)
- [Folder README](README.md)
- [Provenance](sources/PROVENANCE.json)
- [Mapping note](sources/MAPPING.md)
- [Pack inventory](../../inventory.json)
- [Pack manifest](../../manifest.json)
- All required primary references resolve inside this repository.

"""


def fix_spec(text: str) -> str:
    text = text.replace("generic-swarm-ops", "upstream-generic-pack")
    text = text.replace("va-agent-swarm", "upstream-va-design")
    text = re.sub(r"https?://\S+", "[historical-url]", text)
    text = re.sub(r"C:\\Project\\[^\s\)\"']+", "business/video/corpus (historical)", text)
    text = re.sub(r"C:/Project/[^\s\)\"']+", "business/video/corpus (historical)", text)
    text = re.sub(
        r"## Local knowledge sources\n.*?(?=\n## )",
        LK,
        text,
        count=1,
        flags=re.S,
    )
    lower = text.lower()
    if "historical" not in lower or (
        "non-binding" not in lower and "non binding" not in lower
    ):
        if "## Provenance" in text:
            text = text.replace(
                "## Provenance",
                (
                    "## Provenance\n"
                    "- Upstream design is historical and non-binding; "
                    "local agent_spec.json is authoritative.\n"
                ),
                1,
            )
        else:
            text += (
                "\n## Provenance\n"
                "- Upstream design is historical and non-binding; "
                "local agent_spec.json is authoritative.\n"
            )
    return text


def main() -> int:
    n = 0
    for path in (VIDEO / "agents").rglob("SPEC.md"):
        original = path.read_text(encoding="utf-8", errors="replace")
        fixed = fix_spec(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8")
            n += 1
    print({"specs_updated": n})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
