"""Nominal identifiers used by durable Host records."""

from __future__ import annotations

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
