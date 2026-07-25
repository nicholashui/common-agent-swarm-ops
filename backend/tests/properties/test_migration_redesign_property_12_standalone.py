"""Property checks for isolated, deterministic standalone verification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

import pytest
from hypothesis import example, given, settings, strategies as st

from app.video.inventory import InventoryIssue, VideoInventoryReport
from app.video.migration import standalone as standalone_module
from app.video.migration.agent_mapping import (
    AgentMappingIssue,
    AgentMappingReport,
    ProjectionValidationReport,
)
from app.video.migration.contracts import ImportFinding, MigrationResult
from app.video.migration.corpus import CorpusIntegrityReport
from app.video.migration.operational_assets import AssetValidationReport
from app.video.migration.specifications import SpecificationIssue, SpecificationReport
from app.video.migration.standalone import (
    DEFAULT_UPSTREAM_REPOSITORIES,
    verify_standalone,
)

_UPSTREAMS: Final[tuple[str, ...]] = DEFAULT_UPSTREAM_REPOSITORIES
_LOCAL_CHECK_NAMES: Final[tuple[str, ...]] = (
    "corpus_integrity",
    "common_inventory_manifest",
    "agent_source_map",
    "agent_id_agreement",
    "required_local_references",
    "specifications",
    "operational_assets",
    "safe_baseline_workflow",
    "safe_registration_paths",
)


@dataclass(frozen=True, slots=True)
class FailingPreconditions:
    """One bounded isolation declaration that must stop before content validation."""

    network_disabled: bool
    upstreams_unavailable: bool
    upstream_available: bool


@st.composite
def _failing_preconditions(draw: st.DrawFn) -> FailingPreconditions:
    """Generate every useful unsatisfied network/upstream precondition shape."""
    network_disabled = draw(st.booleans())
    upstreams_unavailable = draw(st.booleans())
    upstream_available = draw(st.booleans())
    if network_disabled and upstreams_unavailable and not upstream_available:
        upstream_available = True
    return FailingPreconditions(
        network_disabled=network_disabled,
        upstreams_unavailable=upstreams_unavailable,
        upstream_available=upstream_available,
    )


@dataclass(frozen=True, slots=True)
class LocalValidatorOutcomes:
    """Bounded pass/fail outcomes for the local standalone checks."""

    corpus_integrity: bool
    common_inventory_manifest: bool
    agent_source_map: bool
    agent_id_agreement: bool
    required_local_references: bool
    specifications: bool
    operational_assets: bool
    safe_baseline_workflow: bool
    safe_registration_paths: bool

    def as_items(self) -> tuple[tuple[str, bool], ...]:
        """Return outcomes paired with the verifier's check names."""
        return tuple(
            zip(
                _LOCAL_CHECK_NAMES,
                (
                    self.corpus_integrity,
                    self.common_inventory_manifest,
                    self.agent_source_map,
                    self.agent_id_agreement,
                    self.required_local_references,
                    self.specifications,
                    self.operational_assets,
                    self.safe_baseline_workflow,
                    self.safe_registration_paths,
                ),
                strict=True,
            )
        )


@st.composite
def _local_validator_outcomes(draw: st.DrawFn) -> LocalValidatorOutcomes:
    """Generate a finite vector covering every local validator boundary."""
    return LocalValidatorOutcomes(
        corpus_integrity=draw(st.booleans()),
        common_inventory_manifest=draw(st.booleans()),
        agent_source_map=draw(st.booleans()),
        agent_id_agreement=draw(st.booleans()),
        required_local_references=draw(st.booleans()),
        specifications=draw(st.booleans()),
        operational_assets=draw(st.booleans()),
        safe_baseline_workflow=draw(st.booleans()),
        safe_registration_paths=draw(st.booleans()),
    )


def _finding(check_name: str) -> ImportFinding:
    """Return a stable synthetic diagnostic for one generated local failure."""
    return ImportFinding(
        code=f"property_12_{check_name}_failure",
        field=check_name,
        message="Generated local validator failure.",
    )


def _findings_for(check_name: str, passed: bool) -> tuple[ImportFinding, ...]:
    """Project a generated boolean onto the real migration finding contract."""
    return () if passed else (_finding(check_name),)


def _result(passed: bool) -> MigrationResult:
    """Convert a generated validator outcome to the canonical migration result."""
    return MigrationResult.PASS if passed else MigrationResult.FAIL


