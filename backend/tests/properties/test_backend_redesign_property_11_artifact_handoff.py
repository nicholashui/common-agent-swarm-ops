"""Property checks for complete, blocked, and opaque artifact handoffs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields, replace
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

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
_ORGANIZATION = OrganizationId("property-11-organization")
_FOREIGN_ORGANIZATION = OrganizationId("property-11-foreign-organization")
_CORRELATION = CorrelationId("property-11-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_PRESENCE_FIELDS = (
    "parent_lineage",
    "technical_specification",
    "rights_and_consent_state",
    "continuity_state",
    "quality_control_state",
    "target_channels",
    "provenance_reference",
)
_MISSING_FIELD_SUBSETS = st.frozensets(st.sampled_from(_PRESENCE_FIELDS))


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _dependent_task(value: str) -> AgentTask:
    return AgentTask(
        metadata=_metadata(f"task-record-{value}"),
        task_id=TaskId(f"dependent-task-{value}"),
        run_reference=f"run-{value}",
        pinned_agent_version_id=AgentVersionId(f"agent-{value}"),
        dependencies=(),
        constraints={},
        approval_gate_ids=(),
        checkpoint_reference=None,
        state=TaskLifecycle.QUEUED,
    )


def _handoff(value: str, missing_fields: frozenset[str], sentinel: str) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"handoff-record-{value}"),
        handoff_id=ArtifactHandoffId(f"handoff-{value}"),
        artifact_identity=f"artifact-{value}",
        artifact_version=f"version-{value}",
        parent_lineage=() if "parent_lineage" in missing_fields else (f"parent-{value}",),
        source_task_id=TaskId(f"source-task-{value}"),
        source_run_reference=f"source-run-{value}",
        brief_scope=f"private-scope::{sentinel}",
        technical_specification=(
            None
            if "technical_specification" in missing_fields
            else {"protected_artifact_content": sentinel, "declared_result": "invalid"}
        ),
        rights_and_consent_state=(
            None if "rights_and_consent_state" in missing_fields else f"denied::{sentinel}"
        ),
        continuity_state=(
            None if "continuity_state" in missing_fields else f"discontinuous::{sentinel}"
        ),
        quality_control_state=(
            None if "quality_control_state" in missing_fields else f"failed::{sentinel}"
        ),
        target_channels=(
            () if "target_channels" in missing_fields else (f"restricted::{sentinel}",)
        ),
        provenance_reference=(
            None if "provenance_reference" in missing_fields else f"provenance-{value}"
        ),
    )


def _stored_task(database: InMemoryControlPlaneDatabase, task_id: TaskId) -> AgentTask:
    with database.unit_of_work() as unit_of_work:
        result = unit_of_work.tasks.get(_ORGANIZATION, task_id)
    assert result.is_success and result.value is not None
    return result.value


# Feature: backend-redesign, Property 11
# **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    missing_fields=_MISSING_FIELD_SUBSETS,
    sensitive_value=_SAFE_VALUES,
)
def test_property_11_artifact_handoff_is_complete_blocked_and_opaque(
    value: str,
    missing_fields: frozenset[str],
    sensitive_value: str,
) -> None:
    """Required presence alone gates dispatch while every external view stays opaque."""
    database = InMemoryControlPlaneDatabase()
    service = ArtifactService(_unit_of_work_factory(database), clock=lambda: _NOW)
    task = _dependent_task(value)
    sentinel = f"PROTECTED-ARTIFACT-CONTENT::{sensitive_value}"
    handoff = _handoff(value, missing_fields, sentinel)

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.tasks.create(task).is_success
    created = service.create_handoff(_ORGANIZATION, handoff)
    assert created.is_success and created.value == handoff
    with database.unit_of_work() as unit_of_work:
        stored_result = unit_of_work.artifacts.get(_ORGANIZATION, handoff.handoff_id)
    assert stored_result.is_success and stored_result.value == handoff
    assert sentinel in repr(stored_result.value)

    expected_missing = tuple(name for name in _PRESENCE_FIELDS if name in missing_fields)
    assert service.missing_required_fields(handoff) == expected_missing
    assert service.missing_required_fields(replace(handoff, brief_scope=None)) == expected_missing

    validation_result = service.validate_dependent_handoff(
        _ORGANIZATION,
        task.task_id,
        handoff.handoff_id,
        _CORRELATION,
    )
    assert validation_result.is_success and validation_result.value is not None
    validation = validation_result.value
    assert validation.missing_fields == expected_missing
    assert validation.is_complete is (not expected_missing)

    retained_task = _stored_task(database, task.task_id)
    if expected_missing:
        assert retained_task.state is TaskLifecycle.BLOCKED
        assert retained_task.blocked_fields == expected_missing
    else:
        assert retained_task.state is TaskLifecycle.QUEUED
        assert retained_task.blocked_fields == ()

    browser_result = service.read_browser_projection(
        _ORGANIZATION,
        handoff.handoff_id,
        _CORRELATION,
    )
    assert browser_result.is_success and browser_result.value is not None
    browser_projection = browser_result.value
    assert {field.name for field in fields(browser_projection)} == {
        "handoff_id",
        "artifact_identity",
        "artifact_version",
        "parent_lineage",
        "source_task_id",
        "source_run_reference",
        "validation",
    }
    assert browser_projection.parent_lineage == handoff.parent_lineage
    assert browser_projection.validation.missing_fields == expected_missing
    assert sentinel not in repr(browser_projection)

    foreign_browser_result = service.read_browser_projection(
        _FOREIGN_ORGANIZATION,
        handoff.handoff_id,
        _CORRELATION,
    )
    assert not foreign_browser_result.is_success
    assert foreign_browser_result.value is None
    assert foreign_browser_result.error is not None
    assert foreign_browser_result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert sentinel not in repr(foreign_browser_result.error)

    dispatched_references: list[object] = []
    downstream_result = service.downstream_input(
        _ORGANIZATION,
        task.task_id,
        handoff.handoff_id,
        _CORRELATION,
    )
    if expected_missing:
        assert not downstream_result.is_success
        assert downstream_result.value is None
        assert downstream_result.error is not None
        assert downstream_result.error.code is ErrorCode.VALIDATION_FAILED
        assert tuple(field.name for field in downstream_result.error.fields) == expected_missing
        assert _stored_task(database, task.task_id).state is TaskLifecycle.BLOCKED
    else:
        assert downstream_result.is_success and downstream_result.value is not None
        downstream_reference = downstream_result.value
        dispatched_references.append(downstream_reference)
        assert {field.name for field in fields(downstream_reference)} == {
            "handoff_id",
            "artifact_identity",
            "artifact_version",
            "provenance_reference",
        }
        assert downstream_reference.provenance_reference == handoff.provenance_reference
        assert sentinel not in repr(downstream_reference)
    assert len(dispatched_references) == int(not expected_missing)

    foreign_downstream_result = service.downstream_input(
        _FOREIGN_ORGANIZATION,
        task.task_id,
        handoff.handoff_id,
        _CORRELATION,
    )
    assert not foreign_downstream_result.is_success
    assert foreign_downstream_result.value is None
    assert foreign_downstream_result.error is not None
    assert foreign_downstream_result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert sentinel not in repr(foreign_downstream_result.error)
