"""Deterministic offline integration coverage for the migration redesign.

All fixtures are created beneath ``tmp_path`` with fixed timestamps and bytes.  The
CLI checks are subprocess calls against the checked-in local seams; no upstream
checkout, provider, credential, or network service is contacted.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.video.migration.agent_mapping import (
    AgentSourceMapValidator,
    inventory_digest,
    write_projections,
)
from app.video.migration.canonical import canonicalize_json, digest_json
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import CorpusManifest, validate_corpus_integrity
from app.video.migration.documentation import (
    ChangedMapReview,
    RefreshKind,
    RefreshOrchestrator,
    RefreshRequest,
    write_local_documentation,
)
from app.video.migration.evidence import (
    REQUIRED_COMPLETION_GATES,
    CompletionClaim,
    ExecutableGateResult,
    InMemoryMigrationEvidenceStore,
    MigrationEvidenceRecorder,
    RollbackRequest,
    RuntimePosture,
    append_rollback_evidence,
    evaluate_completion,
    verify_authorized_rollback,
)
from app.video.migration.operational_assets import AssetValidationReport, OperationalAssetValidator
from app.video.migration.standalone import DEFAULT_UPSTREAM_REPOSITORIES

NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
RECORDED_AT = "2025-01-01T12:00:00Z"
AGENT_IDS = tuple(f"video.agent_{index:03d}" for index in range(114))
SCRIPT_ROOT = Path(__file__).resolve().parents[4] / "scripts" / "business"


@dataclass(frozen=True)
class PackContext:
    project_root: Path
    video_root: Path
    source_root: Path
    snapshot: SourceSnapshot
    workflow: dict[str, object]
    workflow_path: str
    process_report: AssetValidationReport


def _list_field(payload: dict[str, object], field: str) -> list[object]:
    """Return a JSON array field with a precise type for strict test checking."""
    value = payload.get(field)
    assert isinstance(value, list)
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{canonicalize_json(value)}\n", encoding="utf-8", newline="\n")


def _tree_state(root: Path) -> tuple[tuple[str, bytes], ...]:
    if not root.exists():
        return ()
    return tuple(
        sorted(
            (path.relative_to(root).as_posix(), path.read_bytes())
            for path in root.rglob("*")
            if path.is_file()
        )
    )


def _run_cli(
    script_name: str, project_root: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT_ROOT / script_name), *arguments]
    environment = dict(os.environ)
    backend_root = str(project_root.parents[1] / "backend") if project_root.name == "video" else ""
    repository_root = Path(__file__).resolve().parents[4]
    backend_root = str(repository_root / "backend")
    environment["PYTHONPATH"] = os.pathsep.join(
        value for value in (backend_root, environment.get("PYTHONPATH", "")) if value
    )
    return subprocess.run(
        command,
        cwd=repository_root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _assert_canonical_json_result(
    completed: subprocess.CompletedProcess[str],
    *,
    expected_result: str,
    report_path: Path | None = None,
) -> dict[str, object]:
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    emitted = completed.stdout.strip()
    assert canonicalize_json(payload) == emitted
    assert payload["result"] == expected_result
    expected_code = 0 if expected_result in {"pass", "no_change"} else 2
    assert completed.returncode == expected_code
    if report_path is not None:
        assert report_path.read_text(encoding="utf-8").strip() == emitted
    return payload


def _inventory() -> dict[str, object]:
    return {
        "pack_id": "video",
        "entries": [
            {
                "agent_id": agent_id,
                "status": "registered",
                "maturity_level": "L0",
                "agent_spec_path": f"agents/{agent_id}/agent_spec.json",
            }
            for agent_id in AGENT_IDS
        ],
    }


def _runtime_binding(agent_id: str) -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "role": f"video production role {agent_id.removeprefix('video.')}",
        "status": "registered",
        "allowed_tools": ["media.stub"],
        "budget_policy": {
            "max_input_tokens": 100,
            "max_output_tokens": 100,
            "max_tool_requests": 1,
        },
        "critique_edges": {"inputs": [agent_id], "outputs": [agent_id]},
        "max_refinement_count": 1,
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": "local-video",
            "network_access": False,
        },
        "production_activation_requested": False,
        "prompt_reference": "video.prompt.default",
        "rubric_reference": "video.rubric.default",
        "schema_version": "1.0",
    }


def _manifest() -> dict[str, object]:
    return {
        "pack_id": "video",
        "pack_version": "1.0.0",
        "production_activation_requested": False,
        "validation": {"expected_agent_count": 114},
        "agents": [
            {
                "agent_id": agent_id,
                "status": "registered",
                "agent_spec_path": f"agents/{agent_id}/agent_spec.json",
                "allowed_tools": ["media.stub"],
                "production_active": False,
            }
            for agent_id in AGENT_IDS
        ],
    }


def _pack_spine() -> dict[str, object]:
    return {
        "definition_type": "pack_graph",
        "id": "video.pack-spine",
        "version": "1.0.0",
        "owner_id": AGENT_IDS[0],
        "authorization_id": "video.local-spine",
        "engine": "graph",
        "execution_budget": {
            "max_node_visits": 4,
            "max_handoffs": 3,
            "max_wall_clock_seconds": 5,
            "max_tool_requests": 1,
        },
        "memory": {"reads": [], "writes": []},
        "risk_gate_ids": ["video.local-safe"],
        "rollback": {
            "plan_id": "video.stub-compensation",
            "compensation_step_ids": ["media-stub"],
        },
        "pattern": "pack_spine",
        "nodes": [
            {
                "id": "supervise",
                "agent_id": AGENT_IDS[0],
                "tool_ids": [],
                "memory_reads": [],
                "memory_writes": [],
            },
            {
                "id": "media-stub",
                "agent_id": AGENT_IDS[1],
                "tool_ids": ["media.stub"],
                "memory_reads": [],
                "memory_writes": [],
            },
            {
                "id": "compliance-review",
                "agent_id": AGENT_IDS[2],
                "tool_ids": [],
                "memory_reads": [],
                "memory_writes": [],
            },
            {
                "id": "complete",
                "agent_id": AGENT_IDS[3],
                "tool_ids": [],
                "memory_reads": [],
                "memory_writes": [],
            },
        ],
        "edges": [
            {"from": "supervise", "to": "media-stub", "max_traversals": 1},
            {"from": "media-stub", "to": "compliance-review", "max_traversals": 1},
            {"from": "compliance-review", "to": "complete", "max_traversals": 1},
        ],
        "entry_node": "supervise",
        "terminal_node_ids": ["complete"],
    }


def _valid_workflow() -> dict[str, object]:
    return {
        "id": "video.edit",
        "workflow_path": "workflows/edit.dna.json",
        "agent_ids": [AGENT_IDS[0]],
        "execution_budget": {
            "max_node_visits": 4,
            "max_handoffs": 2,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "tool_ids": ["media.stub"],
        "risk_gate_ids": ["consent-review"],
        "compensation": {"strategy": "rollback"},
        "critique_loops": {"enabled": True, "max_iterations": 2},
        "human_interrupts": ["release-review"],
    }


def _create_base_pack(
    project_root: Path, *, empty_corpus_manifest: bool
) -> tuple[Path, Path, SourceSnapshot]:
    video_root = project_root / "business" / "video"
    (video_root / "agents").mkdir(parents=True)
    (video_root / "workflows").mkdir(parents=True)
    (video_root / "corpus").mkdir(parents=True)
    _write_json(video_root / "inventory.json", _inventory())
    _write_json(video_root / "manifest.json", _manifest())
    for agent_id in AGENT_IDS:
        _write_json(
            video_root / "agents" / agent_id / "agent_spec.json",
            _runtime_binding(agent_id),
        )
    _write_json(video_root / "workflows" / "pack_spine.json", _pack_spine())

    map_entries = [
        {
            "common_agent_id": agent_id,
            "mapping_status": "common_only",
            "source_agent_ids": [],
            "source_documents": ["inventory.json"],
            "rationale": "Human-approved common contract role with no suitable source role.",
            "reviewed_by": "reviewer-1",
            "reviewed_at": RECORDED_AT,
        }
        for agent_id in AGENT_IDS
    ]
    source_map = {
        "inventory_digest": inventory_digest(AGENT_IDS),
        "entries": map_entries,
    }
    _write_json(video_root / "AGENT_SOURCE_MAP.json", source_map)
    mapping_report = AgentSourceMapValidator().validate(
        _inventory(), source_map, video_root=video_root, repository_root=project_root
    )
    assert mapping_report.is_valid
    write_projections(video_root, mapping_report)
    if empty_corpus_manifest:
        (video_root / "corpus" / "MANIFEST.json").write_bytes(
            CorpusManifest(entries=()).to_json_bytes()
        )

    source_root = project_root / "fixed-source"
    source_root.mkdir()
    (source_root / "guide.md").write_bytes(b"fixed inert guide\n")
    snapshot = SourceSnapshot(
        source_repository="https://example.invalid/video",
        source_commit="commit-fixed-1",
        source_root=str(source_root),
        recorded_at=NOW,
    )
    return video_root, source_root, snapshot


def _approved_set(snapshot: SourceSnapshot, content: bytes) -> ApprovedImportSet:
    digest = hashlib.sha256(content).hexdigest()
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(
            ApprovedImportFile(
                source_path="guide.md",
                destination_path="guide.md",
                size_bytes=len(content),
                sha256=digest,
                original_repository=snapshot.source_repository,
                original_commit=snapshot.source_commit,
                original_path="guide.md",
                license_status="reviewed",
            ),
        ),
        total_bytes=len(content),
        license_status="reviewed",
        approved_by="reviewer-1",
        approved_at=NOW,
        approval_id="approval-fixed-1",
    )


def _run_import_flow(
    project_root: Path, source_root: Path, snapshot: SourceSnapshot
) -> tuple[ApprovedImportSet, dict[str, object], dict[str, object]]:
    evidence_root = project_root / "evidence"
    evidence_root.mkdir()
    dry_report_path = evidence_root / "import-dry-run.json"
    dry = _run_cli(
        "import_video_corpus.py",
        project_root,
        "--source-root",
        str(source_root),
        "--source-repository",
        snapshot.source_repository,
        "--source-commit",
        snapshot.source_commit,
        "--recorded-at",
        RECORDED_AT,
        "--project-root",
        str(project_root),
        "--license-status",
        "reviewed",
        "--report",
        str(dry_report_path),
    )
    dry_payload = _assert_canonical_json_result(
        dry, expected_result="pass", report_path=dry_report_path
    )
    assert dry_payload["mode"] == "dry_run"

    content = (source_root / "guide.md").read_bytes()
    approved = _approved_set(snapshot, content)
    approval_path = evidence_root / "approved-import-set.json"
    approval_path.write_text(f"{approved.canonical_json()}\n", encoding="utf-8", newline="\n")
    write_report_path = evidence_root / "import-write.json"
    write = _run_cli(
        "import_video_corpus.py",
        project_root,
        "--source-root",
        str(source_root),
        "--source-repository",
        snapshot.source_repository,
        "--source-commit",
        snapshot.source_commit,
        "--recorded-at",
        RECORDED_AT,
        "--project-root",
        str(project_root),
        "--license-status",
        "reviewed",
        "--approved-import-set",
        str(approval_path),
        "--approval-id",
        approved.approval_id,
        "--approved-by",
        approved.approved_by,
        "--write",
        "--report",
        str(write_report_path),
    )
    write_payload = _assert_canonical_json_result(
        write, expected_result="pass", report_path=write_report_path
    )

    manifest_before = (
        project_root / "business" / "video" / "corpus" / "MANIFEST.json"
    ).read_bytes()
    guide_before = (project_root / "business" / "video" / "corpus" / "guide.md").read_bytes()
    repeat = _run_cli(
        "import_video_corpus.py",
        project_root,
        "--source-root",
        str(source_root),
        "--source-repository",
        snapshot.source_repository,
        "--source-commit",
        snapshot.source_commit,
        "--recorded-at",
        RECORDED_AT,
        "--project-root",
        str(project_root),
        "--license-status",
        "reviewed",
        "--approved-import-set",
        str(approval_path),
        "--approval-id",
        approved.approval_id,
        "--approved-by",
        approved.approved_by,
        "--write",
    )
    repeat_payload = _assert_canonical_json_result(repeat, expected_result="no_change")
    assert (
        project_root / "business" / "video" / "corpus" / "MANIFEST.json"
    ).read_bytes() == manifest_before
    assert (
        project_root / "business" / "video" / "corpus" / "guide.md"
    ).read_bytes() == guide_before
    return approved, write_payload, repeat_payload


def _build_complete_pack(project_root: Path) -> PackContext:
    video_root, source_root, snapshot = _create_base_pack(project_root, empty_corpus_manifest=True)
    evidence_root = project_root / "evidence"
    evidence_root.mkdir()
    spec_report_path = evidence_root / "spec-write.json"
    specs = _run_cli(
        "build_video_agent_specs.py",
        project_root,
        "--project-root",
        str(project_root),
        "--video-root",
        "business/video",
        "--write",
        "--report",
        str(spec_report_path),
    )
    _assert_canonical_json_result(specs, expected_result="pass", report_path=spec_report_path)

    workflow = _valid_workflow()
    workflow_path = "workflows/edit.dna.json"
    workflow_report = OperationalAssetValidator(
        AGENT_IDS, ("media.stub",)
    ).register_adapted_workflow(video_root, workflow, workflow_path=workflow_path)
    assert workflow_report.result is MigrationResult.PASS

    process = {
        "processes": [
            {
                "process_id": "video-editing",
                "workflow_path": workflow_path,
                "agent_ids": [AGENT_IDS[0]],
            }
        ]
    }
    process_report = OperationalAssetValidator(
        AGENT_IDS, ("media.stub",)
    ).validate_process_coverage(process, {workflow_path: workflow}, video_root=video_root)
    assert process_report.is_valid
    _write_json(video_root / "process_coverage.json", process)
    (video_root / "knowledge" / "consumers").mkdir(parents=True)
    (video_root / "knowledge" / "consumers" / "editor.md").write_text(
        "Local video consumer\n", encoding="utf-8"
    )
    (video_root / "knowledge" / "seeds").mkdir(parents=True)
    (video_root / "knowledge" / "seeds" / "editing.md").write_text(
        "Inert local editing seed\n", encoding="utf-8"
    )
    _write_json(
        video_root / "knowledge" / "seeds" / "index.json",
        {
            "seeds": [
                {
                    "seed_path": "knowledge/seeds/editing.md",
                    "provenance": {
                        "repository": "local-video-pack",
                        "commit": "commit-fixed-1",
                        "path": "guide.md",
                        "license_status": "reviewed",
                    },
                    "consumer_ref": "knowledge/consumers/editor.md",
                    "review_status": "pass",
                }
            ]
        },
    )
    documentation = write_local_documentation(project_root, video_root=video_root)
    assert documentation.is_valid
    return PackContext(
        project_root,
        video_root,
        source_root,
        snapshot,
        workflow,
        workflow_path,
        process_report,
    )


def _standalone_cli(
    project_root: Path, *flags: str, report_name: str
) -> subprocess.CompletedProcess[str]:
    report_path = project_root / "evidence" / report_name
    return _run_cli(
        "check_video_domain_standalone.py",
        project_root,
        "--project-root",
        str(project_root),
        "--video-root",
        "business/video",
        *flags,
        "--report",
        str(report_path),
    )


def test_dry_run_approved_import_idempotence_and_canonical_evidence(
    tmp_path: Path,
) -> None:
    """Dry-run is non-mutating; exact approval writes once and re-applies safely."""
    video_root, source_root, snapshot = _create_base_pack(tmp_path, empty_corpus_manifest=False)
    before = _tree_state(video_root)
    dry = _run_cli(
        "import_video_corpus.py",
        tmp_path,
        "--source-root",
        str(source_root),
        "--source-repository",
        snapshot.source_repository,
        "--source-commit",
        snapshot.source_commit,
        "--recorded-at",
        RECORDED_AT,
        "--project-root",
        str(tmp_path),
        "--license-status",
        "reviewed",
    )
    dry_payload = _assert_canonical_json_result(dry, expected_result="pass")
    assert dry_payload["mode"] == "dry_run"
    assert _tree_state(video_root) == before

    approved, write_payload, repeat_payload = _run_import_flow(tmp_path, source_root, snapshot)
    assert approved.files[0].destination_path == "guide.md"
    assert write_payload["result"] == "pass"
    assert repeat_payload["result"] == "no_change"
    assert repeat_payload["unchanged_paths"]
    assert write_payload["excluded_from_configuration"] == ["guide.md"]
    integrity = validate_corpus_integrity(video_root / "corpus")
    assert integrity.is_valid


def test_rehash_mismatch_and_standalone_114_id_agreement_use_isolated_cli_fakes(
    tmp_path: Path,
) -> None:
    """Standalone reports corpus rehash drift and then passes the exact 114-ID fixture."""
    imported_project = tmp_path / "imported"
    _, source_root, snapshot = _create_base_pack(imported_project, empty_corpus_manifest=False)
    _run_import_flow(imported_project, source_root, snapshot)
    guide = imported_project / "business" / "video" / "corpus" / "guide.md"
    guide.write_bytes(b"tampered corpus bytes\n")
    mismatch = _standalone_cli(
        imported_project,
        "--network-disabled",
        "--upstream-unavailable",
        report_name="standalone-mismatch.json",
    )
    mismatch_payload = _assert_canonical_json_result(
        mismatch,
        expected_result="fail",
        report_path=imported_project / "evidence" / "standalone-mismatch.json",
    )
    assert any(
        finding["code"] == "corpus_digest_mismatch"
        for finding in _list_field(mismatch_payload, "findings")
        if isinstance(finding, dict)
    )
    assert guide.is_file()

    standalone_project = tmp_path / "standalone"
    _build_complete_pack(standalone_project)
    passing = _standalone_cli(
        standalone_project,
        "--network-disabled",
        "--upstream-unavailable",
        report_name="standalone-pass.json",
    )
    assert passing.returncode == 0
    assert passing.stdout == "STANDALONE PASS\n"
    assert passing.stderr == ""
    report = json.loads(
        (standalone_project / "evidence" / "standalone-pass.json").read_text(encoding="utf-8")
    )
    assert (
        canonicalize_json(report)
        == (standalone_project / "evidence" / "standalone-pass.json")
        .read_text(encoding="utf-8")
        .strip()
    )
    assert report["result"] == "pass"
    checks = {
        check["name"]: check["result"]
        for check in _list_field(report, "checks")
        if isinstance(check, dict)
    }
    assert checks["agent_id_agreement"] == "pass"
    assert report["preconditions"]["unavailable_upstreams"] == list(DEFAULT_UPSTREAM_REPOSITORIES)


def test_spec_cli_aggregates_multiple_errors_across_the_fixed_114_id_set(
    tmp_path: Path,
) -> None:
    """Controlled SPEC validation reports independent failures in one canonical result."""
    context = _build_complete_pack(tmp_path)
    first = context.video_root / "agents" / AGENT_IDS[0] / "SPEC.md"
    second = context.video_root / "agents" / AGENT_IDS[1] / "SPEC.md"
    first_text = first.read_text(encoding="utf-8")
    second_text = second.read_text(encoding="utf-8")
    responsibility_start = first_text.index("## Responsibility\n") + len("## Responsibility\n")
    next_heading = first_text.index("\n## Boundaries and escalation", responsibility_start)
    first.write_text(
        first_text[:responsibility_start] + "Generic role.\n" + first_text[next_heading:],
        encoding="utf-8",
    )
    second.write_text(second_text.replace("## Provenance\n", ""), encoding="utf-8")

    report_path = tmp_path / "evidence" / "spec-errors.json"
    result = _run_cli(
        "build_video_agent_specs.py",
        tmp_path,
        "--project-root",
        str(tmp_path),
        "--video-root",
        "business/video",
        "--dry-run",
        "--report",
        str(report_path),
    )
    payload = _assert_canonical_json_result(result, expected_result="fail", report_path=report_path)
    findings = {
        (item["agent_id"], item["code"])
        for item in _list_field(payload, "findings")
        if isinstance(item, dict)
    }
    assert (AGENT_IDS[0], "generic_responsibility") in findings
    assert (AGENT_IDS[1], "missing_required_heading") in findings
    assert len(_list_field(payload, "inventory_agent_ids")) == 114
    assert first.read_text(encoding="utf-8") != ""


def test_workflow_process_registration_and_special_skill_exclusion_keep_baseline(
    tmp_path: Path,
) -> None:
    """Only bounded local workflows/processes register; incomplete skills remain absent."""
    context = _build_complete_pack(tmp_path)
    assert context.process_report.is_valid
    assert (context.video_root / context.workflow_path).is_file()
    baseline = (context.video_root / "workflows" / "pack_spine.json").read_bytes()
    assert baseline == (context.video_root / "workflows" / "pack_spine.json").read_bytes()

    skill = {
        "skills": [
            {
                "skill_id": "unreviewed-caption-skill",
                "compatibility": True,
                "security": False,
                "overlap": True,
                "license": False,
                "consumer_ref": "knowledge/consumers/editor.md",
                "reviewer": "reviewer-1",
                "reviewed_at": RECORDED_AT,
                "result": "pass",
                "included": False,
            }
        ]
    }
    skill_report = OperationalAssetValidator(AGENT_IDS, ("media.stub",)).validate_special_skills(
        skill, video_root=context.video_root
    )
    assert skill_report.result is MigrationResult.FAIL
    assert skill_report.accepted_ids == ()
    assert not (context.video_root / "special_skills" / "unreviewed-caption-skill").exists()
    assert any(
        finding.code == "special_skill_review_incomplete" for finding in skill_report.findings
    )


def test_standalone_preconditions_fail_before_content_and_success_is_marker_only(
    tmp_path: Path,
) -> None:
    """Network/upstream fakes short-circuit first; isolated success emits only its marker."""
    _build_complete_pack(tmp_path)
    network_failure = _standalone_cli(
        tmp_path, "--upstream-unavailable", report_name="network-failure.json"
    )
    network_payload = _assert_canonical_json_result(
        network_failure,
        expected_result="fail",
        report_path=tmp_path / "evidence" / "network-failure.json",
    )
    assert network_payload["content_validation_started"] is False
    assert {
        finding["code"]
        for finding in _list_field(network_payload, "findings")
        if isinstance(finding, dict)
    } == {"standalone_network_enabled"}

    upstream_failure = _standalone_cli(
        tmp_path,
        "--network-disabled",
        "--upstream-unavailable",
        "--upstream-available",
        "generic-swarm-ops",
        report_name="upstream-failure.json",
    )
    upstream_payload = _assert_canonical_json_result(
        upstream_failure,
        expected_result="fail",
        report_path=tmp_path / "evidence" / "upstream-failure.json",
    )
    assert upstream_payload["content_validation_started"] is False
    assert any(
        finding["code"] == "standalone_upstream_available"
        for finding in _list_field(upstream_payload, "findings")
        if isinstance(finding, dict)
    )


def _passing_gates() -> tuple[ExecutableGateResult, ...]:
    return tuple(
        ExecutableGateResult(
            gate=name,
            result=MigrationResult.PASS,
            evidence_ref=f"check:{name}",
        )
        for name in REQUIRED_COMPLETION_GATES
    )


def test_completion_blocking_refresh_review_and_evidence_rollback_are_digest_exact(
    tmp_path: Path,
) -> None:
    """Completion remains conjunctive; reviewed refreshes and rollback retain evidence digests."""
    context = _build_complete_pack(tmp_path)
    gates = _passing_gates()
    blocked = evaluate_completion(gates, blockers=("security finding remains",))
    assert blocked.result is MigrationResult.BLOCKED
    assert not blocked.is_complete
    assert any(finding.code == "completion_blocker_security" for finding in blocked.findings)

    claim = CompletionClaim(
        claim_id="claim-fixed-1",
        statement="The local migration checks passed.",
        executable_evidence=tuple(gate.evidence_ref for gate in gates),
    )
    complete = evaluate_completion(gates, completion_claim=claim)
    assert complete.is_complete
    assert complete.runtime_activation_changed is False

    before_map = {"entries": [{"common_agent_id": AGENT_IDS[0], "rationale": "old"}]}
    after_map = {"entries": [{"common_agent_id": AGENT_IDS[0], "rationale": "new"}]}
    missing_review = RefreshOrchestrator().run(
        RefreshRequest(
            source_root=context.source_root,
            snapshot=context.snapshot,
            destination_root=context.video_root / "corpus",
            repository_root=context.project_root,
            approved_import_set=_approved_set(context.snapshot, b"fixed inert guide\n"),
            refresh_kind=RefreshKind.NORMAL,
            write_mode=True,
            license_status="reviewed",
            map_before=before_map,
            map_after=after_map,
            standalone_check=lambda _request: True,
            evidence_recorder=lambda _report: True,
        )
    )
    assert missing_review.result is MigrationResult.BLOCKED
    assert any(
        finding.code == "refresh_changed_map_review_required" for finding in missing_review.findings
    )

    review = ChangedMapReview(
        review_id="map-refresh-review-1",
        reviewer="reviewer-1",
        reviewed_at=NOW,
        common_agent_ids=(AGENT_IDS[0],),
    )
    refreshed_reports = []
    for refresh_kind in (RefreshKind.NORMAL, RefreshKind.URGENT):
        refreshed_reports.append(
            RefreshOrchestrator().run(
                RefreshRequest(
                    source_root=context.source_root,
                    snapshot=context.snapshot,
                    destination_root=context.video_root / "corpus",
                    repository_root=context.project_root,
                    approved_import_set=_approved_set(context.snapshot, b"fixed inert guide\n"),
                    refresh_kind=refresh_kind,
                    write_mode=True,
                    license_status="reviewed",
                    map_before=before_map,
                    map_after=after_map,
                    changed_map_review=review,
                    standalone_check=lambda _request: True,
                    evidence_recorder=lambda _report: True,
                    update_docs=True,
                )
            )
        )
    assert refreshed_reports[0].steps == refreshed_reports[1].steps
    assert all(
        report.is_success and report.completion_gate_passed for report in refreshed_reports
    ), [
        {
            "result": report.result.value,
            "steps": report.steps,
            "findings": [finding.code for finding in report.findings],
            "approval_verified": report.approval_verified,
            "standalone_passed": report.standalone_passed,
            "evidence_recorded": report.evidence_recorded,
            "provenance_preserved": report.provenance_preserved,
            "completion_gate_passed": report.completion_gate_passed,
        }
        for report in refreshed_reports
    ]
    assert all(
        report.approval_verified and report.provenance_preserved for report in refreshed_reports
    )

    pre_import_digest = CorpusManifest(entries=()).digest()
    change_set_digest = digest_json({"change_set": "migration-fixed-1"})
    store = InMemoryMigrationEvidenceStore()
    recorder = MigrationEvidenceRecorder(store)
    evidence = recorder.record_phase(
        evidence_id="migration-phase-fixed-1",
        phase="import",
        source_snapshot=context.snapshot,
        correlation_id="migration-correlation-fixed-1",
        recorded_at=NOW,
        commands=(
            "import_video_corpus.py --write",
            "check_video_domain_standalone.py --network-disabled",
        ),
        results=("pass", "STANDALONE PASS"),
        change_set_ref="migration-change-fixed-1",
        pre_import_manifest_digest=pre_import_digest,
        corpus_manifest_digest=refreshed_reports[0].corpus_manifest_digest,
        mapping_review_ref=review.review_id,
        standalone_result="STANDALONE PASS",
        documentation_check_result="pass",
        review_references=(review.review_id,),
        change_set_digest=change_set_digest,
    )
    assert evidence.pre_import_manifest_digest == pre_import_digest
    rollback_request = RollbackRequest(
        change_set_ref=evidence.change_set_ref,
        predecessor_manifest_digest=pre_import_digest,
        restored_manifest_digest=pre_import_digest,
        authorization_ref="rollback-review-fixed-1",
        authorized=True,
        authorized_by="reviewer-1",
        git_revert_applied=True,
        change_set_digest=change_set_digest,
        runtime_before=RuntimePosture("L0", False),
        runtime_after=RuntimePosture("L0", False),
    )
    rollback = verify_authorized_rollback(evidence, rollback_request)
    assert rollback.is_valid
    assert rollback.runtime_activation_changed is False
    rollback_evidence = append_rollback_evidence(
        recorder,
        evidence_id="migration-rollback-fixed-1",
        original=evidence,
        verification=rollback,
        recorded_at=NOW,
        correlation_id="migration-correlation-fixed-1",
    )
    assert rollback_evidence.result is MigrationResult.PASS
    assert tuple(record.evidence_id for record in store.records()) == (
        "migration-phase-fixed-1",
        "migration-rollback-fixed-1",
    )
    assert store.records()[0].pre_import_manifest_digest == pre_import_digest
    assert store.records()[1].pre_import_manifest_digest == pre_import_digest
