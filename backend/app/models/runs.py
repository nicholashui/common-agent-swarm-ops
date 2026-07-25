"""Versioned run records shared by all workflow engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata, validate_semantic_version
from app.models.control_plane import (
    AgentNodeAttemptId,
    RunProvenanceId,
    _validate_adoption_metadata,
)
from app.models.evidence import EvidenceReference
from app.models.identifiers import AgentId, DomainId, DomainPackId, RunId, WorkflowDefinitionId
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
    provenance_id: RunProvenanceId | None = None
    dispatch_attempts: tuple[DispatchAttempt, ...] = ()
    tool_effects: tuple[ToolEffect, ...] = ()
    failure: FailureState | None = None
    output: Mapping[str, object] | None = None
    graph_id: str | None = None
    graph_thread_id: str | None = None
    invocation_association_id: str | None = None
    pack_id: DomainPackId | None = None
    pack_version: str | None = None
    host_contract_version: str | None = None
    alc_version: str | None = None

    def __post_init__(self) -> None:
        """Keep queued records safe to retry and dispatch attempts uniquely addressable."""
        if self.provenance_id is not None and not str(self.provenance_id).strip():
            raise ValueError("Run provenance identifiers must be non-empty when present.")
        for value, name in (
            (self.invocation_association_id, "invocation_association_id"),
            (str(self.pack_id) if self.pack_id is not None else None, "pack_id"),
        ):
            if value is not None and not value.strip():
                raise ValueError(f"{name} must be non-empty when present.")
        for value, name in (
            (self.pack_version, "pack_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
        ):
            if value is not None:
                validate_semantic_version(value, name)
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
        return (
            bool(self.dispatch_attempts)
            and self.status is RunStatus.QUEUED
            and all(
                attempt.status is DispatchAttemptStatus.FAILED for attempt in self.dispatch_attempts
            )
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


class AgentNodeAttemptStatus(StrEnum):
    """Execution state for one immutable Agent_Node_Attempt identity."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    RETRIED = "retried"
    ESCALATED = "escalated"


@dataclass(frozen=True, slots=True)
class AgentNodeAttempt:
    """Run-scoped node attempt that can receive one terminal Learning_Episode."""

    metadata: RecordMetadata
    attempt_id: AgentNodeAttemptId
    run_id: RunId
    node_id: str
    organization_id: str
    domain_id: DomainId
    pack_id: DomainPackId
    pack_version: str
    agent_id: AgentId
    workflow_id: str
    status: AgentNodeAttemptStatus
    terminal_outcome_reference: str | None = None
    retrieval_record_reference: str | None = None

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.attempt_id), "attempt_id"),
            (str(self.run_id), "run_id"),
            (self.node_id, "node_id"),
            (self.organization_id, "organization_id"),
            (str(self.domain_id), "domain_id"),
            (str(self.pack_id), "pack_id"),
            (self.pack_version, "pack_version"),
            (str(self.agent_id), "agent_id"),
            (self.workflow_id, "workflow_id"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")
        if self.organization_id != str(self.metadata.organization_id):
            raise ValueError("Attempt organization must match record metadata.")
        validate_semantic_version(self.pack_version, "pack_version")
        object.__setattr__(self, "status", AgentNodeAttemptStatus(self.status))
        if (
            self.status
            in {
                AgentNodeAttemptStatus.COMPLETED,
                AgentNodeAttemptStatus.FAILED,
                AgentNodeAttemptStatus.BLOCKED,
                AgentNodeAttemptStatus.RETRIED,
                AgentNodeAttemptStatus.ESCALATED,
            }
            and not self.terminal_outcome_reference
        ):
            raise ValueError("Terminal node attempts require an outcome reference.")
        for optional_value, name in (
            (self.terminal_outcome_reference, "terminal_outcome_reference"),
            (self.retrieval_record_reference, "retrieval_record_reference"),
        ):
            if optional_value is not None and not optional_value.strip():
                raise ValueError(f"{name} must be non-empty when present.")