def _install_local_validator_outcomes(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: LocalValidatorOutcomes,
) -> None:
    """Replace validator seams with generated outcomes while retaining real aggregation."""
    corpus_report = CorpusIntegrityReport(
        result=_result(outcomes.corpus_integrity),
        findings=_findings_for("corpus_integrity", outcomes.corpus_integrity),
    )
    monkeypatch.setattr(
        standalone_module,
        "validate_corpus_integrity",
        lambda _root: corpus_report,
    )

    inventory_issues = (
        (
            InventoryIssue(
                code="property_12_common_inventory_manifest_failure",
                message="Generated local validator failure.",
                field="common_inventory_manifest",
            ),
        )
        if not outcomes.common_inventory_manifest
        else ()
    )
    inventory_report = VideoInventoryReport(
        is_valid=outcomes.common_inventory_manifest,
        manifest_agent_ids=(),
        inventory_agent_ids=(),
        agent_spec_ids=(),
        issues=inventory_issues,
    )
    monkeypatch.setattr(
        standalone_module.VideoInventoryValidator,
        "validate",
        lambda _validator, *_args, **_kwargs: inventory_report,
    )

    mapping_issues = (
        (
            AgentMappingIssue(
                code="property_12_agent_source_map_failure",
                field="agent_source_map",
                message="Generated local validator failure.",
            ),
        )
        if not outcomes.agent_source_map
        else ()
    )
    mapping_report = AgentMappingReport(
        is_valid=outcomes.agent_source_map,
        inventory_agent_ids=(),
        map_agent_ids=(),
        entries=(),
        issues=mapping_issues,
    )
    monkeypatch.setattr(
        standalone_module.AgentSourceMapValidator,
        "validate",
        lambda _validator, *_args, **_kwargs: mapping_report,
    )
    monkeypatch.setattr(
        standalone_module,
        "validate_projection_files",
        lambda *_args, **_kwargs: ProjectionValidationReport(is_valid=True),
    )
    monkeypatch.setattr(
        standalone_module,
        "validate_roster_projection",
        lambda *_args, **_kwargs: ProjectionValidationReport(is_valid=True),
    )

    monkeypatch.setattr(
        standalone_module,
        "_ids_agreement_findings",
        lambda *_args, **_kwargs: _findings_for("agent_id_agreement", outcomes.agent_id_agreement),
    )
    monkeypatch.setattr(
        standalone_module,
        "_required_reference_findings",
        lambda *_args, **_kwargs: _findings_for(
            "required_local_references", outcomes.required_local_references
        ),
    )

    specification_issues = (
        (
            SpecificationIssue(
                code="property_12_specifications_failure",
                agent_id="video.property_12_agent",
                field="specifications",
                message="Generated local validator failure.",
            ),
        )
        if not outcomes.specifications
        else ()
    )
    specification_report = SpecificationReport(
        is_valid=outcomes.specifications,
        result=_result(outcomes.specifications),
        inventory_agent_ids=(),
        issues=specification_issues,
    )
    monkeypatch.setattr(
        standalone_module,
        "validate_specifications",
        lambda *_args, **_kwargs: specification_report,
    )

    def asset_report(check_name: str, passed: bool) -> AssetValidationReport:
        return AssetValidationReport(
            result=_result(passed),
            findings=_findings_for(check_name, passed),
        )

    monkeypatch.setattr(
        standalone_module.OperationalAssetValidator,
        "validate_knowledge_seeds",
        lambda _validator, *_args, **_kwargs: asset_report(
            "operational_assets", outcomes.operational_assets
        ),
    )
    monkeypatch.setattr(
        standalone_module.OperationalAssetValidator,
        "validate_special_skills",
        lambda _validator, *_args, **_kwargs: asset_report(
            "operational_assets", outcomes.operational_assets
        ),
    )
    monkeypatch.setattr(
        standalone_module,
        "_workflow_definition_findings",
        lambda *_args, **_kwargs: _findings_for(
            "safe_baseline_workflow", outcomes.safe_baseline_workflow
        ),
    )
    monkeypatch.setattr(
        standalone_module,
        "_safe_registration_findings",
        lambda *_args, **_kwargs: _findings_for(
            "safe_registration_paths", outcomes.safe_registration_paths
        ),
    )

    def read_json(
        _path: Path,
        _findings: list[ImportFinding],
        _field: str,
    ) -> object:
        return {}

    monkeypatch.setattr(standalone_module, "_read_json", read_json)
    monkeypatch.setattr(
        standalone_module,
        "_load_agent_specs",
        lambda *_args, **_kwargs: ({}, ()),
    )
    monkeypatch.setattr(
        standalone_module,
        "_load_workflows",
        lambda *_args, **_kwargs: ({}, ()),
    )
    monkeypatch.setattr(
        standalone_module,
        "_load_process_index",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        standalone_module,
        "_load_operational_records",
        lambda *_args, **_kwargs: {"entries": []},
    )


