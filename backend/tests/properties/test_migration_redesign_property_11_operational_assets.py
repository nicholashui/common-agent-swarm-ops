"""Property checks for constrained local Video Pack operational assets."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import MigrationResult
from app.video.migration.operational_assets import (
    AssetValidationReport,
    OperationalAssetValidator,
    register_adapted_workflow,
)

_AGENT_IDS: Final[tuple[str, ...]] = (
    "video.property_11_editor",
    "video.property_11_reviewer",
)
_ALLOWED_TOOLS: Final[tuple[str, ...]] = ("video.read", "video.write")
_WORKFLOW_PATH: Final[str] = "workflows/property-11.dna.json"
_SEED_PATH: Final[str] = "knowledge/seeds/property-11.md"
_CONSUMER_PATH: Final[str] = "processes/property-11.json"
_REVIEWED_AT: Final[str] = "2025-01-01T12:00:00Z"
_REVIEWER: Final[str] = "operational-assets-reviewer-property-11"
_MUTATION_KINDS: Final[tuple[str, ...]] = (
    "valid",
    "unknown_workflow_agent",
    "disallowed_workflow_tool",
    "missing_workflow_budget",
    "invalid_workflow_budget",
    "missing_risk_gate",
    "missing_compensation",
    "missing_critique",
    "missing_interrupt",
    "unknown_process_workflow",
    "invalid_process_workflow",
    "unknown_process_agent",
    "missing_seed_provenance",
    "missing_seed_consumer",
    "incomplete_skill_review",
    "missing_skill_consumer",
    "included_skill",
)
_WORKFLOW_MUTATIONS: Final[frozenset[str]] = frozenset(
    {
        "unknown_workflow_agent",
        "disallowed_workflow_tool",
        "missing_workflow_budget",
        "invalid_workflow_budget",
        "missing_risk_gate",
        "missing_compensation",
        "missing_critique",
        "missing_interrupt",
    }
)
_PROCESS_MUTATIONS: Final[frozenset[str]] = frozenset(
    {"unknown_process_workflow", "invalid_process_workflow", "unknown_process_agent"}
)
_SEED_MUTATIONS: Final[frozenset[str]] = frozenset(
    {"missing_seed_provenance", "missing_seed_consumer"}
)
_SKILL_MUTATIONS: Final[frozenset[str]] = frozenset(
    {"incomplete_skill_review", "missing_skill_consumer", "included_skill"}
)
_EXPECTED_CODES: Final[dict[str, frozenset[str]]] = {
    "unknown_workflow_agent": frozenset({"unknown_common_agent_id"}),
    "disallowed_workflow_tool": frozenset({"disallowed_workflow_tool"}),
    "missing_workflow_budget": frozenset({"missing_workflow_budget"}),
    "invalid_workflow_budget": frozenset({"invalid_workflow_budget"}),
    "missing_risk_gate": frozenset({"missing_workflow_risk_gate"}),
    "missing_compensation": frozenset({"missing_workflow_compensation"}),
    "missing_critique": frozenset({"missing_workflow_critique_loop"}),
    "missing_interrupt": frozenset({"missing_workflow_human_interrupt"}),
    "unknown_process_workflow": frozenset({"process_workflow_not_passing"}),
    "invalid_process_workflow": frozenset({"invalid_process_workflow_reference"}),
    "unknown_process_agent": frozenset({"unknown_process_agent_id"}),
    "missing_seed_provenance": frozenset({"missing_local_knowledge_provenance"}),
    "missing_seed_consumer": frozenset({"missing_knowledge_consumer"}),
    "incomplete_skill_review": frozenset({"special_skill_review_incomplete"}),
    "missing_skill_consumer": frozenset({"special_skill_consumer_missing"}),
    "included_skill": frozenset({"special_skill_must_remain_absent"}),
}
_EXPECTED_FIELDS: Final[dict[str, frozenset[str]]] = {
    # These diagnostic codes intentionally look like long secret-like tokens to
    # the shared redaction guard; their stable fields remain observable.
    "missing_interrupt": frozenset({"human_interrupts"}),
    "included_skill": frozenset({"skills[0]"}),
}


@dataclass(frozen=True, slots=True)
class OperationalAssetCase:
    """One bounded operational-asset fixture and one named fault mutation."""

    kind: str
    agent_id: str
    tool_id: str
    node_count: int
    handoff_count: int
    tool_count: int


@st.composite
def _operational_asset_cases(draw: st.DrawFn) -> OperationalAssetCase:
    """Generate small workflows and their related local asset records."""
    handoff_count = draw(st.integers(min_value=0, max_value=1))
    return OperationalAssetCase(
        kind=draw(st.sampled_from(_MUTATION_KINDS)),
        agent_id=draw(st.sampled_from(_AGENT_IDS)),
        tool_id=draw(st.sampled_from(_ALLOWED_TOOLS)),
        node_count=draw(st.integers(min_value=handoff_count + 1, max_value=2)),
        handoff_count=handoff_count,
        tool_count=draw(st.integers(min_value=0, max_value=1)),
    )


def _workflow(case: OperationalAssetCase) -> dict[str, object]:
    """Build a bounded adapted workflow satisfying every operational control."""
    nodes: list[dict[str, object]] = []
    for index in range(case.node_count):
        node: dict[str, object] = {
            "id": f"node-{index}",
            "agent_id": case.agent_id,
        }
        if case.tool_count == 1 and index == 0:
            node["tool_ids"] = [case.tool_id]
        nodes.append(node)

    edges: list[dict[str, str]] = []
    if case.handoff_count == 1:
        edges.append({"from": "node-0", "to": "node-1"})

    return {
        "workflow_path": _WORKFLOW_PATH,
        "agent_ids": [case.agent_id],
        "nodes": nodes,
        "edges": edges,
        "execution_budget": {
            "max_node_visits": case.node_count,
            "max_handoffs": case.handoff_count,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": case.tool_count,
        },
        "risk_gate_ids": ["human.release"],
        "compensation": {"strategy": "rollback"},
        "critique_loops": {"enabled": True, "max_iterations": 1},
        "human_interrupts": ["release.approval"],
    }


def _process(case: OperationalAssetCase) -> dict[str, object]:
    """Build a local process entry covering the generated workflow and agent."""
    return {
        "workflow_path": _WORKFLOW_PATH,
        "agent_ids": [case.agent_id],
    }


def _seed() -> dict[str, object]:
    """Build an inert knowledge seed with local provenance and a consumer."""
    return {
        "seed_path": _SEED_PATH,
        "provenance": {
            "repository": "https://example.invalid/video-source",
            "commit": "snapshot-property-11",
            "path": "upstream/video/property-11-seed.md",
            "license_status": "reviewed",
        },
        "consumer_ref": _CONSUMER_PATH,
        "review_status": "pass",
    }


def _special_skill() -> dict[str, object]:
    """Build a reviewed special-skill proposal that remains absent by default."""
    return {
        "skill_id": "property-11-caption-review",
        "compatibility": True,
        "security": True,
        "overlap": True,
        "license": True,
        "consumer_ref": _CONSUMER_PATH,
        "reviewer": _REVIEWER,
        "reviewed_at": _REVIEWED_AT,
        "result": "pass",
        "included": False,
    }


def _write_json(path: Path, value: object) -> None:
    """Write deterministic local fixture content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _materialize_local_assets(video_root: Path, workflow: dict[str, object]) -> None:
    """Create only the local files required by process and seed consumers."""
    workflow_path = workflow.get("workflow_path")
    if not isinstance(workflow_path, str):
        raise AssertionError("Generated workflows must have a string local path.")
    _write_json(video_root / workflow_path, workflow)
    _write_json(video_root / _CONSUMER_PATH, {"consumer": "local-property-11"})
    (video_root / _SEED_PATH).parent.mkdir(parents=True, exist_ok=True)
    (video_root / _SEED_PATH).write_text(
        "Inert local knowledge seed for property 11.\n", encoding="utf-8"
    )


