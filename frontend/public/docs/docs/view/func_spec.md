# Document viewer — functional specification

**Route:** `/docs/view?path=` · **Component:** `MarkdownViewerPage`  
**Note:** Independent of right drawer (help_spec.md).

## Functional requirements

### FR-DOC-001 Path constraint
- `path` query MUST start with `/docs/` and MUST NOT contain `..`.

### FR-DOC-002 Load
- Fetch same-origin markdown; cache successes.
- Soft-miss HTML/404; hard error shows path+message.

### FR-DOC-003 Render
- Same MarkdownDocument rules (GFM-ish, relative assets).

### FR-DOC-004 Navigation
- Back to console link returns to `/`.

### FR-DOC-005 Help self-docs
- Optional `/docs/docs/view/*` for meta documentation about the viewer.
