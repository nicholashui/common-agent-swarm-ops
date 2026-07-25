"""Transactional writing and integrity validation for imported Video Pack corpus data.

The corpus writer accepts only metadata from a reviewed import set.  It treats
source files as opaque bytes, stages them inside the corpus root, verifies every
staged destination, and publishes new data files plus canonical provenance
records with atomic replacements.  Existing corpus files are never overwritten
or removed; a destination collision is reported before publication.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import Final

from app.video.migration.approval import ApprovalVerificationReport
from app.video.migration.canonical import sort_findings
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    CanonicalRecord,
    CorpusManifestEntry,
    ImportFinding,
    MigrationResult,
)
from app.video.migration.paths import (
    PathInput,
    UnsafeLocalPathError,
    normalize_relative_path,
    resolve_under_root,
)

MANIFEST_FILENAME: Final[str] = "MANIFEST.json"
SOURCE_COMMIT_FILENAME: Final[str] = "SOURCE_COMMIT.txt"
SOURCE_URL_FILENAME: Final[str] = "SOURCE_URL.txt"
SOURCE_COPIED_AT_FILENAME: Final[str] = "SOURCE_COPIED_AT.txt"
CORPUS_SCHEMA_VERSION: Final[str] = "1.0"
CORPUS_CLASSIFICATION: Final[str] = "untrusted_reference_data"
_CONTROL_FILENAMES: Final[frozenset[str]] = frozenset(
    {
        MANIFEST_FILENAME,
        SOURCE_COMMIT_FILENAME,
        SOURCE_URL_FILENAME,
        SOURCE_COPIED_AT_FILENAME,
    }
)
_STAGE_PREFIX: Final[str] = ".corpus-stage-"


@dataclass(frozen=True, slots=True)
class CorpusManifest(CanonicalRecord):
    """Canonical machine-readable inventory of imported corpus files."""

    entries: tuple[CorpusManifestEntry, ...]
    schema_version: str = CORPUS_SCHEMA_VERSION
    classification: str = CORPUS_CLASSIFICATION

    def __post_init__(self) -> None:
        entries = tuple(self.entries)
        if any(not isinstance(entry, CorpusManifestEntry) for entry in entries):
            raise TypeError("entries must contain CorpusManifestEntry records.")
        paths = tuple(entry.path for entry in entries)
        if len(paths) != len(set(paths)):
            raise ValueError("entries must not contain duplicate paths.")
        object.__setattr__(self, "entries", tuple(sorted(entries, key=lambda entry: entry.path)))
        if self.schema_version != CORPUS_SCHEMA_VERSION:
            raise ValueError("Unsupported corpus manifest schema version.")
        if self.classification != CORPUS_CLASSIFICATION:
            raise ValueError("Imported corpus must remain untrusted reference data.")

    def to_json_bytes(self) -> bytes:
        """Return canonical manifest bytes with one final newline."""
        return f"{self.canonical_json()}\n".encode()


@dataclass(frozen=True, slots=True)
class CorpusIntegrityReport(CanonicalRecord):
    """Deterministic result of rehashing a local corpus manifest."""

    result: MigrationResult
    findings: tuple[ImportFinding, ...]
    entries: tuple[CorpusManifestEntry, ...] = ()
    manifest_digest: str | None = None
    excluded_from_configuration: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        entries = tuple(self.entries)
        if any(not isinstance(entry, CorpusManifestEntry) for entry in entries):
            raise TypeError("entries must contain CorpusManifestEntry records.")
        object.__setattr__(self, "entries", tuple(sorted(entries, key=lambda entry: entry.path)))
        if self.manifest_digest is not None:
            _validate_digest(self.manifest_digest, "manifest_digest")
            object.__setattr__(self, "manifest_digest", self.manifest_digest.casefold())
        object.__setattr__(
            self,
            "excluded_from_configuration",
            _safe_path_tuple(self.excluded_from_configuration),
        )

    @property
    def is_valid(self) -> bool:
        """Return whether every manifest entry matched its destination file."""
        return self.result is MigrationResult.PASS


@dataclass(frozen=True, slots=True)
class CorpusWriteReport(CanonicalRecord):
    """Result of an approval-gated, staged corpus publication."""

    result: MigrationResult
    findings: tuple[ImportFinding, ...]
    entries: tuple[CorpusManifestEntry, ...] = ()
    changed_paths: tuple[str, ...] = ()
    unchanged_paths: tuple[str, ...] = ()
    manifest_digest: str | None = None
    excluded_from_configuration: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        entries = tuple(self.entries)
        if any(not isinstance(entry, CorpusManifestEntry) for entry in entries):
            raise TypeError("entries must contain CorpusManifestEntry records.")
        object.__setattr__(self, "entries", tuple(sorted(entries, key=lambda entry: entry.path)))
        object.__setattr__(self, "changed_paths", _safe_path_tuple(self.changed_paths))
        object.__setattr__(self, "unchanged_paths", _safe_path_tuple(self.unchanged_paths))
        if self.manifest_digest is not None:
            _validate_digest(self.manifest_digest, "manifest_digest")
            object.__setattr__(self, "manifest_digest", self.manifest_digest.casefold())
        object.__setattr__(
            self,
            "excluded_from_configuration",
            _safe_path_tuple(self.excluded_from_configuration),
        )

    @property
    def is_success(self) -> bool:
        """Return whether the staged corpus was published or already current."""
        return self.result in (MigrationResult.PASS, MigrationResult.NO_CHANGE)

    @property
    def is_no_change(self) -> bool:
        """Return whether the approved set was already fully published."""
        return self.result is MigrationResult.NO_CHANGE

    @property
    def configuration_paths(self) -> tuple[str, ...]:
        """Compatibility name for paths deliberately excluded from configuration."""
        return self.excluded_from_configuration


# Descriptive aliases used by callers that call this operation an import.
CorpusImportReport = CorpusWriteReport
CorpusValidationReport = CorpusIntegrityReport


def _safe_path_tuple(values: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(normalize_relative_path(value) for value in values)
    return tuple(sorted(set(normalized)))


def _validate_digest(value: str, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a SHA-256 digest.")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError(f"{name} must be a SHA-256 digest.") from error


def _finding(
    code: str,
    *,
    path: str = "",
    field: str = "",
    message: str,
) -> ImportFinding:
    return ImportFinding(code=code, path=path, field=field, message=message)


def _failure(
    findings: Iterable[ImportFinding],
    *,
    entries: Iterable[CorpusManifestEntry] = (),
    manifest_digest: str | None = None,
    excluded_paths: Iterable[str] = (),
    result: MigrationResult = MigrationResult.FAIL,
    changed_paths: Iterable[str] = (),
    unchanged_paths: Iterable[str] = (),
) -> CorpusWriteReport:
    return CorpusWriteReport(
        result=result,
        findings=tuple(findings),
        entries=tuple(entries),
        changed_paths=tuple(changed_paths),
        unchanged_paths=tuple(unchanged_paths),
        manifest_digest=manifest_digest,
        excluded_from_configuration=tuple(excluded_paths),
    )


def _empty_integrity(
    findings: Iterable[ImportFinding], *, excluded_paths: Iterable[str] = ()
) -> CorpusIntegrityReport:
    return CorpusIntegrityReport(
        result=MigrationResult.FAIL,
        findings=tuple(findings),
        excluded_from_configuration=tuple(excluded_paths),
    )


def _hash_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _resolve_root(
    root: PathInput, *, create: bool
) -> tuple[Path | None, tuple[ImportFinding, ...]]:
    try:
        raw = Path(root)
        resolved = raw.resolve(strict=False)
    except (OSError, RuntimeError, TypeError):
        return None, (
            _finding(
                "corpus_invalid_destination_root",
                message="The corpus destination root could not be resolved.",
            ),
        )
    if resolved.exists() and not resolved.is_dir():
        return None, (
            _finding(
                "corpus_invalid_destination_root",
                message="The corpus destination root is not a directory.",
            ),
        )
    if create:
        try:
            resolved.mkdir(parents=True, exist_ok=True)
        except OSError:
            return None, (
                _finding(
                    "corpus_destination_unwritable",
                    message="The corpus destination root could not be created.",
                ),
            )
    return resolved, ()


def _destination_path(root: Path, relative_path: str) -> tuple[Path | None, ImportFinding | None]:
    try:
        normalized = normalize_relative_path(relative_path)
        candidate = root.joinpath(*normalized.split("/"))
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, RuntimeError, TypeError, ValueError, UnsafeLocalPathError):
        return None, _finding(
            "corpus_destination_path_mismatch",
            path=relative_path,
            field="path",
            message="The approved destination does not resolve beneath the corpus root.",
        )
    return resolved, None


def _source_path(
    snapshot_root: str, relative_path: str
) -> tuple[Path | None, ImportFinding | None]:
    try:
        return (
            resolve_under_root(
                snapshot_root, relative_path, must_exist=True, require_readable=True
            ),
            None,
        )
    except (OSError, RuntimeError, TypeError, ValueError, UnsafeLocalPathError):
        return None, _finding(
            "corpus_source_path_invalid",
            path=relative_path,
            field="source_path",
            message=(
                "The approved source file is missing, unreadable, or outside the snapshot root."
            ),
        )


def _manifest_from_json(raw: object) -> CorpusManifest:
    if not isinstance(raw, Mapping):
        raise ValueError("Manifest must be a JSON object.")
    raw_entries = raw.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("Manifest entries must be a JSON array.")
    entries: list[CorpusManifestEntry] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("Manifest entries must be JSON objects.")
        values = dict(raw_entry)
        entries.append(CorpusManifestEntry(**values))
    return CorpusManifest(
        entries=tuple(entries),
        schema_version=str(raw.get("schema_version", CORPUS_SCHEMA_VERSION)),
        classification=str(raw.get("classification", CORPUS_CLASSIFICATION)),
    )


def _read_manifest(root: Path) -> tuple[CorpusManifest | None, tuple[ImportFinding, ...]]:
    path = root / MANIFEST_FILENAME
    if not path.exists():
        return None, ()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return _manifest_from_json(raw), ()
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        return None, (
            _finding(
                "corpus_manifest_invalid",
                path=MANIFEST_FILENAME,
                message="The corpus manifest is not a valid canonical manifest.",
            ),
        )


def _manifest_extra_files(root: Path, expected: set[str]) -> tuple[str, ...]:
    extras: list[str] = []
    if not root.exists():
        return ()
    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            path = Path(current_root) / name
            relative = path.relative_to(root).as_posix()
            if relative in _CONTROL_FILENAMES or relative.startswith(f"{_STAGE_PREFIX}"):
                continue
            if relative not in expected:
                extras.append(relative)
        for name in sorted(directory_names):
            path = Path(current_root) / name
            if path.is_symlink():
                relative = path.relative_to(root).as_posix()
                if relative not in expected and not relative.startswith(_STAGE_PREFIX):
                    extras.append(relative)
    return tuple(sorted(extras))


def _integrity_for_manifest(
    root: Path,
    manifest: CorpusManifest,
    *,
    include_extras: bool = True,
    excluded_paths: Iterable[str] = (),
) -> CorpusIntegrityReport:
    findings: list[ImportFinding] = []
    expected_paths = {entry.path for entry in manifest.entries}
    for entry in manifest.entries:
        actual, path_finding = _destination_path(root, entry.path)
        if path_finding is not None or actual is None:
            findings.append(
                path_finding
                or _finding(
                    "corpus_path_mismatch",
                    path=entry.path,
                    message="The manifest path is not contained by the corpus root.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=entry.path,
                    message="The corpus manifest path does not match a contained destination.",
                )
            )
            continue
        if not actual.exists() or not actual.is_file():
            findings.append(
                _finding(
                    "corpus_path_mismatch",
                    path=entry.path,
                    field="path",
                    message="The manifest entry has no corresponding regular destination file.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=entry.path,
                    message="The corpus destination path is missing or not a regular file.",
                )
            )
            continue
        try:
            size_bytes, sha256 = _hash_file(actual)
        except OSError:
            findings.append(
                _finding(
                    "corpus_unreadable_destination",
                    path=entry.path,
                    message="The corpus destination could not be re-hashed.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=entry.path,
                    message="The corpus destination could not be validated.",
                )
            )
            continue
        if size_bytes != entry.size_bytes:
            findings.append(
                _finding(
                    "corpus_size_mismatch",
                    path=entry.path,
                    field="size_bytes",
                    message="The destination size differs from the manifest entry.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=entry.path,
                    message="The corpus destination size does not match its manifest entry.",
                )
            )
        if sha256 != entry.sha256:
            findings.append(
                _finding(
                    "corpus_digest_mismatch",
                    path=entry.path,
                    field="sha256",
                    message="The destination SHA-256 differs from the manifest entry.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=entry.path,
                    message="The corpus destination digest does not match its manifest entry.",
                )
            )
    if include_extras:
        for path in _manifest_extra_files(root, expected_paths):
            findings.append(
                _finding(
                    "corpus_unmanifested_file",
                    path=path,
                    message="A corpus file is not declared by the canonical manifest.",
                )
            )
            findings.append(
                _finding(
                    "corpus_integrity_failure",
                    path=path,
                    message="The corpus contains a file outside the manifest.",
                )
            )
    return CorpusIntegrityReport(
        result=MigrationResult.PASS if not findings else MigrationResult.FAIL,
        findings=tuple(findings),
        entries=manifest.entries,
        manifest_digest=manifest.digest(),
        excluded_from_configuration=tuple(excluded_paths),
    )


def validate_corpus_integrity(
    destination_root: PathInput,
    *,
    excluded_paths: Iterable[str] = (),
) -> CorpusIntegrityReport:
    """Recompute every destination size and digest against ``MANIFEST.json``."""
    root, root_findings = _resolve_root(destination_root, create=False)
    excluded = tuple(excluded_paths)
    if root is None:
        return _empty_integrity(root_findings, excluded_paths=excluded)
    manifest, findings = _read_manifest(root)
    if findings:
        return _empty_integrity(findings, excluded_paths=excluded)
    if manifest is None:
        return _empty_integrity(
            (
                _finding(
                    "corpus_manifest_missing",
                    path=MANIFEST_FILENAME,
                    message="The corpus manifest does not exist.",
                ),
            ),
            excluded_paths=excluded,
        )
    return _integrity_for_manifest(root, manifest, excluded_paths=excluded)


# Compatibility aliases for callers using verification terminology.
verify_corpus_integrity = validate_corpus_integrity
check_corpus_integrity = validate_corpus_integrity


def _manifest_entries_for(
    approved_files: Iterable[ApprovedImportFile],
) -> tuple[CorpusManifestEntry, ...]:
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
        for file in approved_files
    )


def _approved_files(
    approved_import_set: ApprovedImportSet,
    verification: ApprovalVerificationReport | None,
) -> tuple[ApprovedImportFile, ...]:
    if verification is None:
        return approved_import_set.files
    if verification.result is not MigrationResult.PASS:
        return ()
    files = tuple(verification.recomputed_files)
    if files != approved_import_set.files:
        return ()
    return files


def _blocked_report(
    findings: Iterable[ImportFinding],
    approved_files: Iterable[ApprovedImportFile],
) -> CorpusWriteReport:
    entries = _manifest_entries_for(approved_files)
    return _failure(
        findings,
        entries=entries,
        excluded_paths=(entry.path for entry in entries),
        result=MigrationResult.BLOCKED,
    )


@dataclass(frozen=True, slots=True)
class CorpusImporter:
    """Write one exact, verified Approved Import Set into a corpus root."""

    destination_root: PathInput

    def write(
        self,
        approved_import_set: ApprovedImportSet,
        *,
        verification: ApprovalVerificationReport | None = None,
        allow_reviewed_replacements: bool = False,
    ) -> CorpusWriteReport:
        """Stage, re-hash, and atomically publish an approved corpus set.

        Existing destinations remain immutable for ordinary imports.  A refresh
        may opt into replacement only after exact approval verification has
        passed; replacements are backed up in the staging directory so a
        failed publish restores the prior destination bytes.
        """
        if not isinstance(approved_import_set, ApprovedImportSet):
            raise TypeError("approved_import_set must be an ApprovedImportSet.")
        approved_files = _approved_files(approved_import_set, verification)
        if verification is not None and verification.result is not MigrationResult.PASS:
            return _blocked_report(verification.findings, approved_import_set.files)
        if verification is not None and not approved_files:
            return _blocked_report(
                (
                    _finding(
                        "corpus_verification_mismatch",
                        field="approved_import_set",
                        message="Verified files do not exactly match the approved import set.",
                    ),
                ),
                approved_import_set.files,
            )

        root, root_findings = _resolve_root(self.destination_root, create=False)
        excluded_paths = tuple(file.destination_path for file in approved_files)
        if root is None:
            return _failure(
                root_findings,
                entries=_manifest_entries_for(approved_files),
                excluded_paths=excluded_paths,
            )

        manifest, manifest_findings = _read_manifest(root)
        if manifest_findings:
            return _failure(
                manifest_findings,
                entries=_manifest_entries_for(approved_files),
                excluded_paths=excluded_paths,
            )
        if manifest is None:
            existing = _manifest_extra_files(root, set())
            if existing:
                existing_findings = tuple(
                    _finding(
                        "corpus_destination_collision",
                        path=path,
                        message="An existing corpus file is not declared by an import manifest.",
                    )
                    for path in existing
                )
                return _failure(
                    existing_findings,
                    entries=_manifest_entries_for(approved_files),
                    excluded_paths=excluded_paths,
                )
            manifest = CorpusManifest(entries=())
        current_integrity = _integrity_for_manifest(
            root,
            manifest,
            excluded_paths=tuple(entry.path for entry in manifest.entries),
        )
        if current_integrity.result is not MigrationResult.PASS:
            return _failure(
                current_integrity.findings,
                entries=current_integrity.entries,
                manifest_digest=current_integrity.manifest_digest,
                excluded_paths=excluded_paths,
            )

        findings: list[ImportFinding] = []
        destination_paths: dict[str, str] = {}
        destination_state: dict[str, tuple[Path, bool]] = {}
        destination_unchanged: set[str] = set()
        for file in approved_files:
            key = file.destination_path.casefold()
            previous = destination_paths.get(key)
            if previous is not None and previous != file.source_path:
                findings.append(
                    _finding(
                        "corpus_destination_collision",
                        path=file.destination_path,
                        field="destination_path",
                        message="Multiple approved files resolve to one destination.",
                    )
                )
            destination_paths[key] = file.source_path
            destination, destination_finding = _destination_path(root, file.destination_path)
            if destination_finding is not None or destination is None:
                findings.append(
                    destination_finding
                    or _finding(
                        "corpus_destination_path_mismatch",
                        path=file.destination_path,
                        message="The destination is outside the corpus root.",
                    )
                )
                continue
            destination_state[file.destination_path] = (
                destination,
                destination.exists() or destination.is_symlink(),
            )
            if destination.is_dir():
                findings.append(
                    _finding(
                        "corpus_path_mismatch",
                        path=file.destination_path,
                        message="The approved destination is an existing directory.",
                    )
                )
                continue
            if destination.exists() or destination.is_symlink():
                try:
                    actual_size, actual_digest = _hash_file(destination)
                except OSError:
                    findings.append(
                        _finding(
                            "corpus_destination_unreadable",
                            path=file.destination_path,
                            message="The existing destination could not be re-hashed.",
                        )
                    )
                    continue
                if actual_size != file.size_bytes and not allow_reviewed_replacements:
                    findings.append(
                        _finding(
                            "corpus_size_mismatch",
                            path=file.destination_path,
                            field="size_bytes",
                            message="The existing destination size differs from the approved file.",
                        )
                    )
                if actual_digest != file.sha256 and not allow_reviewed_replacements:
                    findings.append(
                        _finding(
                            "corpus_digest_mismatch",
                            path=file.destination_path,
                            field="sha256",
                            message=(
                                "The existing destination digest differs from the approved file."
                            ),
                        )
                    )
                if actual_size == file.size_bytes and actual_digest == file.sha256:
                    destination_unchanged.add(file.destination_path)

        source_root = approved_import_set.snapshot.source_root
        stage_entries = _manifest_entries_for(approved_files)
        merged_entries: dict[str, CorpusManifestEntry] = {
            entry.path: entry for entry in manifest.entries
        }
        merged_entries.update({entry.path: entry for entry in stage_entries})
        target_manifest = CorpusManifest(entries=tuple(merged_entries.values()))
        excluded_paths = tuple(entry.path for entry in target_manifest.entries)

        # Source metadata is verified before a destination can be changed.
        for file in approved_files:
            source, source_finding = _source_path(source_root, file.source_path)
            if source_finding is not None or source is None:
                findings.append(
                    source_finding
                    or _finding(
                        "corpus_source_path_invalid",
                        path=file.source_path,
                        message="The approved source path could not be resolved.",
                    )
                )
                continue
            try:
                source_size, source_digest = _hash_file(source)
            except OSError:
                findings.append(
                    _finding(
                        "corpus_source_unreadable",
                        path=file.source_path,
                        message="The approved source file could not be re-hashed.",
                    )
                )
                continue
            if source_size != file.size_bytes:
                findings.append(
                    _finding(
                        "corpus_source_size_mismatch",
                        path=file.source_path,
                        field="size_bytes",
                        message="The source size differs from the approved import metadata.",
                    )
                )
            if source_digest != file.sha256:
                findings.append(
                    _finding(
                        "corpus_source_digest_mismatch",
                        path=file.source_path,
                        field="sha256",
                        message="The source digest differs from the approved import metadata.",
                    )
                )

        if findings:
            return _failure(
                findings,
                entries=target_manifest.entries,
                manifest_digest=target_manifest.digest(),
                excluded_paths=excluded_paths,
            )

        try:
            root.mkdir(parents=True, exist_ok=True)
            stage_root = Path(tempfile.mkdtemp(prefix=_STAGE_PREFIX, dir=str(root)))
        except OSError:
            return _failure(
                (
                    _finding(
                        "corpus_staging_failed",
                        message="The verified corpus files could not be staged locally.",
                    ),
                ),
                entries=target_manifest.entries,
                manifest_digest=target_manifest.digest(),
                excluded_paths=excluded_paths,
            )

        created_destinations: list[Path] = []
        original_controls: dict[Path, bytes | None] = {}
        original_destinations: dict[Path, Path] = {}
        changed_paths: list[str] = []
        unchanged_paths: list[str] = []
        try:
            for file in approved_files:
                source, source_finding = _source_path(source_root, file.source_path)
                if source_finding is not None or source is None:
                    raise _CorpusOperationError(
                        source_finding
                        or _finding(
                            "corpus_source_path_invalid",
                            path=file.source_path,
                            message="The approved source path could not be resolved.",
                        )
                    )
                staged = stage_root.joinpath(*file.destination_path.split("/"))
                staged.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, staged)
                staged_size, staged_digest = _hash_file(staged)
                if staged_size != file.size_bytes:
                    raise _CorpusOperationError(
                        _finding(
                            "corpus_size_mismatch",
                            path=file.destination_path,
                            field="size_bytes",
                            message="The staged destination size differs from the approved file.",
                        )
                    )
                if staged_digest != file.sha256:
                    raise _CorpusOperationError(
                        _finding(
                            "corpus_digest_mismatch",
                            path=file.destination_path,
                            field="sha256",
                            message="The staged destination digest differs from the approved file.",
                        )
                    )

            staged_manifest = stage_root / MANIFEST_FILENAME
            staged_manifest.write_bytes(target_manifest.to_json_bytes())
            copied_at = approved_import_set.snapshot.recorded_at.astimezone(UTC).isoformat()
            copied_at = copied_at.replace("+00:00", "Z")
            provenance = {
                SOURCE_COMMIT_FILENAME: f"{approved_import_set.snapshot.source_commit}\n",
                SOURCE_URL_FILENAME: f"{approved_import_set.snapshot.source_repository}\n",
                SOURCE_COPIED_AT_FILENAME: f"{copied_at}\n",
            }
            staged_controls: dict[str, Path] = {MANIFEST_FILENAME: staged_manifest}
            for filename, value in provenance.items():
                staged_path = stage_root / filename
                staged_path.write_text(value, encoding="utf-8", newline="\n")
                staged_controls[filename] = staged_path

            # Ordinary imports never overwrite an existing destination.  A
            # reviewed refresh may replace an existing destination after the
            # new bytes have been staged and hashed.
            for index, file in enumerate(approved_files):
                destination = destination_state[file.destination_path][0]
                if file.destination_path in destination_unchanged:
                    unchanged_paths.append(file.destination_path)
                    continue
                staged = stage_root.joinpath(*file.destination_path.split("/"))
                if destination.exists() or destination.is_symlink():
                    if not allow_reviewed_replacements:
                        unchanged_paths.append(file.destination_path)
                        continue
                    backup = stage_root / "__backups__" / str(index)
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(destination, backup)
                    original_destinations[destination] = backup
                    os.replace(staged, destination)
                    changed_paths.append(file.destination_path)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() or destination.is_symlink():
                    raise _CorpusOperationError(
                        _finding(
                            "corpus_destination_collision",
                            path=file.destination_path,
                            message=(
                                "A destination appeared after preflight and was not overwritten."
                            ),
                        )
                    )
                os.replace(staged, destination)
                created_destinations.append(destination)
                changed_paths.append(file.destination_path)

            for filename, staged_path in staged_controls.items():
                destination = root / filename
                new_bytes = staged_path.read_bytes()
                old_bytes: bytes | None
                try:
                    old_bytes = destination.read_bytes() if destination.exists() else None
                except OSError:
                    old_bytes = None
                original_controls[destination] = old_bytes
                if old_bytes == new_bytes:
                    unchanged_paths.append(filename)
                    continue
                os.replace(staged_path, destination)
                changed_paths.append(filename)

            integrity = validate_corpus_integrity(root, excluded_paths=excluded_paths)
            if integrity.result is not MigrationResult.PASS:
                _rollback_new_destinations(created_destinations)
                _rollback_replacements(original_destinations)
                _restore_controls(original_controls)
                return _failure(
                    integrity.findings,
                    entries=integrity.entries,
                    manifest_digest=integrity.manifest_digest,
                    excluded_paths=excluded_paths,
                    changed_paths=(),
                    unchanged_paths=(),
                )
            result = MigrationResult.PASS if changed_paths else MigrationResult.NO_CHANGE
            return _failure(
                (),
                entries=target_manifest.entries,
                manifest_digest=target_manifest.digest(),
                excluded_paths=excluded_paths,
                result=result,
                changed_paths=changed_paths,
                unchanged_paths=unchanged_paths,
            )
        except _CorpusOperationError as error:
            _rollback_new_destinations(created_destinations)
            _rollback_replacements(original_destinations)
            _restore_controls(original_controls)
            return _failure(
                (error.finding,),
                entries=target_manifest.entries,
                manifest_digest=target_manifest.digest(),
                excluded_paths=excluded_paths,
                changed_paths=(),
                unchanged_paths=(),
            )
        except (OSError, ValueError, TypeError) as error:
            _rollback_new_destinations(created_destinations)
            _rollback_replacements(original_destinations)
            _restore_controls(original_controls)
            return _failure(
                (
                    _finding(
                        "corpus_publish_failed",
                        message=f"Corpus publication failed: {type(error).__name__}.",
                    ),
                ),
                entries=target_manifest.entries,
                manifest_digest=target_manifest.digest(),
                excluded_paths=excluded_paths,
            )
        finally:
            shutil.rmtree(stage_root, ignore_errors=True)


def _rollback_new_destinations(paths: Iterable[Path]) -> None:
    """Remove only files created by this failed operation, never old pack files."""
    for path in reversed(tuple(paths)):
        try:
            if path.is_file() and not path.is_symlink():
                path.unlink()
        except OSError:
            pass


def _rollback_replacements(original_destinations: Mapping[Path, Path]) -> None:
    """Restore destination files replaced by a failed reviewed refresh."""
    for destination, backup in original_destinations.items():
        try:
            if backup.exists():
                shutil.copyfile(backup, destination)
        except OSError:
            pass


def _restore_controls(original_controls: Mapping[Path, bytes | None]) -> None:
    for path, original in original_controls.items():
        try:
            if original is None:
                if path.exists() and path.is_file():
                    path.unlink()
            else:
                path.write_bytes(original)
        except OSError:
            pass


class _CorpusOperationError(Exception):
    def __init__(self, finding: ImportFinding) -> None:
        self.finding = finding
        super().__init__(finding.message)


def write_corpus(
    destination_root: PathInput,
    approved_import_set: ApprovedImportSet,
    *,
    verification: ApprovalVerificationReport | None = None,
    allow_reviewed_replacements: bool = False,
) -> CorpusWriteReport:
    """Convenience wrapper for :class:`CorpusImporter`."""
    return CorpusImporter(destination_root).write(
        approved_import_set,
        verification=verification,
        allow_reviewed_replacements=allow_reviewed_replacements,
    )


def write_approved_corpus(
    destination_root: PathInput,
    approved_import_set: ApprovedImportSet,
    *,
    verification: ApprovalVerificationReport | None = None,
    allow_reviewed_replacements: bool = False,
) -> CorpusWriteReport:
    """Compatibility alias for :func:`write_corpus`."""
    return write_corpus(
        destination_root,
        approved_import_set,
        verification=verification,
        allow_reviewed_replacements=allow_reviewed_replacements,
    )


# Explicit names for callers that use "import" rather than "write".
import_corpus = write_corpus
stage_and_publish_corpus = write_corpus


__all__ = [
    "CORPUS_CLASSIFICATION",
    "CORPUS_SCHEMA_VERSION",
    "MANIFEST_FILENAME",
    "SOURCE_COMMIT_FILENAME",
    "SOURCE_COPIED_AT_FILENAME",
    "SOURCE_URL_FILENAME",
    "CorpusImportReport",
    "CorpusImporter",
    "CorpusIntegrityReport",
    "CorpusManifest",
    "CorpusValidationReport",
    "CorpusWriteReport",
    "check_corpus_integrity",
    "import_corpus",
    "stage_and_publish_corpus",
    "validate_corpus_integrity",
    "verify_corpus_integrity",
    "write_approved_corpus",
    "write_corpus",
]
