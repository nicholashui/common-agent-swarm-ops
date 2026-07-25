"""Property checks for Special_Business_Agent representation integrity."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final, Literal, cast

from hypothesis import given, settings, strategies as st

from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIAL_AGENT_SPEC_PATHS,
    SPECIALS_INVENTORY_PATH,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_SCHEMA_PATH,
    AcceptedSpecialAgent,
    AcceptedSpecialsState,
    canonical_agent_spec_path,
    validate_specials_pack,
)
from tests.fakes.specials_governance import materialize_specials_governance

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SCHEMA_SOURCE_PATH: Final[Path] = (
    _REPOSITORY_ROOT / "business" / "specials" / "schemas" / "special-agent-spec.schema.json"
)
_MUTATION_KINDS: Final[tuple[str, ...]] = (
    "ordering",
    "canonical_id",
    "spagent_substitution",
    "path",
    "status",
    "tools",
    "membership",
)
MutationTarget = Literal["manifest", "inventory", "spec"]


@dataclass(frozen=True, slots=True)
class IntegrityMutation:
    """One representation mutation applied to a valid local pack."""

    kind: str
    target: MutationTarget
    agent_index: int
    inventory_required: bool


def _agent_spec(agent_id: str) -> dict[str, object]:
    """Return a complete immutable-profile specification for one test agent."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": f"Local data-only role for {agent_name}.",
        "allowed_tools": [],
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": f"specials-property-03-{agent_name}",
            "network_access": False,
        },
        "budget_policy": {
            "max_input_tokens": 1024,
            "max_output_tokens": 1024,
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
    """Return the canonical manifest projection for one agent."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "allowed_tools": [],
        "production_activation_requested": False,
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _inventory_entry(agent_id: str) -> dict[str, object]:
    """Return the canonical conditional-inventory projection for one agent."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _write_json(path: Path, value: object) -> None:
    """Write a deterministic local JSON fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_object(path: Path) -> dict[str, object]:
    """Read a fixture object without using any validator internals."""
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"Expected object fixture at {path}.")
    return cast(dict[str, object], value)


def _write_pack_fixture(
    tmp_path: Path,
    *,
    inventory_required: bool,
    manifest_order: tuple[str, ...],
    inventory_order: tuple[str, ...],
) -> tuple[Path, list[str]]:
    """Create a complete local manifest/specification fixture and allowlist."""
    repository_root = tmp_path / "special-business-agents-property-03"
    schema_path = repository_root / SPECIALS_SCHEMA_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes(_SCHEMA_SOURCE_PATH.read_bytes())

    manifest = {
        "pack_id": "specials",
        "agents": [_manifest_entry(agent_id) for agent_id in manifest_order],
        "production_activation_requested": False,
        "inventory_required": inventory_required,
    }
    manifest_path = repository_root / SPECIALS_MANIFEST_PATH
    _write_json(manifest_path, manifest)

    allowlisted_paths = [SPECIALS_SCHEMA_PATH, SPECIALS_MANIFEST_PATH]
    for agent_id in SPECIAL_AGENT_IDS:
        relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        _write_json(repository_root / relative_path, _agent_spec(agent_id))
        allowlisted_paths.append(relative_path)

    if inventory_required:
        inventory = {"entries": [_inventory_entry(agent_id) for agent_id in inventory_order]}
        _write_json(repository_root / SPECIALS_INVENTORY_PATH, inventory)
        allowlisted_paths.append(SPECIALS_INVENTORY_PATH)

    return repository_root, list(
        materialize_specials_governance(repository_root, allowlisted_paths)
    )


def _path_for_target(
    repository_root: Path,
    target: MutationTarget,
    inventory_required: bool,
    agent_index: int,
) -> Path:
    """Return the local representation file selected by a mutation."""
    if target == "manifest":
        return repository_root / SPECIALS_MANIFEST_PATH
    if target == "inventory" and inventory_required:
        return repository_root / SPECIALS_INVENTORY_PATH
    if target == "spec":
        return repository_root / SPECIAL_AGENT_SPEC_PATHS[agent_index]
    raise AssertionError(f"Invalid mutation target {target!r} for the fixture.")


def _target_entry_index(entries: list[object], agent_id: str) -> int:
    """Locate an agent in a generated manifest or inventory ordering."""
    for index, entry in enumerate(entries):
        if isinstance(entry, dict) and entry.get("agent_id") == agent_id:
            return index
    raise AssertionError(f"Fixture does not contain expected agent {agent_id!r}.")


def _apply_mutation(
    repository_root: Path,
    allowlisted_paths: list[str],
    mutation: IntegrityMutation,
    *,
    inventory_required: bool,
) -> None:
    """Apply one invalid change without changing the validator implementation."""
    agent_id = SPECIAL_AGENT_IDS[mutation.agent_index]
    if mutation.kind == "membership" and mutation.target == "spec":
        spec_path = SPECIAL_AGENT_SPEC_PATHS[mutation.agent_index]
        allowlisted_paths.remove(spec_path)
        return

    path = _path_for_target(
        repository_root,
        mutation.target,
        inventory_required,
        mutation.agent_index,
    )
    document = _read_object(path)
    if mutation.target == "spec":
        document["agent_id"] = (
            "specials.invalid-catalog-member"
            if mutation.kind == "canonical_id"
            else "spagent.replacement"
            if mutation.kind == "spagent_substitution"
            else document["agent_id"]
        )
        if mutation.kind == "status":
            document["status"] = "registered"
        elif mutation.kind == "tools":
            document["allowed_tools"] = ["not-allowed"]
        elif mutation.kind not in {"canonical_id", "spagent_substitution"}:
            raise AssertionError(f"Unsupported specification mutation {mutation.kind!r}.")
        _write_json(path, document)
        return

    raw_entries = document.get("agents" if mutation.target == "manifest" else "entries")
    if not isinstance(raw_entries, list):
        raise AssertionError("The local representation must contain an entry list.")
    entry_index = _target_entry_index(raw_entries, agent_id)
    entry = raw_entries[entry_index]
    if not isinstance(entry, dict):
        raise AssertionError("The local representation entry must be an object.")

    if mutation.kind == "membership":
        del raw_entries[entry_index]
    elif mutation.kind == "canonical_id":
        entry["agent_id"] = "specials.invalid-catalog-member"
    elif mutation.kind == "spagent_substitution":
        entry["agent_id"] = "spagent.replacement"
    elif mutation.kind == "path":
        entry["agent_spec_path"] = "agents/specials.invalid-catalog-member/agent_spec.json"
    elif mutation.kind == "status":
        entry["status"] = "registered"
    elif mutation.kind == "tools":
        entry["allowed_tools"] = ["not-allowed"]
    else:
        raise AssertionError(f"Unsupported manifest/inventory mutation {mutation.kind!r}.")
    _write_json(path, document)


@st.composite
def _integrity_mutations(draw: st.DrawFn) -> IntegrityMutation:
    """Generate representation changes while respecting each schema's fields."""
    kind = draw(st.sampled_from(_MUTATION_KINDS))
    agent_index = draw(st.integers(min_value=0, max_value=len(SPECIAL_AGENT_IDS) - 1))
    inventory_required = draw(st.booleans())
    if kind == "ordering":
        target: MutationTarget = "manifest"
    elif kind == "tools":
        targets: tuple[MutationTarget, ...] = ("manifest", "spec")
        target = draw(st.sampled_from(targets))
    elif kind == "path":
        targets = ("manifest", "inventory") if inventory_required else ("manifest",)
        target = draw(st.sampled_from(targets))
    elif inventory_required:
        targets = ("manifest", "inventory", "spec")
        target = draw(st.sampled_from(targets))
    else:
        targets = ("manifest", "spec")
        target = draw(st.sampled_from(targets))
    return IntegrityMutation(kind, target, agent_index, inventory_required)


def _previous_state() -> AcceptedSpecialsState:
    """Return a sentinel state that invalid proposals must preserve exactly."""
    return AcceptedSpecialsState(
        agents=(AcceptedSpecialAgent("specials.aesthetics-agent"),),
        validation_report_digest="previous-property-03-state",
    )


# **Validates: Requirements 2.1, 3.2, 3.3, 3.4**
# Feature: special-business-agents, Property 3: Manifest/specification consistency
@settings(max_examples=100, derandomize=True, database=None, deadline=None)
@given(
    manifest_order=st.permutations(SPECIAL_AGENT_IDS),
    inventory_order=st.permutations(SPECIAL_AGENT_IDS),
    mutation=_integrity_mutations(),
)
def test_specials_manifest_specification_and_inventory_integrity(
    manifest_order: list[str],
    inventory_order: list[str],
    mutation: IntegrityMutation,
) -> None:
    """Reordering passes; every generated integrity mutation fails atomically."""
    with TemporaryDirectory() as temporary_directory:
        tmp_path = Path(temporary_directory)
        inventory_required = mutation.inventory_required

        repository_root, allowlisted_paths = _write_pack_fixture(
            tmp_path,
            inventory_required=inventory_required,
            manifest_order=tuple(manifest_order),
            inventory_order=tuple(inventory_order),
        )
        previous_state = _previous_state()

        if mutation.kind == "ordering":
            report = validate_specials_pack(
                repository_root,
                allowlisted_paths,
                previous_state=previous_state,
            )
            assert report.validation_outcome == "pass"
            assert report.accepted_agent_ids == SPECIAL_AGENT_IDS
            assert report.rejected_agent_ids == ()
            assert report.findings == ()
            assert report.manifest.result == "pass"
            assert report.inventory.result == ("pass" if inventory_required else "not_required")
            return

        _apply_mutation(
            repository_root,
            allowlisted_paths,
            mutation,
            inventory_required=inventory_required,
        )
        report = validate_specials_pack(
            repository_root,
            allowlisted_paths,
            previous_state=previous_state,
        )

        assert report.validation_outcome == "fail"
        assert report.accepted_agent_ids == ()
        assert report.registration_effect == "none"
        assert report.accepted_state is previous_state
        assert report.accepted_state == previous_state
        assert report.findings

        if mutation.kind == "spagent_substitution":
            expected_categories = {"asset_namespace"}
        elif mutation.kind == "path":
            expected_categories = {"path", "integrity"}
        elif mutation.kind in {"status", "tools"}:
            expected_categories = {"schema"}
        else:
            expected_categories = {"integrity"}
        assert any(finding.category in expected_categories for finding in report.findings)
