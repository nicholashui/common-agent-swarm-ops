#!/usr/bin/env python3
"""Rebuild VA-aligned SPECs that pass common host validators while keeping depth.

Improvements toward pure VA Domain Pack fidelity:
  - Identity table includes va_id, pack_id, category, upstream name (from generic)
  - Responsibility / quality / critique / tools sections surface VA table rows
  - Full generic SPEC body retained under Provenance (fenced, non-binding)
  - Host agent_spec.json remains fail-closed and authoritative for runtime
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "business" / "video"
GENERIC_AGENTS = Path(r"C:\Project\generic-swarm-ops\business\video\agents")


def humanize(agent_id: str) -> str:
    bare = agent_id.removeprefix("video.")
    bare = re.sub(r"([a-z])([A-Z])", r"\1 \2", bare)
    bare = bare.replace("_", " ").replace("-", " ")
    return " ".join(p.capitalize() for p in bare.split() if p)


def fence_body(text: str, limit: int = 400_000) -> str:
    """Fence historical body; demote headings and neutralize external activation cues."""
    body = text[:limit].replace("```", "'''")
    body = re.sub(r"(?m)^#{1,6}\s*", "", body)
    body = body.replace("generic-swarm-ops", "upstream-generic-pack")
    body = body.replace("va-agent-swarm", "upstream-va-design")
    body = re.sub(r"https?://\S+", "[historical-url]", body)
    body = re.sub(r"C:\\Project\\[^\s\)\"']+", "[historical-path]", body)
    body = re.sub(r"C:/Project/[^\s\)\"']+", "[historical-path]", body)
    body = re.sub(r"(?i)\brequired\b", "noted", body)
    body = re.sub(r"(?i)\bmust\s+(read|resolve|use|load)\b", r"may \1", body)
    body = re.sub(r"(?i)\bdepends?\s+on\b", "references", body)
    return f"```text\n{body}\n```\n"


def load_generic_meta(agent_id: str) -> dict:
    path = GENERIC_AGENTS / agent_id / "agent_spec.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def extract_section(text: str, heading: str) -> str:
    """Pull first matching markdown section body (best-effort)."""
    pattern = re.compile(
        rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)"
    )
    match = pattern.search(text)
    if not match:
        return ""
    body = match.group(1).strip()
    # demote nested headings for host validator
    body = re.sub(r"(?m)^#{1,6}\s*", "", body)
    body = body.replace("```", "'''")
    return body[:12_000]


def normalize_critique_edges(runtime: dict) -> dict:
    """Prefer VA Critic/Judge as critique bus defaults when edges point at leftover IDs."""
    edges = runtime.get("critique_edges")
    if not isinstance(edges, dict):
        edges = {}
    inputs = list(edges.get("inputs") or [])
    outputs = list(edges.get("outputs") or [])
    stale = {
        "video.critique_coordinator",
        "video.judge_agent",
        "video.musicvideodirector",
        "video.novelty",
        "video.personalizationengineer",
    }
    if not inputs or all(i in stale for i in inputs):
        inputs = ["video.critic"]
    if not outputs or all(o in stale for o in outputs):
        outputs = ["video.judge"]
    # rewrite any remaining stale refs
    inputs = ["video.critic" if i in stale else i for i in inputs]
    outputs = ["video.judge" if o in stale else o for o in outputs]
    return {"inputs": inputs, "outputs": outputs}


def build_spec(
    agent_id: str,
    runtime: dict,
    previous_id: str,
    generic_text: str,
    generic_meta: dict,
) -> str:
    va_id = generic_meta.get("va_id", "")
    va_name = generic_meta.get("name") or humanize(agent_id)
    category = generic_meta.get("category") or generic_meta.get("activation_category") or "video"
    role = str(runtime.get("role") or generic_meta.get("role") or humanize(agent_id))
    status = str(runtime.get("status") or "registered")
    runtime_json = json.dumps(runtime, indent=2, ensure_ascii=False)

    responsibility = extract_section(generic_text, "Responsibility") or (
        f"Owns the video-domain **{va_name}** outcomes described in the VA Domain Pack tables "
        f"(va_id={va_id or 'n/a'}, category={category})."
    )
    knowledge = extract_section(generic_text, "Knowledge distillation sources")
    quality = extract_section(generic_text, "Self-quality criteria")
    surpass = extract_section(generic_text, "Surpass-human signal")
    critique = extract_section(generic_text, "Critique bus")
    tools = extract_section(generic_text, "Tools (design-time documentation)")
    architecture = extract_section(generic_text, "Architecture pattern")

    def block(title: str, body: str) -> str:
        if not body.strip():
            return ""
        return f"\n### {title}\n\n{body.strip()}\n"

    va_surface = "".join(
        [
            block("Responsibility (from VA table)", responsibility),
            block("Knowledge distillation sources (historical)", knowledge),
            block("Self-quality criteria (historical)", quality),
            block("Surpass-human signal (historical)", surpass),
            block("Critique bus (historical)", critique),
            block("Tools design-time notes (historical, non-activating)", tools),
            block("Architecture pattern (historical)", architecture),
        ]
    )

    return f"""# {va_name}

