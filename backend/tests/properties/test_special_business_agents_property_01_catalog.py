"""Property checks for the fixed Special_Agent catalog projection."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIAL_SOURCE_CATALOG,
    SPECIAL_SOURCE_PATHS,
    SPECIALS_INVENTORY_PATH,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_SCHEMA_PATH,
    AcceptedSpecialAgent,
    AcceptedSpecialsState,
    canonical_agent_spec_path,
    is_canonical_agent_id,
    source_for_agent_id,
    source_for_path,
    validate_specials_pack,
)
from tests.fakes.specials_governance import materialize_specials_governance

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SCHEMA_SOURCE_PATH: Final[Path] = (
    _REPOSITORY_ROOT / "business" / "specials" / "schemas" / "special-agent-spec.schema.json"
)
_CONTROLLER_SOURCE_PATH: Final[str] = "docs/special_agents_redesign/agents/controller_agent.md"


@dataclass(frozen=True, slots=True)
class CatalogCase:
    """One bounded catalog mutation generated for the property."""

    kind: str
    index: int
    target: str
    path_variant: str


@dataclass(frozen=True, slots=True)
class FixtureValues:
    """JSON values written into one temporary repository fixture."""

    manifest: dict[str, object]
    inventory: dict[str, object]
    specifications: dict[str, dict[str, object]]
    exact_projection: bool


@st.composite
def _catalog_cases(draw: st.DrawFn) -> CatalogCase:
    """Generate membership, ordering, path, identity, and namespace mutations."""
    return CatalogCase(
        kind=draw(
            st.sampled_from(
                (
                    "valid",
                    "permutation",
                    "subset",
                    "duplicate",
                    "path",
                    "canonical_id",
                    "asset_id",
                )
            )
        ),
        index=draw(st.integers(min_value=0, max_value=len(SPECIAL_AGENT_IDS) - 1)),
        target=draw(st.sampled_from(("manifest", "inventory", "spec"))),
        path_variant=draw(st.sampled_from(("traversal", "absolute", "wrong_id"))),
    )


def _agent_spec(agent_id: str) -> dict[str, object]:
    """Build a valid data-only specification without reading source content."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": "Special_Agent data-only property fixture",
        "allowed_tools": [],
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": "specials-local-deterministic-v1",
            "network_access": False,
        },
        "budget_policy": {
            "max_input_tokens": 1,
            "max_output_tokens": 1,
            "max_tool_requests": 0,
        },
        "prompt_reference": f"spagent.{agent_name}-prompt",
        "rubric_reference": f"spagent.{agent_name}-rubric",
        "critique_edges": {
            "inputs": [f"spagent.{agent_name}-input"],
            "outputs": [f"spagent.{agent_name}-output"],
        },
        "max_refinement_count": 1,
        "production_activation_requested": False,
    }


def _manifest_entry(agent_id: str) -> dict[str, object]:
    """Build one canonical manifest entry."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "allowed_tools": [],
        "production_activation_requested": False,
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _inventory_entry(agent_id: str) -> dict[str, object]:
    """Build one canonical inventory entry."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _replacement_id(index: int) -> str:
    """Return a different canonical ID for a membership/identity mutation."""
    return SPECIAL_AGENT_IDS[(index + 1) % len(SPECIAL_AGENT_IDS)]


def _asset_replacement(index: int) -> str:
    """Return a valid asset-namespace value that cannot identify an agent."""
    agent_name = SPECIAL_AGENT_IDS[index].removeprefix("specials.")
    return f"spagent.{agent_name}"


