# NN UI 19: Cost Governance & Usage Analytics Spec

**UI ID:** nn_ui_19_costs  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui19  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Full financial visibility, budgeting, and optimization tooling so LLM spend (the main variable cost) is transparent and controllable at commons and fleet scale.

## Layout & Structure
Analytics dashboard with breakdown charts + budget cards + simulator. Filters by business, common agent/version, pattern, time.

## Key Components
- Breakdown Charts: By business/pattern/common agent/version/model (stacked bars, pies, trends). Sparklines for quick trends.
- Budget Cards: Current spend vs budget per scope, alert status, remaining. Set/edit budgets.
- What-If Simulator: Select common version update or pattern change → projected cost/quality impact across affected swarms.
- Optimization Recommendations: Meta-critic suggestions with estimated savings and quality delta.
- Reports: Monthly/exportable cost reports, chargeback views, efficiency leaderboards per common component.
- Alerts: Cost threshold breaches with actions (notify, throttle, create proposal for cheaper alternative).

## Data & API
- Cost attribution at fine granularity (run + agent + model + common version).
- Budget CRUD + breach detection.
- What-if simulation engine.
- Forecasting and recommendation endpoints.

## Interactions
- Click chart segment → filter whole dashboard or drill to activity.
- Simulator: Adjust parameters → live updated projection table + "Apply recommendation" button.
- Budget set → impact preview on current spend.

## Polish & Accessibility
Clear financial visualizations (positive/negative deltas color coded). Accessible charts and tables. Export prominent. Bilingual currency/format support if needed.

## Wireframe Summary
Top filters. Left: Budget cards + alerts. Center: Breakdown charts + trends. Right: Simulator panel + recommendations. Bottom: Leaderboards + export.

**Implementation Notes:** Accurate per-common-version cost attribution is powerful for commons optimization. Simulator is high-leverage for safe decision making. Integrate with existing billing APIs where possible.


## VA-Agent-Swarm Cost Alignment

Cost views must attribute budget to the graph/task structure in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md): Common version, model/provider/tool, iteration/retry, concurrency, phase/template, artifact/delivery target, and quality/gate outcome. Optimizations may recommend policy-approved model or routing changes but cannot silently weaken required L1/L2/L3 quality, rights/provenance, or approval controls.
