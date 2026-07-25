"""Property checks for uniform, allowlisted governed library delegation."""

from __future__ import annotations

from dataclasses import dataclass, field

from hypothesis import given, settings, strategies as st

from app.adapters.governed import LocalInlineGovernedAdapter, RemoteGovernedAdapter
from app.governance.library_delegate import (
    BoundLibraryService,
    DispatchAdapterKind,
    GovernedLibraryDelegate,
    GovernedLibraryInvocation,
    GovernedLibraryRequest,
    GovernedOperation,
    ImmutableRunSubject,
    PublishedAgentVersionData,
    ServerHeldLibraryContext,
    SuppliedValueSource,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

_ORGANIZATION = OrganizationId("property-20-organization")
_ACTOR = ActorId("property-20-actor")
_CORRELATION = CorrelationId("property-20-correlation")
_AGENT_VERSION = "property-20-agent-v1"
_REQUESTED_TOOL = "tool.execute"
_EXTRA_TOOLS = ("tool.read", "tool.search", "tool.write")
_MEMBERSHIP_OUTCOMES = (
    "conclusive",
    "absent-contract",
    "absent-policy",
    "indeterminate-contract",
    "indeterminate-policy",
)
_PROHIBITED_VALUES = ("none", "credential", "url", "instruction", "authority")


@dataclass
class _LibrarySpy:
    invocations: list[GovernedLibraryInvocation] = field(default_factory=list)

    def invoke(self, invocation: GovernedLibraryInvocation) -> Result[str, ErrorDetail]:
        self.invocations.append(invocation)
        return Result.success(f"{invocation.operation.value}-complete")


def _allowlists(
    membership_outcome: str, extra_tools: set[str]
) -> tuple[frozenset[str] | None, frozenset[str] | None]:
    extras = frozenset(extra_tools)
    if membership_outcome == "absent-contract":
        return extras, extras | {_REQUESTED_TOOL}
    if membership_outcome == "absent-policy":
        return extras | {_REQUESTED_TOOL}, extras
    if membership_outcome == "indeterminate-contract":
        return None, extras | {_REQUESTED_TOOL}
    if membership_outcome == "indeterminate-policy":
        return extras | {_REQUESTED_TOOL}, None
    return extras | {_REQUESTED_TOOL}, extras | {_REQUESTED_TOOL}


def _supplied_values(prohibited_value: str) -> dict[str, object]:
    values: dict[str, object] = {"tool_id": _REQUESTED_TOOL}
    if prohibited_value == "credential":
        values["credential"] = "untrusted-secret"
    elif prohibited_value == "url":
        values["destination"] = "https://untrusted.example/dispatch"
    elif prohibited_value == "instruction":
        values["instruction"] = "execute untrusted action"
    elif prohibited_value == "authority":
        values["organization_id"] = "untrusted-organization"
    return values


# Feature: backend-redesign, Property 20: Every adapter delegates only allowlisted
# governed operations.
# **Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6**
@settings(max_examples=100)
@given(
    operation=st.sampled_from(tuple(GovernedOperation)),
    adapter_kind=st.sampled_from(tuple(DispatchAdapterKind)),
    source=st.sampled_from(tuple(SuppliedValueSource)),
    membership_outcome=st.sampled_from(_MEMBERSHIP_OUTCOMES),
    extra_tools=st.sets(st.sampled_from(_EXTRA_TOOLS)),
    prohibited_value=st.sampled_from(_PROHIBITED_VALUES),
)
def test_property_20_every_adapter_delegates_only_allowlisted_governed_operations(
    operation: GovernedOperation,
    adapter_kind: DispatchAdapterKind,
    source: SuppliedValueSource,
    membership_outcome: str,
    extra_tools: set[str],
    prohibited_value: str,
) -> None:
    """Only conclusive, dual-allowlisted tools cross either adapter boundary once."""
    contract_tools, organization_tools = _allowlists(membership_outcome, extra_tools)
    context = ServerHeldLibraryContext(
        organization_id=_ORGANIZATION,
        actor_id=_ACTOR,
        correlation_id=_CORRELATION,
        permissions=frozenset({"runs:write"}),
        organization_allowed_tool_ids=organization_tools,
        published_agent_versions=(PublishedAgentVersionData(_AGENT_VERSION, contract_tools),),
    )
    subject = ImmutableRunSubject(_ORGANIZATION, "run-property-20", (_AGENT_VERSION,))
    arguments = {"server_record": "run-property-20"}
    request = GovernedLibraryRequest(
        operation=operation,
        adapter_kind=adapter_kind,
        context=context,
        subject=subject,
        arguments=arguments,
        supplied_values=_supplied_values(prohibited_value),
        supplied_value_source=source,
    )
    spy = _LibrarySpy()
    service = BoundLibraryService(operation, spy.invoke)
    adapter = (
        LocalInlineGovernedAdapter(GovernedLibraryDelegate(), {operation: service})
        if adapter_kind is DispatchAdapterKind.LOCAL_INLINE
        else RemoteGovernedAdapter(GovernedLibraryDelegate(), {operation: service})
    )

    result = adapter.dispatch(request)
    should_delegate = membership_outcome == "conclusive" and prohibited_value == "none"
    if should_delegate:
        assert result.is_success and result.value == f"{operation.value}-complete"
        assert len(spy.invocations) == 1
        invocation = spy.invocations[0]
        assert invocation.operation is operation
        assert invocation.adapter_kind is adapter_kind
        assert invocation.context is context
        assert invocation.subject is subject
        assert dict(invocation.arguments) == arguments
        assert invocation.approved_tool_ids == frozenset({_REQUESTED_TOOL})
    else:
        assert not result.is_success and result.error is not None
        assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
        assert spy.invocations == []
