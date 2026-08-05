"""Multi-mode offline critics (standard | red_team | paul_elder | six_hats)."""

from __future__ import annotations

from typing import Any, Literal

CriticMode = Literal["standard", "red_team", "paul_elder", "six_hats"]


def verify_output(
    *,
    goal: str,
    status: str,
    l1: dict[str, Any] | None,
    l2: dict[str, Any] | None,
    needs_hitl: bool,
    tool_invocations: list[dict[str, Any]] | None,
    critic_mode: CriticMode = "standard",
) -> dict[str, Any]:
    """Return pass/fail + issues + suggestions (deterministic).

    Only ``blockers`` fail the critic. Mode-specific notes land in ``warnings``.
    """
    blockers: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []
    l1 = l1 or {}
    l2 = l2 or {}
    tools = tool_invocations or []

    ok_status = status == "ok"
    # L1/L2 dicts may use different keys; missing → do not invent fail
    l1_fail = l1.get("pass") is False or l1.get("ok") is False
    l2_fail = l2.get("pass") is False or l2.get("ok") is False
    if not ok_status and status not in {"", "ok"}:
        # only hard-fail when status is an explicit failure class
        if status in {"failed", "error", "denied"}:
            blockers.append(f"status_not_ok:{status}")
        else:
            warnings.append(f"status_non_ok:{status}")
    if l1_fail:
        blockers.append("l1_failed")
    if l2_fail:
        blockers.append("l2_failed")
    if needs_hitl and status != "ok":
        blockers.append("needs_hitl")
    elif needs_hitl:
        warnings.append("needs_hitl_flag")
    if not tools:
        warnings.append("no_tool_act_recorded")
        suggestions.append("Ensure Host tool registry Act phase runs for evidence")

    if critic_mode == "red_team":
        warnings.extend(_red_team(goal, tools))
        suggestions.append("Adversarially re-check single points of failure before ship")
    elif critic_mode == "paul_elder":
        warnings.extend(_paul_elder(goal, status))
        suggestions.append("Check clarity, accuracy, relevance, sufficiency vs goal")
    elif critic_mode == "six_hats":
        warnings.extend(_six_hats(goal, blockers + warnings))
        suggestions.append("Black-hat risk pass + White-hat evidence completeness")
    else:
        if not goal.strip():
            blockers.append("empty_goal")
        suggestions.append("Standard verifier: L1/L2 + status gates")

    blockers = list(dict.fromkeys(blockers))
    warnings = list(dict.fromkeys(warnings))
    passed = len(blockers) == 0
    score = 1.0 if passed else max(0.0, 1.0 - 0.2 * len(blockers))
    if warnings and passed:
        score = max(0.55, score - 0.03 * len(warnings))
    return {
        "critic_mode": critic_mode,
        "pass": passed,
        "issues": blockers,  # blockers only (backward-compatible key)
        "blockers": blockers,
        "warnings": warnings,
        "suggestions": suggestions[:6],
        "score": round(score, 4),
    }


def ensemble_verify(
    *,
    goal: str,
    status: str,
    l1: dict[str, Any] | None,
    l2: dict[str, Any] | None,
    needs_hitl: bool,
    tool_invocations: list[dict[str, Any]] | None,
    modes: list[str] | None = None,
) -> dict[str, Any]:
    modes_in = modes or ["standard"]
    valid: list[CriticMode] = []
    for m in modes_in:
        mm = str(m).strip().lower()
        if mm in {"standard", "red_team", "paul_elder", "six_hats"}:
            valid.append(mm)  # type: ignore[arg-type]
    if not valid:
        valid = ["standard"]

    results = [
        verify_output(
            goal=goal,
            status=status,
            l1=l1,
            l2=l2,
            needs_hitl=needs_hitl,
            tool_invocations=tool_invocations,
            critic_mode=mode,
        )
        for mode in valid
    ]
    all_blockers: list[str] = []
    all_warnings: list[str] = []
    for r in results:
        all_blockers.extend(r.get("blockers") or r.get("issues") or [])
        all_warnings.extend(r.get("warnings") or [])
    all_blockers = list(dict.fromkeys(all_blockers))
    all_warnings = list(dict.fromkeys(all_warnings))
    avg = sum(float(r.get("score") or 0) for r in results) / max(1, len(results))
    return {
        "modes": valid,
        "results": results,
        "pass": len(all_blockers) == 0,
        "issues": all_blockers,
        "blockers": all_blockers,
        "warnings": all_warnings,
        "score": round(avg, 4),
        "note": "Offline critic ensemble — not live LLM judges.",
    }


def _red_team(goal: str, tools: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    g = goal.lower()
    if "production" in g or "live" in g:
        issues.append("red_team:goal_may_assume_production_activation")
    live_tools = [t for t in tools if t.get("mode") == "live_blocked"]
    if live_tools:
        issues.append("red_team:live_media_tools_blocked_as_expected")
    if len(tools) == 1 and tools[0].get("tool_id") == "media.stub":
        issues.append("red_team:single_stub_tool_may_hide_missing_allowlist")
    return issues


def _paul_elder(goal: str, status: str) -> list[str]:
    issues: list[str] = []
    if len(goal.strip()) < 12:
        issues.append("paul_elder:goal_lacks_clarity_or_depth")
    if status not in {"ok", "needs_review", "failed", "error"}:
        issues.append("paul_elder:status_label_unclear")
    return issues


def _six_hats(goal: str, existing: list[str]) -> list[str]:
    issues: list[str] = []
    if existing:
        issues.append("six_hats:black_hat_risks_present")
    if "creative" in goal.lower() or "ideation" in goal.lower():
        issues.append("six_hats:green_hat_ensure_alternatives_considered")
    return issues
