"""Property tests for terminally safe, durable run failure processing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.models.common import OptimisticTransition, RecordMetadata
from app.models.contracts import ErrorCode, RepositoryError, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.failure_processing import FailureProcessor

# Feature: generic-swarm-business-os, Property 9: Failure processing is terminally safe and
# evidence-complete.
# **Validates: Requirements 4.3, 4.4**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-9")
_CORRELATION_ID = CorrelationId("corr-property-9")
_FAILURE_CODES = {
    "failure": "step_failed",
    "timeout": "timeout",
    "interruption": "interrupted",
    "ambiguous-state": "ambiguous_execution_state",
}


@dataclass(frozen=True, slots=True)
class FailureSequence:
    """A bounded partially executed run and its terminal failure signal."""

    failure_signal: str
    starting_status: RunStatus
    existing_effect_ids: tuple[int, ...]
    completed_effect_ids: tuple[int, ...]
    evidence_ids: tuple[int, ...]
    unstarted_step_ids: tuple[int, ...]
    final_transition_available: bool


class RecordingFailureRepository(InMemoryRunRepository):
    """A local repository that exposes durable failure-processing transitions."""

    def __init__(self, final_transition_available: bool) -> None:
        super().__init__()
        self._final_transition_available = final_transition_available
        self.transition_attempts: list[RunRecord] = []
        self.persisted_transitions: list[RunRecord] = []

    def transition(
        self, record: RunRecord, transition: OptimisticTransition
    ) -> Result[RunRecord, RepositoryError]:
        self.transition_attempts.append(record)
        if (
            not self._final_transition_available
            and record.failure is not None
            and record.failure.failure_processing_complete
        ):
            return Result.failure(
                RepositoryError(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Final failure-processing persistence is unavailable.",
                    _CORRELATION_ID,
                )
            )
        persisted = super().transition(record, transition)
        if persisted.is_success and persisted.value is not None:
            self.persisted_transitions.append(persisted.value)
        return persisted


@st.composite
def _failure_sequences(draw: st.DrawFn) -> FailureSequence:
    """Generate bounded local sequences with partial effects and terminal signals."""
    return FailureSequence(
        failure_signal=draw(st.sampled_from(tuple(_FAILURE_CODES))),
        starting_status=draw(
            st.sampled_from((RunStatus.DISPATCHING, RunStatus.WAITING_FOR_APPROVAL))
        ),
        existing_effect_ids=tuple(
            draw(st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=4))
        ),
        completed_effect_ids=tuple(
            draw(st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=4))
        ),
        evidence_ids=tuple(
            draw(st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=4))
        ),
        unstarted_step_ids=tuple(
            draw(st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=4))
        ),
        final_transition_available=draw(st.booleans()),
    )


def _effect(effect_id: int) -> ToolEffect:
    """Build one deterministic completed local adapter effect."""
    return ToolEffect(
        adapter_id=f"local.adapter-{effect_id}",
        request_digest=f"request-{effect_id}",
        outcome="completed",
        effect_digest=f"effect-{effect_id}",
        completed_at=_NOW,
        reversible=True,
    )


def _evidence(evidence_id: int) -> EvidenceReference:
    """Build one deterministic failure-evidence reference."""
    return EvidenceReference(
        evidence_id=EvidenceId(f"evidence-{evidence_id}"),
        digest=f"digest-{evidence_id}",
        kind="execution-event",
    )


def _active_run(sequence: FailureSequence) -> RunRecord:
    """Build a locally persisted partially executed run in an active state."""
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-property-9"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=_CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        run_id=RunId("run-property-9"),
        workflow_definition_id=WorkflowDefinitionId("workflow-property-9"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="workflow-digest-property-9",
        engine=WorkflowEngineKind.LEGACY,
        status=sequence.starting_status,
        created_for_dispatch_at=_NOW,
        tool_effects=tuple(_effect(effect_id) for effect_id in sequence.existing_effect_ids),
    )


def _ordered_unique[T](values: tuple[T, ...]) -> tuple[T, ...]:
    """Match the failure processor's durable, first-seen de-duplication order."""
    return tuple(dict.fromkeys(values))


