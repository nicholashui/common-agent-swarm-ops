"""Property checks for atomic, evidence-complete learning activation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.contracts import AgentLearningContract
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
)
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_LIFECYCLE_STATUSES = tuple(AgentLifecycleStatus)


@dataclass(frozen=True, slots=True)
class _ActivationCase:
    """Bounded ALC, lifecycle, change, and activation-evidence inputs."""

    case_id: int
    agent_id: AgentId
    lifecycle_status: AgentLifecycleStatus
    learning_required: bool
    effective_alc_version: str | None
    alc_candidates: tuple[AgentLearningContract, ...]
    evidence: ActivationEvidence
    change_references: tuple[str, ...]


def _version(patch: int) -> str:
    """Return a bounded semantic version for generated declarations."""
    return f"1.0.{patch}"


def _alc(
    agent_id: AgentId,
    version: str,
    case_id: int,
    candidate_index: int,
    retrieval_policy: str,
    reflection_policy: str,
    retention_policy: str,
) -> AgentLearningContract:
    """Build one valid, reference-only ALC for a generated candidate set."""
    return AgentLearningContract(
        agent_id=agent_id,
        version=version,
        memory_scopes=(f"agent:{agent_id}:memory",),
        retrieval_policy=retrieval_policy,
        reflection_policy=reflection_policy,
        evaluation_references=(f"evaluation-{case_id}-{candidate_index}",),
        retention_policy=retention_policy,
        human_promotion_policy="review-required",
    )


@st.composite
def _activation_cases(draw: st.DrawFn) -> _ActivationCase:
    """Generate bounded candidate ALC sets and every activation evidence vector."""
    case_id = draw(st.integers(min_value=0, max_value=10_000))
    agent_id = AgentId(f"learning-agent-{case_id}")
    should_activate = draw(st.booleans())
    target_count = 1 if should_activate else draw(st.integers(min_value=0, max_value=2))
    foreign_count = draw(st.integers(min_value=0, max_value=2))
    policy = st.sampled_from(("enabled", "disabled"))

    candidates: list[AgentLearningContract] = []
    target_versions: list[str] = []
    for candidate_index in range(target_count):
        version = _version(draw(st.integers(min_value=0, max_value=3)))
        target_versions.append(version)
        candidate_policy = st.just("enabled") if should_activate else policy
        candidates.append(
            _alc(
                agent_id,
                version,
                case_id,
                candidate_index,
                draw(candidate_policy),
                draw(candidate_policy),
                draw(candidate_policy),
            )
        )
    for candidate_index in range(foreign_count):
        foreign_agent_id = AgentId(f"other-agent-{case_id}-{candidate_index}")
        candidates.append(
            _alc(
                foreign_agent_id,
                _version(draw(st.integers(min_value=0, max_value=3))),
                case_id,
                target_count + candidate_index,
                draw(policy),
                draw(policy),
                draw(policy),
            )
        )

    lifecycle_status = draw(st.sampled_from(_LIFECYCLE_STATUSES))
    learning_required = True if should_activate else draw(st.booleans())
    effective_alc_version: str | None
    if should_activate:
        effective_alc_version = (
            target_versions[0]
            if lifecycle_status is AgentLifecycleStatus.ACTIVE
            else draw(st.one_of(st.none(), st.just(target_versions[0])))
        )
    elif lifecycle_status is AgentLifecycleStatus.ACTIVE and learning_required:
        effective_alc_version = draw(
            st.sampled_from((_version(0), _version(1), _version(2), _version(3)))
        )
    else:
        effective_alc_version = draw(
            st.one_of(
                st.none(),
                st.sampled_from((_version(0), _version(1), _version(2), _version(3))),
            )
        )

    if should_activate:
        evidence = ActivationEvidence(
            approved_agent_scoped_memory=True,
            pre_action_retrieval_enabled=True,
            learning_episode_capture_enabled=True,
            reflection_evaluator_enabled=True,
            retention_policy="enabled",
            required_evaluations_passed=True,
            evidence_references=(f"evidence-{case_id}",),
        )
    else:
        evidence = ActivationEvidence(
            approved_agent_scoped_memory=draw(st.booleans()),
            pre_action_retrieval_enabled=draw(st.booleans()),
            learning_episode_capture_enabled=draw(st.booleans()),
            reflection_evaluator_enabled=draw(st.booleans()),
            retention_policy=draw(st.one_of(st.none(), st.sampled_from(("enabled", "disabled")))),
            required_evaluations_passed=False,
            evidence_references=(f"evidence-{case_id}",),
        )
    change_count = draw(st.integers(min_value=1, max_value=2))
    change_references = tuple(
        f"change-{case_id}-{change_index}" for change_index in range(change_count)
    )
    return _ActivationCase(
        case_id=case_id,
        agent_id=agent_id,
        lifecycle_status=lifecycle_status,
        learning_required=learning_required,
        effective_alc_version=effective_alc_version,
        alc_candidates=tuple(candidates),
        evidence=evidence,
        change_references=change_references,
    )


def _lifecycle(case: _ActivationCase) -> AgentLifecycle:
    """Build the immutable lifecycle snapshot supplied to the service."""
    return AgentLifecycle(
        metadata=RecordMetadata(
            record_id=RecordId(f"lifecycle-record-{case.case_id}"),
            organization_id=OrganizationId(f"organization-{case.case_id}"),
            correlation_id=CorrelationId(f"correlation-{case.case_id}"),
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        lifecycle_id=AgentLifecycleId(f"lifecycle-{case.case_id}"),
        pack_id=DomainPackId(f"pack-{case.case_id}"),
        immutable_version=_version(0),
        agent_id=case.agent_id,
        status=case.lifecycle_status,
        learning_required=case.learning_required,
        effective_alc_version=case.effective_alc_version,
        activation_evidence_references=(
            (f"existing-activation-{case.case_id}",)
            if case.lifecycle_status is AgentLifecycleStatus.ACTIVE and case.learning_required
            else ()
        ),
    )


def _policy_is_enabled(value: str | bool | None) -> bool:
    """Match the service's enabled-policy interpretation for expected outcomes."""
    return isinstance(value, str) and value.strip().casefold() not in {
        "",
        "disabled",
        "disable",
        "off",
        "false",
        "none",
        "not_enabled",
    }


