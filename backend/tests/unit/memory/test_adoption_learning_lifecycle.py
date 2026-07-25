"""Deterministic lifecycle, retrieval, and terminal-episode edge tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.contracts import AgentLearningContract, ErrorCode
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    AgentNodeAttemptId,
)
from app.models.evidence import LearningTerminalOutcome, RetrievalRecord
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
_ORGANIZATION = OrganizationId("organization-lifecycle")
_CORRELATION = CorrelationId("correlation-lifecycle")
_DOMAIN = DomainId("domain-lifecycle")
_PACK = DomainPackId("pack-lifecycle")
_AGENT = AgentId("agent-lifecycle")
_MEMORY_SCOPE = "agent:agent-lifecycle:memory"


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _alc(version: str = "1.0.0") -> AgentLearningContract:
    return AgentLearningContract(
        agent_id=_AGENT,
        version=version,
        memory_scopes=(_MEMORY_SCOPE,),
        retrieval_policy="enabled",
        reflection_policy="enabled",
        evaluation_references=(f"evaluation:{version}",),
        retention_policy="enabled",
        human_promotion_policy="review-required",
    )


def _activation_evidence() -> ActivationEvidence:
    return ActivationEvidence(
        approved_agent_scoped_memory=True,
        pre_action_retrieval_enabled=True,
        learning_episode_capture_enabled=True,
        reflection_evaluator_enabled=True,
        retention_policy="enabled",
        required_evaluations_passed=True,
        evidence_references=("activation:evidence",),
    )


def _lifecycle(
    *,
    status: AgentLifecycleStatus = AgentLifecycleStatus.CATALOGED,
    effective_alc_version: str | None = None,
    activation_evidence_references: tuple[str, ...] = (),
    change_references: tuple[str, ...] = (),
) -> AgentLifecycle:
    return AgentLifecycle(
        metadata=_metadata("lifecycle-record"),
        lifecycle_id=AgentLifecycleId("lifecycle-1"),
        pack_id=_PACK,
        immutable_version="1.0.0",
        agent_id=_AGENT,
        status=status,
        learning_required=True,
        effective_alc_version=effective_alc_version,
        activation_evidence_references=activation_evidence_references,
        change_references=change_references,
    )


def _attempt(
    attempt_id: str,
    *,
    status: AgentNodeAttemptStatus = AgentNodeAttemptStatus.QUEUED,
) -> AgentNodeAttempt:
    terminal_reference = (
        f"terminal:{attempt_id}" if status is not AgentNodeAttemptStatus.QUEUED else None
    )
    return AgentNodeAttempt(
        metadata=_metadata(f"attempt-record:{attempt_id}"),
        attempt_id=AgentNodeAttemptId(attempt_id),
        run_id=RunId(f"run:{attempt_id}"),
        node_id=f"node:{attempt_id}",
        organization_id=str(_ORGANIZATION),
        domain_id=_DOMAIN,
        pack_id=_PACK,
        pack_version="1.0.0",
        agent_id=_AGENT,
        workflow_id="workflow:lifecycle",
        status=status,
        terminal_outcome_reference=terminal_reference,
    )


def _service(repositories: DeterministicAdoptionRepositories) -> LearningLifecycleService:
    return LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        attempt_repository=repositories.attempts,
        clock=lambda: _NOW,
    )


@pytest.mark.parametrize(
    "alc_candidates",
    [
        (),
        (_alc("1.0.0"), _alc("2.0.0")),
    ],
    ids=("zero", "multiple"),
)
def test_activation_blocks_zero_or_multiple_effective_alcs(
    alc_candidates: tuple[AgentLearningContract, ...],
) -> None:
    """A learning-required agent cannot activate without exactly one named ALC."""
    repositories = DeterministicAdoptionRepositories()
    service = _service(repositories)

    result = service.evaluate_activation(_lifecycle(), alc_candidates, _activation_evidence())

    assert result.is_success and result.value is not None
    assert result.value.status is AgentLifecycleStatus.BLOCKED
    assert result.value.effective_alc_version is None
    assert "activation:failed:effective_alc_cardinality" in (
        result.value.activation_evidence_references
    )
    assert repositories.lifecycle.records() == (result.value,)


def test_activation_with_one_effective_alc_and_all_evidence_becomes_active() -> None:
    """Exactly one valid named ALC and every activation gate produce active status."""
    repositories = DeterministicAdoptionRepositories()
    service = _service(repositories)

    result = service.evaluate_activation(_lifecycle(), (_alc(),), _activation_evidence())

    assert result.is_success and result.value is not None
    assert result.value.status is AgentLifecycleStatus.ACTIVE
    assert result.value.effective_alc_version == "1.0.0"
    assert result.value.activation_evidence_references == (
        "activation:evidence",
        "alc:agent-lifecycle@1.0.0",
        "activation:agent-scoped-memory",
        "activation:pre-action-retrieval",
        "activation:learning-episode-capture",
        "activation:reflection-evaluator",
        "activation:retention-policy",
        "activation:required-evaluations",
    )


def test_active_agent_is_suspended_before_change_and_can_reactivate_afterward() -> None:
    """Suspension is durably ordered before the post-change active decision."""
    repositories = DeterministicAdoptionRepositories()
    service = _service(repositories)
    active = _lifecycle(
        status=AgentLifecycleStatus.ACTIVE,
        effective_alc_version="1.0.0",
        activation_evidence_references=("activation:previous",),
    )

    suspended = service.suspend_for_change(active, ("change:workflow-policy",))
    assert suspended.is_success and suspended.value is not None
    assert suspended.value.status is AgentLifecycleStatus.SUSPENDED
    assert suspended.value.change_references == ("change:workflow-policy",)
    assert repositories.lifecycle.records() == (suspended.value,)

    reactivated = service.evaluate_activation(suspended.value, (_alc(),), _activation_evidence())

    assert reactivated.is_success and reactivated.value is not None
    assert reactivated.value.status is AgentLifecycleStatus.ACTIVE
    assert repositories.lifecycle.records() == (suspended.value, reactivated.value)
    assert repositories.lifecycle.records()[0].status is AgentLifecycleStatus.SUSPENDED
    assert repositories.lifecycle.records()[1].status is AgentLifecycleStatus.ACTIVE


@pytest.mark.parametrize("terminal_outcome", tuple(LearningTerminalOutcome))
def test_each_terminal_outcome_persists_one_immutable_episode(
    terminal_outcome: LearningTerminalOutcome,
) -> None:
    """Completed, failed, blocked, retried, and escalated outcomes are all retained."""
    repositories = DeterministicAdoptionRepositories()
    service = _service(repositories)
    attempt = _attempt(
        f"attempt:{terminal_outcome.value}", status=AgentNodeAttemptStatus(terminal_outcome)
    )

    result = service.record_terminal_episode(
        attempt,
        terminal_outcome,
        f"outcome:{terminal_outcome.value}",
        evidence_references=(f"evidence:{terminal_outcome.value}",),
    )

    assert result.is_success and result.value is not None
    assert result.value.terminal_outcome is terminal_outcome
    assert result.value.outcome_reference == f"outcome:{terminal_outcome.value}"
    assert result.value.evidence_references == (f"evidence:{terminal_outcome.value}",)
    assert repositories.episodes.records() == (result.value,)


def test_retrieval_failure_blocks_before_action_audits_and_recovers_on_retry() -> None:
    """A retrieval write failure blocks execution, audits the block, and permits a retry."""
    failure_plan = FakeFailurePlan()
    failure_plan.fail_next_persistence("retrieval.append")
    repositories = DeterministicAdoptionRepositories(failure_plan)
    service = _service(repositories)
    attempt = _attempt("attempt:retrieval")
    executed: list[RetrievalRecord] = []

    def observe(retrieval: RetrievalRecord) -> RetrievalRecord:
        executed.append(retrieval)
        return retrieval

    blocked = service.execute_learning_action(
        attempt,
        _MEMORY_SCOPE,
        observe,
        lesson_references=(),
    )

    assert not blocked.is_success
    assert blocked.error is not None
    assert blocked.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert executed == []
    assert repositories.retrievals.records() == ()
    assert len(repositories.audit.records) == 1
    assert repositories.audit.records[0].action == "learning.retrieval.blocked"
    assert repositories.audit.records[0].outcome == "retrieval_record_persistence_failed"
    assert repositories.audit.records[0].subject_reference == f"attempt:{attempt.attempt_id}"

    retried = service.execute_learning_action(
        attempt,
        _MEMORY_SCOPE,
        observe,
        lesson_references=(),
    )

    assert retried.is_success and retried.value is not None
    assert retried.value.lesson_references == ()
    assert retried.value.approved_filters == {
        "organization_id": str(_ORGANIZATION),
        "domain_id": str(_DOMAIN),
        "pack_version": "1.0.0",
        "agent_id": str(_AGENT),
        "memory_scope": _MEMORY_SCOPE,
    }
    assert executed == [retried.value]
    assert repositories.retrievals.records() == (retried.value,)
    assert len(repositories.audit.records) == 1


def test_episode_recovery_retry_is_idempotent_after_write_failure() -> None:
    """A failed terminal write blocks recovery, then retries to one immutable episode."""
    failure_plan = FakeFailurePlan()
    failure_plan.fail_next_persistence("episode.append")
    repositories = DeterministicAdoptionRepositories(failure_plan)
    service = _service(repositories)
    attempt = _attempt("attempt:recovery", status=AgentNodeAttemptStatus.FAILED)
    assert repositories.attempts.append(attempt).is_success

    first = service.record_terminal_episode(
        attempt,
        LearningTerminalOutcome.FAILED,
        "outcome:recovery",
        evidence_references=("evidence:recovery",),
    )

    assert not first.is_success
    assert first.error is not None
    assert first.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert repositories.episodes.records() == ()
    blocked_attempt = repositories.attempts.records()[0]
    assert blocked_attempt.status is AgentNodeAttemptStatus.BLOCKED
    assert len(repositories.audit.records) == 1
    assert repositories.audit.records[0].action == "learning.episode.recovery_blocked"

    recovered = service.record_terminal_episode(
        attempt,
        LearningTerminalOutcome.FAILED,
        "outcome:recovery",
        evidence_references=("evidence:recovery",),
    )
    duplicate_retry = service.record_terminal_episode(
        attempt,
        LearningTerminalOutcome.FAILED,
        "outcome:recovery",
        evidence_references=("evidence:recovery",),
    )

    assert recovered.is_success and recovered.value is not None
    assert duplicate_retry.is_success and duplicate_retry.value == recovered.value
    assert repositories.episodes.records() == (recovered.value,)
    assert len(repositories.audit.records) == 1
