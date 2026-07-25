"""Focused TaskCoordinator lifecycle tests for backend-redesign task 7.3."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import UTC, datetime
from itertools import count
from typing import cast

from app.core.task_coordinator import TaskCoordinator, TaskTransitionCommand
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CommonPatternVersionId,
    GraphRevision,
    GraphRevisionId,
    GraphValidationCategory,
    GraphValidationCategoryResult,
    GraphValidationId,
    GraphValidationReport,
    RunProvenance,
    RunProvenanceId,
    SwarmInstance,
    SwarmInstanceId,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-task-coordinator")
_CORRELATION = CorrelationId("correlation-task-coordinator")
_RUN_REFERENCE = "run-focused"
_AGENT_VERSION_ID = AgentVersionId("agent-focused-v1")
_GRAPH_REVISION_ID = GraphRevisionId("graph-focused-v1")
_GATE_ID = ApprovalGateId("gate-focused")


def _metadata(record_id: str, *, version: int = 1) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=version,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _prepared_coordinator() -> tuple[
    InMemoryControlPlaneDatabase,
    TaskCoordinator,
    AgentTask,
    AgentTask,
    ApprovalGate,
]:
    database = InMemoryControlPlaneDatabase()
    graph_repository = InMemoryGraphRepository()
    swarm_id = SwarmInstanceId("swarm-focused")
    assert graph_repository.create_instance(
        SwarmInstance(metadata=_metadata("swarm-record"), swarm_instance_id=swarm_id)
    ).is_success

    nodes: tuple[Mapping[str, object], ...] = (
        {"id": "source", "agent_version_id": str(_AGENT_VERSION_ID)},
        {
            "id": "dependent",
            "agent_version_id": str(_AGENT_VERSION_ID),
            "dependencies": ["source"],
            "approval_gate_ids": [str(_GATE_ID)],
        },
    )
    revision = GraphRevision(
        metadata=_metadata("graph-record"),
        graph_revision_id=_GRAPH_REVISION_ID,
        swarm_instance_id=swarm_id,
        revision=1,
        nodes=nodes,
        edges=(),
        layout={},
        version_pins={"agent_version_ids": [str(_AGENT_VERSION_ID)]},
        policies={},
    )
    assert graph_repository.append_revision(revision, expected_revision=0).is_success
    report = GraphValidationReport(
        metadata=_metadata("validation-record"),
        graph_validation_id=GraphValidationId("validation-focused"),
        graph_revision_id=_GRAPH_REVISION_ID,
        categories=tuple(
            GraphValidationCategoryResult(category=category, passed=True)
            for category in GraphValidationCategory
        ),
        eligible_for_run=True,
        workflow_definition={"id": "workflow-focused"},
        workflow_definition_version="1.0.0",
        agent_version_ids=(_AGENT_VERSION_ID,),
    )
    assert graph_repository.append_validation(report).is_success

    gate = ApprovalGate(
        metadata=_metadata("gate-record"),
        approval_gate_id=_GATE_ID,
        pending_operation_reference="operation-focused",
        status=ApprovalGateStatus.PENDING,
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.append_approval(gate).is_success

    sequences = count(1)
    coordinator = TaskCoordinator(
        graph_repository,
        _unit_of_work_factory(database),
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(sequences),
    )
    prepared = coordinator.prepare_tasks(
        _ORGANIZATION,
        _CORRELATION,
        _GRAPH_REVISION_ID,
        _RUN_REFERENCE,
    )
    assert prepared.is_success and prepared.value is not None
    tasks = {str(task.task_id): task for task in prepared.value.tasks}
    return (
        database,
        coordinator,
        tasks[f"{_RUN_REFERENCE}:source"],
        tasks[f"{_RUN_REFERENCE}:dependent"],
        gate,
    )


def _read_task(database: InMemoryControlPlaneDatabase, task_id: TaskId) -> AgentTask:
    with database.unit_of_work() as unit_of_work:
        result = unit_of_work.tasks.get(_ORGANIZATION, task_id)
    assert result.is_success and result.value is not None
    return result.value


def test_task_lifecycle_contains_exactly_the_required_states() -> None:
    """The lifecycle enum neither omits required states nor admits extra states."""
    assert tuple(state.value for state in TaskLifecycle) == (
        "idle",
        "queued",
        "running",
        "self_refine",
        "waiting_for_critique",
        "blocked",
        "failed",
        "complete",
    )


def test_stale_transition_returns_conflict_without_mutation_or_evidence() -> None:
    """A stale expected version cannot alter a task or append transition evidence."""
    database, coordinator, source, _, _ = _prepared_coordinator()
    before_history = tuple(database._state.task_transitions[source.task_id])
    before_counts = (
        len(database._state.audits),
        len(database._state.events),
        len(database._state.outbox),
    )

    stale = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        source.metadata.version - 1,
    )

    assert not stale.is_success
    assert stale.error is not None and stale.error.code is ErrorCode.CONFLICT
    assert _read_task(database, source.task_id) == source
    assert tuple(database._state.task_transitions[source.task_id]) == before_history
    assert (
        len(database._state.audits),
        len(database._state.events),
        len(database._state.outbox),
    ) == before_counts


def test_dependent_queues_only_after_dependency_and_gate_are_satisfied() -> None:
    """Completing one prerequisite cannot queue a task until its pending gate is approved."""
    database, coordinator, source, dependent, gate = _prepared_coordinator()
    claimed = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        source.metadata.version,
    )
    assert claimed.is_success and claimed.value is not None
    completed = coordinator.transition(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        claimed.value.task.metadata.version,
        TaskTransitionCommand(TaskLifecycle.COMPLETE, "source_complete"),
    )
    assert completed.is_success and completed.value is not None
    assert _read_task(database, dependent.task_id).state is TaskLifecycle.IDLE

    approved_gate = replace(
        gate,
        metadata=replace(gate.metadata, version=2, updated_at=_NOW),
        status=ApprovalGateStatus.APPROVED,
        decision="approved",
        decision_reason="focused-test",
        reviewer_reference="operator",
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.replace_approval(approved_gate).is_success
    queued = coordinator.queue_satisfied(_ORGANIZATION, _CORRELATION, _RUN_REFERENCE)

    assert queued.is_success and queued.value is not None and len(queued.value) == 1
    current = _read_task(database, dependent.task_id)
    assert current.state is TaskLifecycle.QUEUED
    history = tuple(database._state.task_transitions[dependent.task_id])
    assert len(history) == 1
    assert history[0].from_state is TaskLifecycle.IDLE
    assert history[0].to_state is TaskLifecycle.QUEUED
    assert history[0].expected_task_version == dependent.metadata.version
    publication = queued.value[0]
    assert database._state.events[publication.event.event_id] == publication.event
    assert database._state.outbox[publication.outbox.outbox_id] == publication.outbox
    assert any(
        audit.action == "task.transitioned"
        and audit.subject_reference == f"task:{dependent.task_id}"
        and audit.outcome == "queued"
        for audit in database._state.audits.values()
    )


def test_replay_creates_distinct_complete_immutable_lineage() -> None:
    """Replay provenance pins its source graph, checkpoint, artifacts, and common versions."""
    database, coordinator, _, _, _ = _prepared_coordinator()
    source = RunProvenance(
        metadata=_metadata("source-provenance-record"),
        run_provenance_id=RunProvenanceId("source-provenance"),
        graph_revision_id=_GRAPH_REVISION_ID,
        workflow_definition={"id": "workflow-focused", "steps": ("source", "dependent")},
        workflow_definition_version="1.0.0",
        agent_version_ids=(_AGENT_VERSION_ID,),
        pattern_version_ids=(CommonPatternVersionId("pattern-focused-v1"),),
        source_checkpoint_reference="original-checkpoint",
        artifact_version_references=("artifact-original-v1",),
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.provenance.append(source).is_success

    replay = coordinator.create_replay_lineage(
        _ORGANIZATION,
        _CORRELATION,
        source.run_provenance_id,
        "replay-checkpoint",
        ("artifact-replay-v2",),
    )

    assert replay.is_success and replay.value is not None
    lineage = replay.value
    assert lineage.run_provenance_id != source.run_provenance_id
    assert lineage.source_run_provenance_id == source.run_provenance_id
    assert lineage.graph_revision_id == source.graph_revision_id
    assert lineage.workflow_definition == source.workflow_definition
    assert lineage.workflow_definition_version == source.workflow_definition_version
    assert lineage.agent_version_ids == source.agent_version_ids
    assert lineage.pattern_version_ids == source.pattern_version_ids
    assert lineage.source_checkpoint_reference == "replay-checkpoint"
    assert lineage.artifact_version_references == ("artifact-replay-v2",)
    with database.unit_of_work() as unit_of_work:
        stored = unit_of_work.provenance.get(_ORGANIZATION, lineage.run_provenance_id)
        original = unit_of_work.provenance.get(_ORGANIZATION, source.run_provenance_id)
    assert stored.is_success and stored.value == lineage
    assert original.is_success and original.value == source
    replay_events = [
        event
        for event in database._state.events.values()
        if event.event_type == "task.replay.lineage.created"
    ]
    assert len(replay_events) == 1
    assert replay_events[0].redacted_payload["source_provenance_id"] == str(
        source.run_provenance_id
    )


def test_queued_task_that_loses_eligibility_remains_queued_and_unclaimable() -> None:
    """Lost execution eligibility is a claim marker, not a parallel lifecycle state."""
    database, coordinator, source, _, _ = _prepared_coordinator()

    changed = coordinator.set_execution_eligibility(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        source.metadata.version,
        False,
    )

    assert changed.is_success and changed.value is not None
    queued_but_ineligible = changed.value.task
    assert queued_but_ineligible.state is TaskLifecycle.QUEUED
    assert queued_but_ineligible.ineligible_for_execution
    claimable = coordinator.is_claimable(_ORGANIZATION, source.task_id, _CORRELATION)
    assert claimable.is_success and claimable.value is False
    history_before_claim = tuple(database._state.task_transitions[source.task_id])

    claim = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        queued_but_ineligible.metadata.version,
    )

    assert not claim.is_success
    assert claim.error is not None and claim.error.code is ErrorCode.INVALID_TRANSITION
    assert _read_task(database, source.task_id) == queued_but_ineligible
    assert tuple(database._state.task_transitions[source.task_id]) == history_before_claim
