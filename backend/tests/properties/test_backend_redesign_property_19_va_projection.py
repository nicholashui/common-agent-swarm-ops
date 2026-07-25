"""Property checks for VA metadata as a canonical common-control-plane projection."""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

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
    GraphRevision,
    GraphRevisionId,
    QualityEvidence,
    QualityEvidenceKind,
    RunProvenance,
    RunProvenanceId,
    SwarmInstanceId,
    TaskId,
    TaskLifecycle,
    WorkItem,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId
from app.models.redaction import REDACTED
from app.repositories.control_plane import InMemoryControlPlaneDatabase
from app.va.service import VaDomainAdapter, VaMetadata, VaProductionAction

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-19-organization")
_ACTOR = ActorId("property-19-actor")
_CORRELATION = CorrelationId("property-19-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_COMMANDS = {
    VaProductionAction.CREATE_RUN: "run.create",
    VaProductionAction.DISPATCH_RUN: "run.dispatch",
    VaProductionAction.RESUME_RUN: "run.resume",
    VaProductionAction.EVALUATE_RUN: "run.evaluate",
}


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _pattern(value: str, published: bool) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata(f"pattern-record-{value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-{value}"),
        status=ContractStatus.PUBLISHED if published else ContractStatus.DRAFT,
        graph_template={"va_templates": ("campaign", "explainer")},
        slot_constraints={"required": ("producer",)},
        compatibility_rules={"va_production_phases": ("brief", "production", "review")},
        risk_requirements={"approval": "required"},
        verification_requirements={"quality": True},
        provenance={"source": "published-registry"},
        content_digest=f"sha256:pattern-{value}",
    )


