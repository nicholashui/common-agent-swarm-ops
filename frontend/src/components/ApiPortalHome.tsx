"use client";

/**
 * @duty ApiPortalHome — API portal projection (ui_15)
 * @role Present portal links and try-it flows only when host-authorized.
 * @controls Portal nav, try-it actions, docs links from projection.
 * @must Fail-closed when try-it contracts are missing.
 * @mustnot Store API keys in browser or invent portal credentials.
 * @redesign docs/frontend_redesign/ui_15_api_portal.md
 */
import React, { useMemo, useState } from "react";
import { InfoTooltip } from './design';
import Link from "next/link";

import {
  type ApiPortalLandingView,
  type ApiPortalNavId,
} from "../lib/projections/api-portal-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function ApiPortalHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: ApiPortalLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [nav, setNav] = useState<ApiPortalNavId>("docs");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(view.selectedEndpointId);
  const [sampleTab, setSampleTab] = useState<"curl" | "python" | "typescript">(
    "curl",
  );
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const endpoints = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.endpoints;
    return view.endpoints.filter(
      (endpoint) =>
        endpoint.path.toLowerCase().includes(q) ||
        endpoint.summary.toLowerCase().includes(q) ||
        endpoint.group.toLowerCase().includes(q) ||
        endpoint.scope.toLowerCase().includes(q),
    );
  }, [query, view.endpoints]);

  const selected =
    endpoints.find((endpoint) => endpoint.id === selectedId) ??
    endpoints[0] ??
    view.endpoints[0];

  const sampleBody =
    sampleTab === "curl"
      ? view.sampleCurl
      : sampleTab === "python"
        ? `from casops import Client  # common-lib

client = Client(token=os.environ["CASOPS_TOKEN"])
run = client.swarms.run(
    "wuxia-short",
    inputs={"as_of": "local-preview"},
    pin_commons=True,
    idempotency_key="7f3c…",
)
# run.run_id, run.events_url — opaque IDs only`
        : `import { createClient } from "@casops/sdk";

const client = createClient({ token: process.env.CASOPS_TOKEN! });
const run = await client.swarms.run("wuxia-short", {
  inputs: { as_of: "local-preview" },
  pinCommons: true,
  idempotencyKey: "7f3c…",
});
// run.runId, run.eventsUrl`;

  return (
    <section aria-label={L(labels, "developer_api_portal")} className="api-portal">
      <header className="api-portal__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <div className="page-title-row">
            <h1>{view.title}</h1>
            <InfoTooltip label="About this screen" text={view.description} />
          </div>
        </div>
        <label className="api-portal__search">
          <span className="visually-hidden">{L(labels, "search_endpoints_and_sdk")}</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={query}
          />
        </label>
      </header>

      {feedback ? (
        <p aria-live="polite" className="api-portal__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="api-portal__body">
        <nav aria-label={L(labels, "api_portal_sections")} className="api-portal__nav">
          {view.nav.map((item) => (
            <button
              aria-current={nav === item.id ? "page" : undefined}
              className={
                nav === item.id
                  ? "api-portal__nav-item api-portal__nav-item--active"
                  : "api-portal__nav-item"
              }
              key={item.id}
              onClick={() => setNav(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
          <label className="api-portal__endpoint-filter">
            <span className="visually-hidden">{L(labels, "filter_endpoints")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={L(labels, "filter_endpoints_2")}
              value={query}
            />
          </label>
          <div className="api-portal__endpoint-groups">
            {(["REGISTRY", "SWARMS", "OPS"] as const).map((group) => {
              const groupEndpoints = endpoints.filter(
                (endpoint) => endpoint.group === group,
              );
              if (groupEndpoints.length === 0) return null;
              return (
                <div key={group}>
                  <p className="api-portal__group-label">{group}</p>
                  <ul>
                    {groupEndpoints.map((endpoint) => (
                      <li key={endpoint.id}>
                        <button
                          className={
                            selected?.id === endpoint.id
                              ? "api-portal__endpoint api-portal__endpoint--active"
                              : "api-portal__endpoint"
                          }
                          onClick={() => {
                            setSelectedId(endpoint.id);
                            setNav("docs");
                          }}
                          type="button"
                        >
                          <span
                            className={`api-portal__method api-portal__method--${endpoint.method.toLowerCase()}`}
                          >
                            {endpoint.method}
                          </span>
                          <code>{endpoint.path}</code>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </nav>

        <div className="api-portal__main">
          {nav === "docs" || nav === "sdks" ? (
            <DocsPanel
              view={view}
              selected={selected}
              sampleTab={sampleTab}
              sampleBody={sampleBody}
              onSampleTab={setSampleTab}
              onAnnounce={announce}
              showSdk={nav === "sdks"}
             labels={labels} />
          ) : null}
          {nav === "tokens" ? (
            <TokensPanel view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {nav === "webhooks" ? (
            <WebhooksPanel view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {nav === "extensibility" ? (
            <ExtensibilityPanel view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
        </div>
      </div>

      <p className="api-portal__footer">{view.footerNote}</p>
    </section>
  );
}

function DocsPanel({
  view,
  selected,
  sampleTab,
  sampleBody,
  onSampleTab,
  onAnnounce,
  showSdk,
  labels,
}: Readonly<{
  view: ApiPortalLandingView;
  selected: ApiPortalLandingView["endpoints"][number] | undefined;
  sampleTab: "curl" | "python" | "typescript";
  sampleBody: string;
  onSampleTab: (tab: "curl" | "python" | "typescript") => void;
  onAnnounce: (message: string) => void;
  showSdk: boolean;
  labels: ScreenLabels;
}>): JSX.Element {
  if (!selected) {
    return (
      <div className="api-portal__empty panel">
        <p>{L(labels, "no_endpoints_match_the_current_filter")}</p>
      </div>
    );
  }

  return (
    <div className="api-portal__docs">
      {showSdk ? (
        <div className="api-portal__sdk-banner">
          <strong>{L(labels, "sdks")}</strong>
          <span>{L(labels, "python_common_lib_typescript_curl_samples")}</span>
        </div>
      ) : null}

      <header className="api-portal__op-head">
        <span
          className={`api-portal__method api-portal__method--${selected.method.toLowerCase()}`}
        >
          {selected.method}
        </span>
        <code>{selected.path}</code>
        <span className="api-portal__scope">Requires: {selected.scope}</span>
      </header>
      <p>{selected.summary}</p>

      <h3>{L(labels, "parameters")}</h3>
      <ul className="api-portal__params">
        {selected.params.map((param) => (
          <li key={param}>
            <code>{param}</code>
          </li>
        ))}
      </ul>

      <div className="api-portal__sample-tabs" role="tablist" aria-label={L(labels, "code_samples")}>
        {(["curl", "python", "typescript"] as const).map((tab) => (
          <button
            aria-selected={sampleTab === tab}
            className={
              sampleTab === tab
                ? "api-portal__sample-tab api-portal__sample-tab--active"
                : "api-portal__sample-tab"
            }
            key={tab}
            onClick={() => onSampleTab(tab)}
            role="tab"
            type="button"
          >
            {tab === "curl" ? "curl" : tab === "python" ? "Python" : "TypeScript"}
          </button>
        ))}
      </div>

      <div className="api-portal__code-block">
        <div className="api-portal__code-head">
          <span>{L(labels, "request")}</span>
          <button
            className="api-portal__linkish"
            onClick={() =>
              onAnnounce(
                "Copy uses local clipboard when available — sample contains no live secrets.",
              )
            }
            type="button"
          >
            Copy
          </button>
        </div>
        <pre>{sampleBody}</pre>
      </div>

      <div className="api-portal__code-block">
        <div className="api-portal__code-head">
          <span>{L(labels, "response")}</span>
        </div>
        <pre>{view.sampleResponse}</pre>
      </div>

      <div className="api-portal__actions">
        <button
          className="api-portal__action api-portal__action--primary"
          onClick={() =>
            onAnnounce(
              "Try it in sandbox requires current session auth and authorized generated contracts.",
            )
          }
          type="button"
        >
          Try it in sandbox
        </button>
        <button
          className="api-portal__action"
          onClick={() =>
            onAnnounce(
              "OpenAPI spec is served from the server when authorized — scopes/rate limits are server-authoritative.",
            )
          }
          type="button"
        >
          View OpenAPI spec
        </button>
      </div>

      <p className="api-portal__safety" role="note">
        {view.safetyNote}
      </p>
    </div>
  );
}

function TokensPanel({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ApiPortalLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="api-portal__tokens">
      <div className="api-portal__section-head">
        <h2>{L(labels, "api_keys_scopes")}</h2>
        <button
          className="api-portal__action api-portal__action--primary"
          onClick={() =>
            onAnnounce(
              "Create key requires an authorized token service. Value shown once and never re-rendered from storage.",
            )
          }
          type="button"
        >
          + Create key
        </button>
      </div>
      <ul className="api-portal__token-list">
        {view.tokens.map((token) => (
          <li key={token.id}>
            <div>
              <strong>{token.name}</strong>
              <code>{token.masked}</code>
              <span>{token.scopes}</span>
            </div>
            <button
              className="api-portal__action"
              onClick={() =>
                onAnnounce(
                  "Rotate requires an authorized token action. New value shown once.",
                )
              }
              type="button"
            >
              Rotate
            </button>
          </li>
        ))}
      </ul>
      <h3>{L(labels, "rate_limit_usage")}</h3>
      <ul className="api-portal__usage">
        {view.usage.map((item) => (
          <li key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </li>
        ))}
      </ul>
      <p className="api-portal__muted">
        Keys shown once at creation · scopes bound server-side. Also manage from{" "}
        <Link href="/profile">{L(labels, "profile_api_tokens")}</Link>.
      </p>
    </div>
  );
}

function WebhooksPanel({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ApiPortalLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="api-portal__webhooks">
      <div className="api-portal__section-head">
        <h2>{L(labels, "webhooks")}</h2>
        <button
          className="api-portal__action api-portal__action--primary"
          onClick={() =>
            onAnnounce("Create webhook endpoint requires an authorized developer action.")
          }
          type="button"
        >
          + Endpoint
        </button>
      </div>
      <ul className="api-portal__webhook-list">
        {view.webhooks.map((hook) => (
          <li key={hook.id}>
            <div>
              <code>{hook.url}</code>
              <span>
                {hook.event} · {hook.status}
              </span>
            </div>
            <div className="api-portal__actions">
              <button
                className="api-portal__action"
                onClick={() =>
                  onAnnounce(
                    "Test webhook sends a redacted sample payload when authorized.",
                  )
                }
                type="button"
              >
                Test
              </button>
              <button
                className="api-portal__action"
                onClick={() =>
                  onAnnounce("Delivery logs require an authorized developer projection.")
                }
                type="button"
              >
                Logs
              </button>
            </div>
          </li>
        ))}
      </ul>
      <h3>{L(labels, "recent_deliveries")}</h3>
      <ul className="api-portal__deliveries">
        {view.deliveries.map((item) => (
          <li key={item.id}>
            <span>{item.time}</span>
            <strong>{item.event}</strong>
            <span>{item.outcome}</span>
          </li>
        ))}
      </ul>
      <div className="api-portal__secret">
        <h3>{L(labels, "signing_secret")}</h3>
        <code>{view.signingSecretMasked}</code>
        <p className="api-portal__muted">
          Verify signatures · payloads redacted · retries w/ backoff.
        </p>
      </div>
    </div>
  );
}

function ExtensibilityPanel({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: ApiPortalLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="api-portal__extensibility">
      <h2>{L(labels, "extensibility")}</h2>
      <p>
        Guides for custom nodes/tools, runtime adapters (Moltbot, LangGraph,
        etc.), and contribution process for new commons.
      </p>
      <h3>{L(labels, "published_schemas_examples")}</h3>
      <ul className="api-portal__schemas">
        {view.schemas.map((schema) => (
          <li key={schema}>{schema}</li>
        ))}
      </ul>
      <p className="api-portal__va" role="note">
        {view.vaNote}
      </p>
      <div className="api-portal__actions">
        <button
          className="api-portal__action"
          onClick={() =>
            onAnnounce(
              "Adapter guides are static docs until authorized content projections connect.",
            )
          }
          type="button"
        >
          Runtime adapter guide
        </button>
        <Link className="api-portal__action api-portal__action--primary" href="/registry">
          Contribute via Registry →
        </Link>
      </div>
    </div>
  );
}
