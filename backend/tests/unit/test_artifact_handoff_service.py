"""Focused tests for adoption Artifact_Handoff barriers and lineage."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from app.artifacts.handoff_service import ArtifactHandoffService
from app.models.common import RecordMetadata
from app.models.control_plane import (
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    TaskId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.artifact_repository import InMemoryArtifactRepository
from tests.fakes.adoption import (
    DeterministicArtifactHandoffRepository,
    DeterministicAuditRepository,
    FakeFailurePlan,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("handoff-organization")
_CORRELATION = CorrelationId("handoff-correlation")


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


def _handoff(handoff_id: str, parents: tuple[str, ...] = ()) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"record-{handoff_id}"),
        handoff_id=ArtifactHandoffId(handoff_id),
        artifact_identity="artifact-handoff",
        artifact_version="1.0.0",
        parent_lineage=parents,
        source_task_id=TaskId("source-task"),
        source_run_reference="source-run",
        brief_scope="brief-reference",
        technical_specification={"schema_version": "1"},
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference="provenance-reference",
        owner_reference="owner-reference",
        classification="internal",
        integrity_reference="sha256:artifact",
        approval_reference="approval-reference",
    )


def test_internal_handoff_is_available_only_after_complete_persistence() -> None:
    repository = InMemoryArtifactRepository()
    service = ArtifactHandoffService(repository, DeterministicAuditRepository(), clock=lambda: _NOW)

    result = service.create_internal(_ORGANIZATION, _handoff("internal"))

    assert result.is_success and result.value is not None
    assert result.value.availability is ArtifactAvailabilityStatus.AVAILABLE
    assert result.value.metadata_persisted
    available = repository.available_for_downstream(_ORGANIZATION)
    assert available.is_success and available.value == (result.value,)


def test_external_handoff_crosses_availability_barrier_after_confirmation() -> None:
    repository = InMemoryArtifactRepository()
    service = ArtifactHandoffService(repository, DeterministicAuditRepository(), clock=lambda: _NOW)

    result = service.submit_external(_ORGANIZATION, _handoff("external"))

    assert result.is_success and result.value is not None
    assert result.value.external
    assert result.value.availability is ArtifactAvailabilityStatus.AVAILABLE
    assert result.value.metadata_persisted
    available = service.available_for_downstream(_ORGANIZATION, _CORRELATION)
    assert available.is_success and available.value == (result.value,)


def test_incomplete_metadata_is_rejected_before_repository_persistence() -> None:
    repository = InMemoryArtifactRepository()
    service = ArtifactHandoffService(repository)
    incomplete = replace(_handoff("incomplete"), approval_reference=None)

    result = service.create_internal(_ORGANIZATION, incomplete)

    assert not result.is_success
    assert result.error is not None
    assert tuple(field.name for field in result.error.fields) == ("approval_reference",)
    assert repository.handoffs_for_organization(_ORGANIZATION) == ()


def test_lineage_cycle_is_rejected_without_persisting_the_candidate() -> None:
    repository = InMemoryArtifactRepository()
    service = ArtifactHandoffService(repository)
    assert service.create_internal(_ORGANIZATION, _handoff("parent", ("child",))).is_success

    result = service.create_internal(_ORGANIZATION, _handoff("child", ("parent",)))

    assert not result.is_success
    assert result.error is not None
    assert result.error.code.value == "conflict"
    retained = repository.handoffs_for_organization(_ORGANIZATION)
    assert tuple(str(record.handoff_id) for record in retained) == ("parent",)


def test_va_extension_schema_blocks_and_audits_invalid_handoff() -> None:
    repository = InMemoryArtifactRepository()
    audits = DeterministicAuditRepository()
    service = ArtifactHandoffService(
        repository,
        audits,
        va_extension_schema={"schema_version": str},
        clock=lambda: _NOW,
    )

    result = service.create_internal(
        _ORGANIZATION,
        replace(_handoff("va-invalid"), technical_specification={"schema_version": 1}),
    )

    assert not result.is_success
    assert repository.handoffs_for_organization(_ORGANIZATION) == ()
    assert len(audits.records) == 1
    assert audits.records[0].action == "artifact_handoff.va_extension.blocked"


def test_external_persistence_failure_keeps_handoff_unavailable() -> None:
    failure_plan = FakeFailurePlan()
    failure_plan.fail_next_persistence("handoff.append")
    repository = DeterministicArtifactHandoffRepository(failure_plan)
    service = ArtifactHandoffService(repository)

    result = service.submit_external(_ORGANIZATION, _handoff("failed"))

    assert not result.is_success
    available = repository.available_for_downstream(_ORGANIZATION)
    assert available.is_success and available.value == ()


def test_premature_external_availability_is_revoked_and_audited() -> None:
    repository = InMemoryArtifactRepository()
    audits = DeterministicAuditRepository()
    service = ArtifactHandoffService(repository, audits, clock=lambda: _NOW)
    pending = replace(_handoff("premature"), external=True)
    assert repository.append(pending).is_success

    result = service.revoke_premature_availability(_ORGANIZATION, pending.handoff_id, _CORRELATION)

    assert result.is_success and result.value is not None
    assert result.value.availability is ArtifactAvailabilityStatus.REVOKED
    available = repository.available_for_downstream(_ORGANIZATION)
    assert available.is_success and available.value == ()
    assert audits.records[0].action == "artifact_handoff.availability.revoked"
