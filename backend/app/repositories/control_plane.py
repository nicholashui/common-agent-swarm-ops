"""Transactional control-plane repository ports and deterministic in-memory fakes."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from types import TracebackType
from typing import Literal, Protocol, runtime_checkable

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuditRecord,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    CritiqueRecord,
    DeploymentConfiguration,
    EventId,
    EventReplayWindow,
    IdempotencyRecord,
    IdempotencyStatus,
    ImportId,
    ImportRecord,
    ImportScanState,
    ImprovementProposal,
    OperationalEvent,
    OutboxId,
    OutboxRecord,
    ProposalId,
    QualityEvidence,
    ReplayRecoveryOutcome,
    RolloutCampaign,
    RolloutCampaignId,
    RunProvenance,
    RunProvenanceId,
    SecurityEvidence,
    TaskId,
    TaskTransition,
    VulnerabilityMigration,
    VulnerabilityMigrationId,
    WorkItem,
    WorkItemId,
    WorkTransition,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId


def _error(code: ErrorCode, message: str) -> ErrorDetail:
    return ErrorDetail(code, message, CorrelationId("control-plane-repository"))


class _StoredRecord(Protocol):
    @property
    def metadata(self) -> RecordMetadata: ...


@runtime_checkable
class CommonContractRepository(Protocol):
    """Organization-scoped immutable common-contract persistence."""

    def append_agent_version(
        self, record: CommonAgentVersion
    ) -> Result[CommonAgentVersion, RepositoryError]: ...

    def get_agent_version(
        self, organization_id: OrganizationId, agent_version_id: AgentVersionId
    ) -> Result[CommonAgentVersion, RepositoryError]: ...

    def append_pattern_version(
        self, record: CommonPatternVersion
    ) -> Result[CommonPatternVersion, RepositoryError]: ...

    def get_pattern_version(
        self, organization_id: OrganizationId, pattern_version_id: CommonPatternVersionId
    ) -> Result[CommonPatternVersion, RepositoryError]: ...

    def replace_agent_draft(
        self, record: CommonAgentVersion
    ) -> Result[CommonAgentVersion, RepositoryError]: ...

    def replace_pattern_draft(
        self, record: CommonPatternVersion
    ) -> Result[CommonPatternVersion, RepositoryError]: ...

    def append_vulnerability_migration(
        self, record: VulnerabilityMigration
    ) -> Result[VulnerabilityMigration, RepositoryError]: ...

    def get_vulnerability_migration(
        self, organization_id: OrganizationId, migration_id: VulnerabilityMigrationId
    ) -> Result[VulnerabilityMigration, RepositoryError]: ...


@runtime_checkable
class ProvenanceRepository(Protocol):
    """Append-only run provenance snapshots."""

    def append(self, record: RunProvenance) -> Result[RunProvenance, RepositoryError]: ...

    def get(
        self, organization_id: OrganizationId, provenance_id: RunProvenanceId
    ) -> Result[RunProvenance, RepositoryError]: ...


@runtime_checkable
class WorkRepository(Protocol):
    """Work records with organization-scoped reads and append-only transitions."""

    def create(self, record: WorkItem) -> Result[WorkItem, RepositoryError]: ...

    def replace(
        self, record: WorkItem, expected_work_version: int
    ) -> Result[WorkItem, RepositoryError]: ...

    def get(
        self, organization_id: OrganizationId, work_item_id: WorkItemId
    ) -> Result[WorkItem, RepositoryError]: ...

    def append_transition(
        self, transition: WorkTransition
    ) -> Result[WorkTransition, RepositoryError]: ...

    def transitions(
        self, organization_id: OrganizationId, work_item_id: WorkItemId
    ) -> Result[tuple[WorkTransition, ...], RepositoryError]: ...


@runtime_checkable
class TaskRepository(Protocol):
    """Task records with organization-scoped reads and append-only transitions."""

    def create(self, record: AgentTask) -> Result[AgentTask, RepositoryError]: ...

    def replace(
        self, record: AgentTask, expected_task_version: int
    ) -> Result[AgentTask, RepositoryError]: ...

    def get(
        self, organization_id: OrganizationId, task_id: TaskId
    ) -> Result[AgentTask, RepositoryError]: ...

    def append_transition(
        self, transition: TaskTransition
    ) -> Result[TaskTransition, RepositoryError]: ...

    def transitions(
        self, organization_id: OrganizationId, task_id: TaskId
    ) -> Result[tuple[TaskTransition, ...], RepositoryError]: ...

    def for_run(
        self, organization_id: OrganizationId, run_reference: str
    ) -> Result[tuple[AgentTask, ...], RepositoryError]: ...


@runtime_checkable
class ArtifactHandoffRepository(Protocol):
    """Organization-scoped opaque artifact handoffs."""

    def append(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, RepositoryError]: ...

    def get(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, RepositoryError]: ...

    def for_run(
        self, organization_id: OrganizationId, run_reference: str
    ) -> Result[tuple[ArtifactHandoff, ...], RepositoryError]: ...


@runtime_checkable
class EvidenceRepository(Protocol):
    """Independent directed critique, quality, approval, proposal, and rollout records."""

    def append_critique(
        self, record: CritiqueRecord
    ) -> Result[CritiqueRecord, RepositoryError]: ...

    def critiques_for_tasks(
        self, organization_id: OrganizationId, task_ids: tuple[TaskId, ...]
    ) -> Result[tuple[CritiqueRecord, ...], RepositoryError]: ...

    def append_quality(
        self, record: QualityEvidence
    ) -> Result[QualityEvidence, RepositoryError]: ...

    def quality_for_subject(
        self, organization_id: OrganizationId, subject_reference: str
    ) -> Result[tuple[QualityEvidence, ...], RepositoryError]: ...

    def append_approval(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]: ...

    def get_approval(
        self, organization_id: OrganizationId, approval_gate_id: ApprovalGateId
    ) -> Result[ApprovalGate, RepositoryError]: ...

    def replace_approval(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]: ...

    def append_proposal(
        self, record: ImprovementProposal
    ) -> Result[ImprovementProposal, RepositoryError]: ...

    def get_proposal(
        self, organization_id: OrganizationId, proposal_id: ProposalId
    ) -> Result[ImprovementProposal, RepositoryError]: ...

    def get_quality(
        self, organization_id: OrganizationId, evidence_id: str
    ) -> Result[QualityEvidence, RepositoryError]: ...

    def append_rollout(
        self, record: RolloutCampaign
    ) -> Result[RolloutCampaign, RepositoryError]: ...

    def get_rollout(
        self, organization_id: OrganizationId, campaign_id: RolloutCampaignId
    ) -> Result[RolloutCampaign, RepositoryError]: ...

    def replace_rollout(
        self, record: RolloutCampaign, expected_version: int
    ) -> Result[RolloutCampaign, RepositoryError]: ...


@runtime_checkable
class EventOutboxRepository(Protocol):
    """Audit, event, delivery, and replay-recovery records retained at one durable boundary."""

    def append_audit(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]: ...

    def append_event(
        self, record: OperationalEvent
    ) -> Result[OperationalEvent, RepositoryError]: ...

    def append_outbox(self, record: OutboxRecord) -> Result[OutboxRecord, RepositoryError]: ...

    def get_event(
        self, organization_id: OrganizationId, event_id: EventId
    ) -> Result[OperationalEvent, RepositoryError]: ...

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, RepositoryError]: ...

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, RepositoryError]: ...


@runtime_checkable
class ImportRepository(Protocol):
    """Organization-scoped accepted import and redacted security evidence storage."""

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]: ...

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]: ...

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, RepositoryError]: ...

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, RepositoryError]: ...


@runtime_checkable
class IdempotencyRepository(Protocol):
    """Atomically reserve actor/key pairs and retain completed command responses."""

    def reserve(self, record: IdempotencyRecord) -> Result[IdempotencyRecord, RepositoryError]: ...

    def get(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        idempotency_key: str,
    ) -> Result[IdempotencyRecord, RepositoryError]: ...

    def complete(self, record: IdempotencyRecord) -> Result[IdempotencyRecord, RepositoryError]: ...


@runtime_checkable
class DeploymentConfigurationRepository(Protocol):
    """Validated configuration storage accessible only within trusted application wiring."""

    def save(
        self, record: DeploymentConfiguration
    ) -> Result[DeploymentConfiguration, RepositoryError]: ...

    def current(self) -> Result[DeploymentConfiguration, RepositoryError]: ...


@runtime_checkable
class ControlPlaneUnitOfWork(Protocol):
    """Transactional composition root for every control-plane mutation."""

    @property
    def common_contracts(self) -> CommonContractRepository: ...

    @property
    def provenance(self) -> ProvenanceRepository: ...

    @property
    def work_items(self) -> WorkRepository: ...

    @property
    def tasks(self) -> TaskRepository: ...

    @property
    def artifacts(self) -> ArtifactHandoffRepository: ...

    @property
    def evidence(self) -> EvidenceRepository: ...

    @property
    def events(self) -> EventOutboxRepository: ...

    @property
    def imports(self) -> ImportRepository: ...

    @property
    def idempotency(self) -> IdempotencyRepository: ...

    @property
    def deployment(self) -> DeploymentConfigurationRepository: ...

    def __enter__(self) -> ControlPlaneUnitOfWork: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


@dataclass(slots=True)
class _State:
    agent_versions: dict[AgentVersionId, CommonAgentVersion] = field(default_factory=dict)
    pattern_versions: dict[CommonPatternVersionId, CommonPatternVersion] = field(
        default_factory=dict
    )
    vulnerability_migrations: dict[VulnerabilityMigrationId, VulnerabilityMigration] = field(
        default_factory=dict
    )
    provenance: dict[RunProvenanceId, RunProvenance] = field(default_factory=dict)
    work_items: dict[WorkItemId, WorkItem] = field(default_factory=dict)
    work_transitions: dict[WorkItemId, tuple[WorkTransition, ...]] = field(default_factory=dict)
    tasks: dict[TaskId, AgentTask] = field(default_factory=dict)
    task_transitions: dict[TaskId, tuple[TaskTransition, ...]] = field(default_factory=dict)
    artifacts: dict[ArtifactHandoffId, ArtifactHandoff] = field(default_factory=dict)
    critiques: dict[str, CritiqueRecord] = field(default_factory=dict)
    quality_evidence: dict[str, QualityEvidence] = field(default_factory=dict)
    approvals: dict[ApprovalGateId, ApprovalGate] = field(default_factory=dict)
    proposals: dict[ProposalId, ImprovementProposal] = field(default_factory=dict)
    rollouts: dict[RolloutCampaignId, RolloutCampaign] = field(default_factory=dict)
    audits: dict[str, AuditRecord] = field(default_factory=dict)
    events: dict[EventId, OperationalEvent] = field(default_factory=dict)
    event_sequences: dict[int, EventId] = field(default_factory=dict)
    outbox: dict[OutboxId, OutboxRecord] = field(default_factory=dict)
    replay_recoveries: dict[RecordId, ReplayRecoveryOutcome] = field(default_factory=dict)
    imports: dict[ImportId, ImportRecord] = field(default_factory=dict)
    security_evidence: dict[str, SecurityEvidence] = field(default_factory=dict)
    idempotency_records: dict[tuple[ActorId, str], IdempotencyRecord] = field(default_factory=dict)
    deployment: DeploymentConfiguration | None = None

    def clone(self) -> _State:
        return _State(
            agent_versions=dict(self.agent_versions),
            pattern_versions=dict(self.pattern_versions),
            vulnerability_migrations=dict(self.vulnerability_migrations),
            provenance=dict(self.provenance),
            work_items=dict(self.work_items),
            work_transitions=dict(self.work_transitions),
            tasks=dict(self.tasks),
            task_transitions=dict(self.task_transitions),
            artifacts=dict(self.artifacts),
            critiques=dict(self.critiques),
            quality_evidence=dict(self.quality_evidence),
            approvals=dict(self.approvals),
            proposals=dict(self.proposals),
            rollouts=dict(self.rollouts),
            audits=dict(self.audits),
            events=dict(self.events),
            event_sequences=dict(self.event_sequences),
            outbox=dict(self.outbox),
            replay_recoveries=dict(self.replay_recoveries),
            imports=dict(self.imports),
            security_evidence=dict(self.security_evidence),
            idempotency_records=dict(self.idempotency_records),
            deployment=self.deployment,
        )


class InMemoryControlPlaneDatabase:
    """Shared deterministic state used only by transaction-scoped in-memory fakes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._state = _State()

    def unit_of_work(self) -> InMemoryControlPlaneUnitOfWork:
        """Create a fresh transaction view over this deterministic local database."""
        return InMemoryControlPlaneUnitOfWork(self)


