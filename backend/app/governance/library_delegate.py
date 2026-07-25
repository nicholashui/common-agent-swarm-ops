"""Sole fail-closed port from dispatch adapters to existing library services."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol
from urllib.parse import urlsplit

from app.governance.authorization import is_safe_tool_identifier
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import ActorId, CorrelationId, OrganizationId


class GovernedOperation(StrEnum):
    """Run-related operations that may cross the library delegation boundary."""

    CREATE = "create"
    DISPATCH = "dispatch"
    RESUME = "resume"
    EVALUATE = "evaluate"
    EVOLVE = "evolve"
    RETRIEVE = "retrieve"


class DispatchAdapterKind(StrEnum):
    """Supported adapter transports; neither kind owns execution authority."""

    LOCAL_INLINE = "local-inline"
    REMOTE = "remote"


class SuppliedValueSource(StrEnum):
    """Untrusted origins whose values must never become server authority."""

    CLIENT = "client"
    GRAPH = "graph"
    ADAPTER_RESPONSE = "adapter-response"
    UNTRUSTED_CONTENT = "untrusted-content"


@dataclass(frozen=True, slots=True)
class PublishedAgentVersionData:
    """Server-loaded tool membership for one immutable published agent version."""

    version_id: str
    allowed_tool_ids: frozenset[str] | None
    published: bool = True

    def __post_init__(self) -> None:
        if not self.version_id.strip():
            raise ValueError("Published agent version identifiers must be non-empty")
        if self.allowed_tool_ids is not None:
            object.__setattr__(self, "allowed_tool_ids", frozenset(self.allowed_tool_ids))


@dataclass(frozen=True, slots=True)
class ServerHeldLibraryContext:
    """Identity, tenant, policy, and contract data loaded only by the server."""

    organization_id: OrganizationId
    actor_id: ActorId
    correlation_id: CorrelationId
    permissions: frozenset[str]
    organization_allowed_tool_ids: frozenset[str] | None
    published_agent_versions: tuple[PublishedAgentVersionData, ...]

    def __post_init__(self) -> None:
        if any(
            not str(value).strip()
            for value in (self.organization_id, self.actor_id, self.correlation_id)
        ):
            raise ValueError("Server-held delegation identity must be complete")
        object.__setattr__(self, "permissions", frozenset(self.permissions))
        if self.organization_allowed_tool_ids is not None:
            object.__setattr__(
                self,
                "organization_allowed_tool_ids",
                frozenset(self.organization_allowed_tool_ids),
            )
        object.__setattr__(self, "published_agent_versions", tuple(self.published_agent_versions))


@dataclass(frozen=True, slots=True)
class ImmutableRunSubject:
    """Server-resolved run subject and its pinned published agent versions."""

    organization_id: OrganizationId
    subject_reference: str
    pinned_agent_version_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.subject_reference.strip():
            raise ValueError("Governed subjects require a non-empty reference")
        if any(not version_id.strip() for version_id in self.pinned_agent_version_ids):
            raise ValueError("Pinned agent version identifiers must be non-empty")
        object.__setattr__(
            self, "pinned_agent_version_ids", tuple(self.pinned_agent_version_ids)
        )


@dataclass(frozen=True, slots=True)
class GovernedLibraryRequest:
    """Data presented by an adapter before any existing library service is called."""

    operation: GovernedOperation
    adapter_kind: DispatchAdapterKind
    context: ServerHeldLibraryContext
    subject: ImmutableRunSubject
    arguments: Mapping[str, object]
    supplied_values: Mapping[str, object]
    supplied_value_source: SuppliedValueSource

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))
        object.__setattr__(self, "supplied_values", MappingProxyType(dict(self.supplied_values)))


@dataclass(frozen=True, slots=True)
class GovernedLibraryInvocation:
    """Validated invocation forwarded unchanged to one existing library service."""

    operation: GovernedOperation
    adapter_kind: DispatchAdapterKind
    context: ServerHeldLibraryContext
    subject: ImmutableRunSubject
    arguments: Mapping[str, object]
    approved_tool_ids: frozenset[str]


class ExistingLibraryService(Protocol):
    """Operation-specific adapter around an existing common-agent-swarm-ops service."""

    @property
    def operation(self) -> GovernedOperation:
        """Return the single governed operation the service supports."""

    def execute(
        self, invocation: GovernedLibraryInvocation
    ) -> Result[object, ErrorDetail]:
        """Invoke existing behavior without implementing a parallel execution path."""


@dataclass(frozen=True, slots=True)
class BoundLibraryService:
    """Bind an existing typed service call to exactly one governed operation."""

    operation: GovernedOperation
    callback: Callable[[GovernedLibraryInvocation], Result[object, ErrorDetail]]

    def execute(self, invocation: GovernedLibraryInvocation) -> Result[object, ErrorDetail]:
        """Forward the validated invocation to the bound existing service."""
        return self.callback(invocation)


class GovernedLibraryDelegate:
    """Validate untrusted influence and call only the matching existing service."""

    def delegate(
        self,
        request: GovernedLibraryRequest,
        service: ExistingLibraryService,
    ) -> Result[object, ErrorDetail]:
        """Fail closed before dispatch, then preserve the library service result."""
        if service.operation is not request.operation:
            return Result.failure(self._denied(request.context.correlation_id))
        if request.context.organization_id != request.subject.organization_id:
            return Result.failure(self._denied(request.context.correlation_id))

        inspection = _inspect_supplied_values(request.supplied_values)
        if inspection.prohibited or inspection.invalid_tool_shape:
            return Result.failure(self._denied(request.context.correlation_id))
        if not self._tools_are_conclusively_allowed(request, inspection.tool_ids):
            return Result.failure(self._denied(request.context.correlation_id))

        invocation = GovernedLibraryInvocation(
            operation=request.operation,
            adapter_kind=request.adapter_kind,
            context=request.context,
            subject=request.subject,
            arguments=request.arguments,
            approved_tool_ids=inspection.tool_ids,
        )
        return service.execute(invocation)

    @staticmethod
    def _tools_are_conclusively_allowed(
        request: GovernedLibraryRequest, tool_ids: frozenset[str]
    ) -> bool:
        if not tool_ids:
            return True
        organization_tools = request.context.organization_allowed_tool_ids
        if organization_tools is None or not tool_ids.issubset(organization_tools):
            return False

        pinned = frozenset(request.subject.pinned_agent_version_ids)
        if not pinned:
            return False
        versions = tuple(
            version
            for version in request.context.published_agent_versions
            if version.version_id in pinned
        )
        if {version.version_id for version in versions} != pinned:
            return False
        if any(not version.published or version.allowed_tool_ids is None for version in versions):
            return False
        published_tools = frozenset(
            tool_id
            for version in versions
            for tool_id in (version.allowed_tool_ids or frozenset())
        )
        return tool_ids.issubset(published_tools)

    @staticmethod
    def _denied(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "The governed operation is not permitted.",
            correlation_id,
        )


@dataclass(frozen=True, slots=True)
class _Inspection:
    tool_ids: frozenset[str]
    prohibited: bool
    invalid_tool_shape: bool


_TOOL_KEYS = frozenset({"adapter", "adapter_id", "adapter_ids", "tool", "tool_id", "tool_ids"})
_CREDENTIAL_PARTS = frozenset(
    {"api_key", "apikey", "credential", "cookie", "password", "secret", "token"}
)
_URL_PARTS = frozenset({"endpoint", "host", "uri", "url"})
_EXECUTABLE_PARTS = frozenset(
    {"command", "executable", "instruction", "prompt", "script", "shell"}
)
_AUTHORITY_PARTS = frozenset(
    {
        "actor",
        "approval",
        "authority",
        "authorization",
        "identity",
        "organization",
        "permission",
        "policy",
        "role",
        "tenant",
    }
)


def _inspect_supplied_values(values: Mapping[str, object]) -> _Inspection:
    tools: set[str] = set()
    prohibited = False
    invalid_tool_shape = False

    def inspect(value: object, key: str | None = None) -> None:
        nonlocal prohibited, invalid_tool_shape
        normalized_key = _normalized_key(key) if key is not None else None
        if normalized_key is not None:
            prohibited_parts = (
                _CREDENTIAL_PARTS | _URL_PARTS | _EXECUTABLE_PARTS | _AUTHORITY_PARTS
            )
            if _matches_part(normalized_key, prohibited_parts):
                prohibited = True
            if normalized_key in _TOOL_KEYS:
                extracted = _tool_values(value)
                if extracted is None:
                    invalid_tool_shape = True
                else:
                    tools.update(extracted)
                return
        if callable(value) or isinstance(value, bytes | bytearray):
            prohibited = True
            return
        if isinstance(value, str):
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith("//"):
                prohibited = True
            return
        if isinstance(value, Mapping):
            for child_key, child in value.items():
                if not isinstance(child_key, str) or not child_key:
                    prohibited = True
                    continue
                inspect(child, child_key)
            return
        if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
            for child in value:
                inspect(child)

    inspect(values)
    safe_tools = frozenset(tool_id for tool_id in tools if is_safe_tool_identifier(tool_id))
    if len(safe_tools) != len(tools):
        invalid_tool_shape = True
    return _Inspection(safe_tools, prohibited, invalid_tool_shape)


def _tool_values(value: object) -> tuple[str, ...] | None:
    if isinstance(value, str):
        return (value,)
    if (
        isinstance(value, Sequence)
        and not isinstance(value, str | bytes | bytearray)
        and all(isinstance(item, str) for item in value)
    ):
        return tuple(value)
    return None


def _normalized_key(value: str) -> str:
    return value.casefold().replace("-", "_")


def _matches_part(value: str, parts: frozenset[str]) -> bool:
    return any(part in value for part in parts)
