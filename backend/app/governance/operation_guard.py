"""Fail-closed operation and provider execution controls."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from math import isfinite
from threading import RLock
from typing import cast
from uuid import uuid4

from app.audit import AuditWriter
from app.governance.adapter_execution import (
    ProviderAdapterDeclaration,
    ProviderAuthorizationDecision,
    ProviderDenialReason,
    authorize_provider_adapter,
    authorized_provider_invocation,
)
from app.models.audit import AuditDecision, AuditEvent
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.identifiers import (
    ActorId,
    AuditEventId,
    CorrelationId,
    OrganizationId,
    new_correlation_id,
    new_record_id,
)
from app.models.operations import (
    OperationClassification,
    OperationDecision,
    OperationDecisionStatus,
    OperationGuardAssessment,
    OperationKind,
    ProductionChangeBlock,
    ProductionChangeBlockReason,
    ProhibitedOperation,
    ProhibitedOperationError,
    ProhibitedOperationReason,
    RequestedOperation,
)


@dataclass(frozen=True, slots=True)
class ProviderExecutionResult:
    """The fail-closed outcome of one governed provider execution."""

    authorization: ProviderAuthorizationDecision
    invoked: bool
    value: object | None = None
    denial_reasons: tuple[ProviderDenialReason, ...] = ()
    audit_recorded: bool | None = None

    @property
    def allowed(self) -> bool:
        """Return whether an authorized provider produced an accepted result."""
        return self.invoked and not self.denial_reasons


class ProductionChangeBlockLatch:
    """One-way, thread-safe latch that prevents subsequent production changes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._block: ProductionChangeBlock | None = None

    def snapshot(self) -> ProductionChangeBlock | None:
        """Return the immutable current block state, if the latch was tripped."""
        with self._lock:
            return self._block

    def trip(self, reason: ProductionChangeBlockReason) -> ProductionChangeBlock:
        """Atomically trip the latch, retaining the first fail-closed cause."""
        with self._lock:
            if self._block is None:
                self._block = ProductionChangeBlock(reason=reason, blocked_at=utc_now())
            return self._block


@dataclass(frozen=True, slots=True)
class ProhibitedErrorDeliveryResult:
    """The result of delivering a prohibited-operation response."""

    assessment: OperationGuardAssessment
    error_delivered: bool | None