def _build_fixture_values(root: Path, case: CatalogCase) -> FixtureValues:
    """Apply one generated mutation to an otherwise exact 19-member projection."""
    manifest_entries = [_manifest_entry(agent_id) for agent_id in SPECIAL_AGENT_IDS]
    inventory_entries = [_inventory_entry(agent_id) for agent_id in SPECIAL_AGENT_IDS]
    specifications = {agent_id: _agent_spec(agent_id) for agent_id in SPECIAL_AGENT_IDS}

    if case.kind == "permutation":
        offset = (case.index + 1) % len(SPECIAL_AGENT_IDS)
        manifest_entries = manifest_entries[offset:] + manifest_entries[:offset]
        inventory_entries = inventory_entries[offset:] + inventory_entries[:offset]
    elif case.kind == "subset":
        if case.target == "manifest":
            manifest_entries.pop(case.index)
        elif case.target == "inventory":
            inventory_entries.pop(case.index)
        else:
            specifications.pop(SPECIAL_AGENT_IDS[case.index])
    elif case.kind == "duplicate":
        if case.target == "manifest":
            manifest_entries.insert(case.index, deepcopy(manifest_entries[case.index]))
        elif case.target == "inventory":
            inventory_entries.insert(case.index, deepcopy(inventory_entries[case.index]))
        else:
            specifications[SPECIAL_AGENT_IDS[case.index]]["agent_id"] = _replacement_id(case.index)
    elif case.kind == "path":
        entry = manifest_entries[case.index]
        if case.path_variant == "traversal":
            entry["agent_spec_path"] = "../agents/escaped/agent_spec.json"
        elif case.path_variant == "absolute":
            entry["agent_spec_path"] = str(root / "outside" / "agent_spec.json")
        else:
            entry["agent_spec_path"] = canonical_agent_spec_path(_replacement_id(case.index))
    elif case.kind == "canonical_id":
        replacement = _replacement_id(case.index)
        if case.target == "manifest":
            manifest_entries[case.index]["agent_id"] = replacement
        elif case.target == "inventory":
            inventory_entries[case.index]["agent_id"] = replacement
        else:
            specifications[SPECIAL_AGENT_IDS[case.index]]["agent_id"] = replacement
    elif case.kind == "asset_id":
        replacement = _asset_replacement(case.index)
        if case.target == "manifest":
            manifest_entries[case.index]["agent_id"] = replacement
        elif case.target == "inventory":
            inventory_entries[case.index]["agent_id"] = replacement
        else:
            specifications[SPECIAL_AGENT_IDS[case.index]]["agent_id"] = replacement

    manifest: dict[str, object] = {
        "pack_id": "specials",
        "agents": manifest_entries,
        "production_activation_requested": False,
        "inventory_required": True,
    }
    inventory: dict[str, object] = {"entries": inventory_entries}
    exact_projection = _has_exact_projection(manifest_entries, inventory_entries, specifications)
    return FixtureValues(manifest, inventory, specifications, exact_projection)


def _has_exact_projection(
    manifest_entries: list[dict[str, object]],
    inventory_entries: list[dict[str, object]],
    specifications: dict[str, dict[str, object]],
) -> bool:
    """Compute the specification's exact projection predicate independently."""
    expected_ids = set(SPECIAL_AGENT_IDS)
    manifest_ids = [entry.get("agent_id") for entry in manifest_entries]
    inventory_ids = [entry.get("agent_id") for entry in inventory_entries]
    if (
        len(manifest_ids) != len(SPECIAL_AGENT_IDS)
        or len(inventory_ids) != len(SPECIAL_AGENT_IDS)
        or set(manifest_ids) != expected_ids
        or set(inventory_ids) != expected_ids
        or len(set(manifest_ids)) != len(SPECIAL_AGENT_IDS)
        or len(set(inventory_ids)) != len(SPECIAL_AGENT_IDS)
        or set(specifications) != expected_ids
    ):
        return False

    for entry in manifest_entries:
        agent_id = entry.get("agent_id")
        if not isinstance(agent_id, str) or not is_canonical_agent_id(agent_id):
            return False
        if entry.get("agent_spec_path") != canonical_agent_spec_path(agent_id):
            return False
    for entry in inventory_entries:
        agent_id = entry.get("agent_id")
        if not isinstance(agent_id, str) or not is_canonical_agent_id(agent_id):
            return False
        if entry.get("agent_spec_path") != canonical_agent_spec_path(agent_id):
            return False
    return all(
        specification.get("agent_id") == agent_id
        for agent_id, specification in specifications.items()
    )


