"""Approval gates that pause critical effects and reauthorize them at resume time."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from math import isfinite
from typing import Protocol, TypeVar
from uuid import uuid4

from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import HostToolBroker, ToolInvocationResult, ToolRequest
from app.models.common import SCHEMA_VERSION, OptimisticTransition, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import (
    ActorId,
    ApprovalId,
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import RunRecord, RunStatus
from app.repositories.protocols import ApprovalRepository, RunRepository

T = TypeVar("T")


class ApprovalGateStatus(StrEnum):
    """The durable gate lifecycle that prevents duplicate resumed effects."""

    PAUSED = "paused"
    REAUTHORIZING = "reauthorizing"
    RESUMED = "resumed"


class ApprovalDecisionValue(StrEnum):
    """The only human decision values that can resume or retain a gate."""

    APPROVED = "approved"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class ActionPreview:
    """The operator-visible explanation emitted before a critical effect."""

    action_id: str
    summary: str
    intended_effect: str
    rollback_preview: str | None = None
    supporting_evidence: tuple[str, ...] = ()
    confidence: float | None = None
    uncertainty: str | None = None
    correction_control: str | None = None

    def __post_init__(self) -> None:
        if not self.action_id or not self.summary or not self.intended_effect:
            raise ValueError("Action previews require an action ID, summary, and intended effect.")
        if self.confidence is not None and (
            not isfinite(self.confidence) or not 0 <= self.confidence <= 1
        ):
            raise ValueError("Action preview confidence must be within the inclusive range [0, 1].")
        if not (
            self.supporting_evidence
            or self.confidence is not None
            or self.uncertainty
            or self.correction_control
        ):
            raise ValueError("Action previews require human-centered operator context.")


@dataclass(frozen=True, slots=True)
class ApprovalGate:
    """A persisted, pre-effect pause with its complete operator action preview."""

    metadata: RecordMetadata
    approval_id: ApprovalId
    run_id: RunId
    risk_tier: str
    action_preview: ActionPreview
    status: ApprovalGateStatus


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    """An immutable submitted human decision, including invalid submissions."""

    metadata: RecordMetadata
    decision_id: RecordId
    approval_id: ApprovalId
    actor_id: ActorId
    selected_value: str
    reason: str
    reason_is_valid: bool
    value_is_valid: bool
    submitted_at: datetime

    @property
    def is_valid_approval(self) -> bool:
        """Return whether this submission can trigger a fresh authorization check."""
        return (
            self.reason_is_valid
            and self.value_is_valid
            and self.selected_value == ApprovalDecisionValue.APPROVED
        )

    @property
    def is_valid_denial(self) -> bool:
        """Return whether this submission deliberately keeps the gate paused."""
        return (
            self.reason_is_valid
            and self.value_is_valid
            and self.selected_value == ApprovalDecisionValue.DENIED
        )


@dataclass(frozen=True, slots=True)
class ApprovalSubmissionOutcome:
    """The observable result of retaining a submission and optionally resuming its effect."""

    gate: ApprovalGate
    decision: ApprovalDecision
    resumed: bool
    invocation: ToolInvocationResult | None = None


class ApprovalResumeEngine(Protocol):
    """The run/engine seam invoked only after a gate is durably claimed for resume."""

    def resume_from_approval(
        self,
        run: RunRecord,
        gate: ApprovalGate,
        authorization_context: AuthorizationContext,
        tool_request: ToolRequest,
    ) -> ToolInvocationResult:
        """Freshly authorize and invoke the pending effect through the Host broker."""


class BrokerApprovalResumeEngine:
    """Default engine seam: route every resumed effect through the Host tool broker."""

    def __init__(self, tool_broker: HostToolBroker) -> None:
        self._tool_broker = tool_broker

    def resume_from_approval(
        self,
        run: RunRecord,
        gate: ApprovalGate,
        authorization_context: AuthorizationContext,
        tool_request: ToolRequest,
    ) -> ToolInvocationResult:
        """Perform a new broker authorization and invoke only if it permits this request."""
        del run, gate
        return self._tool_broker.request_tool(tool_request, authorization_context)


class GovernanceService:
    """Pause critical effects, retain decisions, and reauthorize only valid approvals."""

    def __init__(
        self,
        run_repository: RunRepository,
        approval_repository: ApprovalRepository,
        tool_broker: HostToolBroker,
        clock: Callable[[], datetime] = utc_now,
        resume_engine: ApprovalResumeEngine | None = None,
    ) -> None:
        self._run_repository = run_repository
        self._approval_repository = approval_repository
        self._resume_engine = resume_engine or BrokerApprovalResumeEngine(tool_broker)
        self._clock = clock

    def pause_before_effect(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
        risk_tier: str,
        action_preview: ActionPreview,
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Persist an action preview and pause a dispatching run before any critical effect."""
        if not risk_tier:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A critical action requires a non-empty risk tier.",
                    correlation_id,
                )
            )
        current = self._get_run(organization_id, run_id, correlation_id)
        if not current.is_success:
            return Result.failure(self._required_error(current))
        if self._required_value(current).status is not RunStatus.DISPATCHING:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Only a dispatching run may pause at an approval gate.",
                    correlation_id,
                )
            )

        now = self._clock()
        identifier = str(uuid4())
        gate = ApprovalGate(
            metadata=RecordMetadata(
                record_id=RecordId(identifier),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            approval_id=ApprovalId(identifier),
            run_id=run_id,
            risk_tier=risk_tier,
            action_preview=action_preview,
            status=ApprovalGateStatus.PAUSED,
        )
        persisted = self._approval_repository.create(gate)
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        paused_run = self._transition_run(
            organization_id,
            run_id,
            RunStatus.DISPATCHING,
            RunStatus.WAITING_FOR_APPROVAL,
            correlation_id,
        )
        if not paused_run.is_success:
            return Result.failure(self._required_error(paused_run))
        return persisted

    def submit_decision(
        self,
        organization_id: OrganizationId,
        approval_id: ApprovalId,
        actor_id: ActorId,
        selected_value: str,
        reason: str,
        authorization_context: AuthorizationContext,
        tool_request: ToolRequest,
        correlation_id: CorrelationId,
    ) -> Result[ApprovalSubmissionOutcome, ErrorDetail]:
        """Retain a human decision and invoke an effect only after fresh full authorization."""
        gate_result = self._approval_repository.get_by_approval_id(organization_id, approval_id)
        if not gate_result.is_success:
            return Result.failure(self._with_correlation(gate_result.error, correlation_id))
        gate = self._required_value(gate_result)
        decision = self._new_decision(
            organization_id,
            approval_id,
            actor_id,
            selected_value,
            reason,
            correlation_id,
        )
        appended = self._approval_repository.append_decision(decision)
        if not appended.is_success:
            return Result.failure(self._with_correlation(appended.error, correlation_id))

        if not decision.is_valid_approval:
            return Result.success(ApprovalSubmissionOutcome(gate, decision, resumed=False))
        if gate.status is not ApprovalGateStatus.PAUSED:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "The approval gate is no longer eligible for resume.",
                    correlation_id,
                    retryable=True,
                )
            )
        if authorization_context.organization_id != organization_id:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Authorization context does not match the approval organization.",
                    correlation_id,
                )
            )

        claimed_gate = self._transition_gate(gate, ApprovalGateStatus.REAUTHORIZING, correlation_id)
        if not claimed_gate.is_success:
            return Result.failure(self._required_error(claimed_gate))
        claimed = self._required_value(claimed_gate)
        dispatching_run = self._transition_run(
            organization_id,
            gate.run_id,
            RunStatus.WAITING_FOR_APPROVAL,
            RunStatus.DISPATCHING,
            correlation_id,
        )
        if not dispatching_run.is_success:
            self._restore_gate(claimed, correlation_id)
            return Result.failure(self._required_error(dispatching_run))

        invocation = self._resume_engine.resume_from_approval(
            self._required_value(dispatching_run),
            claimed,
            replace(authorization_context, approval_state=ApprovalState.APPROVED),
            tool_request,
        )
        if not invocation.allowed:
            restored_run = self._transition_run(
                organization_id,
                gate.run_id,
                RunStatus.DISPATCHING,
                RunStatus.WAITING_FOR_APPROVAL,
                correlation_id,
            )
            restored_gate = self._restore_gate(claimed, correlation_id)
            if not restored_run.is_success:
                return Result.failure(self._required_error(restored_run))
            if not restored_gate.is_success:
                return Result.failure(self._required_error(restored_gate))
            return Result.success(
                ApprovalSubmissionOutcome(
                    self._required_value(restored_gate),
                    decision,
                    resumed=False,
                    invocation=invocation,
                )
            )

        resumed_gate = self._transition_gate(claimed, ApprovalGateStatus.RESUMED, correlation_id)
        if not resumed_gate.is_success:
            return Result.failure(self._required_error(resumed_gate))
        return Result.success(
            ApprovalSubmissionOutcome(
                self._required_value(resumed_gate),
                decision,
                resumed=True,
                invocation=invocation,
            )
        )

    def _new_decision(
        self,
        organization_id: OrganizationId,
        approval_id: ApprovalId,
        actor_id: ActorId,
        selected_value: str,
        reason: str,
        correlation_id: CorrelationId,
    ) -> ApprovalDecision:
        now = self._clock()
        identifier = RecordId(str(uuid4()))
        return ApprovalDecision(
            metadata=RecordMetadata(
                record_id=identifier,
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            decision_id=identifier,
            approval_id=approval_id,
            actor_id=actor_id,
            selected_value=selected_value,
            reason=reason,
            reason_is_valid=isinstance(reason, str) and 1 <= len(reason) <= 1000,
            value_is_valid=(
                isinstance(selected_value, str)
                and selected_value in {ApprovalDecisionValue.APPROVED, ApprovalDecisionValue.DENIED}
            ),
            submitted_at=now,
        )

    def _get_run(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        fetched = self._run_repository.get_by_run_id(organization_id, run_id)
        if not fetched.is_success:
            return Result.failure(self._with_correlation(fetched.error, correlation_id))
        return fetched

    def _transition_run(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        expected_status: RunStatus,
        target_status: RunStatus,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        current_result = self._get_run(organization_id, run_id, correlation_id)
        if not current_result.is_success:
            return current_result
        current = self._required_value(current_result)
        if current.status is not expected_status:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "Run status changed before approval processing could continue.",
                    correlation_id,
                    retryable=True,
                )
            )
        updated = replace(
            current,
            metadata=replace(
                current.metadata,
                correlation_id=correlation_id,
                version=current.metadata.version + 1,
                updated_at=self._clock(),
            ),
            status=target_status,
        )
        transitioned = self._run_repository.transition(
            updated,
            OptimisticTransition(
                record_id=current.metadata.record_id,
                organization_id=organization_id,
                expected_version=current.metadata.version,
                correlation_id=correlation_id,
            ),
        )
        if not transitioned.is_success:
            return Result.failure(self._with_correlation(transitioned.error, correlation_id))
        return transitioned

    def _transition_gate(
        self,
        gate: ApprovalGate,
        target_status: ApprovalGateStatus,
        correlation_id: CorrelationId,
    ) -> Result[ApprovalGate, ErrorDetail]:
        updated = replace(
            gate,
            metadata=replace(
                gate.metadata,
                correlation_id=correlation_id,
                version=gate.metadata.version + 1,
                updated_at=self._clock(),
            ),
            status=target_status,
        )
        transitioned = self._approval_repository.transition(
            updated,
            OptimisticTransition(
                record_id=gate.metadata.record_id,
                organization_id=gate.metadata.organization_id,
                expected_version=gate.metadata.version,
                correlation_id=correlation_id,
            ),
        )
        if not transitioned.is_success:
            return Result.failure(self._with_correlation(transitioned.error, correlation_id))
        return transitioned

    def _restore_gate(
        self, gate: ApprovalGate, correlation_id: CorrelationId
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Return a denied-at-resume gate to paused state without discarding its submission."""
        return self._transition_gate(gate, ApprovalGateStatus.PAUSED, correlation_id)

    @staticmethod
    def _with_correlation(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Approval persistence is unavailable.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @staticmethod
    def _required_value(result: Result[T, ErrorDetail]) -> T:
        if result.value is None:
            raise RuntimeError("A successful repository result did not contain a record.")
        return result.value

    @staticmethod
    def _required_error(result: Result[T, ErrorDetail]) -> ErrorDetail:
        if result.error is None:
            raise RuntimeError("A failed repository result did not contain an error.")
        return result.error
