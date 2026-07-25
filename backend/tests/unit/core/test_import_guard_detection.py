"""Focused import guard regression checks."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import cast

from app.core.ingress import (
    ContentTypeDetector,
    ImportGuard,
    ImportStorage,
    ImportSubmission,
)
from app.models.common import RecordMetadata
from app.models.contracts import RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ImportRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-a")


class _Repository:
    def __init__(self) -> None:
        self.records: list[ImportRecord] = []

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, RepositoryError]:
        self.records.append(record)
        return Result.success(record)


class _Storage:
    def __init__(self) -> None:
        self.quarantined: list[tuple[OrganizationId, str, bytes]] = []

    def quarantine(self, organization_id: OrganizationId, reference: str, content: bytes) -> None:
        self.quarantined.append((organization_id, reference, content))

    def release(self, organization_id: OrganizationId, reference: str) -> None:
        raise AssertionError("Scanning is enabled, so an accepted import remains quarantined.")

    def discard(self, organization_id: OrganizationId, reference: str) -> None:
        raise AssertionError("Persistence does not fail in this focused test.")


class _ChangingDetector:
    def __init__(self) -> None:
        self.calls = 0

    def detect(self, content: bytes) -> str:
        self.calls += 1
        return "application/json" if self.calls == 1 else "text/plain"


def test_import_guard_persists_the_single_detected_type_it_validated() -> None:
    """A non-deterministic detector cannot alter metadata after validation."""
    content = b'{"safe": true}'
    metadata = RecordMetadata(
        record_id=RecordId("import-record"),
        organization_id=_ORGANIZATION,
        correlation_id=CorrelationId("import-correlation"),
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )
    submission = ImportSubmission(
        metadata=metadata,
        import_id=ImportId("import-a"),
        storage_name="Safe Import.json",
        declared_type="application/json",
        checksum=hashlib.sha256(content).hexdigest(),
        content=content,
    )
    repository = _Repository()
    storage = _Storage()
    detector = _ChangingDetector()

    result = ImportGuard(
        cast(ImportRepository, repository),
        cast(ImportStorage, storage),
        detector=cast(ContentTypeDetector, detector),
    ).accept(_ORGANIZATION, submission)

    assert result.is_success and result.value is not None
    assert detector.calls == 1
    assert result.value.detected_type == "application/json"
    assert len(repository.records) == len(storage.quarantined) == 1


def test_import_guard_rejects_invalid_checksum_before_detection_or_storage() -> None:
    """Cheap invalid metadata must prevent detector invocation and storage effects."""
    content = b'{"safe": true}'
    submission = ImportSubmission(
        metadata=RecordMetadata(
            record_id=RecordId("invalid-import-record"),
            organization_id=_ORGANIZATION,
            correlation_id=CorrelationId("invalid-import-correlation"),
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        import_id=ImportId("invalid-import"),
        storage_name="Safe Import.json",
        declared_type="application/json",
        checksum="0" * 64,
        content=content,
    )
    repository = _Repository()
    storage = _Storage()
    detector = _ChangingDetector()

    result = ImportGuard(
        cast(ImportRepository, repository),
        cast(ImportStorage, storage),
        detector=cast(ContentTypeDetector, detector),
    ).accept(_ORGANIZATION, submission)

    assert not result.is_success
    assert detector.calls == 0
    assert repository.records == []
    assert storage.quarantined == []
