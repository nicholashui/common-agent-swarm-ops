"""Unit tests for video pack agent runtime (loader, critique bus, golden spine)."""

from __future__ import annotations

import pytest

from app.video.pack_runtime.critique import CritiqueBus, CritiqueSeverity
from app.video.pack_runtime.golden import PackGoldenRunner
from app.video.pack_runtime.loader import PackAgentLoader
from app.video.pack_runtime.paths import SPINE_AGENT_IDS
from app.video.pack_runtime.runner import PackAgentRunner


def test_loader_loads_orchestrator_prompt_rubric_skill() -> None:
    bundle = PackAgentLoader().load("video.orchestrator")
    assert bundle.agent_id == "video.orchestrator"
    assert "Responsibility" in bundle.prompt_text
    assert bundle.rubric.get("pass_threshold") == 85 or (
        (bundle.rubric.get("layers") or {}).get("L2_rubric") or {}
    ).get("pass_threshold") == 85
    assert "video.orchestrator" in bundle.skill_markdown
    assert bundle.has_distillation_plan
    assert bundle.has_source_catalog
    assert "video.critic" in bundle.critique_edges["inputs"]


def test_critique_bus_enforces_edges_and_hitl_blocker() -> None:
    bus = CritiqueBus()
    msg = bus.send(
        correlation_id="c1",
        from_id="video.orchestrator",
        to_id="video.judge",
        severity=CritiqueSeverity.BLOCKER,
        claim="stall",
        allowed_outputs=("video.judge",),
    )
    assert msg.requires_hitl is True
    received = bus.receive(
        correlation_id="c1",
        to_id="video.judge",
        allowed_inputs=("video.orchestrator",),
    )
    assert len(received) == 1

    with pytest.raises(PermissionError):
        bus.send(
            correlation_id="c1",
            from_id="video.orchestrator",
            to_id="video.editor",
            severity="minor",
            claim="nope",
            allowed_outputs=("video.judge",),
        )

    with pytest.raises(PermissionError):
        bus.resolve_dispute(
            correlation_id="c1",
            judge_id="video.judge",
            target_message_id=msg.message_id,
            resolution="fixed",
            confirm_hitl=False,
        )

    resolution = bus.resolve_dispute(
        correlation_id="c1",
        judge_id="video.judge",
        target_message_id=msg.message_id,
        resolution="fixed with human confirm",
        confirm_hitl=True,
    )
    assert resolution.kind == "resolution"
    assert bus.unresolved_blockers("c1") == ()


def test_offline_runner_spine_agent_ok() -> None:
    runner = PackAgentRunner()
    result = runner.run(
        "video.planner",
        goal="Plan offline synthetic DAG step",
        constraints={"network": False, "production": False},
        emit_self_critique_to="video.judge",
    )
    assert result.l1["passed"] is True
    assert result.skill_loaded is True
    assert result.status in {"ok", "needs_refine", "needs_hitl"}
    assert result.artifact.get("summary")
    assert result.prompt_reference.startswith("video.prompt.")


def test_offline_runner_fail_closed_on_network_constraint() -> None:
    result = PackAgentRunner().run(
        "video.memory",
        goal="should fail closed",
        constraints={"network": True},
    )
    assert result.status == "failed"
    assert result.l1["passed"] is False


def test_golden_spine_suite_passes() -> None:
    suite = PackGoldenRunner().run_spine()
    assert suite.total == len(SPINE_AGENT_IDS)
    assert suite.failed == 0, {
        r.agent_id: r.errors for r in suite.results if not r.passed
    }
    assert suite.passed == suite.total


def test_refine_loop_increments_when_forced_l2_fail() -> None:
    result = PackAgentRunner().run(
        "video.critic",
        goal="force refine path",
        force_l2_fail_once=True,
        constraints={"network": False, "production": False},
    )
    assert result.refinement_count >= 1
    assert result.l1["passed"] is True


def test_human_baseline_protocol_and_synthetic_gate_never_claims_met() -> None:
    from app.video.pack_runtime.baseline import HumanBaselineService, build_protocol

    svc = HumanBaselineService()
    try:
        svc.load("video.orchestrator")
    except FileNotFoundError:
        svc.save(
            build_protocol(
                "video.orchestrator",
                surpass_signal="Lower TTD than human EP at same scope",
                va_name="OrchestratorAgent",
            )
        )

    for i in range(5):
        svc.record_human_trial(
            "video.orchestrator",
            score=70 + i,
            rater_id="synthetic_ci",
            synthetic=True,
            notes="ci only",
        )
    svc.measure_agent_offline("video.orchestrator", trials=5)
    gate = svc.evaluate_gate("video.orchestrator")
    assert gate.met is False  # synthetic must never claim surpass
    assert gate.status in {"synthetic_checked", "incomplete", "not_met", "met"}
    if gate.status == "synthetic_checked":
        assert gate.met is False

    # Clear synthetic so real raters can start clean
    cleared = svc.clear_human_trials("video.orchestrator", only_synthetic=True)
    assert (cleared.get("human_baseline") or {}).get("status") == "pending"
    assert (cleared.get("gate") or {}).get("met") is False
