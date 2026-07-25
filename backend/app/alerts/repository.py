"""Append-only persistence port and deterministic fake for operator alerts."""

from __future__ import annotations

from threading import RLock
from typing import Protocol, runtime_checkable

from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import AlertId, OperatorAlert
from app.models.identifiers import OrganizationId


@runtime_checkable
class OperatorAlertRepository(Protocol):
    """Retain redacted alerts and expose them only inside their organization scope."""

    def append(self, alert: OperatorAlert) -> Result[OperatorAlert, RepositoryError]: ...

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[OperatorAlert, ...], RepositoryError]: ...


class InMemoryOperatorAlertRepository:
    """Thread-safe deterministic alert storage for isolated application composition and tests."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._alerts: dict[AlertId, OperatorAlert] = {}

    def append(self, alert: OperatorAlert) -> Result[OperatorAlert, RepositoryError]:
        """Append one immutable alert, rejecting only a duplicate alert identifier."""
        with self._lock:
            if alert.alert_id in self._alerts:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Operator alert already exists.",
                        alert.metadata.correlation_id,
                    )
                )
            self._alerts[alert.alert_id] = alert
            return Result.success(alert)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[OperatorAlert, ...], RepositoryError]:
        """Return organization-scoped alerts in detection order."""
        with self._lock:
            return Result.success(
                tuple(
                    alert
                    for alert in self._alerts.values()
                    if alert.metadata.organization_id == organization_id
                )
            )
