"""Focused ArtifactService acceptance tests for backend-redesign task 8.3."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import fields
from datetime import UTC, datetime
from typing import cast

from app.artifacts.service import ArtifactService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ArtifactHandoff,
    ArtifactHandoffId,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("artifact-service-organization")
_FOREIGN_ORGANIZATION = OrganizationId("artifact-service-foreign-organization")
_CORRELATION = CorrelationId("artifact-service-correlation")


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _metadata(record_id: str, organization_id: OrganizationId = _ORGANIZATION) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=organization_id,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _task() -> AgentTask:
    return AgentTask(
        metadata=_metadata("dependent-task-record"),
        task_id=TaskId("dependent-task"),
        run_reference="run-focused",
        pinned_agent_version_id=AgentVersionId("agent-focused-v1"),
        dependencies=(),
        constraints={},
        approval_gate_ids=(),
        checkpoint_reference=None,
        state=TaskLifecycle.QUEUED,
    )


def _handoff(
    *,
    organization_id: OrganizationId = _ORGANIZATION,
    technical_specification: Mapping[str, object] | None,
    provenance_reference: str | None = "provenance-focused",
) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata("handoff-record", organization_id),
        handoff_id=ArtifactHandoffId("handoff-focused"),
        artifact_identity="artifact-focused",
        artifact_version="version-1",
        parent_lineage=("parent-version",),
        source_task_id=TaskId("source-task"),
        source_run_reference="source-run",
        brief_scope="restricted-brief",
        technical_specification=technical_specification,
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference=provenance_reference,
    )


def _service(database: InMemoryControlPlaneDatabase) -> ArtifactService:
    return ArtifactService(_unit_of_work_factory(database), clock=lambda: _NOW)


def test_complete_handoff_accepts_dependent_dispatch_with_reference_only_input() -> None:
    """Complete presence fields permit dispatch and expose only authorized references."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    task = _task()
    sentinel = "PROTECTED-ARTIFACT-CONTENT"
    handoff = _handoff(technical_specification={"content": sentinel})
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.tasks.create(task).is_success
    assert service.create_handoff(_ORGANIZATION, handoff).is_success

    validation = service.validate_dependent_handoff(
        _ORGANIZATION, task.task_id, handoff.handoff_id, _CORRELATION
    )
    dispatched = service.downstream_input(
        _ORGANIZATION, task.task_id, handoff.handoff_id, _CORRELATION
    )

    assert validation.is_success and validation.value is not None
    assert validation.value.is_complete
    assert dispatched.is_success and dispatched.value is not None
    assert dispatched.value.provenance_reference == handoff.provenance_reference
    assert sentinel not in repr(dispatched.value)
    with database.unit_of_work() as unit_of_work:
        stored_task = unit_of_work.tasks.get(_ORGANIZATION, task.task_id)
    assert stored_task.is_success and stored_task.value is not None
    assert stored_task.value.state is TaskLifecycle.QUEUED
    assert stored_task.value.blocked_fields == ()


def test_incomplete_handoff_persists_each_missing_field_name_and_blocks_dispatch() -> None:
    """Missing required fields are durably retained on the dependent blocked task."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    task = _task()
    handoff = _handoff(technical_specification=None, provenance_reference=None)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.tasks.create(task).is_success
    assert service.create_handoff(_ORGANIZATION, handoff).is_success

    validation = service.validate_dependent_handoff(
        _ORGANIZATION, task.task_id, handoff.handoff_id, _CORRELATION
    )
    dispatched = service.downstream_input(
        _ORGANIZATION, task.task_id, handoff.handoff_id, _CORRELATION
    )

    expected_missing = ("technical_specification", "provenance_reference")
    assert validation.is_success and validation.value is not None
    assert validation.value.missing_fields == expected_missing
    assert not validation.value.is_complete
    assert not dispatched.is_success
    assert dispatched.error is not None
    assert dispatched.error.code is ErrorCode.VALIDATION_FAILED
    assert tuple(field.name for field in dispatched.error.fields) == expected_missing
    with database.unit_of_work() as unit_of_work:
        stored_task = unit_of_work.tasks.get(_ORGANIZATION, task.task_id)
    assert stored_task.is_success and stored_task.value is not None
    assert stored_task.value.state is TaskLifecycle.BLOCKED
    assert stored_task.value.blocked_fields == expected_missing


def test_browser_projection_is_redacted_and_organization_scoped() -> None:
    """A permitted projection omits protected values and foreign reads stay non-disclosing."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    sentinel = "PROTECTED-ARTIFACT-CONTENT"
    handoff = _handoff(technical_specification={"content": sentinel})
    assert service.create_handoff(_ORGANIZATION, handoff).is_success

    permitted = service.read_browser_projection(_ORGANIZATION, handoff.handoff_id, _CORRELATION)
    foreign = service.read_browser_projection(
        _FOREIGN_ORGANIZATION, handoff.handoff_id, _CORRELATION
    )

    assert permitted.is_success and permitted.value is not None
    assert {field.name for field in fields(permitted.value)} == {
        "handoff_id",
        "artifact_identity",
        "artifact_version",
        "parent_lineage",
        "source_task_id",
        "source_run_reference",
        "validation",
    }
    assert sentinel not in repr(permitted.value)
    assert not foreign.is_success
    assert foreign.value is None
    assert foreign.error is not None
    assert foreign.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert sentinel not in repr(foreign.error)
