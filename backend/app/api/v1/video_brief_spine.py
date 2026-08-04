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
) -> tuple[dict[str, Any] | None, str | None]:
    """Build UserBriefV1 snapshot. Returns (brief, error_message)."""
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

    brief = {
        "brief_id": _new_id("brief"),
        "version": USER_BRIEF_VERSION,
        "text": text.strip(),
        "locale": locale,
        "scale_profile": scale_s,
        "archetype": arch_s,
        "constraints": constraints,
        "as_of": _utc_now().isoformat(),
        "correlation_id": correlation_id,
    }
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


def apply_stub_step(
    spine: dict[str, Any],
    *,
    step_id: str | None,
    brief_text: str,
    idempotency_key: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """Advance one stub step. Returns (updated_spine_snapshot_fields, error).

    Mutates spine in place; caller holds lock.
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
    # Idempotency: if already completed with same key, no-op success is handled by caller store
    if idempotency_key and spine.get("_last_idempotency_key") == idempotency_key:
        return spine, None

    art_kind = str(target.get("artifact_kind") or f"{sid}_output")
    art_ref = _new_id("art")
    artifact = {
        "ref": art_ref,
        "kind": art_kind,
        "step_id": sid,
        "agent_id": target.get("agent_id"),
        "stub_tool": target.get("stub_tool"),
        "stub": True,
        "production_media": False,
        "summary": _stub_summary(sid, art_kind, brief_text),
        "created_at": _utc_now().isoformat(),
    }
    arts = spine.setdefault("artifacts", {})
    if not isinstance(arts, dict):
        spine["artifacts"] = {}
        arts = spine["artifacts"]
    arts[art_ref] = artifact

    if bool(target.get("human_gate_required")):
        # Package: complete stub artifact but pause for human
        target["status"] = "waiting_for_approval"
        target["artifact_ref"] = art_ref
        target["note"] = "Package stub ready · human gate required"
        target["completed_at"] = None
        spine["status"] = "waiting_for_approval"
        spine["current_step_index"] = target_index
        approval_id = _new_id("appr")
        spine["approval_id"] = approval_id
        if idempotency_key:
            spine["_last_idempotency_key"] = idempotency_key
        return spine, None

    target["status"] = "completed"
    target["artifact_ref"] = art_ref
    target["completed_at"] = _utc_now().isoformat()
    target["note"] = "stub completed"
    spine["current_step_index"] = target_index + 1
    spine["status"] = "running"
    # If last non-gate step finished, stay running until package
    remaining = any(str(s.get("status")) == "queued" for s in steps if isinstance(s, dict))
    if not remaining:
        spine["status"] = "completed"
    if idempotency_key:
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
    return {
        "workflow_id": spine.get("workflow_id", SPINE_WORKFLOW_ID),
        "production_ready": False,
        "mode": "stub",
        "status": spine.get("status"),
        "current_step_index": spine.get("current_step_index", 0),
        "brief_id": spine.get("brief_id"),
        "steps": steps_out,
        "artifacts": arts_out,
        "approval_id": spine.get("approval_id"),
        "package_decision": spine.get("package_decision"),
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
    "public_spine_view",
    "validate_user_brief_text",
]