class _RepositoryBase:
    def __init__(self, unit_of_work: InMemoryControlPlaneUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def _state(self) -> _State:
        return self._unit_of_work._active_state()

    @staticmethod
    def _missing(label: str) -> ErrorDetail:
        return _error(ErrorCode.NOT_FOUND, f"{label} was not found.")

    @classmethod
    def _scoped[T: _StoredRecord](
        cls, organization_id: OrganizationId, record: T | None, label: str
    ) -> Result[T, RepositoryError]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(cls._missing(label))
        return Result.success(record)


class InMemoryCommonContractRepository(_RepositoryBase):
    """Append-only common contract fake; records are immutable after insertion."""

    def append_agent_version(
        self, record: CommonAgentVersion
    ) -> Result[CommonAgentVersion, RepositoryError]:
        state = self._state()
        if record.agent_version_id in state.agent_versions:
            return Result.failure(_error(ErrorCode.CONFLICT, "Agent version already exists."))
        state.agent_versions[record.agent_version_id] = record
        return Result.success(record)

    def get_agent_version(
        self, organization_id: OrganizationId, agent_version_id: AgentVersionId
    ) -> Result[CommonAgentVersion, RepositoryError]:
        return self._scoped(
            organization_id, self._state().agent_versions.get(agent_version_id), "Agent version"
        )

    def append_pattern_version(
        self, record: CommonPatternVersion
    ) -> Result[CommonPatternVersion, RepositoryError]:
        state = self._state()
        if record.pattern_version_id in state.pattern_versions:
            return Result.failure(_error(ErrorCode.CONFLICT, "Pattern version already exists."))
        state.pattern_versions[record.pattern_version_id] = record
        return Result.success(record)

    def get_pattern_version(
        self, organization_id: OrganizationId, pattern_version_id: CommonPatternVersionId
    ) -> Result[CommonPatternVersion, RepositoryError]:
        return self._scoped(
            organization_id,
            self._state().pattern_versions.get(pattern_version_id),
            "Pattern version",
        )

    def replace_agent_draft(
        self, record: CommonAgentVersion
    ) -> Result[CommonAgentVersion, RepositoryError]:
        state = self._state()
        existing = state.agent_versions.get(record.agent_version_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Agent version"))
        if existing.status is not ContractStatus.DRAFT or record.status is not ContractStatus.DRAFT:
            return Result.failure(
                _error(ErrorCode.INVALID_TRANSITION, "Published agent versions are immutable.")
            )
        if existing.metadata.record_id != record.metadata.record_id:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Draft agent record identity cannot change.")
            )
        state.agent_versions[record.agent_version_id] = record
        return Result.success(record)

    def replace_pattern_draft(
        self, record: CommonPatternVersion
    ) -> Result[CommonPatternVersion, RepositoryError]:
        state = self._state()
        existing = state.pattern_versions.get(record.pattern_version_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Pattern version"))
        if existing.status is not ContractStatus.DRAFT or record.status is not ContractStatus.DRAFT:
            return Result.failure(
                _error(ErrorCode.INVALID_TRANSITION, "Published pattern versions are immutable.")
            )
        if existing.metadata.record_id != record.metadata.record_id:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Draft pattern record identity cannot change.")
            )
        state.pattern_versions[record.pattern_version_id] = record
        return Result.success(record)

    def append_vulnerability_migration(
        self, record: VulnerabilityMigration
    ) -> Result[VulnerabilityMigration, RepositoryError]:
        state = self._state()
        if record.migration_id in state.vulnerability_migrations:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Vulnerability migration already exists.")
            )
        state.vulnerability_migrations[record.migration_id] = record
        return Result.success(record)

    def get_vulnerability_migration(
        self, organization_id: OrganizationId, migration_id: VulnerabilityMigrationId
    ) -> Result[VulnerabilityMigration, RepositoryError]:
        return self._scoped(
            organization_id,
            self._state().vulnerability_migrations.get(migration_id),
            "Vulnerability migration",
        )


