# ruff: noqa: E501
"""Dependency-injectable composition for the local versioned Host control plane."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import TypeVar

from app.adapters.local import default_local_adapters
from app.audit import AuditWriter
from app.engines.migration import LegacyEngineRetirement
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
)
from app.evaluation.service import EvaluationService
from app.evolution.service import EvolutionService
from app.governance.approvals import (
    ActionPreview,
    ApprovalGate,
    ApprovalSubmissionOutcome,
    GovernanceService,
)
from app.governance.authorization import AuthorizationContext
from app.governance.tool_broker import HostToolBroker, ToolRequest
from app.memory.models import MemoryScope, MemoryScopeType
from app.memory.repository import InMemoryMemoryRepository
from app.memory.retrieval import KnowledgeRetriever, RetrievalConfiguration, RetrievalRequester
from app.models.audit import AuditEvent
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.identifiers import (
    ActorId,
    ApprovalId,
    CorrelationId,
    OrganizationId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord
from app.registry.pack_validator import DomainPackValidator
from app.repositories.approval_repository import InMemoryApprovalRepository
from app.repositories.artifact_repository import InMemoryArtifactRepository
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository
from app.repositories.pack_repository import (
    DomainPackRecord,
    InMemoryPackRepository,
    PackRegistrationStatus,
)
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import DispatchOutcome, RunService
from app.video.release import ReleaseService, RunOutputBlockerProvider
from app.workflows.validator import RegisteredReferences, WorkflowDefinitionValidator

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class StoredDefinition:
    """An immutable organization-scoped workflow definition version."""

    organization_id: OrganizationId
    workflow_id: WorkflowDefinitionId
    version: str
    definition: Mapping[str, object]
    registered_at: datetime


@dataclass(frozen=True, slots=True)
class OperatorEvent:
    """A redaction-safe run event retained for observation endpoints."""

    kind: str
    recorded_at: datetime
    action_preview: ActionPreview | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class PendingApprovalOperation:
    """Host-created pending effect data; no API payload can replace this authority."""

    authorization_context: AuthorizationContext
    tool_request: ToolRequest


class InMemoryApiAuditRepository:
    """Deterministic local audit store used by the default API composition."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        self.events.append(event)
        return Result.success(event)


