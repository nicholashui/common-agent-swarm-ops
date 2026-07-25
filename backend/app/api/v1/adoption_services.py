"""Dependency-injectable composition for the adoption control-plane routes."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace as dc_replace
from threading import RLock
from typing import TypeVar

from app.artifacts.handoff_service import ArtifactHandoffService
from app.evaluation.verification_suite import VerificationSuite
from app.governance.adapter_execution import (
    ProviderAdapterDeclaration,
    ProviderAuthorizationDecision,
    authorize_provider_adapter,
)
from app.governance.authorization import (
    ApprovalState,
    AuthorizationContext,
    AuthorizationService as GovernanceAuthorizationService,
    DataAccessRequest,
)
from app.governance.operational_containment import OperationalContainmentService
from app.memory.learning_lifecycle import LearningLifecycleService
from app.memory.lesson_service import LessonService
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata, utc_now
from app.models.contracts import (
    ErrorCode,
    ErrorDetail,
    Result,
)
from app.models.control_plane import (
    AgentNodeAttemptId,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuditRecord,
    AuthorizationDecision as AuthorizationDecisionRecord,
    AuthorizationDecisionId,
    AuthorizationOutcome,
    InvocationAssociation,
    MaturityState,
    RecoveryAction,
    Registration,
    ReleaseReadinessDecision,
    VerificationRun,
)
from app.models.evidence import LearningEpisode, Lesson, RetrievalRecord
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    InvocationId,
    OrganizationId,
    RecordId,
    RunId,
    new_record_id,
)
from app.models.runs import AgentNodeAttempt
from app.registry.admission import PackAdmission
from app.registry.compatibility import (
    CompatibilityEvaluation,
    CompatibilityMatrixEntry,
    CompatibilityRegistry,
    DeclaredCompatibilityRanges,
)
from app.registry.pack_validator import DomainPackValidator
from app.repositories.pack_repository import InMemoryPackRepository
from app.repositories.protocols import (
    AgentLifecycleRepository,
    AgentNodeAttemptRepository,
    ArtifactHandoffRepository,
    AuditRecordRepository,
    AuthorizationDecisionRepository,
    InvocationAssociationRepository,
    LearningEpisodeRepository,
    LessonRepository,
    MaturityStateRepository,
    RecoveryActionRepository,
    RegistrationRepository,
    ReleaseReadinessDecisionRepository,
    RetrievalRecordRepository,
    RunRepository,
    VerificationRunRepository,
)
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences

RecordT = TypeVar("RecordT")
KeyT = TypeVar("KeyT")


class InMemoryAdoptionRepository[RecordT, KeyT]:
    """Thread-safe append-only repository used by the default local composition."""

    def __init__(self, label: str, key_for: Callable[[RecordT], KeyT]) -> None:
        self._label = label
        self._key_for = key_for
        self._records: dict[KeyT, RecordT] = {}
        self._record_ids: set[RecordId] = set()
        self._lock = RLock()

    def append(self, record: RecordT) -> Result[RecordT, ErrorDetail]:
        with self._lock:
            key = self._key_for(record)
            record_id = getattr(getattr(record, "metadata", None), "record_id", None)
            if key in self._records or record_id in self._record_ids:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, f"{self._label} already exists.")
                )
            self._records[key] = record
            if isinstance(record_id, str):
                self._record_ids.add(RecordId(record_id))
            return Result.success(record)

    def replace(self, record: RecordT) -> Result[RecordT, ErrorDetail]:
        with self._lock:
            key = self._key_for(record)
            if key not in self._records:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, f"{self._label} was not found.")
                )
            self._records[key] = record
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[RecordT, ErrorDetail]:
        with self._lock:
            record = next(
                (
                    candidate
                    for candidate in self._records.values()
                    if getattr(getattr(candidate, "metadata", None), "record_id", None) == record_id
                ),
                None,
            )
            metadata = getattr(record, "metadata", None) if record is not None else None
            if record is None or getattr(metadata, "organization_id", None) != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, f"{self._label} was not found.")
                )
            return Result.success(record)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[RecordT, ...], ErrorDetail]:
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if getattr(getattr(record, "metadata", None), "organization_id", None)
                    == organization_id
                )
            )

    def records(self) -> tuple[RecordT, ...]:
        with self._lock:
            return tuple(self._records.values())

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(
            code,
            message,
            CorrelationId("adoption-repository"),
            retryable=code is ErrorCode.REPOSITORY_UNAVAILABLE,
        )


class InMemoryInvocationAssociationRepository(
    InMemoryAdoptionRepository[InvocationAssociation, str], InvocationAssociationRepository
):
    def __init__(self) -> None:
        super().__init__("Invocation association", lambda record: str(record.invocation_id))

    def get_by_invocation_id(
        self, organization_id: OrganizationId, invocation_id: str
    ) -> Result[InvocationAssociation, ErrorDetail]:
        record = self._records.get(invocation_id)
        if record is None or record.organization_id != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Invocation association was not found.")
            )
        return Result.success(record)


class InMemoryRegistrationRepository(
    InMemoryAdoptionRepository[Registration, tuple[DomainPackId, str]], RegistrationRepository
):
    def __init__(self) -> None:
        super().__init__("Registration", lambda record: record.identity_key)

    def get_by_pack_version(
        self, organization_id: OrganizationId, pack_id: DomainPackId, immutable_version: str
    ) -> Result[Registration, ErrorDetail]:
        record = self._records.get((pack_id, immutable_version))
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(self._error(ErrorCode.NOT_FOUND, "Registration was not found."))
        return Result.success(record)


class InMemoryArtifactHandoffRepository(
    InMemoryAdoptionRepository[ArtifactHandoff, ArtifactHandoffId], ArtifactHandoffRepository
):
    def __init__(self) -> None:
        super().__init__("Artifact handoff", lambda record: record.handoff_id)

    def append_handoff(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, ErrorDetail]:
        return self.append(record)

    def get(
        self, organization_id: OrganizationId, handoff_id: RecordId | ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        record = next((item for item in self.records() if item.handoff_id == handoff_id), None)
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Artifact handoff was not found.")
            )
        return Result.success(record)

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        return Result.success(
            tuple(
                record
                for record in self.records()
                if record.metadata.organization_id == organization_id
                and record.availability is ArtifactAvailabilityStatus.AVAILABLE
                and record.metadata_persisted
            )
        )

    def confirm_metadata_persistence(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        current = self.get(organization_id, handoff_id)
        if not current.is_success or current.value is None:
            return current

        confirmed = dc_replace(
            current.value,
            availability=ArtifactAvailabilityStatus.AVAILABLE,
            metadata_persisted=True,
        )
        return self.replace(confirmed)

    def revoke_availability(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        current = self.get(organization_id, handoff_id)
        if not current.is_success or current.value is None:
            return current

        revoked = dc_replace(current.value, availability=ArtifactAvailabilityStatus.REVOKED)
        return self.replace(revoked)


class InMemoryRetrievalRecordRepository(
    InMemoryAdoptionRepository[RetrievalRecord, object], RetrievalRecordRepository
):
    def __init__(self) -> None:
        super().__init__("Retrieval record", lambda record: record.retrieval_record_id)

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[RetrievalRecord, ErrorDetail]:
        record = next((item for item in self.records() if item.attempt_id == attempt_id), None)
        if record is None or record.organization_id != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Retrieval record was not found.")
            )
        return Result.success(record)


class InMemoryLearningEpisodeRepository(
    InMemoryAdoptionRepository[LearningEpisode, object], LearningEpisodeRepository
):
    def __init__(self) -> None:
        super().__init__("Learning episode", lambda record: record.episode_id)

    def append(self, record: LearningEpisode) -> Result[LearningEpisode, ErrorDetail]:
        if any(item.attempt_id == record.attempt_id for item in self.records()):
            return Result.failure(
                self._error(
                    ErrorCode.CONFLICT, "A terminal episode already exists for the attempt."
                )
            )
        return super().append(record)

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[LearningEpisode, ErrorDetail]:
        record = next((item for item in self.records() if item.attempt_id == attempt_id), None)
        if record is None or record.organization_id != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Learning episode was not found.")
            )
        return Result.success(record)


class InMemoryLessonRepository(InMemoryAdoptionRepository[Lesson, object], LessonRepository):
    def __init__(self) -> None:
        super().__init__("Lesson", lambda record: record.lesson_id)

    def retrievable_for(
        self,
        organization_id: OrganizationId,
        domain_id: str,
        pack_version: str,
        agent_id: AgentId,
        memory_scope: str,
    ) -> Result[tuple[Lesson, ...], ErrorDetail]:
        return Result.success(
            tuple(
                lesson
                for lesson in self.records()
                if lesson.metadata.organization_id == organization_id
                and str(lesson.domain_id) == domain_id
                and lesson.pack_version_range.contains(pack_version)
                and lesson.agent_id == agent_id
                and lesson.memory_scope == memory_scope
                and lesson.retrievable
                and not lesson.revoked
                and not lesson.stale
            )
        )

    def revoke(
        self, organization_id: OrganizationId, lesson_id: str
    ) -> Result[Lesson, ErrorDetail]:

        current = next((item for item in self.records() if str(item.lesson_id) == lesson_id), None)
        if current is None or current.metadata.organization_id != organization_id:
            return Result.failure(self._error(ErrorCode.NOT_FOUND, "Lesson was not found."))
        return self.replace(dc_replace(current, retrievable=False, revoked=True))


class InMemoryAgentNodeAttemptRepository(
    InMemoryAdoptionRepository[AgentNodeAttempt, object], AgentNodeAttemptRepository
):
    def __init__(self) -> None:
        super().__init__("Agent node attempt", lambda record: record.attempt_id)

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[AgentNodeAttempt, ErrorDetail]:
        record = next((item for item in self.records() if item.attempt_id == attempt_id), None)
        if record is None or OrganizationId(record.organization_id) != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Agent node attempt was not found.")
            )
        return Result.success(record)

    def mark_blocked_for_recovery(
        self,
        organization_id: OrganizationId,
        attempt_id: AgentNodeAttemptId,
        correlation_id: CorrelationId,
    ) -> Result[AgentNodeAttempt, ErrorDetail]:
        from app.models.runs import AgentNodeAttemptStatus

        current = self.get_by_attempt_id(organization_id, attempt_id)
        if not current.is_success or current.value is None:
            return current
        blocked = dc_replace(
            current.value,
            metadata=dc_replace(
                current.value.metadata,
                correlation_id=correlation_id,
                version=current.value.metadata.version + 1,
            ),
            status=AgentNodeAttemptStatus.BLOCKED,
            terminal_outcome_reference=current.value.terminal_outcome_reference
            or f"recovery:{attempt_id}",
        )
        return self.replace(blocked)


class InMemoryMaturityStateRepository(
    InMemoryAdoptionRepository[MaturityState, object], MaturityStateRepository
):
    def __init__(self) -> None:
        super().__init__("Maturity state", lambda record: record.identity_key)


class InMemoryAuditRecordRepository(AuditRecordRepository):
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []
        self._lock = RLock()

    def append(self, record: AuditRecord) -> Result[AuditRecord, ErrorDetail]:
        with self._lock:
            if any(item.audit_id == record.audit_id for item in self._records):
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Audit record already exists.",
                        record.metadata.correlation_id,
                    )
                )
            self._records.append(record)
            return Result.success(record)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[AuditRecord, ...], ErrorDetail]:
        with self._lock:
            return Result.success(
                tuple(
                    item
                    for item in self._records
                    if item.metadata.organization_id == organization_id
                )
            )

    @property
    def records(self) -> tuple[AuditRecord, ...]:
        with self._lock:
            return tuple(self._records)


class InMemoryVerificationRunRepository(
    InMemoryAdoptionRepository[VerificationRun, object], VerificationRunRepository
):
    def __init__(self) -> None:
        super().__init__("Verification run", lambda record: record.verification_run_id)


class InMemoryReleaseReadinessRepository(
    InMemoryAdoptionRepository[ReleaseReadinessDecision, tuple[object, str, str]],
    ReleaseReadinessDecisionRepository,
):
    def __init__(self) -> None:
        super().__init__(
            "Release readiness decision",
            lambda record: (record.pack_id, record.immutable_version, record.workflow_id),
        )

    def get_terminal(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        workflow_id: str,
    ) -> Result[ReleaseReadinessDecision, ErrorDetail]:
        record = self._records.get((pack_id, immutable_version, workflow_id))
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                self._error(ErrorCode.NOT_FOUND, "Release readiness decision was not found.")
            )
        return Result.success(record)


class InMemoryRecoveryActionRepository(
    InMemoryAdoptionRepository[RecoveryAction, object], RecoveryActionRepository
):
    def __init__(self) -> None:
        super().__init__("Recovery action", lambda record: record.recovery_action_id)


class InMemoryAuthorizationDecisionRepository(
    InMemoryAdoptionRepository[AuthorizationDecisionRecord, object], AuthorizationDecisionRepository
):
    def __init__(self) -> None:
        super().__init__("Authorization decision", lambda record: record.decision_id)


@dataclass(frozen=True, slots=True)
class AdoptionRepositories:
    """All repository ports owned by the adoption dependency graph."""

    registrations: RegistrationRepository
    invocations: InvocationAssociationRepository
    authorizations: AuthorizationDecisionRepository
    handoffs: ArtifactHandoffRepository
    lifecycles: AgentLifecycleRepository
    attempts: AgentNodeAttemptRepository
    retrievals: RetrievalRecordRepository
    episodes: LearningEpisodeRepository
    lessons: LessonRepository
    verifications: VerificationRunRepository
    releases: ReleaseReadinessDecisionRepository
    recoveries: RecoveryActionRepository
    maturity: MaturityStateRepository
    audits: AuditRecordRepository


@dataclass(frozen=True, slots=True)
class CompatibilityRouteResult:
    """Compatibility evidence plus the guard status used by invocation routes."""

    evaluation: CompatibilityEvaluation
    evidence: object


class AdoptionServices:
    """Compose adoption controllers once and expose typed, fail-closed operations."""

    def __init__(self, repositories: AdoptionRepositories | None = None) -> None:
        self.repositories = repositories or _default_repositories()
        self.compatibility_registry = CompatibilityRegistry()
        self.host_supported_range = CompatibilityRange.exact("1.0.0")
        self.alc_supported_range = CompatibilityRange.exact("1.0.0")
        self.pack_admission = PackAdmission(
            self.repositories.registrations,
            self.repositories.audits,
            validator=DomainPackValidator(InMemoryPackRepository()),
        )
        self.authorization = GovernanceAuthorizationService()
        self.artifact_handoffs = ArtifactHandoffService(
            self.repositories.handoffs,
            self.repositories.audits,
        )
        self.learning_lifecycle = LearningLifecycleService(
            self.repositories.lifecycles,
            self.repositories.retrievals,
            self.repositories.episodes,
            self.repositories.audits,
            self.repositories.attempts,
        )
        self.lessons = LessonService(
            self.repositories.lessons,
            self.repositories.retrievals,
            self.repositories.episodes,
            self.repositories.audits,
        )
        self.operational_containment = OperationalContainmentService(
            self.repositories.releases,
            self.repositories.maturity,
            self.repositories.audits,
        )
        self.verification = VerificationSuite(
            self.repositories.verifications,
            self.repositories.releases,
            compatibility_repository=self.compatibility_registry.matrix_repository,
            audit_repository=self.repositories.audits,
        )
        self.invocation = RunService(
            _adoption_run_repository(),
            RegisteredReferences(
                agent_ids=frozenset(),
                tool_ids=frozenset(),
                memory_scope_ids=frozenset(),
                risk_gate_ids=frozenset(),
                rollback_plan_ids=frozenset(),
                authorization_ids=frozenset(),
            ),
            invocation_association_repository=self.repositories.invocations,
            audit_repository=self.repositories.audits,
            compatibility_registry=self.compatibility_registry,
        )
        self._governance_contexts: dict[
            tuple[OrganizationId, str, str, AgentId], AuthorizationContext
        ] = {}
        self._provider_declarations: dict[
            tuple[OrganizationId, str, str], ProviderAdapterDeclaration
        ] = {}

    def register_pack(
        self,
        manifest: Mapping[str, object],
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
    ) -> Result[Registration, ErrorDetail]:
        """Admit a declarative pack and index only server-derived governance context."""
        submitted = dict(manifest)
        submitted["signer_id"] = str(actor_id)
        result = self.pack_admission.register(
            submitted,
            signer=actor_id,
            correlation_id=correlation_id,
            organization_id=organization_id,
            host_contract=None,
            alc_contract=None,
        )
        if not result.is_success or result.value is None:
            return Result.failure(_with_correlation(result.error, correlation_id))
        registration = result.value
        self._record_compatibility_for_registration(registration)
        self._index_governance_contexts(
            submitted, registration, organization_id, actor_id, correlation_id
        )
        return Result.success(registration)

    def submit_invocation(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        invocation_id: str,
        domain_id: str,
        pack_id: str,
        pack_version: str,
        agent_id: str,
        workflow_id: str,
        run_id: str,
    ) -> Result[InvocationAssociation, ErrorDetail]:
        try:
            metadata = _metadata(organization_id, correlation_id)
            association = InvocationAssociation(
                metadata=metadata,
                invocation_id=InvocationId(invocation_id),
                organization_id=organization_id,
                domain_id=DomainId(domain_id),
                pack_version=pack_version,
                agent_id=AgentId(agent_id),
                workflow_id=workflow_id,
                run_id=RunId(run_id),
                correlation_id=correlation_id,
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        result = self.invocation.begin_invocation(association, pack_id=DomainPackId(pack_id))
        return (
            result
            if result.is_success
            else Result.failure(_with_correlation(result.error, correlation_id))
        )

    def compatibility(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        pack_id: str,
        immutable_version: str,
        pack_contract_version: str,
        host_range: CompatibilityRange,
        alc_range: CompatibilityRange,
        supported_host_version: str,
        supported_alc_version: str,
    ) -> Result[CompatibilityRouteResult, ErrorDetail]:
        try:
            evaluation = self.compatibility_registry.evaluate_detailed(
                DeclaredCompatibilityRanges(
                    host_range, alc_range, DomainPackId(pack_id), immutable_version
                ),
                CompatibilityRange.exact(supported_host_version),
                CompatibilityRange.exact(supported_alc_version),
            )
            entry = CompatibilityMatrixEntry(
                pack_contract_version=pack_contract_version,
                host_contract_version=supported_host_version,
                alc_version=supported_alc_version,
                status=evaluation.status,
                pack_id=DomainPackId(pack_id),
                immutable_version=immutable_version,
                evidence_reference=f"compatibility:{pack_id}@{immutable_version}",
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        retained = self.verification.record_compatibility_result(
            organization_id, correlation_id, entry
        )
        if not retained.is_success or retained.value is None:
            return Result.failure(
                retained.error
                or ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Compatibility evidence is unavailable.",
                    correlation_id,
                    retryable=True,
                )
            )
        return Result.success(CompatibilityRouteResult(evaluation, retained.value))

    def governance_context(
        self,
        organization_id: OrganizationId,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        correlation_id: CorrelationId,
    ) -> Result[AuthorizationContext, ErrorDetail]:
        context = self._governance_contexts.get(
            (organization_id, domain_id, pack_version, AgentId(agent_id))
        )
        if context is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Governance declaration is unavailable.",
                    correlation_id,
                )
            )
        return Result.success(context)

    def authorize_data(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        memory_scope: str,
    ) -> Result[AuthorizationDecisionRecord, ErrorDetail]:
        context = self.governance_context(
            organization_id, domain_id, pack_version, agent_id, correlation_id
        )
        if not context.is_success or context.value is None:
            return Result.failure(
                context.error
                or ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Governance declaration is unavailable.",
                    correlation_id,
                )
            )
        decision = self.authorization.authorize_data_access(
            context.value,
            DataAccessRequest(
                str(organization_id), domain_id, pack_version, agent_id, memory_scope
            ),
        )
        return self._persist_authorization(
            organization_id,
            correlation_id,
            domain_id,
            pack_version,
            agent_id,
            memory_scope,
            decision.permitted,
            tuple(str(item) for item in decision.denied_constraints),
        )

    def authorize_tool(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        tool_id: str,
    ) -> Result[AuthorizationDecisionRecord, ErrorDetail]:
        context = self.governance_context(
            organization_id, domain_id, pack_version, agent_id, correlation_id
        )
        if not context.is_success or context.value is None:
            return Result.failure(
                context.error
                or ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Governance declaration is unavailable.",
                    correlation_id,
                )
            )
        decision = self.authorization.evaluate(context.value, tool_id)
        return self._persist_authorization(
            organization_id,
            correlation_id,
            domain_id,
            pack_version,
            agent_id,
            tool_id,
            decision.permitted,
            tuple(str(item) for item in decision.denied_constraints),
        )

    def authorize_outbound(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        destination: str,
    ) -> Result[AuthorizationDecisionRecord, ErrorDetail]:
        context = self.governance_context(
            organization_id, domain_id, pack_version, agent_id, correlation_id
        )
        if not context.is_success or context.value is None:
            return Result.failure(
                context.error
                or ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Governance declaration is unavailable.",
                    correlation_id,
                )
            )
        decision = self.authorization.authorize_outbound(context.value, destination)
        return self._persist_authorization(
            organization_id,
            correlation_id,
            domain_id,
            pack_version,
            agent_id,
            destination,
            decision.permitted,
            tuple(str(item) for item in decision.denied_constraints),
        )

    def authorize_provider(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        provider_id: str,
        capability: str,
    ) -> Result[AuthorizationDecisionRecord, ErrorDetail]:
        declaration = self._provider_declarations.get((organization_id, domain_id, pack_version))
        decision: ProviderAuthorizationDecision = authorize_provider_adapter(
            object(), declaration, capability=capability
        )
        reasons = tuple(str(item) for item in decision.denied_reasons)
        return self._persist_authorization(
            organization_id,
            correlation_id,
            domain_id,
            pack_version,
            agent_id,
            provider_id,
            decision.permitted,
            reasons,
        )

    def _persist_authorization(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        domain_id: str,
        pack_version: str,
        agent_id: str,
        capability: str,
        allowed: bool,
        reasons: tuple[str, ...],
    ) -> Result[AuthorizationDecisionRecord, ErrorDetail]:
        outcome = AuthorizationOutcome.ALLOWED if allowed else AuthorizationOutcome.DENIED
        record = AuthorizationDecisionRecord(
            metadata=_metadata(organization_id, correlation_id),
            decision_id=AuthorizationDecisionId(str(new_record_id())),
            organization_id=organization_id,
            domain_id=DomainId(domain_id),
            pack_version=pack_version,
            agent_id=AgentId(agent_id),
            capability=capability,
            scope={"capability": capability},
            outcome=outcome,
            reason=None if allowed else (";".join(reasons) or "authorization_denied"),
            evidence_references=(f"authorization:{capability}",),
            recorded_at=utc_now(),
        )
        persisted = self.repositories.authorizations.append(record)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(_with_correlation(persisted.error, correlation_id))
        if not allowed:
            self._append_audit(
                organization_id, correlation_id, "governance.denied", capability, "denied"
            )
        return Result.success(persisted.value)

    def _record_compatibility_for_registration(self, registration: Registration) -> None:
        evaluation = self.compatibility_registry.evaluate_detailed(
            DeclaredCompatibilityRanges(
                registration.host_compatibility_range,
                registration.alc_compatibility_range,
                registration.pack_id,
                registration.immutable_version,
            ),
            self.host_supported_range,
            self.alc_supported_range,
        )
        _ = evaluation

    def _index_governance_contexts(
        self,
        manifest: Mapping[str, object],
        registration: Registration,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
    ) -> None:
        domain_id = str(manifest.get("domain_id") or registration.pack_id)
        raw_agents = manifest.get("agents")
        if not isinstance(raw_agents, list):
            return
        for raw_agent in raw_agents:
            if not isinstance(raw_agent, Mapping):
                continue
            agent_id = raw_agent.get("agent_id")
            if not isinstance(agent_id, str) or not agent_id.strip():
                continue
            tools = _string_set(raw_agent.get("allowed_tools"))
            scopes = _string_set(raw_agent.get("memory_scopes"))
            outbound = _string_set(raw_agent.get("allowed_outbound_destinations"))
            self._governance_contexts[
                (organization_id, domain_id, registration.immutable_version, AgentId(agent_id))
            ] = AuthorizationContext(
                agent_id=agent_id,
                step_id=f"registration:{registration.registration_id}",
                organization_id=str(organization_id),
                actor_id=str(actor_id),
                correlation_id=str(correlation_id),
                agent_allowed_tools=tools,
                step_declared_tools=tools,
                role_allowed_tools=tools,
                organization_allowed_tools=tools,
                risk_allowed_tools=tools,
                approval_state=ApprovalState.NOT_REQUIRED,
                domain_id=domain_id,
                pack_version=registration.immutable_version,
                supported_pack_range=CompatibilityRange.exact(registration.immutable_version),
                declared_memory_scopes=scopes,
                declared_outbound_destinations=outbound,
                declared_tool_ids=tools,
            )

    def _append_audit(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        action: str,
        subject_reference: str,
        outcome: str,
    ) -> None:
        now = utc_now()
        record = AuditRecord(
            metadata=_metadata(organization_id, correlation_id),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=subject_reference,
            outcome=outcome,
            recorded_at=now,
        )
        try:
            self.repositories.audits.append(record)
        except Exception:
            return


def _default_repositories() -> AdoptionRepositories:
    return AdoptionRepositories(
        registrations=InMemoryRegistrationRepository(),
        invocations=InMemoryInvocationAssociationRepository(),
        authorizations=InMemoryAuthorizationDecisionRepository(),
        handoffs=InMemoryArtifactHandoffRepository(),
        lifecycles=InMemoryAdoptionRepository(
            "Agent lifecycle", lambda record: record.lifecycle_id
        ),
        attempts=InMemoryAgentNodeAttemptRepository(),
        retrievals=InMemoryRetrievalRecordRepository(),
        episodes=InMemoryLearningEpisodeRepository(),
        lessons=InMemoryLessonRepository(),
        verifications=InMemoryVerificationRunRepository(),
        releases=InMemoryReleaseReadinessRepository(),
        recoveries=InMemoryRecoveryActionRepository(),
        maturity=InMemoryMaturityStateRepository(),
        audits=InMemoryAuditRecordRepository(),
    )


def _adoption_run_repository() -> RunRepository:
    from app.repositories.run_repository import InMemoryRunRepository

    return InMemoryRunRepository()


def _metadata(organization_id: OrganizationId, correlation_id: CorrelationId) -> RecordMetadata:
    now = utc_now()
    return RecordMetadata(
        record_id=new_record_id(),
        organization_id=organization_id,
        correlation_id=correlation_id,
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=now,
        updated_at=now,
    )


def _string_set(value: object) -> frozenset[str]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return frozenset()
    return frozenset(item.strip() for item in value if isinstance(item, str) and item.strip())


def _with_correlation(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
    if error is None:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Adoption persistence is unavailable.",
            correlation_id,
            retryable=True,
        )
    return ErrorDetail(error.code, error.message, correlation_id, error.retryable, error.fields)


_DEFAULT_ADOPTION_SERVICES = AdoptionServices()


def get_adoption_services() -> AdoptionServices:
    """Return the composed adoption graph; tests/deployments may override this dependency."""
    return _DEFAULT_ADOPTION_SERVICES
