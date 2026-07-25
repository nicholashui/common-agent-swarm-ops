"""Property checks for complete, acyclic Artifact_Handoff availability barriers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.artifacts.handoff_service import ArtifactHandoffService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    TaskId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.artifact_repository import InMemoryArtifactRepository
from tests.fakes.adoption import DeterministicAuditRepository, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_OPTIONAL_METADATA_FIELDS = (
    "owner_reference",
    "classification",
    "integrity_reference",
    "approval_reference",
    "provenance_reference",
)


@dataclass(frozen=True, slots=True)
class _HandoffCase:
    """Bounded lineage, metadata, and persistence events for one property example."""

    case_id: int
    parent_indexes: tuple[tuple[int, ...], ...]
    missing_metadata_fields: frozenset[str]
    internal_append_succeeds: bool
    external_append_succeeds: bool
    external_confirmation_succeeds: bool
    premature_external_exposure: bool
    audit_append_succeeds: bool

    @property
    def organization_id(self) -> OrganizationId:
        """Return the generated tenant boundary for the case."""
        return OrganizationId(f"property-6-org-{self.case_id}")

    @property
    def correlation_id(self) -> CorrelationId:
        """Return the generated correlation boundary for the case."""
        return CorrelationId(f"property-6-correlation-{self.case_id}")


class _ControlledArtifactRepository(InMemoryArtifactRepository):
    """Deterministic handoff fake exposing append and confirmation event outcomes."""

    def __init__(
        self,
        *,
        append_succeeds: bool = True,
        confirmation_succeeds: bool = True,
        expose_prematurely: bool = False,
    ) -> None:
        super().__init__()
        self.append_succeeds = append_succeeds
        self.confirmation_succeeds = confirmation_succeeds
        self.expose_prematurely = expose_prematurely
        self.events: list[str] = []

    def append_handoff(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, ErrorDetail]:
        """Record the availability state presented to persistence before any write."""
        self.events.append(f"append:{record.availability.value}:{record.metadata_persisted}")
        if not self.append_succeeds:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Artifact handoff persistence is unavailable.",
                    record.metadata.correlation_id,
                    retryable=True,
                )
            )
        return super().append_handoff(record)

    def confirm_metadata_persistence(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Record and optionally fail the external metadata confirmation barrier."""
        self.events.append("confirm")
        if not self.confirmation_succeeds:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Artifact handoff metadata confirmation is unavailable.",
                    CorrelationId("property-6-confirmation"),
                    retryable=True,
                )
            )
        return super().confirm_metadata_persistence(organization_id, handoff_id)

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        """Optionally model a faulty external exposure before confirmation."""
        self.events.append("available")
        if not self.expose_prematurely:
            return super().available_for_downstream(organization_id)
        return Result.success(
            tuple(
                record
                for record in self.handoffs_for_organization(organization_id)
                if record.external and record.availability is ArtifactAvailabilityStatus.PENDING
            )
        )


@st.composite
def _handoff_cases(draw: st.DrawFn) -> _HandoffCase:
    """Generate short acyclic lineages and independently configurable write outcomes."""
    case_id = draw(st.integers(min_value=0, max_value=1_000))
    lineage_length = draw(st.integers(min_value=1, max_value=4))
    parent_indexes: list[tuple[int, ...]] = []
    for index in range(lineage_length):
        if index == 0:
            parent_indexes.append(())
            continue
        parents = draw(
            st.lists(
                st.integers(min_value=0, max_value=index - 1),
                min_size=0,
                max_size=min(index, 2),
                unique=True,
            )
        )
        parent_indexes.append(tuple(parents))

    return _HandoffCase(
        case_id=case_id,
        parent_indexes=tuple(parent_indexes),
        missing_metadata_fields=frozenset(
            draw(
                st.sets(
                    st.sampled_from(_OPTIONAL_METADATA_FIELDS),
                    min_size=0,
                    max_size=len(_OPTIONAL_METADATA_FIELDS),
                )
            )
        ),
        internal_append_succeeds=draw(st.booleans()),
        external_append_succeeds=draw(st.booleans()),
        external_confirmation_succeeds=draw(st.booleans()),
        premature_external_exposure=draw(st.booleans()),
        audit_append_succeeds=draw(st.booleans()),
    )


