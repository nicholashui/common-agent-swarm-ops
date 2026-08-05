"""After-Action Review + Double-Loop scaffold (agent_loop_v3 Phase 4)."""

from __future__ import annotations

from typing import Any


def build_aar(
    *,
    goal: str,
    plan_summary: str,
    actual_status: str,
    observations: list[str],
    issues: list[str],
    cynefin_domain: str = "complicated",
) -> dict[str, Any]:
    """Structured 4-question AAR artifact."""
    supposed = plan_summary or f"Complete offline Plan→Act→Self-Review for: {goal[:200]}"
    happened = (
        f"status={actual_status}; "
        f"observations={len(observations)}; issues={len(issues)}"
    )
    why_bits = list(issues[:5]) if issues else ["No major issues recorded in offline harness"]
    if cynefin_domain in {"complex", "chaotic"} and issues:
        why_bits.append("5_whys_lite: check prompts → process → tools → data → context")

    next_actions: list[str] = []
    if issues:
        next_actions.append("Tighten L2 rubric or goal constraints for next run")
        next_actions.append("Re-run with enable_fast_path=false if domain is complex")
    else:
        next_actions.append("Record successful pattern for RPD fast path")
        next_actions.append("Keep fail-closed production_media policy")

    return {
        "supposed_to_happen": supposed[:800],
        "what_actually_happened": happened,
        "why": why_bits,
        "what_next": next_actions,
        "cynefin_domain": cynefin_domain,
        "note": "Offline AAR — structured reflection without live LLM.",
    }


def double_loop_notes(
    *,
    aar: dict[str, Any],
    issues: list[str],
) -> dict[str, Any]:
    """Ask meta questions after single-loop AAR (offline stubs)."""
    governing = [
        "Are success criteria / L2 thresholds calibrated for this agent role?",
        "Is the tool allowlist too narrow or too broad for the goal?",
        "Should Cynefin routing prefer full deliberative mode for this class of goal?",
    ]
    recommend_change = bool(issues)
    return {
        "single_loop_lessons": list(aar.get("what_next") or [])[:4],
        "governing_variable_questions": governing,
        "recommend_meta_change": recommend_change,
        "proposed_meta_edits": (
            [
                "Raise reflection depth for similar goals",
                "Add red_team critic mode by default for complex domain",
            ]
            if recommend_change
            else ["No meta change required this run"]
        ),
        "note": "Double-loop scaffold only — does not auto-mutate pack prompts.",
    }
