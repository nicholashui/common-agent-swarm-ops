#!/usr/bin/env python3
"""Export agent workflow templates for Registry Agent Workflow UI.

Sources:
  - business/*/design/workflows/wf_*_arch_*.dna.json (DNA handoff graphs)
  - business/video/design/production_scale_framework.md (S1–S7 scale crews)
  - agent_spec.json for display names / categories

Writes frontend/src/lib/projections/agent-workflow.generated.ts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_OUT = _ROOT / "frontend" / "src" / "lib" / "projections" / "agent-workflow.generated.ts"
_EXCLUDED_PACKS = frozenset({"specials", "evals", "schemas", "seeds"})
_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")

# Scale crews from production_scale_framework.md (active bands; not full 114).
_SCALE_TEMPLATES: list[dict] = [
    {
        "id": "scale.s1.micro",
        "scaleId": "S1",
        "label": "S1 — Micro Production",
        "background": (
            "Foundation tier for in-feed ads, promos, vlogs, and short tutorials. "
            "Prioritizes rapid turnaround and cost compression with a minimal crew."
        ),
        "whenToUse": "Social spikes, single-SKU promos under a day, UAT of thin DNA graphs (A/B/H).",
        "whoShouldUse": "Social/performance marketers, solo creators, host operators.",
        "howToUse": (
            "Set scale_profile=S1; pick archetype A/B/H; single social delivery branch; "
            "L1 hard, light L2; skip theatrical/broadcast."
        ),
        "source": "business/video/design/production_scale_framework.md#s1",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.router",
            "video.memory",
            "video.judge",
            "video.gatekeeper",
            "video.trendintelligence",
            "video.copywriter",
            "video.screenwriter",
            "video.director",
            "video.promptengineer",
            "video.aiqaconsistency",
            "video.editor",
            "video.accessibility",
            "video.socialmediastrategist",
            "video.compliance",
            "video.analyst",
        ],
        "phaseFlow": [
            ("greenlight", ["video.planner", "video.producer"]),
            ("concept", ["video.trendintelligence", "video.copywriter", "video.screenwriter"]),
            ("production", ["video.director", "video.promptengineer", "video.aiqaconsistency"]),
            ("post", ["video.editor", "video.accessibility"]),
            ("distribution", ["video.socialmediastrategist", "video.compliance"]),
            ("learning", ["video.analyst"]),
        ],
        "archetypes": ["A", "B", "H", "D"],
    },
    {
        "id": "scale.s2.small",
        "scaleId": "S2",
        "label": "S2 — Small Production",
        "background": (
            "Multi-scene coherence with light cinematography/VFX and richer audio. "
            "Multiple social + mezzanine outputs."
        ),
        "whenToUse": "Branded short films, animated explainers, interview packages, multi-scene AI shorts.",
        "whoShouldUse": "Creative leads, brand managers, producers.",
        "howToUse": (
            "scale_profile=S2; archetypes C/E/G light; ≥2 delivery branches; "
            "AIQAConsistency on multi-shot identity."
        ),
        "source": "business/video/design/production_scale_framework.md#s2",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.director",
            "video.screenwriter",
            "video.storyboard",
            "video.conceptartist",
            "video.cinematographer",
            "video.promptengineer",
            "video.aiqaconsistency",
            "video.editor",
            "video.colorist",
            "video.composer",
            "video.sounddesign",
            "video.voiceover",
            "video.brand",
            "video.vfxsupervisor",
            "video.compliance",
            "video.audiencesim",
            "video.analyst",
        ],
        "phaseFlow": [
            ("greenlight", ["video.planner", "video.producer"]),
            ("pre_production", ["video.screenwriter", "video.storyboard", "video.conceptartist"]),
            ("production", ["video.director", "video.cinematographer", "video.promptengineer", "video.aiqaconsistency"]),
            ("post", ["video.editor", "video.colorist", "video.composer", "video.sounddesign"]),
            ("review", ["video.brand", "video.compliance"]),
            ("learning", ["video.analyst", "video.audiencesim"]),
        ],
        "archetypes": ["C", "D", "E", "G"],
    },
    {
        "id": "scale.s3.medium",
        "scaleId": "S3",
        "label": "S3 — Medium Production",
        "background": (
            "Professional broadcast-like cadence: recurring shows, training series, "
            "and mid-form packages with stronger compliance and memory."
        ),
        "whenToUse": "Recurring show packaging, corporate training series, documentary segments.",
        "whoShouldUse": "Showrunners, compliance, channel managers, instructional designers.",
        "howToUse": (
            "scale_profile=S3; require Compliance+Legal before distribution; "
            "Memory project bible for series continuity; multi-platform schedule."
        ),
        "source": "business/video/design/production_scale_framework.md#s3",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.showrunner",
            "video.memory",
            "video.screenwriter",
            "video.sme",
            "video.instructionaldesign",
            "video.director",
            "video.promptengineer",
            "video.aiqaconsistency",
            "video.editor",
            "video.accessibility",
            "video.compliance",
            "video.legal",
            "video.channelmanager",
            "video.lms",
            "video.factchecker",
            "video.standardseditor",
            "video.analyst",
        ],
        "phaseFlow": [
            ("greenlight", ["video.planner", "video.producer", "video.compliance"]),
            ("concept", ["video.showrunner", "video.screenwriter", "video.sme", "video.instructionaldesign"]),
            ("production", ["video.director", "video.promptengineer", "video.aiqaconsistency"]),
            ("post", ["video.editor", "video.accessibility"]),
            ("review", ["video.legal", "video.standardseditor", "video.factchecker"]),
            ("distribution", ["video.channelmanager", "video.lms"]),
            ("learning", ["video.analyst"]),
        ],
        "archetypes": ["F", "I", "C"],
    },
    {
        "id": "scale.s4.medium_large",
        "scaleId": "S4",
        "label": "S4 — Medium-Large Production",
        "background": (
            "Premium TV / high-end digital: music videos, multi-outlet packaging, "
            "rights-heavy clearance, parallel picture/sound/marketing."
        ),
        "whenToUse": "Music videos, premium brand film, label/digital releases.",
        "whoShouldUse": "Label A&R, MV directors, rights counsel, marketing leads.",
        "howToUse": (
            "scale_profile=S4; parallel picture∥sound∥marketing; legal/music clearance "
            "before master; trailer cutdowns before picture lock when possible."
        ),
        "source": "business/video/design/production_scale_framework.md#s4",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.musicvideodirector",
            "video.choreography",
            "video.casting",
            "video.cinematographer",
            "video.promptengineer",
            "video.continuity",
            "video.vfxsupervisor",
            "video.aiqaconsistency",
            "video.editor",
            "video.colorist",
            "video.composer",
            "video.soundmixer",
            "video.musicsupervisor",
            "video.legal",
            "video.compliance",
            "video.deepfakedetection",
            "video.trailereditor",
            "video.socialmediastrategist",
            "video.labeldigital",
            "video.distributor",
            "video.analyst",
        ],
        "phaseFlow": [
            ("greenlight", ["video.producer", "video.planner", "video.legal"]),
            ("concept", ["video.musicvideodirector", "video.choreography", "video.casting"]),
            (
                "production",
                [
                    "video.cinematographer",
                    "video.promptengineer",
                    "video.continuity",
                    "video.vfxsupervisor",
                    "video.aiqaconsistency",
                ],
            ),
            ("post", ["video.editor", "video.colorist", "video.composer", "video.soundmixer"]),
            ("review", ["video.musicsupervisor", "video.compliance", "video.deepfakedetection"]),
            ("distribution", ["video.trailereditor", "video.socialmediastrategist", "video.labeldigital"]),
            ("learning", ["video.analyst"]),
        ],
        "archetypes": ["G", "E"],
    },
    {
        "id": "scale.s5.large",
        "scaleId": "S5",
        "label": "S5 — Large Production",
        "background": (
            "Multi-unit simultaneous operations: variety, sports, concert, awards-style shows "
            "with heavy analytics and merge gates."
        ),
        "whenToUse": "Multi-camera live-to-tape, sports/concert highlight factories, multi-segment campaigns.",
        "whoShouldUse": "Network EPs, sports producers, live showrunners, campaign strategists.",
        "howToUse": (
            "scale_profile=S5; concurrent unit DAGs under one production; "
            "AudienceSim per segment; formal HiTL on safety/rights."
        ),
        "source": "business/video/design/production_scale_framework.md#s5",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.showrunner",
            "video.director",
            "video.cameraoperator",
            "video.sportsanalyst",
            "video.editor",
            "video.audiencesim",
            "video.emotionalarc",
            "video.standardseditor",
            "video.legal",
            "video.trustsafety",
            "video.ethics",
            "video.channelmanager",
            "video.socialmediastrategist",
            "video.comms",
            "video.awardsstrategist",
            "video.analyst",
            "video.gatekeeper",
            "video.judge",
        ],
        "phaseFlow": [
            ("greenlight", ["video.planner", "video.producer", "video.gatekeeper"]),
            ("production_units", ["video.showrunner", "video.director", "video.cameraoperator", "video.sportsanalyst"]),
            ("merge", ["video.orchestrator", "video.editor", "video.audiencesim"]),
            ("review", ["video.standardseditor", "video.legal", "video.trustsafety", "video.ethics"]),
            ("distribution", ["video.channelmanager", "video.socialmediastrategist", "video.comms"]),
            ("learning", ["video.analyst", "video.awardsstrategist"]),
        ],
        "archetypes": ["E", "I", "G"],
    },
    {
        "id": "scale.s6.very_large",
        "scaleId": "S6",
        "label": "S6 — Very Large / Documentary",
        "background": (
            "Research- and archive-heavy long form: docuseries, historical, limited series "
            "with continuous fact mesh and corrections."
        ),
        "whenToUse": "Documentary explained episodes/series, scientific or historical limited series.",
        "whoShouldUse": "Showrunners, journalist/research leads, archive producers, standards & ethics.",
        "howToUse": (
            "scale_profile=S6; research before full greenlight; Legal+Ethics dual clearance; "
            "ArchiveMaster mandatory; corrections pipeline post-launch."
        ),
        "source": "business/video/design/production_scale_framework.md#s6",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.showrunner",
            "video.journalist",
            "video.screenwriter",
            "video.webresearch",
            "video.archiveresearch",
            "video.archiveproducer",
            "video.factchecker",
            "video.citation",
            "video.director",
            "video.editor",
            "video.voiceover",
            "video.colorist",
            "video.soundmixer",
            "video.legal",
            "video.ethics",
            "video.standardseditor",
            "video.channelmanager",
            "video.seo",
            "video.archivemaster",
            "video.corrections",
            "video.analyst",
        ],
        "phaseFlow": [
            ("research", ["video.webresearch", "video.archiveresearch", "video.journalist"]),
            ("greenlight", ["video.producer", "video.legal", "video.ethics", "video.planner"]),
            ("production", ["video.director", "video.archiveproducer", "video.factchecker"]),
            ("post", ["video.editor", "video.voiceover", "video.colorist", "video.soundmixer"]),
            ("review", ["video.factchecker", "video.legal", "video.standardseditor", "video.ethics"]),
            ("distribution", ["video.channelmanager", "video.seo", "video.archivemaster"]),
            ("learning", ["video.corrections", "video.analyst"]),
        ],
        "archetypes": ["I", "E"],
    },
    {
        "id": "scale.s7.premium",
        "scaleId": "S7",
        "label": "S7 — Premium / Cinematic",
        "background": (
            "Feature-length and cinematic productions with formal release governance, "
            "full L1/L2/L3 mesh, multi-territory packaging, and phased full-pool scheduling."
        ),
        "whenToUse": "Feature AI-assisted film, high-risk IP/consent, multi-territory theatrical+stream.",
        "whoShouldUse": "Studio EP, director, legal leadership, sales/distribution — mandatory HiTL.",
        "howToUse": (
            "scale_profile=S7; hard GateKeeper+human gates; character/reference banks required; "
            "full distribution matrix; tools only via host production activation."
        ),
        "source": "business/video/design/production_scale_framework.md#s7",
        "agentIds": [
            "video.orchestrator",
            "video.planner",
            "video.producer",
            "video.screenwriter",
            "video.director",
            "video.conceptartist",
            "video.casting",
            "video.storyboard",
            "video.productiondesign",
            "video.continuity",
            "video.promptengineer",
            "video.cinematographer",
            "video.aiqaconsistency",
            "video.vfxsupervisor",
            "video.voiceclone",
            "video.lipsync",
            "video.composer",
            "video.editor",
            "video.colorist",
            "video.soundmixer",
            "video.judge",
            "video.gatekeeper",
            "video.audiencesim",
            "video.mpa",
            "video.ethics",
            "video.compliance",
            "video.legal",
            "video.sales",
            "video.distributor",
            "video.trailereditor",
            "video.marketing",
            "video.archivemaster",
            "video.festivalstrategist",
            "video.awardsstrategist",
            "video.analyst",
            "video.evaluationharness",
            "video.memory",
            "video.router",
        ],
        "phaseFlow": [
            ("development", ["video.screenwriter", "video.producer", "video.director", "video.conceptartist", "video.legal"]),
            ("pre_production", ["video.storyboard", "video.productiondesign", "video.casting", "video.continuity"]),
            (
                "production",
                [
                    "video.promptengineer",
                    "video.cinematographer",
                    "video.aiqaconsistency",
                    "video.vfxsupervisor",
                    "video.voiceclone",
                    "video.composer",
                ],
            ),
            ("post", ["video.editor", "video.colorist", "video.soundmixer"]),
            ("review", ["video.judge", "video.gatekeeper", "video.audiencesim", "video.mpa", "video.ethics", "video.compliance"]),
            ("distribution", ["video.sales", "video.distributor", "video.trailereditor", "video.marketing", "video.archivemaster"]),
            ("learning", ["video.analyst", "video.evaluationharness", "video.awardsstrategist"]),
        ],
        "archetypes": ["J"],
    },
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_name(agent_id: str, role: str = "", va_name: str | None = None) -> str:
    if va_name and str(va_name).strip():
        return str(va_name).replace("Agent", "").strip() or str(va_name)
    if role:
        base = role.split("(")[0].strip()
        base = re.sub(r"Agent\b", "", base).strip(" /")
        if base:
            return base
    leaf = agent_id.split(".")[-1]
    return leaf.replace("_", " ").title()


def _load_agent_index(pack_dir: Path) -> dict[str, dict]:
    agents_root = pack_dir / "agents"
    index: dict[str, dict] = {}
    if not agents_root.is_dir():
        return index
    for agent_dir in sorted(agents_root.iterdir()):
        if not agent_dir.is_dir():
            continue
        spec_path = agent_dir / "agent_spec.json"
        if not spec_path.is_file():
            continue
        try:
            spec = _read_json(spec_path)
        except (OSError, json.JSONDecodeError):
            continue
        agent_id = str(spec.get("agent_id") or agent_dir.name)
        if not _SAFE_ID.match(agent_id):
            continue
        index[agent_id] = {
            "id": agent_id,
            "name": _display_name(
                agent_id,
                str(spec.get("role") or ""),
                str(spec.get("va_name") or "") or None,
            ),
            "role": str(spec.get("role") or ""),
            "categoryId": str(spec.get("va_category") or "unknown"),
            "status": str(spec.get("status") or "registered"),
            "href": f"/registry/agents/{agent_id}",
        }
    return index


def _edges_from_phase_flow(phase_flow: list[tuple[str, list[str]]]) -> list[dict]:
    """Sequential handoffs: last agents of phase N → first agents of phase N+1, plus within-phase chain."""
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def add(frm: str, to: str, kind: str, label: str) -> None:
        key = (frm, to, kind)
        if key in seen or frm == to:
            return
        seen.add(key)
        edges.append({"fromId": frm, "toId": to, "kind": kind, "label": label})

    for phase_name, agents in phase_flow:
        for i in range(len(agents) - 1):
            add(agents[i], agents[i + 1], "handoff", phase_name)
    for i in range(len(phase_flow) - 1):
        prev_agents = phase_flow[i][1]
        next_agents = phase_flow[i + 1][1]
        if not prev_agents or not next_agents:
            continue
        # Connect phase tail → next phase head (and light fan-in/out)
        add(prev_agents[-1], next_agents[0], "phase", f"{phase_flow[i][0]}→{phase_flow[i+1][0]}")
        if len(prev_agents) > 1:
            add(prev_agents[0], next_agents[0], "phase", f"{phase_flow[i][0]}→{phase_flow[i+1][0]}")
    return edges


def _template_from_scale(pack_id: str, scale: dict, agent_index: dict[str, dict]) -> dict:
    agent_ids = [a for a in scale["agentIds"] if a in agent_index]
    # keep declared order even if some missing
    agents = [agent_index[a] for a in agent_ids]
    phase_flow = [
        (name, [a for a in ids if a in agent_index]) for name, ids in scale["phaseFlow"]
    ]
    edges = _edges_from_phase_flow(phase_flow)
    steps: list[dict] = []
    for phase_name, ids in phase_flow:
        for aid in ids:
            steps.append(
                {
                    "id": f"{scale['id']}.{phase_name}.{aid}",
                    "label": agent_index[aid]["name"],
                    "agentId": aid,
                    "phase": phase_name,
                    "humanGate": phase_name in {"greenlight", "review"},
                    "next": [],
                }
            )
    return {
        "id": f"{pack_id}.{scale['id']}",
        "packId": pack_id,
        "kind": "scale",
        "scaleId": scale["scaleId"],
        "label": scale["label"],
        "background": scale["background"],
        "whenToUse": scale["whenToUse"],
        "whoShouldUse": scale["whoShouldUse"],
        "howToUse": scale["howToUse"],
        "source": scale["source"],
        "archetypes": scale["archetypes"],
        "dnaWorkflowId": None,
        "agentIds": agent_ids,
        "agents": agents,
        "steps": steps,
        "callEdges": edges,
        "phaseOrder": [p[0] for p in phase_flow],
    }


def _template_from_dna(
    pack_id: str, dna_path: Path, agent_index: dict[str, dict]
) -> dict | None:
    try:
        dna = _read_json(dna_path)
    except (OSError, json.JSONDecodeError):
        return None
    steps_raw = dna.get("steps")
    if not isinstance(steps_raw, list) or not steps_raw:
        return None

    step_by_id: dict[str, dict] = {}
    agents_ordered: list[str] = []
    steps: list[dict] = []
    for raw in steps_raw:
        if not isinstance(raw, dict):
            continue
        sid = str(raw.get("id") or "")
        agent = str(raw.get("agent") or "")
        if not sid or not agent:
            continue
        step_by_id[sid] = raw
        if agent not in agents_ordered and agent in agent_index:
            agents_ordered.append(agent)
        next_ids = raw.get("next") if isinstance(raw.get("next"), list) else []
        steps.append(
            {
                "id": sid,
                "label": str(raw.get("id") or sid).replace("_", " "),
                "agentId": agent,
                "phase": str(raw.get("state") or "step"),
                "humanGate": bool(raw.get("human_gate_required")),
                "next": [str(n) for n in next_ids],
            }
        )

    edges: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for step in steps:
        from_agent = step["agentId"]
        for nid in step["next"]:
            target = step_by_id.get(nid)
            if not target:
                continue
            to_agent = str(target.get("agent") or "")
            if not to_agent or to_agent not in agent_index or from_agent not in agent_index:
                continue
            key = (from_agent, to_agent)
            if key in seen or from_agent == to_agent:
                # still record step-level multi hops with different label? skip dup
                if key in seen:
                    continue
            seen.add(key)
            kind = "gate" if target.get("human_gate_required") else "handoff"
            edges.append(
                {
                    "fromId": from_agent,
                    "toId": to_agent,
                    "kind": kind,
                    "label": f"{step['id']}→{nid}",
                }
            )

    agents = [agent_index[a] for a in agents_ordered if a in agent_index]
    dna_id = str(dna.get("id") or dna_path.stem)
    name = str(dna.get("name") or dna_id)
    return {
        "id": f"{pack_id}.dna.{dna_id}",
        "packId": pack_id,
        "kind": "dna",
        "scaleId": None,
        "label": name,
        "background": str(dna.get("objective") or name),
        "whenToUse": f"Use host DNA workflow `{dna_id}` when matching content archetype.",
        "whoShouldUse": f"Owner: {dna.get('owner') or pack_id + '.orchestrator'}",
        "howToUse": (
            f"Start DNA graph `{dna_id}` under business/{pack_id}/design/workflows/. "
            "Follow step handoffs; human gates when irreversible."
        ),
        "source": str(dna_path.relative_to(_ROOT)).replace("\\", "/"),
        "archetypes": [],
        "dnaWorkflowId": dna_id,
        "agentIds": [a["id"] for a in agents],
        "agents": agents,
        "steps": steps,
        "callEdges": edges,
        "phaseOrder": list(dict.fromkeys(s["phase"] for s in steps)),
    }


def _build_pack_group(pack_dir: Path, pack_id: str) -> dict | None:
    agent_index = _load_agent_index(pack_dir)
    if not agent_index:
        return None

    templates: list[dict] = []
    if pack_id == "video":
        for scale in _SCALE_TEMPLATES:
            templates.append(_template_from_scale(pack_id, scale, agent_index))

    wf_dir = pack_dir / "design" / "workflows"
    if wf_dir.is_dir():
        for dna_path in sorted(wf_dir.glob("wf_*_arch_*.dna.json")):
            tpl = _template_from_dna(pack_id, dna_path, agent_index)
            if tpl:
                templates.append(tpl)

    if not templates:
        return None

    return {
        "packId": pack_id,
        "label": pack_id.replace("_", " ").title(),
        "folderPath": f"business/{pack_id}",
        "agentCount": len(agent_index),
        "templateCount": len(templates),
        "templates": templates,
    }


def _ts_literal(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _render_ts(payload: dict) -> str:
    body = _ts_literal(payload)
    return f"""/* AUTO-GENERATED by scripts/business/export_agent_workflows_for_ui.py — do not edit. */
