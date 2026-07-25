"""Property checks for exact, approval-gated corpus writes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.approval import ApprovalVerificationReport, verify_human_import_gate
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    HistoricalProvenance,
    ImportCandidate,
    ImportDryRunReport,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.intake import plan_source_intake

_RECORDED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_APPROVED_LICENSE: Final[str] = "approved-license"
_APPROVER: Final[str] = "migration-approver-property-05"
_APPROVAL_ID: Final[str] = "approval-property-05"
_FILE_CONTENTS: Final[dict[str, bytes]] = {
    "guides/intro.md": b"introductory local reference\n",
    "notes/quality.md": b"quality criteria reference\n",
}
_MISMATCH_FIELDS: Final[tuple[str, ...]] = (
    "snapshot_repository",
    "snapshot_commit",
    "snapshot_root",
    "source_path",
    "destination_path",
    "size_bytes",
    "sha256",
    "original_repository",
    "original_commit",
    "original_path",
    "file_license_status",
    "approval_license_status",
    "approval_id",
    "approved_by",
    "total_bytes",
)
_FILE_MISMATCH_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "source_path",
        "destination_path",
        "size_bytes",
        "sha256",
        "original_repository",
        "original_commit",
        "original_path",
        "file_license_status",
    }
)


@dataclass(frozen=True, slots=True)
class _ApprovalMismatch:
    """One generated field drift in the recomputed report or approval record."""

    field: str
    file_index: int = 0


@dataclass(frozen=True, slots=True)
class _ApprovalFixture:
    """Fixed local source, destination, report, and approval inputs."""

    source_root: Path
    destination_root: Path
    report: ImportDryRunReport
    approved: ApprovedImportSet
    provenance: dict[str, HistoricalProvenance]


@st.composite
def _approval_mismatches(draw: st.DrawFn) -> _ApprovalMismatch:
    """Generate one bounded mismatch from the exact approval comparison surface."""
    field = draw(st.sampled_from(_MISMATCH_FIELDS))
    file_index = draw(st.integers(min_value=0, max_value=len(_FILE_CONTENTS) - 1))
    if field not in _FILE_MISMATCH_FIELDS:
        file_index = 0
    return _ApprovalMismatch(field=field, file_index=file_index)


def _write_source_files(source_root: Path) -> None:
    """Create the small, reviewed local source fixture."""
    for relative_path, content in _FILE_CONTENTS.items():
        source_path = source_root.joinpath(*relative_path.split("/"))
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(content)


def _build_fixture(tmp_path: Path) -> _ApprovalFixture:
    """Build a passing dry-run and its exact human-approved import set."""
    source_root = tmp_path / "source"
    destination_root = tmp_path / "pack" / "corpus"
    _write_source_files(source_root)
    destination_root.mkdir(parents=True)
    (destination_root / "keep.txt").write_bytes(b"pre-existing destination data")

    snapshot = SourceSnapshot(
        source_repository="https://example.invalid/video",
        source_commit="fixture-commit-1",
        source_root="fixture/source",
        recorded_at=_RECORDED_AT,
    )
    report = plan_source_intake(
        source_root,
        snapshot,
        destination_root=destination_root,
        destination_prefix="incoming",
        license_status=_APPROVED_LICENSE,
    )
    if report.result is not MigrationResult.PASS or report.findings:
        raise AssertionError("The exact approval fixture must have a passing dry-run.")

    provenance = {
        candidate.source_path: HistoricalProvenance(
            repository="https://example.invalid/historical-video",
            commit="historical-commit-1",
            path=f"upstream/{candidate.source_path}",
            license_status=_APPROVED_LICENSE,
        )
        for candidate in report.included
    }
    approved_files = tuple(
        _approved_file(candidate, provenance[candidate.source_path])
        for candidate in report.included
    )
    approved = ApprovedImportSet(
        snapshot=snapshot,
        files=approved_files,
        total_bytes=sum(file.size_bytes for file in approved_files),
        license_status=_APPROVED_LICENSE,
        approved_by=_APPROVER,
        approved_at=_RECORDED_AT,
        approval_id=_APPROVAL_ID,
    )
    return _ApprovalFixture(
        source_root=source_root,
        destination_root=destination_root,
        report=report,
        approved=approved,
        provenance=provenance,
    )


def _approved_file(
    candidate: ImportCandidate,
    provenance: HistoricalProvenance,
) -> ApprovedImportFile:
    """Convert one included candidate into its exact reviewed approval record."""
    if candidate.destination_path is None:
        raise AssertionError("The passing fixture must declare every destination.")
    if candidate.size_bytes is None or candidate.sha256 is None:
        raise AssertionError("The passing fixture must calculate every file digest and size.")
    return ApprovedImportFile(
        source_path=candidate.source_path,
        destination_path=candidate.destination_path,
        size_bytes=candidate.size_bytes,
        sha256=candidate.sha256,
        original_repository=provenance.repository,
        original_commit=provenance.commit,
        original_path=provenance.path,
        license_status=provenance.license_status,
    )


def _verify(
    fixture: _ApprovalFixture,
    report: ImportDryRunReport,
    approved: ApprovedImportSet,
) -> ApprovalVerificationReport:
    """Run the exact gate with all independently recomputed declarations."""
    return verify_human_import_gate(
        report,
        approved,
        approval_id=_APPROVAL_ID,
        approval_identity=_APPROVAL_ID,
        approved_by=_APPROVER,
        license_status=_APPROVED_LICENSE,
        provenance=fixture.provenance,
        declared_destinations=tuple(file.destination_path for file in fixture.approved.files),
    )


def _write_if_approved(
    fixture: _ApprovalFixture,
    report: ImportDryRunReport,
    approved: ApprovedImportSet,
) -> ApprovalVerificationReport:
    """Model the write boundary: no destination mutation occurs before PASS."""
    verification = _verify(fixture, report, approved)
    if not verification.is_approved:
        return verification

    for candidate in report.included:
        if candidate.destination_path is None:
            raise AssertionError("A passing approval must have a destination for every file.")
        source_path = fixture.source_root.joinpath(*candidate.source_path.split("/"))
        destination_path = fixture.destination_root.joinpath(*candidate.destination_path.split("/"))
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(source_path.read_bytes())
    return verification


def _tree_state(root: Path) -> tuple[tuple[str, bytes], ...]:
    """Capture destination files so blocked writes can prove no mutation."""
    return tuple(
        (
            path.relative_to(root).as_posix(),
            path.read_bytes(),
        )
        for path in sorted(
            (candidate for candidate in root.rglob("*") if candidate.is_file()),
            key=lambda candidate: candidate.relative_to(root).as_posix(),
        )
    )


def _mutate_fixture(
    fixture: _ApprovalFixture,
    mismatch: _ApprovalMismatch,
) -> tuple[ImportDryRunReport, ApprovedImportSet]:
    """Apply one logical mismatch while retaining valid typed records."""
    field = mismatch.field
    index = mismatch.file_index
    report = fixture.report
    approved = fixture.approved

    if field in {"snapshot_repository", "snapshot_commit", "snapshot_root"}:
        if field == "snapshot_repository":
            drifted_snapshot = replace(
                approved.snapshot,
                source_repository="https://example.invalid/drifted-video",
            )
        elif field == "snapshot_commit":
            drifted_snapshot = replace(approved.snapshot, source_commit="drifted-commit")
        else:
            drifted_snapshot = replace(approved.snapshot, source_root="fixture/drifted-source")
        return report, replace(approved, snapshot=drifted_snapshot)

    if field == "total_bytes":
        return replace(report, total_bytes=report.total_bytes + 1), approved

    if field in {"source_path", "destination_path", "size_bytes", "sha256"}:
        candidates = list(report.included)
        candidate = candidates[index]
        if field == "source_path":
            mutated = replace(candidate, source_path="drifted/source.md")
        elif field == "destination_path":
            if candidate.destination_path is None:
                raise AssertionError("The passing fixture must declare every destination.")
            mutated = replace(candidate, destination_path="incoming/drifted.md")
        elif field == "size_bytes":
            if candidate.size_bytes is None:
                raise AssertionError("The passing fixture must calculate every file size.")
            mutated = replace(candidate, size_bytes=candidate.size_bytes + 1)
        else:
            mutated = replace(candidate, sha256="0" * 64)
        candidates[index] = mutated
        total_bytes = report.total_bytes + 1 if field == "size_bytes" else report.total_bytes
        return replace(report, included=tuple(candidates), total_bytes=total_bytes), approved

    files = list(approved.files)
    if field in {
        "original_repository",
        "original_commit",
        "original_path",
        "file_license_status",
    }:
        file = files[index]
        if field == "original_repository":
            files[index] = replace(
                file,
                original_repository="https://example.invalid/drifted-provenance",
            )
        elif field == "original_commit":
            files[index] = replace(file, original_commit="drifted-provenance-commit")
        elif field == "original_path":
            files[index] = replace(file, original_path="upstream/drifted/path.md")
        else:
            files[index] = replace(file, license_status="different-license")
        return report, replace(approved, files=tuple(files))
    if field == "approval_license_status":
        return report, replace(approved, license_status="different-license")
    if field == "approval_id":
        return report, replace(approved, approval_id="different-approval-id")
    if field == "approved_by":
        return report, replace(approved, approved_by="different-approver")
    raise AssertionError(f"Unhandled approval mismatch field: {field}")


# Feature: migration-redesign, Property 5: Write-mode imports exactly match human approval.
# **Validates: Requirements 3.3, 4.1, 4.2**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(_ApprovalMismatch("snapshot_repository"))
@example(_ApprovalMismatch("source_path", 0))
@example(_ApprovalMismatch("destination_path", 1))
@example(_ApprovalMismatch("size_bytes", 0))
@example(_ApprovalMismatch("sha256", 1))
@example(_ApprovalMismatch("original_repository", 0))
@example(_ApprovalMismatch("original_commit", 1))
@example(_ApprovalMismatch("original_path", 0))
@example(_ApprovalMismatch("file_license_status", 1))
@example(_ApprovalMismatch("approval_license_status"))
@example(_ApprovalMismatch("total_bytes"))
@example(_ApprovalMismatch("approval_id"))
@example(_ApprovalMismatch("approved_by"))
@given(mismatch=_approval_mismatches())
def test_generated_one_field_approval_mismatches_block_without_mutation(
    mismatch: _ApprovalMismatch,
) -> None:
    """Every generated approval drift blocks the write boundary and preserves state."""
    with TemporaryDirectory() as temporary_root:
        fixture = _build_fixture(Path(temporary_root))
        before = _tree_state(fixture.destination_root)
        mutated_report, mutated_approved = _mutate_fixture(fixture, mismatch)

        verification = _write_if_approved(fixture, mutated_report, mutated_approved)

        assert verification.result is MigrationResult.BLOCKED
        assert verification.findings
        assert not verification.is_approved
        assert _tree_state(fixture.destination_root) == before


def test_explicit_exact_approval_match_permits_write(tmp_path: Path) -> None:
    """An exact snapshot, file set, metadata, provenance, and byte total may write."""
    fixture = _build_fixture(tmp_path)
    before = _tree_state(fixture.destination_root)

    verification = _write_if_approved(fixture, fixture.report, fixture.approved)

    assert verification.result is MigrationResult.PASS
    assert verification.findings == ()
    assert verification.is_approved
    assert verification.recomputed_files == fixture.approved.files
    assert verification.recomputed_total_bytes == fixture.approved.total_bytes
    after = _tree_state(fixture.destination_root)
    assert after != before
    assert ("incoming/guides/intro.md", _FILE_CONTENTS["guides/intro.md"]) in after
    assert ("incoming/notes/quality.md", _FILE_CONTENTS["notes/quality.md"]) in after
