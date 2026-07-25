"""Focused acceptance tests for backend-redesign tasks 18.1 and 18.3."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.alerts.repository import InMemoryOperatorAlertRepository
from app.alerts.service import AlertEvaluation, AlertPolicy, AlertService, AlertTrace
from app.models.contracts import ErrorDetail, Result
from app.models.control_plane import AlertKind
from app.models.identifiers import CorrelationId, OrganizationId
from app.models.redaction import REDACTED

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("alerts-organization")
_CORRELATION = CorrelationId("alerts-correlation")


def _policy() -> AlertPolicy:
    return AlertPolicy(
        readiness_failure_enabled=True,
        queue_age_seconds=60,
        terminal_run_failure_rate=0.2,
        replay_gap_enabled=True,
        outbox_lag_seconds=30,
        approval_expiry_enabled=True,
        rollback_enabled=True,
    )


def _trace(*, correlation: CorrelationId | None = _CORRELATION) -> AlertTrace:
    return AlertTrace(
        organization_id=_ORGANIZATION,
        correlation_id=correlation,
        subject_reference="run:alerts-1",
    )


def _evaluate_trigger(
    service: AlertService, kind: AlertKind, trace: AlertTrace
) -> Result[AlertEvaluation, ErrorDetail]:
    details = {"token": "secret", "raw_prompt": "private"}
    match kind:
        case AlertKind.READINESS_FAILURE:
            return service.evaluate_readiness(trace, unavailable=True, details=details)
        case AlertKind.QUEUE_AGE:
            return service.evaluate_queue_age(trace, age_seconds=60, details=details)
        case AlertKind.TERMINAL_RUN_FAILURE_RATE:
            return service.evaluate_terminal_run_failure_rate(
                trace, failure_rate=0.2, details=details
            )
        case AlertKind.REPLAY_GAP:
            return service.evaluate_replay_gap(trace, detected=True, details=details)
        case AlertKind.OUTBOX_LAG:
            return service.evaluate_outbox_lag(trace, lag_seconds=30, details=details)
        case AlertKind.APPROVAL_EXPIRY:
            return service.evaluate_approval_expiry(trace, expired=True, details=details)
        case AlertKind.ROLLBACK:
            return service.evaluate_rollback(trace, initiated=True, details=details)
    raise AssertionError(f"Unexpected alert kind: {kind}")


@pytest.mark.parametrize(
    ("kind", "expected_observed_value", "expected_threshold"),
    (
        (AlertKind.READINESS_FAILURE, None, None),
        (AlertKind.QUEUE_AGE, 60, 60),
        (AlertKind.TERMINAL_RUN_FAILURE_RATE, 0.2, 0.2),
        (AlertKind.REPLAY_GAP, None, None),
        (AlertKind.OUTBOX_LAG, 30, 30),
        (AlertKind.APPROVAL_EXPIRY, None, None),
        (AlertKind.ROLLBACK, None, None),
    ),
)
def test_alert_service_persists_each_configured_trigger_with_safe_trace(
    kind: AlertKind,
    expected_observed_value: float | None,
    expected_threshold: float | None,
) -> None:
    """Each configured trigger kind retains its own redacted, traceable operator alert."""
    repository = InMemoryOperatorAlertRepository()
    service = AlertService(repository, _policy(), clock=lambda: _NOW)

    result = _evaluate_trigger(service, kind, _trace())

    assert result.is_success and result.value is not None and result.value.triggered
    alert = result.value.alert
    assert alert is not None
    assert alert.kind is kind
    assert alert.metadata.correlation_id == _CORRELATION
    assert alert.subject_reference == "run:alerts-1"
    assert alert.observed_value == expected_observed_value
    assert alert.threshold == expected_threshold
    assert alert.details["token"] == REDACTED
    assert alert.details["raw_prompt"] == REDACTED
    retained = repository.list_for_organization(_ORGANIZATION)
    assert retained.is_success and retained.value == (alert,)


def test_alert_service_skips_unconfigured_and_below_threshold_conditions() -> None:
    """Disabled monitors and values below thresholds do not create alerts."""
    repository = InMemoryOperatorAlertRepository()
    service = AlertService(
        repository,
        AlertPolicy(queue_age_seconds=60, terminal_run_failure_rate=0.2),
        clock=lambda: _NOW,
    )

    readiness = service.evaluate_readiness(_trace(), unavailable=True)
    queue_age = service.evaluate_queue_age(_trace(), age_seconds=59)
    failure_rate = service.evaluate_terminal_run_failure_rate(_trace(), failure_rate=0.19)
    retained = repository.list_for_organization(_ORGANIZATION)

    assert all(
        result.is_success and result.value is not None
        for result in (readiness, queue_age, failure_rate)
    )
    assert all(
        not result.value.triggered
        for result in (readiness, queue_age, failure_rate)
        if result.value
    )
    assert retained.is_success and retained.value == ()


def test_alert_service_generates_a_safe_correlation_for_subject_only_trace() -> None:
    """Subject-only operational signals remain traceable through a generated safe correlation ID."""
    repository = InMemoryOperatorAlertRepository()
    service = AlertService(repository, AlertPolicy(replay_gap_enabled=True), clock=lambda: _NOW)

    result = service.evaluate_replay_gap(_trace(correlation=None), detected=True)

    assert result.is_success and result.value is not None and result.value.alert is not None
    assert result.value.alert.subject_reference == "run:alerts-1"
    assert str(result.value.alert.metadata.correlation_id)
