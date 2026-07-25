"""Focused tests for exact reviewed Agent Source Map validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.video.migration.agent_mapping import (
    AgentSourceMapValidator,
    MappingWriteBlockedError,
    build_projections,
    inventory_digest,
    validate_projection_files,
    validate_roster_projection,
    write_projections,
)

NOW = "2025-01-01T00:00:00Z"


def _inventory(count: int = 114) -> dict[str, object]:
    return {
        "pack_id": "video",
        "entries": [{"agent_id": f"video.agent_{index:03d}"} for index in range(count)],
    }


def _entry(agent_id: str, **overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "common_agent_id": agent_id,
        "mapping_status": "common_only",
        "source_agent_ids": [],
        "source_documents": ["inventory.json"],
        "rationale": "Human-approved common contract role with no suitable source role.",
        "reviewed_by": "reviewer-1",
        "reviewed_at": NOW,
    }
    entry.update(overrides)
    return entry


def _source_map(
    inventory: dict[str, object], entries: list[dict[str, object]]
) -> dict[str, object]:
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    ids = [entry["agent_id"] for entry in raw_entries if isinstance(entry, dict)]
    assert all(isinstance(agent_id, str) for agent_id in ids)
    return {"inventory_digest": inventory_digest(ids), "entries": entries}


def test_valid_map_preserves_inventory_order_and_projects_common_ids() -> None:
    inventory = _inventory()
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    entries = [_entry(item["agent_id"]) for item in raw_entries if isinstance(item, dict)]

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert report.is_valid
    assert len(report.entries) == 114
    projections = build_projections(report)
    roster_entries = projections.roster["entries"]
    assert isinstance(roster_entries, list)
    assert all(isinstance(entry, dict) for entry in roster_entries)
    assert [entry["agent_id"] for entry in roster_entries] == [
        item["common_agent_id"] for item in entries
    ]
    assert "video.agent_000" in projections.map_markdown
    assert "source_agent_ids" not in projections.roster_json


def test_invalid_mapping_prerequisites_block_specification_write() -> None:
    inventory = _inventory()
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    entries = [_entry(item["agent_id"]) for item in raw_entries if isinstance(item, dict)]
    entries[0]["ambiguous"] = True
    entries.pop()
    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert {issue.code for issue in report.issues} >= {
        "ambiguous_mapping",
        "missing_common_agent_id",
    }
    with pytest.raises(MappingWriteBlockedError):
        report.require_write_mode()


def test_reused_source_requires_distinct_reviewed_rationale() -> None:
    inventory = _inventory()
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    entries = [_entry(item["agent_id"]) for item in raw_entries if isinstance(item, dict)]
    entries[0].update(
        mapping_status="exact",
        source_agent_ids=["source.shared"],
        rationale="The shared source role is an exact match.",
    )
    entries[1].update(
        mapping_status="related",
        source_agent_ids=["source.shared"],
        rationale="The shared source role is an exact match.",
    )

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(issue.code == "reused_source_rationale_not_distinct" for issue in report.issues)


def test_source_documents_must_be_local_readable_files(tmp_path: Path) -> None:
    video_root = tmp_path / "business" / "video"
    video_root.mkdir(parents=True)
    (video_root / "inventory.json").write_text("{}", encoding="utf-8")
    (video_root / "inventory.json").touch()
    inventory = _inventory()
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    entries = [_entry(item["agent_id"]) for item in raw_entries if isinstance(item, dict)]
    entries[0]["source_documents"] = ["generic-swarm-ops/study/agents.md"]

    report = AgentSourceMapValidator().validate(
        inventory,
        _source_map(inventory, entries),
        video_root=video_root,
    )

    assert not report.is_valid
    assert any(issue.code == "external_source_document" for issue in report.issues)


def test_write_and_validate_projections_are_derived_from_reviewed_map(tmp_path: Path) -> None:
    video_root = tmp_path / "video"
    video_root.mkdir()
    inventory = _inventory()
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    entries = [_entry(item["agent_id"]) for item in raw_entries if isinstance(item, dict)]
    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    write_projections(video_root, report)

    projection_report = validate_projection_files(video_root, report)
    assert projection_report.is_valid
    assert (video_root / "ROSTER.json").is_file()
    assert (video_root / "MAP.md").is_file()


def test_roster_projection_requires_exact_ordered_common_ids() -> None:
    ids = [f"video.agent_{index:03d}" for index in range(114)]

    roster_report = validate_roster_projection(
        {"entries": [{"agent_id": agent_id} for agent_id in ids]}, ids
    )

    assert roster_report.is_valid
