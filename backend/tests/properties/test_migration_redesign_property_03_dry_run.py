"""Property checks for deterministic, bounded, side-effect-free dry-run intake."""

from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import tempfile
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, NoReturn

import pytest
from hypothesis import given, settings, strategies as st

from app.video.migration.contracts import (
    ImportCandidate,
    ImportDryRunReport,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.intake import plan_source_intake

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_IMPORT_CLI: Final[Path] = _REPOSITORY_ROOT / "scripts" / "business" / "import_video_corpus.py"
_RECORDED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_MAX_GENERATED_FILES: Final[int] = 5
_MAX_GENERATED_BYTES: Final[int] = 64
_SAFE_CONTENT_ALPHABET: Final[tuple[str, ...]] = tuple(
    "abcdefghijklmnopqrstuvwxyz .,;!?-_/0123456789"
)
_SAFE_SEGMENT = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=8,
)
_SAFE_SOURCE_PATH = st.builds(
    lambda parents, leaf: "/".join((*parents, f"{leaf}.md")),
    st.lists(_SAFE_SEGMENT, min_size=0, max_size=2),
    _SAFE_SEGMENT,
)
_SAFE_CONTENT = st.text(
    alphabet=st.sampled_from(_SAFE_CONTENT_ALPHABET),
    min_size=0,
    max_size=_MAX_GENERATED_BYTES,
).map(lambda value: value.encode("ascii"))
_BOUNDED_SOURCE_TREE = st.dictionaries(
    keys=_SAFE_SOURCE_PATH,
    values=_SAFE_CONTENT,
    max_size=_MAX_GENERATED_FILES,
)


def _snapshot() -> SourceSnapshot:
    """Return the same logical pinned snapshot for equivalent local fixtures."""
    return SourceSnapshot(
        source_repository="https://example.invalid/video",
        source_commit="fixture-commit-1",
        source_root="fixture/source",
        recorded_at=_RECORDED_AT,
    )


