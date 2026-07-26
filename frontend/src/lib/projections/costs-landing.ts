/**
 * Local Cost & Token Analytics fixture for ui_19_costs.md / .svg.
 * Presentation-only. Redacted financial bands; no client budget authority.
 * Optimizations cannot silently weaken L1/L2/L3, rights/provenance, or approvals.
 */

import type { ScreenLabels } from "./screen-labels";

export interface CostsKpi {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail: string;
  readonly tone: "indigo" | "green" | "amber" | "violet";
}

export interface CostsSwarmRow {
  readonly id: string;
  readonly name: string;
  readonly spend: string;
  readonly sharePercent: number;
  readonly tokens: string;
}

export interface CostsAgentRow {
  readonly id: string;
  readonly agent: string;
  readonly tokens: string;
  readonly cost: string;
  readonly inputShare: string;
  readonly outputShare: string;
  readonly toolShare: string;
  readonly commonVersion: string;
}

export interface CostsRecommendation {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly savings: string;
  readonly qualityNote: string;
}

export interface CostsLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly periodLabel: string;
  readonly searchPlaceholder: string;
  readonly kpis: readonly CostsKpi[];
  readonly trendNote: string;
  readonly swarmBreakdown: readonly CostsSwarmRow[];
  readonly agentUsage: readonly CostsAgentRow[];
  readonly budget: {
    readonly monthly: string;
    readonly spent: string;
    readonly remaining: string;
    readonly utilization: string;
    readonly alertThreshold: string;
    readonly projectedEom: string;
  };
  readonly savings: {
    readonly savedThisMonth: string;
    readonly efficiencyGain: string;
    readonly ifAllCommons: string;
  };
  readonly recommendations: readonly CostsRecommendation[];
  readonly simulator: {
    readonly title: string;
    readonly scenario: string;
    readonly projectedDelta: string;
    readonly qualityGuard: string;
  };
  readonly reports: readonly string[];
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_COSTS_LANDING: CostsLandingView = {
  labels: {
    "search_costs": "Search costs",
    "cost_trend": "Cost Trend",
    "total_spend_jul_1": "↑ Total spend · Jul 1",
    "cost_by_swarm": "Cost by Swarm",
    "token_usage_by_agent": "Token Usage by Agent",
    "agent": "Agent",
    "common_version": "Common version",
    "tokens": "Tokens",
    "cost": "Cost",
    "in_out_tools": "In / Out / Tools",
    "budget_alerts": "Budget & Alerts",
    "monthly_budget": "Monthly budget",
    "spent": "Spent",
    "remaining": "Remaining",
    "utilization": "Utilization",
    "alert_threshold": "Alert threshold",
    "commons_savings_impact": "Commons Savings Impact",
    "saved_this_month_by_using_commons": "Saved this month by using commons",
    "token_efficiency_gain_from_commons": "Token efficiency gain from commons",
    "if_all_custom_commons_equivalent": "If all custom → commons-equivalent",
    "optimization_recommendations": "Optimization Recommendations",
    "reports": "Reports",
    "cost_and_token_analytics": "Cost and token analytics",
    "cost_kpis": "Cost KPIs",
  },
  eyebrow: "COSTS",
  title: "Cost & Token Analytics",
  description:
    "Token usage, cost attribution, budget alerts & commons savings impact.",
  periodLabel: "Last 30 days",
  searchPlaceholder: "Search swarm, agent, period…",
  kpis: [
    {
      id: "spend",
      label: "Total spend (30d)",
      value: "$1,248",
      detail: "redacted band",
      tone: "indigo",
    },
    {
      id: "tokens",
      label: "Total tokens",
      value: "42.1M",
      detail: "in + out + tools",
      tone: "violet",
    },
    {
      id: "savings",
      label: "Savings from commons",
      value: "$412",
      detail: "vs custom baselines",
      tone: "green",
    },
    {
      id: "cpsr",
      label: "Cost / successful run",
      value: "$0.18",
      detail: "held-out quality retained",
      tone: "amber",
    },
    {
      id: "util",
      label: "Budget utilization",
      value: "78%",
      detail: "within monthly budget",
      tone: "green",
    },
  ],
  trendNote: "↑ Total spend · Jul 1 → today (local preview chart)",
  swarmBreakdown: [
    {
      id: "s1",
      name: "TradingResearch α",
      spend: "$412",
      sharePercent: 33,
      tokens: "12.1M",
    },
    {
      id: "s2",
      name: "ContentPipeline β",
      spend: "$298",
      sharePercent: 24,
      tokens: "9.4M",
    },
    {
      id: "s3",
      name: "DSE Tutor Fleet",
      spend: "$186",
      sharePercent: 15,
      tokens: "6.2M",
    },
    {
      id: "s4",
      name: "LegacyModernizer",
      spend: "$154",
      sharePercent: 12,
      tokens: "5.1M",
    },
    {
      id: "s5",
      name: "Others (4)",
      spend: "$198",
      sharePercent: 16,
      tokens: "9.3M",
    },
  ],
  agentUsage: [
    {
      id: "a1",
      agent: "DataFetcher v2.1",
      tokens: "8.2M",
      cost: "$186",
      inputShare: "62%",
      outputShare: "28%",
      toolShare: "10%",
      commonVersion: "Common v2.1",
    },
    {
      id: "a2",
      agent: "SentimentAgent v1.9",
      tokens: "6.4M",
      cost: "$142",
      inputShare: "55%",
      outputShare: "40%",
      toolShare: "5%",
      commonVersion: "Common v1.9",
    },
    {
      id: "a3",
      agent: "VerifierNode v3.0",
      tokens: "5.1M",
      cost: "$128",
      inputShare: "48%",
      outputShare: "44%",
      toolShare: "8%",
      commonVersion: "Common v3.0",
    },
    {
      id: "a4",
      agent: "CustomReportAgent",
      tokens: "4.8M",
      cost: "$156",
      inputShare: "50%",
      outputShare: "42%",
      toolShare: "8%",
      commonVersion: "Fork of Common v2.3",
    },
  ],
  budget: {
    monthly: "$1,600",
    spent: "$1,248",
    remaining: "$352",
    utilization: "78%",
    alertThreshold: "85%",
    projectedEom: "Projected end-of-month: $1,540 (within budget)",
  },
  savings: {
    savedThisMonth: "$412",
    efficiencyGain: "+11% token efficiency from commons",
    ifAllCommons: "If all custom → commons-equivalent: +$96/mo est.",
  },
  recommendations: [
    {
      id: "r1",
      title: "Suggest using CommonReportAgent v2.2 instead",
      body: "Replace CustomReportAgent fork where compatible.",
      savings: "−42% tokens",
      qualityNote: "Same quality band · L1/L2 gates retained",
    },
    {
      id: "r2",
      title: "Route SentimentAgent cheap model for pre-filter",
      body: "Policy-approved quality-cost routing only.",
      savings: "−18% tokens on pre-filter",
      qualityNote: "Cannot weaken required L2 groundedness",
    },
  ],
  simulator: {
    title: "What-If Simulator",
    scenario:
      "Upgrade CustomReportAgent → CommonReportAgent v2.2 across 19 swarms",
    projectedDelta: "Est. −$96/mo · quality delta 0.0 within held-out band",
    qualityGuard:
      "Optimizations may recommend policy-approved model/routing changes but cannot silently weaken required L1/L2/L3 quality, rights/provenance, or approval controls.",
  },
  reports: [
    "Monthly cost report (CSV)",
    "Chargeback by workspace",
    "Commons efficiency leaderboard",
    "Budget breach history",
  ],
  safetyNote:
    "Cost attribution includes Common version, model/provider/tool, iteration/retry, concurrency, phase/template, artifact/delivery target, and quality/gate outcome (redacted). No client-created budget authority.",
  footerNote:
    "Local preview costs · redacted metrics only · Set budget / Apply recommendation / Export require authorized finance actions.",
};
