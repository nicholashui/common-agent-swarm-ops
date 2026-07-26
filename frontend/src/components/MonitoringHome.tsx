"use client";

import React, { useState } from "react";
import Link from "next/link";

import {
  type MonitoringLandingView,
  type MonitoringTabId,
  type MonitoringTraceNode,
} from "../lib/projections/monitoring-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function MonitoringHome({
  view }: Readonly<{ view: MonitoringLandingView }>): JSX.Element {
  const labels = view.labels;
  const [tab, setTab] = useState<MonitoringTabId>("traces");
  const [search, setSearch] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [selectedNodeId, setSelectedNodeId] = useState("pred");

  const announce = (message: string): void => setStatusMessage(message);

  return (
    <section aria-label={L(labels, "advanced_monitoring")} className="monitoring-home">
      <header className="monitoring-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
          <p className="monitoring-home__live" role="status">
            <span aria-hidden="true" className="monitoring-home__live-dot" />
            {view.liveLabel}
          </p>
        </div>
        <label className="monitoring-home__search">
          <span className="visually-hidden">{L(labels, "search_traces_and_alerts")}</span>
          <input
            onChange={(event) => setSearch(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={search}
          />
        </label>
      </header>

      <div
        aria-live="polite"
        className="monitoring-home__fleet"
        role="region"
        aria-label={L(labels, "live_fleet_cards")}
      >
        {view.fleet.map((card) => (
          <article
            className={`monitoring-home__fleet-card monitoring-home__fleet-card--${card.tone}`}
            key={card.id}
          >
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.detail}</span>
          </article>
        ))}
      </div>

      {statusMessage ? (
        <p aria-live="polite" className="monitoring-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="monitoring-home__body">
        <aside aria-label={L(labels, "monitoring_filters")} className="monitoring-home__filters">
          <h2>{L(labels, "filters")}</h2>
          {view.filters.map((filter) => (
            <button className="monitoring-home__filter" key={filter.id} type="button">
              <span>{filter.label}</span>
              <strong>{filter.value} ▾</strong>
            </button>
          ))}
          <p className="monitoring-home__muted">{view.eventTypesNote}</p>
        </aside>

        <div className="monitoring-home__main">
          <div
            aria-label={L(labels, "monitoring_tabs")}
            className="monitoring-home__tabs"
            role="tablist"
          >
            {view.tabs.map((entry) => (
              <button
                aria-selected={tab === entry.id}
                className={
                  tab === entry.id
                    ? "monitoring-home__tab monitoring-home__tab--active"
                    : "monitoring-home__tab"
                }
                key={entry.id}
                onClick={() => setTab(entry.id)}
                role="tab"
                type="button"
              >
                {entry.label}
              </button>
            ))}
          </div>

          {tab === "traces" ? (
            <TracesPanel
              view={view}
              selectedNodeId={selectedNodeId}
              onSelect={setSelectedNodeId}
              onAnnounce={announce}
              search={search}
             labels={labels} />
          ) : null}
          {tab === "alerts" ? (
            <AlertsPanel view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
          {tab === "metrics" ? <MetricsPanel view={view}  labels={labels} /> : null}
          {tab === "anomalies" ? (
            <AnomaliesPanel view={view} onAnnounce={announce}  labels={labels} />
          ) : null}
        </div>
      </div>

      <p className="monitoring-home__footer">{view.footerNote}</p>
    </section>
  );
}

function TracesPanel({
  view,
  selectedNodeId,
  onSelect,
  onAnnounce,
  search,
  labels,
}: Readonly<{
  view: MonitoringLandingView;
  selectedNodeId: string;
  onSelect: (id: string) => void;
  onAnnounce: (message: string) => void;
  search: string;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="monitoring-home__traces">
      <div className="monitoring-home__trace-board">
        <header className="monitoring-home__trace-head">
          <div>
            <h3>{view.traceTitle}</h3>
            <p>{view.traceMeta}</p>
          </div>
          <span className="monitoring-home__timeline-scale">{L(labels, "label_0s")}</span>
        </header>
        <ul className="monitoring-home__tree">
          {view.traceTree.map((node) => (
            <TraceNode
              key={node.id}
              node={node}
              depth={0}
              selectedId={selectedNodeId}
              onSelect={onSelect}
              search={search}
            />
          ))}
        </ul>
      </div>

      <aside aria-label={L(labels, "selected_span")} className="monitoring-home__inspector">
        <h3>{view.selectedSpan.title}</h3>
        <p className="monitoring-home__span-metrics">
          {view.selectedSpan.metrics}
        </p>
        <ul>
          {view.selectedSpan.detailLines.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        <div className="monitoring-home__actions">
          <Link
            className="monitoring-home__action monitoring-home__action--primary"
            href="/registry/agents/local-preview"
          >
            Open Agent Detail →
          </Link>
          <Link className="monitoring-home__action" href="/canvas">
            View in Canvas
          </Link>
          <button
            className="monitoring-home__action"
            onClick={() =>
              onAnnounce(
                "Full span detail requires an authorized trace projection reference.",
              )
            }
            type="button"
          >
            Expand evidence
          </button>
        </div>
      </aside>
    </div>
  );
}

function TraceNode({
  node,
  depth,
  selectedId,
  onSelect,
  search,
}: Readonly<{
  node: MonitoringTraceNode;
  depth: number;
  selectedId: string;
  onSelect: (id: string) => void;
  search: string;
}>): JSX.Element {
  const q = search.trim().toLowerCase();
  const matches =
    q.length === 0 ||
    node.label.toLowerCase().includes(q) ||
    (node.version?.toLowerCase().includes(q) ?? false) ||
    (node.meta?.toLowerCase().includes(q) ?? false);

  return (
    <li>
      <button
        className={
          selectedId === node.id
            ? `monitoring-home__node monitoring-home__node--${node.kind} monitoring-home__node--selected`
            : `monitoring-home__node monitoring-home__node--${node.kind}`
        }
        onClick={() => onSelect(node.id)}
        style={{ marginLeft: depth * 14 }}
        type="button"
      >
        <span className={`monitoring-home__status-dot monitoring-home__status-dot--${node.status}`} />
        <strong>
          {node.label}
          {node.version ? ` ${node.version}` : ""}
        </strong>
        {node.meta ? <span>{node.meta}</span> : null}
        {!matches ? (
          <span className="visually-hidden"> (filtered)</span>
        ) : null}
      </button>
      {node.children?.length ? (
        <ul>
          {node.children.map((child) => (
            <TraceNode
              depth={depth + 1}
              key={child.id}
              node={child}
              onSelect={onSelect}
              search={search}
              selectedId={selectedId}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

function AlertsPanel({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: MonitoringLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="monitoring-home__alerts">
      <div className="monitoring-home__section-head">
        <h3>{L(labels, "alert_rules")}</h3>
        <button
          className="monitoring-home__action monitoring-home__action--primary"
          onClick={() =>
            onAnnounce("New alert rule requires an authorized ops action.")
          }
          type="button"
        >
          + New Rule
        </button>
      </div>
      <div className="monitoring-home__table-wrap">
        <table className="monitoring-home__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "condition")}</th>
              <th scope="col">{L(labels, "action")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "actions")}</th>
            </tr>
          </thead>
          <tbody>
            {view.alertRules.map((rule) => (
              <tr key={rule.id}>
                <td>
                  <strong>{rule.condition}</strong>
                </td>
                <td>{rule.action}</td>
                <td>{rule.enabled ? "Enabled" : "Disabled"}</td>
                <td>
                  <button
                    className="monitoring-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Test notification requires an authorized ops action.",
                      )
                    }
                    type="button"
                  >
                    Test notify
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <AnomaliesPanel view={view} onAnnounce={onAnnounce} compact  labels={labels} />
    </div>
  );
}

function MetricsPanel({
  view,
  labels,
}: Readonly<{
  view: MonitoringLandingView;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="monitoring-home__metrics">
      <h3>{L(labels, "metrics_explorer")}</h3>
      <p className="monitoring-home__muted">{view.metricsTitle}</p>
      <ul className="monitoring-home__metric-bars">
        {view.metricBars.map((bar) => (
          <li key={bar.id}>
            <div className="monitoring-home__metric-label">
              <strong>
                {bar.label} · {bar.value}
              </strong>
            </div>
            <div className="monitoring-home__metric-track">
              <i
                className={`monitoring-home__metric-fill monitoring-home__metric-fill--${bar.tone}`}
                style={{ width: `${bar.percent}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
      <p className="monitoring-home__muted">
        Pre-built common-version impact dashboards · query builder reserved for
        authorized metrics projections.
      </p>
    </div>
  );
}

function AnomaliesPanel({
  view,
  onAnnounce,
  compact = false,
  labels,
}: Readonly<{
  view: MonitoringLandingView;
  onAnnounce: (message: string) => void;
  compact?: boolean;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className={compact ? "monitoring-home__anomalies monitoring-home__anomalies--compact" : "monitoring-home__anomalies"}>
      <h3>{L(labels, "anomaly_feed")}</h3>
      <ul>
        {view.anomalies.map((item) => (
          <li
            className={
              item.highRisk
                ? "monitoring-home__anomaly monitoring-home__anomaly--risk"
                : "monitoring-home__anomaly"
            }
            key={item.id}
          >
            <strong>{item.title}</strong>
            <p>{item.body}</p>
            <span className="monitoring-home__muted">{item.freshness}</span>
            <div className="monitoring-home__actions">
              <button
                className="monitoring-home__action monitoring-home__action--primary"
                onClick={() =>
                  onAnnounce(
                    item.highRisk
                      ? "High-risk anomaly links to gate/audit evidence only — no sensitive material exposed."
                      : "Rollback requires an authorized recovery action with impact confirmation.",
                  )
                }
                type="button"
              >
                {item.highRisk ? "Open audit evidence" : "Rollback v2.0"}
              </button>
              <button
                className="monitoring-home__action"
                onClick={() =>
                  onAnnounce(
                    "Investigate requires an authorized trace/activity projection.",
                  )
                }
                type="button"
              >
                Investigate
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
