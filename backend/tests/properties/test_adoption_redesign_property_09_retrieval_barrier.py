"""Property checks for pre-action retrieval evidence barriers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.learning_lifecycle import LearningLifecycleService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import AgentNodeAttemptId
from app.models.evidence import RetrievalRecord
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import AgentNodeAttempt, AgentNodeAttemptStatus
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class _RetrievalCase:
    """Bounded retrieval results, approved scope, and persistence outcome."""

    case_id: int
    memory_scope: str
    lesson_references: tuple[str, ...]
    persistence_failure: bool


@st.composite
def _retrieval_cases(draw: st.DrawFn) -> _RetrievalCase:
    """Generate empty or non-empty lesson results and retrieval write failures."""
    case_id = draw(st.integers(min_value=0, max_value=10_000))
    lesson_ids = draw(
        st.lists(
            st.integers(min_value=0, max_value=100),
            min_size=0,
            max_size=3,
            unique=True,
        )
    )
    scope_id = draw(st.integers(min_value=0, max_value=10_000))
    return _RetrievalCase(
        case_id=case_id,
        memory_scope=f"agent:{case_id}:memory:{scope_id}",
        lesson_references=tuple(f"lesson:{case_id}:{lesson_id}" for lesson_id in lesson_ids),
        persistence_failure=draw(st.booleans()),
    )


def _attempt(case: _RetrievalCase) -> AgentNodeAttempt:
    """Build a queued learning-required node attempt for one generated case."""
    organization_id = OrganizationId(f"organization-property-9-{case.case_id}")
    correlation_id = CorrelationId(f"correlation-property-9-{case.case_id}")
    return AgentNodeAttempt(
        metadata=RecordMetadata(
            record_id=RecordId(f"attempt-record-property-9-{case.case_id}"),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        attempt_id=AgentNodeAttemptId(f"attempt-property-9-{case.case_id}"),
        run_id=RunId(f"run-property-9-{case.case_id}"),
        node_id=f"node-property-9-{case.case_id}",
        organization_id=str(organization_id),
        domain_id=DomainId(f"domain-property-9-{case.case_id}"),
        pack_id=DomainPackId(f"pack-property-9-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=AgentId(f"agent-property-9-{case.case_id}"),
        workflow_id=f"workflow-property-9-{case.case_id}",
        status=AgentNodeAttemptStatus.QUEUED,
    )


def _service(repositories: DeterministicAdoptionRepositories) -> LearningLifecycleService:
    """Compose the lifecycle service entirely from deterministic repository fakes."""
    return LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        clock=lambda: _NOW,
    )


# Feature: adoption-redesign, Property 9: Retrieval evidence precedes learning-required execution
# **Validates: Requirements 4.7, 4.8**
@settings(max_examples=100, deadline=None)
@given(case=_retrieval_cases())
def test_property_09_retrieval_evidence_precedes_learning_required_execution(
    case: _RetrievalCase,
) -> None:
    """Exactly one retrieval record crosses the barrier before action execution."""
    failure_plan = FakeFailurePlan(
        persistence_operations={"retrieval.append"} if case.persistence_failure else set()
    )
    repositories = DeterministicAdoptionRepositories(failure_plan)
    service = _service(repositories)
    attempt = _attempt(case)
    approved_filters = {
        "organization_id": attempt.organization_id,
        "domain_id": str(attempt.domain_id),
        "pack_version": attempt.pack_version,
        "agent_id": str(attempt.agent_id),
        "memory_scope": case.memory_scope,
    }
    execution_observations: list[tuple[int, tuple[str, ...]]] = []

    def execute(retrieval_record: RetrievalRecord) -> RetrievalRecord:
        """Observe durable evidence at the action boundary without using a mock."""
        execution_observations.append(
            (len(repositories.retrievals.records()), retrieval_record.lesson_references)
        )
        return retrieval_record

    result = service.execute_learning_action(
        attempt,
        case.memory_scope,
        execute,
        case.lesson_references,
        approved_filters=approved_filters,
    )

    if case.persistence_failure:
        assert not result.is_success
        assert result.error is not None
        assert result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
        assert execution_observations == []
        assert repositories.retrievals.records() == ()
        assert len(repositories.audit.records) == 1
        assert repositories.audit.records[0].action == "learning.retrieval.blocked"
        return

    assert result.is_success
    assert result.value is not None
    records = repositories.retrievals.records()
    assert len(records) == 1
    record = records[0]
    assert record.attempt_id == attempt.attempt_id
    assert record.lesson_references == case.lesson_references
    assert record.approved_filters == approved_filters
    assert execution_observations == [(1, case.lesson_references)]
    assert result.value == record
    assert repositories.audit.records == ()
