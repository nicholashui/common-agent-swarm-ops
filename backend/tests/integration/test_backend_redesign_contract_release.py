"""Isolated FastAPI integration coverage for the generated-contract lifecycle."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.contracts.release import (
    ContractReleaseService,
    FileContractLifecycleRepository,
    FileManualRetentionHandoff,
    InMemoryContractLifecycleRepository,
    InMemoryManualRetentionHandoff,
    LegacyRouteMetadata,
    ReleaseStatus,
    extract_public_openapi,
)
from app.main import create_app

# **Validates: Requirements 1.4, 1.5, 15.1, 15.3, 15.4**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


class FailingOpenApiApplication(FastAPI):
    """Application that proves generation failures retain no exception details."""

    def openapi(self) -> dict[str, Any]:
        raise RuntimeError("database-password=must-not-be-retained")


def _clock() -> datetime:
    return _NOW


def _mounted_probe_application() -> FastAPI:
    """Mount a concrete public route alongside the implemented control-plane routes."""
    application = create_app()
    router = APIRouter()

    @router.get("/openapi-probe", operation_id="readOpenApiProbe")
    async def read_openapi_probe() -> dict[str, str]:
        return {"source": "mounted-route"}

    application.include_router(router, prefix="/api/v1")
    return application


def test_extracts_openapi_from_mounted_implemented_public_routes() -> None:
    """Mounted public handlers are callable and appear in the generated contract."""
    application = _mounted_probe_application()

    with TestClient(application) as client:
        response = client.get("/api/v1/openapi-probe")

    assert response.status_code == 200
    payload = cast(dict[str, object], response.json())
    assert payload["data"] == {"source": "mounted-route"}
    document = extract_public_openapi(application)
    paths = cast(dict[str, object], document["paths"])
    assert "/api/v1/openapi-probe" in paths
    assert "/api/v1/context" in paths
    probe = cast(dict[str, object], paths["/api/v1/openapi-probe"])
    assert cast(dict[str, object], probe["get"])["operationId"] == "readOpenApiProbe"


def test_generation_failure_records_safe_warning_without_blocking_release() -> None:
    """OpenAPI exceptions result in a stable warning and a permitted publication."""
    repository = InMemoryContractLifecycleRepository()
    service = ContractReleaseService(
        FailingOpenApiApplication(),
        repository,
        InMemoryManualRetentionHandoff(),
        clock=_clock,
    )

    result = service.publish("1.2.0")

    assert result.status is ReleaseStatus.PUBLISHED_WITH_WARNING
    assert result.publication_permitted
    assert result.openapi_document is None
    assert result.typed_artifact is None
    assert [warning.code for warning in repository.warnings] == ["openapi_generation_failed"]
    assert "password" not in repository.warnings[0].message
    assert "database" not in repository.warnings[0].message


def test_changed_mounted_document_regenerates_typed_artifacts(tmp_path: Path) -> None:
    """A changed mounted document atomically replaces both generated artifact files."""
    application = _mounted_probe_application()
    repository = FileContractLifecycleRepository(tmp_path, Path("release"))
    service = ContractReleaseService(
        application,
        repository,
        FileManualRetentionHandoff(tmp_path, Path("manual-retention")),
        artifact_directory=repository.output_directory,
        clock=_clock,
    )
    initial = service.publish("1.0.0")
    assert initial.status is ReleaseStatus.PUBLISHED
    assert initial.openapi_document is not None
    first_artifact = (repository.output_directory / "browser-client-contracts.ts").read_text(
        encoding="utf-8"
    )

    router = APIRouter()

    @router.get("/openapi-revision-two", operation_id="readOpenApiRevisionTwo")
    async def read_openapi_revision_two() -> dict[str, str]:
        return {"revision": "two"}

    application.include_router(router, prefix="/api/v1")
    application.openapi_schema = None
    updated = service.publish("1.0.1", previous_document=initial.openapi_document)

    assert updated.status is ReleaseStatus.PUBLISHED
    assert updated.openapi_document is not None
    updated_paths = cast(dict[str, object], updated.openapi_document["paths"])
    assert "/api/v1/openapi-revision-two" in updated_paths
    artifact_path = repository.output_directory / "browser-client-contracts.ts"
    assert artifact_path.read_text(encoding="utf-8") == updated.typed_artifact
    assert artifact_path.read_text(encoding="utf-8") != first_artifact
    assert '"readOpenApiRevisionTwo"' in artifact_path.read_text(encoding="utf-8")
    written_document = json.loads(
        (repository.output_directory / "openapi.json").read_text(encoding="utf-8")
    )
    assert "/api/v1/openapi-revision-two" in written_document["paths"]


def test_compatibility_mapping_is_retained_then_handed_off_after_sunset() -> None:
    """Supported adapters retain mapping/sunset metadata and retired adapters transfer it."""
    repository = InMemoryContractLifecycleRepository()
    retention = InMemoryManualRetentionHandoff()
    service = ContractReleaseService(create_app(), repository, retention, clock=_clock)

    supported = service.publish("1.0.0")

    assert supported.status is ReleaseStatus.PUBLISHED
    key = ("GET", "/api/v1/workflow-runs/{run_id}/events")
    mapped_route = repository.legacy_routes[key]
    assert mapped_route.supported
    assert mapped_route.canonical_projection == "run.events"
    assert mapped_route.sunset_criteria

    retired = LegacyRouteMetadata(
        method=mapped_route.method,
        route=mapped_route.route,
        canonical_projection=mapped_route.canonical_projection,
        sunset_criteria=mapped_route.sunset_criteria,
        supported=False,
        migration_record="migration-workflow-runs-v2",
    )
    retired_result = service.publish("1.0.1", legacy_routes=(retired,))

    assert retired_result.status is ReleaseStatus.PUBLISHED
    assert repository.legacy_routes[key] == retired
    handoff = retention.records[("GET", retired.route, "migration-workflow-runs-v2")]
    assert handoff.contract_version == "1.0.1"
    assert handoff.route.canonical_projection == "run.events"
    assert handoff.route.sunset_criteria == mapped_route.sunset_criteria
    assert handoff.route.migration_record == "migration-workflow-runs-v2"
