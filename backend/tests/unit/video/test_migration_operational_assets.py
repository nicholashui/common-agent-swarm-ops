from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Protocol

import pytest

from app.video.migration.contracts import ImportFinding, MigrationResult
from app.video.migration.operational_assets import (
    OperationalAssetValidator,
    register_adapted_workflow,
)

KNOWN_AGENT_IDS = ("video.editor", "video.reviewer")
ALLOWED_TOOLS = ("local.read", "local.write")
PACK_SPINE_CONTENT = '{"id":"video.pack-spine","version":"1.0.0"}\n'


@pytest.fixture
def valid_workflow() -> dict[str, Any]:
    """Return one fixed, bounded workflow accepted by the local contracts."""
    return {
        "id": "video.edit",
        "workflow_path": "workflows/edit.dna.json",
        "agent_ids": ["video.editor"],
        "execution_budget": {
            "max_node_visits": 4,
            "max_handoffs": 2,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "tool_ids": ["local.read"],
        "risk_gate_ids": ["consent-review"],
        "compensation": {"strategy": "rollback"},
        "critique_loops": {"enabled": True, "max_iterations": 2},
        "human_interrupts": ["release-review"],
    }


@pytest.fixture
def valid_process() -> dict[str, object]:
    return {
        "processes": [
            {
                "process_id": "video-editing",
                "workflow_path": "workflows/edit.dna.json",
                "agent_ids": ["video.editor"],
            }
        ]
    }


@pytest.fixture
def valid_knowledge_seed() -> dict[str, object]:
    return {
        "seed_path": "knowledge/seeds/editing.md",
        "provenance": {
            "repository": "local-video-pack",
            "commit": "commit-1",
            "path": "corpus/editing-guide.md",
            "license_status": "reviewed",
        },
        "consumer_ref": "knowledge/consumers/editor.md",
        "review_status": "pass",
    }


@pytest.fixture
def valid_special_skill() -> dict[str, object]:
    return {
        "skill_id": "caption-quality",
        "compatibility": True,
        "security": True,
        "overlap": True,
        "license": True,
        "consumer_ref": "knowledge/consumers/editor.md",
        "reviewer": "reviewer-1",
        "reviewed_at": "2025-01-01T12:00:00Z",
        "result": "pass",
        "included": False,
    }


def _validator() -> OperationalAssetValidator:
    return OperationalAssetValidator(KNOWN_AGENT_IDS, ALLOWED_TOOLS)


def _write_local_asset_tree(video_root: Path, valid_workflow: dict[str, Any]) -> None:
    (video_root / "workflows").mkdir(parents=True)
    (video_root / "knowledge" / "seeds").mkdir(parents=True)
    (video_root / "knowledge" / "consumers").mkdir(parents=True)
    (video_root / "workflows" / "edit.dna.json").write_text(
        json.dumps(valid_workflow, sort_keys=True), encoding="utf-8"
    )
    (video_root / "knowledge" / "seeds" / "editing.md").write_text(
        "Editing seed", encoding="utf-8"
    )
    (video_root / "knowledge" / "consumers" / "editor.md").write_text(
        "Local editor consumer", encoding="utf-8"
    )


class _FindingReport(Protocol):
    findings: tuple[ImportFinding, ...]


def _finding_codes(report: _FindingReport) -> set[str]:
    return {finding.code for finding in report.findings}


def test_unknown_common_agent_is_rejected(valid_workflow: dict[str, Any]) -> None:
    workflow = copy.deepcopy(valid_workflow)
    workflow["agent_ids"] = ["video.unknown"]

    report = _validator().validate_workflow(workflow)

    assert report.result == "fail"
    assert "unknown_common_agent_id" in _finding_codes(report)


def test_disallowed_workflow_tool_is_rejected(valid_workflow: dict[str, Any]) -> None:
    workflow = copy.deepcopy(valid_workflow)
    workflow["tool_ids"] = ["provider.activate"]

    report = _validator().validate_workflow(workflow)

    assert report.result == "fail"
    assert "disallowed_workflow_tool" in _finding_codes(report)


def test_unbounded_workflow_graph_is_rejected(valid_workflow: dict[str, Any]) -> None:
    workflow = copy.deepcopy(valid_workflow)
    execution_budget = workflow["execution_budget"]
    assert isinstance(execution_budget, dict)
    execution_budget.pop("max_node_visits")

    report = _validator().validate_workflow(workflow)

    assert report.result == "fail"
    assert "missing_workflow_budget" in _finding_codes(report)
    assert any(
        finding.field == "execution_budget.max_node_visits"
        for finding in report.findings
    )


def test_absent_workflow_gates_are_rejected(valid_workflow: dict[str, Any]) -> None:
    workflow = copy.deepcopy(valid_workflow)
    for field in (
        "risk_gate_ids",
        "compensation",
        "critique_loops",
        "human_interrupts",
    ):
        workflow.pop(field)

    report = _validator().validate_workflow(workflow)

    assert report.result == "fail"
    assert _finding_codes(report) >= {
        "missing_workflow_risk_gate",
        "missing_workflow_compensation",
        "missing_workflow_critique_loop",
    }
    assert any(finding.field == "human_interrupts" for finding in report.findings)


def test_process_requires_passing_workflow_and_known_agent(
    valid_workflow: dict[str, Any], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    _write_local_asset_tree(video_root, valid_workflow)
    process = {
        "processes": [
            {
                "workflow_path": "workflows/not-passing.dna.json",
                "agent_ids": ["video.unknown"],
            }
        ]
    }

    report = _validator().validate_process_coverage(
        process,
        {"workflows/edit.dna.json": valid_workflow},
        video_root=video_root,
    )

    assert report.result is MigrationResult.FAIL
    assert _finding_codes(report) >= {
        "process_workflow_not_passing",
        "unknown_process_agent_id",
        "missing_local_asset",
    }
    assert report.accepted_ids == ()


def test_knowledge_seed_with_invalid_consumer_is_rejected(
    valid_knowledge_seed: dict[str, object], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    (video_root / "knowledge" / "seeds").mkdir(parents=True)
    (video_root / "knowledge" / "seeds" / "editing.md").write_text(
        "Editing seed", encoding="utf-8"
    )
    seed = copy.deepcopy(valid_knowledge_seed)
    seed["consumer_ref"] = "knowledge/consumers/missing.md"

    report = _validator().validate_knowledge_seed(seed, video_root=video_root)

    assert report.result is MigrationResult.FAIL
    assert "invalid_knowledge_consumer" in _finding_codes(report)
    assert report.accepted_ids == ()


def test_special_skill_with_incomplete_review_is_kept_absent(
    valid_special_skill: dict[str, object], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    (video_root / "knowledge" / "consumers").mkdir(parents=True)
    (video_root / "knowledge" / "consumers" / "editor.md").write_text(
        "Local editor consumer", encoding="utf-8"
    )
    skill = copy.deepcopy(valid_special_skill)
    skill["security"] = False
    skill["license"] = False

    report = _validator().validate_special_skill(skill, video_root=video_root)

    assert report.result is MigrationResult.FAIL
    assert "special_skill_review_incomplete" in _finding_codes(report)
    assert report.accepted_ids == ()


def test_special_skill_with_invalid_consumer_is_kept_absent(
    valid_special_skill: dict[str, object], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    skill = copy.deepcopy(valid_special_skill)
    skill["consumer_ref"] = "knowledge/consumers/missing.md"

    report = _validator().validate_special_skill(skill, video_root=video_root)

    assert report.result is MigrationResult.FAIL
    assert "special_skill_consumer_missing" in _finding_codes(report)
    assert report.accepted_ids == ()


def test_valid_local_operational_assets_are_accepted(
    valid_workflow: dict[str, Any],
    valid_process: dict[str, object],
    valid_knowledge_seed: dict[str, object],
    valid_special_skill: dict[str, object],
    tmp_path: Path,
) -> None:
    video_root = tmp_path / "business" / "video"
    _write_local_asset_tree(video_root, valid_workflow)

    report = _validator().validate(
        {"workflows/edit.dna.json": valid_workflow},
        process_index=valid_process,
        knowledge_seeds={"seeds": [valid_knowledge_seed]},
        special_skills={"skills": [valid_special_skill]},
        video_root=video_root,
    )

    assert report.result is MigrationResult.PASS
    assert report.process_report is not None and report.process_report.is_valid
    assert report.knowledge_report is not None and report.knowledge_report.is_valid
    assert (
        report.special_skill_report is not None and report.special_skill_report.is_valid
    )
    assert report.accepted_workflow_paths == ("workflows/edit.dna.json",)
    assert report.special_skill_report.accepted_ids == ("caption-quality",)


def test_registration_retains_safe_baseline_spine(
    valid_workflow: dict[str, Any], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    workflows_root = video_root / "workflows"
    workflows_root.mkdir(parents=True)
    spine = workflows_root / "pack_spine.json"
    spine.write_text(PACK_SPINE_CONTENT, encoding="utf-8")

    report = register_adapted_workflow(
        video_root,
        valid_workflow,
        KNOWN_AGENT_IDS,
        ALLOWED_TOOLS,
        workflow_path="workflows/edit.dna.json",
    )

    assert report.result is MigrationResult.PASS
    assert spine.read_text(encoding="utf-8") == PACK_SPINE_CONTENT
    assert (workflows_root / "edit.dna.json").read_text(encoding="utf-8") == (
        json.dumps(valid_workflow, sort_keys=True, separators=(",", ":")) + "\n"
    )


def test_rejected_registration_does_not_replace_safe_baseline_spine(
    valid_workflow: dict[str, Any], tmp_path: Path
) -> None:
    video_root = tmp_path / "business" / "video"
    workflows_root = video_root / "workflows"
    workflows_root.mkdir(parents=True)
    spine = workflows_root / "pack_spine.json"
    spine.write_text(PACK_SPINE_CONTENT, encoding="utf-8")
    invalid_workflow = copy.deepcopy(valid_workflow)
    invalid_workflow["agent_ids"] = ["video.unknown"]

    report = register_adapted_workflow(
        video_root,
        invalid_workflow,
        KNOWN_AGENT_IDS,
        ALLOWED_TOOLS,
        workflow_path="workflows/invalid.dna.json",
    )

    assert report.result is MigrationResult.BLOCKED
    assert spine.read_text(encoding="utf-8") == PACK_SPINE_CONTENT
    assert not (workflows_root / "invalid.dna.json").exists()
