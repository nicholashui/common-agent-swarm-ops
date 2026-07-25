"""Property checks for operational containment and independent maturity evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.governance.operational_containment import (
    CapacityAction,
    OperationalContainmentService,
    PackOperationalStatus,
)
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.control_plane import MaturityLevel, MaturityState, MaturityStateId
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class OperationalContainmentCase:
    """Bounded capacity, provider-failure, audit, and maturity inputs."""

    case_id: int
    observed_load: int
    approved_load_limit: int
    action: CapacityAction
    provider_failure: bool
    audit_persists: bool
    maturity_levels: tuple[MaturityLevel, ...]


@st.composite
def _operational_containment_cases(draw: st.DrawFn) -> OperationalContainmentCase:
    """Generate bounded limits, actions, failure modes, and agent maturities."""
    return OperationalContainmentCase(
        case_id=draw(st.integers(min_value=0, max_value=9_999)),
        observed_load=draw(st.integers(min_value=0, max_value=20)),
        approved_load_limit=draw(st.integers(min_value=0, max_value=20)),
        action=draw(st.sampled_from(tuple(CapacityAction))),
        provider_failure=draw(st.booleans()),
        audit_persists=draw(st.booleans()),
        maturity_levels=tuple(
            draw(st.lists(st.sampled_from(tuple(MaturityLevel)), min_size=1, max_size=4))
        ),
    )


def _case(
    *,
    case_id: int,
    observed_load: int,
    approved_load_limit: int,
    action: CapacityAction,
    provider_failure: bool = False,
    audit_persists: bool = True,
    maturity_levels: tuple[MaturityLevel, ...] = (
        MaturityLevel.CATALOGED,
        MaturityLevel.REGISTERED,
        MaturityLevel.ACTIVE,
        MaturityLevel.PRODUCTION_PROVEN,
    ),
) -> OperationalContainmentCase:
    """Build explicit boundary cases for both approved capacity actions."""
    return OperationalContainmentCase(
        case_id=case_id,
        observed_load=observed_load,
        approved_load_limit=approved_load_limit,
        action=action,
        provider_failure=provider_failure,
        audit_persists=audit_persists,
        maturity_levels=maturity_levels,
    )


def _organization(case: OperationalContainmentCase) -> OrganizationId:
    """Return the isolated organization for one generated containment."""
    return OrganizationId(f"organization-property-26-{case.case_id}")


def _pack(case: OperationalContainmentCase) -> DomainPackId:
    """Return the isolated pack for one generated containment."""
    return DomainPackId(f"domain-pack-property-26-{case.case_id}")


def _correlation(case: OperationalContainmentCase) -> CorrelationId:
    """Return the deterministic request correlation for one generated case."""
    return CorrelationId(f"correlation-property-26-{case.case_id}")


def _maturity_states(case: OperationalContainmentCase) -> tuple[MaturityState, ...]:
    """Build one independently attributable maturity record per generated agent."""
    organization_id = _organization(case)
    pack_id = _pack(case)
    correlation_id = _correlation(case)
    return tuple(
        MaturityState(
            metadata=RecordMetadata(
                record_id=RecordId(f"record-property-26-{case.case_id}-{index}"),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=_NOW,
                updated_at=_NOW,
            ),
            maturity_state_id=MaturityStateId(f"maturity-property-26-{case.case_id}-{index}"),
            pack_id=pack_id,
            immutable_version=_VERSION,
            agent_id=AgentId(f"agent-property-26-{case.case_id}-{index}"),
            level=level,
            evidence_references=(f"evidence:property-26:{case.case_id}:{index}",),
        )
        for index, level in enumerate(case.maturity_levels)
    )


def _maturity_evidence(
    states: tuple[MaturityState, ...],
) -> tuple[tuple[str, str, MaturityLevel, tuple[str, ...]], ...]:
    """Project independent identity and maturity evidence for exact comparison."""
    return tuple(
        (
            str(state.agent_id),
            str(state.maturity_state_id),
            state.level,
            state.evidence_references,
        )
        for state in states
    )


# Feature: adoption-redesign, Property 26: Operational containment preserves independent maturity evidence  # noqa: E501
# **Validates: Requirements 9.8, 9.9**
@settings(max_examples=100, deadline=None)
@example(
    case=_case(
        case_id=0,
        observed_load=2,
        approved_load_limit=1,
        action=CapacityAction.THROTTLE,
    )
)
@example(
    case=_case(
        case_id=1,
        observed_load=2,
        approved_load_limit=1,
        action=CapacityAction.DISABLE,
    )
)
@example(
    case=_case(
        case_id=2,
        observed_load=0,
        approved_load_limit=0,
        action=CapacityAction.DISABLE,
        provider_failure=True,
        audit_persists=False,
        maturity_levels=(MaturityLevel.ACTIVE, MaturityLevel.PRODUCTION_PROVEN),
    )
)
@given(case=_operational_containment_cases())
def test_property_26_capacity_containment_preserves_independent_maturity(
    case: OperationalContainmentCase,
) -> None:
    """Containment follows the approved action without changing agent maturity."""
    failure_plan = FakeFailurePlan(fail_audit=not case.audit_persists)
    repositories = DeterministicAdoptionRepositories(failure_plan)
    service = OperationalContainmentService(
        repositories.release_decisions,
        repositories.maturity,
        repositories.audit,
        clock=lambda: _NOW,
    )
    prior_states = _maturity_states(case)
    for state in prior_states:
        persisted = repositories.maturity.append(state)
        assert persisted.is_success

    prior_evidence = _maturity_evidence(prior_states)
    if case.provider_failure:
        result = service.disable_pack_for_provider_failure(
            _organization(case),
            _pack(case),
            immutable_version=_VERSION,
            maturity_states=prior_states,
            failure_reference=f"provider-failure:property-26:{case.case_id}",
            correlation_id=_correlation(case),
        )
        expected_action = CapacityAction.DISABLE
        expected_status = PackOperationalStatus.DISABLED
        expected_applied = True
    else:
        result = service.apply_capacity_action(
            _organization(case),
            _pack(case),
            observed_load=case.observed_load,
            approved_load_limit=case.approved_load_limit,
            action=case.action,
            immutable_version=_VERSION,
            maturity_states=prior_states,
            correlation_id=_correlation(case),
        )
        exceeded = case.observed_load > case.approved_load_limit
        expected_action = case.action
        expected_status = (
            PackOperationalStatus.DISABLED
            if exceeded and case.action is CapacityAction.DISABLE
            else PackOperationalStatus.THROTTLED
            if exceeded
            else PackOperationalStatus.ENABLED
        )
        expected_applied = exceeded

    assert result.is_success and result.value is not None
    containment = result.value
    assert containment.action is expected_action
    assert containment.operational_status is expected_status
    assert containment.applied is expected_applied
    assert containment.disabled is (expected_status is PackOperationalStatus.DISABLED)
    assert _maturity_evidence(containment.maturity_states) == prior_evidence
    assert tuple(state.agent_id for state in containment.maturity_states) == tuple(
        state.agent_id for state in prior_states
    )
    assert containment.audit_recorded is (case.audit_persists if expected_applied else None)
    if expected_status is PackOperationalStatus.DISABLED:
        assert all(not state.pack_operational for state in containment.maturity_states)
    else:
        assert all(state.pack_operational for state in containment.maturity_states)

    persisted_states = repositories.maturity.records()
    assert _maturity_evidence(persisted_states) == prior_evidence
