"""Safe append-only audit writer with an optional alternate local sink."""

from __future__ import annotations

from dataclasses import dataclass, replace

from app.models.audit import AuditEvent
from app.repositories.protocols import AuditRepository


@dataclass(frozen=True, slots=True)
class AuditWriteResult:
    """The non-throwing outcome of attempting to retain an audit event."""

    recorded: bool
    alternate_sink_used: bool = False


class AuditWriter:
    """Write audit events to a primary sink, then one configured local alternative."""

    def __init__(
        self,
        primary_repository: AuditRepository,
        alternate_repository: AuditRepository | None = None,
    ) -> None:
        self._primary_repository = primary_repository
        self._alternate_repository = alternate_repository

    def append(self, event: AuditEvent) -> AuditWriteResult:
        """Record an event without allowing an audit outage to permit an action."""
        if self._append_to(self._primary_repository, event):
            return AuditWriteResult(recorded=True)
        if self._alternate_repository is None:
            return AuditWriteResult(recorded=False)
        alternate_event = replace(event, alternate_sink_used=True)
        if self._append_to(self._alternate_repository, alternate_event):
            return AuditWriteResult(recorded=True, alternate_sink_used=True)
        return AuditWriteResult(recorded=False)

    def check_health(self, probe: AuditEvent) -> AuditWriteResult:
        """Confirm that the primary or alternate sink can durably retain an audit probe."""
        return self.append(probe)

    @staticmethod
    def _append_to(repository: AuditRepository, event: AuditEvent) -> bool:
        """Treat repository exceptions and typed failures as unavailable audit storage."""
        try:
            return repository.append(event).is_success
        except Exception:
            return False