class InMemoryProvenanceRepository(_RepositoryBase):
    """Append-only immutable run provenance fake."""

    def append(self, record: RunProvenance) -> Result[RunProvenance, RepositoryError]:
        state = self._state()
        if record.run_provenance_id in state.provenance:
            return Result.failure(_error(ErrorCode.CONFLICT, "Run provenance already exists."))
        state.provenance[record.run_provenance_id] = record
        return Result.success(record)

    def get(
        self, organization_id: OrganizationId, provenance_id: RunProvenanceId
    ) -> Result[RunProvenance, RepositoryError]:
        return self._scoped(
            organization_id, self._state().provenance.get(provenance_id), "Run provenance"
        )


class InMemoryWorkRepository(_RepositoryBase):
    """Organization-scoped work fake with transition history that can only grow."""

    def create(self, record: WorkItem) -> Result[WorkItem, RepositoryError]:
        state = self._state()
        if record.work_item_id in state.work_items:
            return Result.failure(_error(ErrorCode.CONFLICT, "Work item already exists."))
        state.work_items[record.work_item_id] = record
        return Result.success(record)

    def replace(
        self, record: WorkItem, expected_work_version: int
    ) -> Result[WorkItem, RepositoryError]:
        state = self._state()
        existing = state.work_items.get(record.work_item_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Work item"))
        if (
            existing.metadata.record_id != record.metadata.record_id
            or existing.metadata.version != expected_work_version
            or record.metadata.version != expected_work_version + 1
            or existing.subject_reference != record.subject_reference
            or existing.idempotency_key != record.idempotency_key
        ):
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Work item changed before it could be updated.")
            )
        state.work_items[record.work_item_id] = record
        return Result.success(record)

    def get(
        self, organization_id: OrganizationId, work_item_id: WorkItemId
    ) -> Result[WorkItem, RepositoryError]:
        return self._scoped(
            organization_id, self._state().work_items.get(work_item_id), "Work item"
        )

    def append_transition(
        self, transition: WorkTransition
    ) -> Result[WorkTransition, RepositoryError]:
        state = self._state()
        work_item = state.work_items.get(transition.work_item_id)
        if (
            work_item is None
            or work_item.metadata.organization_id != transition.metadata.organization_id
        ):
            return Result.failure(self._missing("Work item"))
        history = state.work_transitions.get(transition.work_item_id, ())
        if any(item.transition_id == transition.transition_id for item in history):
            return Result.failure(_error(ErrorCode.CONFLICT, "Work transition already exists."))
        state.work_transitions[transition.work_item_id] = (*history, transition)
        return Result.success(transition)

    def transitions(
        self, organization_id: OrganizationId, work_item_id: WorkItemId
    ) -> Result[tuple[WorkTransition, ...], RepositoryError]:
        work_item = self.get(organization_id, work_item_id)
        if not work_item.is_success:
            return Result.failure(work_item.error or self._missing("Work item"))
        return Result.success(self._state().work_transitions.get(work_item_id, ()))


