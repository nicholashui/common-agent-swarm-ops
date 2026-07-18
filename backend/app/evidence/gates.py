"""Deterministic Product-Bar gate evaluation over retained target-local evidence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from hashlib import sha256
from string import hexdigits

from app.evaluation.migration_evidence import (
    MIGRATION_CONTROL_ORGANIZATION_ID,
    MigrationGate,
)
from app.evaluation.models import DEFAULT_NAMED_CHECKS, EvaluationOutcome
from app.evaluation.product_bar import (
    ProductBarCommandResult,
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
)
from app.evidence.records import (
    CRITERION_TRANSITIONS,
    AdapterVersion,
    EvidenceGateAssessment,
    EvidenceGateRecord,
    EvidenceGateSnapshot,
    InMemoryEvidenceGateRepository,
    SchemaVersion,
)
from app.evolution.models import PromotionDecision
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId, EvidenceId, OrganizationId, new_record_id
from app.models.runs import RunStatus, WorkflowEngineKind
from app.video.artifacts import ReleaseDecision
from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT


class EvidenceGateRunner:
    """Assemble independent E1-E9 records without executing production work."""

    def __init__(
        self,
        product_bar: ProductBarEvidenceService,
        repository: InMemoryEvidenceGateRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._product_bar = product_bar
        self._repository = repository
        self._clock = clock


    def evaluate(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        snapshot: EvidenceGateSnapshot,
    ) -> Result[EvidenceGateAssessment, ErrorDetail]:
        """Record every criterion; a failure blocks only its configured transition."""
        validation_error = self._validate_snapshot(organization_id, snapshot)
        if validation_error is not None:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, validation_error, correlation_id)
            )
        records: list[EvidenceGateRecord] = []
        for criterion in ProductBarCriterion:
            passed, reasons = self._evaluate_criterion(criterion, snapshot)
            outcome = (
                ProductBarEvidenceOutcome.PASS if passed else ProductBarEvidenceOutcome.FAIL
            )
            product_bar = self._product_bar.record_evidence(
                organization_id,
                correlation_id,
                criterion,
                outcome,
                run_ids=tuple(run.run_id for run in snapshot.runs),
                evaluation_run_ids=tuple(
                    run.evaluation_run_id for run in snapshot.evaluations
                ),
                evidence_hashes=self._hashes(snapshot),
                command_results=(self._command_result(snapshot),),
                supporting_references=self._references(snapshot),
            )
            if not product_bar.is_success or product_bar.value is None:
                return Result.failure(self._product_bar_error(product_bar.error, correlation_id))
            record = self._new_record(
                organization_id,
                correlation_id,
                snapshot,
                criterion,
                outcome,
                reasons,
                product_bar.value.evidence_id,
            )
            appended = self._repository.append(record)
            if not appended.is_success or appended.value is None:
                return Result.failure(self._repository_error(appended.error, correlation_id))
            records.append(appended.value)
        blocked = tuple(
            record.next_transition
            for record in records
            if record.outcome is ProductBarEvidenceOutcome.FAIL
        )
        return Result.success(
            EvidenceGateAssessment(
                organization_id,
                self._clock(),
                tuple(records),
                blocked,
                production_mutated=False,
            )
        )

    @staticmethod
    def _command_result(snapshot: EvidenceGateSnapshot) -> ProductBarCommandResult:
        command = snapshot.command_result
        return ProductBarCommandResult(
            command.command,
            command.exit_code,
            command.output_digest,
            command.completed_at,
        )


    def _evaluate_criterion(
        self, criterion: ProductBarCriterion, snapshot: EvidenceGateSnapshot
    ) -> tuple[bool, tuple[str, ...]]:
        """Evaluate one capability from only its relevant target-local evidence."""
        engines = {run.engine for run in snapshot.runs if run.status is RunStatus.COMPLETED}
        migration = self._migration_gate_passed(
            snapshot, MigrationGate.CROSS_ORGANIZATION_RESUME_DENIAL
        )
        conditions: dict[ProductBarCriterion, tuple[tuple[str, bool], ...]] = {
            ProductBarCriterion.E1: (
                ("legacy completed", WorkflowEngineKind.LEGACY in engines),
                ("graph completed", WorkflowEngineKind.GRAPH in engines),
                ("operator path check", self._claim(snapshot, criterion, "operator-path")),
            ),
            ProductBarCriterion.E2: (
                (
                    "restart controls check",
                    self._claim(snapshot, criterion, "durable-controls-restart"),
                ),
                ("cross-organization resume denial", migration),
            ),
            ProductBarCriterion.E3: (
                ("completed adapter effect", self._has_completed_effect(snapshot)),
                (
                    "adapter audit check",
                    self._claim(snapshot, criterion, "adapter-audit-effect"),
                ),
            ),
            ProductBarCriterion.E4: (
                ("traceable process artifact", self._has_process_artifact(snapshot)),
            ),
            ProductBarCriterion.E5: (
                ("sandbox assessment is non-mutating", self._has_safe_sandbox(snapshot)),
                (
                    "canary rollback check",
                    self._claim(snapshot, criterion, "sandbox-canary-rollback"),
                ),
            ),
            ProductBarCriterion.E6: (
                ("complete twenty-task evaluation", self._has_complete_evaluation(snapshot)),
                (
                    "automatic promotion blocked",
                    self._claim(snapshot, criterion, "automatic-promotion-blocked"),
                ),
            ),
            ProductBarCriterion.E7: (
                ("operator forms check", self._claim(snapshot, criterion, "frontend-forms")),
            ),
            ProductBarCriterion.E8: (
                (
                    "configured recovery check",
                    self._claim(snapshot, criterion, "postgres-recovery"),
                ),
                ("cross-organization resume denial", migration),
            ),
            ProductBarCriterion.E9: (
                ("exact video inventory", self._has_video_inventory(snapshot)),
                ("retained release denial", self._has_release_denial(snapshot)),
                (
                    "release denial cases",
                    self._claim(snapshot, criterion, "release-denial-cases"),
                ),
            ),
        }
        failures = tuple(name for name, passed in conditions[criterion] if not passed)
        passed = not failures and snapshot.command_result.exit_code == 0
        return passed, failures

    @staticmethod
    def _claim(
        snapshot: EvidenceGateSnapshot, criterion: ProductBarCriterion, name: str
    ) -> bool:
        return any(
            claim.criterion is criterion and claim.name == name and claim.passed
            for claim in snapshot.claims
        )


    @staticmethod
    def _has_completed_effect(snapshot: EvidenceGateSnapshot) -> bool:
        return any(
            run.status is RunStatus.COMPLETED and run.tool_effects for run in snapshot.runs
        )

    @staticmethod
    def _has_process_artifact(snapshot: EvidenceGateSnapshot) -> bool:
        return any(
            artifact.source_log_set_id.strip() and artifact.supporting_record_refs
            for artifact in snapshot.process_artifacts
        )

    @staticmethod
    def _has_safe_sandbox(snapshot: EvidenceGateSnapshot) -> bool:
        return any(
            assessment.candidate_count == 1
            and assessment.decision
            in {PromotionDecision.BLOCKED, PromotionDecision.PERMITTED}
            and not assessment.production_applied
            for assessment in snapshot.promotion_assessments
        )

    @staticmethod
    def _has_complete_evaluation(snapshot: EvidenceGateSnapshot) -> bool:
        expected_kinds = {check.kind for check in DEFAULT_NAMED_CHECKS}
        return any(
            run.completed
            and run.transition_permitted
            and len(run.task_ids) >= 20
            and {result.check_kind for result in run.results} == expected_kinds
            and all(result.outcome is EvaluationOutcome.PASS for result in run.results)
            for run in snapshot.evaluations
        )

    @staticmethod
    def _has_video_inventory(snapshot: EvidenceGateSnapshot) -> bool:
        return any(
            report.is_valid
            and len(report.manifest_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
            and len(report.inventory_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
            for report in snapshot.video_inventory_reports
        )

    @staticmethod
    def _has_release_denial(snapshot: EvidenceGateSnapshot) -> bool:
        return any(
            request.decision is ReleaseDecision.DENIED
            and request.unmet_conditions
            and not request.artifact_released
            for request in snapshot.release_requests
        )

    @staticmethod
    def _migration_gate_passed(
        snapshot: EvidenceGateSnapshot, required_gate: MigrationGate
    ) -> bool:
        return any(
            assessment.is_satisfied
            and any(gate.gate is required_gate and gate.passed for gate in assessment.gates)
            for assessment in snapshot.migration_assessments
        )


    def _new_record(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        snapshot: EvidenceGateSnapshot,
        criterion: ProductBarCriterion,
        outcome: ProductBarEvidenceOutcome,
        reasons: tuple[str, ...],
        product_bar_evidence_id: EvidenceId,
    ) -> EvidenceGateRecord:
        timestamp = self._clock()
        metadata = RecordMetadata(
            new_record_id(),
            organization_id,
            correlation_id,
            SCHEMA_VERSION,
            1,
            timestamp,
            timestamp,
        )
        return EvidenceGateRecord(
            metadata=metadata,
            evidence_id=EvidenceId(str(new_record_id())),
            product_bar_evidence_id=product_bar_evidence_id,
            criterion=criterion,
            outcome=outcome,
            next_transition=CRITERION_TRANSITIONS[criterion],
            reasons=reasons,
            run_ids=tuple(run.run_id for run in snapshot.runs),
            evaluation_run_ids=tuple(
                run.evaluation_run_id for run in snapshot.evaluations
            ),
            migration_evidence_ids=tuple(
                item.evidence_id for item in snapshot.migration_assessments
            ),
            release_request_ids=tuple(
                item.release_request_id for item in snapshot.release_requests
            ),
            local_record_ids=self._local_record_ids(snapshot),
            evidence_hashes=self._hashes(snapshot),
            adapter_versions=snapshot.adapter_versions,
            schema_versions=snapshot.schema_versions,
            command_result=snapshot.command_result,
            supporting_references=self._references(snapshot),
            recorded_at=timestamp,
        )

    @staticmethod
    def _local_record_ids(snapshot: EvidenceGateSnapshot) -> tuple[str, ...]:
        values = [
            *(str(run.metadata.record_id) for run in snapshot.runs),
            *(str(run.metadata.record_id) for run in snapshot.evaluations),
            *(str(item.metadata.record_id) for item in snapshot.migration_assessments),
            *(str(item.metadata.record_id) for item in snapshot.process_artifacts),
            *(str(item.metadata.record_id) for item in snapshot.promotion_assessments),
            *(str(item.metadata.record_id) for item in snapshot.release_requests),
            *(str(item.evidence_id) for item in snapshot.claims),
        ]
        return tuple(dict.fromkeys(values))


    def _references(self, snapshot: EvidenceGateSnapshot) -> tuple[EvidenceReference, ...]:
        references: list[EvidenceReference] = []
        references.extend(
            EvidenceReference(
                EvidenceId(str(run.run_id)), run.workflow_definition_digest, "run"
            )
            for run in snapshot.runs
        )
        references.extend(
            EvidenceReference(
                EvidenceId(str(run.evaluation_run_id)), run.configuration_digest, "evaluation"
            )
            for run in snapshot.evaluations
        )
        references.extend(
            EvidenceReference(item.evidence_id, item.configuration_digest, "migration")
            for item in snapshot.migration_assessments
        )
        references.extend(
            EvidenceReference(
                EvidenceId(str(item.release_request_id)),
                self._digest(str(item.release_request_id)),
                "video-release",
            )
            for item in snapshot.release_requests
        )
        references.extend(
            EvidenceReference(item.evidence_id, item.digest, "local-check")
            for item in snapshot.claims
        )
        references.extend(self._adapter_reference(adapter) for adapter in snapshot.adapter_versions)
        references.extend(self._schema_reference(schema) for schema in snapshot.schema_versions)
        return tuple(references)

    def _adapter_reference(self, adapter: AdapterVersion) -> EvidenceReference:
        return EvidenceReference(
            EvidenceId(adapter.adapter_id),
            self._digest(f"{adapter.adapter_id}:{adapter.version}"),
            "local-adapter",
        )

    def _schema_reference(self, schema: SchemaVersion) -> EvidenceReference:
        return EvidenceReference(
            EvidenceId(schema.schema_name),
            self._digest(f"{schema.schema_name}:{schema.version}"),
            "schema",
        )

    def _hashes(self, snapshot: EvidenceGateSnapshot) -> tuple[str, ...]:
        return tuple(dict.fromkeys(reference.digest for reference in self._references(snapshot)))

    @staticmethod
    def _digest(value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()


    @staticmethod
    def _validate_snapshot(
        organization_id: OrganizationId, snapshot: EvidenceGateSnapshot
    ) -> str | None:
        if not snapshot.runs and not snapshot.evaluations:
            return "Evidence gates require a local run or evaluation record."
        if not snapshot.adapter_versions or not snapshot.schema_versions:
            return "Evidence gates require retained adapter and schema versions."
        command = snapshot.command_result
        if not command.command.strip() or not EvidenceGateRunner._is_sha256(
            command.output_digest
        ):
            return "Evidence gates require a local command and SHA-256 output digest."
        if any(
            not item.adapter_id.strip() or not item.version.strip()
            for item in snapshot.adapter_versions
        ):
            return "Evidence gate adapter versions must be non-empty."
        if any(
            not item.schema_name.strip() or item.version < 1
            for item in snapshot.schema_versions
        ):
            return "Evidence gate schema versions must be positive and named."
        if (
            any(record.metadata.organization_id != organization_id for record in snapshot.runs)
            or any(
                record.metadata.organization_id != organization_id
                for record in snapshot.evaluations
            )
            or any(
                record.metadata.organization_id != organization_id
                for record in snapshot.process_artifacts
            )
            or any(
                record.metadata.organization_id != organization_id
                for record in snapshot.promotion_assessments
            )
            or any(
                record.metadata.organization_id != organization_id
                for record in snapshot.release_requests
            )
        ):
            return "Evidence gates cannot combine records from another organization."
        if any(
            record.metadata.organization_id != MIGRATION_CONTROL_ORGANIZATION_ID
            for record in snapshot.migration_assessments
        ):
            return "Migration evidence must use the target-local migration control organization."
        if any(
            not claim.name.strip() or not EvidenceGateRunner._is_sha256(claim.digest)
            for claim in snapshot.claims
        ):
            return "Evidence gate claims require names and SHA-256 digests."
        return None

    @staticmethod
    def _is_sha256(value: str) -> bool:
        return len(value) == 64 and all(character in hexdigits for character in value)

    @staticmethod
    def _product_bar_error(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Product-Bar evidence retention failed.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Evidence gate retention failed.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)
