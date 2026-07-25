"""Validated archival and deletion lifecycle service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.core.configuration import ConfigurationService, StartupComponent
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId
from app.models.retention import (
    PreservedRetentionEvidence,
    RetentionAction,
    RetentionCategory,
    RetentionOutcome,
    RetentionPolicy,
    RetentionRecord,
    parse_retention_policies,
)

_RETENTION_CORRELATION_ID = CorrelationId("retention")


class RetentionRepository(Protocol):
    """Persistence port that applies one lifecycle transition atomically."""

    def find_expired(
        self, category: RetentionCategory, expired_before: datetime
    ) -> Result[tuple[RetentionRecord, ...], ErrorDetail]:
        """Return active records in the category older than the cutoff."""

    def apply_lifecycle(
        self,
        record: RetentionRecord,
        action: RetentionAction,
        evidence: PreservedRetentionEvidence,
    ) -> Result[bool, ErrorDetail]:
        """Archive/delete and preserve selected evidence in one durable outcome."""


class RetentionService:
    """Apply only schema-validated deployment retention policy."""

    def __init__(
        self,
        configuration_service: ConfigurationService,
        repository: RetentionRepository,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        correlation_id: CorrelationId = _RETENTION_CORRELATION_ID,
    ) -> None:
        self._configuration_service = configuration_service
        self._repository = repository
        self._clock = clock
        self._correlation_id = correlation_id

    def apply_expired(self) -> Result[tuple[RetentionOutcome, ...], ErrorDetail]:
        """Apply configured actions to every currently expired record."""
        configuration = self._configuration_service.validated_configuration
        status = self._configuration_service.status
        if (
            configuration is None
            or status is None
            or not status.is_enabled(StartupComponent.RETENTION)
        ):
            return Result.failure(self._configuration_failure())
        try:
            policies = parse_retention_policies(configuration.retention_policies)
            now = self._timestamp()
        except ValueError:
            return Result.failure(self._configuration_failure())

        outcomes: list[RetentionOutcome] = []
        for policy in policies:
            expired = self._repository.find_expired(
                policy.category, now - timedelta(days=policy.max_age_days)
            )
            if not expired.is_success or expired.value is None:
                return Result.failure(expired.error or self._repository_failure())
            for record in expired.value:
                evidence = self._evidence(record, policy)
                if evidence is None:
                    return Result.failure(self._evidence_failure())
                applied = self._repository.apply_lifecycle(record, policy.action, evidence)
                if not applied.is_success:
                    return Result.failure(applied.error or self._repository_failure())
                outcomes.append(RetentionOutcome(record.record_id, record.category, policy.action))
        return Result.success(tuple(outcomes))

    def _evidence(
        self, record: RetentionRecord, policy: RetentionPolicy
    ) -> PreservedRetentionEvidence | None:
        authorization = (
            record.authorization_evidence if policy.preserve_authorization_evidence else None
        )
        provenance = record.provenance_evidence if policy.preserve_provenance_evidence else None
        if (
            (policy.preserve_authorization_evidence and authorization is None)
            or (policy.preserve_provenance_evidence and provenance is None)
        ):
            return None
        return PreservedRetentionEvidence(authorization, provenance)

    def _timestamp(self) -> datetime:
        timestamp = self._clock()
        if timestamp.tzinfo is None:
            raise ValueError("Retention clocks must return timezone-aware timestamps.")
        return timestamp

    def _configuration_failure(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.CONFIGURATION_INVALID,
            "Retention policy is not validated and cannot be applied.",
            self._correlation_id,
        )

    def _evidence_failure(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "Required retention evidence is unavailable.",
            self._correlation_id,
        )

    def _repository_failure(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "The retention lifecycle could not be applied.",
            self._correlation_id,
            retryable=True,
        )