class InMemoryTaskRepository(_RepositoryBase):
    """Organization-scoped task fake with append-only transition history."""

    def create(self, record: AgentTask) -> Result[AgentTask, RepositoryError]:
        state = self._state()
        if record.task_id in state.tasks:
            return Result.failure(_error(ErrorCode.CONFLICT, "Task already exists."))
        state.tasks[record.task_id] = record
        return Result.success(record)

    def replace(
        self, record: AgentTask, expected_task_version: int
    ) -> Result[AgentTask, RepositoryError]:
        state = self._state()
        existing = state.tasks.get(record.task_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Task"))
        if (
            existing.metadata.record_id != record.metadata.record_id
            or existing.metadata.version != expected_task_version
            or record.metadata.version != expected_task_version + 1
        ):
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Task changed before it could be updated.")
            )
        state.tasks[record.task_id] = record
        return Result.success(record)

    def get(
        self, organization_id: OrganizationId, task_id: TaskId
    ) -> Result[AgentTask, RepositoryError]:
        return self._scoped(organization_id, self._state().tasks.get(task_id), "Task")

    def append_transition(
        self, transition: TaskTransition
    ) -> Result[TaskTransition, RepositoryError]:
        state = self._state()
        task = state.tasks.get(transition.task_id)
        if task is None or task.metadata.organization_id != transition.metadata.organization_id:
            return Result.failure(self._missing("Task"))
        history = state.task_transitions.get(transition.task_id, ())
        if any(item.transition_id == transition.transition_id for item in history):
            return Result.failure(_error(ErrorCode.CONFLICT, "Task transition already exists."))
        state.task_transitions[transition.task_id] = (*history, transition)
        return Result.success(transition)

    def transitions(
        self, organization_id: OrganizationId, task_id: TaskId
    ) -> Result[tuple[TaskTransition, ...], RepositoryError]:
        task = self.get(organization_id, task_id)
        if not task.is_success:
            return Result.failure(task.error or self._missing("Task"))
        return Result.success(self._state().task_transitions.get(task_id, ()))

    def for_run(
        self, organization_id: OrganizationId, run_reference: str
    ) -> Result[tuple[AgentTask, ...], RepositoryError]:
        """Return the organization-scoped tasks that share one durable run reference."""
        return Result.success(
            tuple(
                task
                for task in self._state().tasks.values()
                if task.metadata.organization_id == organization_id
                and task.run_reference == run_reference
            )
        )


class InMemoryArtifactHandoffRepository(_RepositoryBase):
    """Opaque handoff fake that permits only organization-scoped retrieval."""

    def append(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, RepositoryError]:
        state = self._state()
        if record.handoff_id in state.artifacts:
            return Result.failure(_error(ErrorCode.CONFLICT, "Artifact handoff already exists."))
        state.artifacts[record.handoff_id] = record
        return Result.success(record)

    def get(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, RepositoryError]:
        return self._scoped(
            organization_id, self._state().artifacts.get(handoff_id), "Artifact handoff"
        )

    def for_run(
        self, organization_id: OrganizationId, run_reference: str
    ) -> Result[tuple[ArtifactHandoff, ...], RepositoryError]:
        """Return only opaque handoffs linked to one organization-scoped run."""
        return Result.success(
            tuple(
                record
                for record in self._state().artifacts.values()
                if record.metadata.organization_id == organization_id
                and record.source_run_reference == run_reference
            )
        )


class InMemoryEvidenceRepository(_RepositoryBase):
    """Append-only independent evidence fake; no aggregate evidence is synthesized."""

    def append_critique(self, record: CritiqueRecord) -> Result[CritiqueRecord, RepositoryError]:
        state = self._state()
        if record.critique_id in state.critiques:
            return Result.failure(_error(ErrorCode.CONFLICT, "Critique already exists."))
        state.critiques[record.critique_id] = record
        return Result.success(record)

    def critiques_for_tasks(
        self, organization_id: OrganizationId, task_ids: tuple[TaskId, ...]
    ) -> Result[tuple[CritiqueRecord, ...], RepositoryError]:
        """Return directed critique evidence for the supplied organization-scoped tasks."""
        selected_ids = frozenset(task_ids)
        return Result.success(
            tuple(
                record
                for record in self._state().critiques.values()
                if record.metadata.organization_id == organization_id
                and record.target_task_id in selected_ids
            )
        )

    def append_quality(self, record: QualityEvidence) -> Result[QualityEvidence, RepositoryError]:
        state = self._state()
        if record.evidence_id in state.quality_evidence:
            return Result.failure(_error(ErrorCode.CONFLICT, "Quality evidence already exists."))
        state.quality_evidence[record.evidence_id] = record
        return Result.success(record)

    def quality_for_subject(
        self, organization_id: OrganizationId, subject_reference: str
    ) -> Result[tuple[QualityEvidence, ...], RepositoryError]:
        records = tuple(
            record
            for record in self._state().quality_evidence.values()
            if record.metadata.organization_id == organization_id
            and record.subject_reference == subject_reference
        )
        return Result.success(records)

    def append_approval(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]:
        state = self._state()
        if record.approval_gate_id in state.approvals:
            return Result.failure(_error(ErrorCode.CONFLICT, "Approval gate already exists."))
        state.approvals[record.approval_gate_id] = record
        return Result.success(record)

    def get_approval(
        self, organization_id: OrganizationId, approval_gate_id: ApprovalGateId
    ) -> Result[ApprovalGate, RepositoryError]:
        return self._scoped(
            organization_id, self._state().approvals.get(approval_gate_id), "Approval gate"
        )

    def replace_approval(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]:
        state = self._state()
        existing = state.approvals.get(record.approval_gate_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Approval gate"))
        if (
            existing.metadata.record_id != record.metadata.record_id
            or record.metadata.version != existing.metadata.version + 1
        ):
            return Result.failure(_error(ErrorCode.CONFLICT, "Approval gate version conflicts."))
        state.approvals[record.approval_gate_id] = record
        return Result.success(record)

    def append_proposal(
        self, record: ImprovementProposal
    ) -> Result[ImprovementProposal, RepositoryError]:
        state = self._state()
        if record.proposal_id in state.proposals:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Improvement proposal already exists.")
            )
        state.proposals[record.proposal_id] = record
        return Result.success(record)

    def get_proposal(
        self, organization_id: OrganizationId, proposal_id: ProposalId
    ) -> Result[ImprovementProposal, RepositoryError]:
        return self._scoped(
            organization_id, self._state().proposals.get(proposal_id), "Improvement proposal"
        )

    def get_quality(
        self, organization_id: OrganizationId, evidence_id: str
    ) -> Result[QualityEvidence, RepositoryError]:
        return self._scoped(
            organization_id, self._state().quality_evidence.get(evidence_id), "Quality evidence"
        )

    def append_rollout(self, record: RolloutCampaign) -> Result[RolloutCampaign, RepositoryError]:
        state = self._state()
        if record.campaign_id in state.rollouts:
            return Result.failure(_error(ErrorCode.CONFLICT, "Rollout campaign already exists."))
        state.rollouts[record.campaign_id] = record
        return Result.success(record)

    def get_rollout(
        self, organization_id: OrganizationId, campaign_id: RolloutCampaignId
    ) -> Result[RolloutCampaign, RepositoryError]:
        return self._scoped(
            organization_id, self._state().rollouts.get(campaign_id), "Rollout campaign"
        )

    def replace_rollout(
        self, record: RolloutCampaign, expected_version: int
    ) -> Result[RolloutCampaign, RepositoryError]:
        state = self._state()
        existing = state.rollouts.get(record.campaign_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Rollout campaign"))
        if (
            existing.metadata.record_id != record.metadata.record_id
            or existing.metadata.version != expected_version
            or record.metadata.version != existing.metadata.version + 1
        ):
            return Result.failure(_error(ErrorCode.CONFLICT, "Rollout campaign version conflicts."))
        state.rollouts[record.campaign_id] = record
        return Result.success(record)


class InMemoryEventOutboxRepository(_RepositoryBase):
    """Append-only audit/event/outbox fake with unique event sequence enforcement."""

    def append_audit(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]:
        state = self._state()
        if record.audit_id in state.audits:
            return Result.failure(_error(ErrorCode.CONFLICT, "Audit record already exists."))
        state.audits[record.audit_id] = record
        return Result.success(record)

    def append_event(self, record: OperationalEvent) -> Result[OperationalEvent, RepositoryError]:
        state = self._state()
        if record.event_id in state.events or record.sequence in state.event_sequences:
            return Result.failure(_error(ErrorCode.CONFLICT, "Operational event already exists."))
        state.events[record.event_id] = record
        state.event_sequences[record.sequence] = record.event_id
        return Result.success(record)

    def append_outbox(self, record: OutboxRecord) -> Result[OutboxRecord, RepositoryError]:
        state = self._state()
        if record.outbox_id in state.outbox or record.event_id not in state.events:
            return Result.failure(_error(ErrorCode.CONFLICT, "Outbox record cannot be appended."))
        event = state.events[record.event_id]
        if event.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Outbox record organization conflicts.")
            )
        state.outbox[record.outbox_id] = record
        return Result.success(record)

    def get_event(
        self, organization_id: OrganizationId, event_id: EventId
    ) -> Result[OperationalEvent, RepositoryError]:
        return self._scoped(
            organization_id, self._state().events.get(event_id), "Operational event"
        )

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, RepositoryError]:
        if not topic.strip() or after_sequence < 0 or maximum_events < 1:
            return Result.failure(
                _error(ErrorCode.VALIDATION_FAILED, "Invalid event replay request.")
            )
        retained = tuple(
            sorted(
                (
                    event
                    for event in self._state().events.values()
                    if event.metadata.organization_id == organization_id and event.topic == topic
                ),
                key=lambda event: event.sequence,
            )
        )
        high_watermark = retained[-1].sequence if retained else 0
        return Result.success(
            EventReplayWindow(
                events=tuple(event for event in retained if event.sequence > after_sequence)[
                    :maximum_events
                ],
                high_watermark=high_watermark,
            )
        )

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, RepositoryError]:
        state = self._state()
        record_id = record.metadata.record_id
        if record_id in state.replay_recoveries:
            return Result.failure(_error(ErrorCode.CONFLICT, "Replay recovery already exists."))
        state.replay_recoveries[record_id] = record
        return Result.success(record)


