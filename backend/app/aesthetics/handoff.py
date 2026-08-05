"""Attach AestheticVerdict onto Shared Artifact Handoff qc_status (spec §8.3)."""

from __future__ import annotations

from typing import Any


def attach_verdict_to_handoff(
    handoff: dict[str, Any],
    verdict: dict[str, Any],
) -> dict[str, Any]:
    """Return a shallow-copied handoff with aesthetic qc fields.

    Does not invent production_media=true. Fail-closed: strips live claims.
    """
    out = dict(handoff)
    aq = float(verdict.get("aesthetic_quality") or 0.0)
    escalate = bool(verdict.get("escalate_to_hitl"))
    # Always namespace under aesthetic_* so consumers can filter aesthetics-derived QC.
    # HITL escalation is also mirrored in qc_meta.aesthetic.escalate_to_hitl.
    if escalate:
        qc = "aesthetic_pending_human"
    elif aq >= 0.7:
        qc = "aesthetic_pass"
    elif aq >= 0.4:
        qc = "aesthetic_review"
    else:
        qc = "aesthetic_fail"

    out["qc_status"] = qc
    aesthetic = {
        "agent_id": "specials.aesthetics-agent",
        "profile_id": verdict.get("profile_id"),
        "aesthetic_quality": aq,
        "hack_likelihood": verdict.get("hack_likelihood"),
        "intent_fidelity": verdict.get("intent_fidelity"),
        "emotion_match": verdict.get("emotion_match"),
        "top_failing_dimensions": list(
            verdict.get("top_failing_dimensions") or []
        ),
        "actionable_critique": list(verdict.get("actionable_critique") or [])[:5],
        "uncertainty_flag": bool(verdict.get("uncertainty_flag")),
        "escalate_to_hitl": escalate,
        "mode": verdict.get("mode"),
        "activation_policy": verdict.get("activation_policy")
        or {"production_media": False, "live_vision": False},
    }
    # Nested under handoff without clobbering other qc metadata
    meta = dict(out.get("qc_meta") or {}) if isinstance(out.get("qc_meta"), dict) else {}
    meta["aesthetic"] = aesthetic
    out["qc_meta"] = meta
    # Never upgrade production_media via aesthetics attach
    if out.get("production_media") is True and (
        aesthetic["activation_policy"] or {}
    ).get("production_media") is False:
        out["production_media"] = False
    return out
