"""Property checks for safety-critical local specification review gates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import (
    AgentSourceMapEntry,
    AgentSpecificationReview,
    MappingStatus,
)
from app.video.migration.specifications import (
    SpecificationIssue,
    build_specification_document,
    validate_specification_document,
)

_REVIEWED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_REVIEWER: Final[str] = "critical-specification-reviewer-property-10"
_PROPERTY_AGENT_ID: Final[str] = "video.property_10_agent"
_CRITICAL_ROLE_NAMES: Final[tuple[str, ...]] = (
    "orchestrator",
    "compliance",
    "rights and consent",
    "privacy",
    "legal",
    "safety",
    "provenance",
    "release",
    "judge",
    "human review coordinator",
)
_NONCRITICAL_ROLE_NAMES: Final[tuple[str, ...]] = (
    "editor",
    "storyboard artist",
    "caption specialist",
    "audio designer",
    "colorist",
)


@dataclass(frozen=True, slots=True)
class RoleClassification:
    """A generated runtime role and its expected critical-review classification."""

    role: str
    is_critical: bool


@st.composite
def _role_classifications(draw: st.DrawFn) -> RoleClassification:
    """Generate critical and noncritical runtime role classifications."""
    is_critical = draw(st.booleans())
    role_names = _CRITICAL_ROLE_NAMES if is_critical else _NONCRITICAL_ROLE_NAMES
    return RoleClassification(role=draw(st.sampled_from(role_names)), is_critical=is_critical)


def _runtime_binding(role: str) -> dict[str, object]:
    """Return a complete, non-active runtime binding for one generated role."""
    return {
        "agent_id": _PROPERTY_AGENT_ID,
        "allowed_tools": [],
        "budget_policy": {
            "max_input_tokens": 2048,
            "max_output_tokens": 1024,
            "max_tool_requests": 0,
        },
        "critique_edges": {"inputs": [], "outputs": []},
        "max_refinement_count": 2,
        "model_policy": {
            "model_id": "local-video-property-10",
            "network_access": False,
            "provider": "local_deterministic",
        },
        "production_activation_requested": False,
        "prompt_reference": "video.prompt.property-10.v1",
        "role": role,
        "rubric_reference": "video.rubric.property-10.v1",
        "schema_version": "1.0",
        "status": "registered",
    }


def _mapping_entry() -> AgentSourceMapEntry:
    """Return a reviewed local mapping entry for the generated specification."""
    return AgentSourceMapEntry(
        common_agent_id=_PROPERTY_AGENT_ID,
        mapping_status=MappingStatus.COMMON_ONLY,
        source_agent_ids=(),
        source_documents=("mapping/property-10.md",),
        rationale="Human-reviewed local video responsibility for the property fixture.",
        reviewed_by=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
    )


def _prepare_fixture(root: Path, role: str) -> tuple[Path, Path, dict[str, object], str]:
    """Create local files required for generated singular SPEC validation."""
    repository_root = root / "repository"
    video_root = repository_root / "business" / "video"
    agent_dir = video_root / "agents" / _PROPERTY_AGENT_ID
    (video_root / "mapping").mkdir(parents=True)
    agent_dir.mkdir(parents=True)
    (video_root / "inventory.json").write_text("{}\n", encoding="utf-8")
    (video_root / "mapping" / "property-10.md").write_text(
        "Local property-test mapping document.\n", encoding="utf-8"
    )
    runtime_binding = _runtime_binding(role)
    (agent_dir / "agent_spec.json").write_text(
        json.dumps(runtime_binding, sort_keys=True), encoding="utf-8"
    )
    document = build_specification_document(
        _PROPERTY_AGENT_ID,
        runtime_binding,
        _mapping_entry(),
        inventory_entry={"status": "registered", "maturity_level": "L0"},
        pack_version="property-10",
    )
    return repository_root, video_root, runtime_binding, document


def _passing_review() -> AgentSpecificationReview:
    """Return a completed local review record accepted by the critical gate."""
    return AgentSpecificationReview(
        common_agent_id=_PROPERTY_AGENT_ID,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        scope="critical specification review",
        result="pass",
    )


def _replace_section(document: str, heading: str, replacement: str) -> str:
    """Replace one generated section body while preserving the document structure."""
    marker = f"## {heading}\n"
    section_start = document.index(marker) + len(marker)
    next_heading = document.find("\n## ", section_start)
    section_end = len(document) if next_heading == -1 else next_heading
    return document[:section_start] + replacement.strip() + "\n" + document[section_end:]


def _issue_codes(issues: tuple[SpecificationIssue, ...]) -> set[str]:
    """Project validator output to stable diagnostic codes."""
    return {issue.code for issue in issues}


# Feature: migration-redesign, Property 10: Safety-critical specifications require
# human review.
# **Validates: Requirements 6.5**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(RoleClassification("orchestrator", True))
@example(RoleClassification("compliance", True))
@example(RoleClassification("rights and consent", True))
@example(RoleClassification("privacy", True))
@example(RoleClassification("legal", True))
@example(RoleClassification("safety", True))
@example(RoleClassification("provenance", True))
@example(RoleClassification("release", True))
@example(RoleClassification("judge", True))
@example(RoleClassification("human review coordinator", True))
@example(RoleClassification("editor", False))
@given(classification=_role_classifications())
def test_property_10_generated_role_classifications_enforce_critical_review_gate(
    classification: RoleClassification,
) -> None:
    """Critical roles need a passing review; noncritical roles do not need this gate."""
    with TemporaryDirectory() as temporary_root:
        root = Path(temporary_root)
        repository_root, video_root, runtime_binding, document = _prepare_fixture(
            root, classification.role
        )
        spec_path = video_root / "agents" / _PROPERTY_AGENT_ID / "SPEC.md"

        without_review = validate_specification_document(
            document,
            _PROPERTY_AGENT_ID,
            runtime_binding,
            video_root=video_root,
            repository_root=repository_root,
            spec_path=spec_path,
            mapping_entry=_mapping_entry(),
        )
        without_review_codes = _issue_codes(without_review)

        if classification.is_critical:
            assert "missing_critical_review" in without_review_codes
            with_passing_review = validate_specification_document(
                document,
                _PROPERTY_AGENT_ID,
                runtime_binding,
                video_root=video_root,
                repository_root=repository_root,
                spec_path=spec_path,
                mapping_entry=_mapping_entry(),
                critical_review=_passing_review(),
            )
            assert with_passing_review == ()
        else:
            assert "missing_critical_review" not in without_review_codes
            assert without_review == ()

            basic_mutation = _replace_section(document, "Responsibility", "Video agent role.")
            with_review_but_invalid_basic_spec = validate_specification_document(
                basic_mutation,
                _PROPERTY_AGENT_ID,
                runtime_binding,
                video_root=video_root,
                repository_root=repository_root,
                spec_path=spec_path,
                mapping_entry=_mapping_entry(),
                critical_review=_passing_review(),
            )
            assert "generic_responsibility" in _issue_codes(with_review_but_invalid_basic_spec)
