# Design — Video pipeline brief → spine

## Overview

Host **product façade** (in-process) owns draft swarms, brief snapshots, spine stub state, package approvals, and activity. Frontend Plan / Execute / Activity / Dashboard / Agent Workflow / Operations consume REST only.

## Components

| Component | Role |
|-----------|------|
| `video_brief_spine.py` | UserBriefV1, DNA step load, stub advance, package decide, public views |
| `product_facade.py` | Materialize, spine run, package store, list flags |
| `composer.py` | recommend/materialize + brief meta |
| `swarms.py` | GET swarm, spine steps, package-decision, artifacts |
| `product_ops.py` | activity, approvals inbox merge, package-approvals detail |
| `approvals.py` | control-plane gates; package fallback for same URL space |
| Frontend clients | product-composer, product-swarms, product-ops, projections |

## Data flow

```text
Plan (goal + brief meta)
  → POST /composer/materialize
  → SwarmRecord{brief, members Phase-1+spine, spine}
  → GET /swarms/{id} + Execute spine panel
  → POST spine/steps (stub) → artifacts
  → package waiting_for_approval + appr_*
  → GET /approvals | /package-approvals/{id}
  → POST decision → completed | denied
```

## Fail-closed rules

- Action references required for mutations.
- Stubs never claim production media.
- Deny package does not resume.
- Catalog agents only; no invented agent_ids.

## Trace

See `trace.md` and focused tests under `backend/tests/unit/api/test_video_brief_spine.py`.
