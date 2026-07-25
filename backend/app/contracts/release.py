"""Deterministic OpenAPI release, typed-client, and compatibility lifecycle build code."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from threading import RLock
from typing import Protocol, cast

from fastapi import FastAPI

_HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_SAFE_GENERATION_MESSAGE = "OpenAPI generation did not complete; publication continued."


class ReleaseStatus(StrEnum):
    """Observable publication decision for one proposed contract version."""

    PUBLISHED = "published"
    PUBLISHED_WITH_WARNING = "published_with_warning"
    BLOCKED = "blocked"


class BreakingChangeKind(StrEnum):
    """Semantic compatibility classes governed by the publication lifecycle."""

    ROUTE_REMOVED = "route_removed"
    FIELD_REMOVED = "field_removed"
    INPUT_NARROWED = "input_narrowed"
    RESPONSE_MEANING_CHANGED = "response_meaning_changed"


@dataclass(frozen=True, slots=True)
class BreakingChange:
    """One redaction-safe semantic difference between public contracts."""

    kind: BreakingChangeKind
    location: str


@dataclass(frozen=True, slots=True)
class CompatibilityLifecycle:
    """Evidence required before any semantic breaking change may publish."""

    replacement_version: str | None = None
    deprecation_window: str | None = None
    migration_record: str | None = None
    compatibility_check_passed: bool = False

    @property
    def is_complete(self) -> bool:
        """Return whether all four independently required lifecycle facts exist."""
        return all(
            value is not None and value.strip()
            for value in (
                self.replacement_version,
                self.deprecation_window,
                self.migration_record,
            )
        ) and self.compatibility_check_passed


@dataclass(frozen=True, slots=True)
class LegacyRouteMetadata:
    """Documented adapter mapping and its governed support/sunset state."""

    method: str
    route: str
    canonical_projection: str
    sunset_criteria: str
    supported: bool = True
    migration_record: str | None = None

    def __post_init__(self) -> None:
        for value, label in (
            (self.method, "method"),
            (self.route, "route"),
            (self.canonical_projection, "canonical_projection"),
            (self.sunset_criteria, "sunset_criteria"),
        ):
            if not value.strip():
                raise ValueError(f"{label} must be non-empty.")
        if not self.route.startswith("/api/v1/workflow-runs/"):
            raise ValueError("Compatibility mappings are limited to /api/v1/workflow-runs/*.")
        if not self.supported and not (self.migration_record or "").strip():
            raise ValueError("Retired compatibility routes require a migration record.")


@dataclass(frozen=True, slots=True)
class GenerationWarning:
    """A stable safe warning that never contains exception or deployment details."""

    contract_version: str
    code: str
    message: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class ContractReleaseRecord:
    """Persisted evidence for a publication decision and its lifecycle inputs."""

    contract_version: str
    status: ReleaseStatus
    document_digest: str | None
    breaking_changes: tuple[BreakingChange, ...]
    lifecycle: CompatibilityLifecycle
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class ManualRetentionRecord:
    """Metadata transferred after a compatibility adapter ends support."""

    route: LegacyRouteMetadata
    contract_version: str
    transferred_at: datetime


@dataclass(frozen=True, slots=True)
class ReleaseResult:
    """Complete deterministic result returned to release automation."""

    status: ReleaseStatus
    openapi_document: Mapping[str, object] | None
    typed_artifact: str | None
    breaking_changes: tuple[BreakingChange, ...]
    warnings: tuple[GenerationWarning, ...]

    @property
    def publication_permitted(self) -> bool:
        return self.status is not ReleaseStatus.BLOCKED


class ContractLifecycleRepository(Protocol):
    """Append-only persistence port for release, warning, and adapter evidence."""

    def append_warning(self, warning: GenerationWarning) -> None: ...

    def append_release(self, release: ContractReleaseRecord) -> None: ...

    def record_legacy_route(self, route: LegacyRouteMetadata) -> None: ...


class ManualRetentionHandoff(Protocol):
    """Configured long-lived handoff for metadata whose route support ended."""

    def transfer(self, record: ManualRetentionRecord) -> None: ...


class InMemoryContractLifecycleRepository:
    """Deterministic append-only fake used by focused release tests."""

    def __init__(self) -> None:
        self.warnings: list[GenerationWarning] = []
        self.releases: list[ContractReleaseRecord] = []
        self.legacy_routes: dict[tuple[str, str], LegacyRouteMetadata] = {}

    def append_warning(self, warning: GenerationWarning) -> None:
        self.warnings.append(warning)

    def append_release(self, release: ContractReleaseRecord) -> None:
        self.releases.append(release)

    def record_legacy_route(self, route: LegacyRouteMetadata) -> None:
        self.legacy_routes[(route.method.upper(), route.route)] = route


class InMemoryManualRetentionHandoff:
    """Deterministic idempotent manual-retention fake."""

    def __init__(self) -> None:
        self.records: dict[tuple[str, str, str], ManualRetentionRecord] = {}

    def transfer(self, record: ManualRetentionRecord) -> None:
        key = (
            record.route.method.upper(),
            record.route.route,
            record.route.migration_record or "",
        )
        self.records[key] = record


class _JsonLedger:
    """Project-root-confined JSON ledger with atomic local replacement."""

    def __init__(self, project_root: Path, output_directory: Path) -> None:
        root = project_root.resolve()
        output = (
            (root / output_directory).resolve()
            if not output_directory.is_absolute()
            else output_directory.resolve()
        )
        try:
            output.relative_to(root)
        except ValueError as error:
            raise ValueError("Contract outputs must remain within the project root.") from error
        output.mkdir(parents=True, exist_ok=True)
        self.output_directory = output
        self._lock = RLock()

    def append(self, name: str, payload: Mapping[str, object]) -> None:
        target = self.output_directory / name
        with self._lock:
            records: list[object] = []
            if target.exists():
                loaded = json.loads(target.read_text(encoding="utf-8"))
                if not isinstance(loaded, list):
                    raise ValueError("Contract lifecycle ledger must contain a JSON array.")
                records.extend(loaded)
            if payload not in records:
                records.append(dict(payload))
            _atomic_write(target, json.dumps(records, indent=2, sort_keys=True) + "\n")


class FileContractLifecycleRepository:
    """Durable local lifecycle repository for build/release automation."""

    def __init__(self, project_root: Path, output_directory: Path) -> None:
        self._ledger = _JsonLedger(project_root, output_directory)

    @property
    def output_directory(self) -> Path:
        return self._ledger.output_directory

    def append_warning(self, warning: GenerationWarning) -> None:
        self._ledger.append("generation-warnings.json", _warning_payload(warning))

    def append_release(self, release: ContractReleaseRecord) -> None:
        self._ledger.append("contract-releases.json", _release_payload(release))

    def record_legacy_route(self, route: LegacyRouteMetadata) -> None:
        self._ledger.append("legacy-route-lifecycle.json", _legacy_payload(route))


class FileManualRetentionHandoff:
    """Configured durable handoff target for retired compatibility metadata."""

    def __init__(self, project_root: Path, output_directory: Path) -> None:
        self._ledger = _JsonLedger(project_root, output_directory)

    def transfer(self, record: ManualRetentionRecord) -> None:
        payload: dict[str, object] = {
            "contract_version": record.contract_version,
            "transferred_at": record.transferred_at.isoformat(),
            "route": _legacy_payload(record.route),
        }
        self._ledger.append("manual-retention-handoffs.json", payload)


class ContractReleaseService:
    """Publish generated artifacts only after deterministic semantic compatibility checks."""

    def __init__(
        self,
        application: FastAPI,
        repository: ContractLifecycleRepository,
        manual_retention: ManualRetentionHandoff,
        artifact_directory: Path | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._application = application
        self._repository = repository
        self._manual_retention = manual_retention
        self._artifact_directory = artifact_directory
        self._clock = clock or (lambda: datetime.now(UTC))

    def publish(
        self,
        contract_version: str,
        *,
        previous_document: Mapping[str, object] | None = None,
        lifecycle: CompatibilityLifecycle | None = None,
        legacy_routes: Sequence[LegacyRouteMetadata] = (),
    ) -> ReleaseResult:
        """Generate, gate, persist, and optionally write one contract release."""
        if not contract_version.strip():
            raise ValueError("contract_version must be non-empty.")
        evidence = lifecycle or CompatibilityLifecycle()
        now = self._clock()
        configured_routes = tuple(legacy_routes)
        for route in configured_routes:
            self._repository.record_legacy_route(route)

        try:
            document = extract_public_openapi(self._application)
        except Exception:
            warning = GenerationWarning(
                contract_version=contract_version,
                code="openapi_generation_failed",
                message=_SAFE_GENERATION_MESSAGE,
                recorded_at=now,
            )
            self._repository.append_warning(warning)
            self._repository.append_release(
                ContractReleaseRecord(
                    contract_version,
                    ReleaseStatus.PUBLISHED_WITH_WARNING,
                    None,
                    (),
                    evidence,
                    now,
                )
            )
            self._transfer_retired(configured_routes, contract_version, now)
            return ReleaseResult(
                ReleaseStatus.PUBLISHED_WITH_WARNING,
                None,
                None,
                (),
                (warning,),
            )

        discovered_routes = discover_legacy_route_metadata(document)
        routes_by_key = {
            (route.method.upper(), route.route): route for route in discovered_routes
        }
        routes_by_key.update(
            {(route.method.upper(), route.route): route for route in configured_routes}
        )
        routes = tuple(routes_by_key.values())
        for route in routes:
            self._repository.record_legacy_route(route)

        changes = evaluate_breaking_changes(previous_document, document)
        status = (
            ReleaseStatus.BLOCKED
            if changes and not evidence.is_complete
            else ReleaseStatus.PUBLISHED
        )
        digest = _document_digest(document)
        release = ContractReleaseRecord(
            contract_version, status, digest, changes, evidence, now
        )
        self._repository.append_release(release)
        if status is ReleaseStatus.BLOCKED:
            return ReleaseResult(status, document, None, changes, ())

        typed_artifact = generate_browser_client_types(document)
        if self._artifact_directory is not None:
            _write_artifacts(self._artifact_directory, document, typed_artifact)
        self._transfer_retired(routes, contract_version, now)
        return ReleaseResult(status, document, typed_artifact, changes, ())

    def _transfer_retired(
        self,
        routes: Sequence[LegacyRouteMetadata],
        contract_version: str,
        transferred_at: datetime,
    ) -> None:
        for route in routes:
            if not route.supported:
                self._manual_retention.transfer(
                    ManualRetentionRecord(route, contract_version, transferred_at)
                )


def extract_public_openapi(application: FastAPI) -> dict[str, object]:
    """Extract implemented /api/v1 routes and describe middleware-owned envelopes."""
    raw = cast(dict[str, object], application.openapi())
    normalized = cast(dict[str, object], json.loads(json.dumps(raw, allow_nan=False)))
    paths = _mapping(normalized.get("paths"))
    if not paths or any(not path.startswith("/api/v1/") for path in paths):
        raise ValueError("OpenAPI contains a route outside the versioned public API.")
    _apply_public_envelopes(normalized)
    return normalized


def discover_legacy_route_metadata(
    document: Mapping[str, object],
) -> tuple[LegacyRouteMetadata, ...]:
    """Read documented adapter mappings directly from implemented route metadata."""
    routes: list[LegacyRouteMetadata] = []
    for path, path_value in _mapping(document.get("paths")).items():
        if not path.startswith("/api/v1/workflow-runs/"):
            continue
        for method, operation_value in _mapping(path_value).items():
            if method not in _HTTP_METHODS:
                continue
            operation = _mapping(operation_value)
            if operation.get("x-compatibility-adapter") is not True:
                continue
            projection = operation.get("x-canonical-projection")
            sunset = operation.get("x-sunset-criteria")
            if not isinstance(projection, str) or not isinstance(sunset, str):
                raise ValueError("Compatibility adapters require mapping and sunset metadata.")
            routes.append(
                LegacyRouteMetadata(
                    method=method,
                    route=path,
                    canonical_projection=projection,
                    sunset_criteria=sunset,
                )
            )
    return tuple(routes)


def _apply_public_envelopes(document: dict[str, object]) -> None:
    components = _mutable_mapping(document.setdefault("components", {}))
    schemas = _mutable_mapping(components.setdefault("schemas", {}))
    schemas.setdefault(
        "PublicResponseMeta",
        {
            "type": "object",
            "required": ["correlation_id"],
            "properties": {"correlation_id": {"type": "string"}},
        },
    )
    paths = _mutable_mapping(document["paths"])
    for path_item_value in paths.values():
        path_item = _mutable_mapping(path_item_value)
        for method, operation_value in path_item.items():
            if method not in _HTTP_METHODS:
                continue
            operation = _mutable_mapping(operation_value)
            responses = _mutable_mapping(operation.get("responses", {}))
            for status_code, response_value in responses.items():
                if not str(status_code).startswith("2"):
                    continue
                response = _mutable_mapping(response_value)
                content = _mutable_mapping(response.get("content", {}))
                media = content.get("application/json")
                if not isinstance(media, dict):
                    continue
                schema = media.get("schema")
                if not isinstance(schema, dict) or schema.get("x-public-envelope") is True:
                    continue
                media["schema"] = {
                    "type": "object",
                    "required": ["data", "meta"],
                    "x-public-envelope": True,
                    "properties": {
                        "data": schema,
                        "meta": {"$ref": "#/components/schemas/PublicResponseMeta"},
                    },
                }


def evaluate_breaking_changes(
    previous: Mapping[str, object] | None,
    proposed: Mapping[str, object],
) -> tuple[BreakingChange, ...]:
    """Classify route/field removal, accepted-input narrowing, and response meaning changes."""
    if previous is None:
        return ()
    changes: set[BreakingChange] = set()
    old_paths = _mapping(previous.get("paths"))
    new_paths = _mapping(proposed.get("paths"))
    for path, old_path_value in old_paths.items():
        old_path = _mapping(old_path_value)
        new_path = _mapping(new_paths.get(path))
        for method in sorted(_HTTP_METHODS.intersection(old_path)):
            location = f"paths.{path}.{method}"
            if method not in new_path:
                changes.add(BreakingChange(BreakingChangeKind.ROUTE_REMOVED, location))
                continue
            old_operation = _mapping(old_path[method])
            new_operation = _mapping(new_path[method])
            _compare_operation_inputs(location, old_operation, new_operation, changes)
            _compare_response_meaning(
                location,
                old_operation,
                new_operation,
                changes,
            )

    old_schemas = _component_schemas(previous)
    new_schemas = _component_schemas(proposed)
    request_schemas = _request_schema_names(previous)
    for schema_name, old_schema_value in old_schemas.items():
        old_schema = _mapping(old_schema_value)
        new_schema = _mapping(new_schemas.get(schema_name))
        location = f"components.schemas.{schema_name}"
        if not new_schema:
            changes.add(BreakingChange(BreakingChangeKind.FIELD_REMOVED, location))
            continue
        _compare_removed_fields(location, old_schema, new_schema, changes)
        if schema_name in request_schemas:
            _compare_input_narrowing(location, old_schema, new_schema, changes)
    return tuple(sorted(changes, key=lambda change: (change.kind.value, change.location)))


def _compare_operation_inputs(
    location: str,
    old_operation: Mapping[str, object],
    new_operation: Mapping[str, object],
    changes: set[BreakingChange],
) -> None:
    old_body = _request_schema(old_operation)
    new_body = _request_schema(new_operation)
    if old_body and not new_body:
        changes.add(
            BreakingChange(BreakingChangeKind.INPUT_NARROWED, f"{location}.requestBody")
        )
    elif old_body and new_body:
        body_location = f"{location}.requestBody.schema"
        _compare_removed_fields(body_location, old_body, new_body, changes)
        _compare_input_narrowing(body_location, old_body, new_body, changes)

    old_parameters = {
        (parameter.get("in"), parameter.get("name")): parameter
        for parameter in _object_sequence(old_operation.get("parameters"))
    }
    new_parameters = {
        (parameter.get("in"), parameter.get("name")): parameter
        for parameter in _object_sequence(new_operation.get("parameters"))
    }
    for key, old_parameter in old_parameters.items():
        new_parameter = new_parameters.get(key)
        parameter_location = f"{location}.parameters.{key[0]}.{key[1]}"
        if new_parameter is None:
            changes.add(
                BreakingChange(BreakingChangeKind.INPUT_NARROWED, parameter_location)
            )
            continue
        if old_parameter.get("required") is not True and new_parameter.get("required") is True:
            changes.add(
                BreakingChange(BreakingChangeKind.INPUT_NARROWED, parameter_location)
            )
        _compare_input_narrowing(
            parameter_location,
            _mapping(old_parameter.get("schema")),
            _mapping(new_parameter.get("schema")),
            changes,
        )


def _compare_response_meaning(
    location: str,
    old_operation: Mapping[str, object],
    new_operation: Mapping[str, object],
    changes: set[BreakingChange],
) -> None:
    old_responses = _mapping(old_operation.get("responses"))
    new_responses = _mapping(new_operation.get("responses"))
    for status_code, old_response_value in old_responses.items():
        response_location = f"{location}.responses.{status_code}"
        new_response = _mapping(new_responses.get(status_code))
        if not new_response:
            changes.add(
                BreakingChange(BreakingChangeKind.RESPONSE_MEANING_CHANGED, response_location)
            )
            continue
        old_response = _mapping(old_response_value)
        for semantic_key in ("description", "x-response-meaning"):
            old_value = old_response.get(semantic_key)
            if old_value is not None and old_value != new_response.get(semantic_key):
                changes.add(
                    BreakingChange(
                        BreakingChangeKind.RESPONSE_MEANING_CHANGED,
                        f"{response_location}.{semantic_key}",
                    )
                )
        old_schema = _response_schema(old_response)
        new_schema = _response_schema(new_response)
        if old_schema and new_schema:
            _compare_removed_fields(
                f"{response_location}.schema", old_schema, new_schema, changes
            )
        if (
            old_schema
            and new_schema
            and _schema_signature(old_schema) != _schema_signature(new_schema)
            and _schema_shape_changed(old_schema, new_schema)
        ):
            changes.add(
                BreakingChange(
                    BreakingChangeKind.RESPONSE_MEANING_CHANGED,
                    f"{response_location}.schema",
                )
            )


def _compare_removed_fields(
    location: str,
    old_schema: Mapping[str, object],
    new_schema: Mapping[str, object],
    changes: set[BreakingChange],
) -> None:
    old_properties = _mapping(old_schema.get("properties"))
    new_properties = _mapping(new_schema.get("properties"))
    for name, old_property in old_properties.items():
        field_location = f"{location}.properties.{name}"
        if name not in new_properties:
            changes.add(BreakingChange(BreakingChangeKind.FIELD_REMOVED, field_location))
            continue
        _compare_removed_fields(
            field_location,
            _mapping(old_property),
            _mapping(new_properties[name]),
            changes,
        )
    old_items = _mapping(old_schema.get("items"))
    new_items = _mapping(new_schema.get("items"))
    if old_items and new_items:
        _compare_removed_fields(f"{location}.items", old_items, new_items, changes)


def _compare_input_narrowing(
    location: str,
    old_schema: Mapping[str, object],
    new_schema: Mapping[str, object],
    changes: set[BreakingChange],
) -> None:
    old_required = _string_set(old_schema.get("required"))
    new_required = _string_set(new_schema.get("required"))
    for field_name in new_required - old_required:
        changes.add(
            BreakingChange(
                BreakingChangeKind.INPUT_NARROWED,
                f"{location}.required.{field_name}",
            )
        )
    if _constraints_narrowed(old_schema, new_schema):
        changes.add(BreakingChange(BreakingChangeKind.INPUT_NARROWED, location))
    old_properties = _mapping(old_schema.get("properties"))
    new_properties = _mapping(new_schema.get("properties"))
    for name in old_properties.keys() & new_properties.keys():
        _compare_input_narrowing(
            f"{location}.properties.{name}",
            _mapping(old_properties[name]),
            _mapping(new_properties[name]),
            changes,
        )


def _constraints_narrowed(
    old_schema: Mapping[str, object], new_schema: Mapping[str, object]
) -> bool:
    if old_schema.get("type") is not None and old_schema.get("type") != new_schema.get("type"):
        return True
    old_enum = set(_scalar_sequence(old_schema.get("enum")))
    new_enum = set(_scalar_sequence(new_schema.get("enum")))
    if old_enum and new_enum and new_enum < old_enum:
        return True
    for minimum_key in ("minimum", "exclusiveMinimum", "minLength", "minItems"):
        old_value = old_schema.get(minimum_key)
        new_value = new_schema.get(minimum_key)
        if isinstance(new_value, int | float) and (
            not isinstance(old_value, int | float) or new_value > old_value
        ):
            return True
    for maximum_key in ("maximum", "exclusiveMaximum", "maxLength", "maxItems"):
        old_value = old_schema.get(maximum_key)
        new_value = new_schema.get(maximum_key)
        if isinstance(new_value, int | float) and (
            not isinstance(old_value, int | float) or new_value < old_value
        ):
            return True
    old_pattern = old_schema.get("pattern")
    new_pattern = new_schema.get("pattern")
    return isinstance(new_pattern, str) and new_pattern != old_pattern


def _request_schema_names(document: Mapping[str, object]) -> set[str]:
    names: set[str] = set()
    for path_value in _mapping(document.get("paths")).values():
        for method, operation_value in _mapping(path_value).items():
            if method not in _HTTP_METHODS:
                continue
            operation = _mapping(operation_value)
            request_body = _mapping(operation.get("requestBody"))
            for media in _mapping(request_body.get("content")).values():
                names.update(_schema_references(_mapping(media).get("schema")))
            for parameter in _object_sequence(operation.get("parameters")):
                names.update(_schema_references(_mapping(parameter).get("schema")))
    return names


def _schema_references(value: object) -> set[str]:
    references: set[str] = set()
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
            references.add(reference.rsplit("/", 1)[-1])
        for child in value.values():
            references.update(_schema_references(child))
    elif isinstance(value, list):
        for child in value:
            references.update(_schema_references(child))
    return references


def generate_browser_client_types(document: Mapping[str, object]) -> str:
    """Generate deterministic dependency-free TypeScript contracts from OpenAPI."""
    lines = [
        "/* Generated from /api/v1 OpenAPI. Do not edit by hand. */",
        (
            "export type JsonValue = null | boolean | number | string | JsonValue[] | "
            "{ [key: string]: JsonValue };"
        ),
        "",
    ]
    for name, schema in sorted(_component_schemas(document).items()):
        lines.extend(_typescript_schema(name, _mapping(schema)))
        lines.append("")
    lines.append("export interface BrowserClientOperations {")
    for path, path_value in sorted(_mapping(document.get("paths")).items()):
        for method, operation_value in sorted(_mapping(path_value).items()):
            if method not in _HTTP_METHODS:
                continue
            operation = _mapping(operation_value)
            operation_id = operation.get("operationId")
            key = operation_id if isinstance(operation_id, str) else f"{method}:{path}"
            request_type = _operation_request_type(operation)
            responses = _operation_response_types(operation)
            lines.append(f'  "{key}": {{')
            lines.append(f'    method: "{method.upper()}";')
            lines.append(f'    path: "{path}";')
            lines.append(f"    request: {request_type};")
            lines.append(f"    responses: {responses};")
            lines.append("  };")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _typescript_schema(name: str, schema: Mapping[str, object]) -> list[str]:
    identifier = _typescript_identifier(name)
    if schema.get("type") == "object" or isinstance(schema.get("properties"), dict):
        lines = [f"export interface {identifier} {{"]
        required = _string_set(schema.get("required"))
        for field_name, field_schema in sorted(_mapping(schema.get("properties")).items()):
            optional = "" if field_name in required else "?"
            lines.append(
                f'  "{field_name}"{optional}: {_typescript_type(_mapping(field_schema))};'
            )
        if schema.get("additionalProperties") is True:
            lines.append("  [key: string]: JsonValue;")
        lines.append("}")
        return lines
    return [f"export type {identifier} = {_typescript_type(schema)};"]


def _typescript_type(schema: Mapping[str, object]) -> str:
    reference = schema.get("$ref")
    if isinstance(reference, str):
        return _typescript_identifier(reference.rsplit("/", 1)[-1])
    enum_values = _scalar_sequence(schema.get("enum"))
    if enum_values:
        return " | ".join(json.dumps(value) for value in enum_values)
    unions = schema.get("anyOf") or schema.get("oneOf")
    if isinstance(unions, list):
        return " | ".join(_typescript_type(_mapping(item)) for item in unions)
    intersections = schema.get("allOf")
    if isinstance(intersections, list):
        return " & ".join(_typescript_type(_mapping(item)) for item in intersections)
    schema_type = schema.get("type")
    if schema_type == "array":
        return f"Array<{_typescript_type(_mapping(schema.get('items')))}>"
    if schema_type == "object" or isinstance(schema.get("properties"), dict):
        required = _string_set(schema.get("required"))
        fields = []
        for name, value in sorted(_mapping(schema.get("properties")).items()):
            optional = "" if name in required else "?"
            fields.append(f'"{name}"{optional}: {_typescript_type(_mapping(value))}')
        return "{ " + "; ".join(fields) + " }"
    return {
        "boolean": "boolean",
        "integer": "number",
        "number": "number",
        "string": "string",
        "null": "null",
    }.get(str(schema_type), "JsonValue")


def _operation_request_type(operation: Mapping[str, object]) -> str:
    request_body = _mapping(operation.get("requestBody"))
    content = _mapping(request_body.get("content"))
    media = _mapping(content.get("application/json"))
    schema = _mapping(media.get("schema"))
    return _typescript_type(schema) if schema else "undefined"


def _operation_response_types(operation: Mapping[str, object]) -> str:
    response_fields: list[str] = []
    for status_code, response_value in sorted(_mapping(operation.get("responses")).items()):
        schema = _response_schema(_mapping(response_value))
        response_fields.append(
            f'"{status_code}": {_typescript_type(schema) if schema else "undefined"}'
        )
    return "{ " + "; ".join(response_fields) + " }"


def _typescript_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_$]", "_", value)
    if not identifier or identifier[0].isdigit():
        identifier = f"Contract_{identifier}"
    return identifier


def _request_schema(operation: Mapping[str, object]) -> Mapping[str, object]:
    request_body = _mapping(operation.get("requestBody"))
    content = _mapping(request_body.get("content"))
    media = _mapping(content.get("application/json"))
    return _mapping(media.get("schema"))


def _response_schema(response: Mapping[str, object]) -> Mapping[str, object]:
    content = _mapping(response.get("content"))
    media = _mapping(content.get("application/json"))
    return _mapping(media.get("schema"))


def _schema_signature(schema: Mapping[str, object]) -> str:
    return json.dumps(schema, sort_keys=True, separators=(",", ":"), default=str)


def _schema_shape_changed(
    old_schema: Mapping[str, object], new_schema: Mapping[str, object]
) -> bool:
    for key in ("$ref", "type", "format", "enum", "oneOf", "anyOf", "allOf"):
        if old_schema.get(key) != new_schema.get(key):
            return True
    return False


def _component_schemas(document: Mapping[str, object]) -> Mapping[str, object]:
    return _mapping(_mapping(document.get("components")).get("schemas"))


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        return {}
    return cast(dict[str, object], value)


def _mutable_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("OpenAPI structure is invalid.")
    return cast(dict[str, object], value)


def _object_sequence(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(_mapping(item) for item in value if isinstance(item, dict))


def _scalar_sequence(value: object) -> tuple[str | int | float | bool | None, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(
        item for item in value if item is None or isinstance(item, str | int | float | bool)
    )


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _document_digest(document: Mapping[str, object]) -> str:
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_artifacts(
    directory: Path, document: Mapping[str, object], typed_artifact: str
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _atomic_write(
        directory / "openapi.json",
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
    )
    _atomic_write(directory / "browser-client-contracts.ts", typed_artifact)


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _warning_payload(warning: GenerationWarning) -> dict[str, object]:
    return {
        "contract_version": warning.contract_version,
        "code": warning.code,
        "message": warning.message,
        "recorded_at": warning.recorded_at.isoformat(),
    }


def _release_payload(release: ContractReleaseRecord) -> dict[str, object]:
    return {
        "contract_version": release.contract_version,
        "status": release.status.value,
        "document_digest": release.document_digest,
        "breaking_changes": [
            {"kind": change.kind.value, "location": change.location}
            for change in release.breaking_changes
        ],
        "lifecycle": asdict(release.lifecycle),
        "recorded_at": release.recorded_at.isoformat(),
    }


def _legacy_payload(route: LegacyRouteMetadata) -> dict[str, object]:
    return {
        "method": route.method.upper(),
        "route": route.route,
        "canonical_projection": route.canonical_projection,
        "sunset_criteria": route.sunset_criteria,
        "supported": route.supported,
        "migration_record": route.migration_record,
    }
