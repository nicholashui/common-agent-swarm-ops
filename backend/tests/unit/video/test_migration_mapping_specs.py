"""Deterministic unit coverage for reviewed maps and local SPEC validation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.video.migration.agent_mapping import AgentSourceMapValidator, inventory_digest
from app.video.migration.contracts import AgentSourceMapEntry, MappingStatus
from app.video.migration.specifications import (
    build_specification_document,
    build_specifications,
    validate_specification_document,
)

NOW = "2025-01-01T00:00:00Z"
REVIEWED_AT = datetime(2025, 1, 1, tzinfo=UTC)


def _inventory() -> dict[str, object]:
    """Return the fixed authoritative 114-ID test inventory."""
    return {
        "pack_id": "video",
        "entries": [{"agent_id": f"video.agent_{index:03d}"} for index in range(114)],
    }


def _inventory_ids(inventory: dict[str, object]) -> list[str]:
    raw_entries = inventory["entries"]
    assert isinstance(raw_entries, list)
    ids = [
        entry["agent_id"]
        for entry in raw_entries
        if isinstance(entry, dict) and isinstance(entry.get("agent_id"), str)
    ]
    assert len(ids) == 114
    return ids


def _mapping_entry(agent_id: str, *, role: str = "editor") -> AgentSourceMapEntry:
    return AgentSourceMapEntry(
        common_agent_id=agent_id,
        mapping_status=MappingStatus.COMMON_ONLY,
        source_agent_ids=(),
        source_documents=("inventory.json",),
        rationale="Human-approved common contract role with no suitable source role.",
        reviewed_by="reviewer-1",
        reviewed_at=REVIEWED_AT,
    )


def _raw_mapping_entry(agent_id: str, **overrides: object) -> dict[str, object]:
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
    return {"inventory_digest": inventory_digest(_inventory_ids(inventory)), "entries": entries}


def _valid_raw_entries(inventory: dict[str, object]) -> list[dict[str, object]]:
    return [_raw_mapping_entry(agent_id) for agent_id in _inventory_ids(inventory)]


def test_missing_common_agent_id_is_reported() -> None:
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    missing_id = entries.pop()["common_agent_id"]

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(
        issue.code == "missing_common_agent_id" and issue.field == missing_id
        for issue in report.issues
    )


def test_duplicate_common_agent_id_is_reported() -> None:
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    duplicate_id = entries[0]["common_agent_id"]
    entries[-1]["common_agent_id"] = duplicate_id

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(issue.code == "duplicate_common_agent_id" for issue in report.issues)


def test_ambiguous_mapping_is_reported() -> None:
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    entries[0]["ambiguous"] = True

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(issue.code == "ambiguous_mapping" for issue in report.issues)


def test_unreviewed_mapping_is_reported() -> None:
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    entries[0]["reviewed_by"] = "unreviewed"

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(issue.code == "missing_human_review" for issue in report.issues)


def test_common_only_mapping_must_not_have_source_agents() -> None:
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    entries[0]["source_agent_ids"] = ["source.editor"]

    report = AgentSourceMapValidator().validate(inventory, _source_map(inventory, entries))

    assert not report.is_valid
    assert any(issue.code == "common_only_has_source_agents" for issue in report.issues)


def _runtime_binding(agent_id: str, *, role: str = "editor") -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "role": role,
        "status": "registered",
        "allowed_tools": ["local.read"],
        "budget_policy": {
            "max_input_tokens": 100,
            "max_output_tokens": 100,
            "max_tool_requests": 1,
        },
        "critique_edges": {"inputs": [], "outputs": []},
        "max_refinement_count": 1,
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": "local-video",
            "network_access": False,
        },
        "production_activation_requested": False,
        "prompt_reference": "video.prompt.default",
        "rubric_reference": "video.rubric.default",
        "schema_version": "1.0",
    }


def _write_local_knowledge_root(tmp_path: Path) -> Path:
    video_root = tmp_path / "business" / "video"
    (video_root / "agents").mkdir(parents=True)
    (video_root / "inventory.json").write_text("{}\n", encoding="utf-8")
    return video_root


def _base_spec(
    video_root: Path, agent_id: str, *, role: str = "editor"
) -> tuple[str, dict[str, object], AgentSourceMapEntry, Path]:
    runtime = _runtime_binding(agent_id, role=role)
    mapping_entry = _mapping_entry(agent_id, role=role)
    spec_path = video_root / "agents" / agent_id / "SPEC.md"
    document = build_specification_document(
        agent_id,
        runtime,
        mapping_entry,
        inventory_entry={"status": "registered"},
        pack_version="1.0",
    )
    return document, runtime, mapping_entry, spec_path


def _replace_section(document: str, heading: str, replacement: str) -> str:
    marker = f"## {heading}\n"
    section_start = document.index(marker) + len(marker)
    next_heading = document.find("\n## ", section_start)
    section_end = len(document) if next_heading == -1 else next_heading
    return document[:section_start] + replacement.strip() + "\n" + document[section_end:]


def test_generic_responsibility_is_reported(tmp_path: Path) -> None:
    video_root = _write_local_knowledge_root(tmp_path)
    agent_id = "video.agent_000"
    document, runtime, mapping_entry, spec_path = _base_spec(video_root, agent_id)
    document = _replace_section(document, "Responsibility", "Generic role.")

    issues = validate_specification_document(
        document,
        agent_id,
        runtime,
        video_root=video_root,
        repository_root=video_root.parent.parent,
        spec_path=spec_path,
        mapping_entry=mapping_entry,
    )

    assert any(issue.code == "generic_responsibility" for issue in issues)


def test_missing_required_heading_is_reported(tmp_path: Path) -> None:
    video_root = _write_local_knowledge_root(tmp_path)
    agent_id = "video.agent_001"
    document, runtime, mapping_entry, spec_path = _base_spec(video_root, agent_id)
    document = document.replace("## Provenance\n", "")

    issues = validate_specification_document(
        document,
        agent_id,
        runtime,
        video_root=video_root,
        repository_root=video_root.parent.parent,
        spec_path=spec_path,
        mapping_entry=mapping_entry,
    )

    assert any(
        issue.code == "missing_required_heading" and issue.field == "Provenance" for issue in issues
    )


def test_external_required_link_is_reported(tmp_path: Path) -> None:
    video_root = _write_local_knowledge_root(tmp_path)
    agent_id = "video.agent_002"
    document, runtime, mapping_entry, spec_path = _base_spec(video_root, agent_id)
    document = _replace_section(
        document,
        "Inputs and outputs",
        "Required source: https://example.invalid/video-guide.",
    )

    issues = validate_specification_document(
        document,
        agent_id,
        runtime,
        video_root=video_root,
        repository_root=video_root.parent.parent,
        spec_path=spec_path,
        mapping_entry=mapping_entry,
    )

    assert any(issue.code == "external_required_reference" for issue in issues)


@pytest.mark.parametrize(
    ("critical_review", "expected_code"),
    [
        (None, "missing_critical_review"),
        (
            {"reviewer": "reviewer-1", "result": "fail", "reviewed_at": NOW},
            "critical_review_not_passed",
        ),
    ],
)
def test_critical_role_requires_a_passing_review(
    tmp_path: Path, critical_review: object, expected_code: str
) -> None:
    video_root = _write_local_knowledge_root(tmp_path)
    agent_id = "video.agent_003"
    document, runtime, mapping_entry, spec_path = _base_spec(
        video_root, agent_id, role="orchestrator"
    )

    issues = validate_specification_document(
        document,
        agent_id,
        runtime,
        video_root=video_root,
        repository_root=video_root.parent.parent,
        spec_path=spec_path,
        mapping_entry=mapping_entry,
        critical_review=critical_review,
    )

    assert any(issue.code == expected_code for issue in issues)


def test_build_specifications_aggregates_failures_across_114_specs(tmp_path: Path) -> None:
    video_root = _write_local_knowledge_root(tmp_path)
    inventory = _inventory()
    entries = _valid_raw_entries(inventory)
    source_map = _source_map(inventory, entries)
    ids = _inventory_ids(inventory)

    for agent_id in ids:
        agent_dir = video_root / "agents" / agent_id
        agent_dir.mkdir()
        (agent_dir / "agent_spec.json").write_text(
            json.dumps(_runtime_binding(agent_id), sort_keys=True), encoding="utf-8"
        )

    first_id, second_id = ids[:2]
    first_document, _, _, _ = _base_spec(video_root, first_id)
    second_document, _, _, _ = _base_spec(video_root, second_id)
    (video_root / "agents" / first_id / "SPEC.md").write_text(
        _replace_section(first_document, "Responsibility", "Generic role."), encoding="utf-8"
    )
    (video_root / "agents" / second_id / "SPEC.md").write_text(
        second_document.replace("## Provenance\n", ""), encoding="utf-8"
    )

    report = build_specifications(
        video_root,
        inventory=inventory,
        source_map=source_map,
        use_existing_specs=True,
    )

    assert not report.is_valid
    assert len(report.drafts) == 114
    issue_pairs = {(issue.agent_id, issue.code) for issue in report.issues}
    assert (first_id, "generic_responsibility") in issue_pairs
    assert (second_id, "missing_required_heading") in issue_pairs
