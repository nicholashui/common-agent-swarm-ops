"""Nominal identifiers used by durable Host records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType
from uuid import UUID, uuid4

ActorId = NewType("ActorId", str)
ApprovalId = NewType("ApprovalId", str)
AuditEventId = NewType("AuditEventId", str)
CorrelationId = NewType("CorrelationId", str)
EvidenceId = NewType("EvidenceId", str)
EvaluationResultId = NewType("EvaluationResultId", str)
EvaluationRunId = NewType("EvaluationRunId", str)
OrganizationId = NewType("OrganizationId", str)
RecordId = NewType("RecordId", str)
RunId = NewType("RunId", str)
WorkflowDefinitionId = NewType("WorkflowDefinitionId", str)


def new_correlation_id() -> CorrelationId:
    """Return a request-safe correlation identifier."""
    return CorrelationId(str(uuid4()))


def new_record_id() -> RecordId:
    """Return a globally unique durable-record identifier."""
    return RecordId(str(uuid4()))


def new_evaluation_run_id() -> EvaluationRunId:
    """Return a unique evaluation execution identifier."""
    return EvaluationRunId(str(uuid4()))


def new_evaluation_result_id() -> EvaluationResultId:
    """Return a unique task/check evaluation-result identifier."""
    return EvaluationResultId(str(uuid4()))


def is_uuid_identifier(value: str) -> bool:
    """Return whether a string is a canonical UUID identifier."""
    try:
        UUID(value)
    except (TypeError, ValueError, AttributeError):
        return False
    return True


AgentId = NewType("AgentId", str)
AgentLearningContractId = NewType("AgentLearningContractId", str)
CommandId = NewType("CommandId", str)
DomainId = NewType("DomainId", str)
DomainPackId = NewType("DomainPackId", str)
HostContractId = NewType("HostContractId", str)
InvocationId = NewType("InvocationId", str)
PackContractId = NewType("PackContractId", str)


@dataclass(frozen=True, slots=True)
class CorrelationAwareIdentifier:
    """A structured identifier that cannot be detached from its request trace."""

    identifier: str
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("Identifiers must be non-empty.")
        if not str(self.correlation_id).strip():
            raise ValueError("Correlation identifiers must be non-empty.")

    @property
    def value(self) -> str:
        """Return the identifier value for serializers and repository keys."""
        return self.identifier


CorrelatedIdentifier = CorrelationAwareIdentifier


CorrelationAwareId = CorrelationAwareIdentifier