def _agent(value: str) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record-{value}"),
        agent_version_id=AgentVersionId(f"agent-{value}"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=f"producer-{value}",
        category="production",
        responsibilities=("produce",),
        boundaries=("no-unapproved-release",),
        escalation_targets=("human-producer",),
        approval_authority=("release-gate",),
        runtime_policy={"max_retries": 2, "api_token": f"secret-{value}"},
        tool_policy={"allow": ("render",)},
        quality_rubric={"minimum": 0.9},
        critique_relationships=("reviewer",),
        knowledge_bindings=("brand-guide",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest=f"sha256:agent-{value}",
    )


def _adapter(
    database: InMemoryControlPlaneDatabase, dispatched: list[tuple[str, str]]
) -> VaDomainAdapter:
    def record_dispatch(command: str, work_item: WorkItem) -> None:
        dispatched.append((command, str(work_item.work_item_id)))

    return VaDomainAdapter(
        database.unit_of_work,
        CommandService(database.unit_of_work, clock=lambda: _NOW),
        clock=lambda: _NOW,
        dispatcher=record_dispatch,
    )


def _seed_canonical_evidence(
    database: InMemoryControlPlaneDatabase, value: str, pattern: CommonPatternVersion
) -> RunProvenanceId:
    agent = _agent(value)
    task_id = TaskId(f"task-{value}")
    gate_id = ApprovalGateId(f"gate-{value}")
    provenance_id = RunProvenanceId(f"provenance-{value}")
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(pattern).is_success
        assert unit_of_work.common_contracts.append_agent_version(agent).is_success
        assert unit_of_work.provenance.append(
            RunProvenance(
                metadata=_metadata(f"provenance-record-{value}"),
                run_provenance_id=provenance_id,
                graph_revision_id=GraphRevisionId(f"graph-{value}"),
                workflow_definition={"version": "1.0.0"},
                workflow_definition_version="1.0.0",
                agent_version_ids=(agent.agent_version_id,),
                pattern_version_ids=(pattern.pattern_version_id,),
                artifact_version_references=(f"artifact-{value}",),
            )
        ).is_success
        assert unit_of_work.tasks.create(
            AgentTask(
                metadata=_metadata(f"task-record-{value}"),
                task_id=task_id,
                run_reference=f"run-{value}",
                pinned_agent_version_id=agent.agent_version_id,
                dependencies=(),
                constraints={"risk": "controlled"},
                approval_gate_ids=(gate_id,),
                checkpoint_reference=f"checkpoint-{value}",
                state=TaskLifecycle.QUEUED,
            )
        ).is_success
        assert unit_of_work.artifacts.append(
            ArtifactHandoff(
                metadata=_metadata(f"artifact-record-{value}"),
                handoff_id=ArtifactHandoffId(f"handoff-{value}"),
                artifact_identity=f"storyboard-{value}",
                artifact_version=f"artifact-{value}",
                parent_lineage=(f"brief-{value}",),
                source_task_id=task_id,
                source_run_reference=f"run-{value}",
                brief_scope="campaign",
                technical_specification={"protected_artifact": f"secret-{value}"},
                rights_and_consent_state="passed",
                continuity_state="passed",
                quality_control_state="passed",
                target_channels=("review",),
                provenance_reference=f"artifact-provenance-{value}",
            )
        ).is_success
        assert unit_of_work.evidence.append_critique(
            CritiqueRecord(
                metadata=_metadata(f"critique-record-{value}"),
                critique_id=f"critique-{value}",
                source_reference=f"reviewer-{value}",
                target_task_id=task_id,
                relationship_reference="reviewer",
                evidence_reference=f"critique-evidence-{value}",
                submitted_at=_NOW,
            )
        ).is_success
        assert unit_of_work.evidence.append_quality(
            QualityEvidence(
                metadata=_metadata(f"quality-record-{value}"),
                evidence_id=f"quality-{value}",
                kind=QualityEvidenceKind.L1_SPECIFICATION,
                subject_reference=f"task:{task_id}",
                passed=True,
                evidence_reference=f"quality-evidence-{value}",
                recorded_at=_NOW,
            )
        ).is_success
        assert unit_of_work.evidence.append_approval(
            ApprovalGate(
                metadata=_metadata(f"approval-record-{value}"),
                approval_gate_id=gate_id,
                pending_operation_reference=f"run:run-{value}",
                status=ApprovalGateStatus.APPROVED,
                decision="approved",
                decision_reason=f"secret-{value}",
                reviewer_reference=f"reviewer-{value}",
            )
        ).is_success
    return provenance_id


def _non_va_graph(value: str) -> GraphRevision:
    return GraphRevision(
        metadata=_metadata(f"non-va-graph-record-{value}"),
        graph_revision_id=GraphRevisionId(f"non-va-graph-{value}"),
        swarm_instance_id=SwarmInstanceId(f"non-va-swarm-{value}"),
        revision=1,
        nodes=({"node_id": f"producer-{value}", "agent_version_id": f"agent-{value}"},),
        edges=(),
        layout={"direction": "left-to-right"},
        version_pins={"agent": f"agent-{value}", "pattern": f"pattern-{value}"},
        policies={"risk": "controlled"},
    )


def _canonical_evidence_snapshot(
    database: InMemoryControlPlaneDatabase,
) -> tuple[object, ...]:
    state = database._state
    return (
        state.pattern_versions.copy(),
        state.agent_versions.copy(),
        state.provenance.copy(),
        state.tasks.copy(),
        state.artifacts.copy(),
        state.critiques.copy(),
        state.quality_evidence.copy(),
        state.approvals.copy(),
    )


# Feature: backend-redesign, Property 19
# **Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    pattern_is_published=st.booleans(),
    template_matches=st.booleans(),
    phase_matches=st.booleans(),
    viewer_is_authorized=st.booleans(),
    action=st.sampled_from(tuple(VaProductionAction)),
)
def test_property_19_va_metadata_is_a_validated_canonical_projection(
    value: str,
    pattern_is_published: bool,
    template_matches: bool,
    phase_matches: bool,
    viewer_is_authorized: bool,
    action: VaProductionAction,
) -> None:
    """VA metadata gates canonical commands while common evidence remains the source of truth."""
    database = InMemoryControlPlaneDatabase()
    pattern = _pattern(value, pattern_is_published)
    provenance_id = _seed_canonical_evidence(database, value, pattern)
    dispatched: list[tuple[str, str]] = []
    adapter = _adapter(database, dispatched)
    metadata = VaMetadata(
        pattern.pattern_version_id,
        "campaign" if template_matches else f"unknown-template-{value}",
        "production" if phase_matches else f"unknown-phase-{value}",
    )
    validation_result = adapter.validate_metadata(_ORGANIZATION, _CORRELATION, metadata)

    assert validation_result.is_success and validation_result.value is not None
    validation = validation_result.value
    expected_valid = pattern_is_published and template_matches and phase_matches
    assert validation.valid is expected_valid
    if expected_valid:
        assert validation.fields == ()
        assert validation.pattern_content_digest == pattern.content_digest
    else:
        assert validation.pattern_content_digest is None
        expected_fields = (
            ("pattern_version_id",)
            if not pattern_is_published
            else tuple(
                field
                for field, matched in (
                    ("template", template_matches),
                    ("production_phase", phase_matches),
                )
                if not matched
            )
        )
        assert tuple(field.name for field in validation.fields) == expected_fields

    evidence_before_action = _canonical_evidence_snapshot(database)
    action_result = adapter.invoke_action(
        _ORGANIZATION,
        _ACTOR,
        _CORRELATION,
        metadata,
        action,
        f"run-{value}",
        f"idempotency-{value}",
    )
    assert _canonical_evidence_snapshot(database) == evidence_before_action
    if not expected_valid:
        assert not action_result.is_success and action_result.error is not None
        assert action_result.error.code is ErrorCode.VALIDATION_FAILED
        assert dispatched == []
        assert database._state.work_items == {}
        assert database._state.idempotency_records == {}
        assert database._state.audits == {}
        assert database._state.events == {}
        assert database._state.outbox == {}
    else:
        assert action_result.is_success and action_result.value is not None
        outcome = action_result.value
        assert outcome.canonical_command == _COMMANDS[action]
        assert outcome.canonical_subject_reference == f"run:run-{value}"
        assert outcome.work_state == "pending"
        assert not outcome.replayed
        assert dispatched == [(outcome.canonical_command, outcome.work_item_id)]
        assert len(database._state.work_items) == 1
        assert len(database._state.idempotency_records) == 1
        assert len(database._state.audits) == 1
        assert len(database._state.events) == 1
        assert len(database._state.outbox) == 1

    viewer_organization = (
        _ORGANIZATION if viewer_is_authorized else OrganizationId(f"foreign-{value}")
    )
    projection_result = adapter.project_run(
        viewer_organization, _CORRELATION, f"run-{value}", provenance_id
    )
    if not viewer_is_authorized:
        assert not projection_result.is_success and projection_result.error is not None
        assert projection_result.error.code is ErrorCode.AUTHORIZATION_DENIED
    else:
        assert projection_result.is_success and projection_result.value is not None
        projection = projection_result.value
        assert projection.run_reference == f"run-{value}"
        assert projection.common_agent_versions[0]["agent_version_id"] == f"agent-{value}"
        assert projection.common_agent_versions[0]["runtime_policy"] == {
            "max_retries": 2,
            "api_token": REDACTED,
        }
        assert projection.agent_tasks[0]["lifecycle_state"] == TaskLifecycle.QUEUED.value
        assert projection.agent_tasks[0]["dependencies"] == ()
        assert projection.artifact_handoffs[0]["parent_lineage"] == (f"brief-{value}",)
        assert "technical_specification" not in projection.artifact_handoffs[0]
        assert projection.critique_records[0]["state"] == "retained"
        assert projection.quality_evidence[0]["passed"] is True
        assert projection.approval_gates[0]["decision_reason_retained"] is True
        assert "decision_reason" not in projection.approval_gates[0]
        assert projection.pinned_provenance["graph_revision_id"] == f"graph-{value}"

    non_va_graph = _non_va_graph(value)
    assert not hasattr(non_va_graph, "va_template")
    assert not hasattr(non_va_graph, "production_phase")
    assert "va_template" not in GraphRevision.__dataclass_fields__
    assert "production_phase" not in GraphRevision.__dataclass_fields__
    assert all("va" not in key for node in non_va_graph.nodes for key in node)
    assert all("va" not in key for key in non_va_graph.version_pins)
