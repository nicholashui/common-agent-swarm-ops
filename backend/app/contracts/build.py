"""Command-line entry point for deterministic public-contract release builds."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from app.contracts.release import (
    CompatibilityLifecycle,
    ContractReleaseService,
    FileContractLifecycleRepository,
    FileManualRetentionHandoff,
    LegacyRouteMetadata,
)
from app.main import create_app


def build_contract_release(
    project_root: Path,
    output_directory: Path,
    manual_retention_directory: Path,
    contract_version: str,
    *,
    previous_document: Mapping[str, object] | None = None,
    lifecycle: CompatibilityLifecycle | None = None,
    legacy_routes: Sequence[LegacyRouteMetadata] = (),
) -> bool:
    """Run one local release build and return whether publication is permitted."""
    repository = FileContractLifecycleRepository(project_root, output_directory)
    handoff = FileManualRetentionHandoff(project_root, manual_retention_directory)
    service = ContractReleaseService(
        create_app(),
        repository,
        handoff,
        artifact_directory=repository.output_directory,
    )
    result = service.publish(
        contract_version,
        previous_document=previous_document,
        lifecycle=lifecycle,
        legacy_routes=legacy_routes,
    )
    return result.publication_permitted


def _json_mapping(path: Path | None) -> Mapping[str, object] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Configured contract JSON must contain an object.")
    return cast(dict[str, object], value)


def _lifecycle(path: Path | None) -> CompatibilityLifecycle | None:
    value = _json_mapping(path)
    if value is None:
        return None
    return CompatibilityLifecycle(
        replacement_version=_optional_string(value.get("replacement_version")),
        deprecation_window=_optional_string(value.get("deprecation_window")),
        migration_record=_optional_string(value.get("migration_record")),
        compatibility_check_passed=value.get("compatibility_check_passed") is True,
    )


def _legacy_routes(path: Path | None) -> tuple[LegacyRouteMetadata, ...]:
    if path is None:
        return ()
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("Legacy route lifecycle JSON must contain an array.")
    routes: list[LegacyRouteMetadata] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Every legacy route lifecycle entry must be an object.")
        routes.append(
            LegacyRouteMetadata(
                method=_required_string(item.get("method"), "method"),
                route=_required_string(item.get("route"), "route"),
                canonical_projection=_required_string(
                    item.get("canonical_projection"), "canonical_projection"
                ),
                sunset_criteria=_required_string(
                    item.get("sunset_criteria"), "sunset_criteria"
                ),
                supported=item.get("supported") is not False,
                migration_record=_optional_string(item.get("migration_record")),
            )
        )
    return tuple(routes)


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and gate Browser_Client contracts.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("build/contracts"))
    parser.add_argument(
        "--manual-retention",
        type=Path,
        default=Path("build/manual-retention"),
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--lifecycle", type=Path)
    parser.add_argument("--legacy-routes", type=Path)
    return parser


def main() -> int:
    """Execute the configured build without exposing exception details in release output."""
    arguments = _parser().parse_args()
    permitted = build_contract_release(
        arguments.project_root,
        arguments.output,
        arguments.manual_retention,
        arguments.version,
        previous_document=_json_mapping(arguments.previous),
        lifecycle=_lifecycle(arguments.lifecycle),
        legacy_routes=_legacy_routes(arguments.legacy_routes),
    )
    print("contract publication permitted" if permitted else "contract publication blocked")
    return 0 if permitted else 2


if __name__ == "__main__":
    raise SystemExit(main())