class InMemoryImportRepository(_RepositoryBase):
    """Organization-scoped import fake retaining security evidence append-only."""

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        state = self._state()
        if record.import_id in state.imports:
            return Result.failure(_error(ErrorCode.CONFLICT, "Import record already exists."))
        state.imports[record.import_id] = record
        return Result.success(record)

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        state = self._state()
        existing = state.imports.get(record.import_id)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Import record"))
        if existing.scan_state is not ImportScanState.QUARANTINED:
            return Result.failure(
                _error(ErrorCode.INVALID_TRANSITION, "Import is not quarantined.")
            )
        if record.scan_state not in {ImportScanState.ALLOWED, ImportScanState.REJECTED}:
            return Result.failure(
                _error(ErrorCode.INVALID_TRANSITION, "Invalid import scan transition.")
            )
        if record.metadata != existing.metadata or record.checksum != existing.checksum:
            return Result.failure(_error(ErrorCode.CONFLICT, "Import record cannot be changed."))
        state.imports[record.import_id] = record
        return Result.success(record)

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, RepositoryError]:
        return self._scoped(organization_id, self._state().imports.get(import_id), "Import record")

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, RepositoryError]:
        state = self._state()
        if record.security_evidence_id in state.security_evidence:
            return Result.failure(_error(ErrorCode.CONFLICT, "Security evidence already exists."))
        if record.import_id is not None:
            imported = state.imports.get(record.import_id)
            if (
                imported is None
                or imported.metadata.organization_id != record.metadata.organization_id
            ):
                return Result.failure(self._missing("Import record"))
        state.security_evidence[record.security_evidence_id] = record
        return Result.success(record)


