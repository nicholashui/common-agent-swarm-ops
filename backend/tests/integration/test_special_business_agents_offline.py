"""Integration evidence for deterministic, offline Special_Agent validation."""

from __future__ import annotations

import builtins
import getpass
import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Final

import pytest

from app.registry import specials_validator
from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIALS_INVENTORY_PATH,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_SCHEMA_PATH,
    AcceptedSpecialsState,
    ValidationReport,
    canonical_agent_spec_path,
    canonical_json_bytes,
    validate_specials_pack,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SCHEMA_SOURCE_PATH: Final[Path] = _REPOSITORY_ROOT / SPECIALS_SCHEMA_PATH


def _agent_spec(agent_id: str) -> dict[str, object]:
    """Build a fixed local data-only specification fixture."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": "Special_Agent offline integration fixture",
        "allowed_tools": [],
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": "specials-offline-fixture-v1",
            "network_access": False,
        },
        "budget_policy": {
            "max_input_tokens": 1,
            "max_output_tokens": 1,
            "max_tool_requests": 0,
        },
        "prompt_reference": f"spagent.{agent_name}-prompt",
        "rubric_reference": f"spagent.{agent_name}-rubric",
        "critique_edges": {
            "inputs": [f"spagent.{agent_name}-input"],
            "outputs": [f"spagent.{agent_name}-output"],
        },
        "max_refinement_count": 1,
        "production_activation_requested": False,
    }


def _manifest_entry(agent_id: str) -> dict[str, object]:
    """Build one fixed canonical manifest entry."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "allowed_tools": [],
        "production_activation_requested": False,
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _inventory_entry(agent_id: str) -> dict[str, object]:
    """Build one fixed canonical inventory entry."""
    return {
        "agent_id": agent_id,
        "status": "draft",
        "agent_spec_path": canonical_agent_spec_path(agent_id),
    }


def _write_json(path: Path, value: object) -> None:
    """Write deterministic UTF-8 JSON fixture bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _write_fixture(root: Path, *, inventory_required: bool = True) -> tuple[str, ...]:
    """Create a fixed complete pack with no source or VA reference directories."""
    schema_path = root / SPECIALS_SCHEMA_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes(_SCHEMA_SOURCE_PATH.read_bytes())

    _write_json(
        root / SPECIALS_MANIFEST_PATH,
        {
            "pack_id": "specials",
            "agents": [_manifest_entry(agent_id) for agent_id in SPECIAL_AGENT_IDS],
            "production_activation_requested": False,
            "inventory_required": inventory_required,
        },
    )

    allowlisted_paths = [SPECIALS_SCHEMA_PATH, SPECIALS_MANIFEST_PATH]
    for agent_id in SPECIAL_AGENT_IDS:
        relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        _write_json(root / relative_path, _agent_spec(agent_id))
        allowlisted_paths.append(relative_path)

    if inventory_required:
        _write_json(
            root / SPECIALS_INVENTORY_PATH,
            {"entries": [_inventory_entry(agent_id) for agent_id in SPECIAL_AGENT_IDS]},
        )
        allowlisted_paths.append(SPECIALS_INVENTORY_PATH)

    return tuple(allowlisted_paths)


def _fixture_snapshot(root: Path, allowlisted_paths: tuple[str, ...]) -> dict[str, bytes]:
    """Capture allowlisted input bytes to prove validation does not mutate them."""
    return {
        relative_path: (root / relative_path).read_bytes() for relative_path in allowlisted_paths
    }


def _assert_canonical_report(report: ValidationReport, root: Path) -> None:
    """Assert report ordering, canonical encoding, and absence of volatile values."""
    report_bytes = report.canonical_bytes()
    report_data = json.loads(report_bytes.decode("utf-8"))
    assert report_bytes == canonical_json_bytes(report_data)

    file_paths = [file_result["path"] for file_result in report_data["files"]]
    assert file_paths == sorted(file_paths)
    assert report_data["accepted_agent_ids"] == sorted(report_data["accepted_agent_ids"])
    assert report_data["rejected_agent_ids"] == sorted(report_data["rejected_agent_ids"])
    finding_keys = [
        (
            finding["category"],
            finding["path"],
            finding["code"],
            finding.get("agent_id", ""),
        )
        for finding in report_data["findings"]
    ]
    assert finding_keys == sorted(finding_keys)

    assert str(root).encode("utf-8") not in report_bytes
    assert b"timestamp" not in report_bytes
    assert b"hostname" not in report_bytes
    assert b"random" not in report_bytes
    assert all(not Path(path).is_absolute() for path in file_paths)
    assert all(not Path(finding["path"]).is_absolute() for finding in report_data["findings"])


def test_offline_validation_is_deterministic_and_retains_canonical_evidence(
    tmp_path: Path,
) -> None:
    """Identical fixed local bytes produce identical ordered reports and no effects."""
    repository_root = tmp_path / "specials-determinism"
    allowlisted_paths = _write_fixture(repository_root)
    before = _fixture_snapshot(repository_root, allowlisted_paths)

    first = validate_specials_pack(repository_root, allowlisted_paths)
    second = validate_specials_pack(repository_root, allowlisted_paths)

    assert first.validation_outcome == second.validation_outcome == "pass"
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.accepted_agent_ids == SPECIAL_AGENT_IDS
    assert first.rejected_agent_ids == ()
    assert first.registration_effect == "eligible_draft_representation"
    assert first.report_retention == "retained"
    assert first.provenance.result == "pass"
    assert first.risk_gate.result == "pass"
    _assert_canonical_report(first, repository_root)
    _assert_canonical_report(second, repository_root)

    retained_path = (
        repository_root
        / specials_validator.SPECIALS_VALIDATION_REPORT_ROOT
        / f"{first.configuration_set_digest}.json"
    )
    assert retained_path.read_bytes() == first.canonical_bytes()
    assert _fixture_snapshot(repository_root, allowlisted_paths) == before


class _ForbiddenOperation:
    """Sentinel that turns an unexpected runtime boundary call into a failure."""

    def __init__(self, operation: str) -> None:
        self.operation = operation

    def __call__(self, *args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError(f"Offline validator attempted forbidden operation: {self.operation}")


def test_offline_validation_does_not_cross_network_process_credential_or_runtime_boundaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation remains local and data-only when forbidden operations are guarded."""
    repository_root = tmp_path / "specials-isolation"
    allowlisted_paths = _write_fixture(repository_root, inventory_required=False)

    forbidden_operations = {
        socket: ("socket", "create_connection", "getaddrinfo", "gethostbyname"),
        subprocess: ("run", "Popen", "call", "check_call", "check_output"),
        os: ("getenv",),
        getpass: ("getuser",),
        builtins: ("eval", "exec", "compile"),
    }
    for module, attributes in forbidden_operations.items():
        for attribute in attributes:
            monkeypatch.setattr(
                module, attribute, _ForbiddenOperation(f"{module.__name__}.{attribute}")
            )

    for attribute in (
        "register",
        "activate",
        "execute",
        "invoke_provider",
        "call_provider",
        "lookup_credentials",
    ):
        monkeypatch.setattr(
            specials_validator,
            attribute,
            _ForbiddenOperation(f"specials_validator.{attribute}"),
            raising=False,
        )

    report = validate_specials_pack(repository_root, allowlisted_paths)

    assert report.validation_outcome == "pass"
    assert report.registration_effect == "eligible_draft_representation"
    assert report.inventory.result == "not_required"
    assert report.accepted_agent_ids == SPECIAL_AGENT_IDS


