"""VA metadata validation, canonical command mapping, and evidence projection."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.core.command_service import CommandService, CommandSubmission, WorkCommand, WorkKind
from app.core.idempotency import request_digest
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AgentTask,
    ApprovalGate,
    ArtifactHandoff,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    CritiqueRecord,
    IdempotencyRecord,
    IdempotencyStatus,
    QualityEvidence,
    RunProvenance,
    RunProvenanceId,
    WorkItem,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, new_record_id
from app.models.redaction import RedactionService, RedactionSurface
from app.repositories.control_plane import ControlPlaneUnitOfWork

UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]
CanonicalDispatcher = Callable[[str, WorkItem], None]


class VaProductionAction(StrEnum):
    """VA actions with an explicit mapping to a common control-plane command."""

    CREATE_RUN = "create_run"
    DISPATCH_RUN = "dispatch_run"
    RESUME_RUN = "resume_run"
    EVALUATE_RUN = "evaluate_run"


_ACTION_COMMANDS: Mapping[VaProductionAction, tuple[str, WorkKind]] = {
    VaProductionAction.CREATE_RUN: ("run.create", WorkKind.RUN),
    VaProductionAction.DISPATCH_RUN: ("run.dispatch", WorkKind.RUN),
    VaProductionAction.RESUME_RUN: ("run.resume", WorkKind.RUN),
    VaProductionAction.EVALUATE_RUN: ("run.evaluate", WorkKind.EVALUATION),
}


@dataclass(frozen=True, slots=True)
class VaMetadata:
    """VA-only template/phase labels tied to one published common pattern version."""

    pattern_version_id: CommonPatternVersionId
    template: str
    production_phase: str

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.pattern_version_id), "pattern_version_id"),
            (self.template, "template"),
            (self.production_phase, "production_phase"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")


@dataclass(frozen=True, slots=True)
class VaMetadataValidation:
    """Field-safe validation against the referenced published common pattern."""

    metadata: VaMetadata
    valid: bool
    fields: tuple[ErrorField, ...]
    pattern_content_digest: str | None = None

    def __post_init__(self) -> None:
        if self.valid == bool(self.fields):
            raise ValueError("Valid VA metadata cannot contain issues and invalid metadata must.")
        if self.valid != (self.pattern_content_digest is not None):
            raise ValueError("Only valid VA metadata may expose the published pattern digest.")


@dataclass(frozen=True, slots=True)
class VaActionOutcome:
    """A VA action translated to one durable canonical command."""

    validation: VaMetadataValidation
    canonical_command: str
    canonical_subject_reference: str
    work_item_id: str
    work_state: str
    replayed: bool


@dataclass(frozen=True, slots=True)
class VaRunProjection:
    """Authorized redacted canonical evidence; no parallel VA evidence model is created."""

    run_reference: str
    common_agent_versions: tuple[Mapping[str, object], ...]
    agent_tasks: tuple[Mapping[str, object], ...]
    artifact_handoffs: tuple[Mapping[str, object], ...]
    critique_records: tuple[Mapping[str, object], ...]
    quality_evidence: tuple[Mapping[str, object], ...]
    approval_gates: tuple[Mapping[str, object], ...]
    pinned_provenance: Mapping[str, object]


class VaDomainAdapter:
    """Translate VA concepts onto published patterns and common command/evidence contracts."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        command_service: CommandService,
        *,
        clock: Callable[[], datetime] = utc_now,
        dispatcher: CanonicalDispatcher | None = None,
        redactor: RedactionService | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._command_service = command_service
        self._clock = clock
        self._dispatcher = dispatcher
        self._redactor = redactor or RedactionService()

    def validate_metadata(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        metadata: VaMetadata,
    ) -> Result[VaMetadataValidation, ErrorDetail]:
        """Validate VA labels only against their organization-scoped published pattern."""
        with self._unit_of_work_factory() as unit_of_work:
            pattern_result = unit_of_work.common_contracts.get_pattern_version(
                organization_id, metadata.pattern_version_id
            )
            pattern = pattern_result.value
            if (
                not pattern_result.is_success
                or pattern is None
                or pattern.status is not ContractStatus.PUBLISHED
            ):
                return Result.success(
                    self._invalid(
                        metadata,
                        ErrorField(
                            "pattern_version_id",
                            "must reference an available published common pattern version",
                        ),
                    )
                )
        fields = self._metadata_issues(metadata, pattern)
        if fields:
            return Result.success(VaMetadataValidation(metadata, False, fields))
        return Result.success(
            VaMetadataValidation(metadata, True, (), pattern_content_digest=pattern.content_digest)
        )

    def invoke_action(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        metadata: VaMetadata,
        action: VaProductionAction,
        run_reference: str,
        idempotency_key: str,
    ) -> Result[VaActionOutcome, ErrorDetail]:
        """Block invalid VA metadata, then atomically retain one canonical work command."""
        validation_result = self.validate_metadata(organization_id, correlation_id, metadata)
        if not validation_result.is_success or validation_result.value is None:
            return Result.failure(self._repository_error(validation_result.error, correlation_id))
        validation = validation_result.value
        if not validation.valid:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "VA metadata does not satisfy the published common pattern.",
                    correlation_id,
                    fields=validation.fields,
                )
            )
        if not run_reference.strip():
            return Result.failure(
                self._validation_error(correlation_id, "Run reference is required.")
            )
        if not idempotency_key.strip():
            return Result.failure(
                self._validation_error(correlation_id, "A non-empty idempotency key is required.")
            )
        command_name, work_kind = _ACTION_COMMANDS[action]
        subject_reference = f"run:{run_reference}"
        digest = request_digest(
            "va.production_action",
            {
                "action": action.value,
                "canonical_command": command_name,
                "pattern_version_id": str(metadata.pattern_version_id),
                "template": metadata.template,
                "production_phase": metadata.production_phase,
                "run_reference": run_reference,
            },
        )
        with self._unit_of_work_factory() as unit_of_work:
            existing = unit_of_work.idempotency.get(
                organization_id, actor_id, idempotency_key
            )
            if existing.is_success and existing.value is not None:
                return self._replayed_outcome(existing.value, validation, digest, correlation_id)
            if existing.error is None or existing.error.code is not ErrorCode.NOT_FOUND:
                return Result.failure(self._repository_error(existing.error, correlation_id))

            now = self._clock()
            reservation = IdempotencyRecord(
                metadata=self._metadata(organization_id, correlation_id, now),
                actor_id=actor_id,
                idempotency_key=idempotency_key,
                request_digest=digest,
                status=IdempotencyStatus.RESERVED,
            )
            reserved = unit_of_work.idempotency.reserve(reservation)
            if not reserved.is_success:
                return Result.failure(self._conflict(correlation_id))
            submission_result = self._command_service.submit_in_transaction(
                unit_of_work,
                organization_id,
                correlation_id,
                WorkCommand(
                    kind=work_kind,
                    subject_reference=subject_reference,
                    idempotency_key=idempotency_key,
                    scheduled_at=now,
                ),
            )
            if not submission_result.is_success or submission_result.value is None:
                unit_of_work.rollback()
                return Result.failure(
                    self._repository_error(submission_result.error, correlation_id)
                )
            submission = submission_result.value
            payload = self._action_payload(
                command_name, subject_reference, submission, replayed=False
            )
            completed = unit_of_work.idempotency.complete(
                IdempotencyRecord(
                    metadata=reservation.metadata,
                    actor_id=actor_id,
                    idempotency_key=idempotency_key,
                    request_digest=digest,
                    status=IdempotencyStatus.COMPLETED,
                    response_reference=f"va-command:{submission.work_item.work_item_id}",
                    response_payload=payload,
                )
            )
            if not completed.is_success:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(completed.error, correlation_id))

        self._deliver(command_name, submission)
        return Result.success(self._outcome(validation, payload, replayed=False))

    def project_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        run_reference: str,
        provenance_id: RunProvenanceId,
    ) -> Result[VaRunProjection, ErrorDetail]:
        """Project common run evidence through organization-scoped repositories and redaction."""
        if not run_reference.strip():
            return Result.failure(
                self._validation_error(correlation_id, "Run reference is required.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            provenance_result = unit_of_work.provenance.get(organization_id, provenance_id)
            provenance = provenance_result.value
            if not provenance_result.is_success or provenance is None:
                return Result.failure(self._unavailable_projection(correlation_id))
            tasks_result = unit_of_work.tasks.for_run(organization_id, run_reference)
            artifacts_result = unit_of_work.artifacts.for_run(organization_id, run_reference)
            if tasks_result.value is None or artifacts_result.value is None:
                return Result.failure(self._unavailable_projection(correlation_id))
            tasks = tasks_result.value
            artifacts = artifacts_result.value
            critiques_result = unit_of_work.evidence.critiques_for_tasks(
                organization_id, tuple(task.task_id for task in tasks)
            )
            if critiques_result.value is None:
                return Result.failure(self._unavailable_projection(correlation_id))
            critiques = critiques_result.value
            quality = self._quality_records(
                unit_of_work,
                organization_id,
                run_reference,
                tuple(str(task.task_id) for task in tasks),
            )
            if quality is None:
                return Result.failure(self._unavailable_projection(correlation_id))
            approvals = []
            for gate_id in dict.fromkeys(
                gate_id for task in tasks for gate_id in task.approval_gate_ids
            ):
                gate_result = unit_of_work.evidence.get_approval(organization_id, gate_id)
                if not gate_result.is_success or gate_result.value is None:
                    return Result.failure(self._unavailable_projection(correlation_id))
                approvals.append(gate_result.value)
            agents = []
            for version_id in provenance.agent_version_ids:
                agent_result = unit_of_work.common_contracts.get_agent_version(
                    organization_id, version_id
                )
                if not agent_result.is_success or agent_result.value is None:
                    return Result.failure(self._unavailable_projection(correlation_id))
                agents.append(agent_result.value)

        return Result.success(
            VaRunProjection(
                run_reference=run_reference,
                common_agent_versions=tuple(self._agent_projection(agent) for agent in agents),
                agent_tasks=tuple(self._task_projection(task) for task in tasks),
                artifact_handoffs=tuple(
                    self._artifact_projection(artifact) for artifact in artifacts
                ),
                critique_records=tuple(
                    self._critique_projection(critique) for critique in critiques
                ),
                quality_evidence=tuple(self._quality_projection(record) for record in quality),
                approval_gates=tuple(self._approval_projection(gate) for gate in approvals),
                pinned_provenance=self._provenance_projection(provenance),
            )
        )

    @staticmethod
    def _metadata_issues(
        metadata: VaMetadata, pattern: CommonPatternVersion
    ) -> tuple[ErrorField, ...]:
        templates = VaDomainAdapter._allowed_values(
            pattern.graph_template, ("va_templates", "templates", "template")
        )
        phases = VaDomainAdapter._allowed_values(
            pattern.compatibility_rules,
            ("va_production_phases", "production_phases", "phases"),
        )
        issues: list[ErrorField] = []
        if metadata.template not in templates:
            issues.append(
                ErrorField("template", "must be allowed by the published common pattern")
            )
        if metadata.production_phase not in phases:
            issues.append(
                ErrorField(
                    "production_phase", "must be allowed by the published common pattern"
                )
            )
        return tuple(issues)

    @staticmethod
    def _allowed_values(
        source: Mapping[str, object], keys: Sequence[str]
    ) -> frozenset[str]:
        values: set[str] = set()
        for key in keys:
            candidate = source.get(key)
            if isinstance(candidate, str) and candidate.strip():
                values.add(candidate)
            elif isinstance(candidate, Sequence) and not isinstance(candidate, str):
                values.update(
                    value for value in candidate if isinstance(value, str) and value.strip()
                )
        return frozenset(values)

    @staticmethod
    def _invalid(metadata: VaMetadata, field: ErrorField) -> VaMetadataValidation:
        return VaMetadataValidation(metadata=metadata, valid=False, fields=(field,))

    def _replayed_outcome(
        self,
        record: IdempotencyRecord,
        validation: VaMetadataValidation,
        digest: str,
        correlation_id: CorrelationId,
    ) -> Result[VaActionOutcome, ErrorDetail]:
        if (
            record.request_digest != digest
            or record.status is not IdempotencyStatus.COMPLETED
            or record.response_payload is None
        ):
            return Result.failure(self._conflict(correlation_id))
        return Result.success(self._outcome(validation, record.response_payload, replayed=True))

    @staticmethod
    def _action_payload(
        command_name: str,
        subject_reference: str,
        submission: CommandSubmission,
        *,
        replayed: bool,
    ) -> Mapping[str, object]:
        return {
            "canonical_command": command_name,
            "canonical_subject_reference": subject_reference,
            "work_item_id": str(submission.work_item.work_item_id),
            "work_state": submission.work_item.state.value,
            "replayed": replayed,
        }

    @staticmethod
    def _outcome(
        validation: VaMetadataValidation,
        payload: Mapping[str, object],
        *,
        replayed: bool,
    ) -> VaActionOutcome:
        canonical_command = payload.get("canonical_command")
        subject_reference = payload.get("canonical_subject_reference")
        work_item_id = payload.get("work_item_id")
        work_state = payload.get("work_state")
        if not all(
            isinstance(value, str)
            for value in (canonical_command, subject_reference, work_item_id, work_state)
        ):
            raise RuntimeError("Stored VA command response is invalid.")
        assert isinstance(canonical_command, str)
        assert isinstance(subject_reference, str)
        assert isinstance(work_item_id, str)
        assert isinstance(work_state, str)
        return VaActionOutcome(
            validation=validation,
            canonical_command=canonical_command,
            canonical_subject_reference=subject_reference,
            work_item_id=work_item_id,
            work_state=work_state,
            replayed=replayed,
        )

    def _deliver(self, command_name: str, submission: CommandSubmission) -> None:
        dispatcher = self._dispatcher
        if dispatcher is None:
            self._command_service.deliver(submission)
            return
        self._command_service.deliver(
            submission,
            dispatch=lambda work_item: dispatcher(command_name, work_item),
        )

    @staticmethod
    def _quality_records(
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        run_reference: str,
        task_ids: tuple[str, ...],
    ) -> tuple[QualityEvidence, ...] | None:
        records: list[QualityEvidence] = []
        seen: set[str] = set()
        for subject in (run_reference, *(f"task:{task_id}" for task_id in task_ids)):
            result = unit_of_work.evidence.quality_for_subject(organization_id, subject)
            if not result.is_success or result.value is None:
                return None
            for record in result.value:
                if record.evidence_id not in seen:
                    seen.add(record.evidence_id)
                    records.append(record)
        return tuple(records)

    def _agent_projection(self, agent: CommonAgentVersion) -> Mapping[str, object]:
        return self._safe(
            {
                "agent_version_id": str(agent.agent_version_id),
                "canonical_identity": agent.canonical_identity,
                "category": agent.category,
                "responsibilities": agent.responsibilities,
                "boundaries": agent.boundaries,
                "escalation_targets": agent.escalation_targets,
                "approval_authority": agent.approval_authority,
                "runtime_policy": agent.runtime_policy,
                "tool_policy": agent.tool_policy,
                "quality_rubric": agent.quality_rubric,
                "critique_relationships": agent.critique_relationships,
                "knowledge_bindings": agent.knowledge_bindings,
                "input_schema": agent.input_schema,
                "output_schema": agent.output_schema,
                "provenance_policy": agent.provenance_policy,
                "content_digest": agent.content_digest,
            }
        )

    def _task_projection(self, task: AgentTask) -> Mapping[str, object]:
        return self._safe(
            {
                "task_id": str(task.task_id),
                "pinned_agent_version_id": str(task.pinned_agent_version_id),
                "dependencies": tuple(str(item) for item in task.dependencies),
                "approval_gate_ids": tuple(str(item) for item in task.approval_gate_ids),
                "checkpoint_reference": task.checkpoint_reference,
                "lifecycle_state": task.state.value,
                "ineligible_for_execution": task.ineligible_for_execution,
                "failure_reason": task.failure_reason,
            }
        )

    def _artifact_projection(self, artifact: ArtifactHandoff) -> Mapping[str, object]:
        return self._safe(
            {
                "handoff_id": str(artifact.handoff_id),
                "artifact_identity": artifact.artifact_identity,
                "artifact_version": artifact.artifact_version,
                "parent_lineage": artifact.parent_lineage,
                "source_task_id": str(artifact.source_task_id),
                "provenance_reference": artifact.provenance_reference,
                "validation_state": (
                    "complete" if self._artifact_complete(artifact) else "incomplete"
                ),
            }
        )

    def _critique_projection(self, critique: CritiqueRecord) -> Mapping[str, object]:
        return self._safe(
            {
                "critique_id": critique.critique_id,
                "source_reference": critique.source_reference,
                "target_task_id": str(critique.target_task_id),
                "relationship_reference": critique.relationship_reference,
                "evidence_reference": critique.evidence_reference,
                "state": "retained",
                "submitted_at": critique.submitted_at.isoformat(),
            }
        )

    def _quality_projection(self, evidence: QualityEvidence) -> Mapping[str, object]:
        return self._safe(
            {
                "evidence_id": evidence.evidence_id,
                "kind": evidence.kind.value,
                "subject_reference": evidence.subject_reference,
                "passed": evidence.passed,
                "evidence_reference": evidence.evidence_reference,
                "recorded_at": evidence.recorded_at.isoformat(),
            }
        )

    def _approval_projection(self, gate: ApprovalGate) -> Mapping[str, object]:
        return self._safe(
            {
                "approval_gate_id": str(gate.approval_gate_id),
                "pending_operation_reference": gate.pending_operation_reference,
                "status": gate.status.value,
                "decision": gate.decision,
                "reviewer_reference": gate.reviewer_reference,
                "decision_reason_retained": gate.decision_reason is not None,
            }
        )

    def _provenance_projection(self, provenance: RunProvenance) -> Mapping[str, object]:
        return self._safe(
            {
                "run_provenance_id": str(provenance.run_provenance_id),
                "graph_revision_id": str(provenance.graph_revision_id),
                "workflow_definition_version": provenance.workflow_definition_version,
                "agent_version_ids": tuple(str(item) for item in provenance.agent_version_ids),
                "pattern_version_ids": tuple(
                    str(item) for item in provenance.pattern_version_ids
                ),
                "source_checkpoint_reference": provenance.source_checkpoint_reference,
                "artifact_version_references": provenance.artifact_version_references,
                "source_run_provenance_id": (
                    str(provenance.source_run_provenance_id)
                    if provenance.source_run_provenance_id is not None
                    else None
                ),
            }
        )

    def _safe(self, values: Mapping[str, object]) -> Mapping[str, object]:
        return self._redactor.redact_mapping(
            values, surface=RedactionSurface.PUBLIC_RESPONSE
        )

    @staticmethod
    def _artifact_complete(artifact: ArtifactHandoff) -> bool:
        return all(
            (
                artifact.parent_lineage,
                artifact.technical_specification,
                artifact.rights_and_consent_state,
                artifact.continuity_state,
                artifact.quality_control_state,
                artifact.target_channels,
                artifact.provenance_reference,
            )
        )

    @staticmethod
    def _metadata(
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        now: datetime,
    ) -> RecordMetadata:
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _validation_error(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _conflict(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.CONFLICT,
            "The idempotency key cannot be reused for a different request.",
            correlation_id,
        )

    @staticmethod
    def _repository_error(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "VA control-plane storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            error.retryable,
            error.fields,
        )

    @staticmethod
    def _unavailable_projection(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "VA run projection is unavailable.",
            correlation_id,
        )
