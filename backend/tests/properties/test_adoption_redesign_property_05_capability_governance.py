"""Property checks for undeclared tool and outbound capability containment."""

from __future__ import annotations

from dataclasses import dataclass, field

from hypothesis import given, settings, strategies as st

from app.governance.authorization import (
    ApprovalState,
    AuthorizationConstraint,
    AuthorizationContext,
    AuthorizationDecision,
    AuthorizationService,
    ScopeConstraint,
)


@dataclass(frozen=True)
class _CapabilityCase:
    """Generated allow-lists with guaranteed-absent capability requests."""

    context: AuthorizationContext
    allowed_tool_ids: frozenset[str]
    absent_tool_ids: tuple[str, ...]
    allowed_destinations: frozenset[str]
    absent_destinations: tuple[str, ...]


@dataclass
class _DeterministicCapabilityGateway:
    """A local effect fake that records only capabilities admitted by governance."""

    authorization_service: AuthorizationService
    tool_effects: list[str] = field(default_factory=list)
    outbound_effects: list[str] = field(default_factory=list)

    def request_tool(self, context: AuthorizationContext, tool_id: str) -> AuthorizationDecision:
        """Record a tool effect only after the real authorization intersection permits it."""
        decision = self.authorization_service.evaluate(context, tool_id)
        if decision.permitted:
            self.tool_effects.append(tool_id)
        return decision

    def request_outbound(
        self, context: AuthorizationContext, destination: str
    ) -> AuthorizationDecision:
        """Record an outbound effect only after the real destination gate permits it."""
        decision = self.authorization_service.authorize_outbound(context, destination)
        if decision.permitted:
            self.outbound_effects.append(destination)
        return decision


@st.composite
def _capability_cases(draw: st.DrawFn) -> _CapabilityCase:
    """Generate bounded allow-lists and disjoint absent capability identifiers."""
    case_id = draw(st.integers(min_value=0, max_value=1_000))
    allowed_tool_numbers = draw(
        st.lists(st.integers(min_value=0, max_value=20), min_size=0, max_size=5, unique=True)
    )
    absent_tool_numbers = draw(
        st.lists(st.integers(min_value=0, max_value=20), min_size=1, max_size=5, unique=True)
    )
    allowed_destination_numbers = draw(
        st.lists(st.integers(min_value=0, max_value=20), min_size=0, max_size=5, unique=True)
    )
    absent_destination_numbers = draw(
        st.lists(st.integers(min_value=0, max_value=20), min_size=1, max_size=5, unique=True)
    )

    allowed_tool_ids = frozenset(f"tool-{number}" for number in allowed_tool_numbers)
    absent_tool_ids = tuple(f"undeclared-tool-{number}" for number in absent_tool_numbers)
    allowed_destinations = frozenset(
        f"service-{number}.example.test" for number in allowed_destination_numbers
    )
    absent_destinations = tuple(
        f"undeclared-{number}.example.test" for number in absent_destination_numbers
    )
    all_tool_ids = allowed_tool_ids | frozenset(absent_tool_ids)
    context = AuthorizationContext(
        agent_id=f"agent-{case_id}",
        step_id=f"step-{case_id}",
        organization_id=f"org-{case_id}",
        actor_id=f"actor-{case_id}",
        correlation_id=f"property-5-{case_id}",
        agent_allowed_tools=all_tool_ids,
        step_declared_tools=allowed_tool_ids,
        role_allowed_tools=all_tool_ids,
        organization_allowed_tools=all_tool_ids,
        risk_allowed_tools=all_tool_ids,
        approval_state=ApprovalState.NOT_REQUIRED,
        declared_outbound_destinations=allowed_destinations,
        declared_tool_ids=allowed_tool_ids,
    )
    return _CapabilityCase(
        context,
        allowed_tool_ids,
        absent_tool_ids,
        allowed_destinations,
        absent_destinations,
    )


# Feature: adoption-redesign, Property 5: Undeclared capabilities cannot escape governance
# **Validates: Requirements 3.5, 3.7**
@settings(max_examples=100, deadline=None)
@given(capability_case=_capability_cases())
def test_property_5_undeclared_capabilities_cannot_escape_governance(
    capability_case: _CapabilityCase,
) -> None:
    """Every absent tool and destination is denied before the deterministic effect fake runs."""
    gateway = _DeterministicCapabilityGateway(AuthorizationService())

    for tool_id in capability_case.allowed_tool_ids:
        assert gateway.request_tool(capability_case.context, tool_id).permitted
    for destination in capability_case.allowed_destinations:
        assert gateway.request_outbound(capability_case.context, destination).permitted

    for tool_id in capability_case.absent_tool_ids:
        decision = gateway.request_tool(capability_case.context, tool_id)
        assert not decision.permitted
        assert AuthorizationConstraint.STEP_DECLARED_TOOLS in decision.denied_constraints

    for destination in capability_case.absent_destinations:
        decision = gateway.request_outbound(capability_case.context, destination)
        assert not decision.permitted
        assert ScopeConstraint.OUTBOUND_DESTINATION in decision.denied_constraints

    assert sorted(gateway.tool_effects) == sorted(capability_case.allowed_tool_ids)
    assert sorted(gateway.outbound_effects) == sorted(capability_case.allowed_destinations)
