"""Evaluate configured degradation conditions and retain traceable safe alerts."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime

from app.alerts.repository import OperatorAlertRepository
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import AlertId, AlertKind, DeploymentConfiguration, OperatorAlert
from app.models.identifiers import CorrelationId, OrganizationId, new_correlation_id, new_record_id


@dataclass(frozen=True, slots=True)
class AlertPolicy:
    """Validated deployment thresholds and enablement flags for operator alerts."""

    readiness_failure_enabled: bool = False
    queue_age_seconds: float | None = None
    terminal_run_failure_rate: float | None = None
    replay_gap_enabled: bool = False
    outbox_lag_seconds: float | None = None
    approval_expiry_enabled: bool = False
    rollback_enabled: bool = False

    def __post_init__(self) -> None:
        for value, name in (
            (self.queue_age_seconds, "queue_age_seconds"),
            (self.outbox_lag_seconds, "outbox_lag_seconds"),
        ):
            if value is not None and (isinstance(value, bool) or value < 0):
                raise ValueError(f"{name} must be a non-negative number.")
        if self.terminal_run_failure_rate is not None and (
            isinstance(self.terminal_run_failure_rate, bool)
            or not 0 <= self.terminal_run_failure_rate <= 1
        ):
            raise ValueError("terminal_run_failure_rate must be between zero and one.")

    @classmethod
    def from_deployment_configuration(
        cls, configuration: DeploymentConfiguration
    ) -> AlertPolicy:
        """Build alert policy only from the validated deployment feature-flag mapping."""
        raw = configuration.feature_flags.get("operational_alerting", {})
        if not isinstance(raw, Mapping):
            raise ValueError("Deployment operational alerting policy is invalid.")
        return cls(
            readiness_failure_enabled=cls._enabled(raw, "readiness_failure"),
            queue_age_seconds=cls._threshold(raw, "queue_age_seconds"),
            terminal_run_failure_rate=cls._threshold(raw, "terminal_run_failure_rate"),
            replay_gap_enabled=cls._enabled(raw, "replay_gap"),
            outbox_lag_seconds=cls._threshold(raw, "outbox_lag_seconds"),
            approval_expiry_enabled=cls._enabled(raw, "approval_expiry"),
            rollback_enabled=cls._enabled(raw, "rollback"),
        )

    @staticmethod
    def _enabled(raw: Mapping[object, object], name: str) -> bool:
        value = raw.get(name, False)
        if not isinstance(value, bool):
            raise ValueError("Deployment operational alerting policy is invalid.")
        return value

    @staticmethod
    def _threshold(raw: Mapping[object, object], name: str) -> float | None:
        value = raw.get(name)
        if value is None:
            return None
        if not isinstance(value, int | float) or isinstance(value, bool):
            raise ValueError("Deployment operational alerting policy is invalid.")
        return float(value)


@dataclass(frozen=True, slots=True)
class AlertTrace:
    """Safe trace context supplied by a server-side operational monitor."""

    organization_id: OrganizationId
    correlation_id: CorrelationId | None = None
    subject_reference: str | None = None

    def __post_init__(self) -> None:
        if self.correlation_id is None and self.subject_reference is None:
            raise ValueError("Alert trace requires a correlation identifier or subject reference.")
        if self.correlation_id is not None and not str(self.correlation_id).strip():
            raise ValueError("Alert correlation_id must be non-empty.")
        if self.subject_reference is not None and not self.subject_reference.strip():
            raise ValueError("Alert subject_reference must be non-empty.")


@dataclass(frozen=True, slots=True)
class AlertEvaluation:
    """The result of checking one configured condition, including an optional durable alert."""

    triggered: bool
    alert: OperatorAlert | None = None


class AlertService:
    """Evaluate only configured conditions and retain a redacted alert for each detection."""

    def __init__(
        self,
        repository: OperatorAlertRepository,
        policy: AlertPolicy,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._policy = policy
        self._clock = clock

    @classmethod
    def from_deployment_configuration(
        cls,
        repository: OperatorAlertRepository,
        configuration: DeploymentConfiguration,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> AlertService:
        """Create alert evaluation from the deployment-owned configured policy."""
        return cls(
            repository,
            AlertPolicy.from_deployment_configuration(configuration),
            clock=clock,
        )

    def evaluate_readiness(
        self, trace: AlertTrace, *, unavailable: bool, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist a readiness alert only when the configured monitor detects unavailability."""
        return self._evaluate(
            trace, AlertKind.READINESS_FAILURE,
            configured=self._policy.readiness_failure_enabled, detected=unavailable,
            details=details,
        )

    def evaluate_queue_age(
        self, trace: AlertTrace, *, age_seconds: float, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist an alert when a work item reaches the configured queue-age threshold."""
        return self._evaluate_threshold(
            trace, AlertKind.QUEUE_AGE, age_seconds, self._policy.queue_age_seconds, details
        )

    def evaluate_terminal_run_failure_rate(
        self, trace: AlertTrace, *, failure_rate: float, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist an alert when the terminal-run failure rate reaches its configured threshold."""
        if not 0 <= failure_rate <= 1:
            raise ValueError("failure_rate must be between zero and one.")
        return self._evaluate_threshold(
            trace, AlertKind.TERMINAL_RUN_FAILURE_RATE, failure_rate,
            self._policy.terminal_run_failure_rate, details,
        )

    def evaluate_replay_gap(
        self, trace: AlertTrace, *, detected: bool, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist a replay-gap alert when replay recovery detects a configured sequence gap."""
        return self._evaluate(
            trace, AlertKind.REPLAY_GAP,
            configured=self._policy.replay_gap_enabled, detected=detected, details=details,
        )

    def evaluate_outbox_lag(
        self, trace: AlertTrace, *, lag_seconds: float, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist an alert when committed outbox delivery reaches its lag threshold."""
        return self._evaluate_threshold(
            trace, AlertKind.OUTBOX_LAG, lag_seconds, self._policy.outbox_lag_seconds, details
        )

    def evaluate_approval_expiry(
        self, trace: AlertTrace, *, expired: bool, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist an alert for a configured approval gate expiry."""
        return self._evaluate(
            trace, AlertKind.APPROVAL_EXPIRY,
            configured=self._policy.approval_expiry_enabled, detected=expired, details=details,
        )

    def evaluate_rollback(
        self, trace: AlertTrace, *, initiated: bool, details: Mapping[str, object] = {}
    ) -> Result[AlertEvaluation, ErrorDetail]:
        """Persist an alert when a configured rollout rollback begins."""
        return self._evaluate(
            trace, AlertKind.ROLLBACK,
            configured=self._policy.rollback_enabled, detected=initiated, details=details,
        )

    def _evaluate_threshold(
        self,
        trace: AlertTrace,
        kind: AlertKind,
        observed_value: float,
        threshold: float | None,
        details: Mapping[str, object],
    ) -> Result[AlertEvaluation, ErrorDetail]:
        if isinstance(observed_value, bool) or observed_value < 0:
            raise ValueError("Observed alert values must be non-negative numbers.")
        return self._evaluate(
            trace,
            kind,
            configured=threshold is not None,
            detected=threshold is not None and observed_value >= threshold,
            observed_value=observed_value,
            threshold=threshold,
            details=details,
        )

    def _evaluate(
        self,
        trace: AlertTrace,
        kind: AlertKind,
        *,
        configured: bool,
        detected: bool,
        observed_value: float | None = None,
        threshold: float | None = None,
        details: Mapping[str, object],
    ) -> Result[AlertEvaluation, ErrorDetail]:
        if not configured or not detected:
            return Result.success(AlertEvaluation(triggered=False))
        correlation_id = trace.correlation_id or new_correlation_id()
        detected_at = self._clock()
        alert = OperatorAlert(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=trace.organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=detected_at,
                updated_at=detected_at,
            ),
            alert_id=AlertId(str(new_record_id())),
            kind=kind,
            summary=f"Configured {kind.value} condition detected.",
            subject_reference=trace.subject_reference,
            detected_at=detected_at,
            observed_value=observed_value,
            threshold=threshold,
            details=details,
        )
        persisted = self._repository.append(alert)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._storage_error(persisted.error, correlation_id))
        return Result.success(AlertEvaluation(triggered=True, alert=persisted.value))

    @staticmethod
    def _storage_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Operator alert storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(error.code, "Operator alert storage is unavailable.", correlation_id)
