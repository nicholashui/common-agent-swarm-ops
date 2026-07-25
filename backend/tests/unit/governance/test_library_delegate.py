"""Focused checks for the sole governed library-delegation boundary."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import pytest

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

_ORGANIZATION = OrganizationId("org-1")
_CORRELATION = CorrelationId("corr-1")
_TOOL = "crm.lookup"


@dataclass
class _InvocationSpy:
    invocations: list[GovernedLibraryInvocation] = field(default_factory=list)

    def invoke(self, invocation: GovernedLibraryInvocation) -> Result[str, ErrorDetail]:
        self.invocations.append(invocation)
        return Result.success(f"{invocation.operation.value}-complete")


def _context(
    *,
    contract_tools: frozenset[str] | None = frozenset({_TOOL}),
    organization_tools: frozenset[str] | None = frozenset({_TOOL}),
) -> ServerHeldLibraryContext:
    return ServerHeldLibraryContext(
        organization_id=_ORGANIZATION,
        actor_id=ActorId("actor-1"),
        correlation_id=_CORRELATION,
        permissions=frozenset({"runs:write"}),
        organization_allowed_tool_ids=organization_tools,
        published_agent_versions=(PublishedAgentVersionData("agent-v1", contract_tools),),
    )


def _request(
    operation: GovernedOperation,
    adapter_kind: DispatchAdapterKind,
    *,
    context: ServerHeldLibraryContext | None = None,
    supplied_values: dict[str, object] | None = None,
    source: SuppliedValueSource = SuppliedValueSource.CLIENT,
) -> GovernedLibraryRequest:
    return GovernedLibraryRequest(
        operation=operation,
        adapter_kind=adapter_kind,
        context=context or _context(),
        subject=ImmutableRunSubject(_ORGANIZATION, "run-1", ("agent-v1",)),
        arguments={"server_record": "record-1"},
        supplied_values=supplied_values or {},
        supplied_value_source=source,
    )


@pytest.mark.parametrize("operation", tuple(GovernedOperation))
@pytest.mark.parametrize("adapter_kind", tuple(DispatchAdapterKind))
def test_every_operation_and_adapter_kind_uses_the_matching_library_service(
    operation: GovernedOperation, adapter_kind: DispatchAdapterKind
) -> None:
    """Create/dispatch/resume/evaluate/evolve/retrieve preserve one governed path."""
    spy = _InvocationSpy()
    service = BoundLibraryService(operation, spy.invoke)
    services = {operation: service}
    adapter = (
        LocalInlineGovernedAdapter(GovernedLibraryDelegate(), services)
        if adapter_kind is DispatchAdapterKind.LOCAL_INLINE
        else RemoteGovernedAdapter(GovernedLibraryDelegate(), services)
    )

    result = adapter.dispatch(_request(operation, adapter_kind, supplied_values={"tool_id": _TOOL}))

    assert result.is_success and result.value == f"{operation.value}-complete"
    assert len(spy.invocations) == 1
    invocation = spy.invocations[0]
    assert invocation.context.actor_id == ActorId("actor-1")
    assert invocation.context.organization_id == _ORGANIZATION
    assert invocation.subject.pinned_agent_version_ids == ("agent-v1",)
    assert invocation.approved_tool_ids == frozenset({_TOOL})


@pytest.mark.parametrize(
    ("contract_tools", "organization_tools", "should_delegate"),
    [
        (frozenset({_TOOL}), frozenset({_TOOL}), True),
        (frozenset(), frozenset({_TOOL}), False),
        (frozenset({_TOOL}), frozenset(), False),
        (None, frozenset({_TOOL}), False),
        (frozenset({_TOOL}), None, False),
    ],
    ids=(
        "allowed-in-both",
        "absent-from-published-contract",
        "absent-from-organization-policy",
        "indeterminate-published-contract",
        "indeterminate-organization-policy",
    ),
)
def test_adapter_response_tool_membership_requires_conclusive_dual_allowlisting(
    contract_tools: frozenset[str] | None,
    organization_tools: frozenset[str] | None,
    should_delegate: bool,
) -> None:
    """Adapter-supplied tools dispatch only with conclusive dual membership."""
    spy = _InvocationSpy()
    request = _request(
        GovernedOperation.DISPATCH,
        DispatchAdapterKind.LOCAL_INLINE,
        context=_context(
            contract_tools=contract_tools,
            organization_tools=organization_tools,
        ),
        supplied_values={"adapter_id": _TOOL},
        source=SuppliedValueSource.ADAPTER_RESPONSE,
    )

    result = GovernedLibraryDelegate().delegate(
        request,
        BoundLibraryService(GovernedOperation.DISPATCH, spy.invoke),
    )

    if should_delegate:
        assert result.is_success
        assert len(spy.invocations) == 1
        assert spy.invocations[0].approved_tool_ids == frozenset({_TOOL})
    else:
        assert not result.is_success
        assert result.error is not None and result.error.code is ErrorCode.AUTHORIZATION_DENIED
        assert spy.invocations == []


def test_effectful_tool_dispatch_forwards_complete_server_held_context() -> None:
    """The existing service receives server-held identity, policy, and version data unchanged."""
    context = ServerHeldLibraryContext(
        organization_id=_ORGANIZATION,
        actor_id=ActorId("actor-server-held"),
        correlation_id=CorrelationId("corr-server-held"),
        permissions=frozenset({"runs:write", "tools:execute"}),
        organization_allowed_tool_ids=frozenset({_TOOL, "docs.read"}),
        published_agent_versions=(
            PublishedAgentVersionData("agent-v1", frozenset({_TOOL})),
            PublishedAgentVersionData("unrelated-agent-v1", frozenset({"docs.read"})),
        ),
    )
    spy = _InvocationSpy()

    result = GovernedLibraryDelegate().delegate(
        _request(
            GovernedOperation.DISPATCH,
            DispatchAdapterKind.REMOTE,
            context=context,
            supplied_values={"tool_id": _TOOL},
        ),
        BoundLibraryService(GovernedOperation.DISPATCH, spy.invoke),
    )

    assert result.is_success
    assert len(spy.invocations) == 1
    invocation = spy.invocations[0]
    assert invocation.context is context
    assert invocation.context.permissions == frozenset({"runs:write", "tools:execute"})
    assert invocation.context.organization_allowed_tool_ids == frozenset({_TOOL, "docs.read"})
    assert invocation.context.published_agent_versions == context.published_agent_versions


def test_local_inline_adapter_preserves_existing_library_failure_contract() -> None:
    """Local-inline dispatch forwards the exact existing-library result without adaptation."""
    invocations: list[GovernedLibraryInvocation] = []
    existing_failure: Result[object, ErrorDetail] = Result.failure(
        ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "Existing library validation failed.",
            _CORRELATION,
        )
    )

    def execute_existing_service(
        invocation: GovernedLibraryInvocation,
    ) -> Result[object, ErrorDetail]:
        invocations.append(invocation)
        return existing_failure

    adapter = LocalInlineGovernedAdapter(
        GovernedLibraryDelegate(),
        {
            GovernedOperation.EVALUATE: BoundLibraryService(
                GovernedOperation.EVALUATE,
                execute_existing_service,
            )
        },
    )

    result = adapter.dispatch(
        _request(
            GovernedOperation.EVALUATE,
            DispatchAdapterKind.LOCAL_INLINE,
            supplied_values={"tool_id": _TOOL},
        )
    )

    assert result is existing_failure
    assert len(invocations) == 1
    assert invocations[0].operation is GovernedOperation.EVALUATE
    assert invocations[0].adapter_kind is DispatchAdapterKind.LOCAL_INLINE


@pytest.mark.parametrize(
    "supplied_values",
    [
        {"credential": "secret-value"},
        {"target": "https://example.test/run"},
        {"instruction": "execute arbitrary code"},
        {"organization_id": "other-org"},
        {"payload": lambda: None},
        {"tool_id": "unknown.tool"},
    ],
)
@pytest.mark.parametrize("adapter_kind", tuple(DispatchAdapterKind))
def test_all_untrusted_authority_shapes_fail_closed_for_local_and_remote_adapters(
    supplied_values: dict[str, object], adapter_kind: DispatchAdapterKind
) -> None:
    """Client, graph, adapter, and untrusted values cannot acquire dispatch authority."""
    spy = _InvocationSpy()
    service = BoundLibraryService(GovernedOperation.DISPATCH, spy.invoke)
    adapter = (
        LocalInlineGovernedAdapter(GovernedLibraryDelegate(), {GovernedOperation.DISPATCH: service})
        if adapter_kind is DispatchAdapterKind.LOCAL_INLINE
        else RemoteGovernedAdapter(GovernedLibraryDelegate(), {GovernedOperation.DISPATCH: service})
    )

    result = adapter.dispatch(
        _request(
            GovernedOperation.DISPATCH,
            adapter_kind,
            supplied_values=supplied_values,
            source=SuppliedValueSource.UNTRUSTED_CONTENT,
        )
    )

    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert spy.invocations == []


def test_adapter_kind_and_operation_cannot_be_substituted() -> None:
    """An adapter cannot redirect a validated request to another transport or service."""
    spy = _InvocationSpy()
    service = BoundLibraryService(GovernedOperation.CREATE, spy.invoke)
    local = LocalInlineGovernedAdapter(
        GovernedLibraryDelegate(), {GovernedOperation.CREATE: service}
    )
    request = _request(GovernedOperation.CREATE, DispatchAdapterKind.REMOTE)

    wrong_transport = local.dispatch(request)
    wrong_operation = GovernedLibraryDelegate().delegate(
        replace(request, adapter_kind=DispatchAdapterKind.LOCAL_INLINE),
        BoundLibraryService(GovernedOperation.RESUME, spy.invoke),
    )

    assert not wrong_transport.is_success
    assert not wrong_operation.is_success
    assert spy.invocations == []
