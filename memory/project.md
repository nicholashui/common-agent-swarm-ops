# Project Memory

**Last studied:** 2026-07-26  
**Branch:** `main` @ `97efc04` (Bug Review)  
**Remote:** `https://github.com/nicholashui/common-agent-swarm-ops`  
**gstack checkpoint:** `~/.gstack/projects/common-agent-swarm-ops/checkpoints/20260726-123259-project-study-baseline.md`

## What this is

**CASOPS** (Common Agent Swarm Operation System) is a monorepo with two tightly related missions:

1. **Harness ops (root Node tooling)** — Local-first system that downloads, audits, curates, and synchronizes **only Kiro and Claude Code** project configuration. Quarantines untrusted sources under `external/sources/`. Never executes/imports downloaded code until audited. Never touches Gemini/Gemini CLI material.
2. **Governed multi-agent ops platform** — FastAPI control plane + Next.js ops console + domain packs. Architecture SoT is `structure.md` v3.1. Design order: **Safety → Auditability → Correctness → Efficiency → Autonomy.**

## Stack (as-built)

| Layer | Location | Notes |
|-------|----------|--------|
| Root tooling | `scripts/`, `package.json` | Node ≥20; doctor, sources, sync, security, sdd, review |
| Rules / skills | `rules/`, `skills/` | Constitution, SDD, security, testing; sync into Kiro/Claude |
| Backend | `backend/app/` | FastAPI; public API only under `/api/v1` |
| Engines | `backend/app/engines/` | LangGraph target + legacy DNA runner (dual-engine strangle) |
| Frontend | `frontend/` | Next 14.2 / React 18 ops console; projection-only browser |
| Business packs | `business/` | Schemas, specials, **video** pack (114 agents, N3) |
| Docs | `docs/` | Redesigns (frontend 20 screens, backend, adoption, migration), security, usage |
| Memory | `memory/` | Continuity only; no secrets |

## Non-negotiables

- FastAPI `/api/v1/*` is the only public control plane; LangGraph is in-process, not a second product API.
- Browser is untrusted: generated REST contracts + authorized SSE; idempotent commands; no client authority.
- Domain logic lives in `business/<domain_id>/`; host stays domain-agnostic.
- Evolution is sandbox-only; never silent production mutation.
- Agent harness outputs: **Kiro + Claude Code only**.
- Spec-driven development with evidence; run tests / sdd gates before handoff.

## Backend map (high signal)

Public routers: adoption, definitions, runs, approvals, evaluation, evolution, memory, events, video, va.  
Supporting domains: governance, audit, evidence, artifacts, alerts, registry, workflows, process_intelligence, core (ingress, transport, idempotency, task coordination, recovery).  
Persistence target: Postgres primary; graph checkpoint migrations present. In-memory control-plane DB used in host foundation paths.

## Frontend map (high signal)

- Screens follow redesign inventory `ui_00`–`ui_20` under `docs/frontend_redesign/` + App Router routes in `frontend/src/app/`.
- Key libs: generated API client, `CommandCoordinator`, `LiveProjectionController`, screen-manifest/inventory/visual verification, session boundaries.
- Components: AppShell, Canvas, Dashboard/OperationalScreens, Composer, Registry, projection controls, UnavailableScreen (placeholder when projections unavailable).

## Video domain

- 114 agents under `business/video/agents/` (retain all forever per N3).
- Activation order: `agent_implement_order_list.md` (spine first: orchestrator, planner, router, judge, gatekeeper, …).

## Local run

- Backend `127.0.0.1:8000`, frontend `127.0.0.1:3000`.
- WIP: `start_all.ps1` / `stop_all.ps1` write PIDs to `.run/servers.json` (`.run/` ignored in WIP).

## Uncommitted work (as of study)

| Path | Intent |
|------|--------|
| `frontend/src/app/page.tsx` | Local dashboard preview instead of UnavailableScreen |
| `frontend/src/app/canvas/page.tsx` | Render Canvas (no redirect home) |
| `frontend/src/app/swarms/[swarmId]/canvas/page.tsx` | Render Canvas (param reserved for future projection) |
| `frontend/src/app/approved-screen-routes.test.tsx` | Match local-render expectations |
| `.gitignore` | Ignore `.run/` |
| `start_all.ps1`, `stop_all.ps1` | Untracked local server lifecycle |

## Useful commands

```bash
npm run doctor && npm run sync:check && npm run sdd:check && npm test
cd frontend && npm test && npm run typecheck
cd backend && pytest
.\start_all.ps1   # WIP
.\stop_all.ps1    # WIP
```

## Naming drift (aware)

- Repo/folder: `common-agent-swarm-ops`
- Some packages/docs: `generic-swarm-ops` / `generic-swarm-business-os` / `generic-swarm-ops-console`
- Treat as product aliases; working tree path is `C:\Project\common-agent-swarm-ops`