def _assert_incomplete_failure(
    record: RunRecord,
    *,
    code: str,
    expected_evidence: tuple[EvidenceReference, ...],
    expected_effects: tuple[ToolEffect, ...],
    expected_stopped_steps: tuple[str, ...],
) -> None:
    """Assert the first durable failure transition meets every incomplete obligation."""
    assert record.status is RunStatus.FAILED
    assert record.failure is not None
    assert record.failure.code == code
    assert not record.failure.failure_processing_complete
    assert record.failure.evidence_references == expected_evidence
    assert record.failure.stopped_step_ids == expected_stopped_steps
    assert record.tool_effects == expected_effects
    projection = record.to_projection()
    assert projection.status is RunStatus.FAILED
    assert projection.failure_code == code


@settings(max_examples=100, deadline=None, derandomize=True)
@example(
    sequence=FailureSequence(
        "failure", RunStatus.DISPATCHING, (1,), (2,), (3,), (4, 5), True
    )
)
@example(
    sequence=FailureSequence(
        "timeout", RunStatus.DISPATCHING, (1,), (1, 2), (3,), (4,), False
    )
)
@example(
    sequence=FailureSequence(
        "interruption", RunStatus.WAITING_FOR_APPROVAL, (1,), (2,), (3, 4), (5,), True
    )
)
@example(
    sequence=FailureSequence(
        "ambiguous-state", RunStatus.WAITING_FOR_APPROVAL, (1, 2), (2, 3), (4,), (5, 6), False
    )
)
@given(sequence=_failure_sequences())
def test_failure_state_sequences_are_terminally_safe_and_evidence_complete(
    sequence: FailureSequence,
) -> None:
    """Partial-effect terminal sequences retain obligations before they may complete."""
    repository = RecordingFailureRepository(sequence.final_transition_available)
    run = _active_run(sequence)
    created = repository.create(run)
    assert created.is_success and created.value == run
    existing_effects = run.tool_effects
    completed_effects = tuple(_effect(effect_id) for effect_id in sequence.completed_effect_ids)
    evidence = tuple(_evidence(evidence_id) for evidence_id in sequence.evidence_ids)
    unstarted_steps = tuple(f"step-{step_id}" for step_id in sequence.unstarted_step_ids)
    expected_effects = _ordered_unique((*existing_effects, *completed_effects))
    expected_evidence = _ordered_unique(evidence)
    expected_stopped_steps = _ordered_unique(unstarted_steps)
    code = _FAILURE_CODES[sequence.failure_signal]

    outcome = FailureProcessor(repository, clock=lambda: _NOW).process(
        run,
        code=code,
        evidence_references=evidence,
        completed_effects=completed_effects,
        unstarted_step_ids=unstarted_steps,
        correlation_id=_CORRELATION_ID,
    )

    assert len(repository.persisted_transitions) == 1 + int(sequence.final_transition_available)
    incomplete = repository.persisted_transitions[0]
    _assert_incomplete_failure(
        incomplete,
        code=code,
        expected_evidence=expected_evidence,
        expected_effects=expected_effects,
        expected_stopped_steps=expected_stopped_steps,
    )

    stored = repository.get_by_run_id(_ORGANIZATION_ID, run.run_id)
    assert stored.is_success and stored.value is not None
    if not sequence.final_transition_available:
        assert not outcome.is_success
        assert outcome.error is not None
        assert outcome.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
        assert len(repository.transition_attempts) == 2
        _assert_incomplete_failure(
            stored.value,
            code=code,
            expected_evidence=expected_evidence,
            expected_effects=expected_effects,
            expected_stopped_steps=expected_stopped_steps,
        )
        return

    assert outcome.is_success and outcome.value is not None
    assert len(repository.transition_attempts) == 2
    assert outcome.value.record == stored.value
    assert stored.value.status is RunStatus.FAILED
    assert stored.value.failure is not None
    assert stored.value.failure.failure_processing_complete
    assert stored.value.failure.code == code
    assert stored.value.failure.evidence_references == expected_evidence
    assert stored.value.failure.stopped_step_ids == expected_stopped_steps
    assert stored.value.tool_effects == expected_effects
