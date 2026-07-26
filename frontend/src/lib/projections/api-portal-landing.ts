/**
 * Local Developer / API Portal fixture for ui_15_api_portal.md / .svg.
 * Presentation-only. OpenAPI-driven docs chrome; tokens/webhooks redacted.
 * VA production semantics labeled as adapter/reference, not deployed endpoints.
 */

import type { ScreenLabels } from "./screen-labels";

export type ApiPortalNavId =
  | "docs"
  | "sdks"
  | "tokens"
  | "webhooks"
  | "extensibility";

export interface ApiEndpointItem {
  readonly id: string;
  readonly method: "GET" | "POST" | "PUT" | "DELETE";
  readonly path: string;
  readonly group: "REGISTRY" | "SWARMS" | "OPS";
  readonly summary: string;
  readonly scope: string;
  readonly params: readonly string[];
}

export interface ApiTokenRow {
  readonly id: string;
  readonly name: string;
  readonly masked: string;
  readonly scopes: string;
}

export interface ApiWebhookRow {
  readonly id: string;
  readonly url: string;
  readonly event: string;
  readonly status: string;
}

export interface ApiDeliveryRow {
  readonly id: string;
  readonly time: string;
  readonly event: string;
  readonly outcome: string;
}

export interface ApiPortalLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly nav: readonly { readonly id: ApiPortalNavId; readonly label: string }[];
  readonly endpoints: readonly ApiEndpointItem[];
  readonly selectedEndpointId: string;
  readonly sampleCurl: string;
  readonly sampleResponse: string;
  readonly tokens: readonly ApiTokenRow[];
  readonly usage: readonly { readonly label: string; readonly value: string }[];
  readonly webhooks: readonly ApiWebhookRow[];
  readonly deliveries: readonly ApiDeliveryRow[];
  readonly signingSecretMasked: string;
  readonly schemas: readonly string[];
  readonly vaNote: string;
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_API_PORTAL_LANDING: ApiPortalLandingView = {
  labels: {
    "search_endpoints_and_sdk": "Search endpoints and SDK",
    "filter_endpoints": "Filter endpoints",
    "no_endpoints_match_the_current_filter": "No endpoints match the current filter.",
    "sdks": "SDKs",
    "python_common_lib_typescript_curl_samples": "Python (common-lib) · TypeScript · curl samples",
    "parameters": "Parameters",
    "request": "Request",
    "response": "Response",
    "api_keys_scopes": "API Keys & Scopes",
    "rate_limit_usage": "Rate Limit & Usage",
    "profile_api_tokens": "Profile → API Tokens",
    "webhooks": "Webhooks",
    "recent_deliveries": "Recent deliveries",
    "signing_secret": "Signing secret",
    "extensibility": "Extensibility",
    "published_schemas_examples": "Published schemas & examples",
    "filter_endpoints_2": "Filter endpoints…",
    "developer_api_portal": "Developer API portal",
    "api_portal_sections": "API portal sections",
    "code_samples": "Code samples",
  },
  eyebrow: "DEVELOPER / API PORTAL",
  title: "Developer / API Portal",
  description:
    "Programmatic access to Registry, swarm runs & ops · OpenAPI-driven docs.",
  searchPlaceholder: "Search endpoints, SDK…",
  nav: [
    { id: "docs", label: "Docs" },
    { id: "sdks", label: "SDKs" },
    { id: "tokens", label: "Tokens" },
    { id: "webhooks", label: "Webhooks" },
    { id: "extensibility", label: "Extensibility" },
  ],
  endpoints: [
    {
      id: "reg-agents",
      method: "GET",
      path: "/api/v1/commons/agents",
      group: "REGISTRY",
      summary: "List common agents (filterable, redacted metrics).",
      scope: "registry.read",
      params: ["q", "domain", "cursor"],
    },
    {
      id: "reg-agent",
      method: "GET",
      path: "/api/v1/commons/agents/{id}",
      group: "REGISTRY",
      summary: "Read common agent version projection.",
      scope: "registry.read",
      params: ["id", "version"],
    },
    {
      id: "reg-propose",
      method: "POST",
      path: "/api/v1/commons/agents/{id}/proposals",
      group: "REGISTRY",
      summary: "Submit improvement proposal (evidence refs only).",
      scope: "registry.propose",
      params: ["id", "diff_ref", "trace_refs"],
    },
    {
      id: "swarm-run",
      method: "POST",
      path: "/api/v1/swarms/{id}/run",
      group: "SWARMS",
      summary:
        "Start a swarm run with pinned common versions. Returns run ID and SSE stream URL.",
      scope: "swarm:run",
      params: ["id", "inputs", "idempotency_key"],
    },
    {
      id: "swarm-graph",
      method: "GET",
      path: "/api/v1/swarms/{id}/graph",
      group: "SWARMS",
      summary: "Read graph revision + pinned commons.",
      scope: "swarm.read",
      params: ["id", "revision"],
    },
    {
      id: "swarm-events",
      method: "GET",
      path: "/api/v1/swarms/{id}/runs/{run_id}/events",
      group: "SWARMS",
      summary: "Redacted SSE event stream (lifecycle, metrics, gates).",
      scope: "swarm.read",
      params: ["id", "run_id", "after_seq"],
    },
    {
      id: "ops-approve",
      method: "POST",
      path: "/api/v1/approvals/{approval_id}/decide",
      group: "OPS",
      summary: "Gate decision (server-authorized command only).",
      scope: "approval.decide",
      params: ["approval_id", "decision", "comment"],
    },
    {
      id: "ops-rollout",
      method: "PUT",
      path: "/api/v1/evolution/rollouts/{id}",
      group: "OPS",
      summary: "Update rollout/canary state with impact analysis refs.",
      scope: "rollout.write",
      params: ["id", "action", "scope_ref"],
    },
  ],
  selectedEndpointId: "swarm-run",
  sampleCurl: `$ curl -X POST https://api.caso.local/v1/swarms/\\\\
  trading-alpha/run \\\\
  -H "Authorization: Bearer $CASOPS_TOKEN" \\\\
  -H "Idempotency-Key: 7f3c…" \\\\
  -d '{"inputs":{"as_of":"local-preview"},"pin_commons":true}'
# scopes enforced server-side · token never in URL
# opaque IDs only · no raw prompts or tool payloads`,
  sampleResponse: `{
  "run_id": "run-4421",
  "status": "accepted",
  "events_url": "/api/v1/swarms/trading-alpha/runs/run-4421/events",
  "pinned_commons": ["VerifierNode@v3.0", "DataFetcher@v2.1"],
  "graph_revision": "r-12"
}`,
  tokens: [
    {
      id: "k1",
      name: "prod-key",
      masked: "caso_sk_••••••••4f2a",
      scopes: "swarm:run",
    },
    {
      id: "k2",
      name: "ci-readonly",
      masked: "caso_sk_••••••••9b13",
      scopes: "registry.read · activity.read",
    },
  ],
  usage: [
    { label: "Requests today", value: "12.4k" },
    { label: "Error rate", value: "0.4%" },
    { label: "p95 latency", value: "180ms" },
  ],
  webhooks: [
    {
      id: "w1",
      url: "https://hooks.mysite/caso",
      event: "run.completed",
      status: "Active",
    },
  ],
  deliveries: [
    { id: "d1", time: "04:12", event: "run.completed", outcome: "2xx" },
    { id: "d2", time: "03:58", event: "rollout.done", outcome: "2xx" },
    { id: "d3", time: "03:44", event: "run.completed", outcome: "retry" },
  ],
  signingSecretMasked: "whsec_••••••••  (HMAC-SHA256)",
  schemas: [
    "Common Agent version",
    "Swarm graph revision",
    "Task / lifecycle states",
    "Artifacts / handoffs",
    "Critiques",
    "L1 / L2 / L3 quality gates",
    "Approvals",
    "Provenance references",
    "Redacted SSE events",
  ],
  vaNote:
    "VA production semantics are documented as an adapter/reference mapping — not as already deployed common-agent-swarm-ops endpoints. Commands: create/launch production, gate decision, critique submission, retry/skip, artifact detail, router configuration, live events.",
  safetyNote:
    "Docs generated from server OpenAPI · scopes/rate limits authoritative server-side. Keys shown once at creation · scopes bound server-side. Verify webhook signatures · payloads redacted · retries with backoff. Examples use opaque IDs and omit credentials, raw tool requests, private prompts, and unredacted artifact data.",
  footerNote:
    "Local preview API portal · Try it / Create key / Test webhook require authorized developer actions within current session context.",
};
