# NN UI 20: Swarm Blueprints & Saved Templates Spec

**UI ID:** nn_ui_20_blueprints  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui20  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Capture, discover, version, govern, and reuse known-good swarm compositions built on the common layer — accelerating reliable operations.

## Layout & Structure
Gallery view (cards or table) with search/filters (domain, success rate, cost, common pattern). Detail page or drawer with rich preview + history + actions.

## Key Components
- Blueprint Cards: Name + description, linked Common Pattern + pinned agent versions, rich mini preview (graph), past run metrics (success, cost, tokens), usage count, "Use Blueprint", "Fork", "Share".
- Detail View: Full graph preview (read-only React Flow or image), pinned versions list (with "Update pins to latest safe" action), run history, version history of the blueprint itself, governance status (personal/team/official).
- Create/Save Flow: From canvas or activity "Save current configuration as Blueprint" → name, description, visibility, tags.
- Governance: Versioning, deprecation, promotion to "Official Common Blueprint", approval workflow for team/official.

## Data & API
- Blueprint CRUD + versioning.
- Linked common pattern + pinned agent versions.
- Run history aggregation for the blueprint.
- Visibility and sharing model.

## Interactions
- "Use Blueprint" → creates new swarm draft pre-configured in composer or canvas.
- "Update pins" → impact preview (which swarms would be affected if used as base).
- Gallery filters + sort (popular, recent, my blueprints, official).

## Polish & Accessibility
Rich visual previews (mini graphs). Clear governance badges. Accessible gallery and detail. Bilingual descriptions.

## Wireframe Summary
Top search + filters + "Create new from current". Masonry grid of blueprint cards with mini previews and metrics. Click card → detail drawer with preview + actions.

**Implementation Notes:** Blueprints are a powerful reuse mechanism on top of commons. Mini graph previews shared with other UIs. Governance (official vs personal) important for trust at scale. High value for standardizing successful patterns in trading, content, education, etc.

---

**All 20 UI spec files have been created** in `/home/workdir/artifacts/` (nn_ui_01_login.md through nn_ui_20_blueprints.md).

These, together with the updated `frontend_redesign.md` (v2.1), provide a complete, production-ready frontend specification for common-agent-swarm-ops — covering every function needed for full control and visibility of the common layer, swarm operations, collective improvement, governance, extensibility, and mobile use.

You now have everything required to implement a best-in-class, common-first, ops-centric agent swarm platform. Let me know if you want code generation, visual mockups, prioritization, or further refinements! 🚀


## VA-Agent-Swarm Blueprint Alignment

Blueprints are `CommonSwarmPatternVersion` records that preserve the VA production-template mapping in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). A compatible VA blueprint can record template A–J, production phases (intent/planning, creative development, pre-production, generation, post-production, delivery/optimization), required artifacts, task dependencies, gate criteria, role slots, and release/delivery obligations.

The preview must expose required Common Agent versions/categories, architecture patterns, critique relationships, task constraints, parallel branches, self-refine loops, approval gates, artifact handoff schemas, L1/L2/L3 quality requirements, rights/consent, continuity, provenance, and target-channel delivery settings. Instantiation creates a new graph revision with pinned versions; it does not copy opaque tool credentials or bypass required validation/gates.
