# Common Agent Swarm Operation System CASOPS

**Project name:** `Common Agent Swarm Operation System CASOPS`  
**Package/repository identifier:** `casops`  
**Purpose:** Build an executable starter repository that downloads and audits approved reference sources, curates reviewed material, and synchronizes first-party configuration **only** for Kiro and Claude Code.  
**Current spec version:** `2.0.0-kiro-claude-only`  
**Last updated:** 2026-07-07

---

## Scope and Use

This repository is an executable boilerplate specification, not documentation alone. A coding agent implementing it MUST create a working `casops` repository with scripts, manifests, tests, documentation, and reproducible Kiro and Claude Code configuration.

Generated agent configuration is strictly limited to these locations:

```text
.kiro/steering/
.kiro/hooks/
.kiro/settings.json
.kiro/mcp.json
CLAUDE.md
.claude/skills/
.claude/commands/
.claude/agents/
.claude/settings.json
```

Do not generate configuration, skills, commands, rules, adapters, or documentation intended for any other agent product.

### Gemini / Gemini CLI exclusion

Gemini and Gemini CLI are prohibited source ecosystems. CASOPS MUST NOT collect, download, audit, curate, import, synchronize, adapt, or generate skills or configuration from Gemini or Gemini CLI. `sources/manifest.json`, `sources/docs-manifest.json`, source locks, audits, sync inputs, examples, tests, and generated outputs MUST contain no Gemini/Gemini CLI source entry or artifact. The only permitted Gemini references are this explicit exclusion policy and validation assertions that enforce it.

This exclusion does **not** prohibit unrelated cross-agent reference sources. Approved sources from other ecosystems may be downloaded and audited as reference material, subject to the import policy, provided they never produce configuration outside the Kiro and Claude Code locations above.

### Implementation prompt

```text
Create a new project named Common Agent Swarm Operation System CASOPS based on <PATH_TO_STARTER_MD>.

Use starter.md as the source-of-truth implementation contract. Create a working executable repository in the current directory; do not merely summarize it.

Create all required directories, package metadata, manifests, scripts, tests, Kiro configuration, Claude Code configuration, docs, examples, task.md, and status.md. Download enabled non-Gemini sources unless network access is unavailable. Then run npm run bootstrap and report the exact result.
```

If network or shell access is unavailable, create every first-party file and record this exact blocker in `status.md`:

```text
BLOCKED: cannot download sources because network/shell execution is unavailable.
```

## Project Modes and Variables

CASOPS supports both self-bootstrap mode (implement this specification in the current repository) and create-new-project mode (generate a downstream project). Missing values use these defaults:

| Variable | Description | Default |
|---|---|---|
| `PROJECT_NAME` | Display name of downstream project | `Common Agent Swarm Operation System CASOPS` |
| `PROJECT_ID` | Package/repository identifier | `casops` |
| `PROJECT_PURPOSE` | Project description | `Executable Kiro and Claude Code operation system` |
| `STACK` | Primary technology stack | `Node.js 20+, plain JavaScript, Node built-ins` |
| `DOWNLOAD_SOURCES` | Download enabled approved sources | `true` |
| `AGENT_SUPPORT` | Output targets | `kiro,claude-code` |
| `PACKAGE_MANAGER` | JavaScript package manager | `npm` |
| `LICENSE` | Generated-project license | `MIT` |

Do not overwrite a non-empty target directory without `--force` or explicit user approval. Preserve user-authored content outside CASOPS managed blocks where practical.

## Critical Implementation Requirements

An implementing agent MUST:

1. Create the repository structure in this document.
2. Create `package.json`, source manifests, executable Node scripts, tests, docs, examples, and status files.
3. Download every enabled permitted source, write `sources/source-lock.json`, and generate `docs/source-audit.md`.
4. Generate only Kiro and Claude Code configuration through `npm run sync`.
5. Run the bootstrap validations and report success or precise blockers.
6. Never execute downloaded code or automatically import it into active configuration.

## Required Repository Structure

