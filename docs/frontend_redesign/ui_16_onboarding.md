# NN UI 16: Onboarding, Help & Documentation Spec

**UI ID:** nn_ui_16_onboarding  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui16  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Accelerate adoption and proficiency so users quickly master control of the common layer and collective improvement workflows.

## Layout & Structure
Dedicated onboarding flow (multi-step or modal) + persistent help center page + contextual "?" elements throughout the app.

## Key Components
- Interactive Tour: Steps (Explore Registry → Compose first swarm from common pattern → Run with live view → Review/approve improvement proposal).
- Help Center: Searchable docs (MD/MDX or Strapi), categorized (Concepts, Common Patterns with visuals, Governance, Contribution, API, Troubleshooting). Bilingual.
- AI Help Chat: Contextual or global ("How do I safely rollout a new common version?").
- Sample Guided Projects: Preloaded demo swarms with step-by-step instructions.
- Feedback/Contribution: "Request new common pattern", "Report commons issue" forms.

## Data & API
- Tour progress per user.
- Docs content (CMS or static).
- AI help endpoint (RAG over docs + commons knowledge).
- Sample project templates.

## Interactions
- Tour progress saved; resume later.
- "?" on any screen opens relevant doc or AI chat with context.
- "Use this sample" → loads into composer/canvas with guided overlay.

## Polish & Accessibility
Smooth tour animations. Accessible help content and chat. Bilingual docs and tour. Search in help center is fast and relevant.

## Wireframe Summary
Onboarding: Progress steps with illustrations. Help Center: Search + category cards + article viewer. In-app: "?" icon → popover or drawer with relevant content + "Ask AI" button.

**Implementation Notes:** Leverage your existing YouTube content (bilingual). Tour completion should feel rewarding. AI help (RAG over docs + commons) is powerful for self-service.


## VA-Agent-Swarm Onboarding Alignment

Onboarding must introduce the common model alongside the structures in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md): agents are versioned configurations, graphs run task/dependency/gate lifecycles, artifacts carry lineage/rights/QC/provenance, critique is directed evidence, and releases require quality and approval gates. Domain-adapter onboarding may introduce VA roles, production phases, and templates without implying they are universal requirements.
