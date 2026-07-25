"""Run read-only, local-only Video Pack standalone verification.

The command never probes or contacts upstream repositories.  Callers must explicitly
assert that network access is disabled and that both historical upstream repositories
are unavailable; those preconditions are checked before any pack content is read.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.video.migration.canonical import canonicalize_json  # noqa: E402
from app.video.migration.standalone import (  # noqa: E402
    DEFAULT_UPSTREAM_REPOSITORIES,
    verify_standalone,
)


_UPSTREAM_ALL = "__all__"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the Video Pack using only local files and explicit isolation claims."
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
    parser.add_argument(
        "--network-disabled",
        "--no-network",
        dest="network_disabled",
        action="store_true",
        help="Explicitly assert that network access is disabled.",
    )
    parser.add_argument(
        "--upstream-unavailable",
        action="append",
        nargs="?",
        const=_UPSTREAM_ALL,
        default=[],
        metavar="REPOSITORY",
        help=(
            "Explicitly assert an upstream is unavailable; repeat for both configured "
            "repositories, or omit the value to assert all are unavailable."
        ),
    )
    parser.add_argument(
        "--upstreams-unavailable",
        action="store_true",
        help="Explicitly assert that all configured upstream repositories are unavailable.",
    )
    parser.add_argument(
        "--upstream-available",
        action="append",
        default=[],
        metavar="REPOSITORY",
        help="Explicitly mark an upstream as available for a deterministic failure test.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path for canonical JSON failure/pass evidence outside business/video.",
    )
    return parser


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_local(path: Path, base: Path, project_root: Path) -> Path:
    candidate = path if path.is_absolute() else base / path
    resolved = candidate.resolve(strict=False)
    if not _is_within(resolved, project_root):
        raise ValueError(
            "Standalone CLI paths must remain beneath the Common Repository root."
        )
    return resolved


def _failure_result(code: str, message: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "result": "fail",
        "content_validation_started": False,
        "findings": [{"code": code, "field": "cli", "message": message, "path": ""}],
    }


def _write_report(report_path: Path | None, output: str) -> bool:
    if report_path is None:
        return True
    try:
        report_path.write_text(f"{output}\n", encoding="utf-8", newline="\n")
    except OSError:
        return False
    return True


def _unavailable_argument(
    value: Sequence[str], all_requested: bool
) -> bool | tuple[str, ...]:
    if all_requested or _UPSTREAM_ALL in value:
        return True
    return tuple(value)


def main(argv: Sequence[str] | None = None) -> int:
    """Run standalone verification and return zero only for ``STANDALONE PASS``."""
    arguments = _parser().parse_args(argv)
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
            raise ValueError(
                "A standalone report cannot be written inside the Video Pack."
            )
        unavailable = _unavailable_argument(
            tuple(arguments.upstream_unavailable), arguments.upstreams_unavailable
        )
        report = verify_standalone(
            video_root,
            repository_root=project_root,
            network_disabled=arguments.network_disabled,
            upstreams_unavailable=unavailable,
            upstream_available=tuple(arguments.upstream_available),
            upstream_repositories=DEFAULT_UPSTREAM_REPOSITORIES,
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        output = canonicalize_json(
            _failure_result(
                "standalone_configuration_error",
                "The standalone CLI paths or isolation declarations could not be validated.",
            )
        )
        print(output)
        return 2

    if report.is_valid:
        if report_path is not None and not _write_report(
            report_path, report.canonical_json()
        ):
            output = canonicalize_json(
                _failure_result(
                    "report_write_failed",
                    "The requested standalone report path could not be written.",
                )
            )
            print(output)
            return 2
        print("STANDALONE PASS")
        return 0

    output = report.canonical_json()
    if report_path is not None and not _write_report(report_path, output):
        output = canonicalize_json(
            _failure_result(
                "report_write_failed",
                "The requested standalone report path could not be written.",
            )
        )
    print(output)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
