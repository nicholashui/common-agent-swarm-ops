/**
 * Local monitoring fixture for ui_09_monitoring.md / .svg.
 * Presentation-only until live SSE/trace projections connect.
 * Redacted event summaries only — no host, queue, or raw traces.
 */

export type MonitoringTabId = "traces" | "alerts" | "metrics" | "anomalies";

export interface MonitoringFleetCard {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail: string;
  readonly tone: "indigo" | "green" | "amber" | "rose";
}

export interface MonitoringTraceNode {
  readonly id: string;
  readonly label: string;
  readonly kind: "root" | "group" | "agent" | "verify";
  readonly version?: string;
  readonly status: "success" | "running" | "error" | "self_refine";
  readonly meta?: string;
  readonly children?: readonly MonitoringTraceNode[];
}

export interface MonitoringAlertRule {
  readonly id: string;
  readonly condition: string;
  readonly action: string;
  readonly enabled: boolean;
}

export interface MonitoringAnomaly {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly freshness: string;
  readonly highRisk?: boolean;
}

export interface MonitoringMetricBar {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly percent: number;
  readonly tone: "good" | "mid" | "bad";
}

export interface MonitoringLandingView {
  readonly title: string;
  readonly description: string;
  readonly liveLabel: string;
  readonly searchPlaceholder: string;
  readonly fleet: readonly MonitoringFleetCard[];
  readonly filters: readonly { readonly id: string; readonly label: string; readonly value: string }[];
  readonly tabs: readonly { readonly id: MonitoringTabId; readonly label: string }[];
  readonly traceTitle: string;
  readonly traceMeta: string;
  readonly traceTree: readonly MonitoringTraceNode[];
  readonly selectedSpan: {
    readonly title: string;
    readonly metrics: string;
    readonly detailLines: readonly string[];
  };
  readonly alertRules: readonly MonitoringAlertRule[];
  readonly anomalies: readonly MonitoringAnomaly[];
  readonly metricsTitle: string;
  readonly metricBars: readonly MonitoringMetricBar[];
  readonly eventTypesNote: string;
  readonly footerNote: string;
}

export const LOCAL_MONITORING_LANDING: MonitoringLandingView = {
  title: "Advanced Monitoring, Tracing & Alerts",
  description:
    "Live fleet observability with common-version traces, alert rules, metrics, and anomaly feed.",
  liveLabel: "Live · SSE seq 4421 · as_of now",
  searchPlaceholder: "Search traces, alerts…",
  fleet: [
    {
      id: "running",
      label: "Running swarms",
      value: "12",
      detail: "2 streaming",
      tone: "indigo",
    },
    {
      id: "health",
      label: "Common health",
      value: "94%",
      detail: "12/14 on latest",
      tone: "green",
    },
    {
      id: "burn",
      label: "Cost burn rate",
      value: "$0.18/min",
      detail: "redacted band",
      tone: "amber",
    },
    {
      id: "anomalies",
      label: "Active anomalies",
      value: "3",
      detail: "1 high-risk",
      tone: "rose",
    },
    {
      id: "alerts",
      label: "Alerts firing",
      value: "2",
      detail: "notify + pause",
      tone: "rose",
    },
  ],
  filters: [
    { id: "time", label: "Time range", value: "Last 1 hour" },
    { id: "version", label: "Common version", value: "All" },
    { id: "swarm", label: "Swarm", value: "TradingResearch α" },
    { id: "status", label: "Status", value: "Success" },
  ],
  tabs: [
    { id: "traces", label: "Traces" },
    { id: "alerts", label: "Alerts" },
    { id: "metrics", label: "Metrics" },
    { id: "anomalies", label: "Anomalies" },
  ],
  traceTitle: "Distributed Trace · run-4421",
  traceMeta: "corr a3f9b1c2 · graph rev 12",
  traceTree: [
    {
      id: "root",
      label: "Swarm root",
      kind: "root",
      status: "running",
      children: [
        {
          id: "parallel",
          label: "Parallel group",
          kind: "group",
          status: "success",
          children: [
            {
              id: "data",
              label: "DataFetcher",
              kind: "agent",
              version: "v2.1",
              status: "success",
              meta: "1.2s · tok 612",
            },
            {
              id: "sent",
              label: "Sentiment",
              kind: "agent",
              version: "v1.9",
              status: "success",
              meta: "2.1s · tok 840",
            },
            {
              id: "pred",
              label: "Predictor",
              kind: "agent",
              version: "v2.0",
              status: "success",
              meta: "320ms · tok 640",
            },
          ],
        },
        {
          id: "synth",
          label: "Synthesis + Verify",
          kind: "group",
          status: "self_refine",
          children: [
            {
              id: "ver",
              label: "VerifierNode",
              kind: "verify",
              version: "v3.0",
              status: "self_refine",
              meta: "iter 1 · iter 2 · iter 3 (pass)",
            },
          ],
        },
      ],
    },
  ],
  selectedSpan: {
    title: "Selected span · Predictor v2.0",
    metrics: "Duration 320ms · tokens 640 · cost $0.02",
    detailLines: [
      "Graph revision: 12",
      "Lifecycle: complete",
      "Checkpoint: ck-91",
      "Tool summary: retrieve · 120ms (redacted)",
      "Artifact lineage: evidence bundle · QC pass",
      "Critique/gate: not required",
      "Quality: L1 pass · L2 pass",
    ],
  },
  alertRules: [
    {
      id: "a1",
      condition: "Error rate > 5% on Common v*",
      action: "→ notify Slack · pause swarm",
      enabled: true,
    },
    {
      id: "a2",
      condition: "Cost > $0.50/min per swarm",
      action: "→ notify Telegram · throttle",
      enabled: true,
    },
    {
      id: "a3",
      condition: "Provenance / rights gate failure",
      action: "→ high-risk · link gate/audit evidence",
      enabled: true,
    },
  ],
  anomalies: [
    {
      id: "n1",
      title: "Error spike · CommonReportAgent",
      body: "After v2.1 rollout, error ↑ in 3 swarms.",
      freshness: "as_of 04:12Z · corr b7f2c9d0",
      highRisk: false,
    },
    {
      id: "n2",
      title: "Waiting for critique backlog",
      body: "4 tasks blocked: waiting_for_critique · severity major.",
      freshness: "as_of 04:10Z · corr c1d2e3f4",
      highRisk: false,
    },
    {
      id: "n3",
      title: "Release provenance failure",
      body: "High-risk: provenance/consent gate failed — open audit evidence only.",
      freshness: "as_of 04:08Z · corr d4e5f6a7",
      highRisk: true,
    },
  ],
  metricsTitle: "Success % by common version",
  metricBars: [
    { id: "m1", label: "v3.0", value: "97%", percent: 97, tone: "good" },
    { id: "m2", label: "v2.9", value: "91%", percent: 91, tone: "good" },
    { id: "m3", label: "v2.1", value: "74%", percent: 74, tone: "mid" },
  ],
  eventTypesNote:
    "Recognizes redacted lifecycle events: task-state, artifact, critique, approval, budget, metric, tool-completed, production-phase, recoverable-error — sequence + correlation only.",
  footerNote:
    "Local preview monitoring · no host/queue/provider internals · Rollback/Investigate/New Rule require authorized ops actions. High-risk release/rights alerts link to gate/audit evidence only.",
};
