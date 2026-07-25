"""Atomic idempotency reservation and safe response replay for state-changing commands."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
from typing import TypeVar

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import IdempotencyRecord, IdempotencyStatus
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, new_record_id
from app.repositories.control_plane import ControlPlaneUnitOfWork

ResponsePayload = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class IdempotencyOutcome:
    """The retained command response and whether it was replayed."""

    response_payload: ResponsePayload
    response_reference: str
    replayed: bool


def request_digest(operation: str, request: Mapping[str, object]) -> str:
    """Create a stable digest from route-owned command inputs, excluding the key itself."""
    canonical = json.dumps(
        {"operation": operation, "request": request},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]
T = TypeVar("T")


class IdempotencyService:
    """Reserve an actor/key pair and retain a response before reporting command success."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def execute(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        idempotency_key: str,
        digest: str,
        command: Callable[[], Result[ResponsePayload, ErrorDetail]],
    ) -> Result[IdempotencyOutcome, ErrorDetail]:
        """Run a command once or return its stored response for a matching actor/key/digest."""
        if not idempotency_key.strip():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A non-empty idempotency key is required.",
                    correlation_id,
                )
            )

        with self._unit_of_work_factory() as unit_of_work:
            existing = unit_of_work.idempotency.get(
                organization_id, actor_id, idempotency_key
            )
            if existing.is_success:
                record = self._value(existing)
                if record.request_digest != digest:
                    return Result.failure(self._conflict(correlation_id))
                if record.status is not IdempotencyStatus.COMPLETED:
                    return Result.failure(self._conflict(correlation_id))
                assert record.response_reference is not None
                assert record.response_payload is not None
                return Result.success(
                    IdempotencyOutcome(
                        record.response_payload,
                        record.response_reference,
                        replayed=True,
                    )
                )
            if existing.error is None or existing.error.code is not ErrorCode.NOT_FOUND:
                return Result.failure(self._with_correlation(existing.error, correlation_id))

            now = self._clock()
            reserved = IdempotencyRecord(
                metadata=RecordMetadata(
                    record_id=new_record_id(),
                    organization_id=organization_id,
                    correlation_id=correlation_id,
                    schema_version=SCHEMA_VERSION,
                    version=1,
                    created_at=now,
                    updated_at=now,
                ),
                actor_id=actor_id,
                idempotency_key=idempotency_key,
                request_digest=digest,
                status=IdempotencyStatus.RESERVED,
            )
            reservation = unit_of_work.idempotency.reserve(reserved)
            if not reservation.is_success:
                return Result.failure(self._conflict(correlation_id))

            command_result = command()
            if not command_result.is_success:
                unit_of_work.rollback()
                return Result.failure(self._with_correlation(command_result.error, correlation_id))

            response_payload = self._value(command_result)
            response_reference = f"idempotency-response:{reserved.metadata.record_id}"
            completed = replace(
                reserved,
                status=IdempotencyStatus.COMPLETED,
                response_reference=response_reference,
                response_payload=response_payload,
            )
            stored = unit_of_work.idempotency.complete(completed)
            if not stored.is_success:
                unit_of_work.rollback()
                return Result.failure(self._with_correlation(stored.error, correlation_id))
            return Result.success(
                IdempotencyOutcome(response_payload, response_reference, replayed=False)
            )

    @staticmethod
    def _conflict(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.CONFLICT,
            "The idempotency key cannot be reused for a different request.",
            correlation_id,
        )

    @staticmethod
    def _with_correlation(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.INTERNAL_ERROR,
                "Idempotency storage failed.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @staticmethod
    def _value(result: Result[T, ErrorDetail]) -> T:
        assert result.value is not None
        return result.value
