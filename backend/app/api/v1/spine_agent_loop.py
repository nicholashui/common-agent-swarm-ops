"""Thin Plan → Act → Self-Review loop for selected spine agents (offline Host).

Uses pack_runtime PackAgentRunner (no network / no production media).
Applies only to closed-world agents with materialized rubrics (planner, QC).
"""

from __future__ import annotations

from typing import Any

from app.video.pack_runtime.critique import CritiqueBus, CritiqueSeverity
from app.video.pack_runtime.runner import PackAgentRunner

# Must-have: L2 offline loop for these spine roles only
SPINE_L2_AGENT_IDS: frozenset[str] = frozenset(
    {
        "video.planner",
        "video.aiqaconsistency",
    }
)

# Product path never enables production tool activation
_ACTIVATION_POLICY = {
    "production_tools": False,
    "network": False,
    "production_media": False,
    "registered_only": True,
}


def activation_policy() -> dict[str, Any]:
    """Host product activation policy (fail-closed)."""
    return dict(_ACTIVATION_POLICY)


def run_spine_agent_loop(
    agent_id: str,
    *,
    goal: str,
    correlation_id: str,
    step_id: str,
    parent_assets: list[str] | None = None,
    force_l2_fail_once: bool = False,
) -> dict[str, Any]:
    """Run offline Plan/Act/Self-Review for one spine agent.

    Returns a redacted loop summary for attachment onto ArtifactHandoffV1.
    """
    policy = activation_policy()
    if agent_id not in SPINE_L2_AGENT_IDS:
        return {
            "agent_id": agent_id,
            "step_id": step_id,
            "skipped": True,
            "reason": "agent not in spine L2 allowlist",
            "policy": policy,
        }

    bus = CritiqueBus()
    runner = PackAgentRunner(critique_bus=bus)
    result = runner.run(
        agent_id,
        goal=goal,
        correlation_id=correlation_id,
        inputs={
            "step_id": step_id,
            "parent_assets": list(parent_assets or []),
            "mode": "spine_stub",
        },
        constraints={
            "network": False,
            "production": False,
            "production_media": False,
        },
        emit_self_critique_to=agent_id,
        force_l2_fail_once=force_l2_fail_once,
    )
    data = result.to_dict()

    # On L2 failure after refinements, emit major critique (self) for audit
    critiques = list(data.get("critiques_emitted") or [])
    l2 = data.get("l2") if isinstance(data.get("l2"), dict) else {}
    if not l2.get("passed") or data.get("status") not in {"ok"}:
        try:
            msg = bus.send(
                correlation_id=correlation_id,
                from_id=agent_id,
                to_id=agent_id,
                severity=CritiqueSeverity.MAJOR,
                claim=(
                    f"Spine step {step_id} self-review incomplete "
                    f"status={data.get('status')} l2={l2.get('score')}"
                ),
                allowed_outputs=(agent_id,),
                artifact_ref=f"spine:{step_id}",
                evidence_refs=tuple(data.get("evidence_refs") or ())[:5],
                kind="critique",
            )
            critiques.append(msg.to_dict())
        except (PermissionError, ValueError):
            pass

    return {
        "agent_id": agent_id,
        "step_id": step_id,
        "skipped": False,
        "policy": policy,
        "status": data.get("status"),
        "needs_hitl": bool(data.get("needs_hitl")),
        "refinement_count": data.get("refinement_count", 0),
        "l1": data.get("l1"),
        "l2": data.get("l2"),
        "critiques": critiques,
        "evidence_refs": data.get("evidence_refs") or [],
        "notes": data.get("notes") or "",
        "prompt_reference": data.get("prompt_reference") or "",
        "rubric_reference": data.get("rubric_reference") or "",
        "phases": {
            "plan": "parse brief + select path (offline harness)",
            "act": "stub tools only · no production media",
            "self_review": "L2 rubric offline score",
        },
    }


def loop_passed(loop: dict[str, Any] | None) -> bool:
    """Whether spine may advance after agent loop."""
    if not isinstance(loop, dict):
        return True
    if loop.get("skipped"):
        return True
    if loop.get("needs_hitl"):
        return False
    status = str(loop.get("status") or "")
    if status == "ok":
        return True
    l2 = loop.get("l2") if isinstance(loop.get("l2"), dict) else {}
    return bool(l2.get("passed")) and status not in {"failed", "needs_hitl"}


__all__ = [
    "SPINE_L2_AGENT_IDS",
    "activation_policy",
    "loop_passed",
    "run_spine_agent_loop",
]