/* Production scale + DNA workflow templates for Agent Workflow UI. */

export type AgentWorkflowEdgeKind = "handoff" | "phase" | "gate" | "parallel";

export type AgentWorkflowTemplateKind = "scale" | "dna";

export interface AgentWorkflowAgentNode {{
  readonly id: string;
  readonly name: string;
  readonly role: string;
  readonly categoryId: string;
  readonly status: string;
  readonly href: string;
}}

export interface AgentWorkflowStep {{
  readonly id: string;
  readonly label: string;
  readonly agentId: string;
  readonly phase: string;
  readonly humanGate: boolean;
  readonly next: readonly string[];
}}

export interface AgentWorkflowEdge {{
  readonly fromId: string;
  readonly toId: string;
  readonly kind: AgentWorkflowEdgeKind;
  readonly label: string;
}}

export interface AgentWorkflowTemplate {{
  readonly id: string;
  readonly packId: string;
  readonly kind: AgentWorkflowTemplateKind;
  readonly scaleId: string | null;
  readonly label: string;
  readonly background: string;
  readonly whenToUse: string;
  readonly whoShouldUse: string;
  readonly howToUse: string;
  readonly source: string;
  readonly archetypes: readonly string[];
  readonly dnaWorkflowId: string | null;
  readonly agentIds: readonly string[];
  readonly agents: readonly AgentWorkflowAgentNode[];
  readonly steps: readonly AgentWorkflowStep[];
  readonly callEdges: readonly AgentWorkflowEdge[];
  readonly phaseOrder: readonly string[];
}}

