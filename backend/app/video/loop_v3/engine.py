"""Offline agent-loop v3 envelope: Cynefin + Premortem + multi-step + AAR.

Wraps (does not replace) the pack Plan→Act→Self-Review harness with bounded
cognitive scaffolding from agent_loop_v3.md.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any, Callable

from app.video.loop_v3.aar import build_aar, double_loop_notes
from app.video.loop_v3.critics import ensemble_verify
from app.video.loop_v3.cynefin import classify_cynefin
from app.video.loop_v3.pattern_store import PatternStore
from app.video.loop_v3.premortem import run_premortem

# Shared process-local pattern store for RPD
_PATTERN_STORE = PatternStore()


def get_pattern_store() -> PatternStore:
    return _PATTERN_STORE


def reset_pattern_store_for_tests() -> PatternStore:
    global _PATTERN_STORE
    _PATTERN_STORE = PatternStore()
    return _PATTERN_STORE


def _action_digest(parts: dict[str, Any]) -> str:
    raw = "|".join(f"{k}={parts.get(k)}" for k in sorted(parts))
    return sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:24]


def run_v3_envelope(
    *,
    agent_id: str,
    goal: str,
    max_steps: int = 3,
    enable_fast_path: bool = True,
    critic_modes: list[str] | None = None,
    cynefin_override: str | None = None,
    run_core: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Execute Phase 0 cognitive setup + bounded steps around core pack run.

    ``run_core`` must perform the offline pack Plan→Act→Self-Review and return
    a dict with keys: ok, status, needs_hitl, l1, l2, tool_invocations,
    artifact_summary, phases, critiques_emitted (as available).
    """
    max_steps = max(1, min(int(max_steps), 8))
    modes = critic_modes or ["standard"]
    cynefin = classify_cynefin(goal, override=cynefin_override)
    domain = str(cynefin.get("domain") or "complicated")

    premortem = run_premortem(goal, agent_id=agent_id, cynefin_domain=domain)
    pattern_hit = _PATTERN_STORE.match(goal, agent_id=agent_id)
    prefer_fast = bool(enable_fast_path and cynefin.get("enable_fast_path") and pattern_hit)
    operating_mode = "fast" if prefer_fast else str(cynefin.get("mode") or "full")

    steps: list[dict[str, Any]] = []
    digests: list[str] = []
    cycle_detected = False
    core_result: dict[str, Any] = {}
    early_exit = False

    # Step 1: plan / premortem (always)
    plan_digest = _action_digest(
        {"phase": "plan", "domain": domain, "mode": operating_mode, "goal": goal[:120]}
    )
    digests.append(plan_digest)
    steps.append(
        {
            "step": 1,
            "phase": "plan",
            "thought": (
                f"Cynefin={domain}; mode={operating_mode}; "
                f"premortem_risks={len(premortem.get('risks') or [])}"
            ),
            "action": "commit_living_plan_scaffold",
            "observation": {
                "cynefin": cynefin,
                "premortem_todos": premortem.get("todo_items"),
                "pattern_match": pattern_hit,
            },
            "digest": plan_digest,
        }
    )

    # Fast path: single core act if pattern match
    remaining = max_steps - 1
    if prefer_fast and remaining >= 1:
        core_result = run_core()
        act_digest = _action_digest(
            {
                "phase": "act_fast",
                "status": core_result.get("status"),
                "tools": len(core_result.get("tool_invocations") or []),
            }
        )
        if act_digest in digests:
            cycle_detected = True
        digests.append(act_digest)
        steps.append(
            {
                "step": 2,
                "phase": "act",
                "thought": "RPD fast path — similar successful pattern; minimal deliberation",
                "action": "pack_plan_act_self_review",
                "observation": {
                    "status": core_result.get("status"),
                    "ok": core_result.get("ok"),
                    "pattern_id": (pattern_hit or {}).get("pattern_id"),
                },
                "digest": act_digest,
                "path": "fast",
            }
        )
        early_exit = True
    else:
        # Full path: optional metacognition step then core
        step_n = 2
        if remaining >= 2 and operating_mode == "full":
            meta_digest = _action_digest({"phase": "metacognition", "domain": domain})
            digests.append(meta_digest)
            steps.append(
                {
                    "step": step_n,
                    "phase": "metacognition",
                    "thought": (
                        "Monitor: bias/progress; confirm Full deliberative mode; "
                        "align plan to premortem mitigations"
                    ),
                    "action": "metacognition_pulse",
                    "observation": {
                        "current_mode": operating_mode,
                        "mitigations_in_focus": (premortem.get("mitigations") or [])[:3],
                    },
                    "digest": meta_digest,
                }
            )
            step_n += 1
            remaining -= 1

        if remaining >= 1:
            core_result = run_core()
            act_digest = _action_digest(
                {
                    "phase": "act_full",
                    "status": core_result.get("status"),
                    "l2": (core_result.get("l2") or {}).get("pass"),
                    "tools": len(core_result.get("tool_invocations") or []),
                }
            )
            if digests.count(act_digest) >= 1:
                # Same act digest only if re-entered — mark thrash risk
                pass
            digests.append(act_digest)
            steps.append(
                {
                    "step": step_n,
                    "phase": "act",
                    "thought": "Full Plan→Act→Self-Review with Host tool registry",
                    "action": "pack_plan_act_self_review",
                    "observation": {
                        "status": core_result.get("status"),
                        "ok": core_result.get("ok"),
                        "needs_hitl": core_result.get("needs_hitl"),
                    },
                    "digest": act_digest,
                    "path": "full",
                }
            )
            step_n += 1

        # Optional replan step if failed and steps remain
        if (
            not core_result.get("ok")
            and step_n <= max_steps
            and int(cynefin.get("max_reflection_rounds") or 1) >= 1
        ):
            replan_digest = _action_digest(
                {
                    "phase": "replan",
                    "status": core_result.get("status"),
                    "issues": "retry_scaffold",
                }
            )
            if replan_digest in digests:
                cycle_detected = True
            else:
                digests.append(replan_digest)
                steps.append(
                    {
                        "step": step_n,
                        "phase": "replan",
                        "thought": "Reflect: loop incomplete — record replan without infinite thrash",
                        "action": "bounded_replan_note",
                        "observation": {
                            "cycle_detected": cycle_detected,
                            "hint": "Adjust goal constraints or accept HITL",
                        },
                        "digest": replan_digest,
                    }
                )

    if not core_result:
        core_result = {
            "ok": False,
            "status": "error",
            "needs_hitl": True,
            "l1": {},
            "l2": {},
            "tool_invocations": [],
            "artifact_summary": "",
        }

    critic = ensemble_verify(
        goal=goal,
        status=str(core_result.get("status") or "error"),
        l1=core_result.get("l1") if isinstance(core_result.get("l1"), dict) else {},
        l2=core_result.get("l2") if isinstance(core_result.get("l2"), dict) else {},
        needs_hitl=bool(core_result.get("needs_hitl")),
        tool_invocations=list(core_result.get("tool_invocations") or []),
        modes=modes if operating_mode == "full" else ["standard"],
    )

    issues = list(critic.get("issues") or [])
    if cycle_detected:
        issues.append("cycle_detected")

    aar = build_aar(
        goal=goal,
        plan_summary=(
            f"mode={operating_mode}; cynefin={domain}; "
            f"mitigations={len(premortem.get('mitigations') or [])}"
        ),
        actual_status=str(core_result.get("status") or "unknown"),
        observations=[str(s.get("phase")) for s in steps],
        issues=issues,
        cynefin_domain=domain,
    )
    dloop = double_loop_notes(aar=aar, issues=issues)

    outcome = "ok" if core_result.get("ok") and critic.get("pass") else "failed"
    quality = float(critic.get("score") or 0.0)
    recorded = _PATTERN_STORE.record(
        goal=goal,
        agent_id=agent_id,
        outcome=outcome,
        cynefin_domain=domain,
        mode=operating_mode,
        quality_score=quality,
        summary=str(core_result.get("artifact_summary") or core_result.get("status") or ""),
    )

    return {
        "v3_enabled": True,
        "cognitive_profile": {
            "enable_fast_path": enable_fast_path,
            "operating_mode": operating_mode,
            "cynefin": cynefin,
            "critic_modes": modes if operating_mode == "full" else ["standard"],
            "max_steps": max_steps,
            "reflection_style": "aar_double_loop_lite",
        },
        "phase0": {
            "cynefin": cynefin,
            "premortem": premortem,
            "pattern_match": pattern_hit,
        },
        "steps": steps,
        "step_count": len(steps),
        "cycle_detected": cycle_detected,
        "early_exit_fast_path": early_exit,
        "critic": critic,
        "aar": aar,
        "double_loop": dloop,
        "pattern_recorded": recorded,
        "patterns_used": [
            "ReAct_lite",
            "Cynefin",
            "Premortem",
            "AAR",
            "DoubleLoop_scaffold",
            "RPD_pattern_store",
            "MultiModeCritic",
        ],
        "note": (
            "Offline agent_loop_v3 Host foundation. Not full multi-step LLM ReAct, "
            "not TextGrad self-evolution, not live multi-agent orchestration."
        ),
        "core": core_result,
    }
