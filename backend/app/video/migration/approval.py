"""Exact, read-only Human Import Gate verification for corpus writes.

Approval verification is deliberately separate from the corpus writer.  It only
recomputes the source metadata exposed by a fresh dry-run and compares that
projection with the recorded :class:`ApprovedImportSet`; it never creates,
updates, or deletes a destination path.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.video.migration.canonical import sort_findings
from app.video.migration.contracts import (
    ApprovedImportFile,
    ApprovedImportSet,
    CanonicalRecord,
    HistoricalProvenance,
    ImportCandidate,
    ImportDryRunReport,
    ImportFinding,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.paths import PathInput, UnsafeLocalPathError, normalize_relative_path

LicenseDeclaration = str | Mapping[str, object] | None
ProvenanceDeclaration = HistoricalProvenance | Mapping[str, object] | None


@dataclass(frozen=True, slots=True)
class ApprovalVerificationReport(CanonicalRecord):
    """Deterministic result of checking one Human Import Gate.

    A passing report is the only result a write-mode importer may admit.  The
    report contains metadata records only; it never contains source file bytes.
    """

    result: MigrationResult
    findings: tuple[ImportFinding, ...]
    recomputed_files: tuple[ApprovedImportFile, ...] = ()
    recomputed_total_bytes: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        files = tuple(self.recomputed_files)
        if any(not isinstance(file, ApprovedImportFile) for file in files):
            raise TypeError("recomputed_files must contain ApprovedImportFile records.")
        object.__setattr__(self, "recomputed_files", tuple(sorted(files, key=_file_key)))
        if (
            isinstance(self.recomputed_total_bytes, bool)
            or not isinstance(self.recomputed_total_bytes, int)
            or self.recomputed_total_bytes < 0
        ):
            raise ValueError("recomputed_total_bytes must be a non-negative integer.")

    @property
    def is_approved(self) -> bool:
        """Return whether the exact gate may authorize a write."""
        return self.result is MigrationResult.PASS

    @property
    def is_valid(self) -> bool:
        """Compatibility alias for callers using validation terminology."""
        return self.is_approved

    @property
    def is_blocked(self) -> bool:
        """Return whether write mode must be blocked."""
        return not self.is_approved


# Descriptive compatibility names for callers that use either approval or gate
# terminology.  They are aliases rather than separate mutable record types.
ApprovalReport = ApprovalVerificationReport
HumanImportGateReport = ApprovalVerificationReport


def verify_human_import_gate(
    report: ImportDryRunReport,
    approved_import_set: ApprovedImportSet,
    *,
    approval_id: str | None = None,
    approval_identity: str | None = None,
    approved_by: str | None = None,
    license_status: LicenseDeclaration = None,
    provenance: ProvenanceDeclaration = None,
    declared_destinations: Iterable[PathInput] | None = None,
) -> ApprovalVerificationReport:
    """Verify that a dry-run is an exact match for a recorded approval.

    ``report`` must be the newly recomputed dry-run for the pinned source.  The
    optional declarations let the caller provide the values used to recompute
    provenance and licensing rather than trusting values copied from the approval
    record.  All comparisons are performed before this function returns and no
    filesystem operation is performed.

    The result is ``blocked`` for any source drift, scope change, destination
    change, metadata mismatch, failed dry-run, or approval-identity mismatch.
    """
    if not isinstance(report, ImportDryRunReport):
        raise TypeError("report must be an ImportDryRunReport.")
    if not isinstance(approved_import_set, ApprovedImportSet):
        raise TypeError("approved_import_set must be an ApprovedImportSet.")

    findings: list[ImportFinding] = []
    findings.extend(report.findings)
    if report.mode is not ImportMode.DRY_RUN:
        findings.append(
            ImportFinding(
                "approval_requires_dry_run",
                field="mode",
                message="Write approval must be checked against a fresh dry-run report.",
            )
        )
    if report.result is not MigrationResult.PASS or report.findings:
        findings.append(
            ImportFinding(
                "approval_dry_run_failed",
                field="report",
                message="The recomputed dry-run is not a passing import proposal.",
            )
        )

    _compare_snapshot_revision(report.snapshot, approved_import_set.snapshot, findings)
    _compare_approval_identity(
        approved_import_set,
        approval_id=approval_id,
        approval_identity=approval_identity,
        approved_by=approved_by,
        findings=findings,
    )

    current_candidates = tuple(sorted(report.included, key=_candidate_key))
    approved_files = tuple(sorted(approved_import_set.files, key=_file_key))
    current_by_source = _unique_candidates(current_candidates, findings)
    approved_by_source = _unique_approved_files(approved_files, findings)
    _compare_ordered_paths(current_candidates, approved_files, findings)
    _compare_scope_and_file_metadata(
        current_candidates,
        approved_files,
        current_by_source,
        approved_by_source,
        findings,
    )
    _compare_declared_destinations(
        current_candidates,
        approved_files,
        declared_destinations,
        findings,
    )
    _compare_total_bytes(report, approved_import_set, current_candidates, findings)
    recomputed_files = _recompute_files(
        report.snapshot,
        current_candidates,
        approved_by_source,
        approved_import_set,
        license_status,
        provenance,
        findings,
    )
    _compare_approved_provenance(
        report.snapshot,
        approved_import_set,
        approved_by_source,
        license_status,
        provenance,
        findings,
    )

    return ApprovalVerificationReport(
        result=MigrationResult.PASS if not findings else MigrationResult.BLOCKED,
        findings=tuple(findings),
        recomputed_files=recomputed_files,
        recomputed_total_bytes=sum(file.size_bytes for file in recomputed_files),
    )


def verify_import_approval(
    report: ImportDryRunReport,
    approved_import_set: ApprovedImportSet,
    **kwargs: object,
) -> ApprovalVerificationReport:
    """Compatibility alias for :func:`verify_human_import_gate`."""
    return verify_human_import_gate(report, approved_import_set, **kwargs)  # type: ignore[arg-type]


def verify_approval(
    report: ImportDryRunReport,
    approved_import_set: ApprovedImportSet,
    **kwargs: object,
) -> ApprovalVerificationReport:
    """Compatibility alias for :func:`verify_human_import_gate`."""
    return verify_human_import_gate(report, approved_import_set, **kwargs)  # type: ignore[arg-type]


verify_approved_import_set = verify_human_import_gate


def _file_key(file: ApprovedImportFile) -> tuple[str, str]:
    return file.destination_path, file.source_path


def _candidate_key(candidate: ImportCandidate) -> tuple[str, str]:
    return candidate.destination_path or "", candidate.source_path


def _compare_snapshot_revision(
    current: SourceSnapshot,
    approved: SourceSnapshot,
    findings: list[ImportFinding],
) -> None:
    for field_name in ("source_repository", "source_commit", "source_root"):
        if getattr(current, field_name) != getattr(approved, field_name):
            findings.append(
                ImportFinding(
                    "approval_snapshot_revision_drift",
                    path="snapshot",
                    field=field_name,
                    message="The recomputed source snapshot does not match the approved revision.",
                )
            )


def _compare_approval_identity(
    approved: ApprovedImportSet,
    *,
    approval_id: str | None,
    approval_identity: str | None,
    approved_by: str | None,
    findings: list[ImportFinding],
) -> None:
    if (
        approval_id is not None
        and approval_identity is not None
        and approval_id != approval_identity
    ):
        findings.append(
            ImportFinding(
                "approval_identity_mismatch",
                field="approval_id",
                message="The supplied approval identities do not agree.",
            )
        )
    expected_id = approval_identity if approval_identity is not None else approval_id
    if expected_id is not None and approved.approval_id != expected_id:
        findings.append(
            ImportFinding(
                "approval_identity_mismatch",
                path=approved.approval_id,
                field="approval_id",
                message="The recorded approval identity does not match the requested gate.",
            )
        )
    if approved_by is not None and approved.approved_by != approved_by:
        findings.append(
            ImportFinding(
                "approval_reviewer_mismatch",
                path=approved.approval_id,
                field="approved_by",
                message="The recorded approver does not match the requested gate identity.",
            )
        )


def _unique_candidates(
    candidates: tuple[ImportCandidate, ...], findings: list[ImportFinding]
) -> dict[str, ImportCandidate]:
    by_source: dict[str, ImportCandidate] = {}
    by_destination: dict[str, str] = {}
    for candidate in candidates:
        if candidate.source_path in by_source:
            findings.append(
                ImportFinding(
                    "approval_duplicate_source_path",
                    path=candidate.source_path,
                    field="included",
                    message="The recomputed import set contains a duplicate source path.",
                )
            )
        else:
            by_source[candidate.source_path] = candidate
        if candidate.destination_path is not None:
            previous = by_destination.get(candidate.destination_path.casefold())
            if previous is not None and previous != candidate.source_path:
                findings.append(
                    ImportFinding(
                        "approval_destination_collision",
                        path=candidate.source_path,
                        field="destination_path",
                        message="The recomputed import set maps multiple files to one destination.",
                    )
                )
            else:
                by_destination[candidate.destination_path.casefold()] = candidate.source_path
    return by_source


def _unique_approved_files(
    files: tuple[ApprovedImportFile, ...], findings: list[ImportFinding]
) -> dict[str, ApprovedImportFile]:
    by_source: dict[str, ApprovedImportFile] = {}
    by_destination: dict[str, str] = {}
    for file in files:
        if file.source_path in by_source:
            findings.append(
                ImportFinding(
                    "approval_duplicate_source_path",
                    path=file.source_path,
                    field="approved.files",
                    message="The approved set contains a duplicate source path.",
                )
            )
        else:
            by_source[file.source_path] = file
        previous = by_destination.get(file.destination_path.casefold())
        if previous is not None and previous != file.source_path:
            findings.append(
                ImportFinding(
                    "approval_destination_collision",
                    path=file.destination_path,
                    field="destination_path",
                    message="The approved set contains a duplicate destination path.",
                )
            )
        else:
            by_destination[file.destination_path.casefold()] = file.source_path
    return by_source


def _compare_ordered_paths(
    candidates: tuple[ImportCandidate, ...],
    files: tuple[ApprovedImportFile, ...],
    findings: list[ImportFinding],
) -> None:
    candidate_sources = tuple(candidate.source_path for candidate in candidates)
    approved_sources = tuple(file.source_path for file in files)
    if candidate_sources != approved_sources:
        findings.append(
            ImportFinding(
                "approval_order_mismatch",
                field="source_paths",
                message="The ordered source-file list differs from the approved import set.",
            )
        )
    candidate_destinations = tuple(candidate.destination_path for candidate in candidates)
    approved_destinations = tuple(file.destination_path for file in files)
    if candidate_destinations != approved_destinations:
        findings.append(
            ImportFinding(
                "approval_destination_order_mismatch",
                field="destination_paths",
                message="The ordered destination list differs from the approved import set.",
            )
        )


def _compare_scope_and_file_metadata(
    candidates: tuple[ImportCandidate, ...],
    files: tuple[ApprovedImportFile, ...],
    candidates_by_source: Mapping[str, ImportCandidate],
    files_by_source: Mapping[str, ApprovedImportFile],
    findings: list[ImportFinding],
) -> None:
    approved_destinations = {file.destination_path.casefold() for file in files}
    for candidate in candidates:
        approved = files_by_source.get(candidate.source_path)
        if approved is None:
            findings.append(
                ImportFinding(
                    "approval_scope_expansion",
                    path=candidate.source_path,
                    field="files",
                    message=(
                        "The recomputed import proposes a source file outside the approved scope."
                    ),
                )
            )
        if candidate.destination_path is None:
            findings.append(
                ImportFinding(
                    "undeclared_destination",
                    path=candidate.source_path,
                    field="destination_path",
                    message="The recomputed file has no safe declared destination.",
                )
            )
        elif candidate.destination_path.casefold() not in approved_destinations:
            findings.append(
                ImportFinding(
                    "undeclared_destination",
                    path=candidate.destination_path,
                    field="destination_path",
                    message="The recomputed destination is not declared by the approved set.",
                )
            )
        if approved is None:
            continue
        if candidate.destination_path != approved.destination_path:
            findings.append(
                ImportFinding(
                    "approval_destination_drift",
                    path=candidate.source_path,
                    field="destination_path",
                    message="The recomputed destination differs from the approved destination.",
                )
            )
        if candidate.size_bytes is None:
            findings.append(
                ImportFinding(
                    "approval_size_missing",
                    path=candidate.source_path,
                    field="size_bytes",
                    message="The recomputed source size is missing.",
                )
            )
        elif candidate.size_bytes != approved.size_bytes:
            findings.append(
                ImportFinding(
                    "approval_size_drift",
                    path=candidate.source_path,
                    field="size_bytes",
                    message="The recomputed source size differs from the approved size.",
                )
            )
        if candidate.sha256 is None:
            findings.append(
                ImportFinding(
                    "approval_digest_missing",
                    path=candidate.source_path,
                    field="sha256",
                    message="The recomputed source digest is missing.",
                )
            )
        elif candidate.sha256 != approved.sha256:
            findings.append(
                ImportFinding(
                    "approval_digest_drift",
                    path=candidate.source_path,
                    field="sha256",
                    message="The recomputed source digest differs from the approved digest.",
                )
            )
    for file in files:
        if file.source_path not in candidates_by_source:
            findings.append(
                ImportFinding(
                    "approval_scope_mismatch",
                    path=file.source_path,
                    field="files",
                    message="An approved source file is absent from the recomputed import scope.",
                )
            )


def _compare_declared_destinations(
    candidates: tuple[ImportCandidate, ...],
    files: tuple[ApprovedImportFile, ...],
    declared_destinations: Iterable[PathInput] | None,
    findings: list[ImportFinding],
) -> None:
    if declared_destinations is None:
        return
    declared: set[str] = set()
    for raw_destination in declared_destinations:
        try:
            declared.add(normalize_relative_path(raw_destination))
        except (TypeError, ValueError, UnsafeLocalPathError):
            findings.append(
                ImportFinding(
                    "undeclared_destination",
                    field="declared_destinations",
                    message="A declared destination is not a safe relative path.",
                )
            )
    current = {candidate.destination_path for candidate in candidates if candidate.destination_path}
    approved = {file.destination_path for file in files}
    for destination in sorted(current - declared):
        findings.append(
            ImportFinding(
                "undeclared_destination",
                path=destination,
                field="destination_path",
                message="The recomputed destination is outside the declared destination set.",
            )
        )
    if approved != declared:
        findings.append(
            ImportFinding(
                "approval_destination_scope_mismatch",
                field="declared_destinations",
                message="Declared destinations must exactly match the approved destination set.",
            )
        )


def _compare_total_bytes(
    report: ImportDryRunReport,
    approved: ApprovedImportSet,
    candidates: tuple[ImportCandidate, ...],
    findings: list[ImportFinding],
) -> None:
    recomputed_total = sum(candidate.size_bytes or 0 for candidate in candidates)
    if report.total_bytes != recomputed_total:
        findings.append(
            ImportFinding(
                "approval_report_total_bytes_mismatch",
                field="total_bytes",
                message="The dry-run total does not equal its ordered file sizes.",
            )
        )
    if report.total_bytes != approved.total_bytes:
        findings.append(
            ImportFinding(
                "approval_total_bytes_mismatch",
                field="total_bytes",
                message="The recomputed total differs from the approved total.",
            )
        )


@dataclass(frozen=True, slots=True)
class _ExpectedProvenance:
    repository: str
    commit: str
    path: str
    license_status: str


def _recompute_files(
    snapshot: SourceSnapshot,
    candidates: tuple[ImportCandidate, ...],
    approved_by_source: Mapping[str, ApprovedImportFile],
    approved: ApprovedImportSet,
    license_status: LicenseDeclaration,
    provenance: ProvenanceDeclaration,
    findings: list[ImportFinding],
) -> tuple[ApprovedImportFile, ...]:
    recomputed: list[ApprovedImportFile] = []
    for candidate in candidates:
        if (
            candidate.destination_path is None
            or candidate.size_bytes is None
            or candidate.sha256 is None
        ):
            continue
        expected = _expected_provenance(
            snapshot,
            candidate.source_path,
            approved_by_source.get(candidate.source_path),
            approved,
            license_status,
            provenance,
            findings,
        )
        try:
            recomputed.append(
                ApprovedImportFile(
                    source_path=candidate.source_path,
                    destination_path=candidate.destination_path,
                    size_bytes=candidate.size_bytes,
                    sha256=candidate.sha256,
                    original_repository=expected.repository,
                    original_commit=expected.commit,
                    original_path=expected.path,
                    license_status=expected.license_status,
                )
            )
        except (TypeError, ValueError):
            findings.append(
                ImportFinding(
                    "approval_recomputed_metadata_invalid",
                    path=candidate.source_path,
                    field="provenance",
                    message="Recomputed approval metadata is not valid for a local import file.",
                )
            )
    return tuple(sorted(recomputed, key=_file_key))


def _expected_provenance(
    snapshot: SourceSnapshot,
    source_path: str,
    approved: ApprovedImportFile | None,
    approved_set: ApprovedImportSet,
    license_status: LicenseDeclaration,
    provenance: ProvenanceDeclaration,
    findings: list[ImportFinding],
) -> _ExpectedProvenance:
    source_provenance: HistoricalProvenance | None = None
    if isinstance(provenance, HistoricalProvenance):
        source_provenance = provenance
    elif isinstance(provenance, Mapping):
        raw = provenance.get(source_path, provenance.get("*"))
        if raw is None:
            findings.append(
                ImportFinding(
                    "approval_provenance_missing",
                    path=source_path,
                    field="provenance",
                    message="No recomputed provenance declaration covers this source file.",
                )
            )
        elif isinstance(raw, HistoricalProvenance):
            source_provenance = raw
        else:
            findings.append(
                ImportFinding(
                    "approval_provenance_invalid",
                    path=source_path,
                    field="provenance",
                    message="The recomputed provenance declaration is not a valid record.",
                )
            )

    expected_license = _license_for(source_path, license_status)
    if isinstance(license_status, Mapping):
        declared_license = license_status.get(source_path, license_status.get("*"))
        if declared_license is None:
            findings.append(
                ImportFinding(
                    "approval_license_missing",
                    path=source_path,
                    field="license_status",
                    message="No recomputed license declaration covers this source file.",
                )
            )
        elif not isinstance(declared_license, str):
            findings.append(
                ImportFinding(
                    "approval_license_invalid",
                    path=source_path,
                    field="license_status",
                    message="The recomputed license declaration is not a text value.",
                )
            )
    if expected_license is None:
        fallback_license = approved_set.license_status
        if approved is not None:
            fallback_license = approved.license_status
        expected_license = (
            source_provenance.license_status if source_provenance is not None else fallback_license
        )
    elif not expected_license.strip():
        findings.append(
            ImportFinding(
                "approval_license_missing",
                path=source_path,
                field="license_status",
                message="A non-empty recomputed license status is required.",
            )
        )

    if source_provenance is None:
        return _ExpectedProvenance(
            snapshot.source_repository,
            snapshot.source_commit,
            source_path,
            expected_license,
        )
    return _ExpectedProvenance(
        source_provenance.repository,
        source_provenance.commit,
        source_provenance.path,
        expected_license,
    )


def _compare_approved_provenance(
    snapshot: SourceSnapshot,
    approved_set: ApprovedImportSet,
    approved_by_source: Mapping[str, ApprovedImportFile],
    license_status: LicenseDeclaration,
    provenance: ProvenanceDeclaration,
    findings: list[ImportFinding],
) -> None:
    for source_path, approved in sorted(approved_by_source.items()):
        expected = _expected_provenance(
            snapshot,
            source_path,
            approved,
            approved_set,
            license_status,
            provenance,
            findings,
        )
        for field_name in ("repository", "commit", "path"):
            if getattr(approved, _approved_field(field_name)) != getattr(expected, field_name):
                findings.append(
                    ImportFinding(
                        "approval_provenance_mismatch",
                        path=source_path,
                        field=f"original_{field_name}",
                        message="The approved provenance differs from the recomputed provenance.",
                    )
                )
        if approved.license_status != expected.license_status:
            findings.append(
                ImportFinding(
                    "approval_license_mismatch",
                    path=source_path,
                    field="license_status",
                    message="The approved license status differs from the recomputed value.",
                )
            )
        if license_status is None and approved.license_status != approved_set.license_status:
            findings.append(
                ImportFinding(
                    "approval_license_mismatch",
                    path=source_path,
                    field="license_status",
                    message="The file license status differs from the approved set declaration.",
                )
            )
    if isinstance(license_status, str) and approved_set.license_status != license_status:
        findings.append(
            ImportFinding(
                "approval_license_mismatch",
                path="approval",
                field="license_status",
                message="The approved set license status differs from the recomputed value.",
            )
        )


def _approved_field(field_name: str) -> str:
    return {
        "repository": "original_repository",
        "commit": "original_commit",
        "path": "original_path",
    }[field_name]


def _license_for(source_path: str, declaration: LicenseDeclaration) -> str | None:
    if isinstance(declaration, Mapping):
        value = declaration.get(source_path, declaration.get("*"))
        return value if isinstance(value, str) else None
    return declaration if isinstance(declaration, str) else None


__all__ = [
    "ApprovalReport",
    "ApprovalVerificationReport",
    "HumanImportGateReport",
    "LicenseDeclaration",
    "ProvenanceDeclaration",
    "verify_approval",
    "verify_approved_import_set",
    "verify_human_import_gate",
    "verify_import_approval",
]
