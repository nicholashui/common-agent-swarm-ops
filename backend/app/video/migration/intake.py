"""Offline source discovery and deterministic Video Pack intake planning.

The planner deliberately has no network, subprocess, or configuration-loading
capability. Source files are read only as bytes for metadata and bounded
classification; their instructions are never parsed or executed.
"""

from __future__ import annotations

import codecs
import hashlib
import os
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.video.migration.contracts import (
    ImportCandidate,
    ImportDryRunReport,
    ImportFinding,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.paths import (
    PathInput,
    UnsafeLocalPathError,
    normalize_relative_path,
    resolve_under_root,
)

# These names are excluded before their contents can become an import. Their
# children are still enumerated so a report remains complete and reviewable.
_PROHIBITED_DIRECTORY_NAMES: Final[frozenset[str]] = frozenset(
    {
        ".cache",
        ".git",
        ".hg",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "build",
        "coverage",
        "dist",
        "env",
        "node_modules",
        "venv",
    }
)
_PROHIBITED_FILE_NAMES: Final[frozenset[str]] = frozenset(
    {
        ".ds_store",
        "thumbs.db",
        ".env",
        ".npmrc",
        ".pypirc",
        "credentials",
        "credentials.json",
        "id_rsa",
        "id_ed25519",
        "known_hosts",
    }
)
_PROHIBITED_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        ".avi",
        ".bin",
        ".class",
        ".dll",
        ".dmg",
        ".exe",
        ".gif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".m4a",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".o",
        ".pdf",
        ".pyc",
        ".so",
        ".wav",
        ".webm",
        ".webp",
    }
)
_PROHIBITED_LOG_SUFFIXES: Final[frozenset[str]] = frozenset({".log", ".trace"})
_LICENSE_GAP_VALUES: Final[frozenset[str]] = frozenset(
    {
        "",
        "missing",
        "not provided",
        "not_provided",
        "pending",
        "tbd",
        "unknown",
        "undetermined",
        "unreviewed",
    }
)
_SECRET_BYTES = (
    re.compile(
        rb"(?i)(?:api[_-]?key|access[_-]?key|secret|token|password|credential|authorization)"
        rb"\s*[:=]\s*[^\s,;]{4,}"
    ),
    re.compile(rb"(?i)-----begin [^-]+ private key-----"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\b(?:ghp|github_pat|sk|xox[baprs])_[A-Za-z0-9_-]{12,}\b"),
)
_PERSONAL_DATA_BYTES = (
    re.compile(rb"(?i)\b(?:social security number|ssn)\s*[:=]"),
    re.compile(rb"(?i)\bcredit card number\s*[:=]"),
    re.compile(rb"(?i)\bdate of birth\s*[:=]"),
)
_PERSONAL_DATA_NAME_PARTS: Final[frozenset[str]] = frozenset(
    {"personal_data", "personal-data", "pii", "customer_data", "customer-data"}
)
_SECRET_NAME_PARTS: Final[frozenset[str]] = frozenset(
    {"secret", "secrets", "credential", "credentials", "password", "private_key"}
)
_MAX_SCAN_CHUNK: Final[int] = 1024 * 1024
_UNSAFE_REASONS: Final[frozenset[str]] = frozenset(
    {"unsafe source path", "unsafe source link", "unreadable source link"}
)
_UNREADABLE_REASONS: Final[frozenset[str]] = frozenset({"unreadable source directory"})

LicenseDeclaration = str | Mapping[str, str] | None
DestinationMapper = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class _FileMetadata:
    """Metadata calculated without retaining source-body content."""

    size_bytes: int
    sha256: str
    is_binary: bool
    has_secret: bool
    has_personal_data: bool


@dataclass(frozen=True, slots=True)
class SourceIntakePlanner:
    """Build a side-effect-free, canonical report from a local source tree."""

    source_root: PathInput
    destination_root: PathInput
    destination_prefix: str = ""
    allow_paths: tuple[str, ...] = ()
    license_status: LicenseDeclaration = None
    destination_mapper: DestinationMapper | None = None
    allowed_existing_destinations: tuple[str, ...] = ()

    def plan(
        self,
        snapshot: SourceSnapshot,
        *,
        mode: ImportMode = ImportMode.DRY_RUN,
    ) -> ImportDryRunReport:
        """Discover and classify all source candidates without changing any path."""
        included: list[ImportCandidate] = []
        excluded: list[ImportCandidate] = []
        findings: list[ImportFinding] = []
        destination_keys: dict[str, str] = {}

        mode = ImportMode(mode)
        if mode is not ImportMode.DRY_RUN:
            findings.append(
                ImportFinding(
                    "write_mode_not_supported",
                    field="mode",
                    message=(
                        "Source discovery is dry-run only; write mode belongs to the import gate."
                    ),
                )
            )

        try:
            source_root = Path(self.source_root).resolve(strict=True)
        except (OSError, RuntimeError, TypeError):
            source_root = None
        if source_root is None or not source_root.is_dir():
            findings.append(
                ImportFinding(
                    "invalid_source_root",
                    path=str(self.source_root),
                    message="The source root is not an accessible local directory.",
                )
            )
            return _report(snapshot, mode, included, excluded, findings)

        try:
            destination_root = Path(self.destination_root).resolve(strict=False)
        except (OSError, RuntimeError, TypeError):
            destination_root = None
            findings.append(
                ImportFinding(
                    "invalid_destination_root",
                    path=str(self.destination_root),
                    message="The destination root cannot be resolved as a local path.",
                )
            )

        prefix, prefix_error = _normalize_prefix(self.destination_prefix)
        if prefix_error is not None:
            findings.append(prefix_error)

        allowed_paths, allow_errors = _normalize_allow_paths(self.allow_paths)
        findings.extend(allow_errors)
        allowed_existing_destinations, destination_allow_errors = _normalize_allow_paths(
            self.allowed_existing_destinations
        )
        findings.extend(destination_allow_errors)
        allowed_existing_destinations = allowed_existing_destinations or ()

        try:
            entries = _walk_source(source_root)
        except OSError:
            entries = ()
            findings.append(
                ImportFinding(
                    "unreadable_source",
                    message="The source tree could not be enumerated.",
                )
            )

        for relative_path, entry, inherited_reason in entries:
            destination_path = _map_destination(
                relative_path,
                prefix,
                self.destination_mapper,
                prefix_error is None,
            )
            unsafe_reason = inherited_reason if _is_unsafe_reason(inherited_reason) else None
            if unsafe_reason is not None:
                excluded.append(
                    ImportCandidate(
                        source_path=relative_path,
                        destination_path=destination_path,
                        classification="excluded",
                        reason=unsafe_reason,
                    )
                )
                findings.append(
                    ImportFinding(
                        "unsafe_path",
                        path=relative_path,
                        message=unsafe_reason,
                    )
                )
                continue
            unreadable_reason = (
                inherited_reason if _is_unreadable_reason(inherited_reason) else None
            )
            if unreadable_reason is not None:
                excluded.append(
                    ImportCandidate(
                        source_path=relative_path,
                        destination_path=destination_path,
                        classification="excluded",
                        reason=unreadable_reason,
                    )
                )
                findings.append(
                    ImportFinding(
                        "unreadable_source",
                        path=relative_path,
                        message=unreadable_reason,
                    )
                )
                continue
            if entry.is_dir() or inherited_reason == "symlinked directory":
                directory_reason = inherited_reason or "prohibited directory"
                excluded.append(
                    ImportCandidate(
                        source_path=relative_path,
                        destination_path=destination_path,
                        classification="excluded",
                        reason=directory_reason,
                    )
                )
                findings.append(
                    ImportFinding(
                        "prohibited_material",
                        path=relative_path,
                        message=directory_reason,
                    )
                )
                continue

            metadata, metadata_error = _file_metadata(entry, source_root, relative_path)
            if metadata_error is not None:
                candidate = ImportCandidate(
                    source_path=relative_path,
                    destination_path=destination_path,
                    classification="excluded",
                    reason="unreadable source candidate",
                )
                excluded.append(candidate)
                findings.append(
                    ImportFinding(
                        "unreadable_source",
                        path=relative_path,
                        message=metadata_error,
                    )
                )
                continue
            assert metadata is not None

            candidate_reason: str | None = inherited_reason or _name_prohibition(relative_path)
            if candidate_reason is None and metadata.is_binary:
                candidate_reason = "binary or generated media"
            if candidate_reason is None and metadata.has_personal_data:
                candidate_reason = "personal data"
            if candidate_reason is None and metadata.has_secret:
                candidate_reason = "secret material"

            if not _is_requested(relative_path, allowed_paths):
                candidate_reason = candidate_reason or "not requested by the allow-list"

            if candidate_reason is None:
                candidate = ImportCandidate(
                    source_path=relative_path,
                    destination_path=destination_path,
                    size_bytes=metadata.size_bytes,
                    sha256=metadata.sha256,
                    classification="included",
                )
                included.append(candidate)
                _add_destination_findings(
                    relative_path,
                    destination_path,
                    destination_root,
                    destination_keys,
                    findings,
                    allowed_existing_destinations,
                )
                _add_license_finding(relative_path, self.license_status, findings)
                continue

            excluded.append(
                ImportCandidate(
                    source_path=relative_path,
                    destination_path=destination_path,
                    size_bytes=metadata.size_bytes,
                    sha256=metadata.sha256,
                    classification="excluded",
                    reason=candidate_reason,
                )
            )
            if candidate_reason != "not requested by the allow-list":
                findings.append(
                    ImportFinding(
                        "prohibited_material",
                        path=relative_path,
                        message=candidate_reason,
                    )
                )
            if metadata.has_secret:
                findings.append(
                    ImportFinding(
                        "secret",
                        path=relative_path,
                        message=(
                            "Secret-like material was detected; source bytes were not retained."
                        ),
                    )
                )

        return _report(snapshot, mode, included, excluded, findings)


def plan_source_intake(
    source_root: PathInput,
    snapshot: SourceSnapshot,
    *,
    destination_root: PathInput,
    destination_prefix: str = "",
    allow_paths: Iterable[PathInput] = (),
    license_status: LicenseDeclaration = None,
    destination_mapper: DestinationMapper | None = None,
    allowed_existing_destinations: Iterable[PathInput] = (),
    mode: ImportMode = ImportMode.DRY_RUN,
) -> ImportDryRunReport:
    """Plan a local source import using the task 1.1 migration contracts."""
    return SourceIntakePlanner(
        source_root=source_root,
        destination_root=destination_root,
        destination_prefix=destination_prefix,
        allow_paths=tuple(os.fspath(path) for path in allow_paths),
        license_status=license_status,
        destination_mapper=destination_mapper,
        allowed_existing_destinations=tuple(
            os.fspath(path) for path in allowed_existing_destinations
        ),
    ).plan(snapshot, mode=mode)


# Descriptive compatibility names for callers that treat planning as discovery.
discover_source_candidates = plan_source_intake
build_dry_run_report = plan_source_intake


def _report(
    snapshot: SourceSnapshot,
    mode: ImportMode,
    included: Iterable[ImportCandidate],
    excluded: Iterable[ImportCandidate],
    findings: Iterable[ImportFinding],
) -> ImportDryRunReport:
    included_items = tuple(included)
    findings_items = tuple(findings)
    result = MigrationResult.FAIL if findings_items else MigrationResult.PASS
    return ImportDryRunReport(
        snapshot=snapshot,
        mode=mode,
        included=included_items,
        excluded=tuple(excluded),
        findings=findings_items,
        total_bytes=sum(item.size_bytes or 0 for item in included_items),
        result=result,
    )


def _normalize_prefix(prefix: str) -> tuple[str, ImportFinding | None]:
    if not prefix or prefix in (".", "./"):
        return "", None
    try:
        return normalize_relative_path(prefix), None
    except UnsafeLocalPathError as error:
        return "", ImportFinding(
            "unsafe_destination_path",
            field="destination_prefix",
            message=f"The destination prefix is not safe ({error.code}).",
        )


def _normalize_allow_paths(
    paths: Iterable[str],
) -> tuple[tuple[str, ...] | None, tuple[ImportFinding, ...]]:
    values = tuple(paths)
    if not values:
        return None, ()
    normalized: list[str] = []
    findings: list[ImportFinding] = []
    for value in values:
        try:
            normalized.append(normalize_relative_path(value))
        except UnsafeLocalPathError as error:
            findings.append(
                ImportFinding(
                    "unsafe_path",
                    field="allow_list",
                    message=f"An allow-list path is unsafe ({error.code}).",
                )
            )
    return tuple(sorted(set(normalized))), tuple(findings)


def _is_requested(relative_path: str, allowed_paths: tuple[str, ...] | None) -> bool:
    if allowed_paths is None:
        return True
    return any(
        relative_path == allowed or relative_path.startswith(f"{allowed}/")
        for allowed in allowed_paths
    )


def _map_destination(
    relative_path: str,
    prefix: str,
    mapper: DestinationMapper | None,
    prefix_is_safe: bool,
) -> str | None:
    if not prefix_is_safe:
        return None
    try:
        mapped = (
            mapper(relative_path)
            if mapper is not None
            else (f"{prefix}/{relative_path}" if prefix else relative_path)
        )
        return normalize_relative_path(mapped)
    except (TypeError, ValueError, UnsafeLocalPathError):
        return None


def _walk_source(
    source_root: Path,
) -> tuple[tuple[str, Path, str | None], ...]:
    """Return sorted file/symlink candidates, retaining prohibited descendants."""
    candidates: list[tuple[str, Path, str | None]] = []

    def visit(directory: Path, inherited_reason: str | None = None) -> None:
        try:
            with os.scandir(directory) as scan:
                entries = sorted(scan, key=lambda item: item.name.casefold())
        except OSError:
            if directory == source_root:
                raise
            relative = directory.relative_to(source_root).as_posix()
            candidates.append((relative, directory, "unreadable source directory"))
            return
        for entry in entries:
            entry_path = Path(entry.path)
            relative = entry_path.relative_to(source_root).as_posix()
            if "\\" in relative:
                candidates.append((relative.replace("\\", "/"), entry_path, "unsafe source path"))
                continue
            is_symlink = entry.is_symlink()
            if entry.is_dir(follow_symlinks=False):
                directory_reason = inherited_reason or _directory_prohibition(entry.name)
                if directory_reason is not None:
                    # The directory itself is a reviewable excluded candidate.
                    candidates.append((relative, entry_path, directory_reason))
                    try:
                        visit(entry_path, directory_reason)
                    except OSError:
                        candidates.append((relative, entry_path, "unreadable prohibited directory"))
                else:
                    visit(entry_path, inherited_reason)
                continue
            if is_symlink:
                try:
                    resolved = entry_path.resolve(strict=True)
                    resolved.relative_to(source_root)
                except (OSError, RuntimeError, ValueError):
                    candidates.append((relative, entry_path, "unsafe source link"))
                    continue
                if resolved.is_dir():
                    candidates.append((relative, entry_path, "symlinked directory"))
                    continue
            candidates.append((relative, entry_path, inherited_reason))

    visit(source_root)
    return tuple(sorted(candidates, key=lambda item: item[0].casefold()))


def _is_unsafe_reason(value: str | None) -> bool:
    return value is not None and value in _UNSAFE_REASONS


def _is_unreadable_reason(value: str | None) -> bool:
    return value is not None and value in _UNREADABLE_REASONS


def _directory_prohibition(name: str) -> str | None:
    lowered = name.casefold()
    if lowered in _PROHIBITED_DIRECTORY_NAMES:
        return "prohibited directory"
    return None


def _name_prohibition(relative_path: str) -> str | None:
    parts = relative_path.split("/")
    basename = parts[-1].casefold()
    if basename in _PROHIBITED_FILE_NAMES:
        return "credential or metadata file"
    if basename.endswith(tuple(_PROHIBITED_LOG_SUFFIXES)) or basename in {"debug.log", "error.log"}:
        return "log output"
    stem_parts = {part.casefold() for part in parts}
    if stem_parts & _SECRET_NAME_PARTS:
        return "credential or secret material"
    if stem_parts & _PERSONAL_DATA_NAME_PARTS:
        return "personal data"
    if basename.endswith(tuple(_PROHIBITED_SUFFIXES)):
        return "binary or generated media"
    return None


def _file_metadata(
    entry: Path,
    source_root: Path,
    relative_path: str,
) -> tuple[_FileMetadata | None, str | None]:
    try:
        resolved = resolve_under_root(
            source_root, relative_path, must_exist=True, require_readable=True
        )
        if not resolved.is_file():
            return None, "The candidate is not a regular file."
        digest = hashlib.sha256()
        size = 0
        is_binary = False
        has_secret = False
        has_personal_data = False
        decoder = codecs.getincrementaldecoder("utf-8")("strict")
        inspection_window = b""
        with resolved.open("rb") as source_file:
            while True:
                chunk = source_file.read(_MAX_SCAN_CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
                is_binary = is_binary or b"\x00" in chunk
                try:
                    decoder.decode(chunk, final=False)
                except UnicodeDecodeError:
                    is_binary = True
                inspection_window = (inspection_window + chunk)[-8192:]
                if any(pattern.search(inspection_window) for pattern in _SECRET_BYTES):
                    has_secret = True
                if any(pattern.search(inspection_window) for pattern in _PERSONAL_DATA_BYTES):
                    has_personal_data = True
        try:
            decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            is_binary = True
        if resolved.suffix.casefold() in _PROHIBITED_SUFFIXES:
            is_binary = True
        return _FileMetadata(
            size, digest.hexdigest(), is_binary, has_secret, has_personal_data
        ), None
    except (OSError, RuntimeError, UnsafeLocalPathError) as error:
        return None, f"The source candidate could not be read ({type(error).__name__})."


def _license_for(path: str, declaration: LicenseDeclaration) -> str | None:
    if isinstance(declaration, Mapping):
        value = declaration.get(path, declaration.get("*"))
        return value if isinstance(value, str) else None
    return declaration if isinstance(declaration, str) else None


def _add_license_finding(
    relative_path: str,
    declaration: LicenseDeclaration,
    findings: list[ImportFinding],
) -> None:
    value = _license_for(relative_path, declaration)
    if value is None or value.strip().casefold() in _LICENSE_GAP_VALUES:
        findings.append(
            ImportFinding(
                "license_provenance_gap",
                path=relative_path,
                field="license_status",
                message="A reviewed license status is required before import approval.",
            )
        )


def _add_destination_findings(
    relative_path: str,
    destination_path: str | None,
    destination_root: Path | None,
    destination_keys: dict[str, str],
    findings: list[ImportFinding],
    allowed_existing_destinations: tuple[str, ...],
) -> None:
    if destination_path is None:
        findings.append(
            ImportFinding(
                "unsafe_destination_path",
                path=relative_path,
                field="destination_path",
                message="The candidate could not be mapped to a safe relative destination.",
            )
        )
        return
    key = destination_path.casefold()
    previous = destination_keys.get(key)
    if previous is not None and previous != relative_path:
        findings.append(
            ImportFinding(
                "destination_collision",
                path=relative_path,
                field="destination_path",
                message=f"Destination is also mapped from {previous}.",
            )
        )
    else:
        destination_keys[key] = relative_path
    if destination_root is None:
        return
    try:
        candidate = destination_root.joinpath(*destination_path.split("/"))
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(destination_root)
        if (candidate.exists() or candidate.is_symlink()) and destination_path.casefold() not in {
            path.casefold() for path in allowed_existing_destinations
        }:
            findings.append(
                ImportFinding(
                    "destination_collision",
                    path=relative_path,
                    field="destination_path",
                    message="The destination already exists and is not declared for replacement.",
                )
            )
    except (OSError, RuntimeError, ValueError):
        findings.append(
            ImportFinding(
                "unsafe_destination_path",
                path=relative_path,
                field="destination_path",
                message="The mapped destination resolves outside the destination root.",
            )
        )


__all__ = [
    "DestinationMapper",
    "LicenseDeclaration",
    "SourceIntakePlanner",
    "build_dry_run_report",
    "discover_source_candidates",
    "plan_source_intake",
]
