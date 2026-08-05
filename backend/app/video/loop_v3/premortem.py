"""Premortem risk scaffold (agent_loop_v3 Phase 0) — offline, deterministic."""

from __future__ import annotations

from typing import Any


def run_premortem(
    goal: str,
    *,
    agent_id: str,
    cynefin_domain: str = "complicated",
) -> dict[str, Any]:
    """Assume failure → list plausible causes → mitigations for living plan."""
    g = (goal or "").strip() or "(empty goal)"
    base_risks = [
        {
            "cause": "Ambiguous success criteria — agent stops early or overshoots",
            "mitigation": "State explicit done criteria in goal constraints and L2 gates",
            "todo": "clarify_success_criteria",
        },
        {
            "cause": "Tool thrashing / repeated stub acts without progress",
            "mitigation": "Enforce max_steps + cycle detection on action digests",
            "todo": "bound_steps_and_cycle_hash",
        },
        {
            "cause": "Weak self-review lets incomplete artifacts pass",
            "mitigation": "Keep L1/L2 fail-closed; escalate_to_hitl on uncertainty",
            "todo": "fail_closed_l2",
        },
        {
            "cause": f"Role overstep by {agent_id} outside pack allowlist",
            "mitigation": "Closed-world pack inventory + tool allowlist only",
            "todo": "registered_agents_only",
        },
        {
            "cause": "Context rot / lost original intent mid-loop",
            "mitigation": "Persist goal + plan summary in project memory each run",
            "todo": "durable_project_memory",
        },
    ]
    if cynefin_domain in {"complex", "chaotic"}:
        base_risks.append(
            {
                "cause": "Emergent coordination failure across crew agents",
                "mitigation": "Prefer sequential stop_on_failure for critical spine steps",
                "todo": "crew_stop_on_failure",
            }
        )
    if "media" in g.lower() or "sora" in g.lower() or "veo" in g.lower():
        base_risks.insert(
            0,
            {
                "cause": "Live media activation assumed without Host go-live",
                "mitigation": "Agent-loop Act remains stub/live_blocked; no production_media",
                "todo": "media_fail_closed",
            },
        )

    return {
        "goal": g[:500],
        "agent_id": agent_id,
        "cynefin_domain": cynefin_domain,
        "risks": base_risks[:7],
        "mitigations": [r["mitigation"] for r in base_risks[:7]],
        "todo_items": [r["todo"] for r in base_risks[:7]],
        "note": "Offline Premortem scaffold — not a live Red Team LLM.",
    }
