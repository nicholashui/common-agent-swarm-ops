"""Deterministic target-local evidence fixture for E1-E9 gate validation."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from app.evaluation.migration_evidence import (
    MigrationAssessmentEvidence,
    MigrationGate,
    MigrationGateEvidence,
)
from app.evaluation.models import (
    DEFAULT_NAMED_CHECKS,
    EvaluationCellResult,
    EvaluationOutcome,
    EvaluationRun,
)
from app.evaluation.product_bar import ProductBarCriterion
from app.evidence.records import (
    AdapterVersion,
    EvidenceGateSnapshot,
    LocalCommandResult,
    LocalEvidenceClaim,
    SchemaVersion,
)
from app.evolution.models import (
    MetricComparison,
    PromotionAssessment,
    PromotionAssessmentId,
    PromotionDecision,
    SandboxVariantId,
)
from app.models.common import RecordMetadata
from app.models.identifiers import (
    CorrelationId,
    EvaluationResultId,
    EvaluationRunId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.process_intelligence.models import ProcessArtifact, ProcessArtifactKind
from app.video.artifacts import (
    ReleaseCondition,
    ReleaseDecision,
    ReleaseRequest,
    ReleaseRequestId,
    VideoArtifactVersionId,
)
from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT, VideoInventoryReport

NOW = datetime(2025, 1, 1, tzinfo=UTC)
FIXTURE_ORGANIZATION_ID = OrganizationId("org-evidence-fixture")
FIXTURE_CORRELATION_ID = CorrelationId("corr-evidence-fixture")



def build_target_local_evidence_fixture() -> EvidenceGateSnapshot:
    """Build one complete local snapshot without invoking adapters or transition APIs."""
    evaluation = _evaluation()
    return EvidenceGateSnapshot(
        runs=(
            _run("legacy", WorkflowEngineKind.LEGACY, ()),
            _run("graph", WorkflowEngineKind.GRAPH, (_effect(),)),
        ),
        evaluations=(evaluation,),
        migration_assessments=(_migration(),),
        process_artifacts=(_process_artifact(),),
        promotion_assessments=(_promotion(evaluation.evaluation_run_id),),
        video_inventory_reports=(_video_inventory(),),
        release_requests=(_release_request(),),
        claims=_claims(),
        adapter_versions=(
            AdapterVersion("crm.lookup", "1.0.0"),
            AdapterVersion("media.stub", "1.0.0"),
        ),
        schema_versions=(
            SchemaVersion("run-record", 1),
            SchemaVersion("video-release", 1),
        ),
        command_result=LocalCommandResult(
            "python -m pytest --tb=short -q tests/evidence",
            0,
            _digest("evidence-fixture-command"),
            NOW,
        ),
    )


def _metadata(
    record_id: str,
    organization_id: OrganizationId = FIXTURE_ORGANIZATION_ID,
) -> RecordMetadata:
    return RecordMetadata(
        RecordId(record_id),
        organization_id,
        FIXTURE_CORRELATION_ID,
        1,
        1,
        NOW,
        NOW,
    )


def _run(name: str, engine: WorkflowEngineKind, effects: tuple[ToolEffect, ...]) -> RunRecord:
    return RunRecord(
        _metadata(f"record-run-{name}"),
        RunId(f"run-{name}"),
        WorkflowDefinitionId(f"workflow-{name}"),
        "1.0.0",
        _digest(f"definition-{name}"),
        engine,
        RunStatus.COMPLETED,
        NOW,
        tool_effects=effects,
    )


def _effect() -> ToolEffect:
    return ToolEffect(
        "crm.lookup", _digest("request"), "completed", _digest("effect"), NOW, True
    )



def _evaluation() -> EvaluationRun:
    task_ids = tuple(f"golden-{index:03d}" for index in range(1, 21))
    results = tuple(
        EvaluationCellResult(
            EvaluationResultId(f"evaluation-result-{task_id}-{check.kind.value}"),
            task_id,
            check.name,
            check.kind,
            check.blocking,
            EvaluationOutcome.PASS,
            NOW,
            _digest(f"{task_id}:{check.name}:pass"),
        )
        for task_id in task_ids
        for check in DEFAULT_NAMED_CHECKS
    )
    return EvaluationRun(
        _metadata("record-evaluation"),
        EvaluationRunId("evaluation-fixture"),
        _digest("evaluation-config"),
        task_ids,
        DEFAULT_NAMED_CHECKS,
        results,
        True,
        True,
    )


def _migration() -> MigrationAssessmentEvidence:
    gates = tuple(
        MigrationGateEvidence(gate, True, (_digest(gate.value),))
        for gate in MigrationGate
    )
    return MigrationAssessmentEvidence(
        _metadata("record-migration", OrganizationId("host-migration")),
        EvidenceId("migration-fixture"),
        _digest("migration-config"),
        gates,
        NOW,
    )


def _process_artifact() -> ProcessArtifact:
    return ProcessArtifact(
        _metadata("record-process"),
        ProcessArtifactKind.DISCOVERED_PROCESS,
        "log-set-fixture",
        ("event-fixture",),
        {"process": "fixture"},
    )


def _promotion(evaluation_run_id: EvaluationRunId) -> PromotionAssessment:
    metric = MetricComparison(10.0, 11.0)
    return PromotionAssessment(
        _metadata("record-promotion"),
        PromotionAssessmentId("assessment-fixture"),
        SandboxVariantId("variant-fixture"),
        1,
        str(evaluation_run_id),
        metric,
        MetricComparison(10.0, 10.0),
        MetricComparison(10.0, 10.0),
        (),
        (),
        PromotionDecision.PERMITTED,
        production_applied=False,
    )



def _video_inventory() -> VideoInventoryReport:
    agents = tuple(f"video.agent-{index:03d}" for index in range(EXPECTED_VIDEO_AGENT_COUNT))
    return VideoInventoryReport(True, agents, agents, agents)


def _release_request() -> ReleaseRequest:
    return ReleaseRequest(
        _metadata("record-release"),
        ReleaseRequestId("release-fixture"),
        VideoArtifactVersionId("artifact-fixture"),
        (ReleaseCondition("rights_and_consent", False, ("fixture-rights",)),),
        ("rights_and_consent",),
        ReleaseDecision.DENIED,
        artifact_released=False,
    )


def _claims() -> tuple[LocalEvidenceClaim, ...]:
    checks = (
        (ProductBarCriterion.E1, "operator-path"),
        (ProductBarCriterion.E2, "durable-controls-restart"),
        (ProductBarCriterion.E3, "adapter-audit-effect"),
        (ProductBarCriterion.E5, "sandbox-canary-rollback"),
        (ProductBarCriterion.E6, "automatic-promotion-blocked"),
        (ProductBarCriterion.E7, "frontend-forms"),
        (ProductBarCriterion.E8, "postgres-recovery"),
        (ProductBarCriterion.E9, "release-denial-cases"),
    )
    return tuple(
        LocalEvidenceClaim(
            EvidenceId(f"claim-{criterion.value.lower()}"),
            criterion,
            name,
            True,
            _digest(name),
            NOW,
        )
        for criterion, name in checks
    )


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()
