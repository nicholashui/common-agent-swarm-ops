"""Focused VA adapter tests for requirements 14.1-14.6."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.command_service import CommandService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    CritiqueRecord,
    GraphRevisionId,
    QualityEvidence,
    QualityEvidenceKind,
    RunProvenance,
    RunProvenanceId,
    TaskId,
    TaskLifecycle,
    WorkItem,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import InMemoryControlPlaneDatabase
from app.va.service import VaDomainAdapter, VaMetadata, VaProductionAction

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORG = OrganizationId("va-org")
_CORRELATION = CorrelationId("va-correlation")
_ACTOR = ActorId("va-operator")


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORG,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _pattern(status: ContractStatus = ContractStatus.PUBLISHED) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata("pattern-record"),
        pattern_version_id=CommonPatternVersionId("va-pattern-v1"),
        status=status,
        graph_template={"va_templates": ("campaign", "explainer")},
        slot_constraints={"required": ("producer",)},
        compatibility_rules={"va_production_phases": ("brief", "production", "review")},
        risk_requirements={"approval": "required"},
        verification_requirements={"quality": True},
        provenance={"source": "published-registry"},
        content_digest="sha256:va-pattern-v1",
    )


def _adapter(
    database: InMemoryControlPlaneDatabase,
    dispatched: list[tuple[str, str]] | None = None,
) -> VaDomainAdapter:
    def record_dispatch(command: str, work: WorkItem) -> None:
        assert dispatched is not None
        dispatched.append((command, str(work.work_item_id)))

    dispatcher = record_dispatch if dispatched is not None else None
    return VaDomainAdapter(
        database.unit_of_work,
        CommandService(database.unit_of_work, clock=lambda: _NOW),
        clock=lambda: _NOW,
        dispatcher=dispatcher,
    )


def _valid_metadata() -> VaMetadata:
    return VaMetadata(CommonPatternVersionId("va-pattern-v1"), "campaign", "production")


def test_metadata_validation_requires_matching_published_pattern_labels() -> None:
    database = InMemoryControlPlaneDatabase()
    adapter = _adapter(database)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success

    valid = adapter.validate_metadata(_ORG, _CORRELATION, _valid_metadata())
    invalid = adapter.validate_metadata(
        _ORG,
        _CORRELATION,
        VaMetadata(CommonPatternVersionId("va-pattern-v1"), "unknown", "release"),
    )
    missing = adapter.validate_metadata(
        _ORG,
        _CORRELATION,
        VaMetadata(CommonPatternVersionId("missing-pattern"), "campaign", "production"),
    )

    assert valid.is_success and valid.value is not None and valid.value.valid
    assert valid.value.pattern_content_digest == "sha256:va-pattern-v1"
    assert invalid.is_success and invalid.value is not None and not invalid.value.valid
    assert {field.name for field in invalid.value.fields} == {"template", "production_phase"}
    assert missing.is_success and missing.value is not None and not missing.value.valid
    assert tuple(field.name for field in missing.value.fields) == ("pattern_version_id",)


def test_invalid_metadata_blocks_action_before_canonical_work_or_dispatch() -> None:
    database = InMemoryControlPlaneDatabase()
    dispatched: list[tuple[str, str]] = []
    adapter = _adapter(database, dispatched)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success

    result = adapter.invoke_action(
        _ORG,
        _ACTOR,
        _CORRELATION,
        VaMetadata(CommonPatternVersionId("va-pattern-v1"), "unknown", "production"),
        VaProductionAction.DISPATCH_RUN,
        "run-1",
        "invalid-action-key",
    )

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert tuple(field.name for field in result.error.fields) == ("template",)
    assert dispatched == []
    assert database._state.work_items == {}
    assert database._state.idempotency_records == {}


def test_valid_action_maps_once_to_canonical_command_and_preserves_common_evidence() -> None:
    database = InMemoryControlPlaneDatabase()
    dispatched: list[tuple[str, str]] = []
    adapter = _adapter(database, dispatched)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success
    pattern_snapshot = database._state.pattern_versions.copy()
    provenance_snapshot = database._state.provenance.copy()

    first = adapter.invoke_action(
        _ORG,
        _ACTOR,
        _CORRELATION,
        _valid_metadata(),
        VaProductionAction.DISPATCH_RUN,
        "run-1",
        "valid-action-key",
    )
    replay = adapter.invoke_action(
        _ORG,
        _ACTOR,
        _CORRELATION,
        _valid_metadata(),
        VaProductionAction.DISPATCH_RUN,
        "run-1",
        "valid-action-key",
    )

    assert first.is_success and first.value is not None
    assert first.value.canonical_command == "run.dispatch"
    assert first.value.canonical_subject_reference == "run:run-1"
    assert first.value.work_state == "pending"
    assert not first.value.replayed
    assert replay.is_success and replay.value is not None and replay.value.replayed
    assert replay.value.work_item_id == first.value.work_item_id
    assert dispatched == [("run.dispatch", first.value.work_item_id)]
    assert len(database._state.work_items) == 1
    assert len(database._state.audits) == 1
    assert len(database._state.events) == 1
    assert len(database._state.outbox) == 1
    assert database._state.pattern_versions == pattern_snapshot
    assert database._state.provenance == provenance_snapshot


def _agent() -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata("agent-record"),
        agent_version_id=AgentVersionId("agent-v1"),
        status=ContractStatus.PUBLISHED,
        canonical_identity="va.producer",
        category="production",
        responsibilities=("produce",),
        boundaries=("no-unapproved-release",),
        escalation_targets=("human-producer",),
        approval_authority=("release-gate",),
        runtime_policy={"max_retries": 2, "api_token": "secret-value"},
        tool_policy={"allow": ("render",)},
        quality_rubric={"minimum": 0.9},
        critique_relationships=("reviewer",),
        knowledge_bindings=("brand-guide",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest="sha256:agent-v1",
    )


def _seed_canonical_run_evidence(database: InMemoryControlPlaneDatabase) -> None:
    task_id = TaskId("task-1")
    gate_id = ApprovalGateId("gate-1")
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success
        assert unit_of_work.common_contracts.append_agent_version(_agent()).is_success
        assert unit_of_work.provenance.append(
            RunProvenance(
                metadata=_metadata("provenance-record"),
                run_provenance_id=RunProvenanceId("provenance-1"),
                graph_revision_id=GraphRevisionId("graph-revision-1"),
                workflow_definition={"version": "1.0.0"},
                workflow_definition_version="1.0.0",
                agent_version_ids=(AgentVersionId("agent-v1"),),
                pattern_version_ids=(CommonPatternVersionId("va-pattern-v1"),),
                artifact_version_references=("artifact-v1",),
            )
        ).is_success
        assert unit_of_work.tasks.create(
            AgentTask(
                metadata=_metadata("task-record"),
                task_id=task_id,
                run_reference="run-1",
                pinned_agent_version_id=AgentVersionId("agent-v1"),
                dependencies=(),
                constraints={"risk": "controlled"},
                approval_gate_ids=(gate_id,),
                checkpoint_reference="checkpoint-1",
                state=TaskLifecycle.QUEUED,
            )
        ).is_success
        assert unit_of_work.artifacts.append(
            ArtifactHandoff(
                metadata=_metadata("artifact-record"),
                handoff_id=ArtifactHandoffId("handoff-1"),
                artifact_identity="storyboard",
                artifact_version="artifact-v1",
                parent_lineage=("brief-v1",),
                source_task_id=task_id,
                source_run_reference="run-1",
                brief_scope="campaign",
                technical_specification={"format": "reference-only"},
                rights_and_consent_state="passed",
                continuity_state="passed",
                quality_control_state="passed",
                target_channels=("review",),
                provenance_reference="artifact-provenance-1",
            )
        ).is_success
        assert unit_of_work.evidence.append_critique(
            CritiqueRecord(
                metadata=_metadata("critique-record"),
                critique_id="critique-1",
                source_reference="reviewer-1",
                target_task_id=task_id,
                relationship_reference="reviewer",
                evidence_reference="critique-evidence-1",
                submitted_at=_NOW,
            )
        ).is_success
        assert unit_of_work.evidence.append_quality(
            QualityEvidence(
                metadata=_metadata("quality-record"),
                evidence_id="quality-1",
                kind=QualityEvidenceKind.L1_SPECIFICATION,
                subject_reference="task:task-1",
                passed=True,
                evidence_reference="quality-evidence-1",
                recorded_at=_NOW,
            )
        ).is_success
        assert unit_of_work.evidence.append_approval(
            ApprovalGate(
                metadata=_metadata("approval-record"),
                approval_gate_id=gate_id,
                pending_operation_reference="run:run-1",
                status=ApprovalGateStatus.APPROVED,
                decision="approved",
                decision_reason="retained but not projected",
                reviewer_reference="reviewer-1",
            )
        ).is_success


def test_run_projection_contains_authorized_redacted_canonical_evidence() -> None:
    database = InMemoryControlPlaneDatabase()
    _seed_canonical_run_evidence(database)
    adapter = _adapter(database)

    result = adapter.project_run(
        _ORG,
        _CORRELATION,
        "run-1",
        RunProvenanceId("provenance-1"),
    )

    assert result.is_success and result.value is not None
    projection = result.value
    assert projection.run_reference == "run-1"
    assert projection.common_agent_versions[0]["agent_version_id"] == "agent-v1"
    assert projection.common_agent_versions[0]["runtime_policy"] == {
        "max_retries": 2,
        "api_token": "[REDACTED]",
    }
    assert projection.agent_tasks[0]["lifecycle_state"] == "queued"
    assert projection.agent_tasks[0]["dependencies"] == ()
    assert projection.artifact_handoffs[0]["parent_lineage"] == ("brief-v1",)
    assert "technical_specification" not in projection.artifact_handoffs[0]
    assert projection.critique_records[0]["state"] == "retained"
    assert projection.quality_evidence[0]["kind"] == "l1_specification"
    assert projection.approval_gates[0]["decision_reason_retained"] is True
    assert "decision_reason" not in projection.approval_gates[0]
    assert projection.pinned_provenance["graph_revision_id"] == "graph-revision-1"

    foreign = adapter.project_run(
        OrganizationId("other-org"),
        CorrelationId("foreign-correlation"),
        "run-1",
        RunProvenanceId("provenance-1"),
    )
    assert not foreign.is_success and foreign.error is not None
    assert foreign.error.code is ErrorCode.AUTHORIZATION_DENIED


def test_non_va_common_records_do_not_require_or_gain_va_fields() -> None:
    database = InMemoryControlPlaneDatabase()
    _seed_canonical_run_evidence(database)

    task = database._state.tasks[TaskId("task-1")]
    provenance = database._state.provenance[RunProvenanceId("provenance-1")]

    assert not hasattr(task, "va_template")
    assert not hasattr(task, "production_phase")
    assert not hasattr(provenance, "va_template")
    assert not hasattr(provenance, "production_phase")