class ControlPlaneServices:
    """Compose current Host services without accepting client-provided identity."""

    def __init__(
        self,
        run_repository: InMemoryRunRepository | None = None,
        pack_repository: InMemoryPackRepository | None = None,
        approval_repository: InMemoryApprovalRepository | None = None,
        evaluation_repository: InMemoryEvaluationRepository | None = None,
        evolution_repository: InMemoryEvolutionRepository | None = None,
        artifact_repository: InMemoryArtifactRepository | None = None,
        memory_repository: InMemoryMemoryRepository | None = None,
        retrieval_configuration: RetrievalConfiguration | None = None,
        starter: Callable[[RunRecord], None] | None = None,
    ) -> None:
        self.run_repository = run_repository or InMemoryRunRepository()
        self.pack_repository = pack_repository or InMemoryPackRepository()
        self.approval_repository = approval_repository or InMemoryApprovalRepository()
        self.evaluation_repository = evaluation_repository or InMemoryEvaluationRepository()
        self.evolution_repository = evolution_repository or InMemoryEvolutionRepository()
        self.artifact_repository = artifact_repository or InMemoryArtifactRepository()
        self.memory_repository = memory_repository or InMemoryMemoryRepository()
        self.migration_evidence_repository = InMemoryMigrationEvidenceRepository()
        self.migration_evidence_service = MigrationEvidenceService(
            self.migration_evidence_repository
        )
        self.legacy_engine_retirement = LegacyEngineRetirement(self.migration_evidence_service)
        self.knowledge_retriever = KnowledgeRetriever(
            self.memory_repository,
            retrieval_configuration,
        )
        self.evaluation_service = EvaluationService(self.evaluation_repository)
        self.evolution_service = EvolutionService(
            self.evolution_repository, self.evaluation_repository
        )
        self.video_release_service = ReleaseService(
            self.artifact_repository, RunOutputBlockerProvider(self.run_repository.records)
        )
        self._references = RegisteredReferences(
            agent_ids=frozenset(),
            tool_ids=frozenset(adapter.adapter_id for adapter in default_local_adapters()),
            memory_scope_ids=frozenset({"organization", "workflow"}),
            risk_gate_ids=frozenset({"low-risk", "critical"}),
            rollback_plan_ids=frozenset({"compensate.crm"}),
            authorization_ids=frozenset({"approval-1"}),
        )
        self.pack_validator = DomainPackValidator(self.pack_repository)
        broker = HostToolBroker(default_local_adapters(), AuditWriter(InMemoryApiAuditRepository()))
        self.governance = GovernanceService(
            self.run_repository,
            self.approval_repository,
            broker,
        )
        self._starter = starter or (lambda _record: None)
        self._definitions: dict[
            tuple[OrganizationId, WorkflowDefinitionId, str], StoredDefinition
        ] = {}
        self._events: dict[tuple[OrganizationId, RunId], list[OperatorEvent]] = {}
        self._pending_approvals: dict[
            tuple[OrganizationId, ApprovalId], PendingApprovalOperation
        ] = {}

    def register_domain(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        manifest: Mapping[str, object],
    ) -> Result[DomainPackRecord, ErrorDetail]:
        """Register one complete non-active pack outcome within the authenticated tenant."""
        registered = self.pack_validator.register_inline(
            manifest,
            organization_id=organization_id,
            correlation_id=correlation_id,
        )
        if not registered.is_success:
            return Result.failure(self._error(registered.error, correlation_id))
        record = self._value(registered)
        if record.status is PackRegistrationStatus.REGISTERED:
            self._add_registered_agent_references(record, manifest)
        return Result.success(record)

    def register_definition(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        definition: Mapping[str, object],
        registered_at: datetime,
    ) -> Result[StoredDefinition, ErrorDetail]:
        """Validate and retain one immutable version before it can be selected for a run."""
        report = WorkflowDefinitionValidator(self._references).validate(definition)
        if not report.is_valid:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Workflow definition must pass validation before registration.",
                    correlation_id,
                    fields=tuple(ErrorField(issue.field, issue.reason) for issue in report.issues),
                )
            )
        workflow_id = definition.get("id")
        version = definition.get("version")
        engine = definition.get("engine")
        if (
            not isinstance(workflow_id, str)
            or not isinstance(version, str)
            or not isinstance(engine, str)
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED, "Workflow identity is invalid.", correlation_id
                )
            )
        key = (organization_id, WorkflowDefinitionId(workflow_id), version)
        if key in self._definitions:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "Workflow definition version already exists.",
                    correlation_id,
                )
            )
        stored = StoredDefinition(
            organization_id,
            WorkflowDefinitionId(workflow_id),
            version,
            MappingProxyType(dict(definition)),
            registered_at,
        )
        self._definitions[key] = stored
        return Result.success(stored)

    def get_definition(
        self,
        organization_id: OrganizationId,
        workflow_id: WorkflowDefinitionId,
        version: str,
        correlation_id: CorrelationId,
    ) -> Result[StoredDefinition, ErrorDetail]:
        """Return exactly one definition version from the authenticated organization."""
        stored = self._definitions.get((organization_id, workflow_id, version))
        if stored is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.NOT_FOUND, "Workflow definition was not found.", correlation_id
                )
            )
        return Result.success(stored)

    def create_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        workflow_id: WorkflowDefinitionId,
        version: str,
    ) -> Result[RunRecord, ErrorDetail]:
        """Create a queued run only from a prior tenant-scoped registered definition."""
        definition = self.get_definition(organization_id, workflow_id, version, correlation_id)
        if not definition.is_success:
            return Result.failure(self._error(definition.error, correlation_id))
        created = self.run_service.create_queued_run(
            organization_id,
            correlation_id,
            self._value(definition).definition,
        )
        if not created.is_success:
            return Result.failure(self._error(created.error, correlation_id))
        record = self._value(created)
        self._record_event(
            organization_id,
            record.run_id,
            OperatorEvent(
                "action_preview",
                record.metadata.updated_at,
                self._run_preview(record),
            ),
        )
        return Result.success(record)

    def preview_or_dispatch(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        run_id: RunId,
        idempotency_key: str,
        confirm: bool,
    ) -> Result[tuple[RunRecord, ActionPreview, DispatchOutcome | None], ErrorDetail]:
        """Emit a persisted action preview before a confirmed dispatch can invoke the starter."""
        fetched = self.run_repository.get_by_run_id(organization_id, run_id)
        if not fetched.is_success:
            return Result.failure(self._error(fetched.error, correlation_id))
        current = self._value(fetched)
        preview = self._dispatch_preview(current)
        if not confirm:
            return Result.success((current, preview, None))
        self._record_event(
            organization_id,
            run_id,
            OperatorEvent("action_preview", current.metadata.updated_at, preview),
        )
        dispatched = self.run_service.dispatch(
            organization_id,
            run_id,
            idempotency_key,
            self._starter,
            correlation_id,
        )
        if not dispatched.is_success:
            return Result.failure(self._error(dispatched.error, correlation_id))
        outcome = self._value(dispatched)
        self._record_event(
            organization_id,
            run_id,
            OperatorEvent(
                "dispatch", outcome.record.metadata.updated_at, detail=outcome.record.status
            ),
        )
        return Result.success((outcome.record, preview, outcome))

    def get_run(
        self, organization_id: OrganizationId, run_id: RunId, correlation_id: CorrelationId
    ) -> Result[RunRecord, ErrorDetail]:
        """Return a durable run only when it belongs to the authenticated organization."""
        fetched = self.run_repository.get_by_run_id(organization_id, run_id)
        if not fetched.is_success:
            return Result.failure(self._error(fetched.error, correlation_id))
        return Result.success(self._value(fetched))

    def get_events(
        self, organization_id: OrganizationId, run_id: RunId, correlation_id: CorrelationId
    ) -> Result[tuple[OperatorEvent, ...], ErrorDetail]:
        """Require an organization-scoped run lookup before exposing any observation history."""
        run = self.get_run(organization_id, run_id, correlation_id)
        if not run.is_success:
            return Result.failure(self._error(run.error, correlation_id))
        return Result.success(tuple(self._events.get((organization_id, run_id), ())))

    def get_approval(
        self,
        organization_id: OrganizationId,
        approval_id: ApprovalId,
        correlation_id: CorrelationId,
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Expose a redacted approval preview only from its authenticated organization."""
        fetched = self.approval_repository.get_by_approval_id(organization_id, approval_id)
        if not fetched.is_success:
            return Result.failure(self._error(fetched.error, correlation_id))
        return Result.success(self._value(fetched))

    def register_pending_approval(
        self,
        gate: ApprovalGate,
        authorization_context: AuthorizationContext,
        tool_request: ToolRequest,
    ) -> None:
        """Register Host-created pending operation data for a gate; routes cannot create it."""
        if authorization_context.organization_id != gate.metadata.organization_id:
            raise ValueError("Approval authority must belong to the gate organization.")
        self._pending_approvals[(gate.metadata.organization_id, gate.approval_id)] = (
            PendingApprovalOperation(authorization_context, tool_request)
        )

    def submit_approval(
        self,
        organization_id: OrganizationId,
        actor_id: str,
        approval_id: ApprovalId,
        selected_value: str,
        reason: str,
        correlation_id: CorrelationId,
    ) -> Result[ApprovalSubmissionOutcome, ErrorDetail]:
        """Submit a decision with the actor solely from trusted request context."""
        pending = self._pending_approvals.get((organization_id, approval_id))
        if pending is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.NOT_FOUND, "Pending approval operation was not found.", correlation_id
                )
            )
        return self.governance.submit_decision(
            organization_id,
            approval_id,
            ActorId(actor_id),
            selected_value,
            reason,
            pending.authorization_context,
            pending.tool_request,
            correlation_id,
        )

    @property
    def run_service(self) -> RunService:
        """Build validation against the current Host-owned reference registry."""
        return RunService(
            self.run_repository,
            self._references,
            legacy_execution_availability=self.legacy_engine_retirement,
        )

    @staticmethod
    def retrieval_requester(
        organization_id: OrganizationId, actor_id: ActorId
    ) -> RetrievalRequester:
        """Derive the only API-searchable scopes from trusted request identity."""
        return RetrievalRequester(
            organization_id=organization_id,
            approved_scopes=(
                MemoryScope(MemoryScopeType.ORGANIZATION, str(organization_id)),
                MemoryScope(MemoryScopeType.AGENT, str(actor_id)),
            ),
        )

    def _add_registered_agent_references(
        self, record: DomainPackRecord, manifest: Mapping[str, object]
    ) -> None:
        raw_agents = manifest.get("agents")
        if not isinstance(raw_agents, list):
            return
        agent_ids = set(self._references.agent_ids)
        tool_ids = set(self._references.tool_ids)
        for agent_record, raw_agent in zip(record.agents, raw_agents, strict=True):
            if agent_record.agent_id is not None:
                agent_ids.add(agent_record.agent_id)
            if isinstance(raw_agent, Mapping):
                values = raw_agent.get("allowed_tools")
                if isinstance(values, list):
                    tool_ids.update(value for value in values if isinstance(value, str))
        self._references = RegisteredReferences(
            agent_ids=frozenset(agent_ids),
            tool_ids=frozenset(tool_ids),
            memory_scope_ids=self._references.memory_scope_ids,
            risk_gate_ids=self._references.risk_gate_ids,
            rollback_plan_ids=self._references.rollback_plan_ids,
            authorization_ids=self._references.authorization_ids,
        )

    @staticmethod
    def _run_preview(record: RunRecord) -> ActionPreview:
        return ActionPreview(
            action_id=f"queue:{record.run_id}",
            summary="Queue a validated workflow run for operator-controlled dispatch.",
            intended_effect="A durable queued run record will be available for dispatch.",
            supporting_evidence=(record.workflow_definition_digest,),
            confidence=1.0,
            correction_control="Do not confirm dispatch; review the run topology instead.",
        )

    @staticmethod
    def _dispatch_preview(record: RunRecord) -> ActionPreview:
        return ActionPreview(
            action_id=f"dispatch:{record.run_id}",
            summary="Dispatch the queued workflow through its selected in-process engine.",
            intended_effect="The selected engine will claim the queued run; no tool effect is implied.",
            rollback_preview="A later failure transition retains completed effects and stops unstarted work.",
            supporting_evidence=(record.workflow_definition_digest,),
            confidence=1.0,
            correction_control="Leave confirmation false to keep the run queued.",
        )

    def _record_event(
        self, organization_id: OrganizationId, run_id: RunId, event: OperatorEvent
    ) -> None:
        self._events.setdefault((organization_id, run_id), []).append(event)

    @staticmethod
    def _value(result: Result[T, ErrorDetail]) -> T:
        if result.value is None:
            raise RuntimeError("A successful control-plane operation did not return a value.")
        return result.value

    @staticmethod
    def _error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Control-plane storage is unavailable.",
                correlation_id,
            )
        return ErrorDetail(error.code, error.message, correlation_id, error.retryable, error.fields)


_DEFAULT_CONTROL_PLANE_SERVICES = ControlPlaneServices()


def get_control_plane_services() -> ControlPlaneServices:
    """Return the local Host composition; tests may override this dependency."""
    return _DEFAULT_CONTROL_PLANE_SERVICES
