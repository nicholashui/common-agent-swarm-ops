"""Property checks for fully reviewed normal and urgent Video Pack refreshes."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import example, given, settings, strategies as st

from app.video.migration.approval import verify_human_import_gate
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    HistoricalProvenance,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import (
    validate_corpus_integrity,
    write_corpus,
)
from app.video.migration.documentation import (
    ChangedMapReview,
    RefreshKind,
    RefreshRequest,
    orchestrate_refresh,
    write_local_documentation,
)
from app.video.migration.intake import plan_source_intake

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_SOURCE_REPOSITORY = "https://example.invalid/video-source"
_SOURCE_PATH = "upstream/video/guide.md"
_COMMON_AGENT_ID = "video.editor"
_REVIEWER = "property-16-reviewer"
_REVIEW_STATES: tuple[str, ...] = ("valid", "missing", "failed", "mismatched")
_SAFE_TEXT = st.text(
    alphabet=st.characters(
        whitelist_categories=("Ll", "Lu", "Nd"),
        whitelist_characters=" \n-_.",
    ),
    min_size=1,
    max_size=24,
)


@dataclass(frozen=True, slots=True)
class RefreshDelta:
    """A small source/map delta and the review state applied to it."""

    refresh_kind: RefreshKind
    before: str
    after: str
    map_changed: bool
    review_state: str


@st.composite
def _refresh_deltas(draw: st.DrawFn) -> RefreshDelta:
    """Generate bounded normal/urgent refreshes with optional map changes."""
    before, after = draw(st.tuples(_SAFE_TEXT, _SAFE_TEXT).filter(lambda pair: pair[0] != pair[1]))
    map_changed = draw(st.booleans())
    return RefreshDelta(
        refresh_kind=draw(st.sampled_from((RefreshKind.NORMAL, RefreshKind.URGENT))),
        before=before,
        after=after,
        map_changed=map_changed,
        review_state=(draw(st.sampled_from(_REVIEW_STATES)) if map_changed else "valid"),
    )


def _snapshot(source_root: Path, commit: str) -> SourceSnapshot:
    """Build a fixed-time pinned source snapshot for one refresh phase."""
    return SourceSnapshot(
        source_repository=_SOURCE_REPOSITORY,
        source_commit=commit,
        source_root=str(source_root),
        recorded_at=_NOW,
    )


def _provenance(commit: str) -> HistoricalProvenance:
    """Build the historical-only provenance retained in the refreshed manifest."""
    return HistoricalProvenance(
        repository=_SOURCE_REPOSITORY,
        commit=commit,
        path=_SOURCE_PATH,
        license_status="reviewed",
    )


def _approved_set(
    snapshot: SourceSnapshot,
    provenance: HistoricalProvenance,
    content: str,
    approval_id: str,
) -> ApprovedImportSet:
    """Create the exact reviewed file set for one pinned source snapshot."""
    payload = content.encode("utf-8")
    approved_file = ApprovedImportFile(
        source_path="guide.md",
        destination_path="guide.md",
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        original_repository=provenance.repository,
        original_commit=provenance.commit,
        original_path=provenance.path,
        license_status=provenance.license_status,
    )
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(approved_file,),
        total_bytes=len(payload),
        license_status="reviewed",
        approved_by=_REVIEWER,
        approved_at=_NOW,
        approval_id=approval_id,
    )


def _create_video_pack(repository_root: Path) -> Path:
    """Create the minimal local pack needed for truthful documentation checks."""
    video_root = repository_root / "business" / "video"
    agent_root = video_root / "agents" / _COMMON_AGENT_ID
    agent_root.mkdir(parents=True)
    (agent_root / "agent_spec.json").write_text("{}\n", encoding="utf-8")
    workflow_root = video_root / "workflows"
    workflow_root.mkdir(parents=True)
    (workflow_root / "pack_spine.json").write_text("{}\n", encoding="utf-8")
    return video_root


def _tree_bytes(root: Path) -> tuple[tuple[str, bytes], ...]:
    """Capture a deterministic destination snapshot for blocked refreshes."""
    if not root.exists():
        return ()
    return tuple(
        sorted(
            (
                path.relative_to(root).as_posix(),
                path.read_bytes(),
            )
            for path in root.rglob("*")
            if path.is_file()
        )
    )


def _map_records(changed: bool) -> tuple[dict[str, object], dict[str, object]]:
    """Return a one-entry map before/after pair with a bounded semantic delta."""
    before: dict[str, object] = {
        "entries": [
            {
                "common_agent_id": _COMMON_AGENT_ID,
                "mapping_status": "exact",
                "source_agent_ids": ["source.editor"],
                "source_documents": ["map.md"],
                "rationale": "The source editing role matches the local editor role.",
            }
        ]
    }
    after: dict[str, object] = {
        "entries": [
            {
                "common_agent_id": _COMMON_AGENT_ID,
                "mapping_status": "exact",
                "source_agent_ids": ["source.editor"],
                "source_documents": ["map.md"],
                "rationale": (
                    "The refreshed source editing role matches the local editor role."
                    if changed
                    else "The source editing role matches the local editor role."
                ),
            }
        ]
    }
    return before, after


def _changed_map_review(state: str) -> ChangedMapReview | None:
    """Build one exact, missing, failed, or mismatched changed-map review."""
    if state == "valid":
        return ChangedMapReview(
            review_id="property-16-map-review",
            reviewer=_REVIEWER,
            reviewed_at=_NOW,
            common_agent_ids=(_COMMON_AGENT_ID,),
            result="pass",
        )
    if state == "missing":
        return None
    if state == "failed":
        return ChangedMapReview(
            review_id="property-16-map-review",
            reviewer=_REVIEWER,
            reviewed_at=_NOW,
            common_agent_ids=(_COMMON_AGENT_ID,),
            result="fail",
        )
    if state == "mismatched":
        return ChangedMapReview(
            review_id="property-16-map-review",
            reviewer=_REVIEWER,
            reviewed_at=_NOW,
            common_agent_ids=("video.other",),
            result="pass",
        )
    raise AssertionError(f"Unhandled changed-map review state: {state}")


def _seed_initial_corpus(
    source_root: Path,
    destination_root: Path,
    content: str,
) -> None:
    """Publish the predecessor corpus that the refresh must update."""
    snapshot = _snapshot(source_root, "snapshot-before")
    provenance = _provenance("snapshot-before")
    approved = _approved_set(snapshot, provenance, content, "property-16-before")
    plan = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        license_status="reviewed",
    )
    approval = verify_human_import_gate(
        plan,
        approved,
        license_status="reviewed",
        provenance=provenance,
        declared_destinations=("guide.md",),
    )
    assert approval.is_approved
    write = write_corpus(destination_root, approved, verification=approval)
    assert write.result is MigrationResult.PASS


def _run_refresh(case: RefreshDelta) -> tuple[RefreshDelta, object, Path]:
    """Materialize one predecessor and execute one reviewed refresh."""
    with TemporaryDirectory() as temporary_root:
        repository_root = Path(temporary_root)
        source_root = repository_root / "source"
        source_root.mkdir()
        source_file = source_root / "guide.md"
        source_file.write_text(case.before, encoding="utf-8", newline="\n")
        video_root = _create_video_pack(repository_root)
        destination_root = video_root / "corpus"
        _seed_initial_corpus(source_root, destination_root, case.before)
        documentation = write_local_documentation(
            repository_root,
            video_root=video_root,
        )
        assert documentation.is_valid
        before_tree = _tree_bytes(destination_root)

        source_file.write_text(case.after, encoding="utf-8", newline="\n")
        snapshot = _snapshot(source_root, "snapshot-after")
        provenance = _provenance("snapshot-after")
        approved = _approved_set(snapshot, provenance, case.after, "property-16-after")
        map_before, map_after = _map_records(case.map_changed)
        report = orchestrate_refresh(
            RefreshRequest(
                source_root=source_root,
                snapshot=snapshot,
                destination_root=destination_root,
                repository_root=repository_root,
                approved_import_set=approved,
                refresh_kind=case.refresh_kind,
                write_mode=True,
                license_status="reviewed",
                provenance=provenance,
                map_before=map_before,
                map_after=map_after,
                changed_map_review=_changed_map_review(case.review_state),
                standalone_check=lambda _request: True,
                evidence_recorder=lambda _report: True,
            )
        )
        # Return only the report and a stable copy of the destination state. The
        # temporary root remains alive for all assertions in this helper's caller.
        return case, (report, before_tree), destination_root


# Feature: migration-redesign, Property 16: Refreshes are full reviewed migrations.
# **Validates: Requirements 10.6, 10.7, 10.8, 10.9, 10.10**
@settings(max_examples=20, deadline=None, derandomize=True)
@example(RefreshDelta(RefreshKind.NORMAL, "before", "after", True, "valid"))
@example(RefreshDelta(RefreshKind.URGENT, "before", "after", True, "valid"))
@given(case=_refresh_deltas())
def test_property_16_normal_and_urgent_refreshes_are_full_reviewed_migrations(
    case: RefreshDelta,
) -> None:
    """Refresh deltas use every gate, update corpus provenance, or fail closed."""
    with TemporaryDirectory() as temporary_root:
        repository_root = Path(temporary_root)
        source_root = repository_root / "source"
        source_root.mkdir()
        source_file = source_root / "guide.md"
        source_file.write_text(case.before, encoding="utf-8", newline="\n")
        video_root = _create_video_pack(repository_root)
        destination_root = video_root / "corpus"
        _seed_initial_corpus(source_root, destination_root, case.before)
        write_local_documentation(repository_root, video_root=video_root)
        before_tree = _tree_bytes(destination_root)
        before_integrity = validate_corpus_integrity(destination_root)
        assert before_integrity.is_valid

        source_file.write_text(case.after, encoding="utf-8", newline="\n")
        snapshot = _snapshot(source_root, "snapshot-after")
        provenance = _provenance("snapshot-after")
        approved = _approved_set(snapshot, provenance, case.after, "property-16-after")
        map_before, map_after = _map_records(case.map_changed)
        changed_review = _changed_map_review(case.review_state)

        report = orchestrate_refresh(
            RefreshRequest(
                source_root=source_root,
                snapshot=snapshot,
                destination_root=destination_root,
                repository_root=repository_root,
                approved_import_set=approved,
                refresh_kind=case.refresh_kind,
                write_mode=True,
                license_status="reviewed",
                provenance=provenance,
                map_before=map_before,
                map_after=map_after,
                changed_map_review=changed_review,
                standalone_check=lambda _request: True,
                evidence_recorder=lambda _report: True,
            )
        )

        assert report.refresh_kind is case.refresh_kind
        assert report.approval_verified
        assert report.provenance_preserved
        assert "pinned_snapshot" in report.steps
        assert "pinned_dry_run" in report.steps
        assert "exact_approval" in report.steps
        assert "standalone" in report.steps
        assert "evidence" in report.steps

        invalid_review = case.map_changed and case.review_state != "valid"
        if invalid_review:
            assert report.result is MigrationResult.BLOCKED
            assert not report.completion_gate_passed
            assert report.changed_map_agent_ids == (_COMMON_AGENT_ID,)
            assert "changed_map_review" in report.steps
            assert "corpus_manifest_blocked" in report.steps
            assert any(
                finding.code == "refresh_changed_map_review_required" for finding in report.findings
            )
            assert _tree_bytes(destination_root) == before_tree
            assert validate_corpus_integrity(destination_root).manifest_digest == (
                before_integrity.manifest_digest
            )
            return

        assert report.result is MigrationResult.PASS
        assert report.completion_gate_passed
        assert report.standalone_passed
        assert report.evidence_recorded
        if case.map_changed:
            assert report.changed_map_agent_ids == (_COMMON_AGENT_ID,)
            assert changed_review is not None and changed_review.is_approved
            assert "changed_map_review" in report.steps
        else:
            assert report.changed_map_agent_ids == ()
            assert "changed_map_review_not_required" in report.steps
        assert "corpus_manifest" in report.steps
        assert "corpus_integrity" in report.steps

        after_integrity = validate_corpus_integrity(destination_root)
        assert after_integrity.is_valid
        assert after_integrity.manifest_digest == report.corpus_manifest_digest
        assert after_integrity.manifest_digest != before_integrity.manifest_digest
        assert after_integrity.entries[0].original_repository == provenance.repository
        assert after_integrity.entries[0].original_commit == provenance.commit
        assert after_integrity.entries[0].original_path == provenance.path
        assert (destination_root / "guide.md").read_text(encoding="utf-8") == case.after


# **Validates: Requirements 10.6, 10.8, 10.9, 10.10**
@settings(max_examples=8, deadline=None, derandomize=True)
@example(RefreshDelta(RefreshKind.NORMAL, "old", "new", True, "failed"))
@example(RefreshDelta(RefreshKind.URGENT, "old", "new", True, "missing"))
@given(
    case=_refresh_deltas().map(
        lambda value: RefreshDelta(
            value.refresh_kind,
            value.before,
            value.after,
            True,
            "mismatched",
        )
    )
)
def test_property_16_invalid_changed_map_reviews_block_both_refresh_kinds(
    case: RefreshDelta,
) -> None:
    """Normal and urgent refreshes reject missing, failed, or mismatched map reviews."""
    with TemporaryDirectory() as temporary_root:
        repository_root = Path(temporary_root)
        source_root = repository_root / "source"
        source_root.mkdir()
        source_file = source_root / "guide.md"
        source_file.write_text(case.before, encoding="utf-8", newline="\n")
        video_root = _create_video_pack(repository_root)
        destination_root = video_root / "corpus"
        _seed_initial_corpus(source_root, destination_root, case.before)
        write_local_documentation(repository_root, video_root=video_root)
        before_tree = _tree_bytes(destination_root)

        source_file.write_text(case.after, encoding="utf-8", newline="\n")
        snapshot = _snapshot(source_root, "snapshot-after")
        provenance = _provenance("snapshot-after")
        approved = _approved_set(snapshot, provenance, case.after, "property-16-after")
        map_before, map_after = _map_records(True)
        report = orchestrate_refresh(
            RefreshRequest(
                source_root=source_root,
                snapshot=snapshot,
                destination_root=destination_root,
                repository_root=repository_root,
                approved_import_set=approved,
                refresh_kind=case.refresh_kind,
                write_mode=True,
                license_status="reviewed",
                provenance=provenance,
                map_before=map_before,
                map_after=map_after,
                changed_map_review=_changed_map_review(case.review_state),
                standalone_check=lambda _request: True,
                evidence_recorder=lambda _report: True,
            )
        )

        assert report.refresh_kind is case.refresh_kind
        assert report.approval_verified
        assert report.result is MigrationResult.BLOCKED
        assert not report.completion_gate_passed
        assert report.changed_map_agent_ids == (_COMMON_AGENT_ID,)
        assert any(
            finding.code == "refresh_changed_map_review_required" for finding in report.findings
        )
        assert _tree_bytes(destination_root) == before_tree
