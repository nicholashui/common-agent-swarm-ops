"""Property checks for exact, reviewed, taxonomy-preserving agent mappings."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, cast

import pytest
from hypothesis import example, given, settings, strategies as st

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT
from app.video.migration.agent_mapping import (
    AgentMappingReport,
    AgentSourceMapValidator,
    MappingWriteBlockedError,
    inventory_digest,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_INVENTORY_PATH: Final[Path] = _REPOSITORY_ROOT / "business" / "video" / "inventory.json"
_REVIEWED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_REVIEWER: Final[str] = "mapping-reviewer-property-08"
_VALID_MAPPING_KINDS: Final[frozenset[str]] = frozenset({"valid", "reuse_distinct"})
_MUTATION_KINDS: Final[tuple[str, ...]] = (
    "valid",
    "omit",
    "duplicate",
    "invalid_status",
    "ambiguous",
    "unreviewed",
    "common_only_source",
    "external_source_document",
    "reuse_distinct",
    "reuse_same",
)


def _load_fixed_inventory() -> dict[str, object]:
    """Load the checked-in authoritative 114-ID inventory fixture."""
    parsed: object = json.loads(_INVENTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise AssertionError("The fixed inventory fixture must be a JSON object.")
    return parsed


def _inventory_ids(inventory: dict[str, object]) -> tuple[str, ...]:
    """Extract the fixed inventory IDs while rejecting malformed fixture data."""
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
class MappingMutation:
    """One bounded mutation applied to a valid 114-entry reviewed map."""

    kind: str
    index: int


@st.composite
def _mapping_mutations(draw: st.DrawFn) -> MappingMutation:
    """Generate bounded taxonomy mutations without creating unbounded test data."""
    return MappingMutation(
        kind=draw(st.sampled_from(_MUTATION_KINDS)),
        index=draw(st.integers(min_value=0, max_value=EXPECTED_VIDEO_AGENT_COUNT - 1)),
    )


def _base_source_map() -> dict[str, object]:
    """Build a deterministic reviewed map for exactly the fixed inventory IDs."""
    reviewed_at = _REVIEWED_AT.isoformat().replace("+00:00", "Z")
    entries: list[dict[str, object]] = []
    for index, agent_id in enumerate(_FIXED_AGENT_IDS):
        common_only = index == 0
        source_agent_ids: list[str] = [] if common_only else [f"source.video-role-{index}"]
        entries.append(
            {
                "common_agent_id": agent_id,
                "mapping_status": "common_only" if common_only else "exact",
                "source_agent_ids": source_agent_ids,
                "source_documents": [
                    f"mapping/{agent_id.removeprefix('video.')}.md",
                ],
                "rationale": (f"Human-reviewed video responsibility relationship for {agent_id}."),
                "reviewed_by": _REVIEWER,
                "reviewed_at": reviewed_at,
            }
        )
    return {
        "schema_version": "1.0",
        "inventory_digest": inventory_digest(_FIXED_AGENT_IDS),
        "entries": entries,
    }


def _entry_dicts(source_map: dict[str, object]) -> list[dict[str, object]]:
    """Return mutable mapping entries from a test-owned map copy."""
    raw_entries = source_map.get("entries")
    if not isinstance(raw_entries, list):
        raise AssertionError("Test source maps must contain an entries array.")
    entries: list[dict[str, object]] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise AssertionError("Test source maps must contain object entries.")
        entries.append(raw_entry)
    return cast(list[dict[str, object]], raw_entries)


def _apply_mutation(mutation: MappingMutation) -> tuple[dict[str, object], set[str]]:
    """Apply one named mutation and return its expected stable diagnostic codes."""
    source_map = deepcopy(_base_source_map())
    entries = _entry_dicts(source_map)
    expected_codes: set[str] = set()

    if mutation.kind == "valid":
        return source_map, expected_codes
    if mutation.kind == "omit":
        omitted_id = _FIXED_AGENT_IDS[mutation.index]
        entries.pop(mutation.index)
        expected_codes.add("missing_common_agent_id")
        assert omitted_id not in {entry.get("common_agent_id") for entry in entries}
    elif mutation.kind == "duplicate":
        entries.append(deepcopy(entries[mutation.index]))
        expected_codes.add("duplicate_common_agent_id")
    elif mutation.kind == "invalid_status":
        entries[mutation.index]["mapping_status"] = "ambiguous"
        expected_codes.add("invalid_mapping_status")
    elif mutation.kind == "ambiguous":
        entries[mutation.index]["ambiguous"] = True
        expected_codes.add("ambiguous_mapping")
    elif mutation.kind == "unreviewed":
        entries[mutation.index]["reviewed_by"] = "unreviewed"
        expected_codes.add("missing_human_review")
    elif mutation.kind == "common_only_source":
        entries[0]["mapping_status"] = "common_only"
        entries[0]["source_agent_ids"] = ["source.video-role-common-only"]
        expected_codes.add("common_only_has_source_agents")
    elif mutation.kind == "external_source_document":
        entries[mutation.index]["source_documents"] = [
            "https://example.invalid/video/source-role.md"
        ]
        expected_codes.add("external_source_document")
    elif mutation.kind in {"reuse_distinct", "reuse_same"}:
        shared_source = "source.video-role-shared"
        for index in (0, 1):
            entries[index]["mapping_status"] = "exact"
            entries[index]["source_agent_ids"] = [shared_source]
        entries[0]["rationale"] = "Shared source role covers the orchestration boundary."
        entries[1]["rationale"] = (
            "Shared source role covers the compliance boundary."
            if mutation.kind == "reuse_distinct"
            else entries[0]["rationale"]
        )
        if mutation.kind == "reuse_same":
            expected_codes.add("reused_source_rationale_not_distinct")
    else:
        raise AssertionError(f"Unhandled mapping mutation: {mutation.kind}")

    return source_map, expected_codes


def _assert_valid_mapping(report: AgentMappingReport) -> None:
    """Assert exact identity, review ordering, and Common-ID-only projections."""
    assert report.is_valid
    assert report.inventory_agent_ids == _FIXED_AGENT_IDS
    assert report.map_agent_ids == _FIXED_AGENT_IDS
    assert tuple(entry.common_agent_id for entry in report.reviewed_entries) == _FIXED_AGENT_IDS
    assert report.can_write_specifications
    report.require_write_mode(True)

    projections = report.projections()
    raw_roster_entries = projections.roster.get("entries")
    assert isinstance(raw_roster_entries, list)
    roster_ids = tuple(
        entry["agent_id"]
        for entry in raw_roster_entries
        if isinstance(entry, dict) and isinstance(entry.get("agent_id"), str)
    )
    assert roster_ids == _FIXED_AGENT_IDS
    assert all(
        "source_agent_ids" not in entry and "source_agent_id" not in entry
        for entry in raw_roster_entries
        if isinstance(entry, dict)
    )


# Feature: migration-redesign, Property 8: Agent mapping is exact, reviewed, and
# taxonomy-preserving.
# **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(MappingMutation("valid", 0))
@example(MappingMutation("omit", 0))
@example(MappingMutation("duplicate", 1))
@example(MappingMutation("invalid_status", 2))
@example(MappingMutation("ambiguous", 3))
@example(MappingMutation("unreviewed", 4))
@example(MappingMutation("common_only_source", 0))
@example(MappingMutation("external_source_document", 5))
@example(MappingMutation("reuse_distinct", 0))
@example(MappingMutation("reuse_same", 0))
@given(mutation=_mapping_mutations())
def test_property_08_agent_mapping_is_exact_reviewed_and_taxonomy_preserving(
    mutation: MappingMutation,
) -> None:
    """Only exact, reviewed, non-ambiguous maps may cross the write boundary."""
    source_map, expected_codes = _apply_mutation(mutation)
    validator = AgentSourceMapValidator()
    report = validator.validate(_FIXED_INVENTORY, source_map)

    if mutation.kind in _VALID_MAPPING_KINDS:
        _assert_valid_mapping(report)
        return

    assert not report.is_valid
    issue_codes = {issue.code for issue in report.issues}
    assert expected_codes <= issue_codes
    assert not report.can_write_specifications
    with pytest.raises(MappingWriteBlockedError):
        report.require_write_mode(True)
    with pytest.raises(MappingWriteBlockedError):
        validator.validate_for_specification_write(
            _FIXED_INVENTORY,
            source_map,
            write_mode=True,
        )


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    (
        (MappingMutation("omit", 0), "missing_common_agent_id"),
        (MappingMutation("duplicate", 1), "duplicate_common_agent_id"),
        (MappingMutation("invalid_status", 2), "invalid_mapping_status"),
        (MappingMutation("ambiguous", 3), "ambiguous_mapping"),
        (MappingMutation("unreviewed", 4), "missing_human_review"),
        (MappingMutation("common_only_source", 0), "common_only_has_source_agents"),
        (MappingMutation("reuse_same", 0), "reused_source_rationale_not_distinct"),
    ),
)
def test_explicit_invalid_mapping_examples_block_write_mode(
    mutation: MappingMutation,
    expected_code: str,
) -> None:
    """Minimal omissions, duplicates, review failures, and reuse errors fail closed."""
    source_map, _ = _apply_mutation(mutation)
    report = AgentSourceMapValidator().validate(_FIXED_INVENTORY, source_map)

    assert not report.is_valid
    assert expected_code in {issue.code for issue in report.issues}
    with pytest.raises(MappingWriteBlockedError):
        report.require_write_mode(True)


def test_common_only_and_distinct_reused_source_examples_are_accepted() -> None:
    """A reviewed common-only role and distinct rationale for source reuse are valid."""
    validator = AgentSourceMapValidator()

    common_only_report = validator.validate(_FIXED_INVENTORY, _base_source_map())
    assert common_only_report.is_valid
    assert common_only_report.reviewed_entries[0].mapping_status.value == "common_only"
    assert common_only_report.reviewed_entries[0].source_agent_ids == ()

    distinct_source_map, _ = _apply_mutation(MappingMutation("reuse_distinct", 0))
    distinct_report = validator.validate(_FIXED_INVENTORY, distinct_source_map)
    assert distinct_report.is_valid
    assert distinct_report.reviewed_entries[0].source_agent_ids == ("source.video-role-shared",)
    assert distinct_report.reviewed_entries[1].source_agent_ids == ("source.video-role-shared",)
