"""Workflow run creation, idempotent dispatch, and durable state transitions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from typing import ClassVar
from uuid import uuid4

from app.engines.migration import LegacyExecutionAvailability
from app.models.common import SCHEMA_VERSION, OptimisticTransition, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AuditRecord,
    GraphValidationReport,
    InvocationAssociation,
    RunProvenanceId,
)
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
    new_record_id,
)
from app.models.runs import (
    DispatchAttempt,
    DispatchAttemptStatus,
    RunRecord,
    RunStatus,
    WorkflowEngineKind,
)
from app.registry.compatibility import CompatibilityRegistry
from app.repositories.protocols import (
    AuditRecordRepository,
    InvocationAssociationRepository,
    RunRepository,
)
from app.workflows.validator import RegisteredReferences, WorkflowDefinitionValidator


def _library_definition(definition: Mapping[str, object]) -> dict[str, object]:
    """Restore retained immutable snapshots to JSON-compatible library input values."""
    return {str(key): _library_value(value) for key, value in definition.items()}


def _library_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _library_definition(value)
    if isinstance(value, tuple | frozenset):
        return [_library_value(item) for item in value]
    return value


DispatchStarter = Callable[[RunRecord], None]


@dataclass(frozen=True, slots=True)
class DispatchOutcome:
    """A persisted dispatch observation that callers may safely audit or retry from."""

    record: RunRecord
    attempt: DispatchAttempt
    is_idempotent: bool
    retry_permitted: bool
    dispatch_error: ErrorDetail | None = None


class RunService:
    """Own the ordering between valid definition checks, queue persistence, and dispatch."""

    _ALLOWED_TRANSITIONS: ClassVar[dict[RunStatus, frozenset[RunStatus]]] = {
        RunStatus.QUEUED: frozenset({RunStatus.DISPATCHING, RunStatus.CANCELLED}),
        RunStatus.DISPATCHING: frozenset(
            {
                RunStatus.QUEUED,
                RunStatus.WAITING_FOR_APPROVAL,
                RunStatus.COMPLETED,
                RunStatus.FAILED,
                RunStatus.CANCELLED,
            }
        ),
        RunStatus.WAITING_FOR_APPROVAL: frozenset(
            {RunStatus.DISPATCHING, RunStatus.FAILED, RunStatus.CANCELLED}
        ),
        RunStatus.COMPLETED: frozenset(),
        RunStatus.FAILED: frozenset(),
        RunStatus.CANCELLED: frozenset(),
    }

    def __init__(
        self,
        repository: RunRepository,
        registered_references: RegisteredReferences,
        clock: Callable[[], datetime] = utc_now,
        legacy_execution_availability: LegacyExecutionAvailability | None = None,
        *,
        invocation_association_repository: InvocationAssociationRepository | None = None,
        association_repository: InvocationAssociationRepository | None = None,
        audit_repository: AuditRecordRepository | None = None,
        compatibility_registry: CompatibilityRegistry | None = None,
    ) -> None:
        self._repository = repository
        self._validator = WorkflowDefinitionValidator(registered_references)
        self._clock = clock
        self._legacy_execution_availability = legacy_execution_availability
        self._association_repository = invocation_association_repository or association_repository
        self._audit_repository = audit_repository
        self._compatibility_registry = compatibility_registry

    def create_queued_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        definition: Mapping[str, object],
        *,
        provenance_id: RunProvenanceId | None = None,
        validated_graph_report: GraphValidationReport | None = None,
    ) -> Result[RunRecord, ErrorDetail]:
        """Validate and persist a uniquely identified queued run before any dispatch occurs."""
        library_definition = _library_definition(definition)
        if validated_graph_report is None:
            report = self._validator.validate(library_definition)
            if not report.is_valid:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "Workflow definition must pass validation before a run is created.",
                        correlation_id,
                        fields=tuple(
                            ErrorField(issue.field, issue.reason) for issue in report.issues
                        ),
                    )
                )
        elif (
            not validated_graph_report.eligible_for_run
            or validated_graph_report.workflow_definition != definition
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Validated graph evidence does not authorize this workflow definition.",
                    correlation_id,
                )
            )
        definition = library_definition
        definition_id = definition.get("id")
        version = definition.get("version")
        engine = definition.get("engine")
        if (
            not isinstance(definition_id, str)
            or not isinstance(version, str)
            or not isinstance(engine, str)
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Workflow definition identity is invalid.",
                    correlation_id,
                )
            )
        try:
            definition_digest = self._definition_digest(definition)
            selected_engine = WorkflowEngineKind(engine)
        except (TypeError, ValueError):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Workflow definition could not be normalized for persistence.",
                    correlation_id,
                )
            )
        if (
            selected_engine is WorkflowEngineKind.LEGACY
            and self._legacy_execution_availability is not None
            and not self._legacy_execution_availability.is_available()
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    (
                        "LegacyEngine is unavailable because migration retirement "
                        "evidence is retained."
                    ),
                    correlation_id,
                )
            )
        now = self._clock()
        run_identifier = str(uuid4())
        record = RunRecord(
            metadata=RecordMetadata(
                record_id=RecordId(run_identifier),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            run_id=RunId(run_identifier),
            workflow_definition_id=WorkflowDefinitionId(definition_id),
            workflow_definition_version=version,
            workflow_definition_digest=definition_digest,
            engine=selected_engine,
            status=RunStatus.QUEUED,
            created_for_dispatch_at=now,
            provenance_id=provenance_id,
        )
        persisted = self._repository.create_queued(record)
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def persist_invocation_association(
        self,
        association: InvocationAssociation,
        *,
        pack_id: DomainPackId | None = None,
    ) -> Result[InvocationAssociation, ErrorDetail]:
        """Persist the complete invocation association before an execution can start."""
        repository = self._association_repository
        if repository is None:
            return self._association_denied(association, "association persistence is unavailable")
        compatibility_error = self._compatibility_error(
            association, pack_id=pack_id, correlation_id=association.correlation_id
        )
        if compatibility_error is not None:
            return Result.failure(compatibility_error)
        if association.metadata.organization_id != association.organization_id:
            return self._association_denied(association, "association organization is invalid")
        try:
            persisted = repository.append(association)
        except Exception:
            persisted = Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Invocation association persistence is unavailable.",
                    association.correlation_id,
                    retryable=True,
                )
            )
        if persisted.is_success:
            return persisted
        return self._association_denied(association, "association persistence failed")

    def begin_invocation(
        self,
        association: InvocationAssociation,
        node_starter: Callable[[InvocationAssociation], None] | None = None,
        *,
        pack_id: DomainPackId | None = None,
    ) -> Result[InvocationAssociation, ErrorDetail]:
        """Persist association, then optionally start a node only after persistence succeeds."""
        persisted = self.persist_invocation_association(association, pack_id=pack_id)
        if not persisted.is_success or node_starter is None:
            return persisted
        try:
            node_starter(association)
        except Exception:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "The agent node could not start after invocation association.",
                    association.correlation_id,
                    retryable=True,
                )
            )
        return persisted

    submit_invocation = begin_invocation

    def dispatch(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        idempotency_key: str,
        starter: DispatchStarter,
        correlation_id: CorrelationId,
        *,
        association: InvocationAssociation | None = None,
        pack_id: DomainPackId | None = None,
    ) -> Result[DispatchOutcome, ErrorDetail]:
        """Claim one queued request, invoke its starter once, and requeue only
        durably failed starts."""
        if not idempotency_key or not idempotency_key.strip():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A non-empty dispatch idempotency key is required.",
                    correlation_id,
                )
            )
        fetched = self._repository.get_by_run_id(organization_id, run_id)
        if not fetched.is_success:
            return Result.failure(self._with_correlation(fetched.error, correlation_id))
        current = self._required_value(fetched)
        prior_attempt = self._find_attempt(current, idempotency_key)
        if prior_attempt is not None:
            return Result.success(
                DispatchOutcome(
                    record=current,
                    attempt=prior_attempt,
                    is_idempotent=True,
                    retry_permitted=(
                        current.status is RunStatus.QUEUED
                        and prior_attempt.status is DispatchAttemptStatus.FAILED
                    ),
                    dispatch_error=(
                        self._dispatch_failure(correlation_id)
                        if prior_attempt.status is DispatchAttemptStatus.FAILED
                        else None
                    ),
                )
            )
        association_value, association_error = self._ensure_dispatch_association(
            current,
            association,
            pack_id=pack_id,
            correlation_id=correlation_id,
        )
        if association_error is not None:
            return Result.failure(association_error)
        if current.status is not RunStatus.QUEUED:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Only queued runs may be dispatched.",
                    correlation_id,
                )
            )
        if (
            current.engine is WorkflowEngineKind.LEGACY
            and self._legacy_execution_availability is not None
            and not self._legacy_execution_availability.is_available()
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    (
                        "LegacyEngine is unavailable because migration retirement "
                        "evidence is retained."
                    ),
                    correlation_id,
                )
            )

        attempt = DispatchAttempt(idempotency_key, self._clock(), DispatchAttemptStatus.STARTED)
        claimed = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            status=RunStatus.DISPATCHING,
            dispatch_attempts=(*current.dispatch_attempts, attempt),
            invocation_association_id=(
                str(association_value.invocation_id)
                if association_value is not None
                else current.invocation_association_id
            ),
            pack_id=pack_id or current.pack_id,
            pack_version=(
                association_value.pack_version
                if association_value is not None
                else current.pack_version
            ),
        )
        persisted_claim = self._repository.transition(
            claimed,
            self._transition_for(current, correlation_id),
        )
        if not persisted_claim.is_success:
            return self._dispatch_conflict_or_failure(
                organization_id, run_id, idempotency_key, correlation_id
            )

        try:
            starter(claimed)
        except Exception:
            return self._requeue_after_dispatch_failure(claimed, attempt, correlation_id)
        return Result.success(
            DispatchOutcome(
                record=claimed,
                attempt=attempt,
                is_idempotent=False,
                retry_permitted=False,
            )
        )

    def transition_status(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        expected_status: RunStatus,
        target_status: RunStatus,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Durably advance a run only across an allowed version-checked lifecycle edge."""
        fetched = self._repository.get_by_run_id(organization_id, run_id)
        if not fetched.is_success:
            return Result.failure(self._with_correlation(fetched.error, correlation_id))
        current = self._required_value(fetched)
        if current.status is not expected_status:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "Run status changed before its transition could be persisted.",
                    correlation_id,
                    retryable=True,
                )
            )
        if target_status not in self._ALLOWED_TRANSITIONS[current.status]:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "The requested run status transition is not permitted.",
                    correlation_id,
                )
            )
        updated = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            status=target_status,
        )
        transitioned = self._repository.transition(
            updated,
            self._transition_for(current, correlation_id),
        )
        if not transitioned.is_success:
            return Result.failure(self._with_correlation(transitioned.error, correlation_id))
        return transitioned

    def _ensure_dispatch_association(
        self,
        current: RunRecord,
        supplied: InvocationAssociation | None,
        *,
        pack_id: DomainPackId | None,
        correlation_id: CorrelationId,
    ) -> tuple[InvocationAssociation | None, ErrorDetail | None]:
        repository = self._association_repository
        if repository is None:
            if supplied is None and self._compatibility_registry is None:
                return None, None
            if supplied is None:
                return None, self._association_context_error(
                    current.metadata.organization_id,
                    correlation_id,
                    str(current.run_id),
                    "Invocation association is required before submission.",
                )
            persisted = self.persist_invocation_association(supplied, pack_id=pack_id)
            return persisted.value, persisted.error

        candidate = supplied
        if candidate is not None:
            if (
                candidate.organization_id != current.metadata.organization_id
                or candidate.run_id != current.run_id
            ):
                return None, self._association_context_error(
                    current.metadata.organization_id,
                    correlation_id,
                    str(candidate.invocation_id),
                    "Invocation association does not match the requested run.",
                )
            existing = repository.get_by_invocation_id(
                current.metadata.organization_id, str(candidate.invocation_id)
            )
            if existing.is_success and existing.value is not None:
                candidate = existing.value
            else:
                persisted = self.persist_invocation_association(candidate, pack_id=pack_id)
                if not persisted.is_success:
                    return None, persisted.error
                candidate = persisted.value
        elif current.invocation_association_id is not None:
            existing = repository.get_by_invocation_id(
                current.metadata.organization_id, current.invocation_association_id
            )
            if not existing.is_success or existing.value is None:
                return None, self._association_context_error(
                    current.metadata.organization_id,
                    correlation_id,
                    current.invocation_association_id,
                    "Invocation association could not be loaded before submission.",
                )
            candidate = existing.value
        else:
            return None, self._association_context_error(
                current.metadata.organization_id,
                correlation_id,
                str(current.run_id),
                "Invocation association is required before submission.",
            )

        assert candidate is not None
        compatibility_error = self._compatibility_error(
            candidate,
            pack_id=pack_id or current.pack_id,
            correlation_id=correlation_id,
        )
        return candidate, compatibility_error

    def _association_denied(
        self, association: InvocationAssociation, reason: str
    ) -> Result[InvocationAssociation, ErrorDetail]:
        return Result.failure(
            self._association_context_error(
                association.organization_id,
                association.correlation_id,
                str(association.invocation_id),
                f"Invocation denied because {reason}.",
            )
        )

    def _association_context_error(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        subject_reference: str,
        message: str,
    ) -> ErrorDetail:
        self._write_association_denial_audit(
            organization_id,
            correlation_id,
            subject_reference,
            "invocation.association.denied",
        )
        return ErrorDetail(ErrorCode.AUTHORIZATION_DENIED, message, correlation_id)

    def _write_association_denial_audit(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        subject_reference: str,
        action: str,
    ) -> None:
        repository = self._audit_repository
        if repository is None:
            return
        now = self._clock()
        audit = AuditRecord(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=subject_reference,
            outcome="denied:association_persistence_failed",
            recorded_at=now,
        )
        try:
            repository.append(audit)
        except Exception:
            return

    def _compatibility_error(
        self,
        association: InvocationAssociation,
        *,
        pack_id: DomainPackId | None,
        correlation_id: CorrelationId,
    ) -> ErrorDetail | None:
        registry = self._compatibility_registry
        if registry is None:
            return None
        if pack_id is None:
            return ErrorDetail(
                ErrorCode.AUTHORIZATION_DENIED,
                "Invocation submission is denied without a Domain_Pack identity.",
                correlation_id,
            )
        decision = registry.guard_invocation(
            pack_id,
            association.pack_version,
            correlation_id=correlation_id,
        )
        if bool(decision):
            return None
        reason = getattr(decision, "reason", "incompatible Domain_Pack version")
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            f"Invocation submission denied: {reason}",
            correlation_id,
        )

    def _requeue_after_dispatch_failure(
        self,
        claimed: RunRecord,
        attempt: DispatchAttempt,
        correlation_id: CorrelationId,
    ) -> Result[DispatchOutcome, ErrorDetail]:
        failure = self._dispatch_failure(correlation_id)
        failed_attempt = replace(
            attempt,
            status=DispatchAttemptStatus.FAILED,
            failure_code=failure.code,
        )
        requeued = replace(
            claimed,
            metadata=self._next_metadata(claimed, correlation_id),
            status=RunStatus.QUEUED,
            dispatch_attempts=(*claimed.dispatch_attempts[:-1], failed_attempt),
        )
        persisted = self._repository.transition(
            requeued,
            self._transition_for(claimed, correlation_id),
        )
        if not persisted.is_success:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Queued run state could not be retained after dispatch failure.",
                    correlation_id,
                )
            )
        return Result.success(
            DispatchOutcome(
                record=requeued,
                attempt=failed_attempt,
                is_idempotent=False,
                retry_permitted=True,
                dispatch_error=failure,
            )
        )

    def _dispatch_conflict_or_failure(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        idempotency_key: str,
        correlation_id: CorrelationId,
    ) -> Result[DispatchOutcome, ErrorDetail]:
        """Return an existing same-key attempt after a race, never invoke a second starter."""
        refreshed = self._repository.get_by_run_id(organization_id, run_id)
        if refreshed.is_success:
            record = self._required_value(refreshed)
            attempt = self._find_attempt(record, idempotency_key)
            if attempt is not None:
                return Result.success(
                    DispatchOutcome(
                        record=record,
                        attempt=attempt,
                        is_idempotent=True,
                        retry_permitted=(
                            record.status is RunStatus.QUEUED
                            and attempt.status is DispatchAttemptStatus.FAILED
                        ),
                        dispatch_error=(
                            self._dispatch_failure(correlation_id)
                            if attempt.status is DispatchAttemptStatus.FAILED
                            else None
                        ),
                    )
                )
        return Result.failure(
            ErrorDetail(
                ErrorCode.CONFLICT,
                "Run dispatch state changed before the attempt could be persisted.",
                correlation_id,
                retryable=True,
            )
        )

    def _next_metadata(self, record: RunRecord, correlation_id: CorrelationId) -> RecordMetadata:
        return replace(
            record.metadata,
            correlation_id=correlation_id,
            version=record.metadata.version + 1,
            updated_at=self._clock(),
        )

    @staticmethod
    def _transition_for(record: RunRecord, correlation_id: CorrelationId) -> OptimisticTransition:
        return OptimisticTransition(
            record_id=record.metadata.record_id,
            organization_id=record.metadata.organization_id,
            expected_version=record.metadata.version,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _find_attempt(record: RunRecord, idempotency_key: str) -> DispatchAttempt | None:
        return next(
            (
                attempt
                for attempt in record.dispatch_attempts
                if attempt.idempotency_key == idempotency_key
            ),
            None,
        )

    @staticmethod
    def _definition_digest(definition: Mapping[str, object]) -> str:
        normalized = json.dumps(dict(definition), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _dispatch_failure(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "The selected workflow engine could not start the queued run.",
            correlation_id,
            retryable=True,
        )

    @staticmethod
    def _with_correlation(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Run storage is unavailable.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @staticmethod
    def _required_value(result: Result[RunRecord, ErrorDetail]) -> RunRecord:
        if result.value is None:
            raise RuntimeError("A successful run repository result did not contain a run record.")
        return result.value
