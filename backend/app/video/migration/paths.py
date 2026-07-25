"""Fail-closed local path normalization and containment utilities."""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path, PureWindowsPath
from typing import Final

from app.video.migration.canonical import redact_diagnostic

_LOCAL_PATH_ERROR_MESSAGES: Final[dict[str, str]] = {
    "absolute_path": "Absolute paths are not accepted.",
    "empty_path": "A relative path is required.",
    "invalid_path": "The path is not a safe relative path.",
    "nul_byte": "NUL bytes are not accepted in paths.",
    "path_traversal": "Parent-directory traversal is not accepted.",
    "out_of_root": "The path resolves outside its approved root.",
    "missing_path": "The required local path does not exist.",
    "unreadable_path": "The required local path is not readable.",
    "not_a_file": "The required local path is not a regular file.",
    "not_a_directory": "The approved root is not a directory.",
}


class UnsafeLocalPathError(ValueError):
    """A redaction-safe path validation failure."""

    def __init__(self, code: str, path: str | None = None) -> None:
        self.code = code
        self.path = redact_diagnostic(path) if path is not None else None
        super().__init__(_LOCAL_PATH_ERROR_MESSAGES.get(code, "Unsafe local path."))


PathInput = str | os.PathLike[str]


def normalize_relative_path(value: PathInput) -> str:
    """Normalize a path to forward-slash relative form without resolving traversal."""
    try:
        raw_value = os.fspath(value)
    except TypeError as error:
        raise UnsafeLocalPathError("invalid_path") from error
    if not isinstance(raw_value, str):
        raise UnsafeLocalPathError("invalid_path")
    raw = unicodedata.normalize("NFKC", raw_value).strip().replace("\\", "/")
    if not raw:
        raise UnsafeLocalPathError("empty_path")
    if "\x00" in raw:
        raise UnsafeLocalPathError("nul_byte")
    windows_path = PureWindowsPath(raw)
    if raw.startswith("/") or windows_path.is_absolute() or bool(windows_path.drive):
        raise UnsafeLocalPathError("absolute_path", raw)
    components = [component for component in raw.split("/") if component not in ("", ".")]
    if not components:
        raise UnsafeLocalPathError("empty_path", raw)
    if any(component == ".." for component in components):
        raise UnsafeLocalPathError("path_traversal", raw)
    normalized = "/".join(components)
    if normalized in (".", ".."):
        raise UnsafeLocalPathError("invalid_path", raw)
    return normalized


def is_within_root(candidate: PathInput, root: PathInput) -> bool:
    """Return whether a resolved candidate is contained by a resolved root."""
    try:
        candidate_path = Path(candidate).resolve(strict=False)
        root_path = Path(root).resolve(strict=False)
        candidate_path.relative_to(root_path)
    except (OSError, ValueError):
        return False
    return True


def resolve_under_root(
    root: PathInput,
    relative_path: PathInput,
    *,
    must_exist: bool = False,
    require_readable: bool = False,
) -> Path:
    """Resolve a relative path under ``root`` and reject symlink escapes."""
    normalized = normalize_relative_path(relative_path)
    try:
        root_path = Path(root).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise UnsafeLocalPathError("out_of_root") from error
    if not root_path.is_dir():
        raise UnsafeLocalPathError("not_a_directory", str(root_path))
    candidate = root_path.joinpath(*normalized.split("/"))
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_path)
    except (OSError, RuntimeError, ValueError) as error:
        raise UnsafeLocalPathError("out_of_root", normalized) from error
    if must_exist and not resolved.exists():
        raise UnsafeLocalPathError("missing_path", normalized)
    if require_readable:
        if not resolved.exists():
            raise UnsafeLocalPathError("missing_path", normalized)
        if not os.access(resolved, os.R_OK):
            raise UnsafeLocalPathError("unreadable_path", normalized)
        if resolved.is_file():
            try:
                with resolved.open("rb"):
                    pass
            except OSError as error:
                raise UnsafeLocalPathError("unreadable_path", normalized) from error
    return resolved


def safe_local_path(
    root: PathInput,
    relative_path: PathInput,
    *,
    must_exist: bool = False,
    require_readable: bool = False,
) -> Path:
    """Compatibility name for :func:`resolve_under_root`."""
    return resolve_under_root(
        root,
        relative_path,
        must_exist=must_exist,
        require_readable=require_readable,
    )


def read_local_bytes(root: PathInput, relative_path: PathInput) -> bytes:
    """Read one contained regular file without exposing its contents in errors."""
    path = resolve_under_root(root, relative_path, must_exist=True, require_readable=True)
    if not path.is_file():
        raise UnsafeLocalPathError("not_a_file", str(relative_path))
    try:
        return path.read_bytes()
    except (OSError, UnicodeError) as error:
        raise UnsafeLocalPathError("unreadable_path", str(relative_path)) from error


def validate_required_local_reference(root: PathInput, relative_path: PathInput) -> Path:
    """Resolve a required local reference and require an existing readable file."""
    return resolve_under_root(root, relative_path, must_exist=True, require_readable=True)


def safe_join(root: PathInput, relative_path: PathInput) -> Path:
    """Compatibility name for a contained, non-mutating path join."""
    return resolve_under_root(root, relative_path)
