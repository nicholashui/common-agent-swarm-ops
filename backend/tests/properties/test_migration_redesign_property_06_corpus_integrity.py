"""Property checks for complete, reproducible, integrity-preserving corpus manifests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    CorpusManifestEntry,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import (
    MANIFEST_FILENAME,
    CorpusImporter,
    CorpusManifest,
    validate_corpus_integrity,
    write_corpus,
)

_RECORDED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_SOURCE_REPOSITORY: Final[str] = "https://example.invalid/historical-video"
_SOURCE_COMMIT: Final[str] = "fixture-commit-property-06"
_LICENSE_STATUS: Final[str] = "reviewed-local-license"
_APPROVED_BY: Final[str] = "migration-approver-property-06"
_APPROVAL_ID: Final[str] = "approval-property-06"
_SAFE_SEGMENT = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=8,
)
_SAFE_RELATIVE_PATH = st.builds(
    lambda parents, leaf: "/".join((*parents, f"{leaf}.md")),
    st.lists(_SAFE_SEGMENT, min_size=0, max_size=2),
    _SAFE_SEGMENT,
)
_APPROVED_FILE_SETS = st.dictionaries(
    keys=_SAFE_RELATIVE_PATH,
    values=st.binary(min_size=1, max_size=64),
    min_size=1,
    max_size=3,
)
_CORRUPTIONS = st.sampled_from(("path", "size", "manifest_digest", "destination_digest"))


def _write_source_files(source_root: Path, files: dict[str, bytes]) -> None:
    """Write generated opaque source bytes beneath the local snapshot root."""
    for relative_path, content in files.items():
        source_path = source_root.joinpath(*relative_path.split("/"))
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(content)


def _approved_import_set(source_root: Path, files: dict[str, bytes]) -> ApprovedImportSet:
    """Build one bounded, exact approved set from the generated source tree."""
    _write_source_files(source_root, files)
    approved_files = tuple(
        ApprovedImportFile(
            source_path=relative_path,
            destination_path=f"incoming/{relative_path}",
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            original_repository=_SOURCE_REPOSITORY,
            original_commit=_SOURCE_COMMIT,
            original_path=f"upstream/{relative_path}",
            license_status=_LICENSE_STATUS,
        )
        for relative_path, content in sorted(files.items())
    )
    snapshot = SourceSnapshot(
        source_repository=_SOURCE_REPOSITORY,
        source_commit=_SOURCE_COMMIT,
        source_root=str(source_root),
        recorded_at=_RECORDED_AT,
    )
    return ApprovedImportSet(
        snapshot=snapshot,
        files=approved_files,
        total_bytes=sum(file.size_bytes for file in approved_files),
        license_status=_LICENSE_STATUS,
        approved_by=_APPROVED_BY,
        approved_at=_RECORDED_AT,
        approval_id=_APPROVAL_ID,
    )


def _expected_entries(approved: ApprovedImportSet) -> tuple[CorpusManifestEntry, ...]:
    """Project the approved set into the exact manifest records expected on disk."""
    return tuple(
        CorpusManifestEntry(
            path=file.destination_path,
            size_bytes=file.size_bytes,
            sha256=file.sha256,
            original_repository=file.original_repository,
            original_commit=file.original_commit,
            original_path=file.original_path,
            license_status=file.license_status,
        )
        for file in approved.files
    )


def _read_manifest(destination_root: Path) -> CorpusManifest:
    """Read the canonical manifest through the same typed model as the writer."""
    raw = json.loads((destination_root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("entries"), list):
        raise AssertionError("The fixture must contain a canonical corpus manifest.")
    entries = tuple(CorpusManifestEntry(**entry) for entry in raw["entries"])
    return CorpusManifest(
        entries=entries,
        schema_version=str(raw.get("schema_version", "1.0")),
        classification=str(raw.get("classification", "untrusted_reference_data")),
    )


def _write_manifest(destination_root: Path, manifest: CorpusManifest) -> None:
    """Replace only the test manifest with canonical bytes for corruption checks."""
    (destination_root / MANIFEST_FILENAME).write_bytes(manifest.to_json_bytes())


def _tree_state(root: Path) -> tuple[tuple[str, bytes, int], ...]:
    """Capture file bytes and modification stamps to prove idempotent reapplication."""
    return tuple(
        (
            path.relative_to(root).as_posix(),
            path.read_bytes(),
            path.stat().st_mtime_ns,
        )
        for path in sorted(
            (candidate for candidate in root.rglob("*") if candidate.is_file()),
            key=lambda candidate: candidate.relative_to(root).as_posix(),
        )
    )


# Feature: migration-redesign, Property 6: Corpus manifests are complete,
# reproducible, and integrity-preserving.
# **Validates: Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11**
@settings(max_examples=24, deadline=None, derandomize=True)
@example({"guide.md": b"a local video reference"})
@given(files=_APPROVED_FILE_SETS)
def test_approved_sets_have_complete_reproducible_manifests_and_idempotent_reapplication(
    files: dict[str, bytes],
) -> None:
    """Every approved file is represented exactly once and a repeat is a no-op."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        destination_root = tmp_path / "business" / "video" / "corpus"
        approved = _approved_import_set(source_root, files)
        expected_entries = _expected_entries(approved)

        first = CorpusImporter(destination_root).write(approved)

        assert first.result is MigrationResult.PASS
        assert first.entries == expected_entries
        assert first.configuration_paths == tuple(entry.path for entry in expected_entries)
        assert first.manifest_digest == CorpusManifest(entries=expected_entries).digest()
        manifest_bytes = (destination_root / MANIFEST_FILENAME).read_bytes()
        manifest = _read_manifest(destination_root)
        assert manifest.entries == expected_entries
        assert manifest.classification == "untrusted_reference_data"
        assert json.loads(manifest_bytes.decode("utf-8"))["classification"] == (
            "untrusted_reference_data"
        )

        integrity = validate_corpus_integrity(
            destination_root,
            excluded_paths=first.configuration_paths,
        )
        assert integrity.is_valid
        assert integrity.entries == expected_entries
        assert integrity.manifest_digest == manifest.digest()
        assert integrity.excluded_from_configuration == first.configuration_paths

        before_reapplication = _tree_state(destination_root)
        second = write_corpus(destination_root, approved)

        assert second.result is MigrationResult.NO_CHANGE
        assert second.is_no_change
        assert second.entries == expected_entries
        assert second.manifest_digest == first.manifest_digest
        assert (destination_root / MANIFEST_FILENAME).read_bytes() == manifest_bytes
        assert _tree_state(destination_root) == before_reapplication


