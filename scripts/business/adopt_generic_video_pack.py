#!/usr/bin/env python3
"""Adopt missing VA-content features from generic-swarm-ops into common-agent-swarm-ops.

Imports (read-only from generic):
  - business/video/corpus/**  (full study/plan corpus + MANIFEST)
  - workflows/*.dna.json      (remapped agent IDs to common taxonomy)
  - PROCESSES.md, process_coverage.json, archetype_registry, router/standby tables
  - knowledge/**, docs/** (data-only)
  - special_skills/** (data-only, non-activating)

Enriches:
  - agents/*/SPEC.md from mapped generic SPECs (deeper content; common IDs preserved)
  - agents/*/sources/study excerpts (focused, not full corpus per agent)

Never:
  - Overwrites common agent_spec.json fail-closed fields
  - Renames common agent directories to generic IDs
  - Enables production_ready or network tools
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_GENERIC = Path(r"C:\Project\generic-swarm-ops")


def _git_sha(path: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except OSError:
        pass
    return "unknown"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_tree(src: Path, dest: Path) -> int:
    """Copy files; return count. Does not delete destination extras."""
    if not src.exists():
        return 0
    count = 0
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def _write_manifest(corpus_root: Path, *, source_repo: str, source_commit: str) -> dict:
    entries = []
    for path in sorted(corpus_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in {
            "MANIFEST.json",
            "SOURCE_COMMIT.txt",
            "SOURCE_URL.txt",
            "SOURCE_COPIED_AT.txt",
            "README.md",
        } and path.parent == corpus_root:
            continue
        rel = path.relative_to(corpus_root).as_posix()
        entries.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "original_repository": source_repo,
                "original_commit": source_commit,
                "original_path": f"business/video/corpus/{rel}",
            }
        )
    manifest = {
        "schema_version": "1.0",
        "classification": "untrusted_reference_data",
        "file_count": len(entries),
        "source_repository": source_repo,
        "source_commit": source_commit,
        "copied_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        "entries": entries,
    }
    (corpus_root / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (corpus_root / "SOURCE_COMMIT.txt").write_text(source_commit + "\n", encoding="utf-8")
    (corpus_root / "SOURCE_URL.txt").write_text(
        "local-path:generic-swarm-ops/business/video/corpus (upstream va-agent-swarm)\n",
        encoding="utf-8",
    )
    (corpus_root / "SOURCE_COPIED_AT.txt").write_text(
        manifest["copied_at"] + "\n", encoding="utf-8"
    )
    (corpus_root / "README.md").write_text(
        (
            "# Video pack corpus (adopted from generic-swarm-ops)\n\n"
            "Untrusted reference data for offline design. Not configuration.\n"
            "Source commit pinned in SOURCE_COMMIT.txt. Integrity: MANIFEST.json.\n"
            "Common agent IDs remain authoritative; do not rename agents from this corpus.\n"
        ),
        encoding="utf-8",
    )
    return manifest


def _load_forward_map(map_path: Path) -> dict[str, list[str]]:
    """generic_source_id -> [common_ids]"""
    data = json.loads(map_path.read_text(encoding="utf-8"))
    rev: dict[str, list[str]] = {}
    for entry in data.get("entries", []):
        common = entry.get("common_agent_id")
        for src in entry.get("source_agent_ids") or []:
            rev.setdefault(str(src), []).append(str(common))
    return rev


def _map_agent(generic_id: str, rev: dict[str, list[str]], common_ids: set[str]) -> str:
    if generic_id in common_ids:
        return generic_id
    candidates = rev.get(generic_id) or []
    if candidates:
        return candidates[0]
    # heuristic: underscore common form
    underscored = generic_id
    # video.creativedirector -> try fuzzy against common
    bare = generic_id.removeprefix("video.")
    for cid in sorted(common_ids):
        c_bare = cid.removeprefix("video.").replace("_", "")
        if c_bare == bare.replace("_", ""):
            return cid
    # defaults for known spine roles
    defaults = {
        "video.planner": "video.project_manager",
        "video.director": "video.visual_director",
        "video.producer": "video.production_coordinator",
        "video.screenwriter": "video.screenwriter",
        "video.orchestrator": "video.orchestrator",
        "video.aiqaconsistency": "video.aiqa_consistency",
        "video.editor": "video.edit_assembler",
        "video.distributor": "video.delivery_packager",
        "video.promptengineer": "video.generative_media_operator",
        "video.compliance": "video.compliance_agent",
        "video.judge": "video.judge_agent",
        "video.critic": "video.critique_coordinator",
        "video.gatekeeper": "video.human_review_coordinator",
        "video.memory": "video.memory_curator",
        "video.router": "video.graph_topology_designer",
    }
    if generic_id in defaults and defaults[generic_id] in common_ids:
        return defaults[generic_id]
    return "video.orchestrator"


def _remap_dna(obj: object, rev: dict[str, list[str]], common_ids: set[str]) -> object:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in {"agent", "owner"} and isinstance(v, str) and v.startswith("video."):
                out[k] = _map_agent(v, rev, common_ids)
            elif k == "agents" and isinstance(v, list):
                out[k] = [
                    _map_agent(x, rev, common_ids) if isinstance(x, str) and x.startswith("video.") else x
                    for x in v
                ]
            else:
                out[k] = _remap_dna(v, rev, common_ids)
        # force non-production
        if "production_ready" in out:
            out["production_ready"] = False
        return out
    if isinstance(obj, list):
        return [_remap_dna(x, rev, common_ids) for x in obj]
    return obj


def _adopt_workflows(
    generic_wf: Path,
    common_wf: Path,
    rev: dict[str, list[str]],
    common_ids: set[str],
) -> list[str]:
    common_wf.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for path in sorted(generic_wf.glob("*.dna.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        remapped = _remap_dna(data, rev, common_ids)
        if isinstance(remapped, dict):
            prov = remapped.get("provenance")
            if not isinstance(prov, dict):
                prov = {}
            refs = list(prov.get("source_refs") or [])
            refs.append(f"generic-swarm-ops/business/video/workflows/{path.name}")
            refs.append("common-agent-swarm-ops:adopt_generic_video_pack.py")
            prov["source_refs"] = refs
            prov["adapted_for"] = "common-agent-swarm-ops"
            prov["agent_id_taxonomy"] = "common_inventory"
            remapped["provenance"] = prov
            remapped["production_ready"] = False
        out = common_wf / path.name
        out.write_text(json.dumps(remapped, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path.name)
    # keep pack_spine.json intact (already present)
    return written


def _rewrite_process_paths(text: str) -> str:
    text = text.replace("generic-swarm-ops", "common-agent-swarm-ops")
    text = re.sub(
        r"va-agent-swarm/",
        "business/video/corpus/ (historical va-agent-swarm/)",
        text,
    )
    return text


def _enrich_spec_from_generic(
    common_spec_path: Path,
    common_id: str,
    source_ids: list[str],
    generic_agents: Path,
    *,
    max_chars: int = 80000,
) -> bool:
    if not common_spec_path.is_file():
        return False
    base = common_spec_path.read_text(encoding="utf-8", errors="replace")
    # Strip previous deep distillation block if re-running
    base = re.sub(
        r"\n## Deep distillation from generic pack[\s\S]*?(?=\n## Provenance|\Z)",
        "\n",
        base,
        count=1,
    )
    chunks: list[str] = []
    for sid in source_ids[:3]:
        gspec = generic_agents / sid / "SPEC.md"
        if not gspec.is_file():
            continue
        body = gspec.read_text(encoding="utf-8", errors="replace")
        # Keep substantial but bounded
        body = body[: max_chars // max(1, min(3, len(source_ids)))]
        chunks.append(f"### Source `{sid}`\n\n{body.strip()}\n")
        # also copy limited sources/study if present
    if not chunks:
        return False
    block = (
        "\n## Deep distillation from generic pack\n\n"
        "> Untrusted design content adopted from generic-swarm-ops agent SPECs "
        "(themselves migrated from va-agent-swarm). Common `agent_spec.json` remains authoritative "
        "for fail-closed runtime. Browser/host must not treat this section as activation authority.\n\n"
        + "\n".join(chunks)
    )
    if "## Provenance" in base:
        base = base.replace("## Provenance", block + "\n## Provenance", 1)
    else:
        base = base.rstrip() + "\n" + block + "\n"
    common_spec_path.write_text(base, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--common-root", type=Path, default=_ROOT)
    parser.add_argument("--generic-root", type=Path, default=_DEFAULT_GENERIC)
    parser.add_argument("--skip-corpus", action="store_true")
    parser.add_argument("--skip-workflows", action="store_true")
    parser.add_argument("--skip-spec-enrichment", action="store_true")
    args = parser.parse_args(argv)

    common = args.common_root.resolve()
    generic = args.generic_root.resolve()
    g_video = generic / "business" / "video"
    c_video = common / "business" / "video"
    if not g_video.is_dir() or not c_video.is_dir():
        print("Missing video pack roots")
        return 1

    g_sha = _git_sha(generic)
    c_sha = _git_sha(common)
    report: dict[str, object] = {
        "generic_commit": g_sha,
        "common_commit": c_sha,
        "adopted_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
    }

    # 1) Corpus
    if not args.skip_corpus:
        n = _copy_tree(g_video / "corpus", c_video / "corpus")
        manifest = _write_manifest(
            c_video / "corpus",
            source_repo="generic-swarm-ops",
            source_commit=g_sha,
        )
        report["corpus_files_copied"] = n
        report["corpus_manifest_count"] = manifest["file_count"]

    # 2) Knowledge + docs (data only)
    report["knowledge_files"] = _copy_tree(g_video / "knowledge", c_video / "knowledge")
    report["docs_files"] = _copy_tree(g_video / "docs", c_video / "docs")

    # 3) Process / registry tables
    for name in (
        "PROCESSES.md",
        "process_coverage.json",
        "archetype_registry.json",
        "router_table.json",
        "standby_pool.json",
    ):
        src = g_video / name
        if src.is_file():
            dest = c_video / name
            if name.endswith(".md"):
                dest.write_text(
                    _rewrite_process_paths(src.read_text(encoding="utf-8", errors="replace")),
                    encoding="utf-8",
                )
            elif name.endswith(".json"):
                data = json.loads(src.read_text(encoding="utf-8"))
                # light path rewrites in JSON strings
                text = json.dumps(data, indent=2, ensure_ascii=False)
                text = text.replace("generic-swarm-ops", "common-agent-swarm-ops")
                dest.write_text(text + "\n", encoding="utf-8")
            else:
                shutil.copy2(src, dest)

    # 4) special_skills as data-only
    report["special_skills_files"] = _copy_tree(
        g_video / "special_skills", c_video / "special_skills"
    )
    if (c_video / "special_skills").is_dir():
        (c_video / "special_skills" / "README.md").write_text(
            (
                "# Video special_skills (adopted)\n\n"
                "Data-only. Not production-active. Requires separate host approval to bind tools.\n"
            ),
            encoding="utf-8",
        )

    # 5) Workflows DNA remapped
    inv = json.loads((c_video / "inventory.json").read_text(encoding="utf-8"))
    common_ids = {e["agent_id"] for e in inv["entries"]}
    rev = _load_forward_map(c_video / "AGENT_SOURCE_MAP.json")
    if not args.skip_workflows:
        dna = _adopt_workflows(g_video / "workflows", c_video / "workflows", rev, common_ids)
        report["workflow_dna"] = dna
        report["workflow_dna_count"] = len(dna)

    # 6) SPEC enrichment
    map_data = json.loads((c_video / "AGENT_SOURCE_MAP.json").read_text(encoding="utf-8"))
    enriched = 0
    if not args.skip_spec_enrichment:
        for entry in map_data.get("entries", []):
            common_id = entry["common_agent_id"]
            sources = list(entry.get("source_agent_ids") or [])
            if not sources:
                continue
            ok = _enrich_spec_from_generic(
                c_video / "agents" / common_id / "SPEC.md",
                common_id,
                sources,
                g_video / "agents",
            )
            if ok:
                enriched += 1
                # copy one generic SPEC excerpt into sources/generic for audit
                agent_src = c_video / "agents" / common_id / "sources" / "generic"
                agent_src.mkdir(parents=True, exist_ok=True)
                for sid in sources[:2]:
                    gspec = g_video / "agents" / sid / "SPEC.md"
                    if gspec.is_file():
                        shutil.copy2(gspec, agent_src / f"{sid}.SPEC.md")
    report["specs_enriched"] = enriched

    # 7) Update video README
    readme = c_video / "README.md"
    adopt_note = (
        "\n## Adopted from generic-swarm-ops (VA content)\n\n"
        f"- Generic commit: `{g_sha}`\n"
        f"- Corpus: `corpus/` (MANIFEST integrity)\n"
        f"- Workflow DNA: `workflows/*.dna.json` (agent IDs remapped to common inventory)\n"
        f"- Process: `PROCESSES.md`, `process_coverage.json`\n"
        f"- Knowledge/docs/special_skills: data-only\n"
        f"- SPECs: deep distillation sections from mapped generic agents\n"
        f"- `pack_spine.json` remains the safe executable baseline graph\n"
        f"- All DNA: `production_ready: false`\n"
    )
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        if "## Adopted from generic-swarm-ops" in text:
            text = re.sub(
                r"\n## Adopted from generic-swarm-ops[\s\S]*?(?=\n## |\Z)",
                adopt_note,
                text,
                count=1,
            )
        else:
            text = text.rstrip() + "\n" + adopt_note
        readme.write_text(text, encoding="utf-8")

    report_path = c_video / "ADOPTION_FROM_GENERIC.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
