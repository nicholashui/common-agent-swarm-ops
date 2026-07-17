# Traceability

| Requirement | Design | Task | Code | Test | Evidence |
|---|---|---|---|---|---|
| REQ-1 | manifest validation | 1,2 | scripts/lib/manifest.mjs | manifest.test.mjs | evidence.md |
| REQ-2 | scoped adapters | 3 | scripts/sync.mjs | sync.test.mjs | evidence.md |
| REQ-3 | safe downloader | 2 | scripts/source-download.mjs | source-download.test.mjs | evidence.md |
| REQ-4 | lifecycle gate | 4 | scripts/sdd-check.mjs | sdd-gate.test.mjs | evidence.md |
| REQ-5 | policy validation | 5 | scripts/lib/fs-safe.mjs | manifest.test.mjs | evidence.md |
| REQ-6 | curated ECC skill distribution | 6 | skills/, scripts/adapters/kiro.mjs, scripts/adapters/claude-code.mjs | adapters.test.mjs, sync.test.mjs | evidence.md |
