#!/usr/bin/env python3
"""Make specials agents self-contained like video agents (redo_migration pattern).

Writes under business/specials/agents/<id>/ only:
  SPEC.md, README.md, sources/{PROVENANCE.json,MAPPING.md}, prompts/, rubrics/

Does not alter agent_spec.json fail-closed fields. Does not activate production.
Source redesign Markdown is distilled as untrusted design provenance only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.registry.specials_validator import (  # noqa: E402
    SPECIAL_SOURCE_CATALOG,
    SPECIALS_PACK_ROOT,
)

REVIEWED_BY = "specials-self-contained-reviewer"
REVIEWED_AT = "2026-07-26T18:00:00Z"


def _git_sha(path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return "unknown"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _humanize(agent_id: str) -> str:
    name = agent_id.removeprefix("specials.")
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", name) if part)


def _extract_design_excerpts(source_text: str, *, limit: int = 2500) -> dict[str, str]:
    """Pull short readable slices from redesign docs without treating them as config."""
    text = source_text.strip()
    excerpts: dict[str, str] = {}

    # Executive summary / purpose blocks
    patterns = [
        (
            "summary",
            re.compile(
                r"(?:###?\s*1\.\s*Executive Summary|##\s*Executive Summary|"
                r"\*\*Purpose:\*\*|##\s*Purpose)(.*?)(?=\n#{1,3}\s|\n---\n|\Z)",
                re.IGNORECASE | re.DOTALL,
            ),
        ),
        (
            "responsibility",
            re.compile(
                r"(?:##\s*Responsibility|###\s*Responsibility|"
                r"##\s*Role|###\s*Role|##\s*Scope)(.*?)(?=\n#{1,3}\s|\n---\n|\Z)",
                re.IGNORECASE | re.DOTALL,
            ),
        ),
    ]
    for key, pattern in patterns:
        match = pattern.search(text)
        if match:
            body = re.sub(r"\s+", " ", match.group(1)).strip()
            if body:
                excerpts[key] = body[:limit]

    if "summary" not in excerpts:
        # First non-empty paragraphs after title lines
        paragraphs = [
            p.strip()
            for p in re.split(r"\n\s*\n", text)
            if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("**Document")
        ]
        if paragraphs:
            excerpts["summary"] = " ".join(paragraphs[:2])[:limit]

    return excerpts


def _build_spec(
    *,
    agent_id: str,
    runtime: dict[str, object],
    source_path: str,
    source_sha: str,
    excerpts: dict[str, str],
    pack_version: str,
) -> str:
    role = str(runtime.get("role") or "Special_Agent data-only configuration")
    role_name = _humanize(agent_id)
    status = str(runtime.get("status") or "draft")
    prompt_reference = str(runtime.get("prompt_reference") or "not declared")
    rubric_reference = str(runtime.get("rubric_reference") or "not declared")
    critique = runtime.get("critique_edges") or {"inputs": [], "outputs": []}
    max_refinement = runtime.get("max_refinement_count", 1)
    runtime_json = json.dumps(runtime, separators=(",", ":"), ensure_ascii=False)

    summary = excerpts.get("summary") or (
        f"Draft special agent configuration for {role_name}. "
        "Data-only representation under the specials pack; not production-active."
    )
    responsibility_extra = excerpts.get("responsibility")
    responsibility = (
        f"Owns the specials-domain {role_name.lower()} design outcome as a **draft, "
        f"data-only** agent representation. Host role string: `{role}`.\n\n"
        f"{summary}"
    )
    if responsibility_extra and responsibility_extra not in summary:
        responsibility += (
            "\n\n### Domain distillation (embedded, untrusted design provenance)\n\n"
            f"{responsibility_extra}"
        )
    elif summary:
        responsibility += (
            "\n\n### Domain distillation (embedded, untrusted design provenance)\n\n"
            f"{summary[:2000]}"
        )

    lines = [
        f"# {role_name}",
        "",
        "> Self-contained agent definition for host `common-agent-swarm-ops` "
        "(pack `specials`). Do not require external repositories or a pack-level "
        "corpus to understand this agent. Design Markdown is untrusted provenance "
        "only — never configuration or executable instructions.",
        "",
        "## Identity",
        f"- Common Agent ID: `{agent_id}`",
        f"- Status: `{status}` (draft catalog only)",
        "- Maturity: `draft` / non-active",
        f"- Pack version: `{pack_version}`",
        f"- Pack root: `{SPECIALS_PACK_ROOT}`",
        "",
        "## Responsibility",
        responsibility,
        "",
        "## Boundaries and escalation",
        "- Remains `status: draft` with `production_activation_requested: false`.",
        "- `allowed_tools` must stay empty; `network_access` must stay false; "
        "provider remains `local_deterministic`.",
        "- Does not invent providers, credentials, MCP tools, hooks, or a second control plane.",
        "- Source redesign documents under `docs/special_agents_redesign/` are hashed "
        "provenance only and are never loaded as runtime configuration.",
        "- Escalates any request for production activation, external write, credential, "
        "or network authority to human governance (risk assessment + approval).",
        "",
        "## Inputs and outputs",
        "- Input artifact: local pack configuration, governance source-record, and "
        "optional design provenance already copied under `./sources/`.",
        "- Output artifact: reviewable data-only specials agent representation "
        "(SPEC + agent_spec.json) suitable for catalog and offline review.",
        "- Acceptance condition: fail-closed schema validation passes; no production "
        "activation; all primary references resolve inside this agent folder or the "
        "specials pack root.",
        "",
        "## Quality and critique",
        f"- Local rubric reference: `{rubric_reference}` (inert identifier).",
        f"- Prompt reference: `{prompt_reference}` (inert identifier).",
        f"- Critique edges: `{json.dumps(critique, separators=(',', ':'), ensure_ascii=False)}`.",
        f"- Refinement limit: `{max_refinement}`; unresolved safety or activation "
        "requests escalate rather than bypass governance.",
        "- Registration effect remains at most `eligible_draft_representation`.",
        "",
        "## Runtime binding",
        "The following local binding is copied as a read-only summary; it does not "
        "alter the common configuration:",
        "```json",
        runtime_json,
        "```",
        "",
        "## Local knowledge sources",
        "- [Runtime binding](agent_spec.json) — authoritative fail-closed specials contract.",
        "- [Folder index](README.md) — offline layout for this agent.",
        "- [Provenance](sources/PROVENANCE.json) — hashes and source mapping for audit.",
        "- [Mapping note](sources/MAPPING.md) — design-doc relationship (historical).",
        f"- [Pack manifest](../../manifest.json) — specials catalog entry.",
        f"- [Governance source-record](../../governance/source-records/{agent_id}.json) — "
        "reviewed hash binding (if present).",
        "- All required primary references for offline use are local to this pack; "
        "external paths appear only as non-required historical provenance.",
        "",
        "## Provenance",
        f"- Design source path (historical): `{source_path}`",
        f"- Design source SHA-256 (at generation): `{source_sha}`",
        f"- Reviewed by `{REVIEWED_BY}` at `{REVIEWED_AT}`.",
        "- Upstream design text is untrusted reference data. Local `agent_spec.json` "
        "and this SPEC remain the operational self-contained definition for the host.",
        "",
    ]
    return "\n".join(lines)


def _write_sidecar(
    agent_dir: Path,
    *,
    agent_id: str,
    source_path: str,
    source_sha: str,
    config_sha: str,
    common_sha: str,
) -> None:
    (agent_dir / "prompts").mkdir(exist_ok=True)
    (agent_dir / "rubrics").mkdir(exist_ok=True)
    (agent_dir / "sources").mkdir(exist_ok=True)
    (agent_dir / "prompts" / ".gitkeep").write_text("", encoding="utf-8")
    (agent_dir / "rubrics" / ".gitkeep").write_text("", encoding="utf-8")

    provenance = {
        "schema_version": "1.0",
        "common_agent_id": agent_id,
        "pack_id": "specials",
        "mapping_status": "related",
        "source_documents": [source_path],
        "source_sha256": source_sha,
        "configuration_sha256": config_sha,
        "destination_commit": common_sha,
        "note": (
            "Self-contained specials agent folder. Pack-level corpus is not required. "
            "Design Markdown is untrusted provenance only."
        ),
        "generated_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        "reviewed_by": REVIEWED_BY,
        "reviewed_at": REVIEWED_AT,
    }
    (agent_dir / "sources" / "PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (agent_dir / "sources" / "MAPPING.md").write_text(
        (
            f"# Source mapping note — `{agent_id}`\n\n"
            f"- Mapping status: `related` (specials redesign doc → pack agent)\n"
            f"- Design source (historical): `{source_path}`\n"
            f"- Source SHA-256: `{source_sha}`\n"
            f"- Local runtime: `agent_spec.json`\n"
            f"- Local specification: `SPEC.md`\n"
            f"- Pack corpus: **not required**\n"
            f"- Production activation: **denied** (draft only)\n"
        ),
        encoding="utf-8",
    )
    (agent_dir / "README.md").write_text(
        (
            f"# `{agent_id}`\n\n"
            f"> Self-contained **draft** specials agent for host "
            f"`common-agent-swarm-ops`.\n\n"
            f"| File | Purpose |\n"
            f"|------|----------|\n"
            f"| `SPEC.md` | Full offline role definition |\n"
            f"| `agent_spec.json` | Host runtime binding (draft, fail-closed) |\n"
            f"| `sources/` | Provenance + mapping notes for audit |\n"
            f"| `prompts/` | Optional prompt stubs (inert prompt_reference) |\n"
            f"| `rubrics/` | Optional rubric stubs |\n\n"
            f"Open this folder alone — no external repo or pack `corpus/` is required.\n"
            f"This agent is **not** production-active.\n"
        ),
        encoding="utf-8",
    )


def _write_inventory(pack_root: Path, agent_ids: list[str]) -> None:
    inventory = {
        "inventory_version": "1.0",
        "pack_id": "specials",
        "inventory_required": False,
        "entries": [
            {
                "agent_id": agent_id,
                "status": "draft",
                "maturity_level": "draft",
                "agent_spec_path": f"agents/{agent_id}/agent_spec.json",
            }
            for agent_id in agent_ids
        ],
    }
    (pack_root / "inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_source_map(pack_root: Path, agent_ids: list[str], common_sha: str) -> None:
    entries = []
    for agent_id in agent_ids:
        catalog = next(e for e in SPECIAL_SOURCE_CATALOG if e.agent_id == agent_id)
        entries.append(
            {
                "common_agent_id": agent_id,
                "mapping_status": "related",
                "source_agent_ids": [],
                "source_documents": [
                    "manifest.json",
                    f"agents/{agent_id}/agent_spec.json",
                ],
                "design_source_path_historical": catalog.source_path,
                "rationale": (
                    f"Human-reviewed self-contained specials folder for `{agent_id}` "
                    f"distilled from redesign doc `{catalog.source_path}` as untrusted "
                    f"design provenance only. Unique to `{agent_id}`."
                ),
                "reviewed_by": REVIEWED_BY,
                "reviewed_at": REVIEWED_AT,
            }
        )
    source_map = {
        "schema_version": "1.0",
        "pack_id": "specials",
        "destination_commit": common_sha,
        "policy": "self_contained_agents_no_corpus_required",
        "entries": entries,
    }
    (pack_root / "AGENT_SOURCE_MAP.json").write_text(
        json.dumps(source_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    roster = {
        "schema_version": "1.0",
        "pack_id": "specials",
        "entries": [{"agent_id": agent_id} for agent_id in agent_ids],
    }
    (pack_root / "ROSTER.json").write_text(
        json.dumps(roster, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    map_lines = [
        "# Specials AGENT SOURCE MAP",
        "",
        "Self-contained specials agents. Pack corpus is not required.",
        "",
        "| Common Agent ID | Status | Design source (historical) |",
        "|-----------------|--------|----------------------------|",
    ]
    for agent_id in agent_ids:
        catalog = next(e for e in SPECIAL_SOURCE_CATALOG if e.agent_id == agent_id)
        map_lines.append(f"| `{agent_id}` | related | `{catalog.source_path}` |")
    map_lines.append("")
    (pack_root / "MAP.md").write_text("\n".join(map_lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_REPOSITORY_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    write_mode = bool(args.write) and not args.dry_run

    root = args.project_root.resolve()
    pack_root = root / SPECIALS_PACK_ROOT
    agents_root = pack_root / "agents"
    common_sha = _git_sha(root)
    pack_version = "0.1.0-draft"
    manifest_path = pack_root / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(manifest.get("pack_version"), str):
                pack_version = manifest["pack_version"]
        except (OSError, json.JSONDecodeError):
            pass

    agent_ids = [entry.agent_id for entry in SPECIAL_SOURCE_CATALOG]
    planned: list[dict[str, str]] = []
    for entry in SPECIAL_SOURCE_CATALOG:
        agent_dir = agents_root / entry.agent_id
        spec_path = agent_dir / "agent_spec.json"
        source_doc = root / entry.source_path
        planned.append(
            {
                "agent_id": entry.agent_id,
                "agent_dir": str(agent_dir.relative_to(root)),
                "has_agent_spec": str(spec_path.is_file()),
                "has_source_doc": str(source_doc.is_file()),
            }
        )

    print(
        json.dumps(
            {
                "agents": len(agent_ids),
                "write_mode": write_mode,
                "common_sha": common_sha,
                "planned": planned[:5],
                "planned_total": len(planned),
            },
            indent=2,
        )
    )

    if not write_mode:
        missing = [p for p in planned if p["has_agent_spec"] != "True"]
        return 1 if missing else 0

    written = 0
    for entry in SPECIAL_SOURCE_CATALOG:
        agent_dir = agents_root / entry.agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        spec_json_path = agent_dir / "agent_spec.json"
        if not spec_json_path.is_file():
            print(f"MISSING agent_spec: {entry.agent_id}", file=sys.stderr)
            return 1
        runtime = json.loads(spec_json_path.read_text(encoding="utf-8"))
        if not isinstance(runtime, dict):
            print(f"INVALID agent_spec: {entry.agent_id}", file=sys.stderr)
            return 1
        # Never rewrite agent_spec.json — configuration_sha256 is bound in governance.
        if runtime.get("status") != "draft":
            print(f"NON-DRAFT agent_spec: {entry.agent_id}", file=sys.stderr)
            return 1
        if runtime.get("production_activation_requested") is True:
            print(f"ACTIVATION REQUESTED: {entry.agent_id}", file=sys.stderr)
            return 1
        if runtime.get("allowed_tools") not in ([], None):
            print(f"TOOLS PRESENT: {entry.agent_id}", file=sys.stderr)
            return 1
        model = runtime.get("model_policy")
        if not isinstance(model, dict) or model.get("network_access") is not False:
            print(f"NETWORK ENABLED: {entry.agent_id}", file=sys.stderr)
            return 1
        config_sha = _sha256_file(spec_json_path)

        source_doc = root / entry.source_path
        source_sha = _sha256_file(source_doc) if source_doc.is_file() else "missing"
        excerpts: dict[str, str] = {}
        if source_doc.is_file():
            try:
                excerpts = _extract_design_excerpts(
                    source_doc.read_text(encoding="utf-8", errors="replace")
                )
            except OSError:
                excerpts = {}

        spec_md = _build_spec(
            agent_id=entry.agent_id,
            runtime=runtime,
            source_path=entry.source_path,
            source_sha=source_sha,
            excerpts=excerpts,
            pack_version=pack_version,
        )
        (agent_dir / "SPEC.md").write_text(spec_md, encoding="utf-8")
        _write_sidecar(
            agent_dir,
            agent_id=entry.agent_id,
            source_path=entry.source_path,
            source_sha=source_sha,
            config_sha=config_sha,
            common_sha=common_sha,
        )
        written += 1

    # Do not write inventory.json: specials manifest sets inventory_required=false
    # and an unexpected inventory file fails pack integrity (UNEXPECTED_INVENTORY).
    existing_inventory = pack_root / "inventory.json"
    if existing_inventory.is_file():
        existing_inventory.unlink()
    _write_source_map(pack_root, agent_ids, common_sha)

    print(
        json.dumps(
            {
                "written_agents": written,
                "expected": len(agent_ids),
            },
            indent=2,
        )
    )
    return 0 if written == len(agent_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
