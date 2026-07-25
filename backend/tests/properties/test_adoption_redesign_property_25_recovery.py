"""Property checks for evidence-gated, target-exact Recovery_Action restoration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.engines.recovery import (
    InMemoryImmutableVersionStore,
    RecoveryService,
)
from app.models.control_plane import RecoveryActionId, RecoveryActionStatus
from app.models.identifiers import CorrelationId, DomainPackId, OrganizationId
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_TARGET_VERSIONS = ("1.0.0", "2.0.0", "3.4.5")
_CURRENT_VERSION = "9.0.0"


@dataclass(frozen=True, slots=True)
class RecoveryCase:
    """Bounded approval, evidence, target, and persistence outcomes."""

    case_id: int
    designated_version: str
    approved: bool
    has_investigation_evidence: bool
    evidence_persists: bool


@st.composite
def _recovery_cases(draw: st.DrawFn) -> RecoveryCase:
    """Generate deterministic Recovery_Action decision and persistence branches."""
    return RecoveryCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        designated_version=draw(st.sampled_from(_TARGET_VERSIONS)),
        approved=draw(st.booleans()),
        has_investigation_evidence=draw(st.booleans()),
        evidence_persists=draw(st.booleans()),
    )


def _organization(case: RecoveryCase) -> OrganizationId:
    """Return the isolated organization for one generated recovery."""
    return OrganizationId(f"organization-property-25-{case.case_id}")


def _pack(case: RecoveryCase) -> DomainPackId:
    """Return the immutable pack identity under the generated recovery."""
    return DomainPackId(f"domain-pack-property-25-{case.case_id}")


def _correlation(case: RecoveryCase) -> CorrelationId:
    """Return the deterministic request correlation for the generated recovery."""
    return CorrelationId(f"correlation-property-25-{case.case_id}")


def _recovery_action_id(case: RecoveryCase) -> RecoveryActionId:
    """Return the stable action identity used by the generated case."""
    return RecoveryActionId(f"recovery-action-property-25-{case.case_id}")


def _service(
    case: RecoveryCase,
) -> tuple[RecoveryService, InMemoryImmutableVersionStore, DeterministicAdoptionRepositories]:
    """Compose RecoveryService from isolated deterministic fakes."""
    failure_plan = FakeFailurePlan()
    if not case.evidence_persists:
        failure_plan.fail_next_persistence("recovery.append")
    repositories = DeterministicAdoptionRepositories(failure_plan)
    versions = InMemoryImmutableVersionStore()
    organization_id = _organization(case)
    pack_id = _pack(case)
    correlation_id = _correlation(case)
    versions.approve_version(organization_id, pack_id, _CURRENT_VERSION)
    versions.approve_version(organization_id, pack_id, case.designated_version)
    initialized = versions.restore(
        organization_id,
        pack_id,
        _CURRENT_VERSION,
        correlation_id,
    )
    assert initialized.is_success
    return (
        RecoveryService(
            repositories.recoveries,
            versions,
            clock=lambda: _NOW,
        ),
        versions,
        repositories,
    )


# Feature: adoption-redesign, Property 25: Recovery is evidence-gated and target-exact
# **Validates: Requirements 9.4, 9.5, 9.6**
@settings(max_examples=100, deadline=None)
@example(
    case=RecoveryCase(
        case_id=0,
        designated_version="1.0.0",
        approved=True,
        has_investigation_evidence=True,
        evidence_persists=True,
    )
)
@example(
    case=RecoveryCase(
        case_id=1,
        designated_version="2.0.0",
        approved=True,
        has_investigation_evidence=True,
        evidence_persists=False,
    )
)
@example(
    case=RecoveryCase(
        case_id=2,
        designated_version="3.4.5",
        approved=True,
        has_investigation_evidence=False,
        evidence_persists=True,
    )
)
@given(case=_recovery_cases())
def test_property_25_recovery_is_evidence_gated_and_target_exact(
    case: RecoveryCase,
) -> None:
    """Only persisted investigation evidence permits exact target restoration."""
    service, versions, repositories = _service(case)
    organization_id = _organization(case)
    pack_id = _pack(case)
    correlation_id = _correlation(case)
    evidence_references = (
        (f"investigation-property-25-{case.case_id}",) if case.has_investigation_evidence else ()
    )

    result = service.recover(
        correlation_id,
        organization_id=organization_id,
        recovery_action_id=_recovery_action_id(case),
        pack_id=pack_id,
        designated_immutable_version=case.designated_version,
        approval_reference=f"approval-property-25-{case.case_id}",
        investigation_evidence_references=evidence_references,
        approved=case.approved,
    )

    expected_restoration = (
        case.approved and case.has_investigation_evidence and case.evidence_persists
    )
    if expected_restoration:
        assert result.is_success and result.value is not None
        recovery = result.value
        assert recovery.status is RecoveryActionStatus.RESTORED
        assert recovery.designated_immutable_version == case.designated_version
        assert recovery.restored_immutable_version == case.designated_version
        assert versions.current_versions[(organization_id, pack_id)] == case.designated_version
        assert versions.restore_calls[-1] == (
            organization_id,
            pack_id,
            case.designated_version,
        )
        assert repositories.recoveries.records() == (recovery,)
    else:
        assert not result.is_success
        assert result.error is not None
        assert versions.current_versions[(organization_id, pack_id)] == _CURRENT_VERSION
        assert versions.restore_calls == [(organization_id, pack_id, _CURRENT_VERSION)]
        assert repositories.recoveries.records() == ()