def _apply_workflow_mutation(
    workflow: dict[str, object], mutation: str
) -> dict[str, object]:
    """Apply one bounded workflow-control mutation."""
    mutated = deepcopy(workflow)
    if mutation == "unknown_workflow_agent":
        mutated["agent_ids"] = ["video.unknown_property_11"]
        raw_nodes = mutated.get("nodes")
        if not isinstance(raw_nodes, list) or not raw_nodes:
            raise AssertionError("Generated workflow must contain nodes.")
        first_node = raw_nodes[0]
        if not isinstance(first_node, dict):
            raise AssertionError("Generated workflow nodes must be objects.")
        first_node["agent_id"] = "video.unknown_property_11"
    elif mutation == "disallowed_workflow_tool":
        raw_nodes = mutated.get("nodes")
        if not isinstance(raw_nodes, list) or not raw_nodes:
            raise AssertionError("Generated workflow must contain nodes.")
        first_node = raw_nodes[0]
        if not isinstance(first_node, dict):
            raise AssertionError("Generated workflow nodes must be objects.")
        first_node["tool_ids"] = ["video.disallowed_property_11"]
        budget = mutated.get("execution_budget")
        if not isinstance(budget, dict):
            raise AssertionError("Generated workflow must contain a budget.")
        budget["max_tool_requests"] = 1
    elif mutation == "missing_workflow_budget":
        budget = mutated.get("execution_budget")
        if not isinstance(budget, dict):
            raise AssertionError("Generated workflow must contain a budget.")
        budget.pop("max_handoffs", None)
    elif mutation == "invalid_workflow_budget":
        budget = mutated.get("execution_budget")
        if not isinstance(budget, dict):
            raise AssertionError("Generated workflow must contain a budget.")
        budget["max_node_visits"] = 0
    elif mutation == "missing_risk_gate":
        mutated.pop("risk_gate_ids", None)
    elif mutation == "missing_compensation":
        mutated.pop("compensation", None)
    elif mutation == "missing_critique":
        mutated.pop("critique_loops", None)
    elif mutation == "missing_interrupt":
        mutated.pop("human_interrupts", None)
    elif mutation != "valid":
        raise AssertionError(f"Unhandled workflow mutation: {mutation}")
    return mutated


