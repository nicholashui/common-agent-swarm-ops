"""Focused tests for documentation integrity and reviewed refresh orchestration."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from app.video.migration.approval import verify_human_import_gate
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import write_corpus
from app.video.migration.documentation import (
    RefreshKind,
    RefreshOrchestrator,
    RefreshRequest,
    changed_map_entries,
    check_documentation_integrity,
    collect_local_asset_snapshot,
    write_local_documentation,
)
from app.video.migration.intake import plan_source_intake

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)


def _snapshot(source_root: Path, commit: str = "commit-1") -> SourceSnapshot:
    return SourceSnapshot("https://example.invalid/video", commit, str(source_root), _NOW)


def _create_video_pack(root: Path) -> Path:
    video_root = root / "business" / "video"
    (video_root / "agents" / "video.editor").mkdir(parents=True)
    (video_root / "agents" / "video.editor" / "agent_spec.json").write_text("{}", encoding="utf-8")
    (video_root / "workflows").mkdir(parents=True)
    (video_root / "workflows" / "pack_spine.json").write_text("{}", encoding="utf-8")
    (video_root / "schemas").mkdir(parents=True)
    (video_root / "schemas" / "pack.json").write_text("{}", encoding="utf-8")
    return video_root


def _approved_set(snapshot: SourceSnapshot, content: bytes) -> ApprovedImportSet:
    digest = hashlib.sha256(content).hexdigest()
    approved_file = ApprovedImportFile(
        source_path="guide.md",
        destination_path="guide.md",
        size_bytes=len(content),
        sha256=digest,
        original_repository=snapshot.source_repository,
        original_commit=snapshot.source_commit,
        original_path="guide.md",
        license_status="reviewed",
    )
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(approved_file,),
        total_bytes=len(content),
        license_status="reviewed",
        approved_by="reviewer-1",
        approved_at=_NOW,
        approval_id="approval-1",
    )


def test_documentation_reports_missing_assets_deterministically_without_operation_blocking(
    tmp_path: Path,
) -> None:
    video_root = _create_video_pack(tmp_path)
    (tmp_path / "adoption.md").write_text(
        "common-agent-swarm-ops owns business/video. 2 agents are documented. "
        "business/video/corpus/MANIFEST.json is checked in.",
        encoding="utf-8",
    )
    (tmp_path / "structure.md").write_text(
        "common-agent-swarm-ops owns business/video. 2 agents are documented.",
        encoding="utf-8",
    )
    (video_root / "README.md").write_text(
        "common-agent-swarm-ops is the Common Repository. "
        "business/video/corpus/MANIFEST.json is the local manifest.",
        encoding="utf-8",
    )

    report = check_documentation_integrity(tmp_path)
    repeat = check_documentation_integrity(tmp_path)

    assert report.result is MigrationResult.FAIL
    assert report.canonical_json() == repeat.canonical_json()
    assert any(finding.code == "documentation_asset_missing" for finding in report.findings)
    assert report.allows_unrelated_operations
    assert not report.completion_gate_passed
    assert all(not finding.blocks_unrelated_operations for finding in report.findings)


def test_local_documentation_is_generated_from_checked_in_asset_counts(tmp_path: Path) -> None:
    video_root = _create_video_pack(tmp_path)

    report = write_local_documentation(tmp_path, video_root=video_root)

    assert report.is_valid
    assert "common-agent-swarm-ops" in (video_root / "README.md").read_text(encoding="utf-8")
    assert "Agents: 1" in (tmp_path / "structure.md").read_text(encoding="utf-8")
    assert collect_local_asset_snapshot(video_root, repository_root=tmp_path).agent_count == 1


def test_changed_map_entries_require_exact_changed_ids() -> None:
    before = {"entries": [{"common_agent_id": "video.editor", "rationale": "old"}]}
    after = {"entries": [{"common_agent_id": "video.editor", "rationale": "new"}]}

    assert changed_map_entries(before, after) == ("video.editor",)


def test_normal_and_urgent_refreshes_use_the_same_gate_sequence(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "guide.md").write_text("guide", encoding="utf-8")
    video_root = _create_video_pack(tmp_path)
    write_local_documentation(tmp_path, video_root=video_root)
    destination_root = video_root / "corpus"
    snapshot = _snapshot(source_root)

    reports = []
    for refresh_kind in (RefreshKind.NORMAL, RefreshKind.URGENT):
        reports.append(
            RefreshOrchestrator().run(
                RefreshRequest(
                    source_root=source_root,
                    snapshot=snapshot,
                    destination_root=destination_root,
                    repository_root=tmp_path,
                    refresh_kind=refresh_kind,
                    license_status="reviewed",
                )
            )
        )

    assert reports[0].result is MigrationResult.PASS
    assert reports[1].result is MigrationResult.PASS
    assert reports[0].steps == reports[1].steps
    assert reports[0].steps == (
        "pinned_snapshot",
        "documentation_check",
        "pinned_dry_run",
        "changed_map_review_not_required",
    )


def test_reviewed_refresh_replaces_existing_corpus_file_and_preserves_idempotence(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_file = source_root / "guide.md"
    source_file.write_bytes(b"old")
    destination_root = tmp_path / "business" / "video" / "corpus"
    snapshot = _snapshot(source_root)
    first_approved = _approved_set(snapshot, b"old")
    first_plan = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        license_status="reviewed",
    )
    first_approval = verify_human_import_gate(
        first_plan,
        first_approved,
        license_status="reviewed",
        declared_destinations=("guide.md",),
    )
    first_write = write_corpus(destination_root, first_approved, verification=first_approval)
    assert first_write.result is MigrationResult.PASS

    source_file.write_bytes(b"new")
    refreshed = _approved_set(snapshot, b"new")
    refreshed_plan = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        license_status="reviewed",
        allowed_existing_destinations=("guide.md",),
    )
    refreshed_approval = verify_human_import_gate(
        refreshed_plan,
        refreshed,
        license_status="reviewed",
        declared_destinations=("guide.md",),
    )
    refreshed_write = write_corpus(
        destination_root,
        refreshed,
        verification=refreshed_approval,
        allow_reviewed_replacements=True,
    )

    assert refreshed_write.result is MigrationResult.PASS
    assert (destination_root / "guide.md").read_bytes() == b"new"
    assert refreshed_write.manifest_digest is not None


def test_reviewed_write_refresh_reaches_completion_only_with_all_callbacks(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_file = source_root / "guide.md"
    source_file.write_text("guide", encoding="utf-8")
    video_root = _create_video_pack(tmp_path)
    write_local_documentation(tmp_path, video_root=video_root)
    snapshot = _snapshot(source_root)
    approved = _approved_set(snapshot, b"guide")

    report = RefreshOrchestrator().run(
        RefreshRequest(
            source_root=source_root,
            snapshot=snapshot,
            destination_root=video_root / "corpus",
            repository_root=tmp_path,
            approved_import_set=approved,
            refresh_kind=RefreshKind.URGENT,
            write_mode=True,
            license_status="reviewed",
            standalone_check=lambda _request: True,
            evidence_recorder=lambda _report: True,
        )
    )

    assert report.result is MigrationResult.PASS
    assert report.completion_gate_passed
    assert report.approval_verified
    assert report.standalone_passed
    assert report.evidence_recorded
    assert report.provenance_preserved