```text
./
├── starter.md
├── README.md
├── CLAUDE.md
├── package.json
├── task.md
├── status.md
├── .gitignore
├── .editorconfig
├── .kiro/
│   ├── settings.json
│   ├── mcp.json
│   ├── steering/
│   └── hooks/
├── .claude/
│   ├── settings.json
│   ├── skills/
│   ├── commands/
│   └── agents/
├── sources/
│   ├── manifest.json
│   ├── docs-manifest.json
│   ├── source-lock.json
│   └── README.md
├── external/
│   ├── .gitignore
│   ├── sources/
│   └── docs/
├── scripts/
│   ├── project-starter.mjs
│   ├── create-project.mjs
│   ├── source-download.mjs
│   ├── source-audit.mjs
│   ├── doctor.mjs
│   ├── sync.mjs
│   ├── security.mjs
│   ├── review.mjs
│   ├── adapters/
│   │   ├── kiro.mjs
│   │   └── claude-code.mjs
│   └── lib/
│       ├── fs-safe.mjs
│       ├── git.mjs
│       ├── manifest.mjs
│       └── report.mjs
├── rules/
│   ├── manifest.json
│   ├── 00-constitution.md
│   ├── 10-karpathy.md
│   ├── 20-sdd.md
│   ├── 30-security.md
│   ├── 40-testing.md
│   ├── 50-token-efficiency.md
│   └── 60-human-approval.md
├── skills/
│   ├── manifest.json
│   ├── planning/
│   ├── implementation/
│   ├── testing/
│   ├── review/
│   ├── security/
│   ├── memory/
│   └── lifecycle/
├── hooks/
│   ├── manifest.json
│   └── scripts/
├── mcp-configs/
│   ├── manifest.json
│   ├── minimal.json
│   └── optional/
├── memory/
│   ├── README.md
│   ├── project.md
│   ├── handoff.md
│   └── reflections/
├── docs/
│   ├── installation.md
│   ├── usage.md
│   ├── agents.md
│   ├── kiro.md
│   ├── claude-code.md
│   ├── architecture.md
│   ├── source-audit.md
│   ├── security.md
│   ├── sync.md
│   ├── troubleshooting.md
│   └── changelog.md
├── examples/
│   ├── sdd-feature-workflow/
│   ├── self-review-workflow/
│   ├── skill-suggestion-workflow/
│   ├── kiro-sync-workflow/
│   └── claude-code-sync-workflow/
└── tests/
    ├── fixtures/
    ├── source-download.test.mjs
    ├── source-audit.test.mjs
    ├── sync.test.mjs
    ├── manifest.test.mjs
    └── adapters.test.mjs
```

## Required `package.json`

Create this file or an equivalent superset. No runtime dependency is required; use Node built-ins only.

```json
{
  "name": "casops",
  "version": "2.0.0-kiro-claude-only",
  "private": true,
  "type": "module",
  "description": "Common Agent Swarm Operation System CASOPS: executable Kiro and Claude Code configuration operations.",
  "scripts": {
    "bootstrap": "node scripts/project-starter.mjs bootstrap",
    "create": "node scripts/project-starter.mjs create",
    "init": "node scripts/project-starter.mjs init",
    "doctor": "node scripts/doctor.mjs",
    "sources:download": "node scripts/source-download.mjs",
    "sources:update": "node scripts/source-download.mjs --update",
    "sources:check": "node scripts/source-download.mjs --check",
    "sources:audit": "node scripts/source-audit.mjs",
    "sync": "node scripts/sync.mjs",
    "sync:check": "node scripts/sync.mjs --check",
    "security": "node scripts/security.mjs",
    "review": "node scripts/review.mjs",
    "test": "node --test tests/*.test.mjs",
    "format": "node scripts/project-starter.mjs format"
  },
  "engines": { "node": ">=20.0.0" }
}
```

## Source Manifests and External Policy

Create `sources/manifest.json` with a permitted-source list. Each record requires `id`, `name`, `url`, `target`, `type`, `enabled`, `priority`, `tier`, `quarantine`, `import_policy`, and `purpose`. Every target MUST begin with `external/sources/`. The manifest MUST contain no Gemini/Gemini CLI record, URL, target, alias, or indirect source definition.

Cross-agent sources remain valid reference inputs when licensed and audited; they must not imply that CASOPS generates their native configuration. A minimum manifest is:

