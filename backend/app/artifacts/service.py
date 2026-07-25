"""Governed opaque artifact handoffs; no method retrieves protected artifact content."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime

from app.models.common import RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AgentTask,
    ArtifactHandoff,
    ArtifactHandoffId,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork

_REQUIRED_HANDOFF_FIELDS = (
    "artifact_identity",
    "artifact_version",
    "parent_lineage",
    "technical_specification",
    "rights_and_consent_state",
    "continuity_state",
    "quality_control_state",
    "target_channels",
    "provenance_reference",
)


@dataclass(frozen=True, slots=True)
class ArtifactHandoffValidation:
    """Presence-only artifact gate result for one dependent task."""

    handoff_id: ArtifactHandoffId
    task_id: TaskId
    missing_fields: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        """Return whether this handoff satisfies the dependent-dispatch presence gate."""
        return not self.missing_fields


@dataclass(frozen=True, slots=True)
class ArtifactBrowserProjection:
    """Authorized redacted browser representation; it intentionally has no content fields."""

    handoff_id: ArtifactHandoffId
    artifact_identity: str
    artifact_version: str
    parent_lineage: tuple[str, ...]
    source_task_id: TaskId
    source_run_reference: str
    validation: ArtifactHandoffValidation


@dataclass(frozen=True, slots=True)
class DownstreamArtifactReference:
    """Authorized downstream input containing references only, never artifact content."""

    handoff_id: ArtifactHandoffId
    artifact_identity: str
    artifact_version: str
    provenance_reference: str


class ArtifactService:
    """Record opaque handoffs and gate dependent tasks without inspecting protected content.

    Callers must pass the organization derived from trusted request context; repository
    lookups remain organization-scoped, and HTTP authorization is applied before this
    service is reached.
    """

    def __init__(
        self,
        unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork],
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def create_handoff(
        self, organization_id: OrganizationId, handoff: ArtifactHandoff
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist a versioned metadata handoff without accepting or storing content."""
        mismatch = self._organization_mismatch(
            organization_id, handoff.metadata.organization_id, handoff.metadata.correlation_id
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        with self._unit_of_work_factory() as unit_of_work:
            created = unit_of_work.artifacts.append(handoff)
            return self._repository_result(created, handoff.metadata.correlation_id)

    def validate_dependent_handoff(
        self,
        organization_id: OrganizationId,
        task_id: TaskId,
        handoff_id: ArtifactHandoffId,
        correlation_id: CorrelationId,
    ) -> Result[ArtifactHandoffValidation, ErrorDetail]:
        """Block only for absent required fields and retain their names on the task."""
        with self._unit_of_work_factory() as unit_of_work:
            task_result = unit_of_work.tasks.get(organization_id, task_id)
            if not task_result.is_success or task_result.value is None:
                return Result.failure(self._unavailable_task(correlation_id))
            handoff_result = unit_of_work.artifacts.get(organization_id, handoff_id)
            if not handoff_result.is_success or handoff_result.value is None:
                return Result.failure(self._unavailable_handoff(correlation_id))

            task = task_result.value
            handoff = handoff_result.value
            validation = ArtifactHandoffValidation(
                handoff_id=handoff.handoff_id,
                task_id=task.task_id,
                missing_fields=self.missing_required_fields(handoff),
            )
            updated_task = self._task_for_validation(task, validation, correlation_id)
            if updated_task is not None:
                persisted = unit_of_work.tasks.replace(updated_task, task.metadata.version)
                if not persisted.is_success:
                    return Result.failure(self._repository_error(persisted, correlation_id))
            return Result.success(validation)

    def read_browser_projection(
        self,
        organization_id: OrganizationId,
        handoff_id: ArtifactHandoffId,
        correlation_id: CorrelationId,
    ) -> Result[ArtifactBrowserProjection, ErrorDetail]:
        """Return an organization-authorized redacted lineage and validation projection."""
        with self._unit_of_work_factory() as unit_of_work:
            handoff_result = unit_of_work.artifacts.get(organization_id, handoff_id)
            if not handoff_result.is_success or handoff_result.value is None:
                return Result.failure(self._unavailable_handoff(correlation_id))
            handoff = handoff_result.value
            validation = ArtifactHandoffValidation(
                handoff_id=handoff.handoff_id,
                task_id=handoff.source_task_id,
                missing_fields=self.missing_required_fields(handoff),
            )
            return Result.success(
                ArtifactBrowserProjection(
                    handoff_id=handoff.handoff_id,
                    artifact_identity=handoff.artifact_identity,
                    artifact_version=handoff.artifact_version,
                    parent_lineage=handoff.parent_lineage,
                    source_task_id=handoff.source_task_id,
                    source_run_reference=handoff.source_run_reference,
                    validation=validation,
                )
            )

    def downstream_input(
        self,
        organization_id: OrganizationId,
        task_id: TaskId,
        handoff_id: ArtifactHandoffId,
        correlation_id: CorrelationId,
    ) -> Result[DownstreamArtifactReference, ErrorDetail]:
        """Provide a complete handoff to a dependent task as references, never content."""
        validation_result = self.validate_dependent_handoff(
            organization_id, task_id, handoff_id, correlation_id
        )
        if not validation_result.is_success or validation_result.value is None:
            return Result.failure(self._repository_error(validation_result, correlation_id))
        validation = validation_result.value
        if not validation.is_complete:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Artifact handoff is incomplete for dependent dispatch.",
                    correlation_id,
                    fields=tuple(
                        ErrorField(name, "required for artifact handoff")
                        for name in validation.missing_fields
                    ),
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            handoff_result = unit_of_work.artifacts.get(organization_id, handoff_id)
            if not handoff_result.is_success or handoff_result.value is None:
                return Result.failure(self._unavailable_handoff(correlation_id))
            handoff = handoff_result.value
            provenance_reference = handoff.provenance_reference
            if provenance_reference is None:
                raise RuntimeError("A complete artifact handoff must have provenance.")
            return Result.success(
                DownstreamArtifactReference(
                    handoff_id=handoff.handoff_id,
                    artifact_identity=handoff.artifact_identity,
                    artifact_version=handoff.artifact_version,
                    provenance_reference=provenance_reference,
                )
            )

    @staticmethod
    def missing_required_fields(handoff: ArtifactHandoff) -> tuple[str, ...]:
        """Return absent presence-gate fields without evaluating field content or quality."""
        fields: Mapping[str, object | None] = {
            "artifact_identity": handoff.artifact_identity,
            "artifact_version": handoff.artifact_version,
            "parent_lineage": handoff.parent_lineage,
            "technical_specification": handoff.technical_specification,
            "rights_and_consent_state": handoff.rights_and_consent_state,
            "continuity_state": handoff.continuity_state,
            "quality_control_state": handoff.quality_control_state,
            "target_channels": handoff.target_channels,
            "provenance_reference": handoff.provenance_reference,
        }
        return tuple(name for name in _REQUIRED_HANDOFF_FIELDS if not _is_present(fields[name]))

    def _task_for_validation(
        self,
        task: AgentTask,
        validation: ArtifactHandoffValidation,
        correlation_id: CorrelationId,
    ) -> AgentTask | None:
        if validation.missing_fields:
            return replace(
                task,
                metadata=self._next_metadata(task.metadata, correlation_id),
                state=TaskLifecycle.BLOCKED,
                blocked_fields=validation.missing_fields,
            )
        if task.state is TaskLifecycle.BLOCKED and task.blocked_fields:
            return replace(
                task,
                metadata=self._next_metadata(task.metadata, correlation_id),
                state=TaskLifecycle.IDLE,
                blocked_fields=(),
            )
        return None

    def _next_metadata(
        self, metadata: RecordMetadata, correlation_id: CorrelationId
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=self._clock(),
        )

    @staticmethod
    def _organization_mismatch(
        organization_id: OrganizationId,
        record_organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> ErrorDetail | None:
        if organization_id == record_organization_id:
            return None
        return ArtifactService._unavailable_handoff(correlation_id)

    @staticmethod
    def _unavailable_handoff(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Artifact handoff is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _unavailable_task(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Dependent task is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _repository_error(
        result: Result[object, ErrorDetail], correlation_id: CorrelationId
    ) -> ErrorDetail:
        error = result.error
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Artifact storage is unavailable.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @classmethod
    def _repository_result[T](
        cls, result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        return Result.failure(cls._repository_error(result, correlation_id))


def _is_present(value: object | None) -> bool:
    """Treat only absent or empty required fields as missing; never inspect their content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, tuple):
        return bool(value)
    return True