export interface AgentWorkflowPackGroup {{
  readonly packId: string;
  readonly label: string;
  readonly folderPath: string;
  readonly agentCount: number;
  readonly templateCount: number;
  readonly templates: readonly AgentWorkflowTemplate[];
}}

export interface AgentWorkflowPayload {{
  readonly schemaVersion: string;
  readonly source: string;
  readonly packCount: number;
  readonly templateCount: number;
  readonly groups: readonly AgentWorkflowPackGroup[];
}}

export const AGENT_WORKFLOW_PAYLOAD: AgentWorkflowPayload = {body} as const;
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=_OUT)
    args = parser.parse_args(argv)

    business = _ROOT / "business"
    groups: list[dict] = []
    if business.is_dir():
        for pack_dir in sorted(business.iterdir()):
            if not pack_dir.is_dir() or pack_dir.name in _EXCLUDED_PACKS:
                continue
            if not (pack_dir / "agents").is_dir():
                continue
            group = _build_pack_group(pack_dir, pack_dir.name)
            if group:
                groups.append(group)

    template_count = sum(g["templateCount"] for g in groups)
    payload = {
        "schemaVersion": "1.0",
        "source": "business/*/design/workflows + production_scale_framework.md",
        "packCount": len(groups),
        "templateCount": template_count,
        "groups": groups,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_render_ts(payload), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "out": str(args.out.relative_to(_ROOT)),
                "packs": len(groups),
                "templates": template_count,
                "sample": [g["packId"] for g in groups[:5]],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
