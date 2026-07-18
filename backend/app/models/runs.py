"""Versioned run records shared by all workflow engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import RunId, WorkflowDefinitionId
from app.models.redaction import redact_mapping


class WorkflowEngineKind(StrEnum):
    """Host-supported execution engines persisted with each run."""

    GRAPH = "graph"
    LEGACY = "legacy"


class RunStatus(StrEnum):
    """Durable lifecycle states for an execution."""

    QUEUED = "queued"
    DISPATCHING = "dispatching"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DispatchAttemptStatus(StrEnum):
    """The persisted outcome of one idempotent request to start a queued run."""

    STARTED = "started"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class DispatchAttempt:
    """A durable dispatch request identity and its observable outcome."""

    idempotency_key: str
    requested_at: datetime
    status: DispatchAttemptStatus
    failure_code: str | None = None

    def __post_init__(self) -> None:
        """Reject ambiguous request identities and outcome states at the model boundary."""
        if not self.idempotency_key.strip():
            raise ValueError("Dispatch attempt idempotency keys must be non-empty.")
        if self.status is DispatchAttemptStatus.FAILED and not self.failure_code:
            raise ValueError("Failed dispatch attempts must retain a failure code.")
        if self.status is DispatchAttemptStatus.STARTED and self.failure_code is not None:
            raise ValueError("Started dispatch attempts cannot retain a failure code.")


@dataclass(frozen=True, slots=True)
class ToolEffect:
    """Durable evidence of an adapter result, never the raw adapter payload."""

    adapter_id: str
    request_digest: str
    outcome: str
    effect_digest: str
    completed_at: datetime
    reversible: bool
    compensation_reference: str | None = None


@dataclass(frozen=True, slots=True)
class FailureState:
    """Failure evidence and completion obligations for a failed run."""

    code: str
    evidence_references: tuple[EvidenceReference, ...]
    stopped_step_ids: tuple[str, ...]
    failure_processing_complete: bool


@dataclass(frozen=True, slots=True)
class RunRecord:
    """The immutable, durably versioned state of one workflow execution."""

    metadata: RecordMetadata
    run_id: RunId
    workflow_definition_id: WorkflowDefinitionId
    workflow_definition_version: str
    workflow_definition_digest: str
    engine: WorkflowEngineKind
    status: RunStatus
    created_for_dispatch_at: datetime
    dispatch_attempts: tuple[DispatchAttempt, ...] = ()
    tool_effects: tuple[ToolEffect, ...] = ()
    failure: FailureState | None = None
    output: Mapping[str, object] | None = None
    graph_id: str | None = None
    graph_thread_id: str | None = None

    def __post_init__(self) -> None:
        """Keep queued records safe to retry and dispatch attempts uniquely addressable."""
        attempt_keys = tuple(attempt.idempotency_key for attempt in self.dispatch_attempts)
        if len(attempt_keys) != len(set(attempt_keys)):
            raise ValueError("Run dispatch attempt idempotency keys must be unique.")
        if self.status is RunStatus.QUEUED and any(
            attempt.status is DispatchAttemptStatus.STARTED for attempt in self.dispatch_attempts
        ):
            raise ValueError("Queued runs cannot retain an unresolved dispatch attempt.")

    @property
    def is_dispatch_retryable(self) -> bool:
        """Return whether a failed dispatch is durably retained in the queued state."""
        return bool(self.dispatch_attempts) and self.status is RunStatus.QUEUED and all(
            attempt.status is DispatchAttemptStatus.FAILED for attempt in self.dispatch_attempts
        )

    def to_projection(self) -> RunProjection:
        """Return a redacted, operator-safe run representation."""
        return RunProjection(
            run_id=self.run_id,
            correlation_id=self.metadata.correlation_id,
            status=self.status,
            engine=self.engine,
            updated_at=self.metadata.updated_at,
            output=redact_mapping(self.output) if self.output is not None else None,
            failure_code=self.failure.code if self.failure is not None else None,
        )


@dataclass(frozen=True, slots=True)
class RunProjection:
    """Redaction-safe execution state exposed to operators."""

    run_id: RunId
    correlation_id: str
    status: RunStatus
    engine: WorkflowEngineKind
    updated_at: datetime
    output: Mapping[str, object] | None
    failure_code: str | None
