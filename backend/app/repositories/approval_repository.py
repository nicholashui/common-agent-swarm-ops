"""In-memory approval-gate persistence with immutable decision submissions."""

from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING

from app.models.common import OptimisticTransition
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import ApprovalId, CorrelationId, OrganizationId, RecordId

if TYPE_CHECKING:
    from app.governance.approvals import ApprovalDecision, ApprovalGate


class InMemoryApprovalRepository:
    """Lock-protected approval storage; decisions are append-only records."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._gates: dict[ApprovalId, ApprovalGate] = {}
        self._gate_record_ids: dict[RecordId, ApprovalId] = {}
        self._decisions: dict[ApprovalId, list[ApprovalDecision]] = {}
        self._decision_record_ids: set[RecordId] = set()

    def create(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]:
        """Persist one initial gate, rejecting duplicate durable identities."""
        with self._lock:
            duplicate = (
                record.approval_id in self._gates
                or record.metadata.record_id in self._gate_record_ids
            )
            if duplicate:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Approval gate already exists.")
                )
            self._gates[record.approval_id] = record
            self._gate_record_ids[record.metadata.record_id] = record.approval_id
            self._decisions[record.approval_id] = []
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[ApprovalGate, RepositoryError]:
        """Return a gate by durable record identity only within its organization."""
        with self._lock:
            approval_id = self._gate_record_ids.get(record_id)
            gate = self._gates.get(approval_id) if approval_id is not None else None
            return self._scoped_gate(organization_id, gate)

    def get_by_approval_id(
        self, organization_id: OrganizationId, approval_id: ApprovalId
    ) -> Result[ApprovalGate, RepositoryError]:
        """Return an approval gate by its public identifier within its organization."""
        with self._lock:
            return self._scoped_gate(organization_id, self._gates.get(approval_id))

    def transition(
        self, record: ApprovalGate, transition: OptimisticTransition
    ) -> Result[ApprovalGate, RepositoryError]:
        """Replace one gate only when durable identity and version checks match."""
        with self._lock:
            current = self._gates.get(record.approval_id)
            if (
                current is None
                or current.metadata.record_id != transition.record_id
                or current.metadata.organization_id != transition.organization_id
                or current.metadata.version != transition.expected_version
                or record.metadata.record_id != transition.record_id
                or record.metadata.organization_id != transition.organization_id
                or record.metadata.version != transition.expected_version + 1
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Approval gate transition conflicts with current state.",
                    )
                )
            self._gates[record.approval_id] = record
            return Result.success(record)

    def append_decision(
        self, decision: ApprovalDecision
    ) -> Result[ApprovalDecision, RepositoryError]:
        """Append one immutable decision only to its owning organization gate."""
        with self._lock:
            gate = self._gates.get(decision.approval_id)
            if gate is None or gate.metadata.organization_id != decision.metadata.organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Approval gate was not found.")
                )
            if decision.metadata.record_id in self._decision_record_ids:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Approval decision already exists.")
                )
            self._decisions[decision.approval_id].append(decision)
            self._decision_record_ids.add(decision.metadata.record_id)
            return Result.success(decision)

    def decisions(
        self, organization_id: OrganizationId, approval_id: ApprovalId
    ) -> Result[tuple[ApprovalDecision, ...], RepositoryError]:
        """Return immutable appended submissions only to the gate's organization."""
        with self._lock:
            gate_result = self._scoped_gate(organization_id, self._gates.get(approval_id))
            if not gate_result.is_success:
                return Result.failure(self._required_error(gate_result))
            return Result.success(tuple(self._decisions[approval_id]))

    def records(self) -> tuple[ApprovalGate, ...]:
        """Return immutable gate snapshots for deterministic local inspection."""
        with self._lock:
            return tuple(self._gates.values())

    def _scoped_gate(
        self, organization_id: OrganizationId, gate: ApprovalGate | None
    ) -> Result[ApprovalGate, RepositoryError]:
        if gate is None or gate.metadata.organization_id != organization_id:
            return Result.failure(self._error(ErrorCode.NOT_FOUND, "Approval gate was not found."))
        return Result.success(gate)

    @staticmethod
    def _required_error(result: Result[ApprovalGate, RepositoryError]) -> RepositoryError:
        if result.error is None:
            raise RuntimeError("A failed approval repository result did not contain an error.")
        return result.error

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("approval-repository"))