class OperationGuard:
    """Classify operations and enforce provider authorization before any side effect."""

    def __init__(
        self,
        latch: ProductionChangeBlockLatch | None = None,
        audit_writer: AuditWriter | None = None,
    ) -> None:
        self._lock = RLock()
        self._latch = latch or ProductionChangeBlockLatch()
        self._audit_writer = audit_writer

    @property
    def latch(self) -> ProductionChangeBlockLatch:
        """Expose the shared one-way production-change latch."""
        return self._latch

    def authorize_provider(
        self,
        adapter: object,
        declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
        *,
        capability: str | None = None,
        correlation_id: str | None = None,
        organization_id: str = "adoption-platform",
        actor_id: str = "governance-controller",
    ) -> ProviderAuthorizationDecision:
        """Authorize a provider and audit every denial before dispatch is possible."""
        decision = authorize_provider_adapter(adapter, declaration, capability=capability)
        if decision.permitted:
            return decision
        audit_recorded = self._record_provider_denial(
            decision,
            decision.denied_reasons,
            correlation_id=correlation_id,
            organization_id=organization_id,
            actor_id=actor_id,
            operation="provider.authorize",
        )
        return replace(decision, audit_recorded=audit_recorded)

    # The explicit alias mirrors the specification terminology for callers.
    authorize_provider_adapter = authorize_provider

    def execute_provider(
        self,
        adapter: object,
        declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
        arguments: Mapping[str, object],
        *,
        capability: str | None = None,
        requested_cost: float | int = 0,
        actual_cost: float | int | None = None,
        timed_out: bool = False,
        unsafe_result: bool = False,
        available: bool | None = None,
        correlation_id: str | None = None,
        organization_id: str = "adoption-platform",
        actor_id: str = "governance-controller",
    ) -> ProviderExecutionResult:
        """Authorize, contain, and execute one provider action without fail-open paths."""
        authorization = self.authorize_provider(
            adapter,
            declaration,
            capability=capability,
            correlation_id=correlation_id,
            organization_id=organization_id,
            actor_id=actor_id,
        )
        if not authorization.permitted:
            return ProviderExecutionResult(
                authorization=authorization,
                invoked=False,
                denial_reasons=authorization.denied_reasons,
                audit_recorded=authorization.audit_recorded,
            )

        declaration_value = _declaration_value(declaration)
        fault = self._provider_fault(
            adapter,
            declaration_value,
            requested_cost=requested_cost,
            actual_cost=actual_cost,
            timed_out=timed_out,
            unsafe_result=unsafe_result,
            available=available,
        )
        if fault is not None:
            return self._denied_provider_result(
                authorization,
                fault,
                correlation_id=correlation_id,
                organization_id=organization_id,
                actor_id=actor_id,
            )

        try:
            with authorized_provider_invocation():
                value = _invoke_provider(
                    adapter,
                    authorization.capability,
                    arguments,
                    correlation_id=correlation_id,
                )
        except TimeoutError:
            return self._denied_provider_result(
                authorization,
                ProviderDenialReason.PROVIDER_TIMEOUT,
                correlation_id=correlation_id,
                organization_id=organization_id,
                actor_id=actor_id,
            )
        except Exception:
            return self._denied_provider_result(
                authorization,
                ProviderDenialReason.PROVIDER_UNAVAILABLE,
                correlation_id=correlation_id,
                organization_id=organization_id,
                actor_id=actor_id,
            )

        result_fault = _result_fault(value)
        if result_fault is not None:
            return self._denied_provider_result(
                authorization,
                result_fault,
                correlation_id=correlation_id,
                organization_id=organization_id,
                actor_id=actor_id,
            )
        return ProviderExecutionResult(authorization=authorization, invoked=True, value=value)

    execute_provider_adapter = execute_provider
    invoke_provider = execute_provider

    def assess(self, operations: Iterable[RequestedOperation]) -> OperationGuardAssessment:
        """Atomically classify all operations before a caller starts production work."""
        with self._lock:
            return self._assess_locked(tuple(operations))

    def assess_and_deliver_prohibited_error(
        self,
        operations: Iterable[RequestedOperation],
        deliver_error: Callable[[ProhibitedOperationError], bool],
    ) -> ProhibitedErrorDeliveryResult:
        """Assess a request and trip the latch if its denial cannot be delivered.

        The evaluation, response delivery result, and latch transition share one lock.
        Therefore another caller cannot receive a production-permitting assessment
        between a failed prohibited-error delivery and the fail-closed latch trip.
        """
        with self._lock:
            assessment = self._assess_locked(tuple(operations))
            error = assessment.prohibited_error
            if error is None:
                return ProhibitedErrorDeliveryResult(assessment, None)
            try:
                delivered = deliver_error(error)
            except Exception:
                delivered = False
            if not delivered:
                assessment = OperationGuardAssessment(
                    decisions=assessment.decisions,
                    prohibited_error=error,
                    production_change_block=self._latch.trip(
                        ProductionChangeBlockReason.PROHIBITED_ERROR_DELIVERY_FAILED
                    ),
                )
            return ProhibitedErrorDeliveryResult(assessment, delivered)

    def _denied_provider_result(
        self,
        authorization: ProviderAuthorizationDecision,
        reason: ProviderDenialReason,
        *,
        correlation_id: str | None,
        organization_id: str,
        actor_id: str,
    ) -> ProviderExecutionResult:
        """Persist a best-effort denial while retaining the denial on audit failure."""
        audit_recorded = self._record_provider_denial(
            authorization,
            (reason,),
            correlation_id=correlation_id,
            organization_id=organization_id,
            actor_id=actor_id,
            operation="provider.execute",
        )
        return ProviderExecutionResult(
            authorization=replace(authorization, audit_recorded=audit_recorded),
            invoked=False,
            denial_reasons=(reason,),
            audit_recorded=audit_recorded,
        )

    def _record_provider_denial(
        self,
        decision: ProviderAuthorizationDecision,
        reasons: Iterable[ProviderDenialReason],
        *,
        correlation_id: str | None,
        organization_id: str,
        actor_id: str,
        operation: str,
    ) -> bool:
        """Attempt to write one redaction-safe provider denial audit event."""
        if self._audit_writer is None:
            return False
        correlation = CorrelationId(correlation_id or str(new_correlation_id()))
        reason_text = ",".join(dict.fromkeys(reason.value for reason in reasons))
        try:
            result = self._audit_writer.append(
                AuditEvent(
                    metadata=RecordMetadata(
                        record_id=new_record_id(),
                        organization_id=OrganizationId(organization_id),
                        correlation_id=correlation,
                        schema_version=SCHEMA_VERSION,
                        version=1,
                        created_at=utc_now(),
                        updated_at=utc_now(),
                    ),
                    audit_event_id=AuditEventId(str(uuid4())),
                    actor_id=ActorId(actor_id),
                    operation=operation,
                    decision=AuditDecision.DENIED,
                    reason=f"{decision.provider_id}:{decision.capability}:{reason_text}",
                    recorded_at=utc_now(),
                )
            )
            return bool(result.recorded)
        except Exception:
            return False

    @staticmethod
    def _provider_fault(
        adapter: object,
        declaration: ProviderAdapterDeclaration | None,
        *,
        requested_cost: float | int,
        actual_cost: float | int | None,
        timed_out: bool,
        unsafe_result: bool,
        available: bool | None,
    ) -> ProviderDenialReason | None:
        """Classify explicit and deterministic provider fault signals before dispatch."""
        failure_mode = _failure_mode(adapter)
        if timed_out or failure_mode == "timeout":
            return ProviderDenialReason.PROVIDER_TIMEOUT
        if unsafe_result or failure_mode == "unsafe_result":
            return ProviderDenialReason.UNSAFE_PROVIDER_RESULT
        is_available = available if available is not None else getattr(adapter, "available", True)
        if is_available is not True or failure_mode == "unavailable":
            return ProviderDenialReason.PROVIDER_UNAVAILABLE
        limit = declaration.cost_limit if declaration is not None else None
        measured_cost = actual_cost if actual_cost is not None else requested_cost
        if (
            limit is None
            or not _finite_nonnegative(measured_cost)
            or measured_cost > limit
            or failure_mode == "budget_exceeded"
        ):
            return ProviderDenialReason.PROVIDER_BUDGET_EXCEEDED
        return None

    def _assess_locked(
        self,
        operations: tuple[RequestedOperation, ...],
    ) -> OperationGuardAssessment:
        classifications = tuple(self._classify(operation) for operation in operations)
        prohibited = tuple(
            ProhibitedOperation(item.operation_id, item.prohibition)
            for item in classifications
            if item.prohibition is not None
        )
        if prohibited:
            return OperationGuardAssessment(
                decisions=tuple(
                    OperationDecision(
                        classification,
                        (
                            OperationDecisionStatus.PROHIBITED
                            if classification.is_prohibited
                            else OperationDecisionStatus.CANCELLED_BY_PROHIBITED_OPERATION
                        ),
                    )
                    for classification in classifications
                ),
                prohibited_error=ProhibitedOperationError(prohibited),
            )

        block = self._latch.snapshot()
        return OperationGuardAssessment(
            decisions=tuple(
                OperationDecision(
                    classification,
                    (
                        OperationDecisionStatus.BLOCKED_BY_PRODUCTION_LATCH
                        if block is not None and operation.targets_production
                        else OperationDecisionStatus.PERMITTED
                    ),
                )
                for operation, classification in zip(operations, classifications, strict=True)
            ),
            production_change_block=block,
        )

    @staticmethod
    def _classify(operation: RequestedOperation) -> OperationClassification:
        prohibitions: list[ProhibitedOperationReason] = []
        if (
            operation.kind is OperationKind.PRODUCTION_PROMOTION
            and operation.targets_production
            and operation.automatic
        ):
            prohibitions.append(ProhibitedOperationReason.AUTOMATIC_PRODUCTION_PROMOTION)
        if operation.kind is OperationKind.HOST_CODE_REWRITE and operation.targets_production:
            prohibitions.append(ProhibitedOperationReason.PRODUCTION_HOST_CODE_REWRITE)
        if operation.kind is OperationKind.ORCHESTRATION:
            if not operation.bounded:
                prohibitions.append(ProhibitedOperationReason.UNBOUNDED_ORCHESTRATION)
            if (
                operation.recorded_authorization is None
                or not operation.recorded_authorization.is_recorded_approval
            ):
                prohibitions.append(ProhibitedOperationReason.MISSING_ORCHESTRATION_AUTHORIZATION)
        return OperationClassification(
            operation_id=operation.operation_id,
            prohibition=prohibitions[0] if prohibitions else None,
        )


