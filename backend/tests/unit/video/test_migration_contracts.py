"""Focused tests for deterministic migration records and local path safety."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.video.migration.canonical import (
    canonical_json_bytes,
    canonicalize_json,
    digest_json,
    sha256_digest,
)
from app.video.migration.common_contracts import (
    CommonPackContractSnapshot,
    compare_common_contracts,
    validate_imported_configuration,
)
from app.video.migration.contracts import (
    AdaptedWorkflowAssessment,
    AgentSourceMapEntry,
    AgentSpecificationReview,
    ApprovedImportFile,
    ApprovedImportSet,
    ImportCandidate,
    ImportDryRunReport,
    ImportFinding,
    ImportMode,
    MappingStatus,
    MigrationEvidence,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.paths import (
    UnsafeLocalPathError,
    is_within_root,
    normalize_relative_path,
    read_local_bytes,
    resolve_under_root,
    validate_required_local_reference,
)

NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
DIGEST = "a" * 64
FIXED_SOURCE_ROOT = "fixtures/source/video"


def _snapshot() -> SourceSnapshot:
    return SourceSnapshot(
        "https://example.invalid/video", "commit-1", FIXED_SOURCE_ROOT, NOW
    )


def _write_common_contract_tree(root: Path) -> None:
    (root / "agents" / "video.editor").mkdir(parents=True)
    (root / "policies").mkdir()
    (root / "schemas").mkdir()
    (root / "workflows").mkdir()
    (root / "corpus").mkdir()
    (root / "inventory.json").write_text(
        '{"entries":[{"agent_id":"video.editor","agent_spec_path":"agents/video.editor/agent_spec.json",'
        '"maturity_level":"L0","status":"registered"}],"pack_id":"video"}',
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        '{"agents":[{"agent_id":"video.editor","agent_spec_path":"agents/video.editor/agent_spec.json",'
        '"allowed_tools":[],"status":"registered"}],"pack_id":"video",'
        '"production_activation_requested":false}',
        encoding="utf-8",
    )
    (root / "agents" / "video.editor" / "agent_spec.json").write_text(
        '{"agent_id":"video.editor","allowed_tools":[],"critique_edges":{"inputs":[],"outputs":[]},'
        '"max_refinement_count":3,"model_policy":{"model_id":"local-video-config-v1",'
        '"network_access":false,"provider":"local_deterministic"},'
        '"production_activation_requested":false,"status":"registered"}',
        encoding="utf-8",
    )
    (root / "policies" / "release.md").write_text("release policy", encoding="utf-8")
    (root / "schemas" / "video.json").write_text('{"version":1}', encoding="utf-8")
    (root / "workflows" / "pack_spine.json").write_text(
        '{"id":"video.pack-spine","version":"1.0.0"}', encoding="utf-8"
    )
    (root / "corpus" / "instruction.txt").write_text(
        "inert reference", encoding="utf-8"
    )


def _approved_file() -> ApprovedImportFile:
    return ApprovedImportFile(
        source_path="zeta/source.md",
        destination_path="reference/source.md",
        size_bytes=5,
        sha256=DIGEST,
        original_repository="https://example.invalid/video",
        original_commit="commit-1",
        original_path="zeta/source.md",
        license_status="reviewed",
    )


def test_canonical_json_and_digest_ignore_mapping_insertion_order() -> None:
    first = {"z": [2, 1], "a": {"b": True, "a": None}}
    second = {"a": {"a": None, "b": True}, "z": [2, 1]}

    assert canonicalize_json(first) == '{"a":{"a":null,"b":true},"z":[2,1]}'
    assert canonicalize_json(first) == canonicalize_json(second)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert digest_json(first) == digest_json(second)
    assert sha256_digest(b"hello") == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_fixed_source_snapshot_has_byte_identical_canonical_record() -> None:
    snapshot = _snapshot()

    assert snapshot.canonical_json() == (
        '{"recorded_at":"2025-01-01T12:00:00Z","source_commit":"commit-1",'
        '"source_repository":"https://example.invalid/video",'
        '"source_root":"fixtures/source/video"}'
    )
    assert snapshot.canonical_json().encode("utf-8") == canonical_json_bytes(snapshot)
    assert snapshot.digest() == digest_json(snapshot)


def test_approved_sets_are_frozen_sorted_and_size_consistent() -> None:
    snapshot = _snapshot()
    approved = ApprovedImportSet(
        snapshot=snapshot,
        files=(_approved_file(),),
        total_bytes=5,
        license_status="reviewed",
        approved_by="reviewer-1",
        approved_at=NOW,
        approval_id="approval-1",
    )

    assert approved.files[0].destination_path == "reference/source.md"
    assert approved.digest() == digest_json(approved)
    with pytest.raises(FrozenInstanceError):
        approved.approval_id = "changed"  # type: ignore[misc]


def test_dry_run_findings_are_sorted_and_secret_values_are_redacted() -> None:
    report = ImportDryRunReport(
        snapshot=_snapshot(),
        mode=ImportMode.DRY_RUN,
        included=(ImportCandidate("z.md", "z.md", 1, DIGEST),),
        excluded=(ImportCandidate("a.md", classification="excluded", reason="cache"),),
        findings=(
            ImportFinding("unsafe_path", path="z.md", message="later"),
            ImportFinding("secret", path="a.md", message="token=super-secret-value"),
        ),
        total_bytes=1,
        result=MigrationResult.FAIL,
    )

    reordered = ImportDryRunReport(
        snapshot=_snapshot(),
        mode=ImportMode.DRY_RUN,
        included=(ImportCandidate("z.md", "z.md", 1, DIGEST),),
        excluded=(ImportCandidate("a.md", classification="excluded", reason="cache"),),
        findings=tuple(reversed(report.findings)),
        total_bytes=1,
        result=MigrationResult.FAIL,
    )

    assert tuple(finding.code for finding in report.findings) == (
        "secret",
        "unsafe_path",
    )
    assert tuple(finding.code for finding in reordered.findings) == (
        "secret",
        "unsafe_path",
    )
    assert canonical_json_bytes(report) == canonical_json_bytes(reordered)
    assert "super-secret-value" not in report.canonical_json()
    assert report.included[0].source_path == "z.md"


def test_typed_review_and_evidence_records_have_no_corpus_body_fields() -> None:
    snapshot = _snapshot()
    mapping = AgentSourceMapEntry(
        common_agent_id="video.editor",
        mapping_status=MappingStatus.COMMON_ONLY,
        source_agent_ids=(),
        source_documents=("mapping/editor.md",),
        rationale="No suitable source role was approved.",
        reviewed_by="reviewer-1",
        reviewed_at=NOW,
    )
    spec_review = AgentSpecificationReview(
        common_agent_id="video.editor",
        reviewer="reviewer-1",
        reviewed_at=NOW,
        scope=("responsibility", "runtime"),
        result="pass",
    )
    workflow = AdaptedWorkflowAssessment(
        workflow_path="workflows/editor.json",
        workflow_digest=DIGEST,
        common_contract_digest=DIGEST,
        result="pass",
        findings=(),
    )
    evidence = MigrationEvidence(
        evidence_id="evidence-1",
        phase="intake",
        result=MigrationResult.PASS,
        commands=("planner --dry-run",),
        results=("pass",),
        source_snapshot=snapshot,
        correlation_id="correlation-1",
        recorded_at=NOW,
        blockers=(),
        residual_risks=(),
        change_set_ref="commit-1",
        mapping_review_ref="map-review-1",
    )

    assert mapping.source_agent_ids == ()
    assert spec_review.scope == ("responsibility", "runtime")
    assert workflow.findings == ()
    assert evidence.to_dict()["phase"] == "intake"
    assert "corpus" not in evidence.to_dict()


def test_common_contract_snapshots_are_byte_identical_and_exclude_corpus(
    tmp_path: Path,
) -> None:
    _write_common_contract_tree(tmp_path)

    first = CommonPackContractSnapshot.capture(tmp_path)
    second = CommonPackContractSnapshot.capture(tmp_path)

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first.contract_digest == second.contract_digest
    assert tuple(record.path for record in first.all_files) == (
        "agents/video.editor/agent_spec.json",
        "inventory.json",
        "manifest.json",
        "policies/release.md",
        "schemas/video.json",
        "workflows/pack_spine.json",
    )
    assert all(not record.path.startswith("corpus/") for record in first.all_files)
    assert first.inventory_agent_ids == ("video.editor",)
    assert first.manifest_agent_ids == ("video.editor",)


def test_common_contract_change_has_stable_blocking_codes(tmp_path: Path) -> None:
    _write_common_contract_tree(tmp_path)
    before = CommonPackContractSnapshot.capture(tmp_path)
    (tmp_path / "schemas" / "video.json").write_text('{"version":2}', encoding="utf-8")
    after = CommonPackContractSnapshot.capture(tmp_path)

    blocked = compare_common_contracts(before, after)
    repeated = compare_common_contracts(before, after)

    assert blocked.result is MigrationResult.BLOCKED
    assert blocked.changed_sections == ("schemas",)
    assert blocked.changed_paths == ("schemas/video.json",)
    assert tuple(finding.code for finding in blocked.findings) == (
        "common_contract_change_requires_review",
    )
    assert canonical_json_bytes(blocked) == canonical_json_bytes(repeated)


def test_configuration_boundary_reports_stable_redacted_codes() -> None:
    material = {
        "provider": "external-provider",
        "credential": "credential-value-must-not-appear",
        "network_access": True,
        "production_activation_requested": True,
        "human_gate_bypass": True,
        "corpus": "inert reference data",
    }

    report = validate_imported_configuration(material)
    repeated = validate_imported_configuration(material)

    assert report.result is MigrationResult.BLOCKED
    assert tuple(finding.code for finding in report.findings) == (
        "imported_human_gate_bypass_request",
        "imported_production_activation_request",
        "corpus_configuration_context",
        "imported_credential_request",
        "imported_network_request",
        "imported_provider_request",
    )
    assert canonical_json_bytes(report) == canonical_json_bytes(repeated)
    assert "credential-value-must-not-appear" not in report.canonical_json()


def test_relative_paths_are_normalized_and_unsafe_forms_rejected() -> None:
    assert normalize_relative_path(r"docs\video/./guide.md") == "docs/video/guide.md"
    for unsafe in (
        "/tmp/file",
        r"C:\temp\file",
        r"\\server\share\file",
        "../secret",
        "a/../../secret",
    ):
        with pytest.raises(UnsafeLocalPathError):
            normalize_relative_path(unsafe)


def test_path_containment_rejects_sibling_prefix_and_requires_readable_files(
    tmp_path: Path,
) -> None:
    root = tmp_path / "pack"
    root.mkdir()
    safe_file = root / "reference.txt"
    safe_file.write_text("reference", encoding="utf-8")

    assert is_within_root(safe_file, root)
    assert not is_within_root(tmp_path / "pack-escape" / "reference.txt", root)
    assert validate_required_local_reference(root, "reference.txt") == safe_file
    with pytest.raises(UnsafeLocalPathError) as error:
        validate_required_local_reference(root, "missing.txt")
    assert error.value.code == "missing_path"


def test_root_resolution_rejects_symlink_escape_and_reads_only_regular_files(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    safe_file = root / "safe.txt"
    safe_file.write_bytes(b"safe")
    assert read_local_bytes(root, "safe.txt") == b"safe"

    outside = tmp_path / "outside"
    outside.mkdir()
    outside_file = outside / "secret.txt"
    outside_file.write_bytes(b"secret")
    link = root / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation is unavailable in this environment.")

    with pytest.raises(UnsafeLocalPathError):
        resolve_under_root(root, "link/secret.txt", must_exist=True)
    with pytest.raises(UnsafeLocalPathError):
        read_local_bytes(root, "missing.txt")
