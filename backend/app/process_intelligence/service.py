"""Ingest permitted event logs into root-confined, traceable process artifacts."""

from __future__ import annotations

import json
from collections.abc import Sequence

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.identifiers import CorrelationId, OrganizationId, new_correlation_id, new_record_id
from app.process_intelligence.models import (
    EventLogSet,
    ProcessArtifact,
    ProcessArtifactDraft,
)
from app.process_intelligence.repository import RootConfinedProcessArtifactRepository
from app.process_intelligence.validation import EventLogValidator, canonical_identifier


class ProcessIntelligenceService:
    """Create artifacts only from permitted logs and their validated record references."""

    def __init__(
        self,
        repository: RootConfinedProcessArtifactRepository,
        validator: EventLogValidator | None = None,
    ) -> None:
        self._repository = repository
        self._validator = validator or EventLogValidator()

    def ingest(
        self,
        raw_log_set: object,
        artifact_drafts: Sequence[ProcessArtifactDraft],
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[tuple[ProcessArtifact, ...], ErrorDetail]:
        """Validate every source and draft before persisting any derived artifact."""
        effective_correlation_id = correlation_id or new_correlation_id()
        log_set_result = self._validator.validate(
            raw_log_set, correlation_id=effective_correlation_id
        )
        if log_set_result.error is not None:
            return Result.failure(log_set_result.error)
        assert log_set_result.value is not None
        errors, normalized_drafts = self._validate_drafts(
            log_set_result.value, artifact_drafts
        )
        if errors:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Process-artifact derivation validation failed.",
                    effective_correlation_id,
                    fields=tuple(errors),
                )
            )
        return self._persist(
            log_set_result.value,
            normalized_drafts,
            organization_id or OrganizationId("host"),
            effective_correlation_id,
        )

    def _validate_drafts(
        self,
        log_set: EventLogSet,
        artifact_drafts: Sequence[ProcessArtifactDraft],
    ) -> tuple[list[ErrorField], tuple[ProcessArtifactDraft, ...]]:
        errors: list[ErrorField] = []
        if not artifact_drafts:
            errors.append(ErrorField("artifact_drafts", "must contain at least one artifact"))
            return errors, ()

        known_record_ids = {record.record_id for record in log_set.records}
        normalized_drafts: list[ProcessArtifactDraft] = []
        for index, draft in enumerate(artifact_drafts):
            field = f"artifact_drafts[{index}]"
            normalized_refs = self._supporting_refs(
                draft.supporting_record_refs, field, known_record_ids, errors
            )
            output = dict(draft.output)
            try:
                json.dumps(output, ensure_ascii=True, allow_nan=False, sort_keys=True)
            except (TypeError, ValueError):
                errors.append(
                    ErrorField(f"{field}.output", "must contain JSON-serializable values")
                )
            normalized_drafts.append(
                ProcessArtifactDraft(draft.kind, normalized_refs, output)
            )
        return errors, tuple(normalized_drafts)

    @staticmethod
    def _supporting_refs(
        raw_refs: tuple[str, ...],
        field: str,
        known_record_ids: set[str],
        errors: list[ErrorField],
    ) -> tuple[str, ...]:
        if not raw_refs:
            errors.append(ErrorField(f"{field}.supporting_record_refs", "must not be empty"))
            return ()
        normalized_refs: list[str] = []
        for ref_index, raw_ref in enumerate(raw_refs):
            normalized = canonical_identifier(raw_ref)
            ref_field = f"{field}.supporting_record_refs[{ref_index}]"
            if normalized is None:
                errors.append(ErrorField(ref_field, "must be a valid record identifier"))
                continue
            if normalized not in known_record_ids:
                errors.append(
                    ErrorField(
                        ref_field,
                        "must reference a record in the source log set",
                    )
                )
                continue
            if normalized in normalized_refs:
                errors.append(ErrorField(ref_field, "must not duplicate a supporting record"))
                continue
            normalized_refs.append(normalized)
        return tuple(normalized_refs)

    def _persist(
        self,
        log_set: EventLogSet,
        drafts: tuple[ProcessArtifactDraft, ...],
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> Result[tuple[ProcessArtifact, ...], ErrorDetail]:
        persisted_artifacts: list[ProcessArtifact] = []
        for draft in drafts:
            timestamp = utc_now()
            artifact = ProcessArtifact(
                metadata=RecordMetadata(
                    record_id=new_record_id(),
                    organization_id=organization_id,
                    correlation_id=correlation_id,
                    schema_version=SCHEMA_VERSION,
                    version=1,
                    created_at=timestamp,
                    updated_at=timestamp,
                ),
                kind=draft.kind,
                source_log_set_id=log_set.log_set_id,
                supporting_record_refs=draft.supporting_record_refs,
                output=draft.output,
            )
            persisted_result = self._repository.persist(artifact)
            if persisted_result.error is not None:
                return Result.failure(persisted_result.error)
            assert persisted_result.value is not None
            persisted_artifacts.append(persisted_result.value)
        return Result.success(tuple(persisted_artifacts))
