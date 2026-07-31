#!/usr/bin/env python3
"""Apply RETHINK_100_IMPROVEMENTS.md to each video pack agent (role-aware).

Source of truth:
  business/video/corpus/study/ui/RETHINK_100_IMPROVEMENTS.md
  (synced from va-agent-swarm/study/ui/RETHINK_100_IMPROVEMENTS.md)

This does NOT activate production models or network. It materializes:
  - sources/RETHINK_100_APPLIED.json  — which items apply + obligations
  - sources/ACQUIRE.md               — optional acquire note for rethink models
  - prompts/*.md                     — RETHINK operating section (idempotent)
  - skills/SKILL.md                  — RETHINK harness section (idempotent)
  - rubrics/*.json                   — optional extra L2 dimensions when missing
  - agent_spec.json                  — improvement.rethink metadata only

Fail-closed: never sets network_access=true or production_activation_requested=true.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "business" / "video" / "agents"
_RETHINK = (
    _ROOT / "business" / "video" / "corpus" / "study" / "ui" / "RETHINK_100_IMPROVEMENTS.md"
)
_REPORT = _ROOT / "business" / "video" / "RETHINK_100_APPLY_REPORT.json"

# ---------------------------------------------------------------------------
# Catalog of RETHINK items (id → short title). Full text lives in the study doc.
# ---------------------------------------------------------------------------
ITEM: dict[int, str] = {
    1: "Seedance 2.0 multi-input / first-last frame",
    2: "Wan 2.6 IP-anchored character consistency",
    3: "Vidu Q2/Q3 temporal consistency",
    4: "Grok Imagine Video I2V",
    5: "Hailuo 2.3 budget-tier generation",
    6: "Kling variant awareness",
    7: "Seedance multi-camera awareness",
    8: "Flux image-gen awareness",
    9: "SD self-hosted cost path awareness",
    10: "Model strengths matrix (router)",
    11: "Multi-model ensemble generation",
    12: "First-and-last-frame control",
    13: "Motion transfer from reference",
    14: "Native audio generation awareness",
    15: "Model deprecation handling",
    16: "Supervisor + Swarm hybrid",
    17: "Node caching",
    18: "Deferred map-reduce nodes",
    19: "Pre/post hooks on nodes",
    20: "Consensus beyond single judge",
    21: "Isolate orchestration from execution",
    22: "Speculative execution with rollback",
    23: "Checkpoint compression",
    24: "Agent pooling / warm-start",
    25: "Priority queues",
    26: "Circuit breaker per external API",
    27: "Event replay / time-travel debug",
    28: "Canary agent configs",
    29: "Shadow mode for new configs",
    30: "Multi-tenant isolation",
    31: "Iterative script verification",
    32: "Hierarchical CoT planning",
    33: "Character bank across shots",
    34: "Shared world model",
    35: "Cinematic language grammar",
    36: "Dedicated boards per stage",
    37: "Hybrid workforce checkpoints (gates)",
    38: "Multi-turn agent conversation",
    39: "Sound director supervision loop",
    40: "Cross-modal temporal state sharing",
    41: "Graph-based memory",
    42: "Act/sequence/beat hierarchy in DAG",
    43: "Shot-adjacency awareness",
    44: "Location scouting focus",
    45: "Character-aware subtitle generation",
    46: "Distinct multi-scene vs 1-shot pipeline",
    47: "Storyboard as control images",
    48: "Reference frame bank",
    49: "Emotion curve verification",
    50: "Retention prediction pre-delivery",
    51: "Generative UI components",
    52: "Infinite canvas workflow",
    53: "Real-time multi-user collaboration",
    54: "AI co-pilot chat",
    55: "Version branches at gates",
    56: "Side-by-side comparison",
    57: "Contextual help",
    58: "Production timeline replay",
    59: "Agent reasoning in plain English",
    60: "Estimated impact preview",
    61: "Template marketplace",
    62: "Progressive loading of partial results",
    63: "Comparison with human baseline",
    64: "Cost prediction intervals",
    65: "Mobile monitoring / gates",
    66: "Webhook/API integrations",
    67: "Batch mode variants",
    68: "White-label mode",
    69: "Offline artifact download",
    70: "Auto WCAG compliance report",
    71: "Multi-language production",
    72: "Brand DNA from past videos",
    73: "Competitor video analysis",
    74: "A/B variant generation",
    75: "Interactive video output",
    76: "Live generation preview",
    77: "Regenerate specific segment only",
    78: "Upscale/enhance pass",
    79: "Music-first workflow",
    80: "Script-first workflow",
    81: "Reference video style extract",
    82: "Seasonal content calendar",
    83: "Performance feedback loop",
    84: "Cross-production character consistency",
    85: "Real-time trend integration",
    86: "VBench 2.0 dimensions",
    87: "Human preference learning (accepts/rejects)",
    88: "Automated regression on config change",
    89: "Cross-model quality normalization",
    90: "Temporal coherence scoring",
    91: "Audio-video sync scoring",
    92: "Audience segment simulation",
    93: "Ethical review automation",
    94: "Provenance chain visualization",
    95: "Quality trend dashboard",
    96: "Usage-based pricing awareness",
    97: "Custom agent creation",
    98: "Agent marketplace",
    99: "Enterprise SSO / audit",
    100: "Self-hosted deployment",
}

# Items every pack agent should internalize (design-time obligations).
UNIVERSAL: tuple[int, ...] = (
    15,  # deprecation awareness
    21,  # host owns orchestration isolation
    26,  # circuit breaker / fail-closed tools
    30,  # multi-tenant isolation (host)
    31,  # iterative verification (self-refine)
    37,  # HiTL gates
    38,  # multi-turn critique conversation
    59,  # plain-English reasoning in artifacts
    63,  # human baseline when available
    87,  # preference when ratings exist
    88,  # golden/regression
    93,  # ethics escalation path
    94,  # provenance refs
)

# Keyword → extra RETHINK items (agent_id or role/category substring match).
ROLE_EXTRAS: list[tuple[tuple[str, ...], tuple[int, ...]]] = [
    (
        ("router",),
        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 89),
    ),
    (
        ("orchestrator", "planner", "producer", "showrunner", "gatekeeper"),
        (6, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 32, 36, 42, 46, 55, 62),
    ),
    (
        ("director", "creativedirector", "musicvideodirector"),
        (1, 2, 7, 11, 12, 16, 33, 35, 43, 47, 48, 80),
    ),
    (
        ("cinematographer", "camera", "drone", "colorist"),
        (2, 6, 12, 13, 35, 43, 47, 48, 90),
    ),
    (
        ("editor", "trailereditor", "continuity"),
        (14, 35, 40, 43, 48, 49, 50, 77, 90, 91),
    ),
    (
        ("screenwriter", "narrative", "comedywriter", "childrensauthor", "journalist"),
        (12, 31, 32, 33, 38, 42, 80),
    ),
    (
        ("storyboard", "conceptartist", "moodboard", "animator", "motiongraphics", "vfx", "styletransfer"),
        (2, 8, 12, 13, 33, 47, 48, 81),
    ),
    (
        ("composer", "sounddesign", "soundmixer", "musicsupervisor", "voiceover", "voiceclone", "lipsync", "audiobook"),
        (5, 14, 39, 79, 91),
    ),
    (
        ("worldbuilding", "productiondesign", "costumedesign", "mua", "casting", "talent", "avatardesign"),
        (2, 33, 34, 44, 48, 84),
    ),
    (
        ("brand", "marketing", "seo", "socialmedia", "performancemarketer", "retention", "roas", "ugc", "channelmanager", "crm", "sales", "comms", "community"),
        (50, 67, 72, 73, 74, 82, 83, 85, 92),
    ),
    (
        ("emotionalarc",),
        (49, 92),
    ),
    (
        ("audiencesim", "learnersim"),
        (50, 92, 87),
    ),
    (
        ("critic", "judge", "evaluationharness", "aiqaconsistency", "standardseditor"),
        (20, 63, 86, 87, 88, 89, 90, 91, 95),
    ),
    (
        ("ethics", "trustsafety", "safetyredteam", "compliance", "legal", "deepfake"),
        (93, 94, 99),
    ),
    (
        ("accessibility", "signlanguage", "localization"),
        (70, 71, 45),
    ),
    (
        ("memory",),
        (33, 34, 41, 48, 84),
    ),
    (
        ("promptengineer", "promptoptimizer", "latencyoptimizer", "costoptimizer", "novelty"),
        (10, 11, 17, 64, 88),
    ),
    (
        ("distributor", "archivemaster", "archiveproducer", "archiveresearch"),
        (69, 78, 94),
    ),
    (
        ("factchecker", "citation", "webresearch", "benchmarkresearch", "sme", "interviewsynthesis"),
        (31, 73, 94),
    ),
    (
        ("festival", "awards", "mpa"),
        (94, 96),
    ),
    (
        ("personalization", "templatedesign", "lms", "instructional"),
        (67, 71, 74, 75),
    ),
    (
        ("foodstylist", "realestate", "travelcine", "sportsanalyst", "medicalillustrator"),
        (2, 48, 81),
    ),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _items_for_agent(agent_id: str, va_category: str, role: str) -> list[int]:
    hay = f"{agent_id} {va_category} {role}".lower()
    chosen: set[int] = set(UNIVERSAL)
    for keys, ids in ROLE_EXTRAS:
        if any(k in hay for k in keys):
            chosen.update(ids)
    # Category-based defaults
    if "1-atl" in hay or "above" in hay:
        chosen.update({16, 32, 33, 42})
    if "2-btl" in hay or "below" in hay:
        chosen.update({43, 47, 48, 90})
    if "3-post" in hay or "post" in hay:
        chosen.update({40, 49, 50, 77, 91})
    if "4-biz" in hay or "business" in hay or "5-dist" in hay:
        chosen.update({67, 74, 83})
    return sorted(chosen)


def _design_models_for_items(item_ids: list[int]) -> list[str]:
    mapping = {
        1: "Seedance 2.0 (design-time only)",
        2: "Wan 2.6 (design-time only)",
        3: "Vidu Q2/Q3 (design-time only)",
        4: "Grok Imagine Video (design-time only)",
        5: "Hailuo 2.3 (design-time only)",
        6: "Kling 2.6/3.0 variants (design-time only)",
        7: "Seedance multi-camera (design-time only)",
        8: "Flux 1.1 Pro Ultra (design-time only)",
        9: "SD 3.5 self-hosted path (design-time only)",
    }
    return [mapping[i] for i in item_ids if i in mapping]


def _obligations(item_ids: list[int], agent_id: str) -> list[str]:
    obs: list[str] = [
        "Host control plane owns orchestration; this agent never opens a second control plane.",
        "Runtime tools remain agent_spec.allowed_tools only; RETHINK model names are design-time.",
        "Fail closed when tools/providers are unavailable (circuit-breaker posture).",
        "Prefer iterative verify → refine ≤ max_refinement_count → HiTL over silent pass.",
        "Emit plain-English reasoning summary in artifacts for operator trust.",
        "Attach provenance / correlation_id / evidence_refs on every handoff.",
    ]
    if any(i in item_ids for i in (33, 48, 84)):
        obs.append(
            "When character/IP consistency matters, require Character Bank + Reference Frame Bank ids in inputs; refuse inventing faces without refs."
        )
    if 43 in item_ids:
        obs.append(
            "Consider previous and next shot adjacency (pacing, eyeline, continuity) before finalizing shot intents or cuts."
        )
    if 12 in item_ids or 1 in item_ids:
        obs.append(
            "When first/last-frame control is in the brief, express start/end keyframes in the artifact; do not invent vendor activation."
        )
    if 31 in item_ids:
        obs.append("Verify intermediate narrative/script artifacts before advancing downstream handoffs.")
    if 10 in item_ids or agent_id.endswith(".router"):
        obs.append(
            "Maintain a design-time model strengths matrix (quality, cost, latency, consistency); host routing remains authoritative."
        )
    if 50 in item_ids or 83 in item_ids:
        obs.append("When metrics exist, surface retention/ROAS hypotheses with confidence — never fabricate live analytics.")
    if 70 in item_ids:
        obs.append("Call out accessibility residual risks; prefer WCAG-oriented checks in L2 notes.")
    if 93 in item_ids:
        obs.append("Escalate stereotype/harm/consent risks to ethics/trust-safety/legal gates.")
    if 91 in item_ids or 14 in item_ids:
        obs.append("Track A/V sync and native-audio implications; do not assume silent video when audio is native.")
    if 77 in item_ids:
        obs.append("Support segment-scoped regenerate intents (keep other segments frozen) when host provides segment ids.")
    if 11 in item_ids:
        obs.append("When ensemble is requested, propose multi-model candidates + selection criterion; host executes tools.")
    return obs


def _upsert_markdown_section(path: Path, marker: str, body: str) -> bool:
    """Insert or replace a section between markers. Returns True if file changed."""
    start = f"<!-- {marker}:start -->"
    end = f"<!-- {marker}:end -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    if start in text and end in text:
        pattern = re.compile(
            re.escape(start) + r".*?" + re.escape(end),
            re.S,
        )
        new_text = pattern.sub(block.rstrip(), text)
    else:
        new_text = text.rstrip() + "\n\n" + block
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def _prompt_section(agent_id: str, item_ids: list[int], models: list[str], obligations: list[str]) -> str:
    lines = [
        "## RETHINK_100 operating guidance (design-time)",
        "",
        f"> Derived from `ui/RETHINK_100_IMPROVEMENTS.md` for `{agent_id}`.",
        "> Does **not** enable production models or network. Host `agent_spec.json` remains authoritative.",
        "",
        "### Applied item ids",
        ", ".join(str(i) for i in item_ids),
        "",
        "### Design-time model landscape (non-activating)",
    ]
    if models:
        for m in models:
            lines.append(f"- {m}")
    else:
        lines.append("- (no additional gen models for this role beyond host allow-list)")
    lines += ["", "### Obligations"]
    for o in obligations:
        lines.append(f"- {o}")
    lines += [
        "",
        "### Collaboration with host architecture",
        "- Commands arrive only via host task envelopes.",
        "- Publish results as structured artifacts; never open browser/UI channels.",
        "- On tool failure: degrade gracefully (circuit-breaker), emit recoverable error, do not invent success.",
    ]
    return "\n".join(lines)


def _skill_section(agent_id: str, item_ids: list[int], obligations: list[str]) -> str:
    lines = [
        "## RETHINK_100 harness notes",
        "",
        f"Source: `business/video/corpus/study/ui/RETHINK_100_IMPROVEMENTS.md` (applied ids: {', '.join(map(str, item_ids[:20]))}"
        + ("…" if len(item_ids) > 20 else "")
        + ").",
        "",
        "### Fail-closed",
        "- Do not treat design-time model names as enabled APIs.",
        "- Runtime: `allowed_tools` + host production flags only.",
        "",
        "### Operator-facing quality",
    ]
    for o in obligations[:8]:
        lines.append(f"- {o}")
    lines += [
        "",
        "### Evidence",
        f"- Machine record: `sources/RETHINK_100_APPLIED.json`",
        f"- Agent: `{agent_id}`",
    ]
    return "\n".join(lines)


def _ensure_rubric_dimensions(rubric_path: Path, item_ids: list[int]) -> bool:
    if not rubric_path.is_file():
        return False
    try:
        data = json.loads(rubric_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    layers = data.setdefault("layers", {})
    l2 = layers.setdefault("L2_rubric", {})
    dims = l2.setdefault("dimensions", [])
    if not isinstance(dims, list):
        return False
    existing = {
        str(d.get("id") or d.get("name") or "").lower()
        for d in dims
        if isinstance(d, dict)
    }
    add: list[dict[str, Any]] = []
    if 90 in item_ids and "temporal_coherence" not in existing:
        add.append(
            {
                "id": "temporal_coherence",
                "name": "Temporal coherence",
                "weight": 1,
                "description": "Multi-shot consistency (motion, identity, lighting continuity).",
                "source": "RETHINK_100#90",
            }
        )
    if 43 in item_ids and "shot_adjacency" not in existing:
        add.append(
            {
                "id": "shot_adjacency",
                "name": "Shot adjacency",
                "weight": 1,
                "description": "Respects previous/next shot context (eyeline, pace, geography).",
                "source": "RETHINK_100#43",
            }
        )
    if 33 in item_ids and "character_consistency" not in existing:
        add.append(
            {
                "id": "character_consistency",
                "name": "Character consistency",
                "weight": 1,
                "description": "Character bank / IP anchors honored when provided.",
                "source": "RETHINK_100#33",
            }
        )
    if 91 in item_ids and "av_sync" not in existing:
        add.append(
            {
                "id": "av_sync",
                "name": "Audio-video sync",
                "weight": 1,
                "description": "Lip-sync / beat-sync residual risks called out.",
                "source": "RETHINK_100#91",
            }
        )
    if 93 in item_ids and "ethics_safety" not in existing:
        add.append(
            {
                "id": "ethics_safety",
                "name": "Ethics & safety",
                "weight": 1,
                "description": "Stereotype/harm/consent flags escalated appropriately.",
                "source": "RETHINK_100#93",
            }
        )
    if 59 in item_ids and "operator_explainability" not in existing:
        add.append(
            {
                "id": "operator_explainability",
                "name": "Operator explainability",
                "weight": 1,
                "description": "Plain-English reasoning present for key decisions.",
                "source": "RETHINK_100#59",
            }
        )
    if not add:
        return False
    dims.extend(add)
    data["rethink_100"] = {
        "applied": True,
        "extra_dimensions": [d["id"] for d in add],
        "doc": "ui/RETHINK_100_IMPROVEMENTS.md",
    }
    rubric_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return True


def _append_acquire_note(agent_dir: Path, models: list[str]) -> None:
    if not models:
        return
    path = agent_dir / "sources" / "ACQUIRE.md"
    marker = "RETHINK_100_MODELS"
    body = (
        f"## {marker}\n\n"
        "Design-time model landscape from RETHINK_100 (do **not** download weights into the pack).\n\n"
        + "\n".join(f"- {m}" for m in models)
        + "\n\n"
        "Runtime remains host allow-list + production gates. See corpus "
        "`study/ui/RETHINK_100_IMPROVEMENTS.md`.\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")
        if marker in text:
            return
        path.write_text(text.rstrip() + "\n\n" + body, encoding="utf-8", newline="\n")
    else:
        path.write_text(
            f"# Acquire notes — {agent_dir.name}\n\n{body}",
            encoding="utf-8",
            newline="\n",
        )


def improve_agent(agent_dir: Path, *, dry_run: bool) -> dict[str, Any]:
    spec_path = agent_dir / "agent_spec.json"
    if not spec_path.is_file():
        return {"agent_id": agent_dir.name, "status": "skip_no_spec"}
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"agent_id": agent_dir.name, "status": "error", "error": str(exc)}

    agent_id = str(spec.get("agent_id") or agent_dir.name)
    role = str(spec.get("role") or "")
    va_category = str(spec.get("va_category") or "")
    item_ids = _items_for_agent(agent_id, va_category, role)
    models = _design_models_for_items(item_ids)
    obligations = _obligations(item_ids, agent_id)

    record = {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "source_doc": "business/video/corpus/study/ui/RETHINK_100_IMPROVEMENTS.md",
        "applied_at": _utc_now(),
        "item_ids": item_ids,
        "item_titles": {str(i): ITEM[i] for i in item_ids if i in ITEM},
        "design_time_models": models,
        "obligations": obligations,
        "runtime_note": (
            "RETHINK model/tool names are non-binding. "
            "allowed_tools + model_policy + production_activation_requested remain authoritative."
        ),
        "production_activation_requested": bool(
            spec.get("production_activation_requested")
        ),
        "network_access": bool(
            (spec.get("model_policy") or {}).get("network_access")
        ),
    }

    result: dict[str, Any] = {
        "agent_id": agent_id,
        "item_count": len(item_ids),
        "item_ids": item_ids,
        "status": "dry_run" if dry_run else "ok",
    }
    if dry_run:
        return result

    sources = agent_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    (sources / "RETHINK_100_APPLIED.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _append_acquire_note(agent_dir, models)

    # Prompt
    pref = str(spec.get("prompt_reference") or "")
    prompt_path = agent_dir / "prompts" / f"{pref}.md" if pref else None
    if prompt_path and prompt_path.is_file():
        result["prompt_updated"] = _upsert_markdown_section(
            prompt_path,
            "RETHINK_100",
            _prompt_section(agent_id, item_ids, models, obligations),
        )

    # Skill
    skill_path = agent_dir / "skills" / "SKILL.md"
    if skill_path.is_file():
        result["skill_updated"] = _upsert_markdown_section(
            skill_path,
            "RETHINK_100",
            _skill_section(agent_id, item_ids, obligations),
        )

    # Rubric
    rref = str(spec.get("rubric_reference") or "")
    rubric_path = agent_dir / "rubrics" / f"{rref}.json" if rref else None
    if rubric_path and rubric_path.is_file():
        result["rubric_updated"] = _ensure_rubric_dimensions(rubric_path, item_ids)

    # agent_spec metadata only
    improvement = dict(spec.get("improvement") or {})
    improvement.update(
        {
            "rethink_100": True,
            "rethink_doc": "ui/RETHINK_100_IMPROVEMENTS.md",
            "rethink_item_count": len(item_ids),
            "rethink_applied_at": record["applied_at"],
            "rethink_record": "sources/RETHINK_100_APPLIED.json",
        }
    )
    spec["improvement"] = improvement
    # never flip fail-closed flags
    if "production_activation_requested" not in spec:
        spec["production_activation_requested"] = False
    spec_path.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    result["status"] = "improved"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", help="Optional agent ids")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-export", action="store_true")
    args = parser.parse_args(argv)

    if not _RETHINK.is_file():
        print(f"Missing RETHINK doc: {_RETHINK}", file=sys.stderr)
        return 2
    if not _AGENTS.is_dir():
        print(f"Missing agents root: {_AGENTS}", file=sys.stderr)
        return 2

    dirs = sorted(
        p
        for p in _AGENTS.iterdir()
        if p.is_dir() and (p / "agent_spec.json").is_file()
    )
    if args.only:
        wanted = set(args.only)
        dirs = [p for p in dirs if p.name in wanted or str(
            json.loads((p / "agent_spec.json").read_text(encoding="utf-8")).get("agent_id")
        ) in wanted]

    results: list[dict[str, Any]] = []
    for agent_dir in dirs:
        results.append(improve_agent(agent_dir, dry_run=args.dry_run))

    improved = sum(1 for r in results if r.get("status") == "improved")
    report = {
        "schema_version": "1.0",
        "generated_at": _utc_now(),
        "source": str(_RETHINK.relative_to(_ROOT)),
        "dry_run": bool(args.dry_run),
        "counts": {
            "agents": len(results),
            "improved": improved,
            "other": len(results) - improved,
        },
        "agents": results,
    }
    if not args.dry_run:
        _REPORT.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps({"report": str(_REPORT.relative_to(_ROOT)), **report["counts"]}, indent=2))
    else:
        print(json.dumps(report["counts"], indent=2))
        # sample
        for r in results[:5]:
            print(f"  {r['agent_id']}: {r['item_count']} items")

    if not args.dry_run and not args.skip_export:
        export = _ROOT / "scripts" / "business" / "export_pack_agents_for_ui.py"
        if export.is_file():
            import subprocess

            subprocess.run([sys.executable, str(export)], check=False, cwd=str(_ROOT))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
