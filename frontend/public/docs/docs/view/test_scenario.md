# Document viewer — test scenarios

| ID | Priority | Given | When | Then |
|----|----------|-------|------|------|
| TS-DOC-001 | P0 | Valid path `/docs/registry/userguide.md` | Open viewer | Markdown headings render |
| TS-DOC-002 | P0 | Path with `..` | Open | Rejected/error |
| TS-DOC-003 | P0 | Path outside `/docs/` | Open | Error |
| TS-DOC-004 | P1 | Missing file | Open | Empty/soft miss message |
| TS-DOC-005 | P1 | HTML 200 fallback | Mock fetch HTML | Treated as miss not content |
| TS-DOC-006 | P2 | Back link | Click | Navigates `/` |