def _apply_process_mutation(
    process: dict[str, object], mutation: str
) -> dict[str, object]:
    """Apply one bounded process-reference mutation."""
    mutated = deepcopy(process)
    if mutation == "unknown_process_workflow":
        mutated["workflow_path"] = "workflows/unknown-property-11.dna.json"
    elif mutation == "invalid_process_workflow":
        mutated["workflow_path"] = "../outside-property-11.dna.json"
    elif mutation == "unknown_process_agent":
        mutated["agent_ids"] = ["video.unknown_property_11"]
    elif mutation != "valid":
        raise AssertionError(f"Unhandled process mutation: {mutation}")
    return mutated


def _apply_seed_mutation(seed: dict[str, object], mutation: str) -> dict[str, object]:
    """Apply one bounded knowledge-seed provenance or consumer mutation."""
    mutated = deepcopy(seed)
    if mutation == "missing_seed_provenance":
        mutated.pop("provenance", None)
    elif mutation == "missing_seed_consumer":
        mutated.pop("consumer_ref", None)
    elif mutation != "valid":
        raise AssertionError(f"Unhandled seed mutation: {mutation}")
    return mutated


def _apply_skill_mutation(skill: dict[str, object], mutation: str) -> dict[str, object]:
    """Apply one bounded special-skill review or inclusion mutation."""
    mutated = deepcopy(skill)
    if mutation == "incomplete_skill_review":
        mutated["security"] = False
    elif mutation == "missing_skill_consumer":
        mutated.pop("consumer_ref", None)
    elif mutation == "included_skill":
        mutated["included"] = True
    elif mutation != "valid":
        raise AssertionError(f"Unhandled special-skill mutation: {mutation}")
    return mutated


def _assert_asset_report(
    report: AssetValidationReport,
    mutation: str,
    accepted_ids: tuple[str, ...] = (),
) -> None:
    """Assert the stable pass/fail boundary for process, seed, and skill reports."""
    if mutation == "valid":
        assert report.is_valid
        assert report.findings == ()
        assert report.accepted_ids == accepted_ids
        return

    assert not report.is_valid
    issue_codes = {finding.code for finding in report.findings}
    expected_codes = _EXPECTED_CODES[mutation]
    expected_fields = _EXPECTED_FIELDS.get(mutation, frozenset())
    assert expected_codes <= issue_codes or expected_fields <= {
        finding.field for finding in report.findings
    }
    assert report.accepted_ids == ()


