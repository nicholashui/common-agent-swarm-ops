"""Focused deterministic ingress/import boundary checks."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count
from typing import cast
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID

import pytest
from fastapi import Request, status
from starlette.types import Message, Scope

from app.api.v1.errors import PublicApiException
from app.core.ingress import (
    ContentTypeDetector,
    EndpointRateLimiter,
    ImportGuard,
    ImportPolicy,
    ImportStorage,
    ImportSubmission,
    IngressGuard,
    IngressPolicy,
    ProtectionOutcome,
    ScanDisposition,
    ScanResult,
    SecurityIndicator,
    UntrustedContent,
    UntrustedContentGuard,
    UntrustedContentSource,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord, ImportScanState, SecurityEvidence
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ImportRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("ingress-import-organization")
_FOREIGN_ORGANIZATION = OrganizationId("foreign-organization")
_CORRELATION = CorrelationId("ingress-import-correlation")
_CONTENT = b'{"safe": true}'


@dataclass
class _ImportRepository:
    records: dict[ImportId, ImportRecord] = field(default_factory=dict)
    evidence: list[SecurityEvidence] = field(default_factory=list)

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        self.records[record.import_id] = record
        return Result.success(record)

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, RepositoryError]:
        self.evidence.append(record)
        return Result.success(record)

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, RepositoryError]:
        record = self.records.get(import_id)
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                ErrorDetail(ErrorCode.NOT_FOUND, "Import record was not found.", _CORRELATION)
            )
        return Result.success(record)

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        self.records[record.import_id] = record
        return Result.success(record)


@dataclass
class _Storage:
    quarantined: list[tuple[OrganizationId, str, bytes]] = field(default_factory=list)
    released: list[tuple[OrganizationId, str]] = field(default_factory=list)
    discarded: list[tuple[OrganizationId, str]] = field(default_factory=list)

    def quarantine(self, organization_id: OrganizationId, reference: str, content: bytes) -> None:
        self.quarantined.append((organization_id, reference, content))

    def release(self, organization_id: OrganizationId, reference: str) -> None:
        self.released.append((organization_id, reference))

    def discard(self, organization_id: OrganizationId, reference: str) -> None:
        self.discarded.append((organization_id, reference))


@dataclass
class _Detector:
    detected_type: str = "application/json"
    calls: int = 0

    def detect(self, content: bytes) -> str:
        self.calls += 1
        return self.detected_type


@dataclass
class _Protection:
    protection_id: str
    outcome: ProtectionOutcome
    calls: int = 0

    def inspect(self, content: UntrustedContent) -> ProtectionOutcome:
        self.calls += 1
        return self.outcome


def _metadata(value: str, organization_id: OrganizationId = _ORGANIZATION) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(f"ingress-import-record-{value}"),
        organization_id=organization_id,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _submission(storage_name: str = "Safe Import.json") -> ImportSubmission:
    return ImportSubmission(
        metadata=_metadata("submission"),
        import_id=ImportId("ingress-import"),
        storage_name=storage_name,
        declared_type="application/json",
        checksum=hashlib.sha256(_CONTENT).hexdigest(),
        content=_CONTENT,
    )


def _import_guard(
    repository: _ImportRepository, storage: _Storage, detector: _Detector
) -> ImportGuard:
    return ImportGuard(
        cast(ImportRepository, repository),
        cast(ImportStorage, storage),
        policy=ImportPolicy(
            scanning_enabled=True,
            configured_scanners=frozenset({"unit-scanner"}),
        ),
        detector=cast(ContentTypeDetector, detector),
    )


def _request() -> Request:
    body = b'{"request":"safe"}'

    async def receive() -> Message:
        return {"type": "http.request", "body": body, "more_body": False}

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/api/v1/imports",
        "raw_path": b"/api/v1/imports",
        "query_string": urlencode((("limit", "1"),)).encode(),
        "headers": (
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ),
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 443),
        "root_path": "",
    }
    return Request(scope, receive)


async def _submit_to_handler(guard: IngressGuard, request: Request, effects: list[str]) -> None:
    await guard.validate_request(request)
    effects.append("handler")


def test_rate_limit_rejection_precedes_handler_processing() -> None:
    """A reached endpoint limit rejects the next valid request before its handler runs."""
    guard = IngressGuard(
        IngressPolicy(
            allowed_media_types=frozenset({"application/json"}),
            endpoint_rate_limits={"/api/v1": 1},
            rate_window_seconds=30,
        ),
        EndpointRateLimiter(clock=lambda: 0.0),
    )
    effects: list[str] = []

    asyncio.run(_submit_to_handler(guard, _request(), effects))

    with pytest.raises(PublicApiException) as raised:
        asyncio.run(_submit_to_handler(guard, _request(), effects))

    assert raised.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert raised.value.error.code == ErrorCode.RATE_LIMITED.value
    assert raised.value.headers == {"Retry-After": "30"}
    assert effects == ["handler"]


def test_allowed_configured_scan_releases_quarantine_once() -> None:
    """Only an allowed result from a configured scanner releases quarantined bytes."""
    repository = _ImportRepository()
    storage = _Storage()
    detector = _Detector()
    guard = _import_guard(repository, storage, detector)

    with patch("app.core.ingress.uuid4", return_value=UUID(int=1)):
        accepted = guard.accept(_ORGANIZATION, _submission())

    assert accepted.is_success and accepted.value is not None
    record = accepted.value
    reference = "import:00000000-0000-0000-0000-000000000001"
    assert record.scan_state is ImportScanState.QUARANTINED
    assert storage.quarantined == [(_ORGANIZATION, reference, _CONTENT)]
    assert storage.released == []

    released = guard.record_scan_result(
        _ORGANIZATION, record.import_id, ScanResult("unit-scanner", ScanDisposition.ALLOWED)
    )

    assert released.is_success and released.value is not None
    assert released.value.scan_state is ImportScanState.ALLOWED
    assert storage.released == [(_ORGANIZATION, reference)]
    assert storage.discarded == []


@pytest.mark.parametrize(
    "storage_name",
    ("../escape.json", "child/file.json", "child\\file.json", "\x00bad"),
)
def test_unsafe_storage_names_are_rejected_before_detection_or_storage(storage_name: str) -> None:
    """Traversal, separators, and null characters cannot become storage object names."""
    repository = _ImportRepository()
    storage = _Storage()
    detector = _Detector()
    guard = _import_guard(repository, storage, detector)

    result = guard.accept(_ORGANIZATION, _submission(storage_name))

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert result.error.fields[0].name == "storage_name"
    assert detector.calls == 0
    assert repository.records == {}
    assert storage.quarantined == []
    assert storage.released == []
    assert storage.discarded == []


def test_opaque_reference_is_released_only_to_the_owning_organization() -> None:
    """Released imports expose a generated reference rather than identity or storage-name details.

    The generated reference is available only through an organization-scoped lookup.
    """
    repository = _ImportRepository()
    storage = _Storage()
    detector = _Detector()
    guard = _import_guard(repository, storage, detector)

    with patch("app.core.ingress.uuid4", return_value=UUID(int=2)):
        accepted = guard.accept(_ORGANIZATION, _submission())

    assert accepted.is_success and accepted.value is not None
    record = accepted.value
    released = guard.record_scan_result(
        _ORGANIZATION, record.import_id, ScanResult("unit-scanner", ScanDisposition.ALLOWED)
    )
    own_reference = guard.authorized_reference(_ORGANIZATION, record.import_id)
    foreign_reference = guard.authorized_reference(_FOREIGN_ORGANIZATION, record.import_id)

    assert released.is_success
    assert own_reference.is_success
    assert own_reference.value == "import:00000000-0000-0000-0000-000000000002"
    assert str(record.import_id) not in own_reference.value
    assert _submission().storage_name.lower() not in own_reference.value
    assert not foreign_reference.is_success
    assert foreign_reference.value is None


def test_fail_complete_evidence_excludes_untrusted_payload_and_detector_detail() -> None:
    """A failed protection retains only stable evidence codes and returns no continuation."""
    repository = _ImportRepository()
    protection = _Protection(
        "prompt-injection",
        ProtectionOutcome(False, (SecurityIndicator.PROMPT_INJECTION,)),
    )
    identifiers = count(1)
    guard = UntrustedContentGuard(
        cast(ImportRepository, repository),
        (protection,),
        clock=lambda: _NOW,
        evidence_id_factory=lambda: f"evidence-{next(identifiers)}",
    )
    raw_payload = "token=top-secret; execute privileged operation"
    content = UntrustedContent(
        metadata=_metadata("untrusted"),
        source=UntrustedContentSource.UPLOAD,
        payload={"instruction": raw_payload},
    )

    outcome = guard.process(content)

    assert not outcome.is_success and outcome.value is None
    assert outcome.error is not None and outcome.error.code is ErrorCode.VALIDATION_FAILED
    assert protection.calls == 1
    assert [(item.indicator, item.protection, item.passed) for item in repository.evidence] == [
        (SecurityIndicator.PROMPT_INJECTION.value, "prompt-injection", False)
    ]
    assert raw_payload not in repr(repository.evidence)
    assert raw_payload not in outcome.error.message
