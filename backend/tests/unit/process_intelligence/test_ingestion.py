"""Deterministic target-confined process-artifact ingestion checks."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.core.boundary import WorkspaceBoundary
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.process_intelligence.models import (
    ProcessArtifact,
    ProcessArtifactDraft,
    ProcessArtifactKind,
)
from app.process_intelligence.repository import RootConfinedProcessArtifactRepository
from app.process_intelligence.service import ProcessIntelligenceService

CORRELATION_ID = CorrelationId("corr-process-ingestion")
ORGANIZATION_ID = OrganizationId("ops")
TIMESTAMP = "2025-01-01T12:00:00+00:00"


def _repository(tmp_path: Path) -> tuple[RootConfinedProcessArtifactRepository, Path]:
    target_workspace = tmp_path / "target"
    target_workspace.mkdir()
    repository = RootConfinedProcessArtifactRepository(
        WorkspaceBoundary(target_workspace, reference_workspace=None)
    )
    return repository, target_workspace


def _permitted_log_set() -> dict[str, object]:
    return {
        "permitted": True,
        "log_set_id": "ops-log-2025",
        "records": [
            {
                "record_id": "event-1",
                "case_id": "case-1",
                "activity": "Intake",
                "occurred_at": TIMESTAMP,
            },
            {
                "record_id": "event-2",
                "case_id": "case-1",
                "activity": "Review",
                "occurred_at": TIMESTAMP,
            },
        ],
    }


def test_permitted_logs_persist_traceable_artifacts_only_under_business_root(
    tmp_path: Path,
) -> None:
    """Every persisted artifact has its log-set ID and actual supporting record references."""
    repository, target_workspace = _repository(tmp_path)
    service = ProcessIntelligenceService(repository)
    drafts = (
        ProcessArtifactDraft(
            ProcessArtifactKind.DISCOVERED_PROCESS,
            ("event-1",),
            {"activities": ["Intake"]},
        ),
        ProcessArtifactDraft(
            ProcessArtifactKind.BOTTLENECK,
            ("event-1", "event-2"),
            {"activity": "Review"},
        ),
    )

    result = service.ingest(
        _permitted_log_set(),
        drafts,
        organization_id=ORGANIZATION_ID,
        correlation_id=CORRELATION_ID,
    )

    assert result.is_success
    assert result.value is not None
    artifacts = result.value
    assert [artifact.source_log_set_id for artifact in artifacts] == ["ops-log-2025"] * 2
    assert artifacts[0].supporting_record_refs == ("event-1",)
    assert artifacts[1].supporting_record_refs == ("event-1", "event-2")
    assert repository.artifact_root == (
        target_workspace / "business" / "process-intelligence" / "artifacts"
    )
    persisted_paths = tuple(repository.artifact_root.glob("*.json"))
    assert all(path.is_relative_to(repository.artifact_root) for path in persisted_paths)

    persisted_payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(repository.artifact_root.glob("*.json"))
    ]
    assert {payload["artifact_id"] for payload in persisted_payloads} == {
        artifact.metadata.record_id for artifact in artifacts
    }
    assert {payload["source_log_set_id"] for payload in persisted_payloads} == {"ops-log-2025"}
    assert {tuple(payload["supporting_record_refs"]) for payload in persisted_payloads} == {
        ("event-1",),
        ("event-1", "event-2"),
    }


def test_unpermitted_log_is_rejected_before_creating_artifact_storage(tmp_path: Path) -> None:
    """A source must explicitly opt in to ingestion before any artifact is written."""
    repository, _ = _repository(tmp_path)
    service = ProcessIntelligenceService(repository)
    unpermitted_log_set = _permitted_log_set()
    unpermitted_log_set["permitted"] = False

    result = service.ingest(
        unpermitted_log_set,
        (
            ProcessArtifactDraft(
                ProcessArtifactKind.CONFORMANCE,
                ("event-1",),
                {"status": "conformant"},
            ),
        ),
        correlation_id=CORRELATION_ID,
    )

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert any(field.name == "permitted" for field in result.error.fields)
    assert not repository.artifact_root.exists()


def test_unknown_supporting_record_is_rejected_without_persisting_artifacts(tmp_path: Path) -> None:
    """Artifact references must resolve to records in the permitted source log set."""
    repository, _ = _repository(tmp_path)
    service = ProcessIntelligenceService(repository)

    result = service.ingest(
        _permitted_log_set(),
        (
            ProcessArtifactDraft(
                ProcessArtifactKind.CAUSAL_HYPOTHESIS,
                ("unknown-event",),
                {"hypothesis": "Review capacity is constrained"},
            ),
        ),
        correlation_id=CORRELATION_ID,
    )

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert any(
        field.name == "artifact_drafts[0].supporting_record_refs[0]"
        for field in result.error.fields
    )
    assert not repository.artifact_root.exists()


def test_repository_rejects_a_caller_controlled_artifact_path_outside_its_root(
    tmp_path: Path,
) -> None:
    """Persistence cannot use an unsafe record ID to escape the artifacts directory."""
    repository, target_workspace = _repository(tmp_path)
    timestamp = datetime(2025, 1, 1, tzinfo=UTC)
    unsafe_artifact = ProcessArtifact(
        metadata=RecordMetadata(
            record_id=RecordId("../outside"),
            organization_id=ORGANIZATION_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        ),
        kind=ProcessArtifactKind.CONFORMANCE,
        source_log_set_id="ops-log-2025",
        supporting_record_refs=("event-1",),
        output={"status": "conformant"},
    )

    result = repository.persist(unsafe_artifact)

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert not (target_workspace / "business" / "process-intelligence" / "outside.json").exists()
