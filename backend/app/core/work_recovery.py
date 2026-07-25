"""Fail-closed durable work recovery decisions derived from deployment policy."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from app.core.command_service import CommandPublication, CommandService, WorkTransitionCommand
from app.models.common import utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import DeploymentConfiguration, WorkItem, WorkItemId, WorkState
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork


class RecoveryDecision(StrEnum):
    """Configured action for interrupted claims that have not reached a terminal state."""

    RECLAIM = "reclaim"
    MANUAL_RECOVERY = "manual_recovery"
    DEAD_LETTER = "dead_letter"


class FailureClassification(StrEnum):
    """Machine-readable failure classes used to prevent unsafe automatic retries."""

    TRANSIENT = "transient"
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    POLICY = "policy"
    RIGHTS_OR_CONSENT = "rights_or_consent"
    SCHEMA = "schema"
    NON_IDEMPOTENT_AMBIGUITY = "non_idempotent_ambiguity"


class RecoveryAction(StrEnum):
    """The stable, governed decision taken for one recovery evaluation."""

    RECLAIMED = "reclaimed"
    MANUAL_RECOVERY_REQUIRED = "manual_recovery_required"
    DEAD_LETTERED = "dead_lettered"
    RETRY_SCHEDULED = "retry_scheduled"
    CANCELLED = "cancelled"
    NON_AUTOMATIC_RETRYABLE = "non_automatic_retryable"
    RETRY_EXHAUSTED = "retry_exhausted"
    DUPLICATE_REPLAY = "duplicate_replay"


@dataclass(frozen=True, slots=True)
class WorkRecoveryPolicy:
    """Validated bounded retry and interrupted-claim recovery policy."""

    claim_expiry_decision: RecoveryDecision
    worker_stop_decision: RecoveryDecision
    max_attempts: int
    retry_delay: timedelta

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("Work recovery max_attempts must be positive.")
        if self.retry_delay < timedelta(0):
            raise ValueError("Work recovery retry_delay cannot be negative.")

    @classmethod
    def from_deployment_configuration(
        cls, configuration: DeploymentConfiguration
    ) -> WorkRecoveryPolicy:
        """Convert a schema-validated deployment policy into typed recovery decisions."""
        policy = configuration.work_recovery_policy
        try:
            claim_expiry_decision = policy["claim_expiry_decision"]
            worker_stop_decision = policy["worker_stop_decision"]
            max_attempts = policy["max_attempts"]
            retry_delay_seconds = policy["retry_delay_seconds"]
            if (
                not isinstance(claim_expiry_decision, str)
                or not isinstance(worker_stop_decision, str)
                or not isinstance(max_attempts, int)
                or isinstance(max_attempts, bool)
                or not isinstance(retry_delay_seconds, int)
                or isinstance(retry_delay_seconds, bool)
            ):
                raise ValueError
            return cls(
                claim_expiry_decision=RecoveryDecision(claim_expiry_decision),
                worker_stop_decision=RecoveryDecision(worker_stop_decision),
                max_attempts=max_attempts,
                retry_delay=timedelta(seconds=retry_delay_seconds),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Deployment work recovery policy is invalid.") from error


@dataclass(frozen=True, slots=True)
class WorkRecoveryOutcome:
    """A durable recovery decision and whether it may dispatch more work."""

    work_item: WorkItem
    action: RecoveryAction
    dispatch_allowed: bool
    duplicate: bool = False


PublicationCallback = Callable[[CommandPublication], None]
UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]
_TERMINAL_FAILURES = frozenset(
    {
        FailureClassification.VALIDATION,
        FailureClassification.AUTHORIZATION,
        FailureClassification.POLICY,
        FailureClassification.RIGHTS_OR_CONSENT,
        FailureClassification.SCHEMA,
        FailureClassification.NON_IDEMPOTENT_AMBIGUITY,
    }
)


class WorkRecoveryService:
    """Recover interrupted work while preserving CommandService transaction guarantees."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        command_service: CommandService,
        policy: WorkRecoveryPolicy,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._command_service = command_service
        self._policy = policy
        self._clock = clock

    @classmethod
    def from_deployment_configuration(
        cls,
        unit_of_work_factory: UnitOfWorkFactory,
        command_service: CommandService,
        configuration: DeploymentConfiguration,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> WorkRecoveryService:
        """Create recovery handling only from the deployment policy's validated schema."""
        return cls(
            unit_of_work_factory,
            command_service,
            WorkRecoveryPolicy.from_deployment_configuration(configuration),
            clock=clock,
        )

    def recover_expired_claim(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        """Apply the configured recovery decision after a durable worker lease expires."""
        current = self._claimed_work(organization_id, correlation_id, work_item_id)
        if not current.is_success or current.value is None:
            return Result.failure(self._error(current.error, correlation_id))
        work_item = current.value
        now = self._now()
        if work_item.claim_expires_at is None or work_item.claim_expires_at > now:
            return Result.failure(self._invalid(correlation_id, "Work claim has not expired."))
        return self._apply_interruption_decision(
            organization_id,
            correlation_id,
            work_item,
            self._policy.claim_expiry_decision,
            "claim_expired",
            publish,
        )

    def recover_worker_stop(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
        worker_id: str,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        """Apply the configured decision only to the matching stopped worker's claim."""
        current = self._claimed_work(organization_id, correlation_id, work_item_id)
        if not current.is_success or current.value is None:
            return Result.failure(self._error(current.error, correlation_id))
        work_item = current.value
        if not worker_id.strip() or work_item.claim_owner != worker_id:
            return Result.failure(
                self._invalid(correlation_id, "Worker does not own the work claim.")
            )
        return self._apply_interruption_decision(
            organization_id,
            correlation_id,
            work_item,
            self._policy.worker_stop_decision,
            "worker_stopped",
            publish,
        )

    def handle_failure(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
        classifications: tuple[FailureClassification, ...],
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        """Fail closed for terminal classes and bound cancellation-aware retries."""
        if not classifications:
            return Result.failure(
                self._invalid(correlation_id, "Failure classification is required.")
            )
        if any(not isinstance(item, FailureClassification) for item in classifications):
            return Result.failure(
                self._invalid(correlation_id, "Failure classification is invalid.")
            )
        current = self._claimed_work(organization_id, correlation_id, work_item_id)
        if not current.is_success or current.value is None:
            return Result.failure(self._error(current.error, correlation_id))
        work_item = current.value
        retained_classifications = tuple(item.value for item in classifications)
        if _TERMINAL_FAILURES.intersection(classifications) or (
            FailureClassification.TRANSIENT not in classifications
        ):
            return self._transition_outcome(
                organization_id,
                correlation_id,
                work_item,
                WorkTransitionCommand(
                    to_state=WorkState.FAILED,
                    reason_code="failure_non_automatic_retryable",
                    retry_classifications=retained_classifications,
                ),
                RecoveryAction.NON_AUTOMATIC_RETRYABLE,
                False,
                publish,
            )
        if work_item.cancellation_requested:
            return self._transition_outcome(
                organization_id,
                correlation_id,
                work_item,
                WorkTransitionCommand(
                    to_state=WorkState.CANCELLED,
                    reason_code="cancellation_requested_before_retry",
                    cancellation_requested=True,
                    retry_classifications=retained_classifications,
                ),
                RecoveryAction.CANCELLED,
                False,
                publish,
            )
        if work_item.attempt >= self._policy.max_attempts:
            return self._transition_outcome(
                organization_id,
                correlation_id,
                work_item,
                WorkTransitionCommand(
                    to_state=WorkState.DEAD_LETTER,
                    reason_code="retry_attempts_exhausted",
                    retry_classifications=retained_classifications,
                ),
                RecoveryAction.RETRY_EXHAUSTED,
                False,
                publish,
            )
        return self._transition_outcome(
            organization_id,
            correlation_id,
            work_item,
            WorkTransitionCommand(
                to_state=WorkState.PENDING,
                reason_code="transient_failure_retry_scheduled",
                attempt=work_item.attempt + 1,
                scheduled_at=self._now() + self._policy.retry_delay,
                retry_classifications=retained_classifications,
            ),
            RecoveryAction.RETRY_SCHEDULED,
            True,
            publish,
        )

    def resolve_duplicate_dispatch(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        """Return the retained idempotent work outcome without a new state mutation or dispatch."""
        with self._unit_of_work_factory() as unit_of_work:
            current = unit_of_work.work_items.get(organization_id, work_item_id)
        if not current.is_success or current.value is None:
            return Result.failure(self._error(current.error, correlation_id))
        return Result.success(
            WorkRecoveryOutcome(
                current.value,
                RecoveryAction.DUPLICATE_REPLAY,
                dispatch_allowed=False,
                duplicate=True,
            )
        )

    def _claimed_work(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
    ) -> Result[WorkItem, ErrorDetail]:
        with self._unit_of_work_factory() as unit_of_work:
            current = unit_of_work.work_items.get(organization_id, work_item_id)
        if not current.is_success or current.value is None:
            return Result.failure(self._error(current.error, correlation_id))
        if current.value.state is not WorkState.CLAIMED:
            return Result.failure(self._invalid(correlation_id, "Work item is not claimed."))
        return Result.success(current.value)

    def _apply_interruption_decision(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item: WorkItem,
        decision: RecoveryDecision,
        reason_prefix: str,
        publish: PublicationCallback | None,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        if decision is RecoveryDecision.RECLAIM:
            command = WorkTransitionCommand(
                to_state=WorkState.PENDING,
                reason_code=f"{reason_prefix}_reclaimed",
                scheduled_at=self._now(),
            )
            return self._transition_outcome(
                organization_id,
                correlation_id,
                work_item,
                command,
                RecoveryAction.RECLAIMED,
                True,
                publish,
            )
        if decision is RecoveryDecision.MANUAL_RECOVERY:
            command = WorkTransitionCommand(
                to_state=WorkState.MANUAL_RECOVERY,
                reason_code=f"{reason_prefix}_manual_recovery_required",
            )
            return self._transition_outcome(
                organization_id,
                correlation_id,
                work_item,
                command,
                RecoveryAction.MANUAL_RECOVERY_REQUIRED,
                False,
                publish,
            )
        command = WorkTransitionCommand(
            to_state=WorkState.DEAD_LETTER,
            reason_code=f"{reason_prefix}_dead_lettered",
        )
        return self._transition_outcome(
            organization_id,
            correlation_id,
            work_item,
            command,
            RecoveryAction.DEAD_LETTERED,
            False,
            publish,
        )

    def _transition_outcome(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item: WorkItem,
        command: WorkTransitionCommand,
        action: RecoveryAction,
        dispatch_allowed: bool,
        publish: PublicationCallback | None,
    ) -> Result[WorkRecoveryOutcome, ErrorDetail]:
        transitioned = self._command_service.transition(
            organization_id,
            correlation_id,
            work_item.work_item_id,
            work_item.metadata.version,
            command,
            publish=publish,
        )
        if not transitioned.is_success or transitioned.value is None:
            return Result.failure(self._error(transitioned.error, correlation_id))
        return Result.success(
            WorkRecoveryOutcome(transitioned.value.work_item, action, dispatch_allowed)
        )

    def _now(self) -> datetime:
        now = self._clock()
        if now.tzinfo is None:
            raise ValueError("Work recovery clocks must return timezone-aware timestamps.")
        return now

    @staticmethod
    def _invalid(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Work recovery storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            error.retryable,
            error.fields,
        )
