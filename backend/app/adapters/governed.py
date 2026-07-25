"""Uniform local-inline and remote adapters for governed library delegation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from app.governance.library_delegate import (
    DispatchAdapterKind,
    ExistingLibraryService,
    GovernedLibraryDelegate,
    GovernedLibraryRequest,
    GovernedOperation,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result


@dataclass(frozen=True, slots=True)
class GovernedDispatchAdapter:
    """Resolve an operation-specific service and always invoke it through the delegate."""

    kind: DispatchAdapterKind
    delegate: GovernedLibraryDelegate
    services: Mapping[GovernedOperation, ExistingLibraryService]

    def __post_init__(self) -> None:
        registered = dict(self.services)
        if any(operation is not service.operation for operation, service in registered.items()):
            raise ValueError("Each governed service must be registered for its own operation")
        object.__setattr__(self, "services", MappingProxyType(registered))

    def dispatch(self, request: GovernedLibraryRequest) -> Result[object, ErrorDetail]:
        """Reject transport substitution and delegate to the matching existing service."""
        if request.adapter_kind is not self.kind:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "The governed operation is not permitted.",
                    request.context.correlation_id,
                )
            )
        service = self.services.get(request.operation)
        if service is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "The governed library operation is unavailable.",
                    request.context.correlation_id,
                )
            )
        return self.delegate.delegate(request, service)


class LocalInlineGovernedAdapter(GovernedDispatchAdapter):
    """Local-inline transport that preserves the same governed delegate boundary."""

    def __init__(
        self,
        delegate: GovernedLibraryDelegate,
        services: Mapping[GovernedOperation, ExistingLibraryService],
    ) -> None:
        super().__init__(DispatchAdapterKind.LOCAL_INLINE, delegate, services)


class RemoteGovernedAdapter(GovernedDispatchAdapter):
    """Remote transport marker with no client-selected endpoint or credential surface."""

    def __init__(
        self,
        delegate: GovernedLibraryDelegate,
        services: Mapping[GovernedOperation, ExistingLibraryService],
    ) -> None:
        super().__init__(DispatchAdapterKind.REMOTE, delegate, services)
