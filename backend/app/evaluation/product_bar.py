"""Independent, local Product-Bar evidence assessment.

Passing command results are retained as evidence only; they do not establish proof.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from string import hexdigits

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvaluationRunId,
    EvidenceId,
    OrganizationId,
    RunId,
    new_record_id,
)
from app.repositories.protocols import ProductBarEvidenceRepository


class ProductBarCriterion(StrEnum):
    """Named, independently evidenced Product-Bar capabilities."""

    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"
    E6 = "E6"
    E7 = "E7"
    E8 = "E8"
    E9 = "E9"


class ProductBarEvidenceOutcome(StrEnum):
    """Observed result of one Product-Bar evidence record."""

    PASS = "pass"
    FAIL = "fail"


class ProductBarStatus(StrEnum):
    """Evidence-based completeness status, never a proof claim."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class ProductBarCommandResult:
    """Digest-only result of a local validation command."""

    command: str
    exit_code: int
    output_digest: str
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class ProductBarEvidenceRecord:
    """Append-only local evidence for exactly one Product-Bar criterion."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    criterion: ProductBarCriterion
    outcome: ProductBarEvidenceOutcome
    run_ids: tuple[RunId, ...]
    evaluation_run_ids: tuple[EvaluationRunId, ...]
    evidence_hashes: tuple[str, ...]
    command_results: tuple[ProductBarCommandResult, ...]
    supporting_references: tuple[EvidenceReference, ...]
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class ProductBarAssessmentEntry:
    """Independent pass/fail summary for one named Product-Bar capability."""

    criterion: ProductBarCriterion
    outcome: ProductBarEvidenceOutcome
    evidence_ids: tuple[EvidenceId, ...]


@dataclass(frozen=True, slots=True)
class ProductBarAssessment:
    """A current local evidence summary for all named Product-Bar capabilities."""

    organization_id: OrganizationId
    assessed_at: datetime
    status: ProductBarStatus
    entries: tuple[ProductBarAssessmentEntry, ...]


class ProductBarEvidenceService:
    """Records local evidence and computes a conservative Product-Bar status."""

    def __init__(
        self,
        repository: ProductBarEvidenceRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def record_evidence(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        criterion: ProductBarCriterion,
        outcome: ProductBarEvidenceOutcome,
        *,
        run_ids: tuple[RunId, ...] = (),
        evaluation_run_ids: tuple[EvaluationRunId, ...] = (),
        evidence_hashes: tuple[str, ...],
        command_results: tuple[ProductBarCommandResult, ...] = (),
        supporting_references: tuple[EvidenceReference, ...] = (),
    ) -> Result[ProductBarEvidenceRecord, ErrorDetail]:
        """Append one criterion-specific record containing only local evidence metadata."""
        validation_error = self._validate_sources(run_ids, evaluation_run_ids, evidence_hashes)
        if validation_error is not None:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, validation_error, correlation_id)
            )
        if any(
            not command_result.command.strip()
            or not self._is_sha256(command_result.output_digest)
            for command_result in command_results
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Command results require a command and SHA-256 output digest.",
                    correlation_id,
                )
            )
        timestamp = self._clock()
        record = ProductBarEvidenceRecord(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            evidence_id=EvidenceId(str(new_record_id())),
            criterion=criterion,
            outcome=outcome,
            run_ids=run_ids,
            evaluation_run_ids=evaluation_run_ids,
            evidence_hashes=evidence_hashes,
            command_results=command_results,
            supporting_references=supporting_references,
            recorded_at=timestamp,
        )
        persisted = self._repository.append(record)
        if persisted.is_success:
            if persisted.value is None:
                raise RuntimeError("Successful Product-Bar persistence had no record.")
            return Result.success(persisted.value)
        return Result.failure(self._repository_error(persisted.error, correlation_id))

    def assess(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> Result[ProductBarAssessment, ErrorDetail]:
        """Return every E1-E9 summary; a missing E1 pass is always incomplete."""
        records_result = self._repository.list_for_organization(organization_id)
        if not records_result.is_success:
            return Result.failure(self._repository_error(records_result.error, correlation_id))
        if records_result.value is None:
            raise RuntimeError("Successful Product-Bar retrieval had no records.")
        entries = tuple(
            self._assessment_entry(criterion, records_result.value)
            for criterion in ProductBarCriterion
        )
        status = (
            ProductBarStatus.COMPLETE
            if all(entry.outcome is ProductBarEvidenceOutcome.PASS for entry in entries)
            else ProductBarStatus.INCOMPLETE
        )
        return Result.success(
            ProductBarAssessment(
                organization_id=organization_id,
                assessed_at=self._clock(),
                status=status,
                entries=entries,
            )
        )

    @staticmethod
    def _assessment_entry(
        criterion: ProductBarCriterion,
        records: tuple[ProductBarEvidenceRecord, ...],
    ) -> ProductBarAssessmentEntry:
        matching_records = tuple(record for record in records if record.criterion is criterion)
        has_pass = any(
            record.outcome is ProductBarEvidenceOutcome.PASS for record in matching_records
        )
        outcome = (
            ProductBarEvidenceOutcome.PASS if has_pass else ProductBarEvidenceOutcome.FAIL
        )
        return ProductBarAssessmentEntry(
            criterion=criterion,
            outcome=outcome,
            evidence_ids=tuple(record.evidence_id for record in matching_records),
        )

    @classmethod
    def _validate_sources(
        cls,
        run_ids: tuple[RunId, ...],
        evaluation_run_ids: tuple[EvaluationRunId, ...],
        evidence_hashes: tuple[str, ...],
    ) -> str | None:
        if not run_ids and not evaluation_run_ids:
            return "Product-Bar evidence requires a local run or evaluation ID."
        if any(not source_id.strip() for source_id in (*run_ids, *evaluation_run_ids)):
            return "Product-Bar evidence IDs must be non-empty."
        if not evidence_hashes or not all(cls._is_sha256(digest) for digest in evidence_hashes):
            return "Product-Bar evidence requires SHA-256 hashes."
        return None

    @staticmethod
    def _is_sha256(value: str) -> bool:
        return len(value) == 64 and all(character in hexdigits for character in value)

    @staticmethod
    def _repository_error(
        error: RepositoryError | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Product-Bar evidence storage failed.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )
