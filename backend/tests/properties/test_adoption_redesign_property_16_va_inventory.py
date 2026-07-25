"""Property checks for complete frozen VA inventory and roster evidence."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from hypothesis import example, given, settings, strategies as st

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT, VideoInventoryValidator

_AGENT_IDS = tuple(f"video.agent-{index:03d}" for index in range(EXPECTED_VIDEO_AGENT_COUNT))
_SOURCE_DISPOSITIONS = ("retain", "migrate", "deprecate", "exclude", "quarantine")
_SOURCE_INVALIDATIONS = (
    "none",
    "hash",
    "owner",
    "classification",
    "missing_disposition",
    "invalid_disposition",
)
_ROSTER_MUTATIONS = ("valid", "missing", "duplicate", "extra", "missing_mapping")


@dataclass(frozen=True, slots=True)
class InventoryEvidenceCase:
    """Bounded source-index and indexed-roster evidence variations."""

    asset_count: int
    source_invalidated_field: str
    roster_mutation: str
    mutation_index: int


@st.composite
def _inventory_evidence_cases(draw: st.DrawFn) -> InventoryEvidenceCase:
    """Generate complete evidence and one bounded invalidation at a time."""
    asset_count = draw(st.integers(min_value=1, max_value=4))
    return InventoryEvidenceCase(
        asset_count=asset_count,
        source_invalidated_field=draw(st.sampled_from(_SOURCE_INVALIDATIONS)),
        roster_mutation=draw(st.sampled_from(_ROSTER_MUTATIONS)),
        mutation_index=draw(st.integers(min_value=0, max_value=EXPECTED_VIDEO_AGENT_COUNT - 1)),
    )


def _manifest() -> dict[str, object]:
    """Build the smallest valid canonical 114-agent manifest."""
    return {
        "pack_id": "video",
        "production_activation_requested": False,
        "validation": {"expected_agent_count": EXPECTED_VIDEO_AGENT_COUNT},
        "agents": [
            {
                "agent_id": agent_id,
                "status": "draft",
                "agent_spec_path": f"agents/{agent_id}/agent_spec.json",
                "allowed_tools": [],
            }
            for agent_id in _AGENT_IDS
        ],
    }


def _inventory() -> dict[str, object]:
    """Build the matching valid canonical 114-agent inventory."""
    return {
        "pack_id": "video",
        "entries": [
            {
                "agent_id": agent_id,
                "status": "draft",
                "agent_spec_path": f"agents/{agent_id}/agent_spec.json",
                "maturity_level": "L0",
            }
            for agent_id in _AGENT_IDS
        ],
    }


def _source_index(case: InventoryEvidenceCase) -> list[dict[str, object]]:
    """Build a frozen source index with at most one generated field defect."""
    entries: list[dict[str, object]] = [
        {
            "asset_id": f"va-source-{index}",
            "asset_hash": f"sha256:property-16-{index}",
            "owner": f"va-owner-{index}",
            "license_or_consent_classification": "consent:approved",
            "disposition": _SOURCE_DISPOSITIONS[index % len(_SOURCE_DISPOSITIONS)],
        }
        for index in range(case.asset_count)
    ]
    target = case.mutation_index % case.asset_count
    if case.source_invalidated_field == "hash":
        entries[target].pop("asset_hash")
    elif case.source_invalidated_field == "owner":
        entries[target].pop("owner")
    elif case.source_invalidated_field == "classification":
        entries[target].pop("license_or_consent_classification")
    elif case.source_invalidated_field == "missing_disposition":
        entries[target].pop("disposition")
    elif case.source_invalidated_field == "invalid_disposition":
        entries[target]["disposition"] = "unrecognized"
    return entries


def _roster(case: InventoryEvidenceCase) -> list[dict[str, object]]:
    """Build one mapping per indexed agent and apply a bounded roster mutation."""
    entries: list[dict[str, object]] = [
        {
            "agent_id": agent_id,
            "mapping": f"VA_Domain_Pack:{agent_id}",
        }
        for agent_id in _AGENT_IDS
    ]
    target = case.mutation_index
    if case.roster_mutation == "missing":
        entries.pop(target)
    elif case.roster_mutation == "duplicate":
        entries[target]["agent_id"] = _AGENT_IDS[(target + 1) % EXPECTED_VIDEO_AGENT_COUNT]
    elif case.roster_mutation == "extra":
        entries.append(
            {
                "agent_id": "video.agent-extra",
                "mapping": "VA_Domain_Pack:video.agent-extra",
            }
        )
    elif case.roster_mutation == "missing_mapping":
        entries[target].pop("mapping")
    return entries


# Feature: adoption-redesign, Property 16: Frozen VA inventory and roster evidence are complete
# **Validates: Requirements 6.2, 6.3, 6.4**
@settings(max_examples=100, deadline=None)
@example(InventoryEvidenceCase(1, "none", "valid", 0))
@example(InventoryEvidenceCase(2, "hash", "valid", 0))
@example(InventoryEvidenceCase(2, "owner", "valid", 1))
@example(InventoryEvidenceCase(2, "classification", "valid", 0))
@example(InventoryEvidenceCase(2, "missing_disposition", "valid", 1))
@example(InventoryEvidenceCase(2, "invalid_disposition", "valid", 0))
@example(InventoryEvidenceCase(1, "none", "missing", 0))
@example(InventoryEvidenceCase(1, "none", "duplicate", 1))
@example(InventoryEvidenceCase(1, "none", "extra", 2))
@example(InventoryEvidenceCase(1, "none", "missing_mapping", 3))
@given(case=_inventory_evidence_cases())
def test_property_16_frozen_va_inventory_and_roster_evidence_are_complete(
    case: InventoryEvidenceCase,
) -> None:
    """Registration preparation requires complete source and roster evidence."""
    validator = VideoInventoryValidator()
    source_index = _source_index(case)
    roster = _roster(case)
    source_report = validator.validate_source_index(source_index)
    roster_report = validator.validate_roster(roster, _AGENT_IDS)
    preparation = validator.validate_migration_inventory(
        _manifest(),
        _inventory(),
        source_index,
        roster,
    )

    source_is_complete = case.source_invalidated_field == "none"
    roster_is_complete = case.roster_mutation == "valid"
    expected_success = source_is_complete and roster_is_complete

    assert source_report.is_valid is source_is_complete
    assert roster_report.is_valid is roster_is_complete
    assert preparation.is_valid is expected_success
    assert preparation.source_index_valid is source_is_complete
    assert preparation.roster_valid is roster_is_complete

    if expected_success:
        assert len(source_report.asset_ids) == case.asset_count
        assert len(roster_report.agent_ids) == EXPECTED_VIDEO_AGENT_COUNT
        assert Counter(roster_report.agent_ids) == Counter(_AGENT_IDS)
        assert preparation.source_index_asset_ids == source_report.asset_ids
        assert preparation.roster_agent_ids == roster_report.agent_ids
    else:
        assert preparation.issues
