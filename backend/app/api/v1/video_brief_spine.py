"""User brief contract + video spine dry-run helpers (process-local façade).

Source of step order: business/video/design/workflows/wf_video_spine_v1.dna.json
(design DNA; production_ready remains false for product path).
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

# backend/app/api/v1/this.py -> parents[4] == repository root
_ROOT = Path(__file__).resolve().parents[4]
_DESIGN_SPINE_DNA = (
    _ROOT / "business" / "video" / "design" / "workflows" / "wf_video_spine_v1.dna.json"
)

SPINE_WORKFLOW_ID = "wf_video_spine_v1"
USER_BRIEF_VERSION = "UserBriefV1"
HANDOFF_CONTRACT_VERSION = "ArtifactHandoffV1"

# L1 required fields for spine stub handoffs (common-agent-structure Input Package subset)
_HANDOFF_L1_REQUIRED: tuple[str, ...] = (
    "artifact_id",
    "version",
    "kind",
    "step_id",
    "agent_id",
    "stub",
    "production_media",
    "parent_assets",
    "qc_status",
    "summary",
    "created_at",
    "provenance_manifest",
)

# Phase-1 crew (Epic B) — closed world, required when video brief materializes.
PHASE_1_AGENT_IDS: tuple[str, ...] = (
    "video.orchestrator",
    "video.planner",
    "video.producer",
)

# Full spine agent set from design DNA (Epic C).
SPINE_AGENT_IDS: tuple[str, ...] = (
    "video.orchestrator",
    "video.planner",
    "video.director",
    "video.screenwriter",
    "video.webresearch",
    "video.aiqaconsistency",
    "video.producer",
)

# Deterministic stub mapping: step_id -> (stub_tool, artifact_kind)
_STEP_STUBS: dict[str, tuple[str, str]] = {
    "orchestrate": ("audit_log", "run_context"),
    "plan": ("audit_log", "parsed_brief"),
    "direct": ("audit_log", "creative_direction"),
    "screenwrite": ("video_script_format", "script"),
    "research": ("audit_log", "research_bundle"),
    "media_gen": ("video_media_gen_stub", "media_stub"),
    "qc": ("video_qc_stub", "qc_report"),
    "package": ("video_package_stub", "package"),
}

_VALID_SCALE = frozenset({"S1", "S2", "S3", "S4", "S5", "S6", "S7"})
_VALID_ARCHETYPE = frozenset({"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"})
_VALID_LOCALE = frozenset({"en", "zh-Hant", "zh-Hans"})


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def load_design_spine_steps() -> list[dict[str, Any]]:
    """Load ordered steps from design DNA; fall back to hardcoded design order."""
    if _DESIGN_SPINE_DNA.is_file():
        try:
            raw = json.loads(_DESIGN_SPINE_DNA.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = None
        if isinstance(raw, dict) and isinstance(raw.get("steps"), list) and raw["steps"]:
            out: list[dict[str, Any]] = []
            for step in raw["steps"]:
                if not isinstance(step, dict):
                    continue
                sid = str(step.get("id") or "").strip()
                agent = str(step.get("agent") or "").strip()
                if not sid or not agent:
                    continue
                tools = step.get("tools") if isinstance(step.get("tools"), list) else []
                stub_tool, art_kind = _STEP_STUBS.get(
                    sid,
                    (str(tools[0]) if tools else "audit_log", f"{sid}_output"),
                )
                out.append(
                    {
                        "id": sid,
                        "agent_id": agent,
                        "stub_tool": stub_tool,
                        "artifact_kind": art_kind,
                        "human_gate_required": bool(step.get("human_gate_required")),
                        "irreversible": bool(step.get("irreversible")),
                    }
                )
            if out:
                return out
    # Fail-closed static design order (matches SYSTEM_REFERENCE spine)
    return [
        {
            "id": sid,
            "agent_id": agent,
            "stub_tool": _STEP_STUBS[sid][0],
            "artifact_kind": _STEP_STUBS[sid][1],
            "human_gate_required": sid == "package",
            "irreversible": sid == "package",
        }
        for sid, agent in (
            ("orchestrate", "video.orchestrator"),
            ("plan", "video.planner"),
            ("direct", "video.director"),
            ("screenwrite", "video.screenwriter"),
            ("research", "video.webresearch"),
            ("media_gen", "video.director"),
            ("qc", "video.aiqaconsistency"),
            ("package", "video.producer"),
        )
    ]


def validate_user_brief_text(text: str) -> str | None:
    """Return error message if text invalid; None if OK."""
    cleaned = (text or "").strip()
    if not cleaned:
        return "Brief text is required (non-empty goal/spec)."
    if len(cleaned) > 2_000:
        return "Brief text exceeds 2000 characters."
    return None


def build_user_brief(
    *,
    text: str,
    brief_meta: dict[str, Any] | None,
    correlation_id: str,
    mint_id: bool = True,
) -> tuple[dict[str, Any] | None, str | None]:
    """Build UserBriefV1 snapshot. Returns (brief, error_message).

    When mint_id is False (recommend preview), omit brief_id so materialize owns identity.
    """
    err = validate_user_brief_text(text)
    if err:
        return None, err
    meta = brief_meta if isinstance(brief_meta, dict) else {}
    locale = str(meta.get("locale") or "en").strip()
    if locale not in _VALID_LOCALE:
        locale = "en"
    scale = meta.get("scale_profile")
    scale_s = str(scale).strip().upper() if scale is not None and str(scale).strip() else None
    if scale_s is not None and scale_s not in _VALID_SCALE:
        return None, f"Invalid scale_profile {scale_s!r}; expected one of {sorted(_VALID_SCALE)}."
    arch = meta.get("archetype")
    arch_s = str(arch).strip().upper() if arch is not None and str(arch).strip() else None
    if arch_s is not None and arch_s not in _VALID_ARCHETYPE:
        return None, f"Invalid archetype {arch_s!r}; expected one of {sorted(_VALID_ARCHETYPE)}."
    constraints_raw = meta.get("constraints")
    constraints: dict[str, Any] = {}
    if isinstance(constraints_raw, dict):
        # Shallow allowlist — no nested blobs / secrets
        for key in ("max_duration_sec", "budget_band", "platform", "notes"):
            if key in constraints_raw and constraints_raw[key] is not None:
                val = constraints_raw[key]
                if key == "max_duration_sec":
                    try:
                        constraints[key] = max(1, min(int(val), 86_400))
                    except (TypeError, ValueError):
                        return None, "constraints.max_duration_sec must be an integer."
                elif key in {"budget_band", "platform"}:
                    constraints[key] = str(val)[:80]
                elif key == "notes":
                    constraints[key] = str(val)[:500]
    # Reject obvious secret-shaped keys if present in raw meta
    for banned in ("password", "secret", "api_key", "token", "authorization"):
        if banned in {k.lower() for k in meta}:
            return None, f"Brief must not include field {banned!r}."

    brief: dict[str, Any] = {
        "version": USER_BRIEF_VERSION,
        "text": text.strip(),
        "locale": locale,
        "scale_profile": scale_s,
        "archetype": arch_s,
        "constraints": constraints,
        "as_of": _utc_now().isoformat(),
        "correlation_id": correlation_id,
    }
    if mint_id:
        brief["brief_id"] = _new_id("brief")
    return brief, None


def goal_looks_like_video_brief(goal: str) -> bool:
    g = (goal or "").lower()
    return any(
        k in g
        for k in (
            "video",
            "youtube",
            "film",
            "cinematic",
            "shot",
            "script",
            "wuxia",
            "storyboard",
            "director",
            "editor",
            "trailer",
            "production brief",
            "brand film",
            "short film",
            "social clip",
        )
    )


def phase1_and_spine_member_ids(*, prefer_video: bool, max_slots: int) -> list[str]:
    """Closed-world ordered agent ids for Phase-1 + spine-capable draft."""
    if not prefer_video:
        return []
    ordered: list[str] = []
    for aid in PHASE_1_AGENT_IDS:
        if aid not in ordered:
            ordered.append(aid)
    for aid in SPINE_AGENT_IDS:
        if aid not in ordered:
            ordered.append(aid)
    return ordered[: max(3, min(max_slots, 12))]


def init_spine_state(*, brief_id: str | None) -> dict[str, Any]:
    steps_def = load_design_spine_steps()
    steps = [
        {
            "id": s["id"],
            "agent_id": s["agent_id"],
            "stub_tool": s["stub_tool"],
            "artifact_kind": s["artifact_kind"],
            "human_gate_required": s["human_gate_required"],
            "irreversible": s["irreversible"],
            "status": "queued",
            "artifact_ref": None,
            "completed_at": None,
            "note": None,
        }
        for s in steps_def
    ]
    return {
        "workflow_id": SPINE_WORKFLOW_ID,
        "production_ready": False,
        "mode": "stub",
        "status": "ready",
        "current_step_index": 0,
        "brief_id": brief_id,
        "steps": steps,
        "artifacts": {},
        "approval_id": None,
        "note": "stub run · not production media",
    }


def next_runnable_step(spine: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first step that is still queued (or waiting package after approve)."""
    status = str(spine.get("status") or "")
    if status in {"completed", "denied", "failed"}:
        return None
    steps = spine.get("steps") if isinstance(spine.get("steps"), list) else []
    for step in steps:
        if not isinstance(step, dict):
            continue
        st = str(step.get("status") or "")
        if st == "queued":
            return step
        if st == "waiting_for_approval":
            return step
    return None


