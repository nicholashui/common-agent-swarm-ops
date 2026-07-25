"""Property checks for immutable, recoverable terminal learning episodes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.learning_lifecycle import LearningLifecycleService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import AgentNodeAttemptId
from app.models.evidence import LearningTerminalOutcome
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
class _TerminalEpisodeCase:
    """Bounded terminal notification and episode-write failure inputs."""

    case_id: int
    terminal_outcome: LearningTerminalOutcome
    notification_count: int
    persistence_failure: bool


@st.composite
def _terminal_episode_cases(draw: st.DrawFn) -> _TerminalEpisodeCase:
    """Generate repeated terminal notifications and configurable episode failures."""
    return _TerminalEpisodeCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        terminal_outcome=draw(st.sampled_from(tuple(LearningTerminalOutcome))),
        notification_count=draw(st.integers(min_value=2, max_value=5)),
        persistence_failure=draw(st.booleans()),
    )


def _attempt(case: _TerminalEpisodeCase) -> AgentNodeAttempt:
    """Build a persisted terminal attempt for one generated case."""
    organization_id = OrganizationId(f"organization-property-10-{case.case_id}")
    correlation_id = CorrelationId(f"correlation-property-10-{case.case_id}")
    outcome_reference = f"terminal-outcome-property-10-{case.case_id}"
    return AgentNodeAttempt(
        metadata=RecordMetadata(
            record_id=RecordId(f"attempt-record-property-10-{case.case_id}"),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        attempt_id=AgentNodeAttemptId(f"attempt-property-10-{case.case_id}"),
        run_id=RunId(f"run-property-10-{case.case_id}"),
        node_id=f"node-property-10-{case.case_id}",
        organization_id=str(organization_id),
        domain_id=DomainId(f"domain-property-10-{case.case_id}"),
        pack_id=DomainPackId(f"pack-property-10-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=AgentId(f"agent-property-10-{case.case_id}"),
        workflow_id=f"workflow-property-10-{case.case_id}",
        status=AgentNodeAttemptStatus(case.terminal_outcome.value),
        terminal_outcome_reference=outcome_reference,
    )


def _service(repositories: DeterministicAdoptionRepositories) -> LearningLifecycleService:
    """Compose the lifecycle service entirely from deterministic repository fakes."""
    return LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        attempt_repository=repositories.attempts,
        clock=lambda: _NOW,
    )


# Feature: adoption-redesign, Property 10: Terminal learning outcomes are immutable and recoverable
# **Validates: Requirements 4.10, 4.11**
@settings(max_examples=100, deadline=None)
@given(case=_terminal_episode_cases())
def test_property_10_terminal_learning_outcomes_are_immutable_and_recoverable(
    case: _TerminalEpisodeCase,
) -> None:
    """Duplicate terminal notifications create one episode or a recovery block."""
    failure_plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(failure_plan)
    attempt = _attempt(case)
    assert repositories.attempts.append(attempt).is_success
    service = _service(repositories)
    outcome_reference = str(attempt.terminal_outcome_reference)
    evidence_references = (f"terminal-evidence-property-10-{case.case_id}",)
    notifications = []

    for _ in range(case.notification_count):
        if case.persistence_failure:
            # The shared fake consumes operation failures one write at a time; restoring
            # the named failure keeps every generated duplicate notification unavailable
            # while allowing recovery-block persistence to succeed.
            failure_plan.persistence_operations.add("episode.append")
        notifications.append(
            service.record_terminal_episode(
                attempt,
                case.terminal_outcome,
                outcome_reference,
                evidence_references=evidence_references,
            )
        )

    if case.persistence_failure:
        assert all(not result.is_success for result in notifications)
        assert all(
            result.error is not None and result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
            for result in notifications
        )
        assert repositories.episodes.records() == ()
        blocked_attempts = repositories.attempts.records()
        assert len(blocked_attempts) == 1
        assert blocked_attempts[0].attempt_id == attempt.attempt_id
        assert blocked_attempts[0].status is AgentNodeAttemptStatus.BLOCKED
        return

    assert all(result.is_success and result.value is not None for result in notifications)
    episodes = repositories.episodes.records()
    assert len(episodes) == 1
    episode = episodes[0]
    assert episode.terminal_identity == (
        OrganizationId(attempt.organization_id),
        attempt.attempt_id,
    )
    assert episode.terminal_outcome is case.terminal_outcome
    assert episode.outcome_reference == outcome_reference
    assert episode.evidence_references == evidence_references
    assert all(result.value == episode for result in notifications)
    assert {result.value.episode_id for result in notifications if result.value is not None} == {
        episode.episode_id
    }