```json
{
  "schema_version": "2.0",
  "generated_from": "starter.md",
  "default_profile": "all",
  "download_root": "external/sources",
  "sources": [
    {"id":"ecc","name":"ECC / Everything Claude Code","url":"https://github.com/affaan-m/ECC.git","target":"external/sources/ecc","type":"git","enabled":true,"priority":"required","tier":"core","quarantine":false,"import_policy":"curated-only","purpose":"Reference for Claude Code patterns and Kiro/Claude-compatible curation."},
    {"id":"anthropic-claude-code","name":"Anthropic Claude Code","url":"https://github.com/anthropics/claude-code.git","target":"external/sources/anthropic-claude-code","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"Official Claude Code compatibility reference."},
    {"id":"anthropic-skills","name":"Anthropic Agent Skills","url":"https://github.com/anthropics/skills.git","target":"external/sources/anthropic-skills","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"curated-only","purpose":"Official skill structure and packaging reference."},
    {"id":"anthropic-claude-plugins-official","name":"Anthropic Claude Plugins Official","url":"https://github.com/anthropics/claude-plugins-official.git","target":"external/sources/anthropic-claude-plugins-official","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"Official Claude Code plugin and configuration reference."},
    {"id":"openai-codex","name":"OpenAI Codex CLI","url":"https://github.com/openai/codex.git","target":"external/sources/openai-codex","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"Cross-agent reference for repository-instruction conventions only."},
    {"id":"opencode","name":"OpenCode","url":"https://github.com/anomalyco/opencode.git","target":"external/sources/opencode","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"Cross-agent configuration and MCP reference only."},
    {"id":"modelcontextprotocol-servers","name":"Model Context Protocol Servers","url":"https://github.com/modelcontextprotocol/servers.git","target":"external/sources/modelcontextprotocol-servers","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"MCP server and safety reference for Kiro and Claude Code."},
    {"id":"modelcontextprotocol-registry","name":"Model Context Protocol Registry","url":"https://github.com/modelcontextprotocol/registry.git","target":"external/sources/modelcontextprotocol-registry","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"MCP discovery reference."},
    {"id":"github-mcp-server","name":"GitHub MCP Server","url":"https://github.com/github/github-mcp-server.git","target":"external/sources/github-mcp-server","type":"git","enabled":true,"priority":"required","tier":"official","quarantine":true,"import_policy":"reference-only","purpose":"GitHub MCP integration reference."},
    {"id":"agents-md","name":"AGENTS.md Specification","url":"https://github.com/openai/agents.md.git","target":"external/sources/agents-md","type":"git","enabled":true,"priority":"required","tier":"standard","quarantine":true,"import_policy":"reference-only","purpose":"Cross-agent repository instruction reference."},
    {"id":"andrej-karpathy-skills","name":"Andrej Karpathy Skills","url":"https://github.com/forrestchang/andrej-karpathy-skills.git","target":"external/sources/andrej-karpathy-skills","type":"git","enabled":true,"priority":"required","tier":"behavior-rules","quarantine":false,"import_policy":"curated-only","purpose":"Behavior-rule reference."},
    {"id":"superpowers","name":"Superpowers","url":"https://github.com/obra/superpowers.git","target":"external/sources/superpowers","type":"git","enabled":true,"priority":"required","tier":"skills","quarantine":true,"import_policy":"curated-only","purpose":"Composable development-skill methodology reference."},
    {"id":"claude-mem","name":"Claude Mem","url":"https://github.com/thedotmack/claude-mem.git","target":"external/sources/claude-mem","type":"git","enabled":true,"priority":"required","tier":"memory","quarantine":true,"import_policy":"reference-only","purpose":"Persistent-memory architecture reference; never install automatically."},
    {"id":"awesome-agent-skills","name":"Awesome Agent Skills","url":"https://github.com/VoltAgent/awesome-agent-skills.git","target":"external/sources/awesome-agent-skills","type":"git","enabled":true,"priority":"optional","tier":"discovery","quarantine":true,"import_policy":"reference-only","purpose":"Cross-agent discovery reference subject to the CASOPS output and Gemini exclusion policies."},
    {"id":"wshobson-agents","name":"Claude Code Subagents by wshobson","url":"https://github.com/wshobson/agents.git","target":"external/sources/wshobson-agents","type":"git","enabled":true,"priority":"optional","tier":"agents","quarantine":true,"import_policy":"curated-only","purpose":"Claude Code specialist-agent patterns."},
    {"id":"modelcontextprotocol-servers-archived","name":"Model Context Protocol Servers Archived","url":"https://github.com/modelcontextprotocol/servers-archived.git","target":"external/sources/modelcontextprotocol-servers-archived","type":"git","enabled":false,"priority":"archived","tier":"historical","quarantine":true,"import_policy":"never-import","purpose":"Historical reference only; do not download by default."}
  ]
}
```