def collect_parent_asset_refs(spine: dict[str, Any], up_to_index: int) -> list[str]:
    """Prior completed step artifact refs for linear handoff lineage."""
    steps = spine.get("steps") if isinstance(spine.get("steps"), list) else []
    parents: list[str] = []
    for j in range(max(0, up_to_index)):
        step = steps[j] if j < len(steps) else None
        if not isinstance(step, dict):
            continue
        ref = step.get("artifact_ref")
        if ref:
            parents.append(str(ref))
    brief_id = spine.get("brief_id")
    if brief_id and not parents:
        parents.append(f"brief:{brief_id}")
    return parents


def build_handoff_artifact(
    *,
    step_id: str,
    agent_id: str,
    kind: str,
    stub_tool: str | None,
    brief_text: str,
    parent_assets: list[str],
    human_gate: bool,
) -> dict[str, Any]:
    """Build ArtifactHandoffV1 payload (stub · not production media)."""
    art_ref = _new_id("art")
    qc = "pending_human" if human_gate else "l1_pass"
    return {
        "artifact_id": art_ref,
        "ref": art_ref,
        "version": 1,
        "contract": HANDOFF_CONTRACT_VERSION,
        "kind": kind,
        "step_id": step_id,
        "agent_id": agent_id,
        "stub_tool": stub_tool,
        "stub": True,
        "production_media": False,
        "parent_assets": list(parent_assets),
        "qc_status": qc,
        "technical_spec": {"mode": "stub", "handoff": HANDOFF_CONTRACT_VERSION},
        "rights_and_consent": "n/a_stub",
        "continuity_state": None,
        "target_channels": [],
        "provenance_manifest": f"stub:{step_id}:{art_ref}",
        "summary": _stub_summary(step_id, kind, brief_text),
        "created_at": _utc_now().isoformat(),
    }


