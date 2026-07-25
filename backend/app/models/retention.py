"""Typed retention policy and lifecycle records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType


class RetentionCategory(StrEnum):
    """Operational record categories governed by deployment retention policy."""

    OPERATIONAL_EVENTS = "operational_events"
    AUDIT_RECORDS = "audit_records"
    TRACES = "traces"
    ARTIFACTS = "artifacts"
    APPROVALS = "approvals"
    IDEMPOTENCY_RECORDS = "idempotency_records"
    FAILED_WORK_ITEMS = "failed_work_items"


class RetentionAction(StrEnum):
    """Allowed terminal actions for an expired active record."""

    ARCHIVE = "archive"
    DELETE = "delete"


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    """Validated lifecycle policy for one durable record category."""

    category: RetentionCategory
    max_age_days: int
    action: RetentionAction
    preserve_authorization_evidence: bool
    preserve_provenance_evidence: bool

    @classmethod
    def from_mapping(
        cls, category: str, value: Mapping[str, object]
    ) -> RetentionPolicy:
        """Parse a deployment mapping without accepting ambiguous policy fields."""
        required_fields = {
            "max_age_days",
            "action",
            "preserve_authorization_evidence",
            "preserve_provenance_evidence",
        }
        if set(value) != required_fields:
            raise ValueError("Retention policy fields are incomplete or unsupported.")
        max_age_days = value["max_age_days"]
        preserve_authorization = value["preserve_authorization_evidence"]
        preserve_provenance = value["preserve_provenance_evidence"]
        if (
            not isinstance(max_age_days, int)
            or isinstance(max_age_days, bool)
            or max_age_days < 1
            or not isinstance(preserve_authorization, bool)
            or not isinstance(preserve_provenance, bool)
        ):
            raise ValueError("Retention policy values are invalid.")
        try:
            parsed_category = RetentionCategory(category)
            action = RetentionAction(str(value["action"]))
        except ValueError as exception:
            raise ValueError("Retention category or action is invalid.") from exception
        return cls(
            parsed_category,
            max_age_days,
            action,
            preserve_authorization,
            preserve_provenance,
        )


@dataclass(frozen=True, slots=True)
class RetentionRecord:
    """Adapter-neutral retained record and its preservation evidence."""

    record_id: str
    category: RetentionCategory
    created_at: datetime
    authorization_evidence: Mapping[str, object] | None = None
    provenance_evidence: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise ValueError("Retention records require an identifier.")
        if self.created_at.tzinfo is None:
            raise ValueError("Retention record timestamps must be timezone-aware.")
        for name in ("authorization_evidence", "provenance_evidence"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, MappingProxyType(dict(value)))


@dataclass(frozen=True, slots=True)
class PreservedRetentionEvidence:
    """Evidence retained independently from an expired source record."""

    authorization: Mapping[str, object] | None
    provenance: Mapping[str, object] | None


@dataclass(frozen=True, slots=True)
class RetentionOutcome:
    """Safe lifecycle result containing identifiers and policy action only."""

    record_id: str
    category: RetentionCategory
    action: RetentionAction


def parse_retention_policies(
    values: Mapping[str, object],
) -> tuple[RetentionPolicy, ...]:
    """Validate and parse every configured retention policy."""
    if not values:
        raise ValueError("At least one retention policy is required.")
    policies: list[RetentionPolicy] = []
    for category, raw_policy in values.items():
        if not isinstance(category, str) or not isinstance(raw_policy, Mapping):
            raise ValueError("Retention policies must be category mappings.")
        policies.append(RetentionPolicy.from_mapping(category, raw_policy))
    return tuple(sorted(policies, key=lambda policy: policy.category.value))
