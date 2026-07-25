"""Evidence-first lifecycle orchestration for learning-required agents.

The service keeps lifecycle decisions separate from immutable evidence persistence:
activation records are appended only after all gates are evaluated, retrieval is a
pre-action barrier, and terminal episode retries are idempotent by attempt identity.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import (
    AgentLearningContract,
    ErrorCode,
    ErrorDetail,
    RepositoryError,
    Result,
)
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    AuditRecord,
    LearningEpisodeId,
    RetrievalRecordId,
)
from app.models.evidence import (
    LearningEpisode,
    LearningTerminalOutcome,
    RetrievalRecord,
)
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    new_record_id,
)
from app.models.runs import AgentNodeAttempt
from app.repositories.protocols import (
    AgentLifecycleRepository,
    AgentNodeAttemptRepository,
    AuditRecordRepository,
    LearningEpisodeRepository,
    RetrievalRecordRepository,
)

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ActivationEvidence:
    """Host-owned evidence required before a learning agent can become active."""

    approved_agent_scoped_memory: bool = False
    pre_action_retrieval_enabled: bool = False
    learning_episode_capture_enabled: bool = False
    reflection_evaluator_enabled: bool = False
    retention_policy: str | bool | None = None
    required_evaluations_passed: bool = False
    evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        references = tuple(str(reference) for reference in self.evidence_references)
        if any(not reference.strip() for reference in references):
            raise ValueError("Activation evidence references must be non-empty.")
        if len(references) != len(set(references)):
            raise ValueError("Activation evidence references must be unique.")
        object.__setattr__(self, "evidence_references", references)

    @property
    def all_required_checks_pass(self) -> bool:
        """Return whether every host-owned activation gate is satisfied."""
        return (
            self.approved_agent_scoped_memory
            and self.pre_action_retrieval_enabled
            and self.learning_episode_capture_enabled
            and self.reflection_evaluator_enabled
            and _policy_is_enabled(self.retention_policy)
            and self.required_evaluations_passed
        )

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> ActivationEvidence:
        """Normalize a redaction-safe evidence mapping from an integration boundary."""
        return cls(
            approved_agent_scoped_memory=_mapping_flag(
                values,
                "approved_agent_scoped_memory",
                "approved_memory",
                "agent_scoped_memory_approved",
            ),
            pre_action_retrieval_enabled=_mapping_flag(
                values,
                "pre_action_retrieval_enabled",
                "retrieval_enabled",
            ),
            learning_episode_capture_enabled=_mapping_flag(
                values,
                "learning_episode_capture_enabled",
                "episode_capture_enabled",
            ),
            reflection_evaluator_enabled=_mapping_flag(
                values,
                "reflection_evaluator_enabled",
                "reflection_enabled",
            ),
            retention_policy=_retention_policy_value(values.get("retention_policy")),
            required_evaluations_passed=_mapping_flag(
                values,
                "required_evaluations_passed",
                "evaluations_passed",
            ),
            evidence_references=_mapping_references(
                values.get("evidence_references", ())
            ),
        )


class LearningLifecycleService:
    """Enforce activation, retrieval, and terminal learning evidence barriers."""

    def __init__(
        self,
        lifecycle_repository: AgentLifecycleRepository,
        retrieval_repository: RetrievalRecordRepository,
        episode_repository: LearningEpisodeRepository,
        audit_repository: AuditRecordRepository | None = None,
        attempt_repository: AgentNodeAttemptRepository | None = None,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._lifecycle_repository = lifecycle_repository
        self._retrieval_repository = retrieval_repository
        self._episode_repository = episode_repository
        self._audit_repository = audit_repository
        self._attempt_repository = attempt_repository
        self._clock = clock

    def evaluate_activation(
        self,
        lifecycle: AgentLifecycle,
        alc_candidates: Iterable[AgentLearningContract],
        evidence: ActivationEvidence | Mapping[str, object] | None = None,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[AgentLifecycle, ErrorDetail]:
        """Append an active or blocked lifecycle decision after evaluating every gate.

        A blocked decision is still returned as a successful persistence result because
        the durable non-active state is the outcome callers must observe. Repository
        failures remain typed failures and never produce an active state.
        """
        effective_correlation = correlation_id or lifecycle.metadata.correlation_id
        normalized_evidence = self._coerce_evidence(evidence)
        candidates = tuple(alc_candidates)
        named = tuple(
            candidate
            for candidate in candidates
            if candidate.agent_id == lifecycle.agent_id
        )
        failures = self._activation_failures(lifecycle, named, normalized_evidence)
        effective_alc = named[0] if len(named) == 1 else None
        status = (
            AgentLifecycleStatus.ACTIVE
            if not failures
            else AgentLifecycleStatus.BLOCKED
        )
        references = self._activation_references(
            effective_alc,
            normalized_evidence,
            failures,
        )
        decision = AgentLifecycle(
            metadata=self._metadata(
                lifecycle.metadata.organization_id, effective_correlation
            ),
            lifecycle_id=AgentLifecycleId(str(new_record_id())),
            pack_id=lifecycle.pack_id,
            immutable_version=lifecycle.immutable_version,
            agent_id=lifecycle.agent_id,
            status=status,
            learning_required=lifecycle.learning_required,
            effective_alc_version=(
                effective_alc.version if effective_alc is not None else None
            ),
            activation_evidence_references=references,
            change_references=lifecycle.change_references,
        )
        persisted = self._append_lifecycle(decision, effective_correlation)
        if not persisted.is_success:
            return persisted
        return persisted

    def suspend_for_change(
        self,
        lifecycle: AgentLifecycle,
        change_references: Iterable[str] | str,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[AgentLifecycle, ErrorDetail]:
        """Persist suspension evidence before a lifecycle-affecting change is applied."""
        effective_correlation = correlation_id or lifecycle.metadata.correlation_id
        changes = _references(change_references, "change_references")
        if not changes:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Lifecycle-affecting changes require evidence references.",
                    effective_correlation,
                )
            )
        if (
            not lifecycle.learning_required
            or lifecycle.status is not AgentLifecycleStatus.ACTIVE
        ):
            return Result.success(lifecycle)
        suspended = AgentLifecycle(
            metadata=self._metadata(
                lifecycle.metadata.organization_id, effective_correlation
            ),
            lifecycle_id=AgentLifecycleId(str(new_record_id())),
            pack_id=lifecycle.pack_id,
            immutable_version=lifecycle.immutable_version,
            agent_id=lifecycle.agent_id,
            status=AgentLifecycleStatus.SUSPENDED,
            learning_required=True,
            effective_alc_version=lifecycle.effective_alc_version,
            activation_evidence_references=lifecycle.activation_evidence_references,
            change_references=changes,
        )
        return self._append_lifecycle(suspended, effective_correlation)

    def record_retrieval(
        self,
        attempt: AgentNodeAttempt,
        memory_scope: str,
        lesson_references: Iterable[str] = (),
        *,
        approved_filters: Mapping[str, object] | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[RetrievalRecord, ErrorDetail]:
        """Persist exactly one retrieval record before a learning-required action."""
        effective_correlation = correlation_id or attempt.metadata.correlation_id
        organization_id = OrganizationId(attempt.organization_id)
        try:
            requested_lessons = _references(lesson_references, "lesson_references")
        except ValueError as error:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED, str(error), effective_correlation
                )
            )
        requested_filters = approved_filters or {
            "organization_id": str(organization_id),
            "domain_id": str(attempt.domain_id),
            "pack_version": attempt.pack_version,
            "agent_id": str(attempt.agent_id),
            "memory_scope": memory_scope,
        }
        existing = self._retrieval_repository.get_by_attempt_id(
            organization_id, attempt.attempt_id
        )
        if existing.is_success and existing.value is not None:
            record = existing.value
            if (
                record.memory_scope == memory_scope
                and record.lesson_references == requested_lessons
                and record.approved_filters == requested_filters
            ):
                return Result.success(record)
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "A different Retrieval_Record already exists for this attempt.",
                    effective_correlation,
                )
            )
        if not existing.is_success and not _is_not_found(existing.error):
            lookup_error = self._repository_error(existing.error, effective_correlation)
            self._audit_block(
                organization_id,
                effective_correlation,
                f"attempt:{attempt.attempt_id}",
                "learning.retrieval.blocked",
                "retrieval_lookup_failed",
            )
            return Result.failure(lookup_error)

        try:
            record = RetrievalRecord(
                metadata=self._metadata(organization_id, effective_correlation),
                retrieval_record_id=RetrievalRecordId(str(new_record_id())),
                attempt_id=attempt.attempt_id,
                organization_id=organization_id,
                domain_id=attempt.domain_id,
                pack_version=attempt.pack_version,
                agent_id=attempt.agent_id,
                memory_scope=memory_scope,
                retrieved_at=self._clock(),
                lesson_references=requested_lessons,
                approved_filters=approved_filters,
            )
        except ValueError as error:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED, str(error), effective_correlation
                )
            )

        try:
            persisted = self._retrieval_repository.append(record)
        except Exception:
            persisted = Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Retrieval_Record persistence is unavailable.",
                    effective_correlation,
                    retryable=True,
                )
            )
        if persisted.is_success and persisted.value is not None:
            return Result.success(persisted.value)

        # A concurrent retry may have committed the one allowed record already.
        retry = self._retrieval_repository.get_by_attempt_id(
            organization_id, attempt.attempt_id
        )
        if retry.is_success and retry.value is not None:
            return Result.success(retry.value)
        persistence_error = self._repository_error(
            persisted.error, effective_correlation
        )
        self._audit_block(
            organization_id,
            effective_correlation,
            f"attempt:{attempt.attempt_id}",
            "learning.retrieval.blocked",
            "retrieval_record_persistence_failed",
        )
        return Result.failure(persistence_error)

    def execute_learning_action(
        self,
        attempt: AgentNodeAttempt,
        memory_scope: str,
        action: Callable[[RetrievalRecord], T],
        lesson_references: Iterable[str] = (),
        *,
        approved_filters: Mapping[str, object] | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[T, ErrorDetail]:
        """Run an action only after its Retrieval_Record crossed the persistence barrier."""
        retrieval = self.record_retrieval(
            attempt,
            memory_scope,
            lesson_references,
            approved_filters=approved_filters,
            correlation_id=correlation_id,
        )
        if not retrieval.is_success or retrieval.value is None:
            return Result.failure(
                retrieval.error
                or ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Learning action is blocked because retrieval evidence is unavailable.",
                    correlation_id or attempt.metadata.correlation_id,
                    retryable=True,
                )
            )
        try:
            return Result.success(action(retrieval.value))
        except Exception:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INTERNAL_ERROR,
                    "Learning action failed after retrieval evidence was retained.",
                    correlation_id or attempt.metadata.correlation_id,
                )
            )

    def record_terminal_episode(
        self,
        attempt: AgentNodeAttempt,
        terminal_outcome: LearningTerminalOutcome | str,
        outcome_reference: str,
        *,
        retrieval_record_id: RetrievalRecordId | None = None,
        evidence_references: Iterable[str] = (),
        correlation_id: CorrelationId | None = None,
    ) -> Result[LearningEpisode, ErrorDetail]:
        """Persist one immutable terminal episode, or block the attempt for recovery."""
        effective_correlation = correlation_id or attempt.metadata.correlation_id
        organization_id = OrganizationId(attempt.organization_id)
        try:
            outcome = LearningTerminalOutcome(terminal_outcome)
            references = _references(evidence_references, "evidence_references")
        except ValueError as error:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED, str(error), effective_correlation
                )
            )

        existing = self._episode_repository.get_by_attempt_id(
            organization_id, attempt.attempt_id
        )
        if existing.is_success and existing.value is not None:
            record = existing.value
            if (
                record.terminal_outcome is outcome
                and record.outcome_reference == outcome_reference
            ):
                return Result.success(record)
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "A different terminal Learning_Episode already exists for this attempt.",
                    effective_correlation,
                )
            )
        if not existing.is_success and not _is_not_found(existing.error):
            lookup_error = self._repository_error(existing.error, effective_correlation)
            self._block_for_recovery(attempt, effective_correlation)
            return Result.failure(lookup_error)

        resolved_retrieval_id = retrieval_record_id or self._retrieval_id_for_attempt(
            organization_id, attempt, effective_correlation
        )
        try:
            episode = LearningEpisode(
                metadata=self._metadata(organization_id, effective_correlation),
                episode_id=LearningEpisodeId(str(new_record_id())),
                attempt_id=attempt.attempt_id,
                organization_id=organization_id,
                domain_id=attempt.domain_id,
                pack_version=attempt.pack_version,
                agent_id=attempt.agent_id,
                terminal_outcome=outcome,
                outcome_reference=outcome_reference,
                recorded_at=self._clock(),
                retrieval_record_id=resolved_retrieval_id,
                evidence_references=references,
            )
        except ValueError as error:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED, str(error), effective_correlation
                )
            )

        try:
            persisted = self._episode_repository.append(episode)
        except Exception:
            persisted = Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Learning_Episode persistence is unavailable.",
                    effective_correlation,
                    retryable=True,
                )
            )
        if persisted.is_success and persisted.value is not None:
            return Result.success(persisted.value)

        retry = self._episode_repository.get_by_attempt_id(
            organization_id, attempt.attempt_id
        )
        if retry.is_success and retry.value is not None:
            return Result.success(retry.value)
        self._block_for_recovery(attempt, effective_correlation)
        return Result.failure(
            self._repository_error(
                persisted.error,
                effective_correlation,
                fallback_message=(
                    "Learning_Episode persistence failed; attempt is blocked for recovery."
                ),
            )
        )

    # The design uses camelCase names in interface tables; retain both spellings.
    evaluateActivation = evaluate_activation  # noqa: N815
    suspendForChange = suspend_for_change  # noqa: N815
    recordRetrieval = record_retrieval  # noqa: N815
    executeLearningAction = execute_learning_action  # noqa: N815
    recordTerminalEpisode = record_terminal_episode  # noqa: N815

    def _activation_failures(
        self,
        lifecycle: AgentLifecycle,
        named: tuple[AgentLearningContract, ...],
        evidence: ActivationEvidence,
    ) -> tuple[str, ...]:
        failures: list[str] = []
        if not lifecycle.learning_required:
            return ("learning_required_declaration_missing",)
        if len(named) != 1:
            failures.append("effective_alc_cardinality")
        elif lifecycle.effective_alc_version is not None and (
            named[0].version != lifecycle.effective_alc_version
        ):
            failures.append("effective_alc_version")
        if not evidence.approved_agent_scoped_memory:
            failures.append("agent_scoped_memory")
        if not evidence.pre_action_retrieval_enabled or not _policy_is_enabled(
            named[0].retrieval_policy if len(named) == 1 else None
        ):
            failures.append("pre_action_retrieval")
        if not evidence.learning_episode_capture_enabled:
            failures.append("learning_episode_capture")
        if not evidence.reflection_evaluator_enabled or not _policy_is_enabled(
            named[0].reflection_policy if len(named) == 1 else None
        ):
            failures.append("reflection_evaluator")
        if (
            not evidence.retention_policy
            or not _policy_is_enabled(evidence.retention_policy)
            or not (len(named) == 1 and _policy_is_enabled(named[0].retention_policy))
        ):
            failures.append("retention_policy")
        if not evidence.required_evaluations_passed or not (
            len(named) == 1 and named[0].evaluation_references
        ):
            failures.append("required_evaluations")
        return tuple(dict.fromkeys(failures))

    @staticmethod
    def _activation_references(
        alc: AgentLearningContract | None,
        evidence: ActivationEvidence,
        failures: tuple[str, ...],
    ) -> tuple[str, ...]:
        references = list(evidence.evidence_references)
        if alc is not None:
            references.append(f"alc:{alc.agent_id}@{alc.version}")
        references.extend(
            f"activation:{reference}"
            for reference in (
                "agent-scoped-memory",
                "pre-action-retrieval",
                "learning-episode-capture",
                "reflection-evaluator",
                "retention-policy",
                "required-evaluations",
            )
            if reference.replace("-", "_") not in failures
        )
        references.extend(f"activation:failed:{failure}" for failure in failures)
        return tuple(dict.fromkeys(references))

    @staticmethod
    def _coerce_evidence(
        evidence: ActivationEvidence | Mapping[str, object] | None,
    ) -> ActivationEvidence:
        if evidence is None:
            return ActivationEvidence()
        if isinstance(evidence, ActivationEvidence):
            return evidence
        return ActivationEvidence.from_mapping(evidence)

    def _append_lifecycle(
        self,
        record: AgentLifecycle,
        correlation_id: CorrelationId,
    ) -> Result[AgentLifecycle, ErrorDetail]:
        try:
            persisted = self._lifecycle_repository.append(record)
        except Exception:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Agent lifecycle persistence is unavailable.",
                    correlation_id,
                    retryable=True,
                )
            )
        if persisted.is_success and persisted.value is not None:
            return Result.success(persisted.value)
        return Result.failure(self._repository_error(persisted.error, correlation_id))

    def _retrieval_id_for_attempt(
        self,
        organization_id: OrganizationId,
        attempt: AgentNodeAttempt,
        correlation_id: CorrelationId,
    ) -> RetrievalRecordId | None:
        result = self._retrieval_repository.get_by_attempt_id(
            organization_id, attempt.attempt_id
        )
        if result.is_success and result.value is not None:
            return result.value.retrieval_record_id
        if result.error is not None and not _is_not_found(result.error):
            self._audit_block(
                organization_id,
                correlation_id,
                f"attempt:{attempt.attempt_id}",
                "learning.episode.recovery_blocked",
                "retrieval_link_unavailable",
            )
        return None

    def _block_for_recovery(
        self,
        attempt: AgentNodeAttempt,
        correlation_id: CorrelationId,
    ) -> None:
        if self._attempt_repository is not None:
            with suppress(Exception):
                self._attempt_repository.mark_blocked_for_recovery(
                    OrganizationId(attempt.organization_id),
                    attempt.attempt_id,
                    correlation_id,
                )
        self._audit_block(
            OrganizationId(attempt.organization_id),
            correlation_id,
            f"attempt:{attempt.attempt_id}",
            "learning.episode.recovery_blocked",
            "learning_episode_persistence_failed",
        )

    def _audit_block(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        subject_reference: str,
        action: str,
        outcome: str,
    ) -> None:
        if self._audit_repository is None:
            return
        now = self._clock()
        audit = AuditRecord(
            metadata=self._metadata(organization_id, correlation_id),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=subject_reference,
            outcome=outcome,
            recorded_at=now,
        )
        try:
            self._audit_repository.append(audit)
        except Exception:
            return

    def _metadata(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> RecordMetadata:
        now = self._clock()
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
    def _repository_error(
        error: RepositoryError | None,
        correlation_id: CorrelationId,
        *,
        fallback_message: str = "Learning lifecycle persistence is unavailable.",
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                fallback_message,
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )


def _mapping_flag(values: Mapping[str, object], *names: str) -> bool:
    for name in names:
        if name in values:
            return _value_is_enabled(values[name])
    return False


def _value_is_enabled(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().casefold() in {
            "enabled",
            "enable",
            "on",
            "true",
            "yes",
            "passed",
        }
    return False


def _policy_is_enabled(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        return False
    return value.strip().casefold() not in {
        "",
        "disabled",
        "disable",
        "off",
        "false",
        "none",
        "not_enabled",
    }


def _retention_policy_value(value: object) -> str | bool | None:
    if isinstance(value, bool | str):
        return value
    return None


def _mapping_references(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return _references(value, "evidence_references")


def _references(values: Iterable[object] | str, name: str) -> tuple[str, ...]:
    raw = (values,) if isinstance(values, str) else tuple(values)
    references = tuple(str(value) for value in raw)
    if any(not reference.strip() for reference in references):
        raise ValueError(f"{name} references must be non-empty.")
    if len(references) != len(set(references)):
        raise ValueError(f"{name} references must be unique.")
    return references


def _is_not_found(error: ErrorDetail | None) -> bool:
    return error is not None and error.code is ErrorCode.NOT_FOUND
