"""Property checks for the breaking public-contract lifecycle gate."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from hypothesis import given, settings, strategies as st

from app.contracts.release import (
    BreakingChangeKind,
    CompatibilityLifecycle,
    ContractReleaseService,
    InMemoryContractLifecycleRepository,
    InMemoryManualRetentionHandoff,
    ReleaseStatus,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


class _StaticOpenApiApplication(FastAPI):
    """Deterministically returns the generated proposed public contract."""

    def __init__(self, document: dict[str, Any]) -> None:
        super().__init__()
        self._document = document

    def openapi(self) -> dict[str, Any]:
        return copy.deepcopy(self._document)


def _clock() -> datetime:
    return _NOW


def _document() -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Property contract", "version": "1.0.0"},
        "paths": {
            "/api/v1/items": {
                "post": {
                    "operationId": "createItem",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Request"}
                            }
                        }
                    },
                    "responses": {"200": {"description": "Created item"}},
                }
            }
        },
        "components": {
            "schemas": {
                "Request": {
                    "type": "object",
                    "properties": {"mode": {"type": "string", "enum": ["standard"]}},
                }
            }
        },
    }


def _documents(
    change: BreakingChangeKind | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    proposed = _document()
    previous = copy.deepcopy(proposed)
    request = previous["components"]["schemas"]["Request"]
    operation = previous["paths"]["/api/v1/items"]["post"]
    if change is BreakingChangeKind.ROUTE_REMOVED:
        previous["paths"]["/api/v1/retired"] = {
            "get": {
                "operationId": "retired",
                "responses": {"200": {"description": "Old"}},
            }
        }
    elif change is BreakingChangeKind.FIELD_REMOVED:
        request["properties"]["legacy"] = {"type": "string"}
    elif change is BreakingChangeKind.INPUT_NARROWED:
        request["properties"]["mode"]["enum"] = ["standard", "extended"]
    elif change is BreakingChangeKind.RESPONSE_MEANING_CHANGED:
        operation["responses"]["200"]["description"] = "Old item response"
    return previous, proposed


def _lifecycle(
    has_replacement: bool,
    has_deprecation: bool,
    has_migration: bool,
    compatibility_passed: bool,
) -> CompatibilityLifecycle:
    return CompatibilityLifecycle(
        replacement_version="v2" if has_replacement else None,
        deprecation_window="2025-01-01/2025-06-01" if has_deprecation else None,
        migration_record="migration-property-2" if has_migration else None,
        compatibility_check_passed=compatibility_passed,
    )


# Feature: backend-redesign, Property 2
# **Validates: Requirements 1.6, 15.2**
@settings(max_examples=100)
@given(
    change=st.sampled_from((None, *BreakingChangeKind)),
    has_replacement=st.booleans(),
    has_deprecation=st.booleans(),
    has_migration=st.booleans(),
    compatibility_passed=st.booleans(),
)
def test_property_02_breaking_contract_lifecycle_gate(
    change: BreakingChangeKind | None,
    has_replacement: bool,
    has_deprecation: bool,
    has_migration: bool,
    compatibility_passed: bool,
) -> None:
    """Breaking diffs publish exactly after all independently required evidence is retained."""
    previous, proposed = _documents(change)
    lifecycle = _lifecycle(
        has_replacement, has_deprecation, has_migration, compatibility_passed
    )
    repository = InMemoryContractLifecycleRepository()
    service = ContractReleaseService(
        _StaticOpenApiApplication(proposed),
        repository,
        InMemoryManualRetentionHandoff(),
        clock=_clock,
    )

    result = service.publish("2.0.0", previous_document=previous, lifecycle=lifecycle)

    expected_to_publish = change is None or lifecycle.is_complete
    assert {breaking_change.kind for breaking_change in result.breaking_changes} == (
        set() if change is None else {change}
    )
    assert result.publication_permitted is expected_to_publish
    assert result.status is (
        ReleaseStatus.PUBLISHED if expected_to_publish else ReleaseStatus.BLOCKED
    )
    assert (result.typed_artifact is not None) is expected_to_publish
    assert repository.releases[-1].lifecycle == lifecycle
