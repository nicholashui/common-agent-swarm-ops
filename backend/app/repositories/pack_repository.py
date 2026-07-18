"""Atomic in-memory persistence for domain-pack registration outcomes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from threading import RLock

from app.models.common import OptimisticTransition, RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId, RecordId


class AgentLifecycleStatus(StrEnum):
    """The only non-active statuses accepted during pack registration."""

    DRAFT = "draft"
    REGISTERED = "registered"


class PackRegistrationStatus(StrEnum):
    """Durable result statuses for a pack registration attempt."""

    REGISTERED = "registered"
    INACTIVE = "inactive"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A stable, redaction-safe reason a manifest cannot be registered."""

    field: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PackAgentRecord:
    """An agent outcome that is always non-active at pack registration time."""

    agent_id: str | None
    supplied_status: str | None
    status: AgentLifecycleStatus | None
    production_active: bool = False
    production_activation_denied: bool = False

    def deny_production_activation(self) -> PackAgentRecord:
        """Return this agent with a durable production-activation denial."""
        return replace(self, production_active=False, production_activation_denied=True)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The complete validation result consumed by the atomic registration write."""

    is_valid: bool
    canonical_pack_id: str | None
    agents: tuple[PackAgentRecord, ...]
    issues: tuple[ValidationIssue, ...] = ()

    def with_issue(self, issue: ValidationIssue) -> ValidationReport:
        """Return an invalid report that retains every prior validation result."""
        return replace(self, is_valid=False, issues=(*self.issues, issue))


@dataclass(frozen=True, slots=True)
class DomainPackRecord:
    """A versioned pack outcome; no record produced here is production-active."""

    metadata: RecordMetadata
    pack_id: str | None
    manifest_digest: str
    status: PackRegistrationStatus
    agents: tuple[PackAgentRecord, ...]
    validation_report: ValidationReport

    @property
    def production_active(self) -> bool:
        """Registration never activates a pack in production."""
        return False


class InMemoryPackRepository:
    """Lock-protected local repository with an atomic canonical pack-ID index."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[RecordId, DomainPackRecord] = {}
        self._registered_pack_ids: dict[str, RecordId] = {}

    def record_outcome(
        self, record: DomainPackRecord
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Persist one complete valid or inactive outcome without partial agent writes."""
        with self._lock:
            if record.metadata.record_id in self._records:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Pack outcome already exists.")
                )

            persisted = self._inactive_for_duplicate_pack_id(record)
            self._records[persisted.metadata.record_id] = persisted
            if (
                persisted.status is PackRegistrationStatus.REGISTERED
                and persisted.pack_id is not None
            ):
                self._registered_pack_ids[persisted.pack_id] = persisted.metadata.record_id
            return Result.success(persisted)

    def create(self, record: DomainPackRecord) -> Result[DomainPackRecord, RepositoryError]:
        """Persist an initial registration outcome through the atomic write path."""
        return self.record_outcome(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Return an outcome only when it belongs to the requested organization."""
        with self._lock:
            record = self._records.get(record_id)
            if record is None or record.metadata.organization_id != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Pack outcome was not found.")
                )
            return Result.success(record)

    def get_by_pack_id(
        self, organization_id: OrganizationId, pack_id: str
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Return the sole registered record associated with a canonical pack ID."""
        with self._lock:
            record_id = self._registered_pack_ids.get(pack_id)
            record = self._records.get(record_id) if record_id is not None else None
            if record is None or record.metadata.organization_id != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Registered pack was not found.")
                )
            return Result.success(record)

    def transition(
        self,
        record: DomainPackRecord,
        transition: OptimisticTransition,
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Persist a later version only when its record identity and version match."""
        with self._lock:
            current = self._records.get(transition.record_id)
            if (
                current is None
                or current.metadata.organization_id != transition.organization_id
                or current.metadata.version != transition.expected_version
                or record.metadata.record_id != transition.record_id
                or record.metadata.organization_id != transition.organization_id
                or record.metadata.version != transition.expected_version + 1
                or record.pack_id != current.pack_id
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Pack outcome transition conflicts with current state.",
                    )
                )
            self._records[transition.record_id] = record
            return Result.success(record)

    def outcomes(self) -> tuple[DomainPackRecord, ...]:
        """Return immutable outcome snapshots for deterministic local inspection."""
        with self._lock:
            return tuple(self._records.values())

    def _inactive_for_duplicate_pack_id(self, record: DomainPackRecord) -> DomainPackRecord:
        if (
            record.status is not PackRegistrationStatus.REGISTERED
            or record.pack_id is None
            or record.pack_id not in self._registered_pack_ids
        ):
            return record
        duplicate_issue = ValidationIssue(
            "pack_id",
            "duplicate_registered_pack_id",
            "A pack with this canonical identifier is already registered.",
        )
        return replace(
            record,
            status=PackRegistrationStatus.INACTIVE,
            agents=tuple(agent.deny_production_activation() for agent in record.agents),
            validation_report=record.validation_report.with_issue(duplicate_issue),
        )

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("pack-repository"))