def validate_handoff_l1(artifact: dict[str, Any] | None) -> list[str]:
    """Return L1 validation errors (empty list = pass). Fail-closed on production_media=true for stubs."""
    if not isinstance(artifact, dict):
        return ["handoff is not an object"]
    errors: list[str] = []
    for key in _HANDOFF_L1_REQUIRED:
        if key not in artifact or artifact.get(key) is None:
            errors.append(f"missing required field {key}")
    if artifact.get("stub") is not True:
        errors.append("stub must be true for spine dry-run handoffs")
    if artifact.get("production_media") is True:
        errors.append("production_media must be false for spine stub path")
    parents = artifact.get("parent_assets")
    if not isinstance(parents, list):
        errors.append("parent_assets must be a list")
    if not str(artifact.get("artifact_id") or "").strip():
        errors.append("artifact_id must be non-empty")
    if not str(artifact.get("summary") or "").strip():
        errors.append("summary must be non-empty")
    qc = str(artifact.get("qc_status") or "")
    if qc not in {"l1_pass", "pending_human", "l1_fail", "denied"}:
        errors.append(f"qc_status invalid: {qc!r}")
    return errors


def apply_stub_step(
    spine: dict[str, Any],
    *,
    step_id: str | None,
    brief_text: str,
    idempotency_key: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """Advance one stub step. Returns (updated_spine_snapshot_fields, error).

    Mutates spine in place; caller holds lock.
    Emits ArtifactHandoffV1 and fails closed on L1 validation errors.
    """
    if not isinstance(spine, dict):
        return None, "Spine not attached."
    if str(spine.get("status")) in {"completed", "denied", "failed"}:
        return None, f"Spine is terminal ({spine.get('status')})."
    if str(spine.get("status")) == "waiting_for_approval":
        return None, "Package is waiting for human approval; submit package decision first."

    steps = spine.get("steps") if isinstance(spine.get("steps"), list) else []
    target: dict[str, Any] | None = None
    target_index = -1
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        if step_id and str(step.get("id")) != step_id:
            continue
        if str(step.get("status")) == "queued":
            # Enforce linear order: no later step before earlier complete
            prior_ok = all(
                str(steps[j].get("status")) == "completed"
                for j in range(idx)
                if isinstance(steps[j], dict)
            )
            if not prior_ok:
                return None, "Earlier spine steps must complete before this step."
            target = step
            target_index = idx
            break
        if step_id and str(step.get("id")) == step_id:
            return None, f"Step {step_id} is not runnable (status={step.get('status')})."

    if target is None:
        return None, "No queued spine step to run."

    sid = str(target["id"])
    # Idempotency map: same key reuses prior success without re-running side effects
    idem_map = spine.get("_idempotency")
    if not isinstance(idem_map, dict):
        idem_map = {}
        spine["_idempotency"] = idem_map
    if idempotency_key and idempotency_key in idem_map:
        return spine, None

    art_kind = str(target.get("artifact_kind") or f"{sid}_output")
    human_gate = bool(target.get("human_gate_required"))
    agent_id = str(target.get("agent_id") or "")
    parents = collect_parent_asset_refs(spine, target_index)

    # Plan → Act → Self-Review for selected spine agents (offline L2)
    from app.api.v1.spine_agent_loop import (
        SPINE_L2_AGENT_IDS,
        loop_passed,
        run_spine_agent_loop,
    )

    agent_loop: dict[str, Any] | None = None
    if agent_id in SPINE_L2_AGENT_IDS and not human_gate:
        corr = str(spine.get("brief_id") or spine.get("workflow_id") or "spine")
        agent_loop = run_spine_agent_loop(
            agent_id,
            goal=brief_text,
            correlation_id=f"{corr}:{sid}",
            step_id=sid,
            parent_assets=parents,
        )
        # Record critiques on spine for operator visibility
        critiques = spine.setdefault("critiques", [])
        if isinstance(critiques, list):
            for c in agent_loop.get("critiques") or []:
                if isinstance(c, dict):
                    critiques.append(c)
        if not loop_passed(agent_loop):
            target["status"] = "failed"
            target["note"] = (
                f"Agent loop fail-closed: status={agent_loop.get('status')} "
                f"l2={((agent_loop.get('l2') or {}).get('score'))}"
            )
            spine["status"] = "failed"
            spine["last_agent_loop"] = agent_loop
            return None, (
                f"Spine step {sid} failed Plan/Act/Self-Review "
                f"(status={agent_loop.get('status')}; "
                f"refinements={agent_loop.get('refinement_count')}). "
                "Fail-closed; no production tools."
            )

    artifact = build_handoff_artifact(
        step_id=sid,
        agent_id=agent_id,
        kind=art_kind,
        stub_tool=str(target.get("stub_tool") or "") or None,
        brief_text=brief_text,
        parent_assets=parents,
        human_gate=human_gate,
    )
    if agent_loop is not None:
        artifact["agent_loop"] = {
            "status": agent_loop.get("status"),
            "l1": agent_loop.get("l1"),
            "l2": agent_loop.get("l2"),
            "refinement_count": agent_loop.get("refinement_count"),
            "phases": agent_loop.get("phases"),
            "policy": agent_loop.get("policy"),
            "rubric_reference": agent_loop.get("rubric_reference"),
            "evidence_refs": (agent_loop.get("evidence_refs") or [])[:8],
        }
        l2 = agent_loop.get("l2") if isinstance(agent_loop.get("l2"), dict) else {}
        if l2.get("passed"):
            artifact["qc_status"] = "l1_pass"
    l1_errors = validate_handoff_l1(artifact)
    if l1_errors:
        return None, "L1 handoff validation failed: " + "; ".join(l1_errors)

    art_ref = str(artifact["artifact_id"])
    arts = spine.setdefault("artifacts", {})
    if not isinstance(arts, dict):
        spine["artifacts"] = {}
        arts = spine["artifacts"]
    arts[art_ref] = artifact

    if human_gate:
        # Package: complete stub artifact but pause for human
        target["status"] = "waiting_for_approval"
        target["artifact_ref"] = art_ref
        target["note"] = "Package stub ready · human gate required · L1 pending_human"
        target["completed_at"] = None
        spine["status"] = "waiting_for_approval"
        spine["current_step_index"] = target_index
        approval_id = _new_id("appr")
        spine["approval_id"] = approval_id
        if idempotency_key:
            idem_map[idempotency_key] = {"step_id": sid, "artifact_ref": art_ref}
            spine["_last_idempotency_key"] = idempotency_key
        return spine, None

    target["status"] = "completed"
    target["artifact_ref"] = art_ref
    target["completed_at"] = _utc_now().isoformat()
    loop_note = ""
    if agent_loop and not agent_loop.get("skipped"):
        l2s = (agent_loop.get("l2") or {}).get("score")
        loop_note = f" · agent_loop L2={l2s}"
    target["note"] = f"stub completed · L1 pass{loop_note}"
    spine["current_step_index"] = target_index + 1
    spine["status"] = "running"
    # If last non-gate step finished, stay running until package
    remaining = any(str(s.get("status")) == "queued" for s in steps if isinstance(s, dict))
    if not remaining:
        spine["status"] = "completed"
    if idempotency_key:
        idem_map[idempotency_key] = {"step_id": sid, "artifact_ref": art_ref}
        spine["_last_idempotency_key"] = idempotency_key
    return spine, None


def decide_package(
    spine: dict[str, Any],
    *,
    decision: str,
    reason: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Approve or deny package gate. Mutates spine."""
    if not isinstance(spine, dict):
        return None, "Spine not attached."
    if str(spine.get("status")) != "waiting_for_approval":
        return None, "Spine is not waiting for package approval."
    decision_n = decision.strip().lower()
    if decision_n not in {"approved", "denied"}:
        return None, "Decision must be approved or denied."
    reason_s = (reason or "").strip()
    if len(reason_s) < 3:
        return None, "Decision reason is required (min 3 characters)."
    if len(reason_s) > 500:
        return None, "Decision reason exceeds 500 characters."

    steps = spine.get("steps") if isinstance(spine.get("steps"), list) else []
    package = next(
        (s for s in steps if isinstance(s, dict) and str(s.get("id")) == "package"),
        None,
    )
    if package is None:
        return None, "Package step missing from spine."
    if str(package.get("status")) != "waiting_for_approval":
        return None, "Package step is not waiting for approval."

    if decision_n == "approved":
        package["status"] = "completed"
        package["completed_at"] = _utc_now().isoformat()
        package["note"] = f"Human approved: {reason_s[:200]}"
        spine["status"] = "completed"
        spine["package_decision"] = {
            "value": "approved",
            "reason": reason_s,
            "decided_at": _utc_now().isoformat(),
        }
    else:
        package["status"] = "denied"
        package["completed_at"] = _utc_now().isoformat()
        package["note"] = f"Human denied: {reason_s[:200]}"
        spine["status"] = "denied"
        spine["package_decision"] = {
            "value": "denied",
            "reason": reason_s,
            "decided_at": _utc_now().isoformat(),
        }
    return spine, None


def _stub_summary(step_id: str, art_kind: str, brief_text: str) -> str:
    digest = re.sub(r"\s+", " ", brief_text.strip())[:80]
    return (
        f"[stub] {art_kind} from step {step_id} · not production media · "
        f"brief_excerpt={digest!r}"
    )


def public_artifact_view(
    artifact: dict[str, Any] | None,
    *,
    swarm_id: str | None = None,
) -> dict[str, Any] | None:
    """Redacted artifact payload for GET-by-ref (stub · not production media)."""
    if not isinstance(artifact, dict):
        return None
    ref = artifact.get("artifact_id") or artifact.get("ref")
    out: dict[str, Any] = {
        "artifact_id": ref,
        "ref": ref,
        "version": artifact.get("version", 1),
        "contract": artifact.get("contract") or HANDOFF_CONTRACT_VERSION,
        "kind": artifact.get("kind"),
        "step_id": artifact.get("step_id"),
        "agent_id": artifact.get("agent_id"),
        "stub_tool": artifact.get("stub_tool"),
        "stub": True,
        "production_media": False,
        "parent_assets": list(artifact.get("parent_assets") or [])
        if isinstance(artifact.get("parent_assets"), list)
        else [],
        "qc_status": artifact.get("qc_status"),
        "summary": artifact.get("summary"),
        "created_at": artifact.get("created_at"),
        "provenance_manifest": artifact.get("provenance_manifest"),
        "agent_loop": artifact.get("agent_loop"),
        "note": "stub run · not production media",
    }
    if swarm_id:
        out["swarm_id"] = swarm_id
    return out


def public_spine_view(spine: dict[str, Any] | None) -> dict[str, Any] | None:
    """Redact internal keys for API response."""
    if not isinstance(spine, dict):
        return None
    steps_out = []
    for s in spine.get("steps") or []:
        if not isinstance(s, dict):
            continue
        steps_out.append(
            {
                "id": s.get("id"),
                "agent_id": s.get("agent_id"),
                "stub_tool": s.get("stub_tool"),
                "artifact_kind": s.get("artifact_kind"),
                "human_gate_required": bool(s.get("human_gate_required")),
                "status": s.get("status"),
                "artifact_ref": s.get("artifact_ref"),
                "completed_at": s.get("completed_at"),
                "note": s.get("note"),
            }
        )
    arts_out: dict[str, Any] = {}
    for ref, art in (spine.get("artifacts") or {}).items():
        if isinstance(art, dict):
            arts_out[str(ref)] = {
                "ref": art.get("ref", ref),
                "kind": art.get("kind"),
                "step_id": art.get("step_id"),
                "agent_id": art.get("agent_id"),
                "stub": True,
                "production_media": False,
                "summary": art.get("summary"),
                "created_at": art.get("created_at"),
            }
    critiques_out: list[dict[str, Any]] = []
    for c in spine.get("critiques") or []:
        if isinstance(c, dict):
            critiques_out.append(
                {
                    "message_id": c.get("message_id"),
                    "from_id": c.get("from_id"),
                    "to_id": c.get("to_id"),
                    "severity": c.get("severity"),
                    "claim": c.get("claim"),
                    "kind": c.get("kind"),
                    "artifact_ref": c.get("artifact_ref"),
                }
            )
    return {
        "workflow_id": spine.get("workflow_id", SPINE_WORKFLOW_ID),
        "production_ready": False,
        "mode": "stub",
        "status": spine.get("status"),
        "current_step_index": spine.get("current_step_index", 0),
        "brief_id": spine.get("brief_id"),
        "steps": steps_out,
        "artifacts": arts_out,
        "critiques": critiques_out[-20:],
        "approval_id": spine.get("approval_id"),
        "package_decision": spine.get("package_decision"),
        "activation_policy": {
            "production_tools": False,
            "network": False,
            "production_media": False,
            "registered_only": True,
        },
        "note": spine.get("note") or "stub run · not production media",
    }


__all__ = [
    "PHASE_1_AGENT_IDS",
    "SPINE_AGENT_IDS",
    "SPINE_WORKFLOW_ID",
    "USER_BRIEF_VERSION",
    "apply_stub_step",
    "build_user_brief",
    "decide_package",
    "goal_looks_like_video_brief",
    "init_spine_state",
    "load_design_spine_steps",
    "next_runnable_step",
    "phase1_and_spine_member_ids",
    "HANDOFF_CONTRACT_VERSION",
    "build_handoff_artifact",
    "collect_parent_asset_refs",
    "public_artifact_view",
    "public_spine_view",
    "validate_handoff_l1",
    "validate_user_brief_text",
]
