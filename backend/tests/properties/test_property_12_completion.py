"""Property tests for successful workflow completion effect retention."""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

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
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences

# Feature: generic-swarm-business-os, Property 12: Successful execution preserves effects at
# completion.
# **Validates: Requirements 4.9**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-12")
_CORRELATION_ID = CorrelationId("corr-property-12")
_REGISTERED_REFERENCES = RegisteredReferences(
    agent_ids=frozenset(),
    tool_ids=frozenset(),
    memory_scope_ids=frozenset(),
    risk_gate_ids=frozenset(),
    rollback_plan_ids=frozenset(),
    authorization_ids=frozenset(),
)


def _effect(effect_id: int) -> ToolEffect:
    """Build one deterministic completed effect without invoking an adapter."""
    return ToolEffect(
        adapter_id=f"local.adapter-{effect_id}",
        request_digest=f"request-{effect_id}",
        outcome="completed",
        effect_digest=f"effect-{effect_id}",
        completed_at=_NOW,
        reversible=True,
    )


@settings(max_examples=100, deadline=None, derandomize=True)
@example(effect_ids=[])
@example(effect_ids=[0])
@example(effect_ids=[0, 9, 1])
@given(effect_ids=st.lists(st.integers(min_value=0, max_value=9), min_size=0, max_size=10))
def test_successful_completion_preserves_every_completed_effect(effect_ids: list[int]) -> None:
    """Normal terminalization retains the ordered complete local effect sequence."""
    effects = tuple(_effect(effect_id) for effect_id in effect_ids)
    repository = InMemoryRunRepository()
    run = RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-property-12"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=_CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        run_id=RunId("run-property-12"),
        workflow_definition_id=WorkflowDefinitionId("workflow-property-12"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="workflow-digest-property-12",
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=_NOW,
        tool_effects=effects,
    )
    assert repository.create(run).is_success

    service = RunService(repository, _REGISTERED_REFERENCES, clock=lambda: _NOW)
    completed = service.transition_status(
        _ORGANIZATION_ID,
        run.run_id,
        RunStatus.DISPATCHING,
        RunStatus.COMPLETED,
        _CORRELATION_ID,
    )

    assert completed.is_success and completed.value is not None
    assert completed.value.status is RunStatus.COMPLETED
    assert completed.value.failure is None
    assert completed.value.tool_effects == effects
    stored = repository.get_by_run_id(_ORGANIZATION_ID, run.run_id)
    assert stored.is_success and stored.value == completed.value
    assert stored.value.tool_effects == effects
