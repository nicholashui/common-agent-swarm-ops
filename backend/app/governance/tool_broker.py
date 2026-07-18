"""The Host-only path for authorizing, invoking, and auditing local tools."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from types import MappingProxyType
from typing import Protocol, TypeGuard
from uuid import uuid4

from app.audit import AuditWriter
from app.governance.adapter_execution import broker_invocation
from app.governance.authorization import (
    AuthorizationContext,
    AuthorizationDecision,
    AuthorizationService,
    ToolInputValidationError,
    ToolInputValue,
    canonical_tool_input,
    is_safe_tool_identifier,
    normalize_tool_input,
)
from app.models.audit import AuditDecision, AuditEvent
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.identifiers import (
    ActorId,
    AuditEventId,
    CorrelationId,
    OrganizationId,
    new_record_id,
)
from app.models.runs import ToolEffect


class BrokerDenialReason(StrEnum):
    """Safe reasons why a broker request did not reach an adapter."""

    INVALID_TOOL_IDENTIFIER = "invalid_tool_identifier"
    LOCAL_ADAPTER_NOT_ALLOWLISTED = "local_adapter_not_allowlisted"
    INVALID_TOOL_INPUT = "invalid_tool_input"


@dataclass(frozen=True, slots=True)
class LocalAdapterResult:
    """A deterministic local adapter outcome without exposing raw result payloads."""

    outcome: str
    effect_digest: str
    reversible: bool
    compensation_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.outcome or not self.effect_digest:
            raise ValueError("Local adapter results require outcome and effect digest")


class LocalToolAdapter(Protocol):
    """The narrow, registered-only adapter interface exposed to the Host broker."""

    adapter_id: str
    version: str
    local_only: bool

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        """Execute deterministic local behavior using safe data-only arguments."""


class ToolEffectRetainer(Protocol):
    """Optional broker-owned capability for retaining completed effect evidence."""

    def retain_tool_effect(self, effect: ToolEffect) -> None:
        """Retain the immutable effect produced by the broker."""


@dataclass(frozen=True, slots=True)
class ToolRequest:
    """Untrusted agent request data; authority always comes from Host context."""

    adapter_id: str
    arguments: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ToolInvocationResult:
    """A safe result that never includes raw arguments or adapter output."""

    authorization: AuthorizationDecision
    invoked: bool
    effect: ToolEffect | None
    denial_reasons: tuple[BrokerDenialReason, ...] = ()
    denial_audit_recorded: bool | None = None

    @property
    def allowed(self) -> bool:
        """Return whether the request both passed checks and reached its local adapter."""
        return self.invoked and self.effect is not None


class LocalAdapterRegistry:
    """Host-owned, immutable allow-list of concrete local adapter objects."""

    def __init__(self, adapters: Iterable[object]) -> None:
        registered: dict[str, LocalToolAdapter] = {}
        for adapter in adapters:
            if not _is_registered_local_adapter(adapter):
                raise ValueError("Only concrete local adapter objects may be registered")
            if not is_safe_tool_identifier(adapter.adapter_id):
                raise ValueError("Local adapter identifiers must be safe registry identifiers")
            if adapter.adapter_id in registered:
                raise ValueError("Local adapter identifiers must be unique")
            registered[adapter.adapter_id] = adapter
        self._adapters = MappingProxyType(registered)

    def get(self, adapter_id: str) -> LocalToolAdapter | None:
        """Resolve one adapter exclusively through the Host-owned allow-list."""
        return self._adapters.get(adapter_id)


class HostToolBroker:
    """Authorize every call, invoke only allowlisted adapters, and audit all denials."""

    def __init__(
        self,
        adapters: Iterable[object],
        audit_writer: AuditWriter,
        authorization_service: AuthorizationService | None = None,
    ) -> None:
        self._adapters = LocalAdapterRegistry(adapters)
        self._audit_writer = audit_writer
        self._authorization_service = authorization_service or AuthorizationService()

    def request_tool(
        self,
        request: ToolRequest,
        context: AuthorizationContext,
    ) -> ToolInvocationResult:
        """Evaluate this request afresh before any local adapter invocation.

        No previous result is consulted. Every denied request attempts an append-only audit
        record, while any audit failure remains a denial with no adapter invocation.
        """
        decision = self._authorization_service.evaluate(context, request.adapter_id)
        denial_reasons = self._request_denial_reasons(request)
        adapter = self._adapters.get(request.adapter_id)
        if adapter is None:
            return self._denied_result(
                context,
                decision,
                (*denial_reasons, BrokerDenialReason.LOCAL_ADAPTER_NOT_ALLOWLISTED),
            )
        if not decision.permitted or denial_reasons:
            return self._denied_result(context, decision, denial_reasons)

        try:
            arguments = normalize_tool_input(request.arguments)
        except ToolInputValidationError:
            return self._denied_result(
                context,
                decision,
                (BrokerDenialReason.INVALID_TOOL_INPUT,),
            )

        with broker_invocation():
            adapter_result = adapter.execute(arguments)
            request_digest = sha256(canonical_tool_input(arguments).encode("utf-8")).hexdigest()
            effect = ToolEffect(
                adapter_id=adapter.adapter_id,
                request_digest=request_digest,
                outcome=adapter_result.outcome,
                effect_digest=adapter_result.effect_digest,
                completed_at=utc_now(),
                reversible=adapter_result.reversible,
                compensation_reference=adapter_result.compensation_reference,
            )
            if _retains_tool_effects(adapter):
                adapter.retain_tool_effect(effect)
        return ToolInvocationResult(decision, invoked=True, effect=effect)

    @staticmethod
    def _request_denial_reasons(request: ToolRequest) -> tuple[BrokerDenialReason, ...]:
        reasons: list[BrokerDenialReason] = []
        if not is_safe_tool_identifier(request.adapter_id):
            reasons.append(BrokerDenialReason.INVALID_TOOL_IDENTIFIER)
        return tuple(reasons)

    def _denied_result(
        self,
        context: AuthorizationContext,
        decision: AuthorizationDecision,
        denial_reasons: tuple[BrokerDenialReason, ...],
    ) -> ToolInvocationResult:
        audit_result = self._audit_writer.append(
            AuditEvent(
                metadata=RecordMetadata(
                    record_id=new_record_id(),
                    organization_id=OrganizationId(context.organization_id),
                    correlation_id=CorrelationId(context.correlation_id),
                    schema_version=SCHEMA_VERSION,
                    version=1,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                ),
                audit_event_id=AuditEventId(str(uuid4())),
                actor_id=ActorId(context.actor_id),
                operation="tool.request",
                decision=AuditDecision.DENIED,
                reason=self._denial_reason(decision, denial_reasons),
                recorded_at=utc_now(),
            )
        )
        return ToolInvocationResult(
            authorization=decision,
            invoked=False,
            effect=None,
            denial_reasons=denial_reasons,
            denial_audit_recorded=audit_result.recorded,
        )

    @staticmethod
    def _denial_reason(
        decision: AuthorizationDecision,
        denial_reasons: tuple[BrokerDenialReason, ...],
    ) -> str:
        values = [str(constraint) for constraint in decision.denied_constraints]
        values.extend(str(reason) for reason in denial_reasons)
        return ",".join(values)


def _retains_tool_effects(value: object) -> TypeGuard[ToolEffectRetainer]:
    """Return whether an adapter can retain the broker-created immutable effect."""
    return callable(getattr(value, "retain_tool_effect", None))


def _is_registered_local_adapter(value: object) -> TypeGuard[LocalToolAdapter]:
    """Reject callables and incomplete or non-local adapter registrations."""
    return (
        not callable(value)
        and isinstance(getattr(value, "adapter_id", None), str)
        and isinstance(getattr(value, "version", None), str)
        and getattr(value, "local_only", False) is True
        and callable(getattr(value, "execute", None))
    )
