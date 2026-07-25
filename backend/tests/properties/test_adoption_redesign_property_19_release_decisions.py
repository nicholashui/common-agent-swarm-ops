"""Property checks for coverage-aware release decisions and evidence retention."""

# The required specification comment exceeds the repository's line-length limit.
# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.evaluation.verification_suite import VerificationSuite
from app.evidence.release_evidence import (
    InMemoryReleaseEvidenceRepository,
    VerificationOutcome,
)
from app.models.control_plane import ReleaseReadinessStatus, VerificationCoverageStatus
from app.models.identifiers import CorrelationId, DomainPackId, OrganizationId
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-property-19")
_PACK = DomainPackId("pack-property-19")
_CORRELATION = CorrelationId("correlation-property-19")


@dataclass(frozen=True, slots=True)
class ReleaseDecisionCase:
    """Bounded verification results and an independent failure-write outcome."""

    integration_results: tuple[bool, ...]
    post_coverage_results: tuple[bool, ...]
    failure_persistence_available: bool


@st.composite
def _release_decision_cases(draw: st.DrawFn) -> ReleaseDecisionCase:
    """Generate bounded result sequences with at least one post-coverage failure."""
    integration_results = draw(st.lists(st.booleans(), min_size=1, max_size=3).map(tuple))
    post_count = draw(st.integers(min_value=1, max_value=3))
    failed_index = draw(st.integers(min_value=0, max_value=post_count - 1))
    post_results = list(draw(st.lists(st.booleans(), min_size=post_count, max_size=post_count)))
    post_results[failed_index] = False
    return ReleaseDecisionCase(
        integration_results=integration_results,
        post_coverage_results=tuple(post_results),
        failure_persistence_available=draw(st.booleans()),
    )


def _checks(prefix: str, outcomes: tuple[bool, ...]) -> tuple[tuple[str, bool], ...]:
    """Name a generated sequence for stable, referenceable evidence records."""
    return tuple((f"{prefix}.{index}", outcome) for index, outcome in enumerate(outcomes))


# Feature: adoption-redesign, Property 19: Release decisions respect coverage state and preserve evidence
# **Validates: Requirements 7.7, 7.8, 7.10**
@settings(max_examples=100, deadline=None)
@example(
    case=ReleaseDecisionCase(
        integration_results=(True,),
        post_coverage_results=(False,),
        failure_persistence_available=True,
    )
)
@example(
    case=ReleaseDecisionCase(
        integration_results=(False, True),
        post_coverage_results=(False, True),
        failure_persistence_available=False,
    )
)
@given(case=_release_decision_cases())
def test_property_19_release_decisions_respect_coverage_and_preserve_evidence(
    case: ReleaseDecisionCase,
) -> None:
    """Post-coverage failures fail release; pre-coverage failures do not fail release."""
    repositories = DeterministicAdoptionRepositories()
    evidence = InMemoryReleaseEvidenceRepository(
        fail_failure_persistence=not case.failure_persistence_available
    )
    suite = VerificationSuite(
        verification_repository=repositories.verifications,
        release_repository=repositories.release_decisions,
        evidence_repository=evidence,
        clock=lambda: _NOW,
    )

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        pack_id=_PACK,
        immutable_version="1.0.0",
        pack_contract_version="1.0.0",
        host_contract_version="1.0.0",
        alc_version="1.0.0",
        integration_checks=_checks("integration", case.integration_results),
        post_coverage_checks=_checks("post-coverage", case.post_coverage_results),
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    integration_complete = all(case.integration_results)
    assert bundle.coverage_status is (
        VerificationCoverageStatus.COMPLETE
        if integration_complete
        else VerificationCoverageStatus.INCOMPLETE
    )

    all_results = bundle.check_results
    assert len(all_results) == len(case.integration_results) + len(case.post_coverage_results)
    assert tuple(result.layer.value for result in all_results[: len(case.integration_results)]) == (
        "integration",
    ) * len(case.integration_results)
    assert tuple(record.outcome for record in evidence.check_results()) == tuple(
        VerificationOutcome.PASS if outcome else VerificationOutcome.FAIL
        for outcome in (*case.integration_results, *case.post_coverage_results)
    )

    integration_results = tuple(
        record for record in all_results if record.layer.value == "integration"
    )
    assert len(integration_results) == len(case.integration_results)
    assert bundle.verification_run.integration_evidence_references == tuple(
        str(record.evidence_id) for record in integration_results
    )

    failure_count = sum(
        not outcome for outcome in (*case.integration_results, *case.post_coverage_results)
    )
    if case.failure_persistence_available:
        assert len(bundle.failure_records) == failure_count
        assert bundle.failure_persistence_errors == ()
    else:
        assert bundle.failure_records == ()
        assert len(bundle.failure_persistence_errors) == failure_count

    if integration_complete:
        assert bundle.release_decision is not None
        assert bundle.release_decision.status is ReleaseReadinessStatus.FAILED
        assert bundle.release_decision.integration_coverage_complete
        assert bundle.release_decision.failure_evidence_references
        assert bundle.release_decision in repositories.release_decisions.records()
        assert bundle.verification_run.coverage_status is VerificationCoverageStatus.COMPLETE
        assert all(record.passed for record in integration_results)
    else:
        assert bundle.release_decision is None
        assert repositories.release_decisions.records() == ()
        assert bundle.verification_run.coverage_status is VerificationCoverageStatus.INCOMPLETE
