"""Property checks for exact migration rollback and ALC retention behavior."""

from __future__ import annotations

# The required property label is intentionally kept in its exact documented form below.
# ruff: noqa: E501
from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.engines.recovery import (
    InMemoryImmutableVersionStore,
    InMemoryLessonRetentionService,
    InMemoryRollbackEvidenceRepository,
    LessonRetentionOutcome,
    MigrationRollbackRequest,
    MigrationRollbackStatus,
    RecoveryService,
)
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata
from app.models.control_plane import LessonId
from app.models.evidence import Lesson, LessonAssessmentOutcome
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_TARGET_VERSIONS = ("1.0.0", "2.0.0", "3.4.5")
_CURRENT_VERSION_BY_TARGET = {
    "1.0.0": "9.0.0",
    "2.0.0": "9.1.0",
    "3.4.5": "9.2.0",
}
_RETENTION_OUTCOMES = {
    "retain": LessonRetentionOutcome.RETAINED,
    "stale": LessonRetentionOutcome.STALE,
    "revoke": LessonRetentionOutcome.REVOKED,
    "delete": LessonRetentionOutcome.DELETED,
    "custom-alc-policy": LessonRetentionOutcome.APPLIED,
}


@dataclass(frozen=True, slots=True)
class MigrationRollbackCase:
    """Bounded rollback targets, prior versions, and affected Lesson inputs."""

    case_id: int
    designated_version: str
    current_version: str
    affected_lesson_count: int
    alc_retention_policy: str


@st.composite
def _migration_rollback_cases(draw: st.DrawFn) -> MigrationRollbackCase:
    """Generate approved target and retention branches with bounded Lesson counts."""
    designated_version = draw(st.sampled_from(_TARGET_VERSIONS))
    return MigrationRollbackCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        designated_version=designated_version,
        current_version=_CURRENT_VERSION_BY_TARGET[designated_version],
        affected_lesson_count=draw(st.integers(min_value=1, max_value=4)),
        alc_retention_policy=draw(st.sampled_from(tuple(_RETENTION_OUTCOMES))),
    )


def _organization(case: MigrationRollbackCase) -> OrganizationId:
    """Return the isolated organization for one generated rollback."""
    return OrganizationId(f"organization-property-18-{case.case_id}")


def _pack(case: MigrationRollbackCase) -> DomainPackId:
    """Return the VA pack identity under the generated migration rollback."""
    return DomainPackId(f"va-domain-pack-property-18-{case.case_id}")


def _correlation(case: MigrationRollbackCase) -> CorrelationId:
    """Return the deterministic request correlation for the generated case."""
    return CorrelationId(f"correlation-property-18-{case.case_id}")