# Feature: migration-redesign, Property 6: Corpus manifests are complete,
# reproducible, and integrity-preserving.
# **Validates: Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10**
@settings(max_examples=24, deadline=None, derandomize=True)
@example(files={"guide.md": b"path corruption"}, corruption="path")
@example(files={"guide.md": b"size corruption"}, corruption="size")
@example(files={"guide.md": b"manifest digest corruption"}, corruption="manifest_digest")
@example(files={"guide.md": b"destination digest corruption"}, corruption="destination_digest")
@given(files=_APPROVED_FILE_SETS, corruption=_CORRUPTIONS)
def test_rehashing_reports_generated_path_size_and_digest_corruption(
    files: dict[str, bytes],
    corruption: str,
) -> None:
    """Rehashing fails closed for path, size, and digest drift without extra mutation."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        destination_root = tmp_path / "business" / "video" / "corpus"
        approved = _approved_import_set(source_root, files)
        initial = write_corpus(destination_root, approved)
        assert initial.result is MigrationResult.PASS

        manifest = _read_manifest(destination_root)
        entry = manifest.entries[0]
        entries = list(manifest.entries)
        if corruption == "path":
            entries[0] = replace(entry, path=f"corrupted/{entry.path}")
        elif corruption == "size":
            entries[0] = replace(entry, size_bytes=entry.size_bytes + 1)
        elif corruption == "manifest_digest":
            bad_digest = "0" * 64 if entry.sha256 != "0" * 64 else "f" * 64
            entries[0] = replace(entry, sha256=bad_digest)
        elif corruption == "destination_digest":
            destination = destination_root.joinpath(*entry.path.split("/"))
            original = destination.read_bytes()
            changed_first_byte = bytes((original[0] ^ 1,))
            destination.write_bytes(changed_first_byte + original[1:])
        else:
            raise AssertionError(f"Unhandled corruption kind: {corruption}")

        if corruption != "destination_digest":
            _write_manifest(destination_root, CorpusManifest(entries=tuple(entries)))
        before_validation = _tree_state(destination_root)

        report = validate_corpus_integrity(destination_root)
        finding_codes = {finding.code for finding in report.findings}

        assert report.result is MigrationResult.FAIL
        assert "corpus_integrity_failure" in finding_codes
        expected_code = {
            "path": "corpus_path_mismatch",
            "size": "corpus_size_mismatch",
            "manifest_digest": "corpus_digest_mismatch",
            "destination_digest": "corpus_digest_mismatch",
        }[corruption]
        assert expected_code in finding_codes
        assert _tree_state(destination_root) == before_validation
