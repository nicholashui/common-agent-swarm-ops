"""Property tests for complete, independent, fail-closed tool authorization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace

import pytest
from hypothesis import given, settings, strategies as st

from app.audit import AuditWriter
from app.governance.authorization import (
    ApprovalState,
    AuthorizationConstraint,
    AuthorizationContext,
    ToolInputValue,
)
from app.governance.tool_broker import HostToolBroker, LocalAdapterResult, ToolRequest
from tests.fakes.broker import InMemoryAuditRepository, authorized_context

# Feature: generic-swarm-business-os, Property 13: Tool authorization is complete, independent,
# and fail-closed.
# **Validates: Requirements 5.1, 5.2, 5.3, 5.5**


@dataclass
class RecordingLocalAdapter:
    """Deterministic local adapter that exposes invocations for broker assertions."""

    adapter_id: str
    version: str = "test-v1"
    local_only: bool = True
    invocations: list[Mapping[str, ToolInputValue]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


@pytest.mark.parametrize("denied_constraint", tuple(AuthorizationConstraint))
@settings(max_examples=100, deadline=None)
@given(
    tool_suffixes=st.lists(
        st.integers(min_value=0, max_value=9_999), min_size=3, max_size=8, unique=True
    ),
    denial_offset=st.integers(min_value=1, max_value=6),
)
def test_distinct_tool_call_sequences_evaluate_every_constraint_independently(
    denied_constraint: AuthorizationConstraint,
    tool_suffixes: list[int],
    denial_offset: int,
) -> None:
    """A prior permitted call cannot bypass a later call's full intersection check."""
    adapter_ids = tuple(f"local.tool{suffix}" for suffix in tool_suffixes)
    denied_index = 1 + denial_offset % (len(adapter_ids) - 2)
    adapters = tuple(RecordingLocalAdapter(adapter_id) for adapter_id in adapter_ids)
    audit_repository = InMemoryAuditRepository()
    broker = HostToolBroker(adapters, AuditWriter(audit_repository))
    permitted_context = authorized_context(adapter_ids)

    for index, adapter_id in enumerate(adapter_ids):
        context = (
            _context_denied_by(permitted_context, denied_constraint)
            if index == denied_index
            else permitted_context
        )
        result = broker.request_tool(ToolRequest(adapter_id, {"sequence": index}), context)

        if index == denied_index:
            assert not result.allowed
            assert not result.invoked
            assert result.effect is None
            assert result.authorization.denied_constraints == (denied_constraint,)
            assert result.denial_audit_recorded is True
        else:
            assert result.allowed
            assert result.invoked
            assert result.effect is not None
            assert result.authorization.denied_constraints == ()

    assert len(set(adapter_ids)) == len(adapter_ids)
    assert sum(len(adapter.invocations) for adapter in adapters) == len(adapter_ids) - 1
    assert len(audit_repository.events) == 1


def _context_denied_by(
    context: AuthorizationContext,
    constraint: AuthorizationConstraint,
) -> AuthorizationContext:
    """Return a context that fails exactly one authorization factor."""
    if constraint is AuthorizationConstraint.AGENT_ALLOWED_TOOLS:
        return replace(context, agent_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.STEP_DECLARED_TOOLS:
        return replace(context, step_declared_tools=frozenset())
    if constraint is AuthorizationConstraint.ROLE_PERMISSIONS:
        return replace(context, role_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.ORGANIZATION_SCOPE:
        return replace(context, organization_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.RISK_POLICY:
        return replace(context, risk_allowed_tools=frozenset())
    return replace(context, approval_state=ApprovalState.PENDING)
