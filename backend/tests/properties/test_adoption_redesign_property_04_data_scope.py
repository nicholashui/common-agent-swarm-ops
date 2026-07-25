"""Property checks for complete-scope data-access authorization."""

from __future__ import annotations

from dataclasses import dataclass, replace

from hypothesis import given, settings, strategies as st

from app.governance.authorization import (
    ApprovalState,
    AuthorizationContext,
    AuthorizationDecision,
    AuthorizationService,
    DataAccessRequest,
    ScopeConstraint,
)
from app.models.common import CompatibilityRange


@dataclass(frozen=True)
class _ScopeCase:
    """Generated approved scope and one independently escaped request per boundary."""

    context: AuthorizationContext
    approved_request: DataAccessRequest
    escaped_requests: tuple[tuple[ScopeConstraint, DataAccessRequest], ...]


@dataclass
class _DeterministicMemoryStore:
    """A local data fake that returns records only after complete authorization."""

    authorization_service: AuthorizationService
    reads: list[DataAccessRequest]

    def read(
        self, context: AuthorizationContext, request: DataAccessRequest
    ) -> tuple[AuthorizationDecision, tuple[str, ...]]:
        """Apply the real scope gate before exposing deterministic data."""
        decision = self.authorization_service.authorize_data_access(context, request)
        if not decision.permitted:
            return decision, ()
        self.reads.append(request)
        return decision, ("scope-bound-record",)


def _version(patch: int) -> str:
    """Return a bounded semantic version for generated pack ranges."""
    return f"1.0.{patch}"


@st.composite
def _scope_cases(draw: st.DrawFn) -> _ScopeCase:
    """Generate one valid scope and guaranteed-distinct boundary escapes."""
    identifier = draw(st.integers(min_value=0, max_value=1000))
    minimum_patch = draw(st.integers(min_value=0, max_value=20))
    maximum_patch = draw(st.integers(min_value=minimum_patch, max_value=minimum_patch + 10))
    approved_patch = draw(st.integers(min_value=minimum_patch, max_value=maximum_patch))

    organization_id = f"org-approved-{identifier}"
    domain_id = f"domain-approved-{identifier}"
    agent_id = f"agent-approved-{identifier}"
    memory_scope = f"memory-approved-{identifier}"
    supported_pack_range = CompatibilityRange(_version(minimum_patch), _version(maximum_patch))
    context = AuthorizationContext(
        agent_id=agent_id,
        step_id=f"step-{identifier}",
        organization_id=organization_id,
        actor_id=f"actor-{identifier}",
        correlation_id=f"property-4-{identifier}",
        agent_allowed_tools=frozenset(),
        step_declared_tools=frozenset(),
        role_allowed_tools=frozenset(),
        organization_allowed_tools=frozenset(),
        risk_allowed_tools=frozenset(),
        approval_state=ApprovalState.NOT_REQUIRED,
        domain_id=domain_id,
        supported_pack_range=supported_pack_range,
        declared_memory_scopes=frozenset({memory_scope}),
    )
    approved_request = DataAccessRequest(
        organization_id=organization_id,
        domain_id=domain_id,
        pack_version=_version(approved_patch),
        agent_id=agent_id,
        memory_scope=memory_scope,
    )
    escaped_requests = (
        (
            ScopeConstraint.ORGANIZATION_SCOPE,
            replace(approved_request, organization_id=f"org-foreign-{identifier}"),
        ),
        (
            ScopeConstraint.DOMAIN_SCOPE,
            replace(approved_request, domain_id=f"domain-foreign-{identifier}"),
        ),
        (
            ScopeConstraint.PACK_VERSION_RANGE,
            replace(approved_request, pack_version=_version(maximum_patch + 1)),
        ),
        (
            ScopeConstraint.AGENT_IDENTITY,
            replace(approved_request, agent_id=f"agent-foreign-{identifier}"),
        ),
        (
            ScopeConstraint.MEMORY_SCOPE,
            replace(approved_request, memory_scope=f"memory-undeclared-{identifier}"),
        ),
    )
    return _ScopeCase(context, approved_request, escaped_requests)


# Feature: adoption-redesign, Property 4: Data access remains within every declared scope
# **Validates: Requirements 3.1, 3.2, 7.3**
@settings(max_examples=100, deadline=None)
@given(scope_case=_scope_cases())
def test_property_4_data_access_requires_complete_declared_scope(
    scope_case: _ScopeCase,
) -> None:
    """Every scope dimension is required before the deterministic fake returns data."""
    authorization_service = AuthorizationService()
    store = _DeterministicMemoryStore(authorization_service, [])

    approved_decision, records = store.read(scope_case.context, scope_case.approved_request)
    assert approved_decision.permitted
    assert records == ("scope-bound-record",)

    for constraint, escaped_request in scope_case.escaped_requests:
        denied_decision, denied_records = store.read(scope_case.context, escaped_request)
        assert not denied_decision.permitted
        assert constraint in denied_decision.denied_constraints
        assert denied_records == ()

    assert store.reads == [scope_case.approved_request]
