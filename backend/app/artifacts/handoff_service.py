"""Fail-closed service for immutable Artifact_Handoff persistence and availability."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime
from typing import Protocol, cast

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuditRecord,
)
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id


class HandoffRepository(Protocol):
    """Minimal repository contract required by the handoff service."""

    def append(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist one immutable handoff."""

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        """Return only confirmed handoffs."""


class AuditRepository(Protocol):
    """Minimal audit repository contract required by the handoff service."""

    def append(self, record: AuditRecord) -> Result[AuditRecord, ErrorDetail]:
        """Persist one immutable audit record."""


ExtensionSchema = (
    Mapping[str, object]
    | frozenset[str]
    | set[str]
    | tuple[str, ...]
    | Callable[[Mapping[str, object]], object]
    | object
)


class ArtifactHandoffService:
    """Validate, persist, and expose opaque handoffs without exposing artifact content."""

    def __init__(
        self,
        repository: HandoffRepository,
        audit_repository: AuditRepository | None = None,
        *,
        va_extension_schema: ExtensionSchema | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._audit_repository = audit_repository
        self._va_extension_schema = va_extension_schema
        self._clock = clock

    def create_internal(
        self,
        organization_or_handoff: OrganizationId | ArtifactHandoff | None = None,
        handoff: ArtifactHandoff | None = None,
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
        extension_schema: ExtensionSchema | None = None,
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist an internal handoff and make it available only after append succeeds."""
        resolved = self._resolve_inputs(
            organization_or_handoff, handoff, organization_id, correlation_id
        )
        if not resolved.is_success or resolved.value is None:
            return Result.failure(
                resolved.error
                or self._validation(CorrelationId("handoff"), "A handoff is required.")
            )
        organization, correlation, candidate = resolved.value
        prepared = self._prepare(
            organization,
            correlation,
            candidate,
            external=False,
            extension_schema=extension_schema,
        )
        if not prepared.is_success or prepared.value is None:
            return Result.failure(
                prepared.error or self._validation(correlation, "Handoff validation failed.")
            )
        return self._persist(prepared.value, correlation)

    def submit_external(
        self,
        organization_or_handoff: OrganizationId | ArtifactHandoff | None = None,
        handoff: ArtifactHandoff | None = None,
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
        extension_schema: ExtensionSchema | None = None,
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist an external handoff as pending until metadata persistence is confirmed."""
        resolved = self._resolve_inputs(
            organization_or_handoff, handoff, organization_id, correlation_id
        )
        if not resolved.is_success or resolved.value is None:
            return Result.failure(
                resolved.error
                or self._validation(CorrelationId("handoff"), "A handoff is required.")
            )
        organization, correlation, candidate = resolved.value
        prepared = self._prepare(
            organization,
            correlation,
            candidate,
            external=True,
            extension_schema=extension_schema,
        )
        if not prepared.is_success or prepared.value is None:
            return Result.failure(
                prepared.error or self._validation(correlation, "Handoff validation failed.")
            )

        pending = prepared.value
        confirm = getattr(self._repository, "confirm_metadata_persistence", None)
        if callable(confirm):
            lineage_error = self._validate_lineage(pending, correlation)
            if lineage_error is not None:
                return Result.failure(lineage_error)
            persisted = self._append(pending, correlation)
            if not persisted.is_success or persisted.value is None:
                return persisted
            confirmed_result = cast(
                Callable[[OrganizationId, ArtifactHandoffId], Result[ArtifactHandoff, ErrorDetail]],
                confirm,
            )(organization, pending.handoff_id)
            return self._repository_result(confirmed_result, correlation)

        # Repositories with a single atomic append provide the confirmation at return.
        confirmed_record = replace(
            pending,
            availability=ArtifactAvailabilityStatus.AVAILABLE,
            metadata_persisted=True,
        )
        return self._persist(confirmed_record, correlation)

    def available_for_downstream(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        """Return only handoffs that have crossed the metadata confirmation barrier."""
        result = self._repository.available_for_downstream(organization_id)
        if result.is_success:
            return Result.success(result.value or ())
        return Result.failure(self._repository_error(result.error, correlation_id))

    def revoke_premature_availability(
        self,
        organization_id: OrganizationId,
        handoff_id: ArtifactHandoffId,
        correlation_id: CorrelationId,
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Revoke an externally exposed handoff and retain the required audit evidence."""
        get_handoff = cast(
            Callable[[OrganizationId, ArtifactHandoffId], Result[ArtifactHandoff, ErrorDetail]],
            getattr(self._repository, "get"),  # noqa: B009
        )
        current_result = get_handoff(organization_id, handoff_id)
        if not current_result.is_success or current_result.value is None:
            return Result.failure(self._repository_error(current_result.error, correlation_id))
        current = current_result.value
        if not current.external or current.metadata_persisted:
            return Result.failure(
                self._validation(correlation_id, "Handoff availability was not premature.")
            )

        revoke = getattr(self._repository, "revoke_availability", None)
        if not callable(revoke):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Handoff availability cannot be revoked by this repository.",
                    correlation_id,
                    retryable=True,
                )
            )
        revoked = cast(
            Callable[[OrganizationId, ArtifactHandoffId], Result[ArtifactHandoff, ErrorDetail]],
            revoke,
        )(organization_id, handoff_id)
        if not revoked.is_success or revoked.value is None:
            return Result.failure(self._repository_error(revoked.error, correlation_id))

        audit_failure = self._append_audit(
            organization_id,
            correlation_id,
            handoff_id,
            "artifact_handoff.availability.revoked",
            "revoked",
        )
        if audit_failure is not None:
            return Result.failure(audit_failure)
        return Result.success(revoked.value)

    # The design names these commands in camelCase; aliases keep both spellings stable.
    createInternal = create_internal  # noqa: N815
    submitExternal = submit_external  # noqa: N815
    revokePrematureAvailability = revoke_premature_availability  # noqa: N815

    def _prepare(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        handoff: ArtifactHandoff,
        *,
        external: bool,
        extension_schema: ExtensionSchema | None,
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        mismatch = self._scope_error(organization_id, correlation_id, handoff)
        if mismatch is not None:
            return Result.failure(mismatch)
        metadata_error = self._metadata_error(handoff, correlation_id)
        if metadata_error is not None:
            return Result.failure(metadata_error)
        schema_error = self._extension_error(
            handoff,
            correlation_id,
            extension_schema if extension_schema is not None else self._va_extension_schema,
        )
        if schema_error is not None:
            self._append_audit(
                organization_id,
                correlation_id,
                handoff.handoff_id,
                "artifact_handoff.va_extension.blocked",
                "blocked",
            )
            return Result.failure(schema_error)

        availability = ArtifactAvailabilityStatus.PENDING
        return Result.success(
            replace(
                handoff,
                external=external,
                availability=availability,
                metadata_persisted=False,
            )
        )

    def _persist(
        self, handoff: ArtifactHandoff, correlation_id: CorrelationId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        lineage_error = self._validate_lineage(handoff, correlation_id)
        if lineage_error is not None:
            return Result.failure(lineage_error)
        prepared = handoff
        if not handoff.external:
            prepared = replace(
                handoff,
                availability=ArtifactAvailabilityStatus.AVAILABLE,
                metadata_persisted=True,
            )
        return self._append(prepared, correlation_id)

    def _validate_lineage(
        self, handoff: ArtifactHandoff, correlation_id: CorrelationId
    ) -> ErrorDetail | None:
        validate_lineage = getattr(self._repository, "validate_lineage", None)
        if not callable(validate_lineage):
            return None
        validator = cast(Callable[[ArtifactHandoff], Result[bool, ErrorDetail]], validate_lineage)
        lineage_result = validator(handoff)
        if lineage_result.is_success:
            return None
        return self._repository_error(lineage_result.error, correlation_id)

    def _append(
        self, handoff: ArtifactHandoff, correlation_id: CorrelationId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        append_handoff = getattr(self._repository, "append_handoff", None)
        result = (
            append_handoff(handoff)
            if callable(append_handoff)
            else self._repository.append(handoff)
        )
        return self._repository_result(result, correlation_id)

    def _resolve_inputs(
        self,
        organization_or_handoff: OrganizationId | ArtifactHandoff | None,
        handoff: ArtifactHandoff | None,
        organization_id: OrganizationId | None,
        correlation_id: CorrelationId | None,
    ) -> Result[tuple[OrganizationId, CorrelationId, ArtifactHandoff], ErrorDetail]:
        candidate = handoff
        resolved_organization = organization_id
        if isinstance(organization_or_handoff, ArtifactHandoff):
            if candidate is not None:
                return Result.failure(
                    self._validation(CorrelationId("handoff"), "Only one handoff is accepted.")
                )
            candidate = organization_or_handoff
        elif organization_or_handoff is not None:
            resolved_organization = organization_or_handoff
        if candidate is None:
            return Result.failure(
                self._validation(CorrelationId("handoff"), "A handoff is required.")
            )
        resolved_organization = resolved_organization or candidate.metadata.organization_id
        resolved_correlation = correlation_id or candidate.metadata.correlation_id
        return Result.success((resolved_organization, resolved_correlation, candidate))

    @staticmethod
    def _scope_error(
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        handoff: ArtifactHandoff,
    ) -> ErrorDetail | None:
        if handoff.metadata.organization_id != organization_id:
            return ErrorDetail(
                ErrorCode.AUTHORIZATION_DENIED,
                "Artifact handoff is outside the organization scope.",
                correlation_id,
            )
        if handoff.metadata.correlation_id != correlation_id:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff correlation does not match the request.",
                correlation_id,
            )
        return None

    @staticmethod
    def _metadata_error(
        handoff: ArtifactHandoff, correlation_id: CorrelationId
    ) -> ErrorDetail | None:
        required = {
            "artifact_identity": handoff.artifact_identity,
            "artifact_version": handoff.artifact_version,
            "source_task_id": handoff.source_task_id,
            "source_run_reference": handoff.source_run_reference,
            "owner_reference": handoff.owner_reference,
            "classification": handoff.classification,
            "integrity_reference": handoff.integrity_reference,
            "approval_reference": handoff.approval_reference,
            "provenance_reference": handoff.provenance_reference,
        }
        missing = tuple(
            ErrorField(name, "required for Artifact_Handoff persistence")
            for name, value in required.items()
            if value is None or not str(value).strip()
        )
        if missing:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff metadata is incomplete.",
                correlation_id,
                fields=missing,
            )
        return None

    def _extension_error(
        self,
        handoff: ArtifactHandoff,
        correlation_id: CorrelationId,
        schema: ExtensionSchema | None,
    ) -> ErrorDetail | None:
        if schema is None:
            return None
        extension = handoff.technical_specification
        failures = self._schema_failures(schema, extension)
        if failures:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff metadata extension does not match the registered VA schema.",
                correlation_id,
                fields=tuple(
                    ErrorField(field, "registered VA schema requirement") for field in failures
                ),
            )
        return None

    @staticmethod
    def _schema_failures(
        schema: ExtensionSchema, extension: Mapping[str, object] | None
    ) -> tuple[str, ...]:
        if extension is None:
            return ("metadata_extension",)
        if isinstance(schema, Mapping):
            failures: list[str] = []
            for key, expected in schema.items():
                type_mismatch = isinstance(expected, type) and not isinstance(
                    extension.get(key), expected
                )
                value_mismatch = (
                    expected is not None
                    and not isinstance(expected, type)
                    and extension.get(key) != expected
                )
                if key not in extension or type_mismatch or value_mismatch:
                    failures.append(str(key))
            return tuple(failures)
        if isinstance(schema, (set, frozenset, tuple)):
            return tuple(str(key) for key in schema if str(key) not in extension)
        validator = getattr(schema, "validate", None)
        result = (
            validator(extension)
            if callable(validator)
            else schema(extension)
            if callable(schema)
            else False
        )
        if result is None or result is True:
            return ()
        if result is False:
            return ("metadata_extension",)
        if isinstance(result, str):
            return (result,)
        if isinstance(result, (tuple, list, set, frozenset)):
            return tuple(str(item) for item in result)
        return () if bool(result) else ("metadata_extension",)

    def _append_audit(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        handoff_id: ArtifactHandoffId,
        action: str,
        outcome: str,
    ) -> ErrorDetail | None:
        if self._audit_repository is None:
            return ErrorDetail(
                ErrorCode.AUDIT_UNAVAILABLE,
                "Artifact handoff audit storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        now = self._clock()
        audit = AuditRecord(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=f"artifact_handoff:{handoff_id}",
            outcome=outcome,
            recorded_at=now,
        )
        persisted = self._audit_repository.append(audit)
        if persisted.is_success:
            return None
        return self._repository_error(persisted.error, correlation_id)

    @staticmethod
    def _validation(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Artifact handoff storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return replace(error, correlation_id=correlation_id)

    @classmethod
    def _repository_result[T](
        cls, result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        return Result.failure(cls._repository_error(result.error, correlation_id))


HandoffService = ArtifactHandoffService