The existing source catalog may be extended with additional permitted sources that obey the same schema and policies. Never add a Gemini/Gemini CLI source, even as disabled, historical, quarantined, reference-only, or documentation-only content.

Create `sources/docs-manifest.json`. It contains only approved documentation references and MUST contain no Gemini/Gemini CLI entry.

```json
{
  "schema_version": "2.0",
  "docs": [
    {"id":"kiro-docs","name":"Kiro Documentation","url":"https://kiro.dev/docs","target":"external/docs/kiro.md","enabled":true,"purpose":"Kiro steering, hooks, settings, and MCP reference."},
    {"id":"claude-code-docs","name":"Claude Code Documentation","url":"https://docs.anthropic.com/en/docs/claude-code","target":"external/docs/claude-code.md","enabled":true,"purpose":"Claude Code project instructions, skills, commands, agents, and settings reference."},
    {"id":"modelcontextprotocol-docs","name":"Model Context Protocol Docs","url":"https://modelcontextprotocol.io","target":"external/docs/modelcontextprotocol.md","enabled":true,"purpose":"MCP concepts, client/server design, and safety reference."}
  ]
}
```

Create `external/.gitignore` as:

```gitignore
# Downloaded upstream repositories and documentation are intentionally not committed.
sources/
docs/
```

Downloaded material is untrusted and MUST NOT be committed. Only curated, licensed, attributed files may enter first-party `rules/`, `skills/`, `hooks/`, `mcp-configs/`, or `docs/attribution/` inputs. These inputs may generate configuration only for Kiro and Claude Code.

## Source Download, Lock, and Audit Behavior

Implement `scripts/source-download.mjs` with these commands:

```bash
npm run sources:download
npm run sources:update
npm run sources:check
node scripts/source-download.mjs --profile all
node scripts/source-download.mjs --profile core
node scripts/source-download.mjs --profile official
node scripts/source-download.mjs --profile discovery
node scripts/source-download.mjs --dry-run
node scripts/source-download.mjs --strict
```

The downloader MUST validate the manifest before selection and fail if any source, documentation record, lock record, or target path references Gemini/Gemini CLI. It MUST select every enabled permitted source, create `external/sources/`, shallow-clone missing repositories, fast-forward existing Git repositories, write `sources/source-lock.json`, and print a summary. It must not download disabled sources by default.

Use only these repository operations:

```bash
git clone --depth 1 <url> <target>
git -C <target> fetch --depth 1 origin
git -C <target> pull --ff-only
git -C <target> remote get-url origin
git -C <target> rev-parse HEAD
git -C <target> branch --show-current
git -C <target> log -1 --format=%cI
git -C <target> log -1 --format=%s
```

A required-source clone/update failure, missing `.git`, invalid URL, or prohibited source reference is fatal. Optional failures are recorded and non-fatal unless `--strict` is given. The downloader MUST NOT run installers, package managers, remote scripts, repository hooks, downloaded code, or writes outside the project root.

`sources/source-lock.json` MUST record `schema_version`, `generated_at`, an entry for each attempted source (`id`, `name`, `url`, `resolved_url`, `target`, `status`, `commit`, `branch`, `last_commit_at`, `last_commit_subject`, `license_files`, `package_files`, `quarantine`, and `import_policy`), and `failures`. It MUST never contain Gemini/Gemini CLI metadata.

Implement `scripts/source-audit.mjs` to read both manifests and the lock and write `docs/source-audit.md`. For each source it must report name, URL, target, status, commit, branch, license files, package files, priority, tier, quarantine, import policy, purpose, selected components, rejected components, and security notes.

The audit MUST reject automatic import when a license is absent, remote install/postinstall behavior is suspicious, a source is archived, credentials are required, global configuration would be modified, MCP access is broad, or the source is prohibited. The audit must explicitly state that cross-agent sources may be reference inputs but can never produce native output for other tools. It must state that all Gemini/Gemini CLI sources and artifacts are prohibited and rejected without download or audit.

The initial audit should mark most sources `Selected components: none yet` and `Rejected components: bulk import rejected until human review`. Small rule-only repositories may be curated only after license and security verification.

## Bootstrap Router, Doctor, and Security

Implement `scripts/project-starter.mjs` with:

