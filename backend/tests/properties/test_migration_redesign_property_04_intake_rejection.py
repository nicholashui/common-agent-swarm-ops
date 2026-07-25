"""Property checks for fail-closed, non-mutating corpus intake rejection."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

import pytest
from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import MigrationResult, SourceSnapshot
from app.video.migration.intake import plan_source_intake

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_IMPORT_CLI: Final[Path] = _REPOSITORY_ROOT / "scripts" / "business" / "import_video_corpus.py"
_RECORDED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
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
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=48,
).map(str.encode)
_UNSAFE_SOURCE_PATHS = st.sampled_from(
    (
        "../outside.md",
        "nested/../../outside.md",
        "/outside.md",
        "C:/outside.md",
        r"C:\outside.md",
    )
)
_SECRET_TOKEN = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),
    min_size=4,
    max_size=16,
)


class _ProhibitedCase(tuple[str, str, bytes, frozenset[str]]):
    """Typed tuple describing one bounded prohibited or secret fixture."""

    __slots__ = ()

    def __new__(
        cls,
        kind: str,
        relative_path: str,
        content: bytes,
        expected_codes: frozenset[str],
    ) -> _ProhibitedCase:
        return tuple.__new__(cls, (kind, relative_path, content, expected_codes))

    @property
    def kind(self) -> str:
        return self[0]

    @property
    def relative_path(self) -> str:
        return self[1]

    @property
    def content(self) -> bytes:
        return self[2]

    @property
    def expected_codes(self) -> frozenset[str]:
        return self[3]


@st.composite
def _prohibited_cases(draw: st.DrawFn) -> _ProhibitedCase:
    """Generate bounded source material classified as prohibited or secret."""
    kind = draw(st.sampled_from(("cache", "log", "secret_path", "secret_content", "binary")))
    if kind == "cache":
        return _ProhibitedCase(
            kind,
            ".cache/fixture.md",
            b"cache output",
            frozenset({"prohibited_material"}),
        )
    if kind == "log":
        return _ProhibitedCase(
            kind,
            "logs/debug.log",
            b"diagnostic output",
            frozenset({"prohibited_material"}),
        )
    if kind == "secret_path":
        return _ProhibitedCase(
            kind,
            "secrets/token.txt",
            b"untrusted secret reference",
            frozenset({"prohibited_material"}),
        )
    if kind == "secret_content":
        token = draw(_SECRET_TOKEN)
        return _ProhibitedCase(
            kind,
            "notes.md",
            f"api_key={token}".encode("ascii"),
            frozenset({"prohibited_material", "secret"}),
        )
    return _ProhibitedCase(
        kind,
        "render.bin",
        b"\x00generated binary content",
        frozenset({"prohibited_material"}),
    )


def _snapshot(source_root: Path) -> SourceSnapshot:
    """Return a fixed local snapshot for deterministic property fixtures."""
    return SourceSnapshot(
        source_repository="https://example.invalid/video",
        source_commit="fixture-commit-1",
        source_root=str(source_root),
        recorded_at=_RECORDED_AT,
    )


def _write_source_file(source_root: Path, relative_path: str, content: bytes) -> None:
    """Create one fixture file beneath the local source root."""
    path = source_root.joinpath(*relative_path.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _prepare_pack(pack_root: Path) -> Path:
    """Create an existing pack tree whose digest must survive rejected intake."""
    (pack_root / "README.md").parent.mkdir(parents=True, exist_ok=True)
    (pack_root / "README.md").write_bytes(b"preexisting local pack\n")
    (pack_root / "manifest.json").write_bytes(b'{"pack":"video"}\n')
    corpus_root = pack_root / "corpus"
    (corpus_root / "existing").mkdir(parents=True, exist_ok=True)
    (corpus_root / "existing" / "reference.md").write_bytes(b"do not replace\n")
    return corpus_root


def _tree_digest(root: Path) -> str:
    """Digest every preexisting pack file by canonical relative path and bytes."""
    digest = hashlib.sha256()
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda candidate: candidate.relative_to(root).as_posix(),
    ):
        relative_path = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative_path).to_bytes(4, "big"))
        digest.update(relative_path)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


# **Validates: Requirements 3.4, 3.5, 3.6, 3.7**
# Feature: migration-redesign, Property 4: Unsafe, prohibited, or colliding
# imports fail before pack mutation.
@settings(max_examples=24, deadline=None, derandomize=True)
@example("../outside.md")
@example("/outside.md")
@example(r"C:\outside.md")
@given(unsafe_path=_UNSAFE_SOURCE_PATHS)
def test_unsafe_source_paths_fail_before_pack_mutation(unsafe_path: str) -> None:
    """Absolute and traversal allow-list paths fail closed without a write."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        _write_source_file(source_root, "guide.md", b"safe local reference")
        pack_root = tmp_path / "business" / "video"
        destination_root = _prepare_pack(pack_root)
        before_digest = _tree_digest(pack_root)

        report = plan_source_intake(
            source_root,
            _snapshot(source_root),
            destination_root=destination_root,
            allow_paths=(unsafe_path,),
            license_status="reviewed",
        )

        assert report.result is MigrationResult.FAIL
        assert "unsafe_path" in {finding.code for finding in report.findings}
        assert report.included == ()
        assert _tree_digest(pack_root) == before_digest


