"""Focused deterministic examples for migration-gate retirement behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.engines.legacy import LegacyEngine, LegacyStep, LegacyStepResult
from app.engines.migration import LegacyEngineRetirement
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
    MigrationGate,
    MigrationGateEvidence,
)
from app.models.common import RecordMetadata
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-migration")
CORRELATION_ID = CorrelationId("migration-correlation")
HASH = "a" * 64


def _gates(*, failed_gate: MigrationGate | None = None) -> tuple[MigrationGateEvidence, ...]:
    return tuple(
        MigrationGateEvidence(
            gate=gate,
            passed=gate is not failed_gate,
            evidence_hashes=(HASH,),
        )
        for gate in MigrationGate
    )


def _retirement() -> LegacyEngineRetirement:
    return LegacyEngineRetirement(
        MigrationEvidenceService(InMemoryMigrationEvidenceRepository(), clock=lambda: NOW)
    )


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


def _run(definition: dict[str, object]) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-migration"),
            organization_id=ORGANIZATION_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RunId("run-migration"),
        workflow_definition_id=WorkflowDefinitionId("ops.legacy"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=LegacyEngine._definition_digest(definition),
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
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
class _RetiringExecutor:
    """Retires the shared registry while the first legacy step is active."""

    retirement: LegacyEngineRetirement
    calls: list[str] = field(default_factory=list)

    def execute(self, _run: RunRecord, step: LegacyStep) -> LegacyStepResult:
        self.calls.append(step.step_id)
        if step.step_id == "step-1":
            retirement = self.retirement.assess_and_retire(
                CORRELATION_ID, HASH, _gates()
            )
            assert retirement.is_success and retirement.value is not None
            assert retirement.value.retired_now
        return LegacyStepResult((_effect(step.step_id),))


def test_failed_or_missing_gate_keeps_legacy_engine_available() -> None:
    """Any current gate failure or omission blocks retirement without disabling legacy."""
    retirement = _retirement()

    failed = retirement.assess_and_retire(
        CORRELATION_ID, HASH, _gates(failed_gate=MigrationGate.FAIL_CLOSED_TOOL_ALLOWLIST)
    )
    missing = retirement.assess_and_retire(CORRELATION_ID, HASH, _gates()[:-1])

    assert failed.is_success and failed.value is not None
    assert not failed.value.assessment.is_satisfied
    assert failed.value.retirement_evidence is None
    assert missing.is_success and missing.value is not None
    assert not missing.value.assessment.is_satisfied
    assert retirement.is_available()


def test_retirement_disables_new_and_active_legacy_execution_with_evidence() -> None:
    """A passing assessment immediately blocks new starts and stops the next legacy step."""
    definition = _definition()
    repository = InMemoryRunRepository()
    assert repository.create(_run(definition)).is_success
    retirement = _retirement()
    executor = _RetiringExecutor(retirement)
    engine = LegacyEngine(
        repository,
        executor,
        legacy_execution_availability=retirement,
    )

    outcome = engine.execute(ORGANIZATION_ID, RunId("run-migration"), definition, CORRELATION_ID)
    new_execution = retirement.begin_legacy_execution(
        ORGANIZATION_ID, RunId("run-new"), CORRELATION_ID
    )

    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.completed
    assert outcome.value.record.status is RunStatus.FAILED
    assert outcome.value.record.failure is not None
    assert outcome.value.record.failure.code == "legacy_engine_retired"
    assert outcome.value.record.failure.failure_processing_complete
    assert outcome.value.record.tool_effects == (_effect("step-1"),)
    assert outcome.value.record.failure.evidence_references
    assert executor.calls == ["step-1"]
    assert not retirement.is_available()
    assert not new_execution.is_success
