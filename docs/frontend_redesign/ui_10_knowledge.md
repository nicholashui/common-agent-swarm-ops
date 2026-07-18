# NN UI 10: Knowledge Management Hub Spec

**UI ID:** nn_ui_10_knowledge  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui10  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Full visibility and control over all knowledge sources (common + business-scoped) that power RAG agents, with seamless contribution from verified swarm runs.

## Layout & Structure
Hub view with collection cards grid + search/filters. Click collection → detail drawer or page with tabs (Sources, Search Test, Config, Contributions, Analytics).

## Key Components
- Collection Cards: Stats (chunks, usage, contribution volume), health badge, last sync.
- Sources Table: Filename/type/status/chunks/actions (preview, reindex, remove, contribute to common).
- Search Test: Input + results list with scores, metadata, "Add to prompt" action.
- Contribution Queue: From verified runs → review → approve to common knowledge.
- Sync Jobs: Git/Strapi/URL schedules with status and logs.
- Optional: Knowledge Graph viz (force-directed) with entity drill-down.

## Data & API
- Collection CRUD + stats.
- Source upload/sync/reindex.
- Hybrid search test endpoint.
- Contribution workflow (propose → review → index to common).
- Analytics queries (query patterns, agent usage).

## Interactions
- Drag-drop upload or "Sync from Git" → progress + AI tagging.
- Search test → relevance feedback buttons (improves future retrieval).
- Verified run contribution prompt (non-intrusive) → adds to queue with provenance.
- Reindex single source or whole collection.

## Polish & Accessibility
Virtualized tables for large source lists. Accessible search and forms. Bilingual metadata support. Loading states for sync/reindex.

## Wireframe Summary
Top search + filters. Grid of collection cards. Detail view: Tabs with sources table, search box + results, contribution queue.

**Implementation Notes:** Deep integration with vector DB and contribution pipeline from nn_ui_05/ nn_ui_06. Git sync is especially valuable for user's large MD corpora. Graph viz is nice-to-have (phase 2).