class InMemoryIdempotencyRepository(_RepositoryBase):
    """Lock-scoped idempotency fake keyed by actor and request key."""

    @staticmethod
    def _key(actor_id: ActorId, idempotency_key: str) -> tuple[ActorId, str]:
        return actor_id, idempotency_key

    def reserve(self, record: IdempotencyRecord) -> Result[IdempotencyRecord, RepositoryError]:
        state = self._state()
        key = self._key(record.actor_id, record.idempotency_key)
        if key in state.idempotency_records:
            return Result.failure(_error(ErrorCode.CONFLICT, "Idempotency key already exists."))
        state.idempotency_records[key] = record
        return Result.success(record)

    def get(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        idempotency_key: str,
    ) -> Result[IdempotencyRecord, RepositoryError]:
        record = self._state().idempotency_records.get(self._key(actor_id, idempotency_key))
        return self._scoped(organization_id, record, "Idempotency record")

    def complete(self, record: IdempotencyRecord) -> Result[IdempotencyRecord, RepositoryError]:
        state = self._state()
        key = self._key(record.actor_id, record.idempotency_key)
        existing = state.idempotency_records.get(key)
        if existing is None or existing.metadata.organization_id != record.metadata.organization_id:
            return Result.failure(self._missing("Idempotency record"))
        if existing.status is IdempotencyStatus.COMPLETED:
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Idempotency response already exists.")
            )
        if existing.request_digest != record.request_digest:
            return Result.failure(_error(ErrorCode.CONFLICT, "Idempotency digest cannot change."))
        state.idempotency_records[key] = record
        return Result.success(record)


