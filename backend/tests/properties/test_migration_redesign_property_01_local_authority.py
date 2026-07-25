"""Property checks for local required references and historical provenance."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

import pytest
from hypothesis import example, given, settings, strategies as st

from app.video.migration.canonical import canonical_json, digest_json
from app.video.migration.contracts import HistoricalProvenance
from app.video.migration.paths import (
    UnsafeLocalPathError,
    is_within_root,
    validate_required_local_reference,
)

_SAFE_COMPONENTS: Final = (
    "README.md",
    "manifest.json",
    "knowledge",
    "seed.txt",
    "agents",
    "agent-spec.md",
    "v1",
)
_SAFE_RELATIVE_PATHS = st.lists(
    st.sampled_from(_SAFE_COMPONENTS),
    min_size=1,
    max_size=3,
).map("/".join)
_UNSAFE_RELATIVE_PATHS = st.sampled_from(
    (
        "../outside.md",
        "nested/../../outside.md",
        "/outside.md",
        "C:/outside.md",
        r"C:\outside.md",
    )
)
_PROVENANCE_REPOSITORIES: Final = (
    "https://example.invalid/generic-swarm-ops",
    "https://example.invalid/va-agent-swarm",
)
_PROVENANCE_COMMITS: Final = ("commit-a", "commit-b", "snapshot-2025-01")
_PROVENANCE_PATHS: Final = (
    "upstream/video/SPEC.md",
    "source/agents/producer.md",
    "historical/corpus/README.md",
)
_LICENSE_STATUSES: Final = ("reviewed", "permissive", "pending-review")


# **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 6.1, 6.4, 6.8, 8.7**
# Feature: migration-redesign, Property 1: Required references are local and
# provenance remains non-binding
@settings(max_examples=24, deadline=None, derandomize=True)
@given(relative_path=_SAFE_RELATIVE_PATHS)
def test_required_local_references_resolve_under_repository_root(
    relative_path: str,
) -> None:
    """Every generated required reference resolves only to an existing local file."""
    with TemporaryDirectory() as temporary_root:
        repository_root = Path(temporary_root)
        local_file = repository_root.joinpath(*relative_path.split("/"))
        local_file.parent.mkdir(parents=True, exist_ok=True)
        local_file.write_bytes(b"local video-pack reference")

        resolved = validate_required_local_reference(repository_root, relative_path)

        assert resolved == local_file.resolve()
        assert is_within_root(resolved, repository_root)
        assert canonical_json({"required_local_reference": relative_path}) == (
            '{"required_local_reference":"' + relative_path + '"}'
        )


# **Validates: Requirements 1.3, 1.4, 1.5, 6.4, 6.8, 8.7**
@settings(max_examples=12, deadline=None, derandomize=True)
@example("../outside.md")
@example("/outside.md")
@given(relative_path=_UNSAFE_RELATIVE_PATHS)
def test_external_and_escaping_required_references_are_rejected(
    relative_path: str,
) -> None:
    """Absolute, Windows-absolute, and traversal references fail closed."""
    with TemporaryDirectory() as temporary_root, pytest.raises(UnsafeLocalPathError) as raised:
        validate_required_local_reference(Path(temporary_root), relative_path)

    assert raised.value.code in {"absolute_path", "path_traversal"}


# **Validates: Requirements 1.3, 1.4, 6.4, 6.8, 8.7**
def test_missing_required_reference_is_rejected(tmp_path: Path) -> None:
    """A missing local file cannot become a required local reference."""
    with pytest.raises(UnsafeLocalPathError) as raised:
        validate_required_local_reference(tmp_path, "business/video/README.md")

    assert raised.value.code == "missing_path"


# **Validates: Requirements 1.5, 1.6, 6.1, 6.4, 6.8**
@settings(max_examples=12, deadline=None, derandomize=True)
@given(
    repository=st.sampled_from(_PROVENANCE_REPOSITORIES),
    commit=st.sampled_from(_PROVENANCE_COMMITS),
    original_path=st.sampled_from(_PROVENANCE_PATHS),
    license_status=st.sampled_from(_LICENSE_STATUSES),
)
def test_upstream_metadata_is_canonical_historical_provenance(
    repository: str,
    commit: str,
    original_path: str,
    license_status: str,
) -> None:
    """Upstream fields are retained as metadata and never satisfy local authority."""
    provenance = HistoricalProvenance(
        repository=repository,
        commit=commit,
        path=original_path,
        license_status=license_status,
    )
    local_reference = "business/video/README.md"
    with TemporaryDirectory() as temporary_root:
        repository_root = Path(temporary_root)
        local_file = repository_root.joinpath(*local_reference.split("/"))
        local_file.parent.mkdir(parents=True, exist_ok=True)
        local_file.write_text("local authority", encoding="utf-8")

        assert (
            validate_required_local_reference(repository_root, local_reference)
            == local_file.resolve()
        )
        with pytest.raises(UnsafeLocalPathError) as raised:
            validate_required_local_reference(repository_root, provenance.path)

    assert raised.value.code == "missing_path"
    assert provenance.to_dict() == {
        "commit": commit,
        "license_status": license_status,
        "path": original_path,
        "repository": repository,
    }
    assert provenance.canonical_json() == canonical_json(provenance.to_dict())
    assert provenance.digest() == digest_json(provenance.to_dict())
