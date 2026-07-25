"""Property checks for truthful, isolated Video Pack documentation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import MigrationResult
from app.video.migration.documentation import (
    check_documentation_integrity,
    collect_local_asset_snapshot,
    write_local_documentation,
)

_ASSET_KINDS: tuple[str, ...] = (
    "agents",
    "workflows",
    "corpus",
    "special_skills",
    "knowledge",
    "schemas",
    "policies",
)
_MUTATION_KINDS: tuple[str, ...] = (
    "missing_asset",
    "count_mismatch",
    "ownership_mismatch",
)


@dataclass(frozen=True, slots=True)
class LocalAssetCounts:
    """Small generated local asset inventory used to render truthful claims."""

    agents: int
    workflows: int
    special_skills: int
    corpus: int
    knowledge: int
    schemas: int
    policies: int

    def as_dict(self) -> dict[str, int]:
        """Return the count keys consumed by documentation claims."""
        return {
            "agents": self.agents,
            "workflows": self.workflows,
            "special_skills": self.special_skills,
            "corpus": self.corpus,
            "knowledge": self.knowledge,
            "schemas": self.schemas,
            "policies": self.policies,
        }


@st.composite
def _local_asset_counts(draw: st.DrawFn) -> LocalAssetCounts:
    """Generate bounded local asset counts without creating a large fixture."""
    return LocalAssetCounts(
        agents=draw(st.integers(min_value=0, max_value=3)),
        workflows=draw(st.integers(min_value=0, max_value=3)),
        special_skills=draw(st.integers(min_value=0, max_value=2)),
        corpus=draw(st.integers(min_value=0, max_value=3)),
        knowledge=draw(st.integers(min_value=0, max_value=3)),
        schemas=draw(st.integers(min_value=0, max_value=2)),
        policies=draw(st.integers(min_value=0, max_value=2)),
    )


@dataclass(frozen=True, slots=True)
class DocumentationMutation:
    """One bounded mutation applied to otherwise generated truthful docs."""

    kind: str
    asset_kind: str = "agents"
    asset_index: int = 1


@st.composite
def _documentation_mutations(draw: st.DrawFn) -> DocumentationMutation:
    """Generate absent-asset, count, and ownership documentation mutations."""
    kind = draw(st.sampled_from(_MUTATION_KINDS))
    asset_kind = draw(st.sampled_from(_ASSET_KINDS)) if kind == "missing_asset" else "agents"
    return DocumentationMutation(
        kind=kind,
        asset_kind=asset_kind,
        asset_index=draw(st.integers(min_value=1, max_value=99)),
    )


def _write_text(path: Path, value: str) -> None:
    """Write one deterministic local fixture file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def _materialize_local_assets(root: Path, counts: LocalAssetCounts) -> Path:
    """Create a bounded local Video Pack whose counts are independently observable."""
    video_root = root / "business" / "video"
    (video_root / "agents").mkdir(parents=True)
    for index in range(counts.agents):
        agent_dir = video_root / "agents" / f"video.property_15_agent_{index}"
        agent_dir.mkdir()
        _write_text(agent_dir / "agent_spec.json", "{}\n")

    for directory_name, count, suffix in (
        ("workflows", counts.workflows, ".dna.json"),
        ("corpus", counts.corpus, ".md"),
        ("knowledge", counts.knowledge, ".md"),
        ("schemas", counts.schemas, ".json"),
        ("policies", counts.policies, ".json"),
    ):
        for index in range(count):
            _write_text(
                video_root / directory_name / f"property-15-{index}{suffix}",
                "local fixture\n",
            )

    for index in range(counts.special_skills):
        (video_root / "special_skills" / f"property-15-skill-{index}").mkdir(parents=True)
    return video_root


def _file_snapshot(root: Path) -> tuple[tuple[str, bytes], ...]:
    """Capture local files so a documentation check can be proven read-only."""
    return tuple(
        sorted(
            (
                path.relative_to(root).as_posix(),
                path.read_bytes(),
            )
            for path in root.rglob("*")
            if path.is_file()
        )
    )


