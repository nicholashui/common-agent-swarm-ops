"""Focused fail-complete checks for the untrusted-content boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import count
from typing import cast

import pytest

from app.core.ingress import (
    GuardedUntrustedContent,
    ProhibitedInfluence,
    ProtectionOutcome,
    SecurityIndicator,
    UntrustedContent,
    UntrustedContentGuard,
    UntrustedContentSource,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord, SecurityEvidence
from app.models.identifiers import CorrelationId, OrganizationId, RecordId

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-a")
_CORRELATION = CorrelationId("correlation-a")


def _metadata() -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId("untrusted-record"),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


class _EvidenceRepository:
    def __init__(self, *, fail: bool = False) -> None:
        self.evidence: list[SecurityEvidence] = []
        self.fail = fail

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import persistence is not used by this guard.")

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import replacement is not used by this guard.")

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, RepositoryError]:
        raise AssertionError("Import lookup is not used by this guard.")

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, RepositoryError]:
        if self.fail:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Security evidence could not be retained.",
                    record.metadata.correlation_id,
                )
            )
        self.evidence.append(record)
        return Result.success(record)


@dataclass(slots=True)
class _Protection:
    protection_id: str
    outcome: ProtectionOutcome
    raises: bool = False
    calls: int = 0

    def inspect(self, content: UntrustedContent) -> ProtectionOutcome:
        self.calls += 1
        if self.raises:
            raise RuntimeError("raw detector detail must not escape")
        return self.outcome


def _guard(
    repository: _EvidenceRepository, protections: tuple[_Protection, ...]
) -> UntrustedContentGuard:
    identifiers = count(1)
    return UntrustedContentGuard(
        repository,
        protections,
        clock=lambda: _NOW,
        evidence_id_factory=lambda: f"evidence-{next(identifiers)}",
    )


def test_every_configured_protection_must_pass_before_immutable_continuation() -> None:
    """All protections run and successful content remains immutable non-authoritative data."""
    repository = _EvidenceRepository()
    first = _Protection("prompt-injection", ProtectionOutcome(True))
    second = _Protection("content-policy", ProtectionOutcome(True))
    source_payload: dict[str, object] = {"message": ["safe data"]}
    content = UntrustedContent(
        metadata=_metadata(),
        source=UntrustedContentSource.RETRIEVAL,
        payload=source_payload,
    )
    source_payload["message"] = ["mutated after snapshot"]

    result = _guard(repository, (first, second)).process(content)

    assert result.is_success and isinstance(result.value, GuardedUntrustedContent)
    assert first.calls == second.calls == 1
    assert repository.evidence == []
    payload = cast(Mapping[str, object], result.value.payload)
    assert payload["message"] == ("safe data",)
    assert not hasattr(result.value, "selected_tool")
    assert not hasattr(result.value, "authority")
    assert not hasattr(result.value, "policy")
    with pytest.raises(TypeError):
        cast(dict[str, object], payload)["message"] = "changed"


def test_every_prohibited_influence_fails_complete_and_records_only_safe_codes() -> None:
    """Authority, tool, policy, validation, and privileged instructions yield no continuation."""
    repository = _EvidenceRepository()
    protection = _Protection("baseline", ProtectionOutcome(True))
    content = UntrustedContent(
        metadata=_metadata(),
        source=UntrustedContentSource.MODEL_OUTPUT,
        payload={"raw_prompt": "token=top-secret"},
        influence_attempts=frozenset(ProhibitedInfluence),
    )

    result = _guard(repository, (protection,)).process(content)

    assert not result.is_success and result.value is None
    assert result.error is not None and result.error.code is ErrorCode.VALIDATION_FAILED
    assert protection.calls == 1
    assert {item.indicator for item in repository.evidence} == {
        SecurityIndicator.AUTHORITY_INFLUENCE.value,
        SecurityIndicator.TOOL_SELECTION.value,
        SecurityIndicator.POLICY_MUTATION.value,
        SecurityIndicator.VALIDATION_BYPASS.value,
        SecurityIndicator.PRIVILEGED_INSTRUCTION.value,
    }
    assert all(item.protection == "untrusted-boundary" for item in repository.evidence)
    assert "top-secret" not in repr(repository.evidence)
    assert all(not item.passed for item in repository.evidence)


def test_security_indicators_and_detector_errors_fail_after_all_protections_run() -> None:
    """Configured detections and indeterminate detector failures both deny continuation."""
    repository = _EvidenceRepository()
    indicators = tuple(
        (
            SecurityIndicator.PROMPT_INJECTION,
            SecurityIndicator.PROHIBITED_CONTENT,
            SecurityIndicator.SUSPICIOUS_TOOL_PROPOSAL,
            SecurityIndicator.ARTIFACT_MANIFEST_MISMATCH,
        )
    )
    detected = _Protection("configured-policy", ProtectionOutcome(False, indicators))
    broken = _Protection("manifest-check", ProtectionOutcome(True), raises=True)
    final = _Protection("final-check", ProtectionOutcome(True))
    content = UntrustedContent(
        metadata=_metadata(),
        source=UntrustedContentSource.THIRD_PARTY,
        payload="Bearer raw-sensitive-token",
    )

    result = _guard(repository, (detected, broken, final)).process(content)

    assert not result.is_success and result.value is None
    assert detected.calls == broken.calls == final.calls == 1
    assert {item.indicator for item in repository.evidence} == {
        *(indicator.value for indicator in indicators),
        SecurityIndicator.PROTECTION_ERROR.value,
    }
    assert "raw-sensitive-token" not in repr(repository.evidence)
    assert "raw detector detail" not in repr(repository.evidence)


def test_security_evidence_persistence_failure_still_returns_no_continuation() -> None:
    """An unavailable evidence store cannot turn a rejected protection into success."""
    repository = _EvidenceRepository(fail=True)
    rejected = _Protection("content-policy", ProtectionOutcome(False))
    later = _Protection("later-check", ProtectionOutcome(True))
    content = UntrustedContent(
        metadata=_metadata(),
        source=UntrustedContentSource.UPLOAD,
        payload=b"untrusted bytes",
    )

    result = _guard(repository, (rejected, later)).process(content)

    assert not result.is_success and result.value is None
    assert rejected.calls == later.calls == 1
    assert result.error is not None
    assert result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert repository.evidence == []
