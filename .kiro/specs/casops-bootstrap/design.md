# Design

## Decision
Node built-ins implement manifest validation, project-root confinement, a Git-only downloader, static audit/security checks, and deterministic adapters. Shared first-party rules and skills are the sole sync inputs. Downloaded repositories remain in ignored `external/sources/` and are neither executed nor copied.

## Requirements trace
- REQ-1: `scripts/lib/manifest.mjs` and `scripts/lib/fs-safe.mjs` validate inputs.
- REQ-2: `scripts/sync.mjs` plus Kiro and Claude Code adapters enforce output paths.
- REQ-3: `scripts/source-download.mjs` selects sources before any Git operation.
- REQ-4: `scripts/sdd-check.mjs` validates structured artifacts.
- REQ-5: policy validators reject prohibited source or target references.
- REQ-6: the reviewed skill manifest and both adapters emit curated, attributed skills to allowlisted Kiro and Claude Code locations.

## Security
All writes use root confinement. Git is spawned with fixed argument arrays. No downloaded files are executed. Hook activation is opt-in and `init` only prints instructions.
