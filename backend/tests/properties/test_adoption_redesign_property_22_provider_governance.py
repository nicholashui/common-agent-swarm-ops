"""Property checks for provider authorization and fail-closed execution."""

# The required specification comment exceeds the repository's line-length limit.
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from hypothesis import example, given, settings, strategies as st

from app.governance.adapter_execution import (
    ProviderAdapterDeclaration,
    ProviderDenialReason,
)
from app.governance.operation_guard import OperationGuard
from tests.fakes.provider import MockProviderAdapter, ProviderFailureMode

_PROVIDER_ID = "provider-property-22"
_CAPABILITY = "text.generate"
_COST_LIMIT = 1


class ProviderOutcome(StrEnum):
    """Bounded provider outcomes exercised by the governance boundary."""

    SUCCESS = "success"
    TIMEOUT = "timeout"
    UNSAFE_RESULT = "unsafe_result"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ProviderGovernanceCase:
    """Generated declaration presence and provider outcome for one action."""

    case_id: int
    declaration_present: bool
    field_presence: tuple[bool, bool, bool, bool, bool]
    outcome: ProviderOutcome


_FIELD_NAMES = (
    "capability",
    "cost_limit",
    "retention_policy",
    "residency",
    "safety_policy",
)
_FIELD_FAILURES = (
    ProviderDenialReason.MISSING_CAPABILITY_DECLARATION,
    ProviderDenialReason.MISSING_COST_DECLARATION,
    ProviderDenialReason.MISSING_RETENTION_DECLARATION,
    ProviderDenialReason.MISSING_RESIDENCY_DECLARATION,
    ProviderDenialReason.MISSING_SAFETY_DECLARATION,
)
_OUTCOME_REASONS = {
    ProviderOutcome.TIMEOUT: ProviderDenialReason.PROVIDER_TIMEOUT,
    ProviderOutcome.UNSAFE_RESULT: ProviderDenialReason.UNSAFE_PROVIDER_RESULT,
    ProviderOutcome.BUDGET_EXCEEDED: ProviderDenialReason.PROVIDER_BUDGET_EXCEEDED,
    ProviderOutcome.UNAVAILABLE: ProviderDenialReason.PROVIDER_UNAVAILABLE,
}


@st.composite
def _provider_governance_cases(draw: st.DrawFn) -> ProviderGovernanceCase:
    """Generate bounded declaration vectors and deterministic provider outcomes."""
    return ProviderGovernanceCase(
        case_id=draw(st.integers(min_value=0, max_value=9_999)),
        declaration_present=draw(st.booleans()),
        field_presence=draw(
            st.tuples(
                st.booleans(),
                st.booleans(),
                st.booleans(),
                st.booleans(),
                st.booleans(),
            )
        ),
        outcome=draw(st.sampled_from(tuple(ProviderOutcome))),
    )


def _case(
    *,
    declaration_present: bool = True,
    missing_field: int | None = None,
    outcome: ProviderOutcome = ProviderOutcome.SUCCESS,
) -> ProviderGovernanceCase:
    """Build a small explicit boundary case for every governance branch."""
    fields = [True] * len(_FIELD_NAMES)
    if missing_field is not None:
        fields[missing_field] = False
    return ProviderGovernanceCase(
        case_id=0,
        declaration_present=declaration_present,
        field_presence=tuple(fields),  # type: ignore[arg-type]
        outcome=outcome,
    )


def _declaration(case: ProviderGovernanceCase) -> ProviderAdapterDeclaration | None:
    """Build the declaration represented by the generated presence vector."""
    if not case.declaration_present:
        return None
    field_values: dict[str, object] = {
        "capability": _CAPABILITY,
        "cost_limit": _COST_LIMIT,
        "retention_policy": "reference_only",
        "residency": "test-local",
        "safety_policy": "deny-on-unsafe",
    }
    for name, present in zip(_FIELD_NAMES, case.field_presence, strict=True):
        if not present:
            field_values[name] = None
    return ProviderAdapterDeclaration(
        provider_id=_PROVIDER_ID,
        capability=field_values["capability"],  # type: ignore[arg-type]
        cost_limit=field_values["cost_limit"],  # type: ignore[arg-type]
        retention_policy=field_values["retention_policy"],  # type: ignore[arg-type]
        residency=field_values["residency"],  # type: ignore[arg-type]
        safety_policy=field_values["safety_policy"],  # type: ignore[arg-type]
    )


def _provider(case: ProviderGovernanceCase) -> MockProviderAdapter:
    """Configure a local fake without contacting an external provider."""
    failure_mode = {
        ProviderOutcome.TIMEOUT: ProviderFailureMode.TIMEOUT,
        ProviderOutcome.UNSAFE_RESULT: ProviderFailureMode.UNSAFE_RESULT,
        ProviderOutcome.UNAVAILABLE: ProviderFailureMode.UNAVAILABLE,
    }.get(case.outcome)
    provider = MockProviderAdapter(_PROVIDER_ID, _CAPABILITY)
    provider.set_failure_mode(failure_mode)
    return provider


# Feature: adoption-redesign, Property 22: Provider authorization and failures fail closed
# **Validates: Requirements 8.8, 8.9, 9.1**
@settings(max_examples=100, deadline=None)
@example(case=_case(declaration_present=False))
@example(case=_case(missing_field=0))
@example(case=_case(missing_field=1))
@example(case=_case(missing_field=2))
@example(case=_case(missing_field=3))
@example(case=_case(missing_field=4))
@example(case=_case(outcome=ProviderOutcome.TIMEOUT))
@example(case=_case(outcome=ProviderOutcome.UNSAFE_RESULT))
@example(case=_case(outcome=ProviderOutcome.BUDGET_EXCEEDED))
@example(case=_case(outcome=ProviderOutcome.UNAVAILABLE))
@given(case=_provider_governance_cases())
def test_property_22_provider_authorization_and_faults_fail_closed(
    case: ProviderGovernanceCase,
) -> None:
    """Only complete declarations and fault-free outcomes can reach the provider."""
    declaration = _declaration(case)
    provider = _provider(case)
    requested_cost = 2 if case.outcome is ProviderOutcome.BUDGET_EXCEEDED else _COST_LIMIT

    result = OperationGuard().execute_provider(
        provider,
        declaration,
        {"input_reference": f"reference:property-22:{case.case_id}"},
        requested_cost=requested_cost,
    )

    declaration_complete = case.declaration_present and all(case.field_presence)
    assert result.authorization.permitted is declaration_complete

    if not declaration_complete:
        assert not result.allowed
        assert not result.invoked
        assert not provider.calls
        if declaration is None:
            assert ProviderDenialReason.MISSING_DOMAIN_PACK_DECLARATION in (
                result.authorization.denied_reasons
            )
        else:
            missing_reasons = {
                reason
                for present, reason in zip(case.field_presence, _FIELD_FAILURES, strict=True)
                if not present
            }
            assert missing_reasons <= set(result.authorization.denied_reasons)
        return

    if case.outcome is ProviderOutcome.SUCCESS:
        assert result.allowed
        assert result.invoked
        assert result.denial_reasons == ()
        assert len(provider.calls) == 1
    else:
        expected_reason = _OUTCOME_REASONS[case.outcome]
        assert not result.allowed
        assert not result.invoked
        assert result.denial_reasons == (expected_reason,)
        assert not provider.calls
