# Evidence

This ledger is append-only. Each entry identifies the command, result, and relevant revision.

- 2026-07-07 | bootstrap implementation | created requirements, design, tasks, traceability, templates, and gate | completed
- 2026-07-07 | `npm run doctor` | pass | Node, Git, manifests, output scope, and local directory checks passed
- 2026-07-07 | `npm run sources:download` | pass | four permitted Git sources downloaded; no source code was executed
- 2026-07-07 | `npm run sources:audit` | pass | lock metadata and review policy report generated
- 2026-07-07 | `npm run security` | pass with warnings | ignored source material reported static installer and postinstall indicators for human review
- 2026-07-07 | `npm run sync -- --dry-run` and `npm test` | pass | 17 allowlisted files planned; 10 focused tests passed
- 2026-07-07 | `npm run sync:check` | pass | generated allowlisted output is reproducible and free of drift
- 2026-07-07 | `npm run sdd:check` | pass | requirements, design, tasks, traceability, and evidence structure accepted
- Required gate: `npm run sdd:check`
- 2026-07-17 | approved ECC curation | installed four MIT-licensed, documentation-only adaptations to allowlisted Kiro and Claude Code skill locations; no ECC code, hooks, MCP configuration, installers, credentials, or Gemini material imported | completed
- 2026-07-17 | `npm run doctor`, `npm run security`, `npm run sync:check`, `npm run sdd:check`, and `npm test` | pass; security retained warnings only for quarantined, excluded ECC source material | 10 focused tests passed
- 2026-07-17 | `structure.md` harness migration | replaced all four Trae/Grok harness references with Kiro and Claude Code-only configuration paths; architecture otherwise preserved | completed
- 2026-07-17 | `npm run sdd:check`, Markdown diagnostics, legacy-harness scan, and `git diff --check` | pass; no Trae or Grok reference remains in the editable structure plan | completed
- 2026-07-24 | agent-hook model pin update | added `action.model: "gpt-5.6-luna"` to `.kiro/hooks/validate-docker-on-change.json`; all 11 legacy agent hooks now use the requested model, while native `.kiro.hook` agent actions inherit the workspace pin | completed
- 2026-07-24 | `npm run format` | pass | project reports no formatter dependency; `.editorconfig` conventions apply
- 2026-07-24 | `npm run sdd:check`, `npm run sync:check`, and diagnostics for all 29 hook files | pass | no SDD/sync drift or hook diagnostics found
- 2026-07-24 | `npm test -- --silent` and standalone hook JSON parse command | not run | execution was blocked by repeated environment permission prompts; hook files were instead validated through editor diagnostics and complete source inspection
- 2026-07-25 | migration and Special_Agent quality-review implementation | fixed migration evidence/property defects, strict typing, standalone unknown-upstream precondition handling, mandatory Special_Agent governance, deterministic test-only governance fixtures, and backend timing-only property flake configuration; no production Approval_Record or Risk_Assessment artifacts were fabricated | completed
- 2026-07-25 | `python -m pytest -q --tb=short` from `backend/` | pass | 724 tests passed, 4 skipped
- 2026-07-25 | `python -m ruff check app tests` and `python -m mypy app tests --show-error-codes --no-error-summary --no-incremental` from `backend/` | pass | no Ruff or strict-mypy findings
- 2026-07-25 | `npm run sdd:check`, `npm run sync:check`, and `npm test -- --silent` | pass | SDD artifacts and passing property metadata accepted; 10 Node tests passed
- 2026-07-25 | `python scripts/business/check_special_business_agents.py --expect-fail-closed` | pass | checked-in Special_Agent pack remains unavailable because mandatory Risk_Assessment records are absent; validation used a temporary copy and wrote no production evidence
- 2026-07-25 | standalone CLI precondition and explicit-offline checks | pass as fail-closed diagnostics | missing isolation claims returned code 2 before content validation; explicit offline claims ran local validation and returned deterministic failure because the checked-in Video Pack still lacks mapping, roster, corpus-manifest, and substantive SPEC assets