```bash
node scripts/project-starter.mjs bootstrap
node scripts/project-starter.mjs create --name demo --path ../demo
node scripts/project-starter.mjs init
node scripts/project-starter.mjs format
```

`bootstrap` MUST run, in order:

```bash
npm run doctor
npm run sources:download
npm run sources:audit
npm run security
npm run sync -- --dry-run
npm run test
```

Any required failure fails bootstrap. `create` may delegate to `scripts/create-project.mjs`; it must parse name, path, purpose, stack, download choice, and overwrite mode, reject a non-empty path without approval/`--force`, copy `starter.md`, replace downstream metadata, generate all required first-party assets, optionally download sources, and print next steps.

Implement `scripts/doctor.mjs`. It MUST check Node >=20, Git availability, working directory, write permissions, both manifests, the scripts directory, the external directory (or ability to create it), OS platform, and symlink support if requested. It MUST also inspect manifests and existing generated assets for prohibited Gemini/Gemini CLI references and for output targets outside the Kiro/Claude Code allowlist. Its output begins:

```text
CASOPS doctor

Node: OK
Git: OK
Manifest: OK
Output scope: OK
External dir: OK
OS: <platform>
Result: OK
```

Implement `scripts/security.mjs` as a static scanner. It MUST scan downloaded repositories for suspicious root scripts, detect committed `.env`, private keys, tokens, and certificates, report MCP configs with broad filesystem access, warn on `curl | bash`, `irm ... | iex`, and postinstall behavior, verify that no prohibited-source artifact is present, and never execute downloaded scripts.

## Kiro and Claude Code Sync Layer

Implement `scripts/sync.mjs` plus two adapters only:

```text
scripts/adapters/kiro.mjs
scripts/adapters/claude-code.mjs
```

Do not create adapters for any other agent system. Sync MUST reject any requested target other than `kiro` or `claude-code`; `--target all` means these two targets only. It must validate that every source input is permitted and that every output path is in the allowlist before reading or writing.

Required commands:

```bash
npm run sync
npm run sync -- --dry-run
npm run sync -- --target kiro
npm run sync -- --target claude-code
npm run sync:check
```

The Kiro adapter generates or previews only:

```text
.kiro/settings.json
.kiro/mcp.json
.kiro/steering/
.kiro/hooks/
```

It must map approved shared rules to steering files, approved hook definitions to `.kiro/hooks/`, and reviewed minimal MCP configuration to `.kiro/mcp.json`. It must not mutate user/global Kiro settings.

The Claude Code adapter generates or previews only:

```text
CLAUDE.md
.claude/settings.json
.claude/skills/
.claude/commands/
.claude/agents/
```

It must map approved shared rules to `CLAUDE.md`, approved skills to `.claude/skills/`, reviewed commands to `.claude/commands/`, and reviewed specialist definitions to `.claude/agents/`. It must not mutate user/global Claude Code settings.

All generated files MUST include this header, adjusted only when the target format requires an equivalent comment:

```text
<!-- AUTO-GENERATED by CASOPS. Do not edit directly.
Source: rules/, skills/, hooks/, mcp-configs/
Run: npm run sync
-->
```

Preserve user-authored content outside managed markers when practical:

```md
<!-- BEGIN CASOPS MANAGED CONTENT -->
Generated content here.
<!-- END CASOPS MANAGED CONTENT -->
```

`sync -- --dry-run` must make no changes and must list planned generated files. `sync:check` must detect stale managed blocks, missing headers, unapproved output paths, non-reproducible output, prohibited source references, and configuration drift. Sync must never copy an entire third-party repository or bulk-import skills.

## Required Rules, Curation, and Approval

Create these shared source files:

```text
rules/00-constitution.md
rules/10-karpathy.md
rules/20-sdd.md
rules/30-security.md
rules/40-testing.md
rules/50-token-efficiency.md
rules/60-human-approval.md
```

`rules/00-constitution.md` MUST include:

```md
# Constitution

- Follow the user's goal exactly.
- Prefer simple, maintainable solutions.
- Make surgical changes.
- Do not perform destructive actions without approval.
- Do not install, execute, or import downloaded third-party code until audited.
- Generate configuration only for Kiro and Claude Code.
- Never collect, download, audit, curate, import, synchronize, or generate material from Gemini or Gemini CLI.
- Run relevant tests or explain why tests were not run.
- Update status after major work.
```

