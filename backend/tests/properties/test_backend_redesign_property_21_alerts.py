"""Property checks for traceable, redaction-safe operational alerts."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.alerts.repository import InMemoryOperatorAlertRepository
from app.alerts.service import AlertEvaluation, AlertPolicy, AlertService, AlertTrace
from app.models.contracts import ErrorDetail, Result
from app.models.control_plane import AlertKind
from app.models.identifiers import CorrelationId, OrganizationId
from app.models.redaction import REDACTED

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-21-organization")
_TRACE_VARIANTS = ("correlation", "subject", "both")
_SAFE_IDENTIFIER_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


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


def _trace(trace_variant: str, identifier: str) -> AlertTrace:
    correlation = CorrelationId(f"property-21-correlation-{identifier}")
    subject = f"run:property-21-{identifier}"
    if trace_variant == "correlation":
        return AlertTrace(organization_id=_ORGANIZATION, correlation_id=correlation)
    if trace_variant == "subject":
        return AlertTrace(organization_id=_ORGANIZATION, subject_reference=subject)
    return AlertTrace(
        organization_id=_ORGANIZATION,
        correlation_id=correlation,
        subject_reference=subject,
    )


def _evaluate(
    service: AlertService,
    kind: AlertKind,
    trace: AlertTrace,
    details: Mapping[str, object],
) -> Result[AlertEvaluation, ErrorDetail]:
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


# Feature: backend-redesign, Property 21: Configured degradation creates traceable safe alerts.
# **Validates: Requirements 17.1**
@settings(max_examples=100, derandomize=True)
@given(
    kind=st.sampled_from(tuple(AlertKind)),
    trace_variant=st.sampled_from(_TRACE_VARIANTS),
    identifier=st.text(alphabet=_SAFE_IDENTIFIER_ALPHABET, min_size=1, max_size=20),
    sensitive_sentinel=st.text(alphabet=_SAFE_IDENTIFIER_ALPHABET, min_size=1, max_size=20),
)
def test_property_21_configured_degradation_creates_traceable_safe_alerts(
    kind: AlertKind,
    trace_variant: str,
    identifier: str,
    sensitive_sentinel: str,
) -> None:
    """Every configured degraded condition retains exactly one redacted traceable alert."""
    repository = InMemoryOperatorAlertRepository()
    service = AlertService(repository, _policy(), clock=lambda: _NOW)
    trace = _trace(trace_variant, identifier)
    secret = f"property-21-secret-{sensitive_sentinel}"
    details = {
        "token": secret,
        "raw_prompt": secret,
        "nested": {"protected_artifact": secret},
        "message": f"token={secret}",
    }

    result = _evaluate(service, kind, trace, details)

    assert result.is_success and result.value is not None
    assert result.value.triggered and result.value.alert is not None
    alert = result.value.alert
    retained = repository.list_for_organization(_ORGANIZATION)
    assert retained.is_success and retained.value == (alert,)
    assert alert.kind is kind
    assert alert.details == {
        "token": REDACTED,
        "raw_prompt": REDACTED,
        "nested": {"protected_artifact": REDACTED},
        "message": REDACTED,
    }
    assert secret not in repr(alert)

    if trace.correlation_id is not None:
        assert alert.metadata.correlation_id == trace.correlation_id
    else:
        assert str(alert.metadata.correlation_id).strip()
    assert alert.subject_reference == trace.subject_reference