def _write_json(root: Path, relative_path: str, value: object) -> None:
    """Write one canonical local JSON fixture file."""
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def _write_fixture(root: Path, values: FixtureValues) -> tuple[str, ...]:
    """Write the explicit allowlist and return only paths used by this fixture."""
    schema_target = root / SPECIALS_SCHEMA_PATH
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    schema_target.write_bytes(_SCHEMA_SOURCE_PATH.read_bytes())
    _write_json(root, SPECIALS_MANIFEST_PATH, values.manifest)
    _write_json(root, SPECIALS_INVENTORY_PATH, values.inventory)
    for agent_id in SPECIAL_AGENT_IDS:
        specification = values.specifications.get(agent_id, _agent_spec(agent_id))
        _write_json(
            root,
            f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}",
            specification,
        )

    represented_specification_paths = tuple(
        f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        for agent_id in SPECIAL_AGENT_IDS
        if agent_id in values.specifications
    )
    controller_source = root / _CONTROLLER_SOURCE_PATH
    controller_source.parent.mkdir(parents=True, exist_ok=True)
    controller_source.write_bytes(b"untrusted controller source fixture bytes")
    return materialize_specials_governance(
        root,
        (
            SPECIALS_SCHEMA_PATH,
            SPECIALS_MANIFEST_PATH,
            SPECIALS_INVENTORY_PATH,
            *represented_specification_paths,
            _CONTROLLER_SOURCE_PATH,
        ),
    )


def _assert_fixed_catalog_and_controller_mapping() -> None:
    """Assert the fixed catalog includes the controller source only as provenance."""
    assert len(SPECIAL_SOURCE_CATALOG) == 19
    assert tuple(entry.agent_id for entry in SPECIAL_SOURCE_CATALOG) == SPECIAL_AGENT_IDS
    assert tuple(entry.source_path for entry in SPECIAL_SOURCE_CATALOG) == SPECIAL_SOURCE_PATHS
    controller = source_for_agent_id("specials.controller-agent")
    assert controller is not None
    assert controller.source_path == _CONTROLLER_SOURCE_PATH
    assert controller.agent_id == "specials.controller-agent"
    assert controller.agent_spec_path == "agents/specials.controller-agent/agent_spec.json"
    assert source_for_path(_CONTROLLER_SOURCE_PATH) == controller
    assert all(source_for_path(entry.source_path) == entry for entry in SPECIAL_SOURCE_CATALOG)


# Feature: special-business-agents, Property 1: Canonical catalog bijection and
# namespace separation.
# **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4**
@settings(max_examples=100, database=None, derandomize=True, deadline=None)
@example(CatalogCase("valid", 0, "manifest", "traversal"))
@example(CatalogCase("permutation", 1, "inventory", "wrong_id"))
@example(CatalogCase("subset", 2, "spec", "absolute"))
@example(CatalogCase("duplicate", 3, "manifest", "traversal"))
@example(CatalogCase("path", 4, "manifest", "absolute"))
@example(CatalogCase("canonical_id", 5, "spec", "wrong_id"))
@example(CatalogCase("asset_id", 6, "inventory", "traversal"))
@given(case=_catalog_cases())
def test_property_01_canonical_catalog_bijection_and_namespace_separation(
    case: CatalogCase,
) -> None:
    """Only the exact canonical 19-member projection is accepted."""
    _assert_fixed_catalog_and_controller_mapping()
    with TemporaryDirectory() as temporary_directory:
        fixture_root = Path(temporary_directory)
        values = _build_fixture_values(fixture_root, case)
        allowlisted_paths = _write_fixture(fixture_root, values)
        previous_state = AcceptedSpecialsState(
            agents=(AcceptedSpecialAgent("specials.controller-agent"),),
            validation_report_digest="prior-accepted-state",
        )

        report = validate_specials_pack(fixture_root, allowlisted_paths, previous_state)

        assert (report.validation_outcome == "pass") is values.exact_projection
        expected_manifest_result = (
            "fail"
            if case.kind == "path" or (case.target == "manifest" and not values.exact_projection)
            else "pass"
        )
        expected_inventory_result = (
            "fail"
            if not values.exact_projection
            and (case.kind == "path" or case.target in {"manifest", "inventory"})
            else "pass"
        )
        assert report.manifest.result == expected_manifest_result
        assert report.inventory.required is True
        assert report.inventory.result == expected_inventory_result
        if values.exact_projection:
            assert report.accepted_agent_ids == SPECIAL_AGENT_IDS
            assert report.rejected_agent_ids == ()
            assert report.accepted_state.agent_ids == SPECIAL_AGENT_IDS
            assert report.registration_effect == "eligible_draft_representation"
            assert tuple(file_result.path for file_result in report.files) == tuple(
                sorted(allowlisted_paths)
            )
        else:
            assert report.accepted_agent_ids == ()
            assert report.rejected_agent_ids == tuple(sorted(SPECIAL_AGENT_IDS))
            assert report.registration_effect == "none"
            assert report.findings
            assert report.accepted_state == previous_state