@settings(max_examples=24, deadline=None, derandomize=True)
@example("../outside.md")
@example("/outside.md")
@given(unsafe_path=_UNSAFE_SOURCE_PATHS)
def test_unsafe_destination_paths_fail_before_pack_mutation(unsafe_path: str) -> None:
    """A mapper cannot redirect a candidate to an absolute or traversal path."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        _write_source_file(source_root, "guide.md", b"safe local reference")
        pack_root = tmp_path / "business" / "video"
        destination_root = _prepare_pack(pack_root)
        before_digest = _tree_digest(pack_root)

        report = plan_source_intake(
            source_root,
            _snapshot(source_root),
            destination_root=destination_root,
            destination_mapper=lambda _source_path: unsafe_path,
            license_status="reviewed",
        )

        assert report.result is MigrationResult.FAIL
        assert "unsafe_destination_path" in {finding.code for finding in report.findings}
        assert _tree_digest(pack_root) == before_digest


# **Validates: Requirements 3.4, 3.5, 3.6, 3.7**
@settings(max_examples=24, deadline=None, derandomize=True)
@given(case=_prohibited_cases())
def test_prohibited_or_secret_material_fails_before_pack_mutation(
    case: _ProhibitedCase,
) -> None:
    """Caches, logs, binaries, secret paths, and secret bytes are never admitted."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        _write_source_file(source_root, case.relative_path, case.content)
        pack_root = tmp_path / "business" / "video"
        destination_root = _prepare_pack(pack_root)
        before_digest = _tree_digest(pack_root)

        report = plan_source_intake(
            source_root,
            _snapshot(source_root),
            destination_root=destination_root,
            license_status="reviewed",
        )
        finding_codes = {finding.code for finding in report.findings}

        assert report.result is MigrationResult.FAIL
        assert case.expected_codes <= finding_codes
        assert report.included == ()
        assert _tree_digest(pack_root) == before_digest


@settings(max_examples=24, deadline=None, derandomize=True)
@given(relative_path=_SAFE_SOURCE_PATH, content=_SAFE_CONTENT)
def test_existing_destination_collision_fails_before_pack_mutation(
    relative_path: str, content: bytes
) -> None:
    """A preexisting destination file is an undeclared collision, not a replacement."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        source_root = tmp_path / "source"
        _write_source_file(source_root, relative_path, content)
        pack_root = tmp_path / "business" / "video"
        destination_root = _prepare_pack(pack_root)
        existing_destination = destination_root / "incoming" / relative_path
        existing_destination.parent.mkdir(parents=True, exist_ok=True)
        existing_destination.write_bytes(b"preexisting destination")
        before_digest = _tree_digest(pack_root)

        report = plan_source_intake(
            source_root,
            _snapshot(source_root),
            destination_root=destination_root,
            destination_prefix="incoming",
            license_status="reviewed",
        )

        assert report.result is MigrationResult.FAIL
        assert "destination_collision" in {finding.code for finding in report.findings}
        assert _tree_digest(pack_root) == before_digest


def test_escaping_source_link_fails_before_pack_mutation(tmp_path: Path) -> None:
    """A source symlink escaping the source root is rejected without reading its target."""
    source_root = tmp_path / "source"
    source_root.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_bytes(b"api_key=must-not-be-read")
    escaping_link = source_root / "escape.md"
    try:
        escaping_link.symlink_to(outside)
    except OSError:
        pytest.skip("Symlink creation is unavailable in this environment.")

    pack_root = tmp_path / "business" / "video"
    destination_root = _prepare_pack(pack_root)
    before_digest = _tree_digest(pack_root)

    report = plan_source_intake(
        source_root,
        _snapshot(source_root),
        destination_root=destination_root,
        license_status="reviewed",
    )
    finding_codes = {finding.code for finding in report.findings}

    assert report.result is MigrationResult.FAIL
    assert "unsafe_path" in finding_codes
    assert "secret" not in finding_codes
    assert _tree_digest(pack_root) == before_digest


def test_rejected_cli_returns_nonzero_json_and_preserves_pack_digest(tmp_path: Path) -> None:
    """The command seam reports rejection with machine-readable output and no writes."""
    source_root = tmp_path / "source"
    _write_source_file(source_root, "guide.md", b"new guide")
    _write_source_file(source_root, "notes.md", b"api_key=not-a-real-secret")
    pack_root = tmp_path / "business" / "video"
    destination_root = _prepare_pack(pack_root)
    (destination_root / "guide.md").write_bytes(b"old guide")
    before_digest = _tree_digest(pack_root)

    completed = subprocess.run(
        [
            sys.executable,
            str(_IMPORT_CLI),
            "--source-root",
            str(source_root),
            "--source-repository",
            "https://example.invalid/video",
            "--source-commit",
            "fixture-commit-1",
            "--recorded-at",
            _RECORDED_AT.isoformat(),
            "--project-root",
            str(tmp_path),
            "--destination-root",
            str(destination_root),
            "--license-status",
            "reviewed",
        ],
        cwd=_REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    report = json.loads(completed.stdout)
    assert completed.returncode != 0
    assert report["result"] == "fail"
    assert {finding["code"] for finding in report["findings"]} >= {
        "destination_collision",
        "prohibited_material",
        "secret",
    }
    assert _tree_digest(pack_root) == before_digest
