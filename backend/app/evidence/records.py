"""Immutable records for deterministic, target-local evidence gates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from threading import RLock

from app.evaluation.migration_evidence import MigrationAssessmentEvidence
from app.evaluation.models import EvaluationRun
from app.evaluation.product_bar import ProductBarCriterion, ProductBarEvidenceOutcome
from app.evolution.models import PromotionAssessment
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvaluationRunId,
    EvidenceId,
    OrganizationId,
    RunId,
)
from app.models.runs import RunRecord
from app.process_intelligence.models import ProcessArtifact
from app.video.artifacts import ReleaseRequest, ReleaseRequestId
from app.video.inventory import VideoInventoryReport


class EvidenceTransition(StrEnum):
    """The one local capability transition guarded by each Product-Bar criterion."""

    FLAGSHIP_GRAPH_DEFAULT = "flagship_graph_default"
    DURABLE_CONTROLS = "durable_controls"
    ADAPTER_EFFECTS = "adapter_effects"
    PROCESS_INTELLIGENCE = "process_intelligence"
    SANDBOX_PROMOTION_REVIEW = "sandbox_promotion_review"
    EVALUATION_TRANSITION = "evaluation_transition"
    OPERATOR_FORMS = "operator_forms"
    DURABLE_RECOVERY = "durable_recovery"
    VIDEO_RELEASE_READINESS = "video_release_readiness"


CRITERION_TRANSITIONS: dict[ProductBarCriterion, EvidenceTransition] = {
    ProductBarCriterion.E1: EvidenceTransition.FLAGSHIP_GRAPH_DEFAULT,
    ProductBarCriterion.E2: EvidenceTransition.DURABLE_CONTROLS,
    ProductBarCriterion.E3: EvidenceTransition.ADAPTER_EFFECTS,
    ProductBarCriterion.E4: EvidenceTransition.PROCESS_INTELLIGENCE,
    ProductBarCriterion.E5: EvidenceTransition.SANDBOX_PROMOTION_REVIEW,
    ProductBarCriterion.E6: EvidenceTransition.EVALUATION_TRANSITION,
    ProductBarCriterion.E7: EvidenceTransition.OPERATOR_FORMS,
    ProductBarCriterion.E8: EvidenceTransition.DURABLE_RECOVERY,
    ProductBarCriterion.E9: EvidenceTransition.VIDEO_RELEASE_READINESS,
}


@dataclass(frozen=True, slots=True)
class AdapterVersion:
    """The version of one registered target-local adapter used by evidence."""

    adapter_id: str
    version: str


@dataclass(frozen=True, slots=True)
class SchemaVersion:
    """The version of one local schema represented by an evidence record."""

    schema_name: str
    version: int


@dataclass(frozen=True, slots=True)
class LocalCommandResult:
    """Digest-only result of a command executed in the target workspace."""

    command: str
    exit_code: int
    output_digest: str
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class LocalEvidenceClaim:
    """A named, hash-addressed assertion produced by a target-local test or check."""

    evidence_id: EvidenceId
    criterion: ProductBarCriterion
    name: str
    passed: bool
    digest: str
    recorded_at: datetime
    supporting_references: tuple[EvidenceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class EvidenceGateSnapshot:
    """Current immutable target-local sources used to independently assess E1 through E9."""

    runs: tuple[RunRecord, ...]
    evaluations: tuple[EvaluationRun, ...]
    migration_assessments: tuple[MigrationAssessmentEvidence, ...]
    process_artifacts: tuple[ProcessArtifact, ...]
    promotion_assessments: tuple[PromotionAssessment, ...]
    video_inventory_reports: tuple[VideoInventoryReport, ...]
    release_requests: tuple[ReleaseRequest, ...]
    claims: tuple[LocalEvidenceClaim, ...]
    adapter_versions: tuple[AdapterVersion, ...]
    schema_versions: tuple[SchemaVersion, ...]
    command_result: LocalCommandResult


@dataclass(frozen=True, slots=True)
class EvidenceGateRecord:
    """One append-only, criterion-specific gate result with complete local provenance."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    product_bar_evidence_id: EvidenceId
    criterion: ProductBarCriterion
    outcome: ProductBarEvidenceOutcome
    next_transition: EvidenceTransition
    reasons: tuple[str, ...]
    run_ids: tuple[RunId, ...]
    evaluation_run_ids: tuple[EvaluationRunId, ...]
    migration_evidence_ids: tuple[EvidenceId, ...]
    release_request_ids: tuple[ReleaseRequestId, ...]
    local_record_ids: tuple[str, ...]
    evidence_hashes: tuple[str, ...]
    adapter_versions: tuple[AdapterVersion, ...]
    schema_versions: tuple[SchemaVersion, ...]
    command_result: LocalCommandResult
    supporting_references: tuple[EvidenceReference, ...]
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class EvidenceGateAssessment:
    """Independent E1-E9 records and the narrowly scoped transitions they block."""

    organization_id: OrganizationId
    assessed_at: datetime
    records: tuple[EvidenceGateRecord, ...]
    blocked_transitions: tuple[EvidenceTransition, ...]
    production_mutated: bool = False


class InMemoryEvidenceGateRepository:
    """Local append-only storage used by the deterministic evidence runner."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[EvidenceId, EvidenceGateRecord] = {}

    def append(self, record: EvidenceGateRecord) -> Result[EvidenceGateRecord, ErrorDetail]:
        """Retain one immutable result without replacing prior evidence."""
        with self._lock:
            if record.evidence_id in self._records:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Evidence gate record already exists.",
                        CorrelationId("evidence-gates"),
                    )
                )
            self._records[record.evidence_id] = record
            return Result.success(record)

    def records(self) -> tuple[EvidenceGateRecord, ...]:
        """Return a deterministic append-only snapshot for local inspection."""
        with self._lock:
            return tuple(self._records.values())
