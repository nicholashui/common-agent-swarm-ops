"""Validation for explicitly permitted, bounded operational event logs."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Final

from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.identifiers import CorrelationId, new_correlation_id
from app.process_intelligence.models import EventLogRecord, EventLogSet

_IDENTIFIER_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)
_MAX_RECORDS: Final[int] = 10_000
_MAX_TEXT_LENGTH: Final[int] = 250


def canonical_identifier(value: object) -> str | None:
    """Normalize a bounded identifier or return ``None`` when it is unsafe."""
    if not isinstance(value, str):
        return None
    canonical = unicodedata.normalize("NFKC", value).strip().casefold()
    if len(canonical) > 100 or not _IDENTIFIER_PATTERN.fullmatch(canonical):
        return None
    return canonical


class EventLogValidator:
    """Validate only log sets explicitly marked as permitted for ingestion."""

    def validate(
        self,
        raw_log_set: object,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[EventLogSet, ErrorDetail]:
        """Return an immutable log set or a safe, complete validation failure."""
        effective_correlation_id = correlation_id or new_correlation_id()
        if not isinstance(raw_log_set, Mapping):
            return Result.failure(
                self._validation_error(
                    effective_correlation_id,
                    (ErrorField("log_set", "must be a JSON object"),),
                )
            )

        errors: list[ErrorField] = []
        if raw_log_set.get("permitted") is not True:
            errors.append(ErrorField("permitted", "must be explicitly true"))
        log_set_id = self._identifier(raw_log_set.get("log_set_id"), "log_set_id", errors)
        records = self._records(raw_log_set.get("records"), errors)
        if errors:
            return Result.failure(self._validation_error(effective_correlation_id, tuple(errors)))
        return Result.success(EventLogSet(log_set_id=log_set_id, records=tuple(records)))

    def _records(self, raw_records: object, errors: list[ErrorField]) -> list[EventLogRecord]:
        if not isinstance(raw_records, list):
            errors.append(ErrorField("records", "must be a JSON array"))
            return []
        if not 1 <= len(raw_records) <= _MAX_RECORDS:
            errors.append(
                ErrorField("records", f"must contain from 1 through {_MAX_RECORDS} records")
            )

        records: list[EventLogRecord] = []
        record_ids: set[str] = set()
        for index, raw_record in enumerate(raw_records[:_MAX_RECORDS]):
            field = f"records[{index}]"
            if not isinstance(raw_record, Mapping):
                errors.append(ErrorField(field, "must be a JSON object"))
                continue
            record_id = self._identifier(raw_record.get("record_id"), f"{field}.record_id", errors)
            case_id = self._text(raw_record.get("case_id"), f"{field}.case_id", errors)
            activity = self._text(raw_record.get("activity"), f"{field}.activity", errors)
            occurred_at = self._timestamp(
                raw_record.get("occurred_at"), f"{field}.occurred_at", errors
            )
            if record_id:
                if record_id in record_ids:
                    errors.append(ErrorField(f"{field}.record_id", "must be unique in the log set"))
                record_ids.add(record_id)
            records.append(EventLogRecord(record_id, case_id, activity, occurred_at))
        return records

    @staticmethod
    def _identifier(value: object, field: str, errors: list[ErrorField]) -> str:
        canonical = canonical_identifier(value)
        if canonical is None:
            errors.append(ErrorField(field, "must be a valid canonical identifier"))
            return ""
        return canonical

    @staticmethod
    def _text(value: object, field: str, errors: list[ErrorField]) -> str:
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value.strip()) > _MAX_TEXT_LENGTH
        ):
            errors.append(
                ErrorField(
                    field,
                    f"must be non-empty text no longer than {_MAX_TEXT_LENGTH} characters",
                )
            )
            return ""
        return value.strip()

    @staticmethod
    def _timestamp(value: object, field: str, errors: list[ErrorField]) -> datetime:
        if not isinstance(value, str):
            errors.append(ErrorField(field, "must be an ISO-8601 timestamp with an offset"))
            return datetime.min.replace(tzinfo=UTC)
        try:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            errors.append(ErrorField(field, "must be an ISO-8601 timestamp with an offset"))
            return datetime.min.replace(tzinfo=UTC)
        if timestamp.tzinfo is None:
            errors.append(ErrorField(field, "must include a UTC offset"))
            return timestamp.replace(tzinfo=UTC)
        return timestamp

    @staticmethod
    def _validation_error(
        correlation_id: CorrelationId, fields: tuple[ErrorField, ...]
    ) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "Permitted event-log validation failed.",
            correlation_id,
            fields=fields,
        )