def test_absent_reference_directories_do_not_override_checked_in_pack_evidence(
    tmp_path: Path,
) -> None:
    """Manifest/spec evidence remains sufficient when untrusted references are absent."""
    repository_root = tmp_path / "specials-without-references"
    allowlisted_paths = _write_fixture(repository_root)

    assert not (repository_root / "docs" / "special_agents_redesign").exists()
    assert not (repository_root / "va").exists()
    report = validate_specials_pack(repository_root, allowlisted_paths)

    assert report.validation_outcome == "pass"
    assert report.accepted_agent_ids == SPECIAL_AGENT_IDS
    assert report.rejected_agent_ids == ()
    assert report.provenance.result == "pass"
    assert report.risk_gate.result == "pass"
    assert not any(
        finding.code in {"MISSING_SOURCE_RECORD", "SOURCE_NOT_READABLE"}
        for finding in report.findings
    )


def test_report_retention_failure_preserves_completed_outcome_and_blocks_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Retention failure changes only evidence/effect status, not completed validation."""
    repository_root = tmp_path / "specials-retention-failure"
    allowlisted_paths = _write_fixture(repository_root)
    before = _fixture_snapshot(repository_root, allowlisted_paths)
    baseline = validate_specials_pack(repository_root, allowlisted_paths)
    previous_state: AcceptedSpecialsState = baseline.accepted_state

    monkeypatch.setattr(specials_validator, "_retain_validation_report", lambda *_args: False)
    report = validate_specials_pack(
        repository_root,
        allowlisted_paths,
        previous_state=previous_state,
    )

    assert report.validation_outcome == baseline.validation_outcome == "pass"
    assert report.accepted_agent_ids == baseline.accepted_agent_ids == SPECIAL_AGENT_IDS
    assert report.rejected_agent_ids == baseline.rejected_agent_ids == ()
    assert report.configuration_set_digest == baseline.configuration_set_digest
    assert report.manifest == baseline.manifest
    assert report.inventory == baseline.inventory
    assert report.provenance == baseline.provenance
    assert report.risk_gate == baseline.risk_gate
    assert report.report_retention == "failed"
    assert report.registration_effect == "none"
    assert any(finding.code == "REPORT_RETENTION_FAILED" for finding in report.findings)
    assert report.accepted_state == previous_state
    assert _fixture_snapshot(repository_root, allowlisted_paths) == before