def _lesson_metadata(case: MigrationRollbackCase, index: int) -> RecordMetadata:
    """Build metadata for one generated affected Lesson."""
    return RecordMetadata(
        record_id=RecordId(f"lesson-record-property-18-{case.case_id}-{index}"),
        organization_id=_organization(case),
        correlation_id=_correlation(case),
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _affected_lessons(case: MigrationRollbackCase) -> tuple[Lesson, ...]:
    """Build valid, reference-only Lessons affected by the restored VA version."""
    return tuple(
        Lesson(
            metadata=_lesson_metadata(case, index),
            lesson_id=LessonId(f"lesson-property-18-{case.case_id}-{index}"),
            organization_id=_organization(case),
            domain_id=DomainId(f"video-domain-property-18-{case.case_id}"),
            pack_version_range=CompatibilityRange.exact(case.designated_version),
            agent_id=AgentId(f"video-agent-property-18-{case.case_id}-{index}"),
            memory_scope=f"agent:video-agent-property-18-{case.case_id}-{index}",
            assessment=LessonAssessmentOutcome.PASSED,
            source_episode_references=(f"episode-property-18-{case.case_id}-{index}",),
            content_reference=f"lesson-content-property-18-{case.case_id}-{index}",
            assessed_at=_NOW,
            retrievable=True,
        )
        for index in range(case.affected_lesson_count)
    )


def _service(
    case: MigrationRollbackCase,
) -> tuple[
    RecoveryService,
    InMemoryImmutableVersionStore,
    InMemoryLessonRetentionService,
    InMemoryRollbackEvidenceRepository,
]:
    """Compose RecoveryService from deterministic in-memory test fakes only."""
    organization_id = _organization(case)
    pack_id = _pack(case)
    correlation_id = _correlation(case)
    versions = InMemoryImmutableVersionStore()
    versions.approve_version(organization_id, pack_id, case.current_version)
    versions.approve_version(organization_id, pack_id, case.designated_version)
    initialized = versions.restore(
        organization_id,
        pack_id,
        case.current_version,
        correlation_id,
    )
    assert initialized.is_success

    retention = InMemoryLessonRetentionService()
    evidence = InMemoryRollbackEvidenceRepository()
    service = RecoveryService(
        DeterministicAdoptionRepositories().recoveries,
        versions,
        retention,
        evidence,
        clock=lambda: _NOW,
    )
    return service, versions, retention, evidence


# Feature: adoption-redesign, Property 18: Approved rollback restores the designated version and retention outcome
# **Validates: Requirements 6.8, 6.9**
@settings(max_examples=100, deadline=None)
@example(
    case=MigrationRollbackCase(
        case_id=0,
        designated_version="1.0.0",
        current_version="9.0.0",
        affected_lesson_count=1,
        alc_retention_policy="retain",
    )
)
@example(
    case=MigrationRollbackCase(
        case_id=1,
        designated_version="3.4.5",
        current_version="9.2.0",
        affected_lesson_count=4,
        alc_retention_policy="delete",
    )
)
@given(case=_migration_rollback_cases())
def test_property_18_approved_rollback_restores_designated_version_and_retention(
    case: MigrationRollbackCase,
) -> None:
    """An approved rollback restores exactly its target and applies ALC retention to all Lessons."""
    service, versions, retention, evidence = _service(case)
    organization_id = _organization(case)
    pack_id = _pack(case)
    correlation_id = _correlation(case)
    lessons = _affected_lessons(case)
    lesson_references = tuple(str(lesson.lesson_id) for lesson in lessons)
    request = MigrationRollbackRequest(
        organization_id=organization_id,
        pack_id=pack_id,
        designated_immutable_version=case.designated_version,
        approval_reference=f"approval-property-18-{case.case_id}",
        affected_lessons=lessons,
        alc_retention_policy=case.alc_retention_policy,
        evidence_references=(f"investigation-property-18-{case.case_id}",),
        rollback_id=f"rollback-property-18-{case.case_id}",
        approved=True,
    )

    result = service.rollback(correlation_id, request)

    assert result.is_success and result.value is not None
    rollback = result.value
    assert rollback.status is MigrationRollbackStatus.RESTORED
    assert rollback.designated_immutable_version == case.designated_version
    assert rollback.restored_immutable_version == case.designated_version
    assert versions.current_versions[(organization_id, pack_id)] == case.designated_version
    assert versions.restore_calls[-1] == (
        organization_id,
        pack_id,
        case.designated_version,
    )

    assert retention.calls == [
        (
            pack_id,
            case.designated_version,
            lesson_references,
            case.alc_retention_policy,
        )
    ]
    assert rollback.affected_lesson_references == lesson_references
    assert tuple(record.lesson_reference for record in rollback.retention_records) == (
        lesson_references
    )
    assert tuple(record.policy_reference for record in rollback.retention_records) == tuple(
        case.alc_retention_policy for _ in lessons
    )
    assert tuple(record.outcome for record in rollback.retention_records) == tuple(
        _RETENTION_OUTCOMES[case.alc_retention_policy] for _ in lessons
    )
    assert evidence.records == (rollback,)