`rules/10-karpathy.md` MUST include think-before-coding, no hidden-requirement assumptions, simplest-working-solution, no speculative abstractions, surgical-change, visible-goal, and verification rules.

`rules/60-human-approval.md` MUST require approval before installing global packages, running remote installers, enabling credentialed MCP servers, copying third-party material into active Kiro or Claude Code configuration, modifying hooks, deleting files, or applying self-generated skill/rule changes.

Downloading is mandatory for every enabled permitted source; importing is never automatic. Keep these states distinct:

```text
downloaded source
audited source
curated import
generated Kiro or Claude Code output
```

Downloaded source state is `external/sources/<source-id>/`, untrusted, ignored by Git, and never executed. Audited state is recorded in `docs/source-audit.md` and `sources/source-lock.json`. Curated imports require a verified license, recorded source commit, recorded file checksum, human approval when high impact, no hidden installation behavior, and attribution.

Curated first-party inputs may live only in `rules/`, `skills/`, `hooks/`, `mcp-configs/`, and `docs/attribution/`. Generated output may live only in the Kiro and Claude Code locations enumerated in this specification. A source can be cross-agent reference material without being prohibited; its content must be transformed manually and safely into Kiro/Claude-compatible output, if approved. Prohibited Gemini/Gemini CLI content is never an eligible input.

## Tests and Acceptance Criteria

Create Node tests at minimum:

```text
tests/manifest.test.mjs
tests/source-download.test.mjs
tests/source-audit.test.mjs
tests/sync.test.mjs
tests/adapters.test.mjs
```

Tests MUST verify:

- both manifests parse;
- each enabled source has all required schema fields;
- source IDs are unique and targets start with `external/sources/`;
- no manifest, lock, audit fixture, or generated fixture contains Gemini/Gemini CLI source material;
- disabled archived sources are not selected by default;
- source-lock shape is valid after a mocked or real run;
- only `kiro.mjs` and `claude-code.mjs` adapters are registered;
- sync rejects all targets and paths outside the Kiro/Claude Code allowlist;
- Kiro dry-run includes only `.kiro/settings.json`, `.kiro/mcp.json`, `.kiro/steering/`, and `.kiro/hooks/`;
- Claude Code dry-run includes only `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/`, `.claude/commands/`, and `.claude/agents/`;
- generated files contain the CASOPS header and managed markers;
- no sync operation writes a third-party native configuration directory.

The following must pass:

```bash
npm run doctor
npm run sources:download
npm run sources:audit
npm run security
npm run sync -- --dry-run
npm run test
```

After a successful enabled-source download, every required manifest target exists; optional failures are recorded in the lock and audit. `sources/source-lock.json` and `docs/source-audit.md` must exist, and `external/` content must remain ignored by Git.

## Required Documentation, Examples, and Status Files

Create `README.md` beginning:

```md
# Common Agent Swarm Operation System CASOPS

Executable system for downloading, auditing, curating, and synchronizing Kiro and Claude Code project configuration.

## Quick start

```bash
npm run bootstrap
```

This downloads permitted upstream repositories into `external/sources/`, writes `sources/source-lock.json` and `docs/source-audit.md`, then validates a Kiro/Claude-only sync plan.

## Important

Downloaded repositories are untrusted until audited. CASOPS never executes downloaded code, never imports third-party skills automatically, and never collects or generates material from Gemini or Gemini CLI.
```

Create the following first-party documentation:

- `docs/agents.md`: supported Kiro and Claude Code workflows, shared rules, validation commands, and reference-source policy.
- `docs/kiro.md`: `.kiro/steering`, `.kiro/hooks`, settings, MCP mapping, managed-block behavior, and local-only scope.
- `docs/claude-code.md`: `CLAUDE.md`, `.claude/skills`, commands, agents, settings mapping, managed-block behavior, and local-only scope.
- `docs/sync.md`: target allowlist, adapter behavior, dry-run/check modes, rollback/backup behavior, and drift remediation.
- `docs/source-audit.md`: generated audit described above.
- `docs/security.md`, `docs/installation.md`, `docs/usage.md`, `docs/architecture.md`, `docs/troubleshooting.md`, and `docs/changelog.md` with CASOPS-specific content.

Create examples only for the declared targets and shared workflows:

```text
examples/sdd-feature-workflow/
examples/self-review-workflow/
examples/skill-suggestion-workflow/
examples/kiro-sync-workflow/
examples/claude-code-sync-workflow/
```

