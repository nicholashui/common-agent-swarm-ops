"""Focused tests for the local-only deterministic intake planner."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.video.migration.approval import verify_human_import_gate
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.intake import plan_source_intake

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)


def _snapshot(source_root: Path) -> SourceSnapshot:
    return SourceSnapshot(
        "https://example.invalid/video",
        "commit-1",
        str(source_root),
        _NOW,
    )


def _tree_snapshot(root: Path) -> tuple[tuple[str, bytes | None], ...]:
    if not root.exists():
        return ()
    return tuple(
        sorted(
            (
                path.relative_to(root).as_posix(),
                path.read_bytes() if path.is_file() else None,
            )
            for path in root.rglob("*")
        )
    )


def test_dry_run_is_canonical_and_does_not_create_destination(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_file = source_root / "guide.md"
    source_file.write_bytes(b"untrusted guide\n")
    destination_root = tmp_path / "pack" / "corpus"

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=destination_root,
        license_status="reviewed",
    )
    repeat = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=destination_root,
        license_status="reviewed",
    )

    assert report.result is MigrationResult.PASS
    assert report.canonical_json() == repeat.canonical_json()
    assert report.included[0].destination_path == "guide.md"
    assert report.included[0].size_bytes == len(b"untrusted guide\n")
    assert report.included[0].sha256 == hashlib.sha256(b"untrusted guide\n").hexdigest()
    assert not destination_root.exists()


def test_dry_run_reports_license_secrets_prohibited_material_and_collision(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "guide.md").write_text("api_key=not-a-real-key\n", encoding="utf-8")
    (source_root / "notes.md").write_text("notes", encoding="utf-8")
    (source_root / "render.mp4").write_bytes(b"\x00\x01unreviewed media")
    (source_root / ".cache").mkdir()
    (source_root / ".cache" / "value.txt").write_text("cache", encoding="utf-8")
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    (destination_root / "guide.md").write_text("old", encoding="utf-8")
    (destination_root / "notes.md").write_text("old", encoding="utf-8")
    before = _tree_snapshot(destination_root)

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=destination_root,
        license_status=None,
    )

    codes = {finding.code for finding in report.findings}
    assert report.result is MigrationResult.FAIL
    assert codes >= {
        "secret",
        "prohibited_material",
        "license_provenance_gap",
        "destination_collision",
    }
    assert {item.source_path for item in report.excluded} == {
        ".cache",
        ".cache/value.txt",
        "guide.md",
        "render.mp4",
    }
    assert any(
        finding.code == "prohibited_material" and finding.path == "render.mp4"
        for finding in report.findings
    )
    assert _tree_snapshot(destination_root) == before


def test_dry_run_rejects_escaping_symlink_without_reading_target(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("do not import", encoding="utf-8")
    link = source_root / "outside.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Symlink creation is unavailable in this environment.")

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=tmp_path / "pack" / "corpus",
        license_status="reviewed",
    )

    assert report.result is MigrationResult.FAIL
    assert any(
        finding.code == "unsafe_path" and finding.path == "outside.txt"
        for finding in report.findings
    )
    assert not (tmp_path / "pack").exists()


def test_allow_list_excludes_unrequested_candidates(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    (source_root / "docs").mkdir(parents=True)
    (source_root / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    (source_root / "notes.md").write_text("notes", encoding="utf-8")

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=tmp_path / "pack" / "corpus",
        allow_paths=("docs",),
        license_status="reviewed",
    )

    assert report.result is MigrationResult.PASS
    assert [item.source_path for item in report.included] == ["docs/guide.md"]
    assert [item.source_path for item in report.excluded] == ["notes.md"]
    assert report.excluded[0].reason == "not requested by the allow-list"


def test_dry_run_report_matches_frozen_canonical_json(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "guide.md").write_bytes(b"untrusted guide\n")

    report = plan_source_intake(
        source_root,
        SourceSnapshot(
            "https://example.invalid/video",
            "commit-1",
            "fixtures/source",
            _NOW,
        ),
        destination_root=tmp_path / "pack" / "corpus",
        license_status="reviewed",
    )

    assert report.mode is ImportMode.DRY_RUN
    assert report.canonical_json() == (
        '{"excluded":[],"findings":[],"included":[{"classification":"included",'
        '"destination_path":"guide.md","reason":"","sha256":"4c68fcde6c9cc6ffc91b260d9c78c3d1adad70d0b6533a5c65d80a5748189108",'
        '"size_bytes":16,"source_path":"guide.md"}],"mode":"dry_run","result":"pass",'
        '"snapshot":{"recorded_at":"2025-01-01T12:00:00Z","source_commit":"commit-1",'
        '"source_repository":"https://example.invalid/video","source_root":"fixtures/source"},'
        '"total_bytes":16}'
    )


def test_dry_run_rejects_unsafe_destination_path_without_mutation(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "guide.md").write_text("guide", encoding="utf-8")
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    (destination_root / "keep.txt").write_text("keep", encoding="utf-8")
    before = _tree_snapshot(destination_root)

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=destination_root,
        destination_mapper=lambda _path: "../outside.md",
        license_status="reviewed",
    )

    assert report.result is MigrationResult.FAIL
    assert any(
        finding.code == "unsafe_destination_path" and finding.path == "guide.md"
        for finding in report.findings
    )
    assert _tree_snapshot(destination_root) == before
    assert not (tmp_path / "pack" / "outside.md").exists()


def _approved_import_set(
    snapshot: SourceSnapshot,
    *,
    digest: str,
    size_bytes: int,
) -> ApprovedImportSet:
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(
            ApprovedImportFile(
                source_path="guide.md",
                destination_path="guide.md",
                size_bytes=size_bytes,
                sha256=digest,
                original_repository=snapshot.source_repository,
                original_commit=snapshot.source_commit,
                original_path="guide.md",
                license_status="reviewed",
            ),
        ),
        total_bytes=size_bytes,
        license_status="reviewed",
        approved_by="reviewer-1",
        approved_at=_NOW,
        approval_id="approval-1",
    )


def test_exact_approval_comparison_passes_without_mutating_destination(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_file = source_root / "guide.md"
    source_file.write_bytes(b"guide")
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    (destination_root / "keep.txt").write_text("keep", encoding="utf-8")
    before = _tree_snapshot(destination_root)
    snapshot = _snapshot(source_root)
    report = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        license_status="reviewed",
    )
    digest = hashlib.sha256(b"guide").hexdigest()

    result = verify_human_import_gate(
        report,
        _approved_import_set(snapshot, digest=digest, size_bytes=5),
        approval_id="approval-1",
        approved_by="reviewer-1",
        license_status="reviewed",
    )

    assert result.result is MigrationResult.PASS
    assert result.is_approved
    assert result.recomputed_files[0].sha256 == digest
    assert _tree_snapshot(destination_root) == before


def test_approval_digest_drift_blocks_without_mutating_destination(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "guide.md").write_bytes(b"new")
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    (destination_root / "keep.txt").write_text("keep", encoding="utf-8")
    before = _tree_snapshot(destination_root)
    snapshot = _snapshot(source_root)
    report = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        license_status="reviewed",
    )

    result = verify_human_import_gate(
        report,
        _approved_import_set(
            snapshot,
            digest=hashlib.sha256(b"old").hexdigest(),
            size_bytes=3,
        ),
        approval_id="approval-1",
        approved_by="reviewer-1",
        license_status="reviewed",
    )

    assert result.result is MigrationResult.BLOCKED
    assert "approval_digest_drift" in {finding.code for finding in result.findings}
    assert _tree_snapshot(destination_root) == before
