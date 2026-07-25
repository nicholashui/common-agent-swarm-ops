"""Property checks for validation before public request and import effects."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import cast
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID

from fastapi import Request
from hypothesis import given, settings, strategies as st
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
    ScanDisposition,
    ScanResult,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord, ImportScanState
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ImportRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-15-organization")
_OTHER_ORGANIZATION = OrganizationId("property-15-other-organization")
_CORRELATION = CorrelationId("property-15-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)
_REQUEST_CASES = st.sampled_from(
    ("valid", "size", "media_type", "route", "pagination", "filter", "rate")
)
_IMPORT_CASES = st.sampled_from(
    ("valid", "owner", "size", "declared_type", "checksum", "storage_name", "detected_type")
)


@dataclass
class _ImportRepositorySpy:
    records: dict[ImportId, ImportRecord] = field(default_factory=dict)

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        self.records[record.import_id] = record
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
class _StorageSpy:
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
class _DetectorSpy:
    detected_type: str
    calls: int = 0

    def detect(self, content: bytes) -> str:
        self.calls += 1
        return self.detected_type


def _metadata(organization_id: OrganizationId, value: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(f"property-15-record-{value}"),
        organization_id=organization_id,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _request(
    *,
    path: str,
    query_pairs: list[tuple[str, str]],
    content_type: str,
    declared_size: int | None = None,
) -> Request:
    body = b'{"request":"safe"}'

    async def receive() -> Message:
        return {"type": "http.request", "body": body, "more_body": False}

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": urlencode(query_pairs).encode(),
        "headers": [
            (b"content-type", content_type.encode()),
            (
                b"content-length",
                str(declared_size if declared_size is not None else len(body)).encode(),
            ),
        ],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 80),
        "root_path": "",
    }
    return Request(scope, receive)


async def _submit_to_handler(guard: IngressGuard, request: Request, effects: list[str]) -> None:
    await guard.validate_request(request)
    effects.append("handler")


def _request_guard() -> IngressGuard:
    return IngressGuard(
        IngressPolicy(
            max_request_bytes=64,
            allowed_media_types=frozenset({"application/json"}),
            max_route_segment_length=12,
            max_page_size=3,
            max_page_offset=5,
            max_page_number=2,
            max_filter_count=2,
            max_filter_length=8,
            endpoint_rate_limits={"/api/v1": 1},
            rate_window_seconds=60,
        ),
        EndpointRateLimiter(clock=lambda: 0.0),
    )


def _submission(value: str, import_case: str) -> ImportSubmission:
    valid_content = f'{{"entry":"{value}"}}'.encode()
    content = b"x" * 65 if import_case == "size" else valid_content
    checksum = hashlib.sha256(content).hexdigest()
    if import_case == "checksum":
        checksum = "0" * 64
    metadata_organization = _OTHER_ORGANIZATION if import_case == "owner" else _ORGANIZATION
    return ImportSubmission(
        metadata=_metadata(metadata_organization, value),
        import_id=ImportId(f"property-15-import-{value}"),
        storage_name="../unsafe.json" if import_case == "storage_name" else f" Safe {value}.JSON ",
        declared_type=(
            "application/x-unsafe" if import_case == "declared_type" else "application/json"
        ),
        checksum=checksum,
        content=content,
    )


# Feature: backend-redesign, Property 15
# **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    request_case=_REQUEST_CASES,
    import_case=_IMPORT_CASES,
    page_size=st.integers(min_value=1, max_value=3),
    offset=st.integers(min_value=0, max_value=5),
    page=st.integers(min_value=1, max_value=2),
    filters=st.lists(_SAFE_VALUES, min_size=0, max_size=2),
    scan_disposition=st.sampled_from(tuple(ScanDisposition)),
)
def test_property_15_ingress_and_import_validation_precedes_effects(
    value: str,
    request_case: str,
    import_case: str,
    page_size: int,
    offset: int,
    page: int,
    filters: list[str],
    scan_disposition: ScanDisposition,
) -> None:
    """Only inputs satisfying every guard can reach handlers, storage, or opaque references."""
    query_pairs = [
        ("limit", str(page_size)),
        ("offset", str(offset)),
        ("page", str(page)),
        ("page_size", str(page_size)),
        *(("filter", filter_value) for filter_value in filters),
    ]
    path = "/api/v1/imports"
    content_type = "application/json"
    declared_size: int | None = None
    if request_case == "size":
        declared_size = 65
    elif request_case == "media_type":
        content_type = "text/plain"
    elif request_case == "route":
        path = f"/api/v1/{'x' * 13}"
    elif request_case == "pagination":
        query_pairs[0] = ("limit", "0")
    elif request_case == "filter":
        query_pairs.append(("filter", "x" * 9))

    effects: list[str] = []
    guard = _request_guard()
    request = _request(
        path=path,
        query_pairs=query_pairs,
        content_type=content_type,
        declared_size=declared_size,
    )
    if request_case == "rate":
        asyncio.run(_submit_to_handler(guard, request, effects))
        request = _request(
            path=path,
            query_pairs=query_pairs,
            content_type=content_type,
            declared_size=declared_size,
        )

    try:
        asyncio.run(_submit_to_handler(guard, request, effects))
    except PublicApiException as error:
        assert request_case != "valid"
        assert error.error.code in {
            ErrorCode.VALIDATION_FAILED.value,
            ErrorCode.RATE_LIMITED.value,
        }
        assert effects == (["handler"] if request_case == "rate" else [])
    else:
        assert request_case == "valid"
        assert effects == ["handler"]

    repository = _ImportRepositorySpy()
    storage = _StorageSpy()
    detector = _DetectorSpy("text/plain" if import_case == "detected_type" else "application/json")
    submission = _submission(value, import_case)
    policy = ImportPolicy(
        max_import_bytes=64,
        allowed_media_types=frozenset({"application/json", "text/plain"}),
        scanning_enabled=True,
        configured_scanners=frozenset({"property-scanner"}),
    )
    with patch("app.core.ingress.uuid4", return_value=UUID(int=15)):
        import_guard = ImportGuard(
            cast(ImportRepository, repository),
            cast(ImportStorage, storage),
            policy=policy,
            detector=cast(ContentTypeDetector, detector),
        )
        accepted = import_guard.accept(_ORGANIZATION, submission)

        if import_case != "valid":
            assert not accepted.is_success and accepted.error is not None
            assert repository.records == {}
            assert storage.quarantined == []
            assert storage.released == []
            assert storage.discarded == []
            assert detector.calls == (1 if import_case == "detected_type" else 0)
            return

        assert accepted.is_success and accepted.value is not None
        stored = accepted.value
        reference = "import:00000000-0000-0000-0000-00000000000f"
        assert stored.scan_state is ImportScanState.QUARANTINED
        assert stored.normalized_storage_name == f"safe-{value}.json"
        assert stored.opaque_storage_reference == reference
        assert list(repository.records.values()) == [stored]
        assert storage.quarantined == [(_ORGANIZATION, reference, submission.content)]
        assert storage.released == []
        assert storage.discarded == []
        assert detector.calls == 1
        assert not import_guard.authorized_reference(_ORGANIZATION, stored.import_id).is_success

        scanned = import_guard.record_scan_result(
            _ORGANIZATION,
            stored.import_id,
            ScanResult("property-scanner", scan_disposition),
        )
        assert scanned.is_success and scanned.value is not None
        if scan_disposition is ScanDisposition.ALLOWED:
            assert scanned.value.scan_state is ImportScanState.ALLOWED
            assert storage.released == [(_ORGANIZATION, reference)]
            opaque_reference = import_guard.authorized_reference(_ORGANIZATION, stored.import_id)
            assert opaque_reference.is_success and opaque_reference.value == reference
        else:
            assert scanned.value.scan_state is ImportScanState.REJECTED
            assert scanned.value.opaque_storage_reference is None
            assert storage.discarded == [(_ORGANIZATION, reference)]
            assert not import_guard.authorized_reference(_ORGANIZATION, stored.import_id).is_success
