# Common Agent Swarm Operation System CASOPS

Executable system for downloading, auditing, curating, and synchronizing Kiro and Claude Code project configuration.

## Quick start

```bash
npm run bootstrap
```

This downloads permitted upstream repositories into `external/sources/`, writes `sources/source-lock.json` and `docs/source-audit.md`, then validates a Kiro/Claude-only sync plan.

## Important

Downloaded repositories are untrusted until audited. CASOPS never executes downloaded code, never imports third-party skills automatically, and never collects or generates material from Gemini or Gemini CLI.

## Local validation

Run `npm run doctor`, `npm run security`, `npm run sync -- --dry-run`, `npm run sync:check`, `npm run sdd:check`, and `npm test`. `npm run init` prints, but does not activate, the local hook.
