#!/usr/bin/env python3
"""Scan business/ for user_guide.script.hk.txt and generate missing MP3s via tts.py."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TTS_SCRIPT = ROOT / "tts.py"
BUSINESS_DIR = ROOT / "business"
INPUT_NAME = "user_guide.script.hk.txt"
OUTPUT_NAME = "user_guide.script.hk.mp3"


def find_pending_tts_jobs(business_dir: Path) -> list[tuple[Path, Path]]:
    """Return (input_txt, output_mp3) pairs where the MP3 does not exist yet."""
    if not business_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {business_dir}")

    jobs: list[tuple[Path, Path]] = []
    for input_path in sorted(business_dir.rglob(INPUT_NAME)):
        if not input_path.is_file():
            continue
        output_path = input_path.parent / OUTPUT_NAME
        if output_path.exists():
            continue
        jobs.append((input_path, output_path))
    return jobs


def rel_to_root(path: Path) -> Path:
    return path.relative_to(ROOT) if path.is_relative_to(ROOT) else path


def list_missing_mp3s(jobs: list[tuple[Path, Path]]) -> None:
    """Print missing MP3 paths (and their source scripts) first."""
    print(f"Missing MP3 count: {len(jobs)}")
    if not jobs:
        print("No missing user_guide.script.hk.mp3 files.")
        return

    print("Missing MP3s:")
    for index, (input_path, output_path) in enumerate(jobs, start=1):
        print(f"  [{index}/{len(jobs)}] {rel_to_root(output_path)}")
        print(f"           source: {rel_to_root(input_path)}")


def run_tts(input_path: Path, output_path: Path) -> None:
    if not TTS_SCRIPT.is_file():
        raise FileNotFoundError(f"tts.py not found: {TTS_SCRIPT}")

    cmd = [
        sys.executable,
        str(TTS_SCRIPT),
        str(input_path),
        "-o",
        str(output_path),
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan business/ for user_guide.script.hk.txt and call tts.py when "
            "user_guide.script.hk.mp3 is missing in the same directory."
        )
    )
    parser.add_argument(
        "--business-dir",
        type=Path,
        default=BUSINESS_DIR,
        help="Root directory to scan (default: ./business).",
    )
    parser.add_argument(
        "--test-first-one",
        action="store_true",
        help="Process only the first pending file for testing.",
    )
    parser.add_argument(
        "--list-missing",
        action="store_true",
        help="List missing MP3s first and exit without calling tts.py.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alias for --list-missing.",
    )
    args = parser.parse_args()

    business_dir = args.business_dir.resolve()
    jobs = find_pending_tts_jobs(business_dir)
    if args.test_first_one:
        jobs = jobs[:1]

    # Always list missing MP3s first.
    list_missing_mp3s(jobs)

    if args.list_missing or args.dry_run:
        print("\nList-only mode: not calling tts.py.")
        return 0

    if not jobs:
        return 0

    print(f"\nGenerating {len(jobs)} missing MP3(s)...")
    succeeded = 0
    failed = 0

    for index, (input_path, output_path) in enumerate(jobs, start=1):
        rel_in = rel_to_root(input_path)
        rel_out = rel_to_root(output_path)
        print(f"\n[{index}/{len(jobs)}] {rel_in} -> {rel_out}")

        try:
            run_tts(input_path, output_path)
            succeeded += 1
            print(f"  ✓ Done: {rel_out}")
        except subprocess.CalledProcessError as exc:
            failed += 1
            print(f"  ✗ tts.py failed with exit code {exc.returncode}")
        except Exception as exc:  # noqa: BLE001 — batch runner should continue
            failed += 1
            print(f"  ✗ Error: {exc}")

    print(f"\nCompleted: {succeeded} succeeded, {failed} failed, {len(jobs)} total.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