# **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9,
# 8.10, 8.11, 8.12, 8.13**
# Feature: migration-redesign, Property 12: Standalone verification checks its
# isolation preconditions first.
@settings(max_examples=32, deadline=None, derandomize=True)
@example(FailingPreconditions(False, True, False))
@example(FailingPreconditions(True, False, False))
@example(FailingPreconditions(True, True, True))
@given(case=_failing_preconditions())
def test_property_12_isolation_preconditions_short_circuit_before_content_validation(
    case: FailingPreconditions,
) -> None:
    """Every unsatisfied isolation declaration fails before a local validator runs."""
    with TemporaryDirectory() as temporary_root, pytest.MonkeyPatch.context() as monkeypatch:
        tmp_path = Path(temporary_root)
        called = False

        def fail_if_called(_root: Path) -> object:
            nonlocal called
            called = True
            raise AssertionError("content validation must not run")

        monkeypatch.setattr(standalone_module, "validate_corpus_integrity", fail_if_called)
        report = verify_standalone(
            tmp_path / "business" / "video",
            network_disabled=case.network_disabled,
            upstreams_unavailable=case.upstreams_unavailable,
            upstream_available=_UPSTREAMS if case.upstream_available else (),
        )

        assert not report.is_valid
        assert not report.content_validation_started
        assert not called
        expected_codes = set()
        if not case.network_disabled:
            expected_codes.add("standalone_network_enabled")
        if not case.upstreams_unavailable or case.upstream_available:
            expected_codes.add("standalone_upstream_available")
        assert {finding.code for finding in report.findings} == expected_codes
        assert (
            report.canonical_json()
            == verify_standalone(
                tmp_path / "business" / "video",
                network_disabled=case.network_disabled,
                upstreams_unavailable=case.upstreams_unavailable,
                upstream_available=_UPSTREAMS if case.upstream_available else (),
            ).canonical_json()
        )


@settings(max_examples=32, deadline=None, derandomize=True)
@example(LocalValidatorOutcomes(True, True, True, True, True, True, True, True, True))
@example(LocalValidatorOutcomes(False, True, True, True, True, True, True, True, True))
@example(LocalValidatorOutcomes(True, True, False, True, True, True, True, True, True))
@example(LocalValidatorOutcomes(True, True, True, True, True, True, False, True, True))
@example(LocalValidatorOutcomes(False, False, False, False, False, False, False, False, False))
@given(outcomes=_local_validator_outcomes())
def test_property_12_isolated_runs_aggregate_every_local_validator_deterministically(
    outcomes: LocalValidatorOutcomes,
) -> None:
    """An isolated run reports PASS exactly when every local validator passes."""
    with TemporaryDirectory() as temporary_root, pytest.MonkeyPatch.context() as monkeypatch:
        tmp_path = Path(temporary_root)
        video_root = tmp_path / "business" / "video"
        (video_root / "workflows").mkdir(parents=True)
        (video_root / "workflows" / "pack_spine.json").write_text("{}\n", encoding="utf-8")
        _install_local_validator_outcomes(monkeypatch, outcomes)

        report = verify_standalone(
            video_root,
            repository_root=tmp_path,
            network_disabled=True,
            upstreams_unavailable=True,
        )

        expected_failures = {check_name for check_name, passed in outcomes.as_items() if not passed}
        actual_failures = {
            check.name for check in report.checks if check.result is MigrationResult.FAIL
        }
        assert actual_failures == expected_failures
        assert report.content_validation_started
        assert report.is_success == (not expected_failures)
        assert report.result is (
            MigrationResult.PASS if not expected_failures else MigrationResult.FAIL
        )
        assert tuple(check.name for check in report.checks) == tuple(
            sorted(("local_inputs", *_LOCAL_CHECK_NAMES))
        )
        assert tuple(report.findings) == tuple(
            sorted(report.findings, key=lambda finding: finding.to_dict()["code"])
        )
        assert (
            report.canonical_json()
            == verify_standalone(
                video_root,
                repository_root=tmp_path,
                network_disabled=True,
                upstreams_unavailable=True,
            ).canonical_json()
        )

        if not expected_failures:
            assert report.to_dict()["result"] == MigrationResult.PASS.value
            assert report.findings == ()