def _declaration_value(
    declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
) -> ProviderAdapterDeclaration | None:
    """Normalize a mapping declaration for cost containment after authorization."""
    if declaration is None or isinstance(declaration, ProviderAdapterDeclaration):
        return declaration
    return ProviderAdapterDeclaration(
        provider_id=_text_value(declaration.get("provider_id")) or "",
        capabilities=_capabilities_value(declaration.get("capabilities", ())),
        capability=_text_value(declaration.get("capability")),
        cost_limit=_cost_value(declaration.get("cost_limit", declaration.get("cost"))),
        retention_policy=_text_value(declaration.get("retention_policy")),
        residency=_text_value(declaration.get("residency")),
        safety_policy=_text_value(declaration.get("safety_policy")),
    )


def _invoke_provider(
    adapter: object,
    capability: str,
    arguments: Mapping[str, object],
    *,
    correlation_id: str | None,
) -> object:
    """Invoke only the narrow adapter method, never a raw external client."""
    invoker = getattr(adapter, "invoke", None)
    if callable(invoker):
        return cast(Callable[..., object], invoker)(
            capability,
            arguments,
            correlation_id=correlation_id,
        )
    executor = getattr(adapter, "execute", None)
    if callable(executor):
        return cast(Callable[..., object], executor)(arguments)
    raise LookupError("Provider adapter has no governed invocation method")


