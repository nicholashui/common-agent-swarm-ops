"""Draft and validate local Video Pack agent specifications.

The command is intentionally local-only.  Dry-run emits one canonical result and
never changes the Video Pack.  Write mode publishes only the validated ``SPEC.md``
files and never edits common inventory, manifest, or runtime binding JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.video.migration.canonical import canonicalize_json  # noqa: E402
from app.video.migration.specifications import (  # noqa: E402
    SpecificationIssue,
    SpecificationReport,
    build_specifications,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft and validate local Video Pack agent specifications."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=_REPOSITORY_ROOT,
        help="Common Repository root containing business/video.",
    )
    parser.add_argument(
        "--video-root",
        type=Path,
        default=Path("business/video"),
        help="Video Pack root, relative to --project-root by default.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and draft without writing (default).",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="Publish exactly one validated SPEC.md per inventory ID.",
    )
    parser.add_argument(
        "--inventory", type=Path, help="Optional local inventory JSON input."
    )
    parser.add_argument(
        "--source-map",
        type=Path,
        help="Optional local reviewed AGENT_SOURCE_MAP.json input.",
    )
    parser.add_argument(
        "--workflow-role-map",
        type=Path,
        help="Optional local WORKFLOW_ROLE_MAP.json input.",
    )
    parser.add_argument(
        "--critical-reviews",
        type=Path,
        help="Optional local critical-role review JSON input.",
    )
    parser.add_argument(
        "--corpus-manifest",
        type=Path,
        help="Optional local corpus/MANIFEST.json input.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional output path for the same canonical JSON result printed to stdout.",
    )
    return parser


def _resolve_local(path: Path, base: Path, project_root: Path) -> Path:
    candidate = path if path.is_absolute() else base / path
    resolved = candidate.resolve(strict=False)
    if not _is_within(resolved, project_root):
        raise ValueError(
            "Local specification inputs must remain beneath the Common Repository root."
        )
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_input(
    requested: Path | None,
    *,
    base: Path,
    project_root: Path,
) -> object | None:
    if requested is None:
        return None
    path = _resolve_local(requested, base, project_root)
    return _load_json(path)


def _failure_result(
    code: str, message: str, *, write_mode: bool = False
) -> dict[str, object]:
    issue = SpecificationIssue(code=code, field="cli", message=message)
    return {
        "schema_version": "1.0",
        "mode": "write" if write_mode else "dry_run",
        "result": "fail",
        "is_valid": False,
        "inventory_agent_ids": [],
        "specifications": [],
        "findings": [issue.to_dict()],
    }


def _emit(
    result: SpecificationReport | dict[str, object], report_path: Path | None
) -> int:
    output = (
        result.canonical_json()
        if isinstance(result, SpecificationReport)
        else canonicalize_json(result)
    )
    if report_path is not None:
        try:
            report_path.write_text(f"{output}\n", encoding="utf-8", newline="\n")
        except OSError:
            failure = _failure_result(
                "report_write_failed",
                "The requested specification report path could not be written.",
            )
            print(canonicalize_json(failure))
            return 2
    print(output)
    if isinstance(result, SpecificationReport):
        return 0 if result.is_valid else 2
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run local specification drafting/validation and return a stable process result."""
    arguments = _parser().parse_args(argv)
    write_mode = bool(arguments.write)
    try:
        project_root = arguments.project_root.resolve(strict=True)
        video_root = _resolve_local(arguments.video_root, project_root, project_root)
        if not video_root.is_dir():
            raise ValueError("The local Video Pack root must be a directory.")
        report_path = (
            _resolve_local(arguments.report, Path.cwd(), project_root)
            if arguments.report is not None
            else None
        )
        if report_path is not None and _is_within(report_path, video_root):
            raise ValueError("A report path cannot add files inside the Video Pack.")
        inventory = _read_optional_input(
            arguments.inventory,
            base=project_root,
            project_root=project_root,
        )
        source_map = _read_optional_input(
            arguments.source_map,
            base=project_root,
            project_root=project_root,
        )
        workflow_role_map = _read_optional_input(
            arguments.workflow_role_map,
            base=project_root,
            project_root=project_root,
        )
        critical_reviews = _read_optional_input(
            arguments.critical_reviews,
            base=project_root,
            project_root=project_root,
        )
        corpus_manifest = _read_optional_input(
            arguments.corpus_manifest,
            base=project_root,
            project_root=project_root,
        )
        result = build_specifications(
            video_root,
            repository_root=project_root,
            inventory=inventory,
            source_map=source_map,
            workflow_role_map=workflow_role_map,
            critical_reviews=critical_reviews,
            corpus_manifest=corpus_manifest,
            write_mode=write_mode,
        )
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return _emit(
            _failure_result(
                "specification_configuration_error",
                "The local specification inputs could not be validated.",
                write_mode=write_mode,
            ),
            None,
        )
    return _emit(result, report_path)


if __name__ == "__main__":
    raise SystemExit(main())
