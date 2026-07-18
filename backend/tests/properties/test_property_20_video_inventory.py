"""Property tests for the exact, configuration-only Video_Pack inventory."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from hypothesis import example, given, settings, strategies as st

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT, VideoInventoryValidator

# Feature: generic-swarm-business-os, Property 20: Video inventory is an exact
# agent-to-entry bijection.
# **Validates: Requirements 9.1**

_VIDEO_ROOT = Path(__file__).resolve().parents[3] / "business" / "video"


@dataclass(frozen=True, slots=True)
class InventoryCase:
    """One bounded valid or invalid exact-inventory configuration mutation."""

    kind: str
    source_index: int
    target_index: int
    suffix: int
    activation_surface: str


def _load_asset(name: str) -> dict[str, object]:
    parsed: object = json.loads((_VIDEO_ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _load_agent_specs() -> dict[str, object]:
    agent_specs: dict[str, object] = {}
    for spec_path in sorted((_VIDEO_ROOT / "agents").glob("*/agent_spec.json")):
        parsed: object = json.loads(spec_path.read_text(encoding="utf-8"))
        agent_specs[spec_path.parent.name] = parsed
    return agent_specs


_MANIFEST = _load_asset("manifest.json")
_INVENTORY = _load_asset("inventory.json")
_AGENT_SPECS = _load_agent_specs()


@st.composite
def _inventory_cases(draw: st.DrawFn) -> InventoryCase:
    """Generate required bounded bijection and activation-invalidating mutations."""
    source_index = draw(st.integers(min_value=0, max_value=EXPECTED_VIDEO_AGENT_COUNT - 1))
    target_candidate = draw(st.integers(min_value=0, max_value=EXPECTED_VIDEO_AGENT_COUNT - 2))
    target_index = target_candidate if target_candidate < source_index else target_candidate + 1
    return InventoryCase(
        kind=draw(
            st.sampled_from(
                ("valid", "duplicate", "missing", "extra", "noncanonical", "activation")
            )
        ),
        source_index=source_index,
        target_index=target_index,
        suffix=draw(st.integers(min_value=0, max_value=9_999)),
        activation_surface=draw(st.sampled_from(("manifest", "agent", "agent_spec"))),
    )


def _entries(document: dict[str, object], field: str) -> list[object]:
    entries = document[field]
    assert isinstance(entries, list)
    return entries


def _entry_identifier(entry: object) -> str:
    assert isinstance(entry, dict)
    agent_id = entry["agent_id"]
    assert isinstance(agent_id, str)
    return agent_id


def _mutate_case(
    case: InventoryCase,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    manifest = deepcopy(_MANIFEST)
    inventory = deepcopy(_INVENTORY)
    agent_specs = deepcopy(_AGENT_SPECS)
    manifest_agents = _entries(manifest, "agents")
    inventory_entries = _entries(inventory, "entries")

    if case.kind == "duplicate":
        inventory_entries[case.target_index] = deepcopy(inventory_entries[case.source_index])
    elif case.kind == "missing":
        inventory_entries.pop(case.source_index)
    elif case.kind == "extra":
        extra_entry = deepcopy(inventory_entries[case.source_index])
        assert isinstance(extra_entry, dict)
        extra_identifier = f"video.extra_{case.suffix}"
        extra_entry["agent_id"] = extra_identifier
        extra_entry["agent_spec_path"] = f"agents/{extra_identifier}/agent_spec.json"
        inventory_entries.append(extra_entry)
    elif case.kind == "noncanonical":
        noncanonical_entry = inventory_entries[case.source_index]
        assert isinstance(noncanonical_entry, dict)
        noncanonical_entry["agent_id"] = f"other.invalid_{case.suffix}"
    elif case.kind == "activation":
        if case.activation_surface == "manifest":
            manifest["production_activation_requested"] = True
        elif case.activation_surface == "agent":
            active_agent = manifest_agents[case.source_index]
            assert isinstance(active_agent, dict)
            active_agent["production_active"] = True
        else:
            agent_id = _entry_identifier(manifest_agents[case.source_index])
            agent_spec = agent_specs[agent_id]
            assert isinstance(agent_spec, dict)
            agent_spec["production_activation_requested"] = True

    return manifest, inventory, agent_specs


def _expected_issue_codes(case: InventoryCase) -> set[str]:
    if case.kind == "duplicate":
        return {"duplicate_inventory_entry", "missing_inventory_entry"}
    if case.kind == "missing":
        return {"invalid_agent_count", "missing_inventory_entry"}
    if case.kind == "extra":
        return {"invalid_agent_count", "extra_inventory_entry"}
    if case.kind == "noncanonical":
        return {"invalid_agent_identifier", "invalid_agent_count"}
    if case.kind == "activation":
        return {"production_activation_requested"}
    return set()


@settings(max_examples=100, deadline=None)
@given(case=_inventory_cases())
@example(InventoryCase("valid", 0, 1, 0, "manifest"))
@example(InventoryCase("duplicate", 0, 1, 1, "manifest"))
@example(InventoryCase("missing", 1, 0, 2, "agent"))
@example(InventoryCase("extra", 2, 0, 3, "agent_spec"))
@example(InventoryCase("noncanonical", 3, 0, 4, "manifest"))
@example(InventoryCase("activation", 4, 0, 5, "manifest"))
@example(InventoryCase("activation", 5, 0, 6, "agent"))
@example(InventoryCase("activation", 6, 0, 7, "agent_spec"))
def test_video_inventory_is_an_exact_configuration_only_bijection(
    case: InventoryCase,
) -> None:
    """Only the exact 114-agent configuration has one safe entry per Video_Pack agent.

    **Validates: Requirements 9.1**
    """
    manifest, inventory, agent_specs = _mutate_case(case)

    report = VideoInventoryValidator().validate(manifest, inventory, agent_specs)

    if case.kind == "valid":
        assert report.is_valid
        assert len(report.manifest_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
        assert len(report.inventory_agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
        assert len(report.agent_spec_ids) == EXPECTED_VIDEO_AGENT_COUNT
        assert set(report.manifest_agent_ids) == set(report.inventory_agent_ids)
        assert set(report.manifest_agent_ids) == set(report.agent_spec_ids)
        return

    assert not report.is_valid
    issue_codes = {issue.code for issue in report.issues}
    assert _expected_issue_codes(case) <= issue_codes
