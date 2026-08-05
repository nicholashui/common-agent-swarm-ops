"""Spine step agent loops — all spine agents use Host AgentLoopService when loadable.

Fail-closed: offline pack harness only; no production media tools.
"""

from __future__ import annotations

from typing import Any

from app.video.agent_loop_service import ACTIVATION_POLICY, get_agent_loop_service

# Full spine agent set from design DNA (all may run offline loops when pack loads)
SPINE_LOOP_AGENT_IDS: frozenset[str] = frozenset(
    {
        "video.orchestrator",
        "video.planner",
        "video.director",
        "video.screenwriter",
        "video.webresearch",
        "video.aiqaconsistency",
        "video.producer",
        "video.creativedirector",
        "video.gatekeeper",
    }
)

# Back-compat alias used by older imports
SPINE_L2_AGENT_IDS = SPINE_LOOP_AGENT_IDS


def activation_policy() -> dict[str, Any]:
    return dict(ACTIVATION_POLICY)


def run_spine_agent_loop(
    agent_id: str,
    *,
    goal: str,
    correlation_id: str,
    step_id: str,
    parent_assets: list[str] | None = None,
    force_l2_fail_once: bool = False,
) -> dict[str, Any]:
    """Run offline Plan/Act/Self-Review for a spine agent via Host AgentLoopService."""
    policy = activation_policy()
    if agent_id not in SPINE_LOOP_AGENT_IDS:
        return {
            "agent_id": agent_id,
            "step_id": step_id,
            "skipped": True,
            "reason": "agent not in spine loop allowlist",
            "policy": policy,
        }

    # force_l2_fail_once is reserved for tests via PackAgentRunner path;
    # Host service path uses real offline scoring.
    if force_l2_fail_once:
        from app.video.pack_runtime.runner import PackAgentRunner

        runner = PackAgentRunner()
        result = runner.run(
            agent_id,
            goal=goal,
            correlation_id=correlation_id,
            inputs={
                "step_id": step_id,
                "parent_assets": list(parent_assets or []),
                "mode": "spine_stub",
            },
            constraints={"network": False, "production": False, "production_media": False},
            emit_self_critique_to=agent_id,
            force_l2_fail_once=True,
        )
        data = result.to_dict()
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
            "critiques": data.get("critiques_emitted") or [],
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

    service = get_agent_loop_service()
    row = service.run(
        agent_id,
        organization_id="spine",
        goal=goal,
        correlation_id=correlation_id,
        inputs={
            "step_id": step_id,
            "parent_assets": list(parent_assets or []),
            "mode": "spine_stub",
        },
    )
    if row.get("error") and not row.get("result"):
        return {
            "agent_id": agent_id,
            "step_id": step_id,
            "skipped": False,
            "policy": policy,
            "status": "failed",
            "needs_hitl": False,
            "refinement_count": 0,
            "l1": {"passed": False},
            "l2": {"passed": False, "score": 0},
            "critiques": [],
            "evidence_refs": [],
            "notes": str(row.get("error")),
            "phases": row.get("phases") or {},
        }

    result = row.get("result") if isinstance(row.get("result"), dict) else row
    return {
        "agent_id": agent_id,
        "step_id": step_id,
        "skipped": False,
        "policy": policy,
        "status": row.get("status") or result.get("status"),
        "needs_hitl": bool(row.get("needs_hitl")),
        "refinement_count": row.get("refinement_count") or result.get("refinement_count") or 0,
        "l1": row.get("l1") or result.get("l1"),
        "l2": row.get("l2") or result.get("l2"),
        "critiques": row.get("critiques_emitted") or result.get("critiques_emitted") or [],
        "evidence_refs": row.get("evidence_refs") or result.get("evidence_refs") or [],
        "notes": row.get("notes") or result.get("notes") or "",
        "prompt_reference": result.get("prompt_reference") or "",
        "rubric_reference": result.get("rubric_reference") or "",
        "phases": row.get("phases")
        or {
            "plan": "parse brief + select path (offline harness)",
            "act": "stub tools only · no production media",
            "self_review": "L2 rubric offline score",
        },
    }


def loop_passed(loop: dict[str, Any] | None) -> bool:
    """True only when the offline loop is a clear pass (fail-closed otherwise)."""
    if not isinstance(loop, dict):
        return True
    if loop.get("skipped"):
        return True
    if loop.get("needs_hitl"):
        return False
    status = str(loop.get("status") or "")
    if status in {"failed", "needs_hitl", "needs_refine"}:
        return False
    l2 = loop.get("l2") if isinstance(loop.get("l2"), dict) else {}
    # Explicit L2 fail always fail-closes, even if status string is stale/ok.
    if l2.get("passed") is False:
        return False
    if status == "ok":
        return True
    return bool(l2.get("passed"))


__all__ = [
    "SPINE_L2_AGENT_IDS",
    "SPINE_LOOP_AGENT_IDS",
    "activation_policy",
    "loop_passed",
    "run_spine_agent_loop",
]
