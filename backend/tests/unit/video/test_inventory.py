"""Focused examples for the data-only Video_Pack inventory validator."""

from __future__ import annotations

import json
from pathlib import Path

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT, VideoInventoryValidator


def _video_root() -> Path:
    return Path(__file__).resolve().parents[4] / "business" / "video"


def _load_asset(name: str) -> dict[str, object]:
    parsed: object = json.loads((_video_root() / name).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _load_agent_specs() -> dict[str, object]:
    agent_specs: dict[str, object] = {}
    for spec_path in sorted((_video_root() / "agents").glob("*/agent_spec.json")):
        parsed: object = json.loads(spec_path.read_text(encoding="utf-8"))
        agent_specs[spec_path.parent.name] = parsed
    return agent_specs


def test_committed_video_inventory_is_an_exact_agent_to_entry_bijection() -> None:
    report = VideoInventoryValidator().validate_directory(_video_root())

    assert report.is_valid
    assert len(report.manifest_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
    assert len(report.inventory_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
    assert len(report.agent_spec_ids) == EXPECTED_VIDEO_AGENT_COUNT
    assert set(report.manifest_agent_ids) == set(report.inventory_agent_ids)
    assert set(report.manifest_agent_ids) == set(report.agent_spec_ids)


def test_missing_inventory_entry_is_rejected_without_activation() -> None:
    manifest = _load_asset("manifest.json")
    inventory = _load_asset("inventory.json")
    entries = inventory["entries"]
    assert isinstance(entries, list)
    inventory["entries"] = entries[:-1]

    report = VideoInventoryValidator().validate(manifest, inventory)

    assert not report.is_valid
    assert {issue.code for issue in report.issues} >= {
        "invalid_agent_count",
        "missing_inventory_entry",
    }


def test_missing_agent_spec_is_rejected_without_registration_or_activation() -> None:
    manifest = _load_asset("manifest.json")
    inventory = _load_asset("inventory.json")
    agent_specs = _load_agent_specs()
    agent_specs.pop("video.orchestrator")

    report = VideoInventoryValidator().validate(manifest, inventory, agent_specs)

    assert not report.is_valid
    assert any(issue.code == "missing_agent_spec" for issue in report.issues)


def test_active_video_agent_configuration_is_rejected() -> None:
    manifest = _load_asset("manifest.json")
    inventory = _load_asset("inventory.json")
    agents = manifest["agents"]
    assert isinstance(agents, list)
    agent = agents[0]
    assert isinstance(agent, dict)
    agent["status"] = "active"

    report = VideoInventoryValidator().validate(manifest, inventory)

    assert not report.is_valid
    assert any(issue.code == "invalid_lifecycle_status" for issue in report.issues)


def test_agent_spec_production_activation_request_is_rejected() -> None:
    manifest = _load_asset("manifest.json")
    inventory = _load_asset("inventory.json")
    agent_specs = _load_agent_specs()
    spec = agent_specs["video.orchestrator"]
    assert isinstance(spec, dict)
    spec["production_activation_requested"] = True

    report = VideoInventoryValidator().validate(manifest, inventory, agent_specs)

    assert not report.is_valid
    assert any(
        issue.code == "production_activation_requested" for issue in report.issues
    )
