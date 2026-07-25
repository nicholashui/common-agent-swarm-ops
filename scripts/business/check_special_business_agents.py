"""Verify that the checked-in Special_Agent pack remains fail-closed."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPOSITORY_ROOT / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.registry.specials_validator import (  # noqa: E402
    SPECIAL_AGENT_IDS,
    SPECIALS_ALLOWLIST_PATHS,
    SPECIALS_PACK_ROOT,
    SPECIALS_SOURCE_RECORD_ROOT,
    ValidationReport,
    validate_specials_pack,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the checked-in Special_Agent pack's mandatory governance boundary."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=_REPOSITORY_ROOT,
        help="Common Repository root containing business/specials.",
    )
    parser.add_argument(
        "--expect-fail-closed",
        action="store_true",
        help="Pass only when missing mandatory governance rejects the checked-in pack.",
    )
    return parser


def _allowlisted_paths(root: Path) -> tuple[str, ...]:
    """Return existing pack files plus the explicit checked-in Source_Record paths."""
    paths = {path for path in SPECIALS_ALLOWLIST_PATHS if (root / path).is_file()}
    paths.update(
        f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json"
        for agent_id in SPECIAL_AGENT_IDS
        if (root / f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json").is_file()
    )
    return tuple(sorted(paths))


def _validate_checked_in_pack(project_root: Path) -> ValidationReport:
    """Validate a temporary copy so report retention never changes the checkout."""
    source_root = project_root / SPECIALS_PACK_ROOT
    if not source_root.is_dir():
        raise ValueError("The checked-in Special_Agent pack directory is missing.")

    with tempfile.TemporaryDirectory(prefix="specials-governance-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        temporary_pack_root = temporary_root / SPECIALS_PACK_ROOT
        shutil.copytree(source_root, temporary_pack_root)
        return validate_specials_pack(
            temporary_root,
            _allowlisted_paths(temporary_root),
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Return zero for a valid pack or the expected fail-closed production state."""
    arguments = _parser().parse_args(argv)
    try:
        report = _validate_checked_in_pack(arguments.project_root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError):
        return 2

    print(report.canonical_bytes().decode("utf-8"))
    if not arguments.expect_fail_closed:
        return 0 if report.validation_outcome == "pass" else 1

    finding_codes = {finding.code for finding in report.findings}
    expected_fail_closed = (
        report.validation_outcome == "fail"
        and report.accepted_agent_ids == ()
        and report.risk_gate.result == "fail"
        and "MISSING_RISK_ASSESSMENT" in finding_codes
    )
    if expected_fail_closed:
        print("SPECIALS GOVERNANCE: FAIL-CLOSED")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
