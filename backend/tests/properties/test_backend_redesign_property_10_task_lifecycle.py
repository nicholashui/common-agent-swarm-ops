"""Property checks for pinned Agent_Task lifecycle coordination."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import UTC, datetime
from itertools import count
from typing import cast

from hypothesis import given, settings, strategies as st

from app.core.task_coordinator import TaskCoordinator, TaskPublication, TaskTransitionCommand
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CommonAgentVersion,
    ContractStatus,
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
    TaskTransition,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-10-organization")
_CORRELATION = CorrelationId("property-10-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_PREREQUISITES = st.sampled_from(
    (frozenset({"dependency"}), frozenset({"gate"}), frozenset({"dependency", "gate"}))
)


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


def _agent(value: str, retry_limit: int, iteration_limit: int) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record-{value}"),
        agent_version_id=AgentVersionId(f"agent-{value}"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=f"agent-{value}",
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("approval",),
        runtime_policy={"retry_limit": retry_limit, "iteration_limit": iteration_limit},
        tool_policy={},
        quality_rubric={},
        critique_relationships=(),
        knowledge_bindings=(),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={},
        content_digest=f"sha256:{value}",
    )


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _seed_graph(
    value: str,
    agent: CommonAgentVersion,
    prerequisites: frozenset[str],
) -> tuple[InMemoryGraphRepository, GraphRevisionId]:
    graph_repository = InMemoryGraphRepository()
    swarm_id = SwarmInstanceId(f"swarm-{value}")
    graph_id = GraphRevisionId(f"graph-{value}")
    assert graph_repository.create_instance(
        SwarmInstance(metadata=_metadata(f"swarm-record-{value}"), swarm_instance_id=swarm_id)
    ).is_success

    dependent: dict[str, object] = {
        "id": "dependent",
        "agent_version_id": str(agent.agent_version_id),
        "constraints": {"priority": "gated"},
        "checkpoint_reference": f"checkpoint-{value}",
    }
    if "dependency" in prerequisites:
        dependent["dependencies"] = ["source"]
    if "gate" in prerequisites:
        dependent["approval_gate_ids"] = [f"gate-{value}"]
    nodes: tuple[Mapping[str, object], ...] = (
        {
            "id": "source",
            "agent_version_id": str(agent.agent_version_id),
            "constraints": {"priority": "source"},
        },
        dependent,
        {"id": "retry", "agent_version_id": str(agent.agent_version_id)},
        {"id": "refine", "agent_version_id": str(agent.agent_version_id)},
    )
    revision = GraphRevision(
        metadata=_metadata(f"graph-record-{value}"),
        graph_revision_id=graph_id,
        swarm_instance_id=swarm_id,
        revision=1,
        nodes=nodes,
        edges=(),
        layout={},
        version_pins={"agent_version_ids": [str(agent.agent_version_id)]},
        policies={},
    )
    assert graph_repository.append_revision(revision, expected_revision=0).is_success
    report = GraphValidationReport(
        metadata=_metadata(f"validation-record-{value}"),
        graph_validation_id=GraphValidationId(f"validation-{value}"),
        graph_revision_id=graph_id,
        categories=tuple(
            GraphValidationCategoryResult(category=category, passed=True)
            for category in GraphValidationCategory
        ),
        eligible_for_run=True,
        workflow_definition={"id": f"workflow-{value}"},
        workflow_definition_version="1.0.0",
        agent_version_ids=(agent.agent_version_id,),
    )
    assert graph_repository.append_validation(report).is_success
    return graph_repository, graph_id


def _gate(value: str, approved: bool) -> ApprovalGate:
    if approved:
        return ApprovalGate(
            metadata=_metadata(f"gate-record-{value}"),
            approval_gate_id=ApprovalGateId(f"gate-{value}"),
            pending_operation_reference=f"operation-{value}",
            status=ApprovalGateStatus.APPROVED,
            decision="approved",
            decision_reason="property-test",
            reviewer_reference="operator",
        )
    return ApprovalGate(
        metadata=_metadata(f"gate-record-{value}"),
        approval_gate_id=ApprovalGateId(f"gate-{value}"),
        pending_operation_reference=f"operation-{value}",
        status=ApprovalGateStatus.PENDING,
    )


def _read_task(database: InMemoryControlPlaneDatabase, task_id: TaskId) -> AgentTask:
    with database.unit_of_work() as unit_of_work:
        result = unit_of_work.tasks.get(_ORGANIZATION, task_id)
    assert result.is_success and result.value is not None
    return result.value


def _history(database: InMemoryControlPlaneDatabase, task_id: TaskId) -> tuple[TaskTransition, ...]:
    with database.unit_of_work() as unit_of_work:
        result = unit_of_work.tasks.transitions(_ORGANIZATION, task_id)
    assert result.is_success and result.value is not None
    return result.value


def _assert_claimable(coordinator: TaskCoordinator, task_id: TaskId, expected: bool) -> None:
    result = coordinator.is_claimable(_ORGANIZATION, task_id, _CORRELATION)
    assert result.is_success and result.value is expected


def _assert_publications_committed(
    database: InMemoryControlPlaneDatabase, publications: list[TaskPublication]
) -> None:
    state = database._state
    assert len(state.audits) == len(state.events) == len(state.outbox)
    assert tuple(sorted(state.event_sequences)) == tuple(range(1, len(state.events) + 1))
    for publication in publications:
        assert state.events[publication.event.event_id] == publication.event
        assert state.outbox[publication.outbox.outbox_id] == publication.outbox
        assert publication.outbox.event_id == publication.event.event_id
        assert any(
            audit.subject_reference == publication.event.subject_reference
            for audit in state.audits.values()
        )


def _approve_pending_gate(database: InMemoryControlPlaneDatabase, gate: ApprovalGate) -> None:
    approved = replace(
        gate,
        metadata=replace(gate.metadata, version=gate.metadata.version + 1, updated_at=_NOW),
        status=ApprovalGateStatus.APPROVED,
        decision="approved",
        decision_reason="property-test",
        reviewer_reference="operator",
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.replace_approval(approved).is_success


# Feature: backend-redesign, Property 10
# **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    prerequisites=_PREREQUISITES,
    gate_approved=st.booleans(),
    use_stale_expected_version=st.booleans(),
    retry_limit=st.integers(min_value=-3, max_value=3),
    iteration_limit=st.integers(min_value=-3, max_value=3),
    unlimited_operations=st.integers(min_value=1, max_value=4),
)
def test_property_10_task_lifecycle_honors_pins_prerequisites_versions_and_limits(
    value: str,
    prerequisites: frozenset[str],
    gate_approved: bool,
    use_stale_expected_version: bool,
    retry_limit: int,
    iteration_limit: int,
    unlimited_operations: int,
) -> None:
    """Pinned tasks queue, transition, recover, replay, and lose claimability exactly."""
    database = InMemoryControlPlaneDatabase()
    agent = _agent(value, retry_limit, iteration_limit)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(agent).is_success

    graph_repository, graph_id = _seed_graph(value, agent, prerequisites)
    gate = _gate(value, gate_approved)
    if "gate" in prerequisites:
        with database.unit_of_work() as unit_of_work:
            assert unit_of_work.evidence.append_approval(gate).is_success

    sequences = count(1)
    coordinator = TaskCoordinator(
        graph_repository,
        _unit_of_work_factory(database),
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(sequences),
    )
    publications: list[TaskPublication] = []
    run_reference = f"run-{value}"
    prepared = coordinator.prepare_tasks(
        _ORGANIZATION,
        _CORRELATION,
        graph_id,
        run_reference,
        publish=publications.append,
    )
    assert prepared.is_success and prepared.value is not None
    tasks = {str(task.task_id): task for task in prepared.value.tasks}
    source = tasks[f"{run_reference}:source"]
    dependent = tasks[f"{run_reference}:dependent"]
    retry_task = tasks[f"{run_reference}:retry"]
    refine_task = tasks[f"{run_reference}:refine"]

    assert all(task.state in TaskLifecycle for task in prepared.value.tasks)
    assert source.pinned_agent_version_id == agent.agent_version_id
    assert dependent.pinned_agent_version_id == agent.agent_version_id
    assert dependent.constraints == {"priority": "gated"}
    assert dependent.checkpoint_reference == f"checkpoint-{value}"
    assert dependent.dependencies == (
        (TaskId(f"{run_reference}:source"),) if "dependency" in prerequisites else ()
    )
    assert dependent.approval_gate_ids == (
        (ApprovalGateId(f"gate-{value}"),) if "gate" in prerequisites else ()
    )
    initially_satisfied = "dependency" not in prerequisites and (
        "gate" not in prerequisites or gate_approved
    )
    assert dependent.state is (TaskLifecycle.QUEUED if initially_satisfied else TaskLifecycle.IDLE)
    _assert_claimable(coordinator, source.task_id, True)
    _assert_claimable(coordinator, retry_task.task_id, True)
    _assert_claimable(coordinator, refine_task.task_id, True)
    _assert_claimable(coordinator, dependent.task_id, initially_satisfied)

    expected_version = source.metadata.version - int(use_stale_expected_version)
    attempted_claim = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        expected_version,
        publish=publications.append,
    )
    if use_stale_expected_version:
        assert not attempted_claim.is_success
        assert attempted_claim.error is not None
        assert attempted_claim.error.code is ErrorCode.CONFLICT
        source = _read_task(database, source.task_id)
        claimed_source = coordinator.claim_task(
            _ORGANIZATION,
            _CORRELATION,
            source.task_id,
            source.metadata.version,
            publish=publications.append,
        )
    else:
        claimed_source = attempted_claim
    assert claimed_source.is_success and claimed_source.value is not None
    source = claimed_source.value.task
    assert source.state is TaskLifecycle.RUNNING

    completed_source = coordinator.transition(
        _ORGANIZATION,
        _CORRELATION,
        source.task_id,
        source.metadata.version,
        TaskTransitionCommand(TaskLifecycle.COMPLETE, "source_complete"),
        publish=publications.append,
    )
    assert completed_source.is_success and completed_source.value is not None
    source = completed_source.value.task
    assert source.state is TaskLifecycle.COMPLETE

    dependent = _read_task(database, dependent.task_id)
    if "gate" in prerequisites and not gate_approved:
        assert dependent.state is TaskLifecycle.IDLE
        _assert_claimable(coordinator, dependent.task_id, False)
        _approve_pending_gate(database, gate)
        queued = coordinator.queue_satisfied(
            _ORGANIZATION,
            _CORRELATION,
            run_reference,
            publish=publications.append,
        )
        assert queued.is_success and queued.value is not None
        assert len(queued.value) == 1
        dependent = _read_task(database, dependent.task_id)
    assert dependent.state is TaskLifecycle.QUEUED
    _assert_claimable(coordinator, dependent.task_id, True)

    made_ineligible = coordinator.set_execution_eligibility(
        _ORGANIZATION,
        _CORRELATION,
        dependent.task_id,
        dependent.metadata.version,
        False,
        publish=publications.append,
    )
    assert made_ineligible.is_success and made_ineligible.value is not None
    dependent = made_ineligible.value.task
    assert dependent.state is TaskLifecycle.QUEUED
    assert dependent.ineligible_for_execution
    _assert_claimable(coordinator, dependent.task_id, False)
    rejected_claim = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        dependent.task_id,
        dependent.metadata.version,
        publish=publications.append,
    )
    assert not rejected_claim.is_success
    assert rejected_claim.error is not None
    assert rejected_claim.error.code is ErrorCode.INVALID_TRANSITION
    assert _read_task(database, dependent.task_id) == dependent

    restored = coordinator.set_execution_eligibility(
        _ORGANIZATION,
        _CORRELATION,
        dependent.task_id,
        dependent.metadata.version,
        True,
        publish=publications.append,
    )
    assert restored.is_success and restored.value is not None
    dependent = restored.value.task
    assert dependent.state is TaskLifecycle.QUEUED
    assert not dependent.ineligible_for_execution
    _assert_claimable(coordinator, dependent.task_id, True)
    claimed_dependent = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        dependent.task_id,
        dependent.metadata.version,
        publish=publications.append,
    )
    assert claimed_dependent.is_success and claimed_dependent.value is not None
    failed_dependent = coordinator.transition(
        _ORGANIZATION,
        _CORRELATION,
        dependent.task_id,
        claimed_dependent.value.task.metadata.version,
        TaskTransitionCommand(
            TaskLifecycle.FAILED,
            "non_retryable_failure",
            failure_reason="non_retryable_failure",
        ),
        publish=publications.append,
    )
    assert failed_dependent.is_success and failed_dependent.value is not None
    dependent = failed_dependent.value.task
    assert dependent.state is TaskLifecycle.FAILED
    assert dependent.failure_reason == "non_retryable_failure"
    _assert_claimable(coordinator, dependent.task_id, False)

    claimed_retry = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        retry_task.task_id,
        retry_task.metadata.version,
        publish=publications.append,
    )
    assert claimed_retry.is_success and claimed_retry.value is not None
    retry_current = claimed_retry.value.task
    retry_attempts = retry_limit + 1 if retry_limit >= 0 else unlimited_operations
    for _ in range(retry_attempts):
        retried = coordinator.retry_task(
            _ORGANIZATION,
            _CORRELATION,
            retry_current.task_id,
            retry_current.metadata.version,
            "transient_failure",
            publish=publications.append,
        )
        assert retried.is_success and retried.value is not None
        retry_current = retried.value.task
        if retry_limit >= 0 and retry_current.state is TaskLifecycle.FAILED:
            assert retry_current.retry_count == retry_limit
            assert retry_current.failure_reason == "retry_limit_exhausted"
            _assert_claimable(coordinator, retry_current.task_id, False)
            break
        assert retry_current.state is TaskLifecycle.QUEUED
        assert retry_current.retry_count <= retry_attempts
        _assert_claimable(coordinator, retry_current.task_id, True)
        claimed_retry = coordinator.claim_task(
            _ORGANIZATION,
            _CORRELATION,
            retry_current.task_id,
            retry_current.metadata.version,
            publish=publications.append,
        )
        assert claimed_retry.is_success and claimed_retry.value is not None
        retry_current = claimed_retry.value.task
    else:
        assert retry_limit < 0
        assert retry_current.state is TaskLifecycle.RUNNING
        assert retry_current.retry_count == unlimited_operations

    claimed_refine = coordinator.claim_task(
        _ORGANIZATION,
        _CORRELATION,
        refine_task.task_id,
        refine_task.metadata.version,
        publish=publications.append,
    )
    assert claimed_refine.is_success and claimed_refine.value is not None
    refine_current = claimed_refine.value.task
    iteration_attempts = iteration_limit + 1 if iteration_limit >= 0 else unlimited_operations
    for _ in range(iteration_attempts):
        refined = coordinator.transition(
            _ORGANIZATION,
            _CORRELATION,
            refine_current.task_id,
            refine_current.metadata.version,
            TaskTransitionCommand(TaskLifecycle.SELF_REFINE, "self_refine"),
            publish=publications.append,
        )
        assert refined.is_success and refined.value is not None
        refine_current = refined.value.task
        if iteration_limit >= 0 and refine_current.state is TaskLifecycle.FAILED:
            assert refine_current.iteration_count == iteration_limit
            assert refine_current.failure_reason == "iteration_limit_exhausted"
            _assert_claimable(coordinator, refine_current.task_id, False)
            break
        assert refine_current.state is TaskLifecycle.SELF_REFINE
        resumed = coordinator.transition(
            _ORGANIZATION,
            _CORRELATION,
            refine_current.task_id,
            refine_current.metadata.version,
            TaskTransitionCommand(TaskLifecycle.RUNNING, "self_refine_resumed"),
            publish=publications.append,
        )
        assert resumed.is_success and resumed.value is not None
        refine_current = resumed.value.task
    else:
        assert iteration_limit < 0
        assert refine_current.state is TaskLifecycle.RUNNING
        assert refine_current.iteration_count == unlimited_operations
        completed_refine = coordinator.transition(
            _ORGANIZATION,
            _CORRELATION,
            refine_current.task_id,
            refine_current.metadata.version,
            TaskTransitionCommand(TaskLifecycle.COMPLETE, "refinement_complete"),
            publish=publications.append,
        )
        assert completed_refine.is_success and completed_refine.value is not None
        assert completed_refine.value.task.state is TaskLifecycle.COMPLETE

    source_lineage = RunProvenance(
        metadata=_metadata(f"provenance-record-{value}"),
        run_provenance_id=RunProvenanceId(f"provenance-{value}"),
        graph_revision_id=graph_id,
        workflow_definition={"id": f"workflow-{value}"},
        workflow_definition_version="1.0.0",
        agent_version_ids=(agent.agent_version_id,),
        pattern_version_ids=(),
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.provenance.append(source_lineage).is_success
    replay = coordinator.create_replay_lineage(
        _ORGANIZATION,
        _CORRELATION,
        source_lineage.run_provenance_id,
        f"replay-checkpoint-{value}",
        (f"artifact-{value}",),
        publish=publications.append,
    )
    assert replay.is_success and replay.value is not None
    assert replay.value.run_provenance_id != source_lineage.run_provenance_id
    assert replay.value.source_run_provenance_id == source_lineage.run_provenance_id
    assert replay.value.graph_revision_id == source_lineage.graph_revision_id
    assert replay.value.workflow_definition == source_lineage.workflow_definition
    assert replay.value.agent_version_ids == source_lineage.agent_version_ids
    assert replay.value.source_checkpoint_reference == f"replay-checkpoint-{value}"
    assert replay.value.artifact_version_references == (f"artifact-{value}",)

    source_history = _history(database, source.task_id)
    assert tuple((item.from_state, item.to_state) for item in source_history) == (
        (TaskLifecycle.IDLE, TaskLifecycle.QUEUED),
        (TaskLifecycle.QUEUED, TaskLifecycle.RUNNING),
        (TaskLifecycle.RUNNING, TaskLifecycle.COMPLETE),
    )
    assert tuple(item.expected_task_version for item in source_history) == (1, 2, 3)
    source_events = tuple(
        event
        for event in database._state.events.values()
        if event.event_type == "task.transitioned"
        and event.redacted_payload["task_id"] == str(source.task_id)
    )
    assert tuple(event.redacted_payload["to_state"] for event in source_events) == (
        "queued",
        "running",
        "complete",
    )
    source_audits = tuple(
        audit
        for audit in database._state.audits.values()
        if audit.action == "task.transitioned"
        and audit.subject_reference == f"task:{source.task_id}"
    )
    assert tuple(audit.outcome for audit in source_audits) == ("queued", "running", "complete")
    assert all(task.state in TaskLifecycle for task in database._state.tasks.values())
    _assert_publications_committed(database, publications)
