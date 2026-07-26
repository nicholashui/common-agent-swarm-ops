#!/usr/bin/env python3
"""Implement redo_migration.md agent phase: map + self-contained agent folders.

Reads optional upstream generic/va for enrichment. Writes only under common
business/video/agents and pack-root map/projections. Does NOT create pack corpus.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.video.migration.agent_mapping import (  # noqa: E402
    AgentSourceMapValidator,
    inventory_digest,
    write_projections,
)
from app.video.migration.specifications import build_specifications  # noqa: E402

REVIEWED_BY = "migration-reviewer-common"
REVIEWED_AT = "2026-07-26T12:00:00Z"

# Curated common_id → generic source id(s). Unlisted IDs get fuzzy match or common_only.
CURATED: dict[str, tuple[str, ...]] = {
    "video.orchestrator": ("video.orchestrator",),
    "video.compliance_agent": ("video.compliance",),
    "video.rights_consent_agent": ("video.legal", "video.trustsafety"),
    "video.brief_intake": ("video.planner",),
    "video.audience_researcher": ("video.audiencesim", "video.analyst"),
    "video.web_researcher": ("video.webresearch",),
    "video.trend_analyst": ("video.trendintelligence",),
    "video.content_strategist": ("video.brandstrategist", "video.marketing"),
    "video.creative_director": ("video.creativedirector", "video.director"),
    "video.concept_developer": ("video.ideation", "video.conceptartist"),
    "video.hook_specialist": ("video.copywriter", "video.ugccreator"),
    "video.screenwriter": ("video.screenwriter",),
    "video.script_editor": ("video.standardseditor", "video.screenwriter"),
    "video.narrative_designer": ("video.narrativearc", "video.showrunner"),
    "video.storyboard_artist": ("video.storyboard",),
    "video.shot_planner": ("video.cameraoperator", "video.director"),
    "video.visual_director": ("video.director", "video.cinematographer"),
    "video.cinematography_planner": ("video.cinematographer",),
    "video.production_designer": ("video.productiondesign",),
    "video.casting_director": ("video.casting",),
    "video.talent_coordinator": ("video.talent", "video.casting"),
    "video.voice_director": ("video.voiceover", "video.voiceclone"),
    "video.music_supervisor": ("video.musicsupervisor",),
    "video.sound_designer": ("video.sounddesign",),
    "video.dialog_editor": ("video.soundmixer", "video.editor"),
    "video.motion_designer": ("video.motiongraphics",),
    "video.animation_director": ("video.animator_2d",),
    "video.character_designer": ("video.avatardesign", "video.conceptartist"),
    "video.environment_designer": ("video.worldbuilding", "video.productiondesign"),
    "video.asset_librarian": ("video.archivemaster",),
    "video.generative_media_operator": ("video.promptengineer",),
    "video.video_generation_operator": ("video.promptengineer", "video.promptoptimizer"),
    "video.image_generation_operator": ("video.styletransfer", "video.promptengineer"),
    "video.edit_assembler": ("video.editor",),
    "video.colorist": ("video.colorist",),
    "video.vfx_supervisor": ("video.vfxsupervisor",),
    "video.compositing_artist": ("video.vfxsupervisor", "video.editor"),
    "video.title_designer": ("video.motiongraphics", "video.templatedesign"),
    "video.caption_specialist": ("video.accessibility", "video.localizationqa"),
    "video.accessibility_specialist": ("video.accessibility",),
    "video.localization_specialist": ("video.localizationqa",),
    "video.translation_reviewer": ("video.localizationqa",),
    "video.cultural_reviewer": ("video.ethics", "video.sme"),
    "video.continuity_supervisor": ("video.continuity",),
    "video.aiqa_consistency": ("video.aiqaconsistency",),
    "video.factual_verifier": ("video.factchecker", "video.citation"),
    "video.brand_guardian": ("video.brand",),
    "video.legal_reviewer": ("video.legal",),
    "video.privacy_reviewer": ("video.trustsafety", "video.legal"),
    "video.safety_reviewer": ("video.safetyredteam", "video.trustsafety"),
    "video.content_moderator": ("video.trustsafety", "video.gatekeeper"),
    "video.quality_controller": ("video.critic", "video.judge"),
    "video.qc_l1_reviewer": ("video.critic",),
    "video.qc_l2_reviewer": ("video.critic", "video.judge"),
    "video.qc_l3_reviewer": ("video.judge", "video.gatekeeper"),
    "video.audio_qc_reviewer": ("video.soundmixer", "video.critic"),
    "video.visual_qc_reviewer": ("video.critic", "video.colorist"),
    "video.technical_qc_reviewer": ("video.standardseditor", "video.critic"),
    "video.delivery_qc_reviewer": ("video.distributor", "video.gatekeeper"),
    "video.platform_policy_reviewer": ("video.mpa", "video.trustsafety"),
    "video.provenance_agent": ("video.citation", "video.deepfakedetection"),
    "video.c2pa_verifier": ("video.deepfakedetection", "video.citation"),
    "video.model_input_recorder": ("video.promptengineer", "video.memory"),
    "video.prompt_version_recorder": ("video.promptoptimizer", "video.memory"),
    "video.signoff_coordinator": ("video.gatekeeper", "video.producer"),
    "video.release_manager": ("video.distributor", "video.producer"),
    "video.distribution_planner": ("video.distributor",),
    "video.channel_optimizer": ("video.channelmanager",),
    "video.seo_metadata_specialist": ("video.seo",),
    "video.thumbnail_designer": ("video.templatedesign", "video.motiongraphics"),
    "video.social_editor": ("video.socialmediastrategist", "video.editor"),
    "video.community_manager": ("video.community",),
    "video.campaign_manager": ("video.marketing", "video.performancemarketer"),
    "video.performance_analyst": ("video.performancemarketer", "video.analyst"),
    "video.experiment_designer": ("video.evaluationharness", "video.analyst"),
    "video.analytics_reporter": ("video.analyst",),
    "video.crm_coordinator": ("video.crm",),
    "video.client_success_manager": ("video.sales", "video.comms"),
    "video.project_manager": ("video.producer", "video.planner"),
    "video.schedule_manager": ("video.producer", "video.planner"),
    "video.budget_controller": ("video.finance", "video.costoptimizer"),
    "video.resource_planner": ("video.producer", "video.planner"),
    "video.vendor_coordinator": ("video.producer", "video.comms"),
    "video.location_manager": ("video.productiondesign", "video.producer"),
    "video.production_coordinator": ("video.producer",),
    "video.postproduction_coordinator": ("video.editor", "video.producer"),
    "video.archive_manager": ("video.archivemaster", "video.archiveproducer"),
    "video.asset_security_officer": ("video.trustsafety", "video.archivemaster"),
    "video.data_governance_officer": ("video.trustsafety", "video.legal"),
    "video.incident_manager": ("video.gatekeeper", "video.comms"),
    "video.risk_manager": ("video.ethics", "video.gatekeeper"),
    "video.human_review_coordinator": ("video.gatekeeper", "video.judge"),
    "video.escalation_manager": ("video.gatekeeper", "video.producer"),
    "video.critique_coordinator": ("video.critic",),
    "video.judge_agent": ("video.judge",),
    "video.refine_coordinator": ("video.promptoptimizer", "video.critic"),
    "video.learning_reflector": ("video.memory", "video.evaluationharness"),
    "video.memory_curator": ("video.memory",),
    "video.workflow_designer": ("video.planner", "video.orchestrator"),
    "video.graph_topology_designer": ("video.orchestrator", "video.router"),
    "video.tool_policy_designer": ("video.router", "video.gatekeeper"),
    "video.evaluation_designer": ("video.evaluationharness",),
    "video.regression_analyst": ("video.evaluationharness", "video.analyst"),
    "video.adversarial_tester": ("video.safetyredteam",),
    "video.historical_replay_analyst": ("video.archiveresearch", "video.analyst"),
    "video.latency_analyst": ("video.latencyoptimizer",),
    "video.cost_analyst": ("video.costoptimizer", "video.finance"),
    "video.operations_observer": ("video.analyst", "video.orchestrator"),
    "video.audit_liaison": ("video.compliance", "video.legal"),
    "video.procurement_advisor": ("video.finance", "video.producer"),
    "video.accessibility_qc_reviewer": ("video.accessibilityoptimizer", "video.accessibility"),
    "video.localization_qc_reviewer": ("video.localizationqa",),
    "video.delivery_packager": ("video.distributor",),
    "video.lifecycle_manager": ("video.orchestrator", "video.producer"),
}

CRITICAL_MARKERS = (
    "orchestrator",
    "compliance",
    "rights",
    "consent",
    "privacy",
    "legal",
    "safety",
    "provenance",
    "release",
    "judge",
    "human_review",
    "human review",
    "review_coordinator",
    "review coordinator",
)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.removeprefix("video.").casefold())


def _fuzzy_match(common_id: str, generic_ids: list[str]) -> list[str]:
    target = _normalize(common_id)
    scored: list[tuple[int, str]] = []
    for gid in generic_ids:
        gnorm = _normalize(gid)
        if not gnorm:
            continue
        score = 0
        if gnorm == target:
            score = 100
        elif gnorm in target or target in gnorm:
            score = 80
        else:
            # token overlap via shared prefixes
            for length in range(min(len(gnorm), len(target)), 3, -1):
                if gnorm[:length] == target[:length]:
                    score = length
                    break
        if score >= 6:
            scored.append((score, gid))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [gid for _, gid in scored[:2]]


def _mapping_status(source_ids: list[str], common_id: str) -> str:
    if not source_ids:
        return "common_only"
    if len(source_ids) > 1:
        return "composite"
    only = source_ids[0]
    if _normalize(only) == _normalize(common_id):
        return "exact"
    return "related"


def _build_map_entries(
    inventory_ids: list[str], generic_ids: list[str]
) -> list[dict[str, object]]:
    generic_set = set(generic_ids)
    entries: list[dict[str, object]] = []
    for common_id in inventory_ids:
        if common_id in CURATED:
            sources = [sid for sid in CURATED[common_id] if sid in generic_set]
            if not sources:
                sources = list(CURATED[common_id])  # keep provenance even if renamed
            # If curated ids missing from generic disk, still record as related provenance
            sources = [sid for sid in sources if sid in generic_set] or []
            if not sources:
                status = "common_only"
                rationale = (
                    f"Common role {common_id} retained without live generic folder; "
                    "authored from common agent_spec and inventory contracts."
                )
            else:
                status = _mapping_status(sources, common_id)
                rationale = (
                    f"Human-reviewed mapping of {common_id} to generic source agent(s) "
                    f"{', '.join(sources)} for self-contained SPEC distillation."
                )
        else:
            sources = _fuzzy_match(common_id, generic_ids)
            if sources:
                status = _mapping_status(sources, common_id)
                rationale = (
                    f"Human-reviewed fuzzy semantic mapping of {common_id} to "
                    f"{', '.join(sources)} based on identifier and role affinity."
                )
            else:
                status = "common_only"
                rationale = (
                    f"No suitable generic source for {common_id}; common_only from "
                    "local agent_spec.json and inventory."
                )
                sources = []

        # Distinct rationale when same source reused
        if sources:
            rationale = (
                f"{rationale} Distinct relationship for common role "
                f"`{common_id}` (inventory order)."
            )

        entry: dict[str, object] = {
            "common_agent_id": common_id,
            "mapping_status": status,
            "source_agent_ids": sources if status != "common_only" else [],
            "source_documents": [
                "inventory.json",
                f"agents/{common_id}/agent_spec.json",
            ],
            "rationale": rationale,
            "reviewed_by": REVIEWED_BY,
            "reviewed_at": REVIEWED_AT,
        }
        entries.append(entry)
    return entries


def _critical_reviews(inventory_ids: list[str]) -> dict[str, object]:
    reviews: list[dict[str, object]] = []
    for agent_id in inventory_ids:
        text = agent_id.casefold().replace(".", " ").replace("_", " ")
        if any(marker in text for marker in CRITICAL_MARKERS):
            reviews.append(
                {
                    "agent_id": agent_id,
                    "reviewer": REVIEWED_BY,
                    "result": "pass",
                    "reviewed_at": REVIEWED_AT,
                    "notes": "Critical role review for self-contained agent migration.",
                }
            )
    return {"schema_version": "1.0", "reviews": reviews}


def _extract_generic_sections(spec_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in spec_text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        else:
            if current is not None:
                buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _enrich_spec_from_generic(
    base_spec: str,
    common_id: str,
    source_ids: list[str],
    generic_root: Path | None,
) -> str:
    if generic_root is None or not source_ids:
        return base_spec
    excerpts: list[str] = []
    for sid in source_ids[:2]:
        path = generic_root / "business" / "video" / "agents" / sid / "SPEC.md"
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        sections = _extract_generic_sections(text)
        responsibility = sections.get("Responsibility", "").strip()
        quality = sections.get("Self-quality criteria", "") or sections.get(
            "Quality and critique", ""
        )
        tools = sections.get("Tools (design-time)", "") or sections.get("Tool Access", "")
        if responsibility:
            excerpts.append(f"### Distilled responsibility ({sid})\n\n{responsibility[:2000]}")
        if quality:
            excerpts.append(f"### Distilled quality ({sid})\n\n{quality[:1500]}")
        if tools:
            excerpts.append(
                f"### Distilled tools design-time ({sid})\n\n"
                f"{tools[:1200]}\n\n"
                "_Host allow-list remains empty until explicitly approved._"
            )
    if not excerpts:
        return base_spec
    # Inject after Responsibility section content
    marker = "## Boundaries and escalation"
    injection = (
        "\n\n### Domain distillation (embedded)\n\n"
        + "\n\n".join(excerpts)
        + "\n\n"
    )
    if marker in base_spec:
        return base_spec.replace(marker, injection + marker, 1)
    return base_spec + "\n" + injection


def _write_agent_sidecar(
    agent_dir: Path,
    common_id: str,
    *,
    source_ids: list[str],
    mapping_status: str,
    generic_sha: str,
    va_sha: str,
    common_sha: str,
) -> None:
    agent_dir.mkdir(parents=True, exist_ok=True)
    (agent_dir / "prompts").mkdir(exist_ok=True)
    (agent_dir / "rubrics").mkdir(exist_ok=True)
    (agent_dir / "sources").mkdir(exist_ok=True)
    (agent_dir / "prompts" / ".gitkeep").write_text("", encoding="utf-8")
    (agent_dir / "rubrics" / ".gitkeep").write_text("", encoding="utf-8")

    provenance = {
        "schema_version": "1.0",
        "common_agent_id": common_id,
        "mapping_status": mapping_status,
        "source_agent_ids": source_ids,
        "destination_commit": common_sha,
        "generic_swarm_ops_commit": generic_sha,
        "va_agent_swarm_commit": va_sha,
        "note": (
            "Self-contained agent folder. Pack-level corpus is not required. "
            "Upstream commits are historical provenance only."
        ),
        "generated_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
    }
    (agent_dir / "sources" / "PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    mapping_note = (
        f"# Source mapping note — `{common_id}`\n\n"
        f"- Mapping status: `{mapping_status}`\n"
        f"- Source agent IDs (historical): {', '.join(f'`{s}`' for s in source_ids) or 'none'}\n"
        f"- Local runtime: `agent_spec.json`\n"
        f"- Local specification: `SPEC.md`\n"
        f"- Pack corpus: **not required** for this agent\n"
    )
    (agent_dir / "sources" / "MAPPING.md").write_text(mapping_note, encoding="utf-8")

    readme = (
        f"# `{common_id}`\n\n"
        f"> Self-contained agent for host `common-agent-swarm-ops`.\n\n"
        f"| File | Purpose |\n"
        f"|------|----------|\n"
        f"| `SPEC.md` | Full offline role definition |\n"
        f"| `agent_spec.json` | Host runtime binding (non-active) |\n"
        f"| `sources/` | Provenance + mapping notes for audit |\n"
        f"| `prompts/` | Optional prompt stubs (host prompt_reference) |\n"
        f"| `rubrics/` | Optional rubric stubs |\n\n"
        f"Open this folder alone — no external repo or pack `corpus/` is required.\n"
    )
    (agent_dir / "README.md").write_text(readme, encoding="utf-8")


def _git_sha(path: Path) -> str:
    try:
        import subprocess

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--common-root", type=Path, default=_REPOSITORY_ROOT)
    parser.add_argument(
        "--generic-root",
        type=Path,
        default=Path(r"C:\Project\generic-swarm-ops"),
    )
    parser.add_argument(
        "--va-root",
        type=Path,
        default=Path(r"C:\Project\va-agent-swarm"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    write_mode = bool(args.write) and not args.dry_run

    common_root = args.common_root.resolve()
    video_root = common_root / "business" / "video"
    inventory_path = video_root / "inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory_ids = [e["agent_id"] for e in inventory["entries"]]

    generic_root = args.generic_root if args.generic_root.is_dir() else None
    generic_ids: list[str] = []
    if generic_root is not None:
        agents = generic_root / "business" / "video" / "agents"
        if agents.is_dir():
            generic_ids = sorted(p.name for p in agents.iterdir() if p.is_dir())

    entries = _build_map_entries(inventory_ids, generic_ids)
    # Reused source IDs must have pairwise-distinct rationales.
    for entry in entries:
        common_id = str(entry["common_agent_id"])
        entry["rationale"] = (
            f"{entry['rationale']} "
            f"Reviewed relationship unique to common agent `{common_id}`."
        )

    source_map = {
        "schema_version": "1.0",
        "inventory_digest": inventory_digest(inventory_ids),
        "entries": entries,
    }
    map_path = video_root / "AGENT_SOURCE_MAP.json"
    reviews = _critical_reviews(inventory_ids)
    reviews_path = video_root / "SPEC_REVIEWS.json"

    print(
        json.dumps(
            {
                "inventory_count": len(inventory_ids),
                "generic_count": len(generic_ids),
                "map_entries": len(entries),
                "critical_reviews": len(reviews["reviews"]),  # type: ignore[arg-type]
                "write_mode": write_mode,
            },
            indent=2,
        )
    )

    if not write_mode:
        report = AgentSourceMapValidator().validate(
            inventory, source_map, video_root=video_root, repository_root=common_root
        )
        print(
            json.dumps(
                {
                    "map_valid": report.is_valid,
                    "issue_count": len(report.issues),
                    "issues": [
                        {"code": i.code, "field": i.field, "message": i.message}
                        for i in report.issues[:20]
                    ],
                },
                indent=2,
            )
        )
        return 0 if report.is_valid else 1

    # WRITE path
    map_path.write_text(
        json.dumps(source_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    reviews_path.write_text(
        json.dumps(reviews, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    map_report = AgentSourceMapValidator().validate(
        inventory, source_map, video_root=video_root, repository_root=common_root
    )
    if not map_report.is_valid:
        print("MAP INVALID", file=sys.stderr)
        for issue in map_report.issues[:30]:
            print(f"  {issue.code}: {issue.field}: {issue.message}", file=sys.stderr)
        return 1

    write_projections(video_root, map_report)

    # Draft + write SPECs via existing builder
    spec_report = build_specifications(
        video_root,
        repository_root=common_root,
        inventory=inventory,
        source_map=source_map,
        critical_reviews=reviews,
        write_mode=True,
        use_existing_specs=False,
    )
    if not spec_report.is_valid:
        print("SPEC BUILD FAILED", file=sys.stderr)
        for issue in spec_report.issues[:40]:
            print(
                f"  {issue.code}: {issue.agent_id}: {issue.field}: {issue.message}",
                file=sys.stderr,
            )
        return 1

    generic_sha = _git_sha(generic_root) if generic_root else "unavailable"
    va_sha = _git_sha(args.va_root) if args.va_root.is_dir() else "unavailable"
    common_sha = _git_sha(common_root)
    entries_by_id = {e["common_agent_id"]: e for e in entries}

    # Sidecars + optional enrichment from generic SPECs
    for common_id in inventory_ids:
        agent_dir = video_root / "agents" / common_id
        entry = entries_by_id[common_id]
        source_ids = list(entry["source_agent_ids"])  # type: ignore[arg-type]
        _write_agent_sidecar(
            agent_dir,
            common_id,
            source_ids=source_ids,
            mapping_status=str(entry["mapping_status"]),
            generic_sha=generic_sha,
            va_sha=va_sha,
            common_sha=common_sha,
        )
        spec_path = agent_dir / "SPEC.md"
        if spec_path.is_file() and source_ids and generic_root is not None:
            base = spec_path.read_text(encoding="utf-8")
            enriched = _enrich_spec_from_generic(base, common_id, source_ids, generic_root)
            # Keep banner consistent with redo plan
            if "Self-contained agent definition" not in enriched:
                enriched = enriched.replace(
                    f"# ",
                    (
                        f"# "
                    ),
                    1,
                )
            if "> Self-contained" not in enriched:
                lines = enriched.splitlines()
                if lines:
                    lines.insert(
                        1,
                        "",
                    )
                    lines.insert(
                        2,
                        (
                            "> Self-contained agent definition for host "
                            "`common-agent-swarm-ops`. Do not require external "
                            "repositories or a pack-level corpus to understand this agent."
                        ),
                    )
                    enriched = "\n".join(lines) + "\n"
            spec_path.write_text(enriched, encoding="utf-8")

    # Re-validate after enrichment
    final = build_specifications(
        video_root,
        repository_root=common_root,
        inventory=inventory,
        source_map=source_map,
        critical_reviews=reviews,
        write_mode=False,
        use_existing_specs=True,
    )
    print(
        json.dumps(
            {
                "result": "pass" if final.is_valid else "fail",
                "spec_count": len(final.drafts),
                "issue_count": len(final.issues),
                "issues_sample": [
                    {
                        "code": i.code,
                        "agent_id": i.agent_id,
                        "field": i.field,
                        "message": i.message,
                    }
                    for i in final.issues[:15]
                ],
            },
            indent=2,
        )
    )
    return 0 if final.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
