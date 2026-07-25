"""Focused tests for exact, read-only Human Import Gate verification."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from app.video.migration.approval import verify_human_import_gate
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    HistoricalProvenance,
    ImportCandidate,
    ImportDryRunReport,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_SOURCE_URL = "https://example.invalid/video"
_SOURCE_COMMIT = "commit-1"


def _snapshot(source_root: Path) -> SourceSnapshot:
    return SourceSnapshot(_SOURCE_URL, _SOURCE_COMMIT, str(source_root), _NOW)


def _report(snapshot: SourceSnapshot, *, digest: str, size: int = 5) -> ImportDryRunReport:
    return ImportDryRunReport(
        snapshot=snapshot,
        mode=ImportMode.DRY_RUN,
        included=(ImportCandidate("guide.md", "reference/guide.md", size, digest),),
        excluded=(),
        findings=(),
        total_bytes=size,
        result=MigrationResult.PASS,
    )


def _approved(snapshot: SourceSnapshot, *, digest: str, size: int = 5) -> ApprovedImportSet:
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(
            ApprovedImportFile(
                source_path="guide.md",
                destination_path="reference/guide.md",
                size_bytes=size,
                sha256=digest,
                original_repository=_SOURCE_URL,
                original_commit=_SOURCE_COMMIT,
                original_path="guide.md",
                license_status="reviewed",
            ),
        ),
        total_bytes=size,
        license_status="reviewed",
        approved_by="reviewer-1",
        approved_at=_NOW,
        approval_id="approval-1",
    )


def test_exact_gate_verification_passes_without_touching_destination(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    destination = destination_root / "reference" / "guide.md"
    destination.parent.mkdir()
    destination.write_text("pre-existing", encoding="utf-8")
    digest = hashlib.sha256(b"guide").hexdigest()
    report = _report(_snapshot(source_root), digest=digest)

    result = verify_human_import_gate(
        report,
        _approved(_snapshot(source_root), digest=digest),
        approval_id="approval-1",
        approved_by="reviewer-1",
        license_status="reviewed",
    )

    assert result.result is MigrationResult.PASS
    assert result.is_approved
    assert result.findings == ()
    assert destination.read_text(encoding="utf-8") == "pre-existing"


def test_digest_drift_blocks_with_no_destination_mutation(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    destination_root = tmp_path / "pack" / "corpus"
    destination_root.mkdir(parents=True)
    before = tuple(destination_root.rglob("*"))
    report = _report(_snapshot(source_root), digest=hashlib.sha256(b"new").hexdigest())
    approved = _approved(_snapshot(source_root), digest=hashlib.sha256(b"old").hexdigest())

    result = verify_human_import_gate(report, approved)

    assert result.result is MigrationResult.BLOCKED
    assert "approval_digest_drift" in {finding.code for finding in result.findings}
    assert tuple(destination_root.rglob("*")) == before


def test_scope_destination_and_identity_drift_are_all_blocked(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    digest = hashlib.sha256(b"guide").hexdigest()
    snapshot = _snapshot(source_root)
    report = ImportDryRunReport(
        snapshot=snapshot,
        mode=ImportMode.DRY_RUN,
        included=(
            # The destination is not the approved declaration and this is a new file.
            _candidate("new.md", "unapproved/new.md", digest),
        ),
        excluded=(),
        findings=(),
        total_bytes=5,
        result=MigrationResult.PASS,
    )

    result = verify_human_import_gate(
        report,
        _approved(snapshot, digest=digest),
        approval_identity="wrong-approval",
        approved_by="wrong-reviewer",
    )

    codes = {finding.code for finding in result.findings}
    assert result.result is MigrationResult.BLOCKED
    assert {
        "approval_identity_mismatch",
        "approval_reviewer_mismatch",
        "approval_scope_expansion",
        "approval_scope_mismatch",
        "undeclared_destination",
    } <= codes


def test_license_and_provenance_declarations_must_match_recorded_gate(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    digest = hashlib.sha256(b"guide").hexdigest()
    snapshot = _snapshot(source_root)
    report = _report(snapshot, digest=digest)
    approved = _approved(snapshot, digest=digest)

    result = verify_human_import_gate(
        report,
        approved,
        license_status="pending",
        provenance={
            "guide.md": HistoricalProvenance(
                repository="https://example.invalid/other",
                commit="other-commit",
                path="other-guide.md",
                license_status="pending",
            )
        },
    )

    codes = {finding.code for finding in result.findings}
    assert result.result is MigrationResult.BLOCKED
    assert "approval_provenance_mismatch" in codes
    assert "approval_license_mismatch" in codes


def _candidate(source_path: str, destination_path: str, digest: str) -> ImportCandidate:
    return ImportCandidate(source_path, destination_path, 5, digest)