def _missing_asset_claim(mutation: DocumentationMutation) -> str:
    """Return a safe local-looking path that is absent from the generated pack."""
    token = f"missing-property-15-{mutation.asset_index}"
    if mutation.asset_kind == "agents":
        return f"business/video/agents/video.property_15_absent_{mutation.asset_index}/SPEC.md"
    suffix = ".dna.json" if mutation.asset_kind == "workflows" else ".md"
    return f"business/video/{mutation.asset_kind}/{token}{suffix}"


def _apply_mutation(
    root: Path,
    video_root: Path,
    counts: LocalAssetCounts,
    mutation: DocumentationMutation,
) -> None:
    """Apply exactly one generated documentation-integrity failure."""
    if mutation.kind == "missing_asset":
        readme = video_root / "README.md"
        _write_text(
            readme,
            readme.read_text(encoding="utf-8")
            + f"\nDocumented local asset: `{_missing_asset_claim(mutation)}`.\n",
        )
        return
    if mutation.kind == "count_mismatch":
        structure = root / "structure.md"
        _write_text(
            structure,
            structure.read_text(encoding="utf-8") + f"\nAgents: {counts.agents + 1}\n",
        )
        return
    if mutation.kind == "ownership_mismatch":
        adoption = root / "adoption.md"
        _write_text(
            adoption,
            adoption.read_text(encoding="utf-8")
            + "\nva-agent-swarm remains the canonical repository.\n",
        )
        return
    raise AssertionError(f"Unhandled documentation mutation: {mutation.kind}")


# Feature: migration-redesign, Property 15: Documentation is truthful but
# operationally isolated.
# **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.9**
@settings(max_examples=24, deadline=None, derandomize=True)
@example(LocalAssetCounts(0, 0, 0, 0, 0, 0, 0))
@example(LocalAssetCounts(2, 1, 1, 2, 1, 1, 1))
@given(counts=_local_asset_counts())
def test_property_15_generated_local_claims_counts_and_ownership_are_truthful(
    counts: LocalAssetCounts,
) -> None:
    """Documentation rendered from local assets passes its integrity gate."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        video_root = _materialize_local_assets(tmp_path, counts)

        report = write_local_documentation(tmp_path, video_root=video_root)
        repeat = check_documentation_integrity(tmp_path, video_root=video_root)

        assert report.result is MigrationResult.PASS
        assert report.is_valid
        assert report.findings == ()
        assert report.assets.counts == counts.as_dict()
        assert report.completion_gate_passed
        assert report.allows_unrelated_operations
        assert all(
            claim["kind"] != "count" or claim["expected"] == claim["actual"]
            for claim in report.claims
        )
        assert report.canonical_json() == repeat.canonical_json()


# **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.9**
@settings(max_examples=24, deadline=None, derandomize=True)
@example(DocumentationMutation("missing_asset", "corpus", 1))
@example(DocumentationMutation("count_mismatch"))
@example(DocumentationMutation("ownership_mismatch"))
@given(mutation=_documentation_mutations())
def test_property_15_documentation_mutations_are_deterministic_non_blocking_and_gate_failing(
    mutation: DocumentationMutation,
) -> None:
    """Absent claims fail completion without mutating or blocking unrelated checks."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        counts = LocalAssetCounts(1, 1, 1, 1, 1, 1, 1)
        video_root = _materialize_local_assets(tmp_path, counts)
        initial = write_local_documentation(tmp_path, video_root=video_root)
        assert initial.is_valid
        _apply_mutation(tmp_path, video_root, counts, mutation)
        before_check = _file_snapshot(tmp_path)

        report = check_documentation_integrity(tmp_path, video_root=video_root)
        repeat = check_documentation_integrity(tmp_path, video_root=video_root)

        expected_code = {
            "missing_asset": "documentation_asset_missing",
            "count_mismatch": "documentation_count_mismatch",
            "ownership_mismatch": "documentation_ownership_mismatch",
        }[mutation.kind]
        assert report.result is MigrationResult.FAIL
        assert expected_code in {finding.code for finding in report.findings}
        assert not report.completion_gate_passed
        assert report.allows_unrelated_operations
        assert report.findings
        assert all(not finding.blocks_unrelated_operations for finding in report.findings)
        assert collect_local_asset_snapshot(video_root, repository_root=tmp_path) == report.assets
        assert report.canonical_json() == repeat.canonical_json()
        assert _file_snapshot(tmp_path) == before_check