def _write_source_tree(root: Path, files: Mapping[str, bytes], *, reverse: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    items = tuple(files.items())
    if reverse:
        items = tuple(reversed(items))
    for relative_path, content in items:
        path = root.joinpath(*relative_path.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def _tree_state(root: Path) -> tuple[tuple[str, bytes], ...] | None:
    """Capture only destination files, preserving the absence of a root."""
    if not root.exists():
        return None
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    return tuple((path.relative_to(root).as_posix(), path.read_bytes()) for path in files)


def _candidate_by_source(report: ImportDryRunReport) -> dict[str, ImportCandidate]:
    candidates = (*report.included, *report.excluded)
    by_source = {candidate.source_path: candidate for candidate in candidates}
    assert len(by_source) == len(candidates)
    return by_source


def _assert_complete_metadata(
    report: ImportDryRunReport,
    files: Mapping[str, bytes],
    *,
    destination_prefix: str,
) -> None:
    candidates = _candidate_by_source(report)
    assert set(candidates) == set(files)
    for relative_path, content in files.items():
        candidate = candidates[relative_path]
        assert candidate.destination_path == f"{destination_prefix}/{relative_path}"
        assert candidate.size_bytes == len(content)
        assert candidate.sha256 == hashlib.sha256(content).hexdigest()
        assert candidate.classification == "included"
    assert report.total_bytes == sum(len(content) for content in files.values())


# **Validates: Requirements 3.1, 3.2, 3.8, 3.9, 3.10**
# Feature: migration-redesign, Property 3: Dry-run source intake is deterministic,
# bounded, and non-mutating
@settings(max_examples=32, deadline=None)
@given(source_files=_BOUNDED_SOURCE_TREE)
def test_generated_dry_runs_are_deterministic_bounded_and_non_mutating(
    source_files: dict[str, bytes],
) -> None:
    """Equivalent bounded trees produce equal reports and never change destinations."""
    with tempfile.TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_a = tmp_path / "source-a"
        source_b = tmp_path / "source-b"
        destination_a = tmp_path / "destination-a"
        destination_b = tmp_path / "destination-b"
        for destination in (destination_a, destination_b):
            destination.mkdir()
            (destination / "keep.txt").write_bytes(b"pre-existing destination data")

        _write_source_tree(source_a, source_files)
        _write_source_tree(source_b, source_files, reverse=True)
        before_a = _tree_state(destination_a)
        before_b = _tree_state(destination_b)

        report_a = plan_source_intake(
            source_a,
            _snapshot(),
            destination_root=destination_a,
            destination_prefix="incoming",
            license_status="reviewed",
        )
        report_b = plan_source_intake(
            source_b,
            _snapshot(),
            destination_root=destination_b,
            destination_prefix="incoming",
            license_status="reviewed",
        )

        assert len(source_files) <= _MAX_GENERATED_FILES
        assert report_a.total_bytes <= _MAX_GENERATED_FILES * _MAX_GENERATED_BYTES
        assert report_a.result is MigrationResult.PASS
        assert report_a.findings == ()
        assert report_a.snapshot.recorded_at == _RECORDED_AT
        assert report_a.canonical_json() == report_b.canonical_json()
        assert report_a.digest() == report_b.digest()
        _assert_complete_metadata(report_a, source_files, destination_prefix="incoming")
        _assert_complete_metadata(report_b, source_files, destination_prefix="incoming")
        assert _tree_state(destination_a) == before_a
        assert _tree_state(destination_b) == before_b


def test_explicit_passing_fixture_has_complete_metadata_and_no_mutation(tmp_path: Path) -> None:
    """A small reviewed text fixture passes with stable metadata and no writes."""
    source = tmp_path / "source"
    destination = tmp_path / "pack" / "corpus"
    files = {
        "docs/guide.md": b"local guide\n",
        "notes/review.txt": b"reviewed reference\n",
    }
    _write_source_tree(source, files)
    destination.mkdir(parents=True)
    (destination / "keep.txt").write_bytes(b"unchanged")
    before = _tree_state(destination)

    report = plan_source_intake(
        source,
        _snapshot(),
        destination_root=destination,
        destination_prefix="reference",
        license_status="reviewed",
    )

    assert report.result is MigrationResult.PASS
    assert report.findings == ()
    _assert_complete_metadata(report, files, destination_prefix="reference")
    assert _tree_state(destination) == before


def test_explicit_failing_fixture_is_machine_readable_non_zero_in_cli_and_non_mutating(
    tmp_path: Path,
) -> None:
    """Secret/collision input fails closed and the CLI emits a non-zero JSON result."""
    source = tmp_path / "source"
    destination = tmp_path / "pack" / "corpus"
    _write_source_tree(
        source,
        {
            "guide.md": b"guide",
            "notes.md": b"api_key=not-a-real-secret",
        },
    )
    destination.mkdir(parents=True)
    (destination / "guide.md").write_bytes(b"old destination")
    before = _tree_state(destination)

    report = plan_source_intake(
        source,
        _snapshot(),
        destination_root=destination,
        license_status=None,
    )
    report_data = json.loads(report.canonical_json())

    assert report.result is MigrationResult.FAIL
    assert {finding.code for finding in report.findings} >= {
        "destination_collision",
        "license_provenance_gap",
        "prohibited_material",
        "secret",
    }
    assert report_data["result"] == "fail"
    assert isinstance(report_data["findings"], list)
    assert "not-a-real-secret" not in report.canonical_json()
    assert _tree_state(destination) == before

    completed = subprocess.run(
        [
            sys.executable,
            str(_IMPORT_CLI),
            "--source-root",
            str(source),
            "--source-repository",
            "https://example.invalid/video",
            "--source-commit",
            "fixture-commit-1",
            "--recorded-at",
            _RECORDED_AT.isoformat(),
            "--project-root",
            str(tmp_path),
            "--destination-root",
            str(destination),
            "--license-status",
            "reviewed",
        ],
        cwd=_REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    cli_data = json.loads(completed.stdout)
    assert completed.returncode != 0
    assert cli_data["mode"] == "dry_run"
    assert cli_data["result"] == "fail"
    assert isinstance(cli_data["findings"], list)
    assert _tree_state(destination) == before


def _forbid_external_capability(*args: object, **kwargs: object) -> NoReturn:
    del args, kwargs
    raise AssertionError("dry-run attempted an external capability")


def test_dry_run_remains_local_when_network_and_process_calls_are_disabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The planner completes using only supplied local files and typed contracts."""
    monkeypatch.setattr(socket, "create_connection", _forbid_external_capability)
    monkeypatch.setattr(urllib.request, "urlopen", _forbid_external_capability)
    monkeypatch.setattr(subprocess, "run", _forbid_external_capability)

    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_source_tree(source, {"guide.md": b"offline guide"})

    report = plan_source_intake(
        source,
        _snapshot(),
        destination_root=destination,
        license_status="reviewed",
    )

    assert report.result is MigrationResult.PASS
    assert report.included[0].source_path == "guide.md"
    assert not destination.exists()