def _metadata(case: _HandoffCase, label: str) -> RecordMetadata:
    """Build immutable record metadata for one generated handoff."""
    return RecordMetadata(
        record_id=RecordId(f"property-6-record-{case.case_id}-{label}"),
        organization_id=case.organization_id,
        correlation_id=case.correlation_id,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _handoff(
    case: _HandoffCase,
    label: str,
    *,
    parent_lineage: tuple[str, ...] = (),
    missing_metadata_fields: frozenset[str] = frozenset(),
) -> ArtifactHandoff:
    """Build a metadata-complete or deliberately incomplete opaque handoff."""
    values: dict[str, str | None] = {
        "owner_reference": f"owner-{case.case_id}-{label}",
        "classification": f"classification-{case.case_id}",
        "integrity_reference": f"sha256:property-6-{case.case_id}-{label}",
        "approval_reference": f"approval-{case.case_id}-{label}",
        "provenance_reference": f"provenance-{case.case_id}-{label}",
    }
    for field_name in missing_metadata_fields:
        values[field_name] = None
    return ArtifactHandoff(
        metadata=_metadata(case, label),
        handoff_id=ArtifactHandoffId(f"property-6-{case.case_id}-{label}"),
        artifact_identity=f"artifact-{case.case_id}-{label}",
        artifact_version="1.0.0",
        parent_lineage=parent_lineage,
        source_task_id=TaskId(f"source-task-{case.case_id}-{label}"),
        source_run_reference=f"source-run-{case.case_id}-{label}",
        brief_scope=f"brief-{case.case_id}",
        technical_specification={"schema_version": "1"},
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        owner_reference=values["owner_reference"],
        classification=values["classification"],
        integrity_reference=values["integrity_reference"],
        approval_reference=values["approval_reference"],
        provenance_reference=values["provenance_reference"],
    )


def _audit_repository(case: _HandoffCase) -> DeterministicAuditRepository:
    """Create an isolated audit fake for the generated revocation outcome."""
    failure_plan = FakeFailurePlan()
    if not case.audit_append_succeeds:
        failure_plan.fail_next_audit()
    return DeterministicAuditRepository(failure_plan)


# Feature: adoption-redesign, Property 6: Artifact availability follows complete, acyclic evidence
# **Validates: Requirements 3.9, 3.10, 3.11, 3.12, 3.13, 7.1, 7.3**
@settings(max_examples=100, deadline=None)
@given(handoff_case=_handoff_cases())
def test_property_6_artifact_availability_requires_complete_acyclic_evidence(
    handoff_case: _HandoffCase,
) -> None:
    """Metadata, lineage, persistence, and availability barriers remain fail-closed."""
    metadata_repository = _ControlledArtifactRepository()
    metadata_service = ArtifactHandoffService(metadata_repository)
    incomplete = _handoff(
        handoff_case,
        "incomplete",
        missing_metadata_fields=handoff_case.missing_metadata_fields,
    )
    metadata_result = metadata_service.create_internal(handoff_case.organization_id, incomplete)
    if handoff_case.missing_metadata_fields:
        assert not metadata_result.is_success
        assert metadata_result.error is not None
        assert tuple(field.name for field in metadata_result.error.fields) == tuple(
            field
            for field in _OPTIONAL_METADATA_FIELDS
            if field in handoff_case.missing_metadata_fields
        )
        assert metadata_repository.handoffs_for_organization(handoff_case.organization_id) == ()
    else:
        assert metadata_result.is_success and metadata_result.value is not None
        assert metadata_result.value.availability is ArtifactAvailabilityStatus.AVAILABLE
        assert metadata_result.value.metadata_persisted

    internal_repository = _ControlledArtifactRepository(
        append_succeeds=handoff_case.internal_append_succeeds
    )
    internal_service = ArtifactHandoffService(internal_repository)
    internal = _handoff(handoff_case, "internal")
    internal_result = internal_service.create_internal(handoff_case.organization_id, internal)
    if handoff_case.internal_append_succeeds:
        assert internal_result.is_success and internal_result.value is not None
        assert internal_result.value.availability is ArtifactAvailabilityStatus.AVAILABLE
        assert internal_result.value.metadata_persisted
        available = internal_repository.available_for_downstream(handoff_case.organization_id)
        assert available.is_success and available.value == (internal_result.value,)
        assert internal_repository.events[0] == "append:available:True"
    else:
        assert not internal_result.is_success
        assert internal_repository.handoffs_for_organization(handoff_case.organization_id) == ()
        available = internal_repository.available_for_downstream(handoff_case.organization_id)
        assert available.is_success and available.value == ()
        assert internal_repository.events[0] == "append:available:True"

    lineage_repository = InMemoryArtifactRepository()
    lineage_service = ArtifactHandoffService(lineage_repository)
    lineage_ids = tuple(
        f"property-6-{handoff_case.case_id}-lineage-{index}"
        for index in range(len(handoff_case.parent_indexes))
    )
    for index, parent_indexes in enumerate(handoff_case.parent_indexes):
        record = _handoff(
            handoff_case,
            f"lineage-{index}",
            parent_lineage=tuple(lineage_ids[parent] for parent in parent_indexes),
        )
        created = lineage_service.create_internal(handoff_case.organization_id, record)
        assert created.is_success and created.value is not None
        assert created.value.availability is ArtifactAvailabilityStatus.AVAILABLE
    retained_lineage = lineage_repository.handoffs_for_organization(handoff_case.organization_id)
    assert tuple(str(record.handoff_id) for record in retained_lineage) == lineage_ids

    cycle_b_id = f"property-6-{handoff_case.case_id}-cycle-b"
    cycle_a = _handoff(handoff_case, "cycle-a", parent_lineage=(cycle_b_id,))
    cycle_b = _handoff(handoff_case, "cycle-b", parent_lineage=(str(cycle_a.handoff_id),))
    assert lineage_service.create_internal(handoff_case.organization_id, cycle_a).is_success
    cycle_result = lineage_service.create_internal(handoff_case.organization_id, cycle_b)
    assert not cycle_result.is_success
    assert cycle_result.error is not None
    assert cycle_result.error.code is ErrorCode.CONFLICT
    assert tuple(
        str(record.handoff_id)
        for record in lineage_repository.handoffs_for_organization(handoff_case.organization_id)
    ) == (*lineage_ids, str(cycle_a.handoff_id))

    external_repository = _ControlledArtifactRepository(
        append_succeeds=handoff_case.external_append_succeeds,
        confirmation_succeeds=handoff_case.external_confirmation_succeeds,
    )
    external_service = ArtifactHandoffService(external_repository)
    external = _handoff(handoff_case, "external")
    external_result = external_service.submit_external(handoff_case.organization_id, external)
    if not handoff_case.external_append_succeeds:
        assert not external_result.is_success
        assert external_repository.events == ["append:pending:False"]
        assert external_repository.handoffs_for_organization(handoff_case.organization_id) == ()
    elif not handoff_case.external_confirmation_succeeds:
        assert not external_result.is_success
        assert external_repository.events == ["append:pending:False", "confirm"]
        pending = external_repository.handoffs_for_organization(handoff_case.organization_id)
        assert len(pending) == 1
        assert pending[0].availability is ArtifactAvailabilityStatus.PENDING
        assert not pending[0].metadata_persisted
        available = external_repository.available_for_downstream(handoff_case.organization_id)
        assert available.is_success and available.value == ()
    else:
        assert external_result.is_success and external_result.value is not None
        assert external_result.value.external
        assert external_result.value.availability is ArtifactAvailabilityStatus.AVAILABLE
        assert external_result.value.metadata_persisted
        available = external_repository.available_for_downstream(handoff_case.organization_id)
        assert available.is_success and available.value == (external_result.value,)
        assert external_repository.events == ["append:pending:False", "confirm", "available"]

    if (
        handoff_case.external_append_succeeds
        and not handoff_case.external_confirmation_succeeds
        and handoff_case.premature_external_exposure
    ):
        audits = _audit_repository(handoff_case)
        premature_repository = _ControlledArtifactRepository(
            confirmation_succeeds=False,
            expose_prematurely=True,
        )
        premature_service = ArtifactHandoffService(
            premature_repository,
            audits,
            clock=lambda: _NOW,
        )
        premature_result = premature_service.submit_external(
            handoff_case.organization_id, _handoff(handoff_case, "premature")
        )
        assert not premature_result.is_success
        leaked = premature_repository.available_for_downstream(handoff_case.organization_id)
        assert leaked.is_success and len(leaked.value or ()) == 1

        revoked = premature_service.revoke_premature_availability(
            handoff_case.organization_id,
            ArtifactHandoffId(f"property-6-{handoff_case.case_id}-premature"),
            handoff_case.correlation_id,
        )
        assert (
            premature_repository.available_for_downstream(handoff_case.organization_id).value == ()
        )
        if handoff_case.audit_append_succeeds:
            assert revoked.is_success and revoked.value is not None
            assert revoked.value.availability is ArtifactAvailabilityStatus.REVOKED
            assert len(audits.records) == 1
            assert audits.records[0].action == "artifact_handoff.availability.revoked"
        else:
            assert not revoked.is_success
            assert revoked.error is not None
            assert revoked.error.code is ErrorCode.AUDIT_UNAVAILABLE
            assert audits.records == ()
