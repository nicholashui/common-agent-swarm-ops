"""Inventory and usage report for pack agent knowledge assets.

Records *all* pack knowledge surfaces bound or enforced during a run
(prompt, skill, rubric, agent_spec, sources, rethink, goldens, etc.),
not only RETHINK items — so test / UAT / production can inspect what
knowledge an agent execution was bound to.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from app.video.pack_runtime.loader import PackAgentBundle
from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT

_KNOWLEDGE_SCHEMA = "pack.knowledge_usage.v1"


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()[:16]


def _rel(agent_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(agent_dir.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _file_asset(
    *,
    asset_id: str,
    kind: str,
    path: Path,
    agent_dir: Path,
    status: str,
    usage: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    exists = path.is_file()
    content_hash = None
    size = 0
    if exists:
        try:
            raw = path.read_bytes()
            size = len(raw)
            content_hash = _sha256_bytes(raw)
        except OSError:
            exists = False
    return {
        "id": asset_id,
        "kind": kind,
        "path": _rel(agent_dir, path) if path else None,
        "present": exists,
        "status": status if exists else "missing",
        "usage": usage if exists else "not_available",
        "content_hash": content_hash,
        "size_bytes": size,
        "details": details or {},
    }


def _prompt_sections(prompt_text: str) -> list[str]:
    sections: list[str] = []
    if "<!-- RETHINK_100:start -->" in prompt_text or "RETHINK_100 operating" in prompt_text:
        sections.append("rethink_100")
    if re.search(r"##\s+Responsibility|###\s+Responsibility", prompt_text):
        sections.append("responsibility")
    if "Self-evaluation" in prompt_text or "L1 Spec" in prompt_text:
        sections.append("self_evaluation")
    if "Does not own" in prompt_text or "does_not_own" in prompt_text:
        sections.append("does_not_own")
    if "Architecture pattern" in prompt_text:
        sections.append("architecture_pattern")
    if "Tools" in prompt_text or "allowlist" in prompt_text.lower():
        sections.append("tools_allowlist")
    if "Collaboration" in prompt_text or "critique" in prompt_text.lower():
        sections.append("collaboration_critique")
    return sections


def build_knowledge_usage(
    bundle: PackAgentBundle,
    *,
    correlation_id: str,
    enforced: set[str] | None = None,
    mode: str = "offline_pack_runner",
) -> dict[str, Any]:
    """Build a full knowledge-usage report for one pack agent run.

    Status vocabulary:
      - missing: file not on disk
      - available: on disk but not loaded into this run
      - bound: loaded into the run working set (prompt/skill/rubric/spec/rethink)
      - enforced: actively checked or used by runner logic this run
    """
    enforced = enforced or set()
    agent_dir = bundle.agent_dir
    assets: list[dict[str, Any]] = []

    # --- Core harness (always bound when loader succeeded) ---
    prompt_path = agent_dir / "prompts" / f"{bundle.prompt_reference}.md"
    rubric_path = agent_dir / "rubrics" / f"{bundle.rubric_reference}.json"
    skill_path = agent_dir / "skills" / "SKILL.md"
    skill_int = agent_dir / "skills" / "integration.json"
    skill_bind = agent_dir / "skills" / "bindings.json"
    spec_path = agent_dir / "agent_spec.json"

    def status_for(asset_id: str, default_bound: bool = True) -> str:
        if asset_id in enforced:
            return "enforced"
        return "bound" if default_bound else "available"

    assets.append(
        _file_asset(
            asset_id=f"spec:{bundle.agent_id}",
            kind="agent_spec",
            path=spec_path,
            agent_dir=agent_dir,
            status=status_for(f"spec:{bundle.agent_id}"),
            usage="runtime_binding_authoritative",
            details={
                "schema_version": bundle.agent_spec.get("schema_version"),
                "status": bundle.agent_spec.get("status"),
                "model_policy": bundle.agent_spec.get("model_policy"),
                "production_activation_requested": bundle.agent_spec.get(
                    "production_activation_requested"
                ),
                "improvement": bundle.agent_spec.get("improvement"),
            },
        )
    )
    assets.append(
        _file_asset(
            asset_id=f"prompt:{bundle.prompt_reference}",
            kind="prompt",
            path=prompt_path,
            agent_dir=agent_dir,
            status=status_for(f"prompt:{bundle.prompt_reference}"),
            usage="system_prompt_loaded",
            details={
                "reference": bundle.prompt_reference,
                "text_hash": _sha256_text(bundle.prompt_text),
                "sections_detected": _prompt_sections(bundle.prompt_text),
                "char_count": len(bundle.prompt_text),
            },
        )
    )
    dims = []
    l2 = (bundle.rubric.get("layers") or {}).get("L2_rubric") or {}
    for d in l2.get("dimensions") or []:
        if isinstance(d, dict):
            dims.append(
                {
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "source": d.get("source"),
                }
            )
    assets.append(
        _file_asset(
            asset_id=f"rubric:{bundle.rubric_reference}",
            kind="rubric",
            path=rubric_path,
            agent_dir=agent_dir,
            status=status_for(f"rubric:{bundle.rubric_reference}"),
            usage="l2_scoring",
            details={
                "reference": bundle.rubric_reference,
                "pass_threshold": l2.get("pass_threshold"),
                "dimensions": dims,
                "rethink_100": bundle.rubric.get("rethink_100"),
            },
        )
    )
    assets.append(
        _file_asset(
            asset_id=f"skill:{bundle.agent_id}",
            kind="skill",
            path=skill_path,
            agent_dir=agent_dir,
            status=status_for(f"skill:{bundle.agent_id}"),
            usage="harness_instructions",
            details={
                "text_hash": _sha256_text(bundle.skill_markdown),
                "has_rethink_section": "RETHINK_100" in bundle.skill_markdown,
                "bindings": bundle.skill_bindings,
            },
        )
    )
    assets.append(
        _file_asset(
            asset_id=f"skill_integration:{bundle.agent_id}",
            kind="skill_integration",
            path=skill_int,
            agent_dir=agent_dir,
            status=status_for(f"skill_integration:{bundle.agent_id}"),
            usage="harness_metadata",
            details={"keys": list(bundle.skill_integration.keys())},
        )
    )
    if skill_bind.is_file():
        assets.append(
            _file_asset(
                asset_id=f"skill_bindings:{bundle.agent_id}",
                kind="skill_bindings",
                path=skill_bind,
                agent_dir=agent_dir,
                status="bound",
                usage="special_skill_bindings",
                details=bundle.skill_bindings if isinstance(bundle.skill_bindings, dict) else {},
            )
        )

    # SPEC / README (available knowledge; not always enforced offline)
    for name, kind in (("SPEC.md", "spec_doc"), ("README.md", "readme")):
        p = agent_dir / name
        assets.append(
            _file_asset(
                asset_id=f"{kind}:{bundle.agent_id}",
                kind=kind,
                path=p,
                agent_dir=agent_dir,
                status="available" if p.is_file() else "missing",
                usage="design_documentation" if p.is_file() else "not_available",
            )
        )

    # Sources tree
    sources = agent_dir / "sources"
    catalog_path = sources / "SOURCE_CATALOG.json"
    distill_path = sources / "DISTILLATION_PLAN.json"
    acquire_path = sources / "ACQUIRE.md"
    provenance_path = sources / "PROVENANCE.json"
    mapping_path = sources / "MAPPING.md"
    rethink_path = sources / "RETHINK_100_APPLIED.json"

    catalog_entries: list[dict[str, Any]] = []
    if catalog_path.is_file():
        try:
            cat = json.loads(catalog_path.read_text(encoding="utf-8"))
            if isinstance(cat, dict):
                entries = cat.get("sources") or cat.get("entries") or cat.get("items") or []
                if isinstance(entries, list):
                    for e in entries[:50]:
                        if isinstance(e, dict):
                            catalog_entries.append(
                                {
                                    "id": e.get("id") or e.get("source_id") or e.get("name"),
                                    "title": e.get("title") or e.get("name"),
                                    "type": e.get("type") or e.get("kind"),
                                }
                            )
                elif isinstance(cat, dict):
                    # flat map form
                    for k, v in list(cat.items())[:50]:
                        if k in {"schema_version", "generated_at", "agent_id"}:
                            continue
                        if isinstance(v, dict):
                            catalog_entries.append(
                                {
                                    "id": k,
                                    "title": v.get("title") or v.get("name") or k,
                                    "type": v.get("type") or v.get("kind"),
                                }
                            )
        except (OSError, json.JSONDecodeError):
            pass

    assets.append(
        _file_asset(
            asset_id=f"source_catalog:{bundle.agent_id}",
            kind="source_catalog",
            path=catalog_path,
            agent_dir=agent_dir,
            status=status_for(
                f"source_catalog:{bundle.agent_id}",
                default_bound=bundle.has_source_catalog,
            ),
            usage="distillation_grounding",
            details={"entry_count": len(catalog_entries), "entries": catalog_entries[:30]},
        )
    )
    assets.append(
        _file_asset(
            asset_id=f"distillation_plan:{bundle.agent_id}",
            kind="distillation_plan",
            path=distill_path,
            agent_dir=agent_dir,
            status=status_for(
                f"distillation_plan:{bundle.agent_id}",
                default_bound=bundle.has_distillation_plan,
            ),
            usage="distillation_plan",
        )
    )
    assets.append(
        _file_asset(
            asset_id=f"acquire:{bundle.agent_id}",
            kind="acquire_runbook",
            path=acquire_path,
            agent_dir=agent_dir,
            status="bound" if bundle.has_acquire_runbook else "missing",
            usage="source_acquire_guidance",
        )
    )
    for p, kind, usage in (
        (provenance_path, "provenance", "provenance_record"),
        (mapping_path, "mapping", "id_mapping_notes"),
    ):
        assets.append(
            _file_asset(
                asset_id=f"{kind}:{bundle.agent_id}",
                kind=kind,
                path=p,
                agent_dir=agent_dir,
                status="available" if p.is_file() else "missing",
                usage=usage if p.is_file() else "not_available",
            )
        )

    # RETHINK record + per-item rows
    rethink_items: list[dict[str, Any]] = []
    rethink_ids: list[int] = []
    if rethink_path.is_file():
        try:
            rdoc = json.loads(rethink_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rdoc = {}
        if isinstance(rdoc, dict):
            rethink_ids = [
                int(x)
                for x in (rdoc.get("item_ids") or [])
                if str(x).isdigit() or isinstance(x, int)
            ]
            titles = rdoc.get("item_titles") or {}
            models = rdoc.get("design_time_models") or []
            obligations = rdoc.get("obligations") or []
            prompt_has_rethink = "rethink_100" in _prompt_sections(bundle.prompt_text)
            assets.append(
                _file_asset(
                    asset_id=f"rethink_record:{bundle.agent_id}",
                    kind="rethink_record",
                    path=rethink_path,
                    agent_dir=agent_dir,
                    status="bound",
                    usage="guidance_bound" if prompt_has_rethink else "record_bound",
                    details={
                        "item_ids": rethink_ids,
                        "item_count": len(rethink_ids),
                        "design_time_models": models,
                        "obligation_count": len(obligations)
                        if isinstance(obligations, list)
                        else 0,
                        "embedded_in_prompt": prompt_has_rethink,
                        "embedded_in_skill": "RETHINK_100" in bundle.skill_markdown,
                        "source_doc": rdoc.get("source_doc"),
                        "applied_at": rdoc.get("applied_at"),
                    },
                )
            )
            for iid in rethink_ids:
                title = ""
                if isinstance(titles, dict):
                    title = str(titles.get(str(iid)) or titles.get(iid) or "")
                item_status = "bound" if prompt_has_rethink else "available"
                # Mark enforced only if runner explicitly enforced (rare offline)
                item_id = f"rethink:item:{iid}"
                if item_id in enforced:
                    item_status = "enforced"
                rethink_items.append(
                    {
                        "id": item_id,
                        "kind": "rethink_item",
                        "item_id": iid,
                        "title": title,
                        "status": item_status,
                        "usage": (
                            "guidance_in_prompt_and_skill" if prompt_has_rethink else "record_only"
                        ),
                        "present": True,
                    }
                )
            assets.extend(rethink_items)
    else:
        assets.append(
            {
                "id": f"rethink_record:{bundle.agent_id}",
                "kind": "rethink_record",
                "path": "sources/RETHINK_100_APPLIED.json",
                "present": False,
                "status": "missing",
                "usage": "not_available",
                "details": {},
            }
        )

    # Excerpts + study trees (list, don't load full text)
    for sub, kind in (
        ("excerpts", "source_excerpt"),
        ("study", "source_study"),
        ("generic", "source_generic"),
    ):
        folder = sources / sub
        if not folder.is_dir():
            continue
        files = sorted(folder.rglob("*"))
        listed = [f for f in files if f.is_file()][:40]
        for f in listed:
            assets.append(
                _file_asset(
                    asset_id=f"{kind}:{_rel(agent_dir, f)}",
                    kind=kind,
                    path=f,
                    agent_dir=agent_dir,
                    status="available",
                    usage="offline_corpus_grounding",
                )
            )

    # Golden / baseline eval knowledge
    golden = EVALS_AGENTS_ROOT / bundle.agent_id / "golden.json"
    baseline = EVALS_AGENTS_ROOT / bundle.agent_id / "baseline_protocol.json"
    assets.append(
        _file_asset(
            asset_id=f"golden:{bundle.agent_id}",
            kind="golden_eval",
            path=golden,
            agent_dir=agent_dir if golden.is_file() else agent_dir,
            status="available" if golden.is_file() else "missing",
            usage="test_fixture" if golden.is_file() else "not_available",
        )
    )
    # path relative fix for evals outside agent dir
    if golden.is_file():
        assets[-1]["path"] = str(golden).replace("\\", "/")
    if baseline.is_file():
        assets.append(
            {
                "id": f"baseline_protocol:{bundle.agent_id}",
                "kind": "baseline_protocol",
                "path": str(baseline).replace("\\", "/"),
                "present": True,
                "status": "available",
                "usage": "human_baseline_protocol",
                "content_hash": _sha256_bytes(baseline.read_bytes()),
                "size_bytes": baseline.stat().st_size,
                "details": {},
            }
        )

    # Critique edges as collaboration knowledge
    assets.append(
        {
            "id": f"critique_edges:{bundle.agent_id}",
            "kind": "critique_edges",
            "path": "agent_spec.json#critique_edges",
            "present": True,
            "status": "bound",
            "usage": "collaboration_routing",
            "details": {
                "inputs": list(bundle.critique_edges.get("inputs") or ()),
                "outputs": list(bundle.critique_edges.get("outputs") or ()),
            },
        }
    )

    # Summary counts
    by_status: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for a in assets:
        st = str(a.get("status") or "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        k = str(a.get("kind") or "unknown")
        by_kind[k] = by_kind.get(k, 0) + 1

    bound_ids = [
        str(a["id"])
        for a in assets
        if a.get("status") in {"bound", "enforced"} and a.get("present", True)
    ]
    enforced_ids = [str(a["id"]) for a in assets if a.get("status") == "enforced"]

    return {
        "schema_version": _KNOWLEDGE_SCHEMA,
        "agent_id": bundle.agent_id,
        "correlation_id": correlation_id,
        "mode": mode,
        "summary": {
            "total_assets": len(assets),
            "by_status": by_status,
            "by_kind": by_kind,
            "bound_count": len(bound_ids),
            "enforced_count": len(enforced_ids),
            "rethink_item_count": len(rethink_ids),
            "source_catalog_entry_count": len(catalog_entries),
            "rubric_dimension_count": len(dims),
        },
        "index": {
            "prompt_reference": bundle.prompt_reference,
            "rubric_reference": bundle.rubric_reference,
            "prompt_sections": _prompt_sections(bundle.prompt_text),
            "rethink_item_ids": rethink_ids,
            "rubric_dimension_ids": [d.get("id") for d in dims if d.get("id")],
            "source_catalog_ids": [e.get("id") for e in catalog_entries if e.get("id")],
            "critique_inputs": list(bundle.critique_edges.get("inputs") or ()),
            "critique_outputs": list(bundle.critique_edges.get("outputs") or ()),
            "allowed_tools": list(bundle.allowed_tools),
            "bound_asset_ids": bound_ids,
            "enforced_asset_ids": enforced_ids,
        },
        "assets": assets,
        "how_to_read": {
            "bound": "Loaded into this run's working set (agent was operating with this knowledge).",
            "enforced": "Runner logic actively checked or scored against this knowledge this run.",
            "available": "Present on disk for the agent but not loaded into this run path.",
            "missing": "Expected knowledge file not present.",
            "note": (
                "Offline runner enforces harness L1/L2 and bind-loads prompt/skill/rubric/spec. "
                "RETHINK items and study excerpts are guidance-bound when embedded in prompt/skill; "
                "they are not live provider activation."
            ),
        },
    }
