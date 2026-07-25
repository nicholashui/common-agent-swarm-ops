"""Integration evidence for the checked-in, data-only ``specials`` pack."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final, cast

import pytest

from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIAL_SOURCE_CATALOG,
    SPECIAL_SOURCE_PATHS,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_SCHEMA_PATH,
    canonical_agent_spec_path,
    canonical_json_bytes,
    sha256_bytes,
    source_for_path,
    validate_specials_pack,
)
from app.video.inventory import (
    EXPECTED_VIDEO_AGENT_COUNT,
    VideoInventoryReport,
    VideoInventoryValidator,
)
from tests.fakes.specials_governance import materialize_specials_governance

# **Validates: Requirements 1.5, 2.2-2.5, 3.5, 4.2-4.3, 6.1-6.5**

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SPECIALS_ROOT: Final[Path] = _REPOSITORY_ROOT / SPECIALS_PACK_ROOT
_VIDEO_ROOT: Final[Path] = _REPOSITORY_ROOT / "business" / "video"
_CONTROLLER_SOURCE_PATH: Final[str] = "docs/special_agents_redesign/agents/controller_agent.md"
_UNTRUSTED_SOURCE_MARKER: Final[bytes] = (
    b"UNTRUSTED_SOURCE_MARKER production_activation_requested=true provider=remote-example"
)


def _load_json(path: Path) -> dict[str, object]:
    """Load one local JSON object fixture."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _write_json(path: Path, value: object) -> None:
    """Write deterministic UTF-8 JSON fixture bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _write_specials_fixture(root: Path) -> tuple[str, ...]:
    """Materialize the exact 19-record pack and its opaque source inputs."""
    schema_path = root / SPECIALS_SCHEMA_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes((_REPOSITORY_ROOT / SPECIALS_SCHEMA_PATH).read_bytes())

    manifest = _load_json(_SPECIALS_ROOT / "manifest.json")
    _write_json(root / SPECIALS_MANIFEST_PATH, manifest)
    allowlisted_paths = [SPECIALS_SCHEMA_PATH, SPECIALS_MANIFEST_PATH]

    for entry in SPECIAL_SOURCE_CATALOG:
        spec_relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(entry.agent_id)}"
        spec_source = _SPECIALS_ROOT / canonical_agent_spec_path(entry.agent_id)
        spec_target = root / spec_relative_path
        spec_target.parent.mkdir(parents=True, exist_ok=True)
        spec_target.write_bytes(spec_source.read_bytes())
        allowlisted_paths.append(spec_relative_path)

    for entry in SPECIAL_SOURCE_CATALOG:
        source_target = root / entry.source_path
        source_target.parent.mkdir(parents=True, exist_ok=True)
        source_bytes = (_REPOSITORY_ROOT / entry.source_path).read_bytes()
        if entry.source_path == _CONTROLLER_SOURCE_PATH:
            source_bytes += b"\n" + _UNTRUSTED_SOURCE_MARKER + b"\n"
        source_target.write_bytes(source_bytes)
        allowlisted_paths.append(entry.source_path)

    return tuple(sorted(materialize_specials_governance(root, allowlisted_paths)))


def _video_snapshot() -> dict[str, str]:
    """Hash the Video_Pack records that this feature must not change."""
    spec_paths = sorted((_VIDEO_ROOT / "agents").glob("*/agent_spec.json"))
    assert len(spec_paths) == EXPECTED_VIDEO_AGENT_COUNT == 114
    paths: list[Path] = [
        _VIDEO_ROOT / "manifest.json",
        _VIDEO_ROOT / "inventory.json",
        *spec_paths,
    ]
    return {
        path.relative_to(_REPOSITORY_ROOT).as_posix(): sha256_bytes(path.read_bytes())
        for path in paths
    }


def _video_validation_behavior() -> VideoInventoryReport:
    """Return the shared Video_Pack validator result for before/after comparison."""
    return VideoInventoryValidator().validate_directory(_VIDEO_ROOT)


def test_pack_schema_and_exact_19_record_fixture_are_data_only(tmp_path: Path) -> None:
    """Validate the local schema, exact catalog, controller mapping, and opaque sources."""
    schema = _load_json(_SPECIALS_ROOT / "schemas" / "special-agent-spec.schema.json")
    definitions = cast(dict[str, object], schema["$defs"])
    canonical_definition = cast(dict[str, object], definitions["CanonicalAgentId"])
    asset_definition = cast(dict[str, object], definitions["SpecialAgentAssetId"])
    properties = cast(dict[str, object], schema["properties"])

    assert schema["$id"] == "special-agent-spec.schema.json"
    assert schema["additionalProperties"] is False
    assert canonical_definition["pattern"] == r"^specials\.[a-z0-9]+(?:-[a-z0-9]+)*$"
    assert asset_definition["pattern"] == r"^spagent\.[a-z0-9]+(?:-[a-z0-9]+)*$"
    assert cast(dict[str, object], properties["agent_id"])["$ref"] == "#/$defs/CanonicalAgentId"
    assert cast(dict[str, object], properties["prompt_reference"])["$ref"] == (
        "#/$defs/SpecialAgentAssetId"
    )

    fixture_root = tmp_path / "specials-pack"
    allowlisted_paths = _write_specials_fixture(fixture_root)
    report = validate_specials_pack(fixture_root, allowlisted_paths)

    assert len(SPECIAL_SOURCE_CATALOG) == 19
    assert len(SPECIAL_AGENT_IDS) == 19
    assert tuple(entry.source_path for entry in SPECIAL_SOURCE_CATALOG) == SPECIAL_SOURCE_PATHS
    assert report.validation_outcome == "pass"
    assert report.accepted_agent_ids == tuple(sorted(SPECIAL_AGENT_IDS))
    assert report.rejected_agent_ids == ()
    assert report.inventory.required is False
    assert report.inventory.result == "not_required"
    assert report.registration_effect == "eligible_draft_representation"
    controller_source = source_for_path(_CONTROLLER_SOURCE_PATH)
    assert controller_source is not None
    assert controller_source.agent_id == "specials.controller-agent"

    report_bytes = report.canonical_bytes()
    assert _UNTRUSTED_SOURCE_MARKER not in report_bytes
    controller_source_bytes = (fixture_root / _CONTROLLER_SOURCE_PATH).read_bytes()
    assert _UNTRUSTED_SOURCE_MARKER in controller_source_bytes
    for agent_id in SPECIAL_AGENT_IDS:
        spec_path = fixture_root / SPECIALS_PACK_ROOT / canonical_agent_spec_path(agent_id)
        assert _UNTRUSTED_SOURCE_MARKER not in spec_path.read_bytes()

    file_paths = {file_result.path for file_result in report.files}
    assert file_paths == set(allowlisted_paths)
    assert _CONTROLLER_SOURCE_PATH in file_paths


def test_schema_rejects_canonical_and_asset_namespace_crossover(tmp_path: Path) -> None:
    """Reject schema examples that exchange canonical IDs and asset references."""
    fixture_root = tmp_path / "specials-schema-crossover"
    allowlisted_paths = _write_specials_fixture(fixture_root)
    spec_relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(SPECIAL_AGENT_IDS[0])}"
    spec_path = fixture_root / spec_relative_path
    spec = _load_json(spec_path)

    spec["prompt_reference"] = "specials.controller-agent"
    _write_json(spec_path, spec)
    report = validate_specials_pack(fixture_root, allowlisted_paths)

    assert report.validation_outcome == "fail"
    assert report.registration_effect == "none"
    assert any(
        finding.code == "NAMESPACE_CROSSOVER" and finding.category == "asset_namespace"
        for finding in report.findings
    )


def test_data_only_allowlist_rejects_unallowlisted_executable_path(tmp_path: Path) -> None:
    """Reject an executable-looking path before it can become pack configuration."""
    fixture_root = tmp_path / "specials-allowlist"
    allowlisted_paths = _write_specials_fixture(fixture_root)
    unsupported_path = "business/specials/workflows/execute.py"
    unsupported_file = fixture_root / unsupported_path
    unsupported_file.parent.mkdir(parents=True, exist_ok=True)
    unsupported_file.write_bytes(b"print('must not be read')\n")

    report = validate_specials_pack(
        fixture_root,
        (*allowlisted_paths, unsupported_path),
    )

    assert report.validation_outcome == "fail"
    assert report.registration_effect == "none"
    assert any(
        finding.code == "UNALLOWLISTED_PATH" and finding.path == unsupported_path
        for finding in report.findings
    )
    assert unsupported_path not in {file_result.path for file_result in report.files}


def test_supported_symlink_containment_rejection_is_fail_closed(tmp_path: Path) -> None:
    """Reject a symlinked agent specification that points outside the repository root."""
    fixture_root = tmp_path / "specials-symlink"
    allowlisted_paths = _write_specials_fixture(fixture_root)
    spec_relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(SPECIAL_AGENT_IDS[0])}"
    symlink_path = fixture_root / spec_relative_path
    outside_path = tmp_path / "outside-agent-spec.json"
    outside_path.write_bytes(symlink_path.read_bytes())
    symlink_path.unlink()
    try:
        os.symlink(outside_path, symlink_path)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"symlink creation is unsupported: {error}")

    report = validate_specials_pack(fixture_root, allowlisted_paths)

    assert report.validation_outcome == "fail"
    assert report.accepted_agent_ids == ()
    assert report.registration_effect == "none"
    assert any(
        finding.code == "SYMLINK_PATH" and finding.path == spec_relative_path
        for finding in report.findings
    )


def test_draft_production_activation_request_is_denied_and_prior_state_retained(
    tmp_path: Path,
) -> None:
    """A draft cannot request production activation or replace accepted state."""
    fixture_root = tmp_path / "specials-draft-activation"
    allowlisted_paths = _write_specials_fixture(fixture_root)
    baseline = validate_specials_pack(fixture_root, allowlisted_paths)
    spec_relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(SPECIAL_AGENT_IDS[0])}"
    spec_path = fixture_root / spec_relative_path
    spec = _load_json(spec_path)
    spec["production_activation_requested"] = True
    _write_json(spec_path, spec)

    report = validate_specials_pack(
        fixture_root,
        allowlisted_paths,
        previous_state=baseline.accepted_state,
    )

    assert baseline.validation_outcome == "pass"
    assert report.validation_outcome == "fail"
    assert report.registration_effect == "none"
    assert report.accepted_agent_ids == ()
    assert report.accepted_state == baseline.accepted_state
    assert any(finding.code == "PRODUCTION_ACTIVATION_REQUESTED" for finding in report.findings)


def test_specials_validation_preserves_video_pack_bytes_and_behavior(tmp_path: Path) -> None:
    """Specials validation must not alter Video_Pack records or validation behavior."""
    before_snapshot = _video_snapshot()
    before_behavior = _video_validation_behavior()
    assert before_behavior.is_valid
    assert len(before_behavior.manifest_agent_ids) == 114
    assert len(before_behavior.inventory_agent_ids) == 114
    assert len(before_behavior.agent_spec_ids) == 114

    fixture_root = tmp_path / "specials-video-isolation"
    report = validate_specials_pack(fixture_root, _write_specials_fixture(fixture_root))
    assert report.validation_outcome == "pass"

    after_snapshot = _video_snapshot()
    after_behavior = _video_validation_behavior()

    assert after_snapshot == before_snapshot
    assert after_behavior == before_behavior
    assert len(after_snapshot) == 2 + EXPECTED_VIDEO_AGENT_COUNT