# Feature: migration-redesign, Property 11: Operational assets are constrained to
# local common contracts.
# **Validates: Requirements 2.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9,
# 7.10, 7.11, 7.12, 7.13, 8.14, 8.15**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(OperationalAssetCase("valid", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0))
@example(
    OperationalAssetCase(
        "unknown_workflow_agent", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "disallowed_workflow_tool", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 1
    )
)
@example(
    OperationalAssetCase(
        "missing_workflow_budget", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "invalid_workflow_budget", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase("missing_risk_gate", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0)
)
@example(
    OperationalAssetCase(
        "missing_compensation", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase("missing_critique", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0)
)
@example(
    OperationalAssetCase("missing_interrupt", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0)
)
@example(
    OperationalAssetCase(
        "unknown_process_workflow", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "invalid_process_workflow", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "unknown_process_agent", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "missing_seed_provenance", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "missing_seed_consumer", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "incomplete_skill_review", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase(
        "missing_skill_consumer", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0
    )
)
@example(
    OperationalAssetCase("included_skill", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 1, 0, 0)
)
@given(case=_operational_asset_cases())
def test_property_11_operational_assets_remain_bounded_and_local(
    case: OperationalAssetCase,
) -> None:
    """Generated operational assets either pass all local gates or fail closed."""
    validator = OperationalAssetValidator(
        known_agent_ids=_AGENT_IDS,
        allowed_tools=_ALLOWED_TOOLS,
    )
    workflow = _workflow(case)

    if case.kind in _WORKFLOW_MUTATIONS or case.kind == "valid":
        assessment = validator.validate_workflow(
            _apply_workflow_mutation(workflow, case.kind),
            workflow_path=_WORKFLOW_PATH,
        )
        if case.kind == "valid":
            assert assessment.result == "pass"
            assert assessment.findings == ()
        else:
            assert assessment.result == "fail"
            issue_codes = {finding.code for finding in assessment.findings}
            expected_codes = _EXPECTED_CODES[case.kind]
            expected_fields = _EXPECTED_FIELDS.get(case.kind, frozenset())
            assert expected_codes <= issue_codes or expected_fields <= {
                finding.field for finding in assessment.findings
            }
        return

    with TemporaryDirectory() as temporary_root:
        video_root = Path(temporary_root) / "business" / "video"
        _materialize_local_assets(video_root, workflow)

        if case.kind in _PROCESS_MUTATIONS:
            process_report = validator.validate_process_coverage(
                [_apply_process_mutation(_process(case), case.kind)],
                {_WORKFLOW_PATH: workflow},
                video_root=video_root,
            )
            _assert_asset_report(process_report, case.kind, (_WORKFLOW_PATH,))
            return

        if case.kind in _SEED_MUTATIONS:
            seed_report = validator.validate_knowledge_seed(
                _apply_seed_mutation(_seed(), case.kind),
                video_root=video_root,
            )
            _assert_asset_report(seed_report, case.kind, (_SEED_PATH,))
            return

        if case.kind in _SKILL_MUTATIONS:
            skill_report = validator.validate_special_skill(
                _apply_skill_mutation(_special_skill(), case.kind),
                video_root=video_root,
            )
            _assert_asset_report(
                skill_report,
                case.kind,
                ("property-11-caption-review",),
            )
            return

        raise AssertionError(f"Unhandled operational asset mutation: {case.kind}")


def test_property_11_valid_assets_register_without_replacing_safe_baseline(
    tmp_path: Path,
) -> None:
    """A complete local asset set passes aggregate validation and preserves pack_spine."""
    case = OperationalAssetCase("valid", _AGENT_IDS[0], _ALLOWED_TOOLS[0], 2, 1, 1)
    validator = OperationalAssetValidator(
        known_agent_ids=_AGENT_IDS,
        allowed_tools=_ALLOWED_TOOLS,
    )
    workflow = _workflow(case)
    seed = _seed()
    skill = _special_skill()
    video_root = tmp_path / "business" / "video"
    _materialize_local_assets(video_root, workflow)

    aggregate = validator.validate(
        workflows=[workflow],
        process_index=[_process(case)],
        knowledge_seeds=[seed],
        special_skills=[skill],
        video_root=video_root,
    )

    assert aggregate.result is MigrationResult.PASS
    assert aggregate.is_valid
    assert aggregate.accepted_workflow_paths == (_WORKFLOW_PATH,)
    assert aggregate.process_report is not None and aggregate.process_report.is_valid
    assert (
        aggregate.knowledge_report is not None and aggregate.knowledge_report.is_valid
    )
    assert (
        aggregate.special_skill_report is not None
        and aggregate.special_skill_report.is_valid
    )

    spine = video_root / "workflows" / "pack_spine.json"
    spine.write_text(
        '{"id":"video.pack-spine","pattern":"safe-baseline"}\n', encoding="utf-8"
    )
    before_spine = spine.read_bytes()
    registered = register_adapted_workflow(
        video_root,
        workflow,
        _AGENT_IDS,
        _ALLOWED_TOOLS,
        workflow_path="workflows/property-11-registered.dna.json",
    )

    assert registered.result is MigrationResult.PASS
    assert (video_root / "workflows" / "property-11-registered.dna.json").is_file()
    assert spine.read_bytes() == before_spine
