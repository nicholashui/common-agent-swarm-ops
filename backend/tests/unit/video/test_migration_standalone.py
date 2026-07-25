"""Focused tests for deterministic standalone isolation and CLI behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from app.video.migration.canonical import finding_sort_key
from app.video.migration.contracts import ImportFinding, MigrationResult
from app.video.migration.standalone import (
    DEFAULT_UPSTREAM_REPOSITORIES,
    StandalonePreconditions,
    StandaloneReport,
    verify_standalone,
)


def test_isolation_failure_short_circuits_content_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Network/upstream failures return before any local validator can run."""
    called = False

    def fail_if_called(*_args: object, **_kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("content validation must not run")

    monkeypatch.setattr("app.video.migration.standalone.validate_corpus_integrity", fail_if_called)

    report = verify_standalone(tmp_path / "business" / "video")

    assert not report.is_valid
    assert not report.content_validation_started
    assert not called
    assert {finding.code for finding in report.findings} == {
        "standalone_network_enabled",
        "standalone_upstream_available",
    }
    assert (
        report.canonical_json()
        == verify_standalone(tmp_path / "business" / "video").canonical_json()
    )


def test_unknown_upstream_availability_is_rejected_before_local_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown upstream declarations fail closed before local validators run."""
    called = False

    def fail_if_called(*_args: object, **_kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("content validation must not run")

    monkeypatch.setattr("app.video.migration.standalone.validate_corpus_integrity", fail_if_called)

    report = verify_standalone(
        tmp_path / "business" / "video",
        network_disabled=True,
        upstreams_unavailable=True,
        upstream_available=("unexpected-upstream",),
    )

    assert not report.is_valid
    assert not report.content_validation_started
    assert not called
    assert {finding.code for finding in report.findings} == {"standalone_unknown_upstream"}
    assert report.findings[0].path == "unexpected-upstream"


def test_isolated_run_aggregates_sorted_machine_readable_failures(tmp_path: Path) -> None:
    """Once isolated, local failures are aggregated and canonically ordered."""
    report = verify_standalone(
        tmp_path / "business" / "video",
        network_disabled=True,
        upstreams_unavailable=True,
    )

    assert report.content_validation_started
    assert report.result is MigrationResult.FAIL
    assert report.findings
    assert tuple(report.findings) == tuple(sorted(report.findings, key=finding_sort_key))
    assert (
        report.canonical_json()
        == verify_standalone(
            tmp_path / "business" / "video",
            network_disabled=True,
            upstreams_unavailable=True,
        ).canonical_json()
    )


def test_cli_prints_exact_success_marker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A passing read-only checker emits only the required success marker."""
    module_path = (
        Path(__file__).resolve().parents[4]
        / "scripts"
        / "business"
        / "check_video_domain_standalone.py"
    )
    module_spec = importlib.util.spec_from_file_location(
        "check_video_domain_standalone", module_path
    )
    assert module_spec is not None and module_spec.loader is not None
    cli = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(cli)
    video_root = tmp_path / "business" / "video"
    video_root.mkdir(parents=True)
    preconditions = StandalonePreconditions(
        network_disabled=True,
        upstream_repositories=DEFAULT_UPSTREAM_REPOSITORIES,
        unavailable_upstreams=DEFAULT_UPSTREAM_REPOSITORIES,
    )
    passing = StandaloneReport(
        result=MigrationResult.PASS,
        preconditions=preconditions,
        content_validation_started=True,
    )
    monkeypatch.setattr(cli, "verify_standalone", lambda *_args, **_kwargs: passing)

    exit_code = cli.main(
        [
            "--project-root",
            str(tmp_path),
            "--video-root",
            "business/video",
            "--network-disabled",
            "--upstream-unavailable",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "STANDALONE PASS\n"
    assert captured.err == ""


def test_precondition_report_does_not_leak_input_values() -> None:
    """Isolation diagnostics contain stable categories, not source content."""
    report = StandaloneReport(
        result=MigrationResult.FAIL,
        preconditions=StandalonePreconditions(
            network_disabled=False,
            upstream_repositories=("generic-swarm-ops", "va-agent-swarm"),
            unavailable_upstreams=(),
        ),
        findings=(
            ImportFinding(
                "standalone_network_enabled",
                message="token=super-secret-value",
            ),
        ),
    )

    assert "super-secret-value" not in report.canonical_json()
