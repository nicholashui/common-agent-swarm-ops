/**
 * Local Eval & Self-Improvement fixture for ui_11_eval.md / .svg.
 * Presentation-only until eval/proposal projections connect.
 * Passing eval does not publish versions or authorize rollout.
 */

import type { ScreenLabels } from "./screen-labels";

export interface EvalScorecard {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly trend: string;
  readonly tone: "green" | "indigo" | "amber" | "violet";
}

export interface EvalProposalRow {
  readonly id: string;
  readonly target: string;
  readonly impact: string;
  readonly traces: string;
  readonly layers: string;
  readonly status: string;
}

export interface EvalHistoryItem {
  readonly id: string;
  readonly title: string;
  readonly beforeAfter: string;
  readonly metrics: string;
}

export interface EvalAbExperiment {
  readonly id: string;
  readonly title: string;
  readonly result: string;
  readonly recommendation: string;
}

export interface EvalLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly scorecards: readonly EvalScorecard[];
  readonly layerNote: string;
  readonly trendLabels: readonly string[];
  readonly insights: readonly {
    readonly id: string;
    readonly title: string;
    readonly body: string;
  }[];
  readonly proposals: readonly EvalProposalRow[];
  readonly campaignNote: string;
  readonly history: readonly EvalHistoryItem[];
  readonly experiments: readonly EvalAbExperiment[];
  readonly evidenceNote: string;
  readonly footerNote: string;
}

export const LOCAL_EVAL_LANDING: EvalLandingView = {
  labels: {
    "search_commons_and_proposals": "Search commons and proposals",
    "score_trends_l1_l2_l3": "Score Trends (L1 / L2 / L3)",
    "l1_validation_l2_l3_never_masked_by_average": "↑ L1 validation · L2/L3 never masked by average",
    "meta_critic_insights": "Meta-Critic Insights",
    "proposal_queue": "Proposal Queue",
    "select": "Select",
    "target_common": "Target common",
    "expected_impact": "Expected impact",
    "supporting_traces": "Supporting traces",
    "l1_l2_l3": "L1 / L2 / L3",
    "status": "Status",
    "actions": "Actions",
    "proposal_review_diff_impact": "Proposal Review — Diff + Impact",
    "campaign_launcher": "Campaign Launcher",
    "improvement_history_a_b_results": "Improvement History & A/B Results",
    "merged_proposals_before_after": "Merged proposals (before → after)",
    "a_b_experiments": "A/B Experiments",
    "eval_and_self_improvement_dashboard": "Eval and self-improvement dashboard",
    "eval_scorecards": "Eval scorecards",
    "proposal_review": "Proposal review",
  },
  eyebrow: "EVAL",
  title: "Eval & Self-Improvement Dashboard",
  description:
    "Evidence-based L1/L2/L3 quality · improvement campaigns · meta-critic insights.",
  searchPlaceholder: "Search commons, proposals…",
  scorecards: [
    {
      id: "success",
      label: "Global success",
      value: "93.4%",
      trend: "↑ 1.2%",
      tone: "green",
    },
    {
      id: "efficiency",
      label: "Token efficiency",
      value: "+7%",
      trend: "vs last month",
      tone: "indigo",
    },
    {
      id: "verifier",
      label: "Verifier pass rate",
      value: "97%",
      trend: "L2 held-out",
      tone: "violet",
    },
    {
      id: "merged",
      label: "Proposals merged /mo",
      value: "37",
      trend: "meta-critic assisted",
      tone: "amber",
    },
    {
      id: "heldout",
      label: "Held-out coverage",
      value: "61%",
      trend: "dev vs held-out split",
      tone: "indigo",
    },
  ],
  layerNote:
    "Aggregate scores never hide a failed lower-layer gate. L1 = all required fields; L2 = rubric + threshold + evidence; L3 = preference vs named baseline.",
  trendLabels: ["L1 validation", "L2 rubric", "L3 preference"],
  insights: [
    {
      id: "i1",
      title: "Top failure mode",
      body: "Groundedness below 0.9 on report synthesis when citations missing.",
    },
    {
      id: "i2",
      title: "Token waste hotspot",
      body: "Trend pre-filter re-runs on already-verified chunks (+18% tokens).",
    },
    {
      id: "i3",
      title: "Suggested pattern change",
      body: "Add structured verification step earlier in Parallel + Verify branches.",
    },
  ],
  proposals: [
    {
      id: "p1",
      target: "video.editor → v3.0",
      impact: "+18% ↓ hallucination",
      traces: "2.1k traces",
      layers: "L1 pass · L2 0.91 · L3 pending",
      status: "ready for review",
    },
    {
      id: "p2",
      target: "video.analyst → v2.5",
      impact: "+4.2% success",
      traces: "890 traces",
      layers: "L1 pass · L2 0.88 · L3 n/a",
      status: "awaiting review",
    },
    {
      id: "p3",
      target: "video.webresearch → v2.2",
      impact: "−9% tokens",
      traces: "1.4k traces",
      layers: "L1 pass · L2 0.94",
      status: "meta-critic draft",
    },
    {
      id: "p4",
      target: "video.trendintelligence → v2.0",
      impact: "+5% quality",
      traces: "640 traces",
      layers: "L1 pass · L2 0.86 · held-out",
      status: "needs more evidence",
    },
  ],
  campaignNote:
    "Select underperforming commons → run batch eval → auto-generate proposals. A passing evaluation does not publish a common version or authorize rollout.",
  history: [
    {
      id: "h1",
      title: "video.judge v2.9 → v3.0",
      beforeAfter: "pass 85% → 97%",
      metrics: "graph rev retained · canary complete",
    },
    {
      id: "h2",
      title: "video.webresearch v2.0 → v2.1",
      beforeAfter: "avg tok 780 → 612",
      metrics: "rollback plan retained",
    },
  ],
  experiments: [
    {
      id: "e1",
      title: "video.editor v3.0 vs v2.9",
      result: "v3.0 leads · p<0.01 · 1.2k samples each",
      recommendation: "Promote winner requires proposal + approval + canary stages",
    },
  ],
  evidenceNote:
    "Each result identifies Common version, graph revision, task/artifact refs, model/tool config, benchmark case, input provenance, retry/iteration, and held-out vs development classification.",
  footerNote:
    "Local preview eval dashboard · redacted evidence only · Approve / Batch Eval / Promote winner require authorized governance actions (proposal → approval → canary → rollback).",
};
