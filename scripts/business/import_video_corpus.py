"""Plan or approval-gate a local Video Pack corpus import.

Dry-run mode discovers source metadata without mutation.  Write mode repeats
that discovery, verifies an exact local Approved Import Set, and delegates all
writes to the transactional corpus importer.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.video.migration.approval import verify_human_import_gate  # noqa: E402
from app.video.migration.canonical import canonicalize_json  # noqa: E402
from app.video.migration.contracts import (  # noqa: E402
    ApprovedImportFile,
    ApprovedImportSet,
    ImportDryRunReport,
    ImportFinding,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import CorpusWriteReport, write_corpus  # noqa: E402
from app.video.migration.intake import LicenseDeclaration, plan_source_intake  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover or approval-gate a local Video Pack corpus import."
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--recorded-at",
        help="UTC ISO-8601 snapshot time; defaults to the current UTC time.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=_REPOSITORY_ROOT,
        help="Common Repository root used for the default corpus destination.",
    )
    parser.add_argument(
        "--destination-root",
        type=Path,
        help="Local corpus root; relative paths are resolved from --project-root.",
    )
    parser.add_argument(
        "--destination-prefix",
        default="",
        help="Safe relative prefix beneath the corpus root for mapped files.",
    )
    parser.add_argument(
        "--allow-path",
        "--allow-list",
        dest="allow_paths",
        action="append",
        default=[],
        help="Restrict intake to this source-relative path or its descendants; repeatable.",
    )
    parser.add_argument(
        "--license-status",
        help="Reviewed license status applied to every requested candidate.",
    )
    parser.add_argument(
        "--license-file",
        type=Path,
        help="JSON object mapping source-relative paths to reviewed license statuses.",
    )
    parser.add_argument(
        "--approved-import-set",
        "--approved-set",
        "--approval-file",
        dest="approved_import_set",
        type=Path,
        help="Canonical JSON Approved Import Set required by --write.",
    )
    parser.add_argument(
        "--approval-id",
        help="Human Import Gate identity; defaults to the recorded approval ID.",
    )
    parser.add_argument(
        "--approved-by",
        help="Human reviewer identity; defaults to the recorded approver.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional output path for the same canonical JSON report printed to stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Perform the side-effect-free source scan (the default mode).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Verify an exact Approved Import Set and publish the corpus transactionally.",
    )
    return parser


def _parse_timestamp(raw: str | None) -> datetime:
    if raw is None:
        return datetime.now(UTC)
    value = raw.strip()
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None:
        raise ValueError("recorded-at must include a timezone.")
    return timestamp.astimezone(UTC)


def _resolve_path(path: Path, base: Path) -> Path:
    return path if path.is_absolute() else base / path


def _load_license_declaration(
    status: str | None,
    license_file: Path | None,
) -> LicenseDeclaration:
    declaration: dict[str, str] = {}
    if status is not None:
        declaration["*"] = status
    if license_file is None:
        return declaration or None
    value = json.loads(license_file.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("license-file must contain a JSON object.")
    for path, license_status in value.items():
        if not isinstance(path, str) or not isinstance(license_status, str):
            raise ValueError("license-file keys and values must be strings.")
        declaration[path] = license_status
    return declaration or None


def _snapshot(arguments: argparse.Namespace) -> SourceSnapshot:
    source_root = _resolve_path(arguments.source_root, Path.cwd())
    return SourceSnapshot(
        source_repository=arguments.source_repository,
        source_commit=arguments.source_commit,
        source_root=str(source_root.resolve(strict=False)),
        recorded_at=_parse_timestamp(arguments.recorded_at),
    )


def _failure_report(snapshot: SourceSnapshot, code: str, message: str) -> ImportDryRunReport:
    return ImportDryRunReport(
        snapshot=snapshot,
        mode=ImportMode.DRY_RUN,
        included=(),
        excluded=(),
        findings=(ImportFinding(code, message=message),),
        total_bytes=0,
        result=MigrationResult.FAIL,
    )


def _failure_write(code: str, message: str) -> CorpusWriteReport:
    return CorpusWriteReport(
        result=MigrationResult.BLOCKED,
        findings=(ImportFinding(code, message=message),),
        excluded_from_configuration=(),
    )


def _parse_approved_import_set(value: object) -> ApprovedImportSet:
    if not isinstance(value, Mapping):
        raise ValueError("approved import set must be a JSON object.")
    nested = value.get("approved_import_set")
    if isinstance(nested, Mapping):
        value = nested
    snapshot_value = value.get("snapshot")
    files_value = value.get("files")
    if not isinstance(snapshot_value, Mapping) or not isinstance(files_value, list):
        raise ValueError("approved import set must contain snapshot and files.")
    recorded_at = snapshot_value.get("recorded_at")
    if not isinstance(recorded_at, str):
        raise ValueError("approved snapshot recorded_at must be an ISO-8601 string.")
    snapshot = SourceSnapshot(
        source_repository=str(snapshot_value["source_repository"]),
        source_commit=str(snapshot_value["source_commit"]),
        source_root=str(snapshot_value["source_root"]),
        recorded_at=_parse_timestamp(recorded_at),
    )
    files: list[ApprovedImportFile] = []
    for raw_file in files_value:
        if not isinstance(raw_file, Mapping):
            raise ValueError("approved files must contain JSON objects.")
        files.append(ApprovedImportFile(**dict(raw_file)))
    total_bytes = value.get("total_bytes")
    if not isinstance(total_bytes, int) or isinstance(total_bytes, bool):
        raise ValueError("approved total_bytes must be an integer.")
    return ApprovedImportSet(
        snapshot=snapshot,
        files=tuple(files),
        total_bytes=total_bytes,
        license_status=str(value["license_status"]),
        approved_by=str(value["approved_by"]),
        approved_at=_parse_timestamp(str(value["approved_at"])),
        approval_id=str(value["approval_id"]),
    )


def _load_approved_import_set(path: Path) -> ApprovedImportSet:
    return _parse_approved_import_set(json.loads(path.read_text(encoding="utf-8")))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _validate_report_path(
    report_path: Path | None,
    *,
    project_root: Path,
    source_root: Path,
    destination_root: Path,
) -> ImportFinding | None:
    if report_path is None:
        return None
    resolved = report_path.resolve(strict=False)
    video_root = project_root / "business" / "video"
    if any(_is_within(resolved, root) for root in (video_root, source_root, destination_root)):
        return ImportFinding(
            "report_path_mutates_pack",
            field="report",
            message="A report must not be written inside the source or Video Pack roots.",
        )
    return None


def _emit(record: ImportDryRunReport | CorpusWriteReport, report_path: Path | None) -> int:
    output = record.canonical_json()
    if report_path is not None:
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(f"{output}\n", encoding="utf-8", newline="\n")
        except OSError:
            fallback = _failure_report(
                record.snapshot if isinstance(record, ImportDryRunReport) else _fallback_snapshot(),
                "report_write_failed",
                "The requested report path could not be written.",
            )
            output = fallback.canonical_json()
            print(output)
            return 2
    print(output)
    return 0 if record.result in (MigrationResult.PASS, MigrationResult.NO_CHANGE) else 2


def _fallback_snapshot() -> SourceSnapshot:
    return SourceSnapshot(
        source_repository="local.invalid",
        source_commit="invalid",
        source_root=".",
        recorded_at=datetime(1970, 1, 1, tzinfo=UTC),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run one local-only dry-run or exact approval-gated write."""
    arguments = _parser().parse_args(argv)
    try:
        snapshot = _snapshot(arguments)
    except (TypeError, ValueError, OSError, OverflowError):
        fallback = {
            "mode": ImportMode.WRITE.value if arguments.write else ImportMode.DRY_RUN.value,
            "result": MigrationResult.FAIL.value,
            "findings": [
                {
                    "code": "invalid_snapshot",
                    "message": "The pinned source snapshot could not be recorded.",
                }
            ],
        }
        print(canonicalize_json(fallback))
        return 2

    project_root = _resolve_path(arguments.project_root, Path.cwd()).resolve(strict=False)
    source_root = _resolve_path(arguments.source_root, Path.cwd()).resolve(strict=False)
    destination_root = (
        _resolve_path(arguments.destination_root, project_root)
        if arguments.destination_root is not None
        else project_root / "business" / "video" / "corpus"
    )
    report_path = (
        _resolve_path(arguments.report, Path.cwd()) if arguments.report is not None else None
    )
    report_path_finding = _validate_report_path(
        report_path,
        project_root=project_root,
        source_root=source_root,
        destination_root=destination_root,
    )
    if report_path_finding is not None:
        return _emit(
            _failure_report(snapshot, report_path_finding.code, report_path_finding.message),
            None,
        )

    approved: ApprovedImportSet | None = None
    if arguments.write:
        if arguments.approved_import_set is None:
            return _emit(
                _failure_write(
                    "approval_required",
                    "--write requires a canonical --approved-import-set record.",
                ),
                report_path,
            )
        try:
            approved = _load_approved_import_set(
                _resolve_path(arguments.approved_import_set, Path.cwd())
            )
        except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError, KeyError):
            return _emit(
                _failure_write(
                    "approval_record_invalid",
                    "The Approved Import Set could not be read or validated.",
                ),
                report_path,
            )

    license_status: LicenseDeclaration = None
    try:
        license_status = _load_license_declaration(arguments.license_status, arguments.license_file)
        report = plan_source_intake(
            source_root,
            snapshot,
            destination_root=destination_root,
            destination_prefix=arguments.destination_prefix,
            allow_paths=tuple(arguments.allow_paths),
            license_status=license_status,
            allowed_existing_destinations=(
                tuple(file.destination_path for file in approved.files)
                if approved is not None
                else ()
            ),
            mode=ImportMode.DRY_RUN,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        report = _failure_report(
            snapshot,
            "intake_configuration_error",
            "The local intake configuration could not be validated.",
        )

    if not arguments.write:
        return _emit(report, report_path)
    if approved is None:
        return _emit(
            _failure_write(
                "approval_required",
                "--write requires a canonical --approved-import-set record.",
            ),
            report_path,
        )

    verification = verify_human_import_gate(
        report,
        approved,
        approval_id=arguments.approval_id or approved.approval_id,
        approved_by=arguments.approved_by or approved.approved_by,
        license_status=license_status,
        declared_destinations=tuple(file.destination_path for file in approved.files),
    )
    result = write_corpus(destination_root, approved, verification=verification)
    return _emit(result, report_path)


if __name__ == "__main__":
    raise SystemExit(main())