class InMemoryDeploymentConfigurationRepository(_RepositoryBase):
    """Trusted-wiring configuration fake; only one validated current configuration is retained."""

    def save(
        self, record: DeploymentConfiguration
    ) -> Result[DeploymentConfiguration, RepositoryError]:
        state = self._state()
        if (
            state.deployment is not None
            and state.deployment.configuration_id != record.configuration_id
        ):
            return Result.failure(
                _error(ErrorCode.CONFLICT, "Deployment configuration already exists.")
            )
        state.deployment = record
        return Result.success(record)

    def current(self) -> Result[DeploymentConfiguration, RepositoryError]:
        record = self._state().deployment
        if record is None:
            return Result.failure(self._missing("Deployment configuration"))
        return Result.success(record)


class InMemoryControlPlaneUnitOfWork:
    """Lock-backed transaction fake that commits all repository changes atomically."""

    def __init__(self, database: InMemoryControlPlaneDatabase) -> None:
        self._database = database
        self._working_state: _State | None = None
        self._active = False
        self.common_contracts = InMemoryCommonContractRepository(self)
        self.provenance = InMemoryProvenanceRepository(self)
        self.work_items = InMemoryWorkRepository(self)
        self.tasks = InMemoryTaskRepository(self)
        self.artifacts = InMemoryArtifactHandoffRepository(self)
        self.evidence = InMemoryEvidenceRepository(self)
        self.events = InMemoryEventOutboxRepository(self)
        self.imports = InMemoryImportRepository(self)
        self.idempotency = InMemoryIdempotencyRepository(self)
        self.deployment = InMemoryDeploymentConfigurationRepository(self)

    def __enter__(self) -> InMemoryControlPlaneUnitOfWork:
        if self._active:
            raise RuntimeError("A unit of work cannot be entered twice.")
        self._database._lock.acquire()
        self._working_state = self._database._state.clone()
        self._active = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if not self._active:
            return False
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False

    def commit(self) -> None:
        state = self._active_state()
        self._database._state = state
        self._close()

    def rollback(self) -> None:
        self._active_state()
        self._close()

    def _active_state(self) -> _State:
        if not self._active or self._working_state is None:
            raise RuntimeError("Repository operations require an active unit of work.")
        return self._working_state

    def _close(self) -> None:
        self._working_state = None
        self._active = False
        self._database._lock.release()