Each sync example must demonstrate generated files exclusively within the matching Kiro or Claude Code allowlist, never configuration for another agent product. The source-audit example must demonstrate the difference between an allowed cross-agent reference source and a prohibited Gemini/Gemini CLI source.

Create `task.md`:

```md
# Task

Implement `starter.md` as the Common Agent Swarm Operation System CASOPS executable repository.

## Required first milestone

- [ ] Create package metadata and source manifests
- [ ] Create create-project flow and downloader
- [ ] Generate source lock and source audit
- [ ] Create Kiro and Claude Code adapters
- [ ] Generate only approved target configuration
- [ ] Run doctor, security, sync dry-run, and tests
```

Create `status.md`:

```md
# Status

## Current phase

CASOPS bootstrap implementation.

## Latest update

Not started.

## Blockers

None yet.

## Commands to run

```bash
npm run bootstrap
```
```

## Implementation Order

1. Read this file fully.
2. Create the folder structure, package metadata, Git ignores, and both manifests.
3. Implement `scripts/lib/fs-safe.mjs`, `git.mjs`, `manifest.mjs`, and `report.mjs`.
4. Implement source downloading, source audit, doctor, security, sync, project starter, and create-project scripts.
5. Implement the Kiro and Claude Code adapters only.
6. Create shared rules, curated input manifests, docs, examples, tests, task, and status files.
7. Run the acceptance commands in order.
8. Update `status.md` with actual results and report the final summary.

## Prohibitions, Definition of Done, and Final Report

The coding agent MUST NOT:

- merely rewrite Markdown instead of creating the executable project;
- pretend downloads occurred or silently skip enabled permitted sources;
- execute downloaded repository scripts or install global packages;
- run remote installer scripts;
- bulk-copy downloaded skills, commands, hooks, or configuration into either target;
- overwrite user files without backup or overwrite a non-empty downstream project without approval;
- mutate global Kiro or global Claude Code configuration;
- emit configuration or adapters for any target outside Kiro and Claude Code;
- collect, download, audit, curate, import, synchronize, adapt, or generate skills/configuration from Gemini or Gemini CLI;
- add a Gemini/Gemini CLI source or documentation manifest entry, including a disabled or historical entry;
- put secrets in memory, log hidden reasoning, or auto-approve self-improvement suggestions.

If a permitted repository moves or redirects, allow the clone, record the resolved remote URL and warning in `sources/source-lock.json`, then continue. If a required permitted repository is unavailable, fail bootstrap, record it in the lock, and identify it precisely. For optional permitted repositories, continue and record the failure in both the lock and audit.

CASOPS is complete only when:

- [ ] the display name is exactly `Common Agent Swarm Operation System CASOPS` and the package/repository identifier is `casops`;
- [ ] `npm run bootstrap` and all required validation scripts exist;
- [ ] manifests contain permitted sources only and contain no Gemini/Gemini CLI entry;
- [ ] enabled permitted sources download into `external/sources/` and lock commits are recorded;
- [ ] source audit is generated and external downloads are ignored by Git;
- [ ] only the Kiro and Claude Code adapters exist and sync dry-run succeeds;
- [ ] generated targets are limited to `.kiro/` features and `CLAUDE.md`/`.claude/` features specified here;
- [ ] downloaded code is not executed or automatically imported;
- [ ] tests pass and `status.md` states actual results.

Non-goals: a web app, backend server, database, frontend framework, TypeScript, Docker, Kubernetes, cloud deployment, runtime third-party bootstrap dependencies, and automatic global tool configuration. Downstream projects may add application folders, CI, testing tools, or deployment assets, but they may not expand CASOPS generated-agent outputs beyond Kiro and Claude Code without a deliberate revision of this specification.

On completion, report:

```text
CASOPS bootstrap complete.

Downloaded permitted sources:
- <count> succeeded
- <count> failed
- <count> skipped

Generated:
- sources/source-lock.json
- docs/source-audit.md
- .kiro/ steering, hooks, settings, and MCP configuration
- CLAUDE.md and .claude/ skills, commands, agents, and settings

Validation:
- doctor: pass/fail
- security: pass/fail
- sync dry-run: pass/fail
- tests: pass/fail

Downloaded repositories are in external/sources/ and are not imported or executed until audited.
Only Kiro and Claude Code configuration was generated.
Gemini and Gemini CLI were excluded from all source and output workflows.
```