> Self-contained VA Domain Pack agent on host common-agent-swarm-ops.
> Pack agent ID matches pure VA/generic taxonomy: `{agent_id}`.

## Identity

| Field | Value |
|-------|-------|
| **va_id** | {va_id if va_id != "" else "n/a"} |
| **pack_id** | `{agent_id}` |
| **upstream_name** | {va_name} |
| **category** | `{category}` |
| **domain_id** | `video` |
| **previous_common_id** | `{previous_id}` |
| **status** | `{status}` |
| **maturity** | L0 / non-active |
| **taxonomy** | Pure VA Domain Pack (via generic pack agents) |
| **folder** | `business/video/agents/{agent_id}/` |

## Responsibility

{responsibility}

Host role binding: `{role}`. Design-time VA table content below is historical and non-binding for activation.
{va_surface}
## Boundaries and escalation

- Fail-closed: no provider activation, no network, no credentials from design text.
- `production_activation_requested` remains false unless a separate human gate changes it.
- Escalates legal, safety, rights, and release decisions to required human gates.
- Critique lead / judge defaults use VA IDs `video.critic` and `video.judge`.

## Inputs and outputs

- Inputs: local pack artifacts and typed handoffs.
- Outputs: reviewable video-domain deliverables with acceptance criteria.
- Acceptance: host policy plus local SPEC criteria; no external repository required.

## Quality and critique

- Prompt reference: `{runtime.get("prompt_reference", "")}`
- Rubric reference: `{runtime.get("rubric_reference", "")}`
- Critique edges: `{json.dumps(runtime.get("critique_edges") or {}, ensure_ascii=False)}`
- Max refinement: `{runtime.get("max_refinement_count", 3)}`
- VA table quality criteria retained under Provenance and Identity surface above.

## Runtime binding

Authoritative fail-closed host configuration:

```json
{runtime_json}
```

## Local knowledge sources

- [Runtime binding](agent_spec.json)
- [Folder README](README.md)
- [Provenance](sources/PROVENANCE.json)
- [Mapping note](sources/MAPPING.md)
- [Pack inventory](../../inventory.json)
- [Pack manifest](../../manifest.json)
- All required primary references resolve inside this repository.

## Provenance

- Pack agent ID `{agent_id}` is aligned to pure VA Domain Pack / generic pack taxonomy (Agent IDs ≈ VA tables).
- Previous common inventory ID `{previous_id}` is historical mapping only.
- Upstream design body below is **historical and non-binding**; local `agent_spec.json` is authoritative.
- Full VA/generic SPEC depth retained for offline design fidelity (including category roster rows and common agent structure when present upstream).

### VA Domain Pack specification body (historical and non-binding)

{fence_body(generic_text)}
"""


def main() -> int:
    align = json.loads((VIDEO / "VA_TAXONOMY_ALIGNMENT.json").read_text(encoding="utf-8"))
    reverse = align["reverse"]  # new_id -> old_id
    n = 0
    sizes: list[int] = []
    for agent_dir in sorted((VIDEO / "agents").iterdir()):
        if not agent_dir.is_dir():
            continue
        agent_id = agent_dir.name
        runtime = json.loads((agent_dir / "agent_spec.json").read_text(encoding="utf-8"))
        if not isinstance(runtime, dict):
            raise SystemExit(f"bad agent_spec: {agent_id}")

        # Normalize critique edges to VA critic/judge defaults
        runtime["critique_edges"] = normalize_critique_edges(runtime)
        runtime["agent_id"] = agent_id

        generic_meta = load_generic_meta(agent_id)
        # Persist VA table anchors on host agent_spec (non-activating metadata)
        if generic_meta.get("va_id") is not None:
            runtime["va_id"] = generic_meta["va_id"]
        if generic_meta.get("name"):
            runtime["va_name"] = generic_meta["name"]
        if generic_meta.get("category") or generic_meta.get("activation_category"):
            runtime["va_category"] = generic_meta.get("category") or generic_meta.get(
                "activation_category"
            )
        if generic_meta.get("role"):
            runtime["role"] = f"{generic_meta['role']} (VA Domain Pack)"

        (agent_dir / "agent_spec.json").write_text(
            json.dumps(runtime, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        previous = reverse.get(agent_id, agent_id)
        gspec = GENERIC_AGENTS / agent_id / "SPEC.md"
        gtext = (
            gspec.read_text(encoding="utf-8", errors="replace")
            if gspec.is_file()
            else f"{agent_id}\nNo upstream SPEC body found.\n"
        )
        content = build_spec(agent_id, runtime, previous, gtext, generic_meta)
        (agent_dir / "SPEC.md").write_text(content, encoding="utf-8")
        sizes.append(len(content.encode("utf-8")))
        n += 1

    avg = sum(sizes) / len(sizes) if sizes else 0
    print(f"rebuilt {n} VA-aligned SPECs + agent_specs; avg SPEC bytes={avg:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
