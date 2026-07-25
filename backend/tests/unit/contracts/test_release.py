"""Focused tests for generated public-contract release lifecycle code."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from app.contracts.release import (
    BreakingChangeKind,
    CompatibilityLifecycle,
    ContractReleaseService,
    FileContractLifecycleRepository,
    FileManualRetentionHandoff,
    InMemoryContractLifecycleRepository,
    InMemoryManualRetentionHandoff,
    LegacyRouteMetadata,
    ReleaseStatus,
    discover_legacy_route_metadata,
    evaluate_breaking_changes,
    extract_public_openapi,
    generate_browser_client_types,
)
from app.main import create_app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


class BrokenOpenApiApplication(FastAPI):
    """Application whose schema generation fails with a sensitive internal detail."""

    def openapi(self) -> dict[str, Any]:
        raise RuntimeError("database-password=must-not-be-retained")


def _clock() -> datetime:
    return _NOW


def test_extracts_only_implemented_public_routes_and_generates_enveloped_types() -> None:
    document = extract_public_openapi(create_app())

    paths = document["paths"]
    assert isinstance(paths, dict)
    assert paths and all(path.startswith("/api/v1/") for path in paths)
    response_schema = paths["/api/v1/context"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert response_schema["x-public-envelope"] is True
    assert response_schema["required"] == ["data", "meta"]

    adapters = discover_legacy_route_metadata(document)
    assert {(adapter.method, adapter.canonical_projection) for adapter in adapters} == {
        ("post", "run.dispatch-command"),
        ("get", "run.detail"),
        ("get", "run.graph-state"),
        ("get", "run.events"),
    }
    artifact = generate_browser_client_types(document)
    assert "export interface BrowserClientOperations" in artifact
    assert 'path: "/api/v1/workflow-runs/{run_id}"' in artifact
    assert "PublicResponseMeta" in artifact


def test_generation_failure_retains_only_safe_warning_and_permits_publication() -> None:
    repository = InMemoryContractLifecycleRepository()
    retention = InMemoryManualRetentionHandoff()
    service = ContractReleaseService(
        BrokenOpenApiApplication(), repository, retention, clock=_clock
    )

    result = service.publish("1.2.0")

    assert result.status is ReleaseStatus.PUBLISHED_WITH_WARNING
    assert result.publication_permitted
    assert result.openapi_document is None
    assert len(repository.warnings) == 1
    warning = repository.warnings[0]
    assert warning.code == "openapi_generation_failed"
    assert "password" not in warning.message
    assert repository.releases[0].status is ReleaseStatus.PUBLISHED_WITH_WARNING


def test_breaking_changes_require_all_lifecycle_evidence_before_publication() -> None:
    application = create_app()
    proposed = extract_public_openapi(application)
    previous = copy.deepcopy(proposed)
    paths = previous["paths"]
    assert isinstance(paths, dict)
    paths["/api/v1/retired"] = {
        "get": {
            "operationId": "retired",
            "responses": {"200": {"description": "Old meaning"}},
        }
    }
    repository = InMemoryContractLifecycleRepository()
    service = ContractReleaseService(
        application, repository, InMemoryManualRetentionHandoff(), clock=_clock
    )

    blocked = service.publish("2.0.0", previous_document=previous)
    published = service.publish(
        "2.0.0",
        previous_document=previous,
        lifecycle=CompatibilityLifecycle(
            replacement_version="v2",
            deprecation_window="2025-01-01/2025-06-01",
            migration_record="migration-17",
            compatibility_check_passed=True,
        ),
    )

    assert blocked.status is ReleaseStatus.BLOCKED
    assert blocked.typed_artifact is None
    assert {change.kind for change in blocked.breaking_changes} == {
        BreakingChangeKind.ROUTE_REMOVED
    }
    assert published.status is ReleaseStatus.PUBLISHED
    assert published.typed_artifact is not None


def test_semantic_diff_detects_removed_fields_narrowed_input_and_response_meaning() -> None:
    previous: dict[str, object] = {
        "paths": {
            "/api/v1/items": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Request"}
                            }
                        }
                    },
                    "responses": {"200": {"description": "Original meaning"}},
                }
            }
        },
        "components": {
            "schemas": {
                "Request": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "mode": {"type": "string", "enum": ["a", "b"]},
                    },
                }
            }
        },
    }
    proposed = copy.deepcopy(previous)
    paths = proposed["paths"]
    components = proposed["components"]
    assert isinstance(paths, dict) and isinstance(components, dict)
    operation = paths["/api/v1/items"]["post"]
    assert isinstance(operation, dict)
    operation["responses"]["200"]["description"] = "Different meaning"
    schemas = components["schemas"]
    assert isinstance(schemas, dict)
    schemas["Request"] = {
        "type": "object",
        "required": ["mode"],
        "properties": {"mode": {"type": "string", "enum": ["a"]}},
    }

    changes = evaluate_breaking_changes(previous, proposed)

    assert {change.kind for change in changes} == {
        BreakingChangeKind.FIELD_REMOVED,
        BreakingChangeKind.INPUT_NARROWED,
        BreakingChangeKind.RESPONSE_MEANING_CHANGED,
    }


def test_file_release_persists_artifacts_lifecycle_and_retired_route_handoff(
    tmp_path: Path,
) -> None:
    release_directory = Path("release")
    repository = FileContractLifecycleRepository(tmp_path, release_directory)
    retention = FileManualRetentionHandoff(tmp_path, Path("manual-retention"))
    retired = LegacyRouteMetadata(
        method="GET",
        route="/api/v1/workflow-runs/{run_id}/events",
        canonical_projection="run.events",
        sunset_criteria="The configured migration window has elapsed.",
        supported=False,
        migration_record="migration-events-v2",
    )
    service = ContractReleaseService(
        create_app(),
        repository,
        retention,
        artifact_directory=repository.output_directory,
        clock=_clock,
    )

    result = service.publish("1.0.0", legacy_routes=(retired,))

    assert result.status is ReleaseStatus.PUBLISHED
    assert (tmp_path / "release" / "openapi.json").is_file()
    assert (tmp_path / "release" / "browser-client-contracts.ts").is_file()
    legacy = json.loads(
        (tmp_path / "release" / "legacy-route-lifecycle.json").read_text("utf-8")
    )
    assert any(record["supported"] is False for record in legacy)
    handoffs = json.loads(
        (tmp_path / "manual-retention" / "manual-retention-handoffs.json").read_text(
            "utf-8"
        )
    )
    assert handoffs[0]["route"]["migration_record"] == "migration-events-v2"
