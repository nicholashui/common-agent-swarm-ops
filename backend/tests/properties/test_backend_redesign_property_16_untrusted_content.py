"""Property checks for fail-complete untrusted-content processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count
from typing import cast

from hypothesis import given, settings, strategies as st

from app.core.ingress import (
    GuardedUntrustedContent,
    ProhibitedInfluence,
    ProtectionOutcome,
    SecurityIndicator,
    UntrustedContent,
    UntrustedContentGuard,
    UntrustedContentSource,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord, SecurityEvidence
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ImportRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-16-organization")
_CORRELATION = CorrelationId("property-16-correlation")
_DETECTION_INDICATORS = (
    SecurityIndicator.PROMPT_INJECTION,
    SecurityIndicator.PROHIBITED_CONTENT,
    SecurityIndicator.SUSPICIOUS_TOOL_PROPOSAL,
    SecurityIndicator.ARTIFACT_MANIFEST_MISMATCH,
)
_INFLUENCE_INDICATORS = {
    ProhibitedInfluence.GRANT_AUTHORITY: SecurityIndicator.AUTHORITY_INFLUENCE,
    ProhibitedInfluence.SELECT_TOOL: SecurityIndicator.TOOL_SELECTION,
    ProhibitedInfluence.CHANGE_POLICY: SecurityIndicator.POLICY_MUTATION,
    ProhibitedInfluence.BYPASS_VALIDATION: SecurityIndicator.VALIDATION_BYPASS,
    ProhibitedInfluence.PRIVILEGED_EXECUTABLE_INSTRUCTION: SecurityIndicator.PRIVILEGED_INSTRUCTION,
}
_PROTECTION_VECTORS = st.lists(
    st.tuples(
        st.booleans(),
        st.lists(st.sampled_from(_DETECTION_INDICATORS), unique=True, max_size=4),
    ),
    max_size=4,
)


@dataclass
class _EvidenceRepositorySpy:
    evidence: list[SecurityEvidence] = field(default_factory=list)

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import persistence is not used by this property.")

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import replacement is not used by this property.")

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import lookup is not used by this property.")

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, RepositoryError]:
        self.evidence.append(record)
        return Result.success(record)


@dataclass
class _ProtectionSpy:
    protection_id: str
    outcome: ProtectionOutcome
    calls: int = 0

    def inspect(self, content: UntrustedContent) -> ProtectionOutcome:
        self.calls += 1
        return self.outcome


@dataclass
class _ProtectedContinuationSpy:
    """Models a downstream effect that may run only with a guarded continuation token."""

    authority: str = "server-owned-authority"
    selected_tool: str = "server-allowlisted-tool"
    policy: str = "server-owned-policy"
    continuations: list[GuardedUntrustedContent] = field(default_factory=list)

    def continue_after_guard(
        self, outcome: Result[GuardedUntrustedContent, RepositoryError]
    ) -> None:
        if outcome.is_success and outcome.value is not None:
            self.continuations.append(outcome.value)


def _metadata() -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId("property-16-untrusted-content"),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


# Feature: backend-redesign, Property 16
# **Validates: Requirements 11.8, 11.9, 11.10, 11.11, 11.12**
@settings(max_examples=100)
@given(
    protection_vector=_PROTECTION_VECTORS,
    influence_attempts=st.frozensets(st.sampled_from(tuple(ProhibitedInfluence))),
    source=st.sampled_from(tuple(UntrustedContentSource)),
)
def test_property_16_untrusted_content_cannot_influence_authority_and_fails_complete(
    protection_vector: list[tuple[bool, list[SecurityIndicator]]],
    influence_attempts: frozenset[ProhibitedInfluence],
    source: UntrustedContentSource,
) -> None:
    """Only a clean protection vector receives a data-only continuation token."""
    protections = tuple(
        _ProtectionSpy(
            protection_id=f"protection-{index}",
            outcome=ProtectionOutcome(
                passed=passed,
                indicators=() if passed else tuple(indicators),
            ),
        )
        for index, (passed, indicators) in enumerate(protection_vector)
    )
    repository = _EvidenceRepositorySpy()
    identifiers = count(1)
    guard = UntrustedContentGuard(
        cast(ImportRepository, repository),
        protections,
        clock=lambda: _NOW,
        evidence_id_factory=lambda: f"property-16-evidence-{next(identifiers)}",
    )
    protected_state = _ProtectedContinuationSpy()
    content = UntrustedContent(
        metadata=_metadata(),
        source=source,
        payload={"untrusted_instruction": "bearer-raw-secret-must-not-be-retained"},
        influence_attempts=influence_attempts,
    )

    outcome = guard.process(content)
    protected_state.continue_after_guard(outcome)

    expected_evidence: list[tuple[str, str]] = [
        ("untrusted-boundary", _INFLUENCE_INDICATORS[influence].value)
        for influence in sorted(influence_attempts, key=lambda item: item.value)
    ]
    for index, (passed, indicators) in enumerate(protection_vector):
        if not passed:
            expected_evidence.extend(
                (f"protection-{index}", indicator.value)
                for indicator in (tuple(indicators) or (SecurityIndicator.PROTECTION_REJECTED,))
            )

    assert [protection.calls for protection in protections] == [1] * len(protections)
    assert protected_state.authority == "server-owned-authority"
    assert protected_state.selected_tool == "server-allowlisted-tool"
    assert protected_state.policy == "server-owned-policy"
    assert [(item.protection, item.indicator) for item in repository.evidence] == expected_evidence
    assert all(not item.passed for item in repository.evidence)
    assert "bearer-raw-secret-must-not-be-retained" not in repr(repository.evidence)

    if expected_evidence:
        assert not outcome.is_success
        assert outcome.value is None
        assert outcome.error is not None
        assert outcome.error.code is ErrorCode.VALIDATION_FAILED
        assert protected_state.continuations == []
        return

    assert outcome.is_success and outcome.value is not None
    assert repository.evidence == []
    assert protected_state.continuations == [outcome.value]
    assert not hasattr(outcome.value, "authority")
    assert not hasattr(outcome.value, "selected_tool")
    assert not hasattr(outcome.value, "policy")
