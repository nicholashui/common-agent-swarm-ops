"""Property checks for complete, substantive, local Video Pack specifications."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final, cast

from hypothesis import example, given, settings, strategies as st

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT
from app.video.migration.agent_mapping import inventory_digest
from app.video.migration.contracts import AgentSourceMapEntry, MappingStatus
from app.video.migration.specifications import (
    REQUIRED_HEADINGS,
    SpecificationIssue,
    build_specification_document,
    build_specifications,
    validate_specification_document,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_INVENTORY_PATH: Final[Path] = _REPOSITORY_ROOT / "business" / "video" / "inventory.json"
_REVIEWED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_REVIEWED_AT_TEXT: Final[str] = "2025-01-01T12:00:00Z"
_REVIEWER: Final[str] = "specification-reviewer-property-09"
_PROPERTY_AGENT_ID: Final[str] = "video.property_09_agent"
_MUTATION_KINDS: Final[tuple[str, ...]] = (
    "valid",
    "missing_heading",
    "duplicate_heading",
    "generic_responsibility",
    "missing_local_reference",
    "external_local_reference",
    "nonhistorical_provenance",
)
_AGGREGATE_MUTATIONS: Final[tuple[str, ...]] = (
    "missing_heading",
    "generic_responsibility",
    "missing_local_reference",
)


def _load_fixed_inventory() -> dict[str, object]:
    """Load the checked-in authoritative inventory used by the property."""
    parsed: object = json.loads(_INVENTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise AssertionError("The fixed inventory fixture must be a JSON object.")
    return parsed


def _inventory_ids(inventory: dict[str, object]) -> tuple[str, ...]:
    """Extract the authoritative Common Agent IDs in inventory order."""
    raw_entries = inventory.get("entries")
    if not isinstance(raw_entries, list):
        raise AssertionError("The fixed inventory fixture must contain an entries array.")
    agent_ids: list[str] = []
    for entry in raw_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("agent_id"), str):
            raise AssertionError("The fixed inventory fixture must contain string agent IDs.")
        agent_ids.append(entry["agent_id"])
    return tuple(agent_ids)


_FIXED_INVENTORY: Final[dict[str, object]] = _load_fixed_inventory()
_FIXED_AGENT_IDS: Final[tuple[str, ...]] = _inventory_ids(_FIXED_INVENTORY)
assert len(_FIXED_AGENT_IDS) == EXPECTED_VIDEO_AGENT_COUNT == 114
assert len(set(_FIXED_AGENT_IDS)) == EXPECTED_VIDEO_AGENT_COUNT


@dataclass(frozen=True, slots=True)
class SpecificationMutation:
    """One bounded mutation applied to a valid local specification document."""

    kind: str
    heading: str | None = None


@st.composite
def _specification_mutations(draw: st.DrawFn) -> SpecificationMutation:
    """Generate heading, responsibility, and reference mutations."""
    kind = draw(st.sampled_from(_MUTATION_KINDS))
    heading = (
        draw(st.sampled_from(REQUIRED_HEADINGS))
        if kind in {"missing_heading", "duplicate_heading"}
        else None
    )
    return SpecificationMutation(kind=kind, heading=heading)


def _runtime_binding(agent_id: str, *, role: str | None = None) -> dict[str, object]:
    """Return a complete non-active local runtime binding for a test agent."""
    return {
        "agent_id": agent_id,
        "allowed_tools": [],
        "budget_policy": {
            "max_input_tokens": 2048,
            "max_output_tokens": 1024,
            "max_tool_requests": 0,
        },
        "critique_edges": {"inputs": [], "outputs": []},
        "max_refinement_count": 2,
        "model_policy": {
            "model_id": "local-video-property-09",
            "network_access": False,
            "provider": "local_deterministic",
        },
        "production_activation_requested": False,
        "prompt_reference": f"video.prompt.{agent_id}.v1",
        "role": role or "Video editor configuration specialist",
        "rubric_reference": f"video.rubric.{agent_id}.v1",
        "schema_version": "1.0",
        "status": "registered",
    }


def _mapping_entry(
    agent_id: str,
    *,
    source_document: str = "mapping/property-09.md",
) -> AgentSourceMapEntry:
    """Return one reviewed local mapping entry for a generated specification."""
    return AgentSourceMapEntry(
        common_agent_id=agent_id,
        mapping_status=MappingStatus.EXACT,
        source_agent_ids=(f"source.{agent_id}",),
        source_documents=(source_document,),
        rationale=f"Human-reviewed video responsibility relationship for {agent_id}.",
        reviewed_by=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
    )


def _prepare_single_spec_fixture(
    tmp_path: Path,
) -> tuple[Path, Path, dict[str, object], AgentSourceMapEntry]:
    """Create the local files needed by singular SPEC validation."""
    repository_root = tmp_path / "repository"
    video_root = repository_root / "business" / "video"
    agent_dir = video_root / "agents" / _PROPERTY_AGENT_ID
    agent_dir.mkdir(parents=True)
    (video_root / "mapping").mkdir(parents=True)
    (video_root / "inventory.json").write_text("{}", encoding="utf-8")
    (video_root / "mapping" / "property-09.md").write_text(
        "Local property-test mapping document.\n", encoding="utf-8"
    )
    runtime_binding = _runtime_binding(_PROPERTY_AGENT_ID)
    (agent_dir / "agent_spec.json").write_text(
        json.dumps(runtime_binding, sort_keys=True), encoding="utf-8"
    )
    return repository_root, video_root, runtime_binding, _mapping_entry(_PROPERTY_AGENT_ID)


def _valid_document(
    tmp_path: Path,
) -> tuple[Path, Path, dict[str, object], AgentSourceMapEntry, str]:
    """Build a valid local SPEC document and its local validation context."""
    repository_root, video_root, runtime_binding, mapping_entry = _prepare_single_spec_fixture(
        tmp_path
    )
    document = build_specification_document(
        _PROPERTY_AGENT_ID,
        runtime_binding,
        mapping_entry,
        inventory_entry={"status": "registered", "maturity_level": "L0"},
        pack_version="property-09",
    )
    return repository_root, video_root, runtime_binding, mapping_entry, document


def _section_lines(document: str, heading: str) -> tuple[list[str], int, int]:
    """Return document lines and the start/end indexes for one section."""
    lines = document.splitlines()
    marker = f"## {heading}"
    try:
        start = lines.index(marker)
    except ValueError as error:
        raise AssertionError(f"Expected generated heading is absent: {heading}") from error
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return lines, start, end


def _replace_section(document: str, heading: str, body: str) -> str:
    """Replace one generated section body while preserving its heading."""
    lines, start, end = _section_lines(document, heading)
    lines[start + 1 : end] = body.splitlines()
    return "\n".join(lines) + "\n"


def _remove_section(document: str, heading: str) -> str:
    """Remove one generated required section, including its heading."""
    lines, start, end = _section_lines(document, heading)
    del lines[start:end]
    return "\n".join(lines) + "\n"


def _duplicate_section(document: str, heading: str) -> str:
    """Append a second instance of one required heading."""
    return document.rstrip("\r\n") + f"\n\n## {heading}\nDuplicate generated section.\n"


def _apply_mutation(document: str, mutation: SpecificationMutation) -> str:
    """Apply one generated mutation to a valid document."""
    if mutation.kind == "valid":
        return document
    if mutation.kind == "missing_heading":
        if mutation.heading is None:
            raise AssertionError("Heading mutations require a heading.")
        return _remove_section(document, mutation.heading)
    if mutation.kind == "duplicate_heading":
        if mutation.heading is None:
            raise AssertionError("Heading mutations require a heading.")
        return _duplicate_section(document, mutation.heading)
    if mutation.kind == "generic_responsibility":
        return _replace_section(document, "Responsibility", "Video agent role.")
    if mutation.kind == "missing_local_reference":
        return _replace_section(
            document,
            "Local knowledge sources",
            "The required local source was not supplied.",
        )
    if mutation.kind == "external_local_reference":
        return _replace_section(
            document,
            "Local knowledge sources",
            "- [External source](https://example.invalid/video/reference.md)",
        )
    if mutation.kind == "nonhistorical_provenance":
        return _replace_section(
            document,
            "Provenance",
            "Source information is retained for context only.",
        )
    raise AssertionError(f"Unhandled specification mutation: {mutation.kind}")


def _expected_codes(mutation: SpecificationMutation) -> set[str]:
    """Return the stable issue codes required by one generated mutation."""
    if mutation.kind == "valid":
        return set()
    if mutation.kind == "missing_heading":
        expected = {"missing_required_heading"}
        heading_effects = {
            "Identity": "identity_mismatch",
            "Responsibility": "generic_responsibility",
            "Local knowledge sources": "missing_local_knowledge_reference",
            "Provenance": "non_historical_provenance",
            "Runtime binding": "invalid_runtime_binding",
        }
        if mutation.heading in heading_effects:
            expected.add(heading_effects[cast(str, mutation.heading)])
        return expected
    if mutation.kind == "duplicate_heading":
        return {"duplicate_required_heading"}
    if mutation.kind == "generic_responsibility":
        return {"generic_responsibility"}
    if mutation.kind == "missing_local_reference":
        return {"missing_local_knowledge_reference"}
    if mutation.kind == "external_local_reference":
        return {
            "external_required_reference",
            "external_local_reference",
            "nonlocal_or_missing_knowledge_reference",
        }
    if mutation.kind == "nonhistorical_provenance":
        return {"non_historical_provenance"}
    raise AssertionError(f"Unhandled expected mutation: {mutation.kind}")


def _issue_codes(issues: tuple[SpecificationIssue, ...]) -> set[str]:
    """Project validator issues to their stable diagnostic codes."""
    return {issue.code for issue in issues}


def _base_source_map() -> dict[str, object]:
    """Build a reviewed source map matching every fixed inventory identity."""
    entries: list[dict[str, object]] = []
    for index, agent_id in enumerate(_FIXED_AGENT_IDS):
        source_document = f"mapping/property-09-{index:03d}.md"
        entries.append(
            {
                "common_agent_id": agent_id,
                "mapping_status": "common_only" if index == 0 else "exact",
                "source_agent_ids": [] if index == 0 else [f"source.video-role-{index}"],
                "source_documents": [source_document],
                "rationale": f"Human-reviewed video responsibility relationship for {agent_id}.",
                "reviewed_by": _REVIEWER,
                "reviewed_at": _REVIEWED_AT_TEXT,
            }
        )
    return {
        "schema_version": "1.0",
        "inventory_digest": inventory_digest(_FIXED_AGENT_IDS),
        "entries": entries,
    }


def _write_complete_local_pack(
    root: Path,
) -> tuple[Path, Path, dict[str, object], dict[str, object]]:
    """Create all local runtime and mapping inputs for a complete 114-ID pack."""
    repository_root = root / "repository"
    video_root = repository_root / "business" / "video"
    (video_root / "agents").mkdir(parents=True)
    (video_root / "mapping").mkdir(parents=True)
    (video_root / "inventory.json").write_text(
        json.dumps(_FIXED_INVENTORY, sort_keys=True), encoding="utf-8"
    )
    source_map = _base_source_map()
    raw_entries = source_map["entries"]
    if not isinstance(raw_entries, list):
        raise AssertionError("The generated source map must contain entries.")
    for index, agent_id in enumerate(_FIXED_AGENT_IDS):
        agent_dir = video_root / "agents" / agent_id
        agent_dir.mkdir()
        runtime_binding = _runtime_binding(agent_id, role=f"Video role {index}")
        (agent_dir / "agent_spec.json").write_text(
            json.dumps(runtime_binding, sort_keys=True), encoding="utf-8"
        )
        (video_root / "mapping" / f"property-09-{index:03d}.md").write_text(
            f"Local mapping document for {agent_id}.\n", encoding="utf-8"
        )
    return repository_root, video_root, _FIXED_INVENTORY, source_map


def _critical_reviews() -> dict[str, object]:
    """Provide completed local reviews for all critical IDs in the fixed inventory."""
    return {
        agent_id: {
            "reviewer": _REVIEWER,
            "reviewed_at": _REVIEWED_AT_TEXT,
            "result": "pass",
        }
        for agent_id in _FIXED_AGENT_IDS
    }


# Feature: migration-redesign, Property 9: Every specification is local, complete,
# and substantive.
# **Validates: Requirements 5.9, 6.1, 6.2, 6.3, 6.4, 6.6, 6.7, 6.8, 6.9**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(SpecificationMutation("valid"))
@example(SpecificationMutation("missing_heading", "Identity"))
@example(SpecificationMutation("missing_heading", "Responsibility"))
@example(SpecificationMutation("missing_heading", "Local knowledge sources"))
@example(SpecificationMutation("duplicate_heading", "Provenance"))
@example(SpecificationMutation("generic_responsibility"))
@example(SpecificationMutation("missing_local_reference"))
@example(SpecificationMutation("external_local_reference"))
@example(SpecificationMutation("nonhistorical_provenance"))
@given(mutation=_specification_mutations())
def test_property_09_generated_spec_mutations_preserve_local_complete_substantive_contract(
    mutation: SpecificationMutation,
) -> None:
    """Every invalid mutation reports its corresponding local SPEC failure."""
    with TemporaryDirectory() as temporary_root:
        repository_root, video_root, runtime_binding, mapping_entry, document = _valid_document(
            Path(temporary_root)
        )
        mutated = _apply_mutation(document, mutation)
        issues = validate_specification_document(
            mutated,
            _PROPERTY_AGENT_ID,
            runtime_binding,
            video_root=video_root,
            repository_root=repository_root,
            spec_path=video_root / "agents" / _PROPERTY_AGENT_ID / "SPEC.md",
            mapping_entry=mapping_entry,
        )

        issue_codes = _issue_codes(issues)
        expected_codes = _expected_codes(mutation)
        if mutation.kind == "valid":
            assert issue_codes == set()
            assert all(f"## {heading}" in document for heading in REQUIRED_HEADINGS)
        else:
            assert expected_codes <= issue_codes


def test_property_09_valid_document_has_all_required_sections_and_local_references(
    tmp_path: Path,
) -> None:
    """A generated valid SPEC contains every heading and resolves local knowledge files."""
    repository_root, video_root, runtime_binding, mapping_entry, document = _valid_document(
        tmp_path
    )
    assert all(f"## {heading}" in document for heading in REQUIRED_HEADINGS)
    assert "https://" not in document.split("## Provenance", 1)[0]
    assert "historical" in document.casefold()
    assert "non-binding" in document.casefold()

    issues = validate_specification_document(
        document,
        _PROPERTY_AGENT_ID,
        runtime_binding,
        video_root=video_root,
        repository_root=repository_root,
        spec_path=video_root / "agents" / _PROPERTY_AGENT_ID / "SPEC.md",
        mapping_entry=mapping_entry,
    )
    assert issues == ()


@settings(max_examples=6, deadline=None, derandomize=True)
@given(mutation_order=st.permutations(_AGGREGATE_MUTATIONS))
def test_property_09_builds_exactly_one_local_spec_per_id_and_aggregates_errors(
    mutation_order: tuple[str, ...],
) -> None:
    """The batch API writes one SPEC per ID and reports every mutated specification."""
    with TemporaryDirectory() as temporary_root:
        repository_root, video_root, inventory, source_map = _write_complete_local_pack(
            Path(temporary_root) / "-".join(mutation_order)
        )
        valid_report = build_specifications(
            video_root,
            repository_root=repository_root,
            inventory=inventory,
            source_map=source_map,
            critical_reviews=_critical_reviews(),
            write_mode=True,
            use_existing_specs=False,
        )

        assert valid_report.is_valid
        assert valid_report.can_write
        assert len(valid_report.drafts) == EXPECTED_VIDEO_AGENT_COUNT
        assert tuple(draft.common_agent_id for draft in valid_report.drafts) == _FIXED_AGENT_IDS
        spec_paths = tuple(sorted(video_root.rglob("SPEC.md")))
        assert len(spec_paths) == EXPECTED_VIDEO_AGENT_COUNT
        assert {path.parent.name for path in spec_paths} == set(_FIXED_AGENT_IDS)
        assert all(
            len(tuple((video_root / "agents" / agent_id).glob("SPEC.md"))) == 1
            for agent_id in _FIXED_AGENT_IDS
        )

        mutation_ids = _FIXED_AGENT_IDS[10:13]
        mutation_headings = {
            "missing_heading": "Boundaries and escalation",
            "generic_responsibility": "Responsibility",
            "missing_local_reference": "Local knowledge sources",
        }
        for agent_id, mutation_kind in zip(mutation_ids, mutation_order, strict=True):
            spec_path = video_root / "agents" / agent_id / "SPEC.md"
            document = spec_path.read_text(encoding="utf-8")
            if mutation_kind == "missing_heading":
                mutated = _remove_section(document, mutation_headings[mutation_kind])
            else:
                mutated = _apply_mutation(document, SpecificationMutation(mutation_kind))
            spec_path.write_text(mutated, encoding="utf-8")

        invalid_report = build_specifications(
            video_root,
            repository_root=repository_root,
            inventory=inventory,
            source_map=source_map,
            critical_reviews=_critical_reviews(),
            write_mode=False,
            use_existing_specs=True,
        )
        assert not invalid_report.is_valid
        issue_pairs = {(issue.agent_id, issue.code) for issue in invalid_report.issues}
        expected_codes_by_mutation = {
            "missing_heading": "missing_required_heading",
            "generic_responsibility": "generic_responsibility",
            "missing_local_reference": "missing_local_knowledge_reference",
        }
        expected_pairs = {
            (agent_id, expected_codes_by_mutation[mutation_kind])
            for agent_id, mutation_kind in zip(mutation_ids, mutation_order, strict=True)
        }
        assert expected_pairs <= issue_pairs
        assert {issue.agent_id for issue in invalid_report.issues} >= set(mutation_ids)
        assert len(invalid_report.issues) >= len(expected_pairs)