def _expected_active(case: _ActivationCase, lifecycle: AgentLifecycle) -> bool:
    """Calculate the complete activation predicate independently of the service."""
    named = tuple(
        candidate for candidate in case.alc_candidates if candidate.agent_id == lifecycle.agent_id
    )
    if len(named) != 1:
        return False
    effective_alc = named[0]
    return (
        lifecycle.learning_required
        and (
            lifecycle.effective_alc_version is None
            or effective_alc.version == lifecycle.effective_alc_version
        )
        and case.evidence.approved_agent_scoped_memory
        and case.evidence.pre_action_retrieval_enabled
        and _policy_is_enabled(effective_alc.retrieval_policy)
        and case.evidence.learning_episode_capture_enabled
        and case.evidence.reflection_evaluator_enabled
        and _policy_is_enabled(effective_alc.reflection_policy)
        and _policy_is_enabled(case.evidence.retention_policy)
        and _policy_is_enabled(effective_alc.retention_policy)
        and case.evidence.required_evaluations_passed
        and bool(effective_alc.evaluation_references)
    )


def _service(
    repositories: DeterministicAdoptionRepositories,
) -> LearningLifecycleService:
    """Compose the lifecycle service entirely from deterministic repository fakes."""
    return LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        clock=lambda: _NOW,
    )


# Feature: adoption-redesign, Property 8: Learning-agent activation is atomic and evidence-complete
# **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 7.3**
@settings(max_examples=100, deadline=None)
@given(activation_case=_activation_cases())
def test_property_8_learning_activation_is_atomic_and_evidence_complete(
    activation_case: _ActivationCase,
) -> None:
    """Activation and post-change reactivation require every independent gate."""
    repositories = DeterministicAdoptionRepositories()
    service = _service(repositories)
    lifecycle = _lifecycle(activation_case)

    initial = service.evaluate_activation(
        lifecycle,
        activation_case.alc_candidates,
        activation_case.evidence,
    )
    assert initial.is_success and initial.value is not None
    initial_expected_active = _expected_active(activation_case, lifecycle)
    assert (initial.value.status is AgentLifecycleStatus.ACTIVE) is initial_expected_active
    if not initial_expected_active:
        assert initial.value.status is not AgentLifecycleStatus.ACTIVE
    else:
        named = tuple(
            candidate
            for candidate in activation_case.alc_candidates
            if candidate.agent_id == lifecycle.agent_id
        )
        assert len(named) == 1
        assert initial.value.effective_alc_version == named[0].version

    active_before_change = None
    if lifecycle.status is AgentLifecycleStatus.ACTIVE and lifecycle.learning_required:
        active_before_change = lifecycle
    elif initial.value.status is AgentLifecycleStatus.ACTIVE and initial.value.learning_required:
        active_before_change = initial.value

    if active_before_change is not None:
        suspended = service.suspend_for_change(
            active_before_change,
            activation_case.change_references,
        )
        assert suspended.is_success and suspended.value is not None
        assert suspended.value.status is AgentLifecycleStatus.SUSPENDED
        assert suspended.value.change_references == activation_case.change_references
        assert repositories.lifecycle.records()[-1] == suspended.value

        post_change = service.evaluate_activation(
            suspended.value,
            activation_case.alc_candidates,
            activation_case.evidence,
        )
        assert post_change.is_success and post_change.value is not None
        post_expected_active = _expected_active(activation_case, suspended.value)
        assert (post_change.value.status is AgentLifecycleStatus.ACTIVE) is post_expected_active
        if not post_expected_active:
            assert post_change.value.status is not AgentLifecycleStatus.ACTIVE
        assert repositories.lifecycle.records()[-2:] == (
            suspended.value,
            post_change.value,
        )
