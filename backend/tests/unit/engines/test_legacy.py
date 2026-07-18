"""Focused deterministic examples for bounded LegacyEngine terminal behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.engines.legacy import (
    AmbiguousEffectError,
    LegacyEngine,
    LegacyStep,
    LegacyStepResult,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.redaction import REDACTED
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-legacy")
CORRELATION_ID = CorrelationId("corr-legacy")


def _definition() -> dict[str, object]:
    return {
        "definition_type": "workflow_dna",
        "id": "ops.legacy",
        "version": "1.0.0",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 2,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "steps": [
            {"id": "step-1", "agent_id": "ops.planner", "tool_ids": ["crm.lookup"]},
            {"id": "step-2", "agent_id": "ops.reviewer", "tool_ids": ["crm.lookup"]},
        ],
    }


def _run(definition: dict[str, object], output: dict[str, object] | None = None) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-legacy"),
            organization_id=ORG_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RunId("run-legacy"),
        workflow_definition_id=WorkflowDefinitionId("ops.legacy"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=LegacyEngine._definition_digest(definition),
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
        output=output,
    )


def _effect(step_id: str) -> ToolEffect:
    return ToolEffect(
        adapter_id="crm.lookup",
        request_digest=f"request-{step_id}",
        outcome="completed",
        effect_digest=f"effect-{step_id}",
        completed_at=NOW,
        reversible=True,
    )


@dataclass
class _RecordingExecutor:
    """Host-owned step fake that returns only predeclared local effects."""

    effects_by_step: dict[str, tuple[ToolEffect, ...]]
    calls: list[str] = field(default_factory=list)

    def execute(self, _run: RunRecord, step: LegacyStep) -> LegacyStepResult:
        self.calls.append(step.step_id)
        return LegacyStepResult(self.effects_by_step.get(step.step_id, ()))


@dataclass
class _AmbiguousExecutor:
    """Host-owned fake that exposes one uncertain step without replaying it."""

    effect: ToolEffect
    calls: list[str] = field(default_factory=list)

    def execute(self, _run: RunRecord, step: LegacyStep) -> LegacyStepResult:
        self.calls.append(step.step_id)
        if step.step_id == "step-1":
            raise AmbiguousEffectError(effects=(self.effect,))
        return LegacyStepResult()


def test_invalid_definition_terminalizes_without_starting_a_step() -> None:
    """An invalid active definition is failed safely before the executor is invoked."""
    definition = _definition()
    repository = InMemoryRunRepository()
    run = _run(definition, {"authorization": "secret", "summary": "pending"})
    assert repository.create(run).is_success
    executor = _RecordingExecutor({})
    invalid_definition = {**definition, "version": "2.0.0"}

    outcome = LegacyEngine(repository, executor).execute(
        ORG_ID, RunId("run-legacy"), invalid_definition, CORRELATION_ID
    )

    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.completed
    assert executor.calls == []
    record = outcome.value.record
    assert record.status is RunStatus.FAILED
    assert record.failure is not None
    assert record.failure.code == "invalid_legacy_definition"
    assert record.failure.stopped_step_ids == ("step-1", "step-2")
    assert record.failure.failure_processing_complete
    projection = record.to_projection()
    assert projection.status is RunStatus.FAILED
    assert projection.failure_code == "invalid_legacy_definition"
    assert projection.output == {"authorization": REDACTED, "summary": "pending"}


def test_successful_terminal_projection_redacts_output_and_retains_effects() -> None:
    """A completed run preserves durable effects while exposing only a safe projection."""
    definition = _definition()
    repository = InMemoryRunRepository()
    run = _run(definition, {"api_token": "secret", "summary": "done"})
    assert repository.create(run).is_success
    effects = (_effect("step-1"), _effect("step-2"))
    executor = _RecordingExecutor(
        {"step-1": (effects[0],), "step-2": (effects[1],)}
    )

    outcome = LegacyEngine(repository, executor).execute(
        ORG_ID, RunId("run-legacy"), definition, CORRELATION_ID
    )

    assert outcome.is_success and outcome.value is not None
    assert outcome.value.completed
    assert executor.calls == ["step-1", "step-2"]
    assert outcome.value.record.status is RunStatus.COMPLETED
    assert outcome.value.record.tool_effects == effects
    projection = outcome.value.record.to_projection()
    assert projection.status is RunStatus.COMPLETED
    assert projection.failure_code is None
    assert projection.output == {"api_token": REDACTED, "summary": "done"}


def test_ambiguous_effect_is_retained_without_replaying_its_step() -> None:
    """Ambiguous work is terminalized with evidence and never retried by LegacyEngine."""
    definition = _definition()
    repository = InMemoryRunRepository()
    assert repository.create(_run(definition)).is_success
    effect = _effect("step-1")
    executor = _AmbiguousExecutor(effect)
    engine = LegacyEngine(repository, executor)

    first = engine.execute(ORG_ID, RunId("run-legacy"), definition, CORRELATION_ID)
    second = engine.execute(ORG_ID, RunId("run-legacy"), definition, CORRELATION_ID)

    assert first.is_success and first.value is not None
    assert not first.value.completed
    assert first.value.record.status is RunStatus.FAILED
    assert first.value.record.tool_effects == (effect,)
    assert first.value.record.failure is not None
    assert first.value.record.failure.code == "ambiguous_effect"
    assert first.value.record.failure.stopped_step_ids == ("step-2",)
    assert first.value.record.failure.failure_processing_complete
    assert not second.is_success
    assert second.error is not None
    assert second.error.code is ErrorCode.INVALID_TRANSITION
    assert executor.calls == ["step-1"]
