"""Property checks for the inert corpus and executable-configuration boundary."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.approval import verify_human_import_gate
from app.video.migration.common_contracts import validate_imported_configuration
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import validate_corpus_integrity, write_corpus
from app.video.migration.intake import plan_source_intake

_RECORDED_AT: Final[datetime] = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_LICENSE_STATUS: Final[str] = "reviewed-local-reference"
_APPROVER: Final[str] = "migration-approver-property-07"
_APPROVAL_ID: Final[str] = "approval-property-07"
_SOURCE_REPOSITORY: Final[str] = "https://example.invalid/video"
_SOURCE_COMMIT: Final[str] = "property-07-commit"
_SOURCE_FILE: Final[str] = "executable-instructions.txt"
_DESTINATION_FILE: Final[str] = "references/executable-instructions.txt"

_EXECUTABLE_DIRECTIVES: Final[tuple[str, ...]] = (
    "#!/bin/sh\nprovider_activation_requested=true\n",
    '{"network_access_requested": true, "command": "activate"}\n',
    "credential_access_requested: x\n",
    "python -c 'enable_production()'\n",
    "skip_human_gate: true\n",
)
_ACTIVATION_CANDIDATES: Final[tuple[tuple[str, str], ...]] = (
    ("provider_activation_requested", "imported_provider_request"),
    ("credential_access_requested", "imported_credential_request"),
    ("network_access_requested", "imported_network_request"),
    ("runtime_activation", "imported_production_activation_request"),
    ("skip_human_gate", "imported_human_gate_bypass_request"),
)
_CORPUS_PATH_FORMS: Final[tuple[str | Path, ...]] = (
    "business/video/corpus/references/executable-instructions.txt",
    "./business/video/corpus/references/executable-instructions.txt",
    "corpus/references/executable-instructions.txt",
    "references/executable-instructions.txt",
    Path("business/video/corpus/references/executable-instructions.txt"),
)


@dataclass(frozen=True, slots=True)
class _CorpusBoundaryCase:
    """One bounded corpus payload and configuration candidate."""

    directive: str
    activation_field: str
    activation_code: str
    activation_value: object
    corpus_path: str | Path


@st.composite
def _corpus_boundary_cases(draw: st.DrawFn) -> _CorpusBoundaryCase:
    """Generate executable-looking bytes and nested activation candidates."""
    activation_field, activation_code = draw(st.sampled_from(_ACTIVATION_CANDIDATES))
    value_kind = draw(st.sampled_from(("boolean", "string", "nested")))
    if value_kind == "boolean":
        activation_value: object = True
    elif value_kind == "string":
        activation_value = "enabled"
    else:
        activation_value = {"requested": True}
    return _CorpusBoundaryCase(
        directive=draw(st.sampled_from(_EXECUTABLE_DIRECTIVES)),
        activation_field=activation_field,
        activation_code=activation_code,
        activation_value=activation_value,
        corpus_path=draw(st.sampled_from(_CORPUS_PATH_FORMS)),
    )


def _approved_import(source_root: Path, content: bytes) -> ApprovedImportSet:
    """Build the exact local approval record for one opaque corpus payload."""
    snapshot = SourceSnapshot(
        source_repository=_SOURCE_REPOSITORY,
        source_commit=_SOURCE_COMMIT,
        source_root=str(source_root),
        recorded_at=_RECORDED_AT,
    )
    return ApprovedImportSet(
        snapshot=snapshot,
        files=(
            ApprovedImportFile(
                source_path=_SOURCE_FILE,
                destination_path=_DESTINATION_FILE,
                size_bytes=len(content),
                sha256=hashlib.sha256(content).hexdigest(),
                original_repository=_SOURCE_REPOSITORY,
                original_commit=_SOURCE_COMMIT,
                original_path=_SOURCE_FILE,
                license_status=_LICENSE_STATUS,
            ),
        ),
        total_bytes=len(content),
        license_status=_LICENSE_STATUS,
        approved_by=_APPROVER,
        approved_at=_RECORDED_AT,
        approval_id=_APPROVAL_ID,
    )


def _write_approved_payload(
    temporary_root: Path, content: bytes
) -> tuple[Path, bytes, tuple[str, ...]]:
    """Run the real dry-run, exact gate, and staged corpus write."""
    source_root = temporary_root / "source"
    destination_root = temporary_root / "business" / "video" / "corpus"
    source_root.mkdir(parents=True)
    (source_root / _SOURCE_FILE).write_bytes(content)
    approved = _approved_import(source_root, content)
    report = plan_source_intake(
        source_root,
        approved.snapshot,
        destination_root=destination_root,
        destination_prefix="references",
        license_status=_LICENSE_STATUS,
    )
    assert report.mode is ImportMode.DRY_RUN
    assert report.result is MigrationResult.PASS
    verification = verify_human_import_gate(
        report,
        approved,
        approval_id=_APPROVAL_ID,
        approval_identity=_APPROVAL_ID,
        approved_by=_APPROVER,
        license_status=_LICENSE_STATUS,
        declared_destinations=(_DESTINATION_FILE,),
    )
    assert verification.result is MigrationResult.PASS
    write_report = write_corpus(
        destination_root,
        approved,
        verification=verification,
    )
    assert write_report.result is MigrationResult.PASS
    assert write_report.configuration_paths == (_DESTINATION_FILE,)
    destination = destination_root.joinpath(*_DESTINATION_FILE.split("/"))
    return destination, content, write_report.configuration_paths


# Feature: migration-redesign, Property 7: Imported corpus cannot enter configuration contexts.
# **Validates: Requirements 4.8, 4.9, 4.10, 2.10, 2.11, 2.12, 2.13, 2.14**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(
    _CorpusBoundaryCase(
        directive=_EXECUTABLE_DIRECTIVES[0],
        activation_field="provider_activation_requested",
        activation_code="imported_provider_request",
        activation_value=True,
        corpus_path=_CORPUS_PATH_FORMS[0],
    )
)
@example(
    _CorpusBoundaryCase(
        directive=_EXECUTABLE_DIRECTIVES[1],
        activation_field="credential_access_requested",
        activation_code="imported_credential_request",
        activation_value={"requested": True},
        corpus_path=_CORPUS_PATH_FORMS[3],
    )
)
@example(
    _CorpusBoundaryCase(
        directive=_EXECUTABLE_DIRECTIVES[2],
        activation_field="network_access_requested",
        activation_code="imported_network_request",
        activation_value="enabled",
        corpus_path=_CORPUS_PATH_FORMS[4],
    )
)
@example(
    _CorpusBoundaryCase(
        directive=_EXECUTABLE_DIRECTIVES[3],
        activation_field="runtime_activation",
        activation_code="imported_production_activation_request",
        activation_value=True,
        corpus_path=_CORPUS_PATH_FORMS[2],
    )
)
@example(
    _CorpusBoundaryCase(
        directive=_EXECUTABLE_DIRECTIVES[4],
        activation_field="skip_human_gate",
        activation_code="imported_human_gate_bypass_request",
        activation_value="enabled",
        corpus_path=_CORPUS_PATH_FORMS[1],
    )
)
@given(case=_corpus_boundary_cases())
def test_property_07_imported_corpus_remains_inert_and_out_of_configuration(
    case: _CorpusBoundaryCase,
) -> None:
    """Executable-looking bytes remain data and all active contexts reject corpus input."""
    content = case.directive.encode("utf-8")
    with TemporaryDirectory() as temporary_root:
        destination, expected_content, excluded_paths = _write_approved_payload(
            Path(temporary_root), content
        )

        assert destination.read_bytes() == expected_content
        integrity = validate_corpus_integrity(
            destination.parent.parent,
            excluded_paths=excluded_paths,
        )
        assert integrity.result is MigrationResult.PASS
        assert integrity.excluded_from_configuration == excluded_paths

        inert_text = validate_imported_configuration(
            {"description": case.directive},
            corpus_paths=excluded_paths,
        )
        assert inert_text.result is MigrationResult.PASS
        assert inert_text.findings == ()

        configuration_candidate = {
            "configuration": {
                "corpus_input": case.corpus_path,
                "activation": {case.activation_field: case.activation_value},
                "tools": [{"input_path": case.corpus_path}],
            }
        }
        boundary = validate_imported_configuration(
            configuration_candidate,
            corpus_paths=(*excluded_paths, "business/video/corpus/" + _DESTINATION_FILE),
        )
        finding_codes = {finding.code for finding in boundary.findings}
        assert boundary.result is MigrationResult.BLOCKED
        assert "corpus_configuration_context" in finding_codes
        assert case.activation_code in finding_codes

        configuration_path = validate_imported_configuration(
            {"tool_input": case.corpus_path},
            corpus_paths=(*excluded_paths, "business/video/corpus/" + _DESTINATION_FILE),
        )
        assert configuration_path.result is MigrationResult.BLOCKED
        assert {finding.code for finding in configuration_path.findings} == {
            "corpus_configuration_context"
        }