def _result_fault(value: object) -> ProviderDenialReason | None:
    """Reject unsafe or typed-failure results before exposing them to a workflow."""
    if isinstance(value, Mapping) and (value.get("unsafe") is True or value.get("safe") is False):
        return ProviderDenialReason.UNSAFE_PROVIDER_RESULT
    if getattr(value, "unsafe", False) is True or getattr(value, "safe", True) is False:
        return ProviderDenialReason.UNSAFE_PROVIDER_RESULT
    if getattr(value, "is_success", True) is False:
        error = getattr(value, "error", None)
        code = str(getattr(error, "code", ""))
        if code in {"health_unavailable", "repository_unavailable"}:
            return ProviderDenialReason.PROVIDER_UNAVAILABLE
        if code == "rate_limited":
            return ProviderDenialReason.PROVIDER_BUDGET_EXCEEDED
        return ProviderDenialReason.UNSAFE_PROVIDER_RESULT
    return None


def _failure_mode(adapter: object) -> str | None:
    value = getattr(adapter, "failure_mode", None)
    raw = getattr(value, "value", value)
    return raw if isinstance(raw, str) else None


def _finite_nonnegative(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value >= 0
    )


def _cost_value(value: object) -> float | int | None:
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value >= 0
    ):
        return value
    return None


def _capabilities_value(value: object) -> frozenset[str] | tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(item for item in value if isinstance(item, str))
    return ()


def _text_value(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
