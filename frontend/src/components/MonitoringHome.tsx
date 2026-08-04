"use client";

/**
 * @duty MonitoringHome — run monitoring projection (ui_09)
 * @role Inspect runs/traces/freshness from projection; inspect intents via onAction.
 * @controls Tabs, inspect run, freshness indicators.
 * @must Show stale/degraded honestly; recovery only when projection allows.
 * @mustnot Fabricate infrastructure health from unauthorized probes.
 * @redesign docs/frontend_redesign/ui_09_monitoring.md
 */
import React, { useEffect, useState } from "react";
import { InfoTooltip } from './design';
import Link from "next/link";

import {
  type MonitoringLandingView,
  type MonitoringTabId,
  type MonitoringTraceNode,
} from "../lib/projections/monitoring-landing";
import { applyMonitoringSamples } from "../lib/projections/operate-samples";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { cycleOption } from "../lib/ui/local-controls";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";
import { SamplesBanner, SamplesToggle } from "./ui/SamplesToggle";

const MONITORING_FILTER_CYCLES: Readonly<Record<string, readonly string[]>> = {
  environment: ["All envs", "demo", "local", "staging"],
  severity: ["All severities", "info", "warn", "error", "critical"],
  window: ["Last 15m", "Last 1h", "Last 24h", "Last 7d"],
  service: ["All services", "control-plane", "worker", "gateway"],
};

export function MonitoringHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: MonitoringLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const hostEmpty = view.fleet.length === 0 && view.traceTree.length === 0;
  const [showSamples, setShowSamples] = useState(hostEmpty);
  const [tab, setTab] = useState<MonitoringTabId>("traces");
  const [search, setSearch] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const dataView = showSamples ? applyMonitoringSamples(view) : view;
  const [selectedNodeId, setSelectedNodeId] = useState("judge");
  const [filterValues, setFilterValues] = useState<ReadonlyMap<string, string>>(
    () => new Map(dataView.filters.map((filter) => [filter.id, filter.value])),
  );

  useEffect(() => {
    setShowSamples(hostEmpty);
  }, [hostEmpty]);

  useEffect(() => {
    setFilterValues(
      new Map(dataView.filters.map((filter) => [filter.id, filter.value])),
    );
  }, [dataView.filters]);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  return (
    <section aria-label={L(labels, "advanced_monitoring")} className="monitoring-home">
      <header className="monitoring-home__header">
        <div>
          <p className="eyebrow">{dataView.eyebrow}</p>
          <div className="page-title-row">
            <SamplesToggle
              show={showSamples}
              onToggle={() => setShowSamples((v) => !v)}
              labelShow="Show sample monitoring"
              labelHide="Hide sample monitoring"
            />
            <h1>{dataView.title}</h1>
            <InfoTooltip label="About this screen" text={dataView.description} />
          </div>
          <p className="monitoring-home__live" role="status">
            <span aria-hidden="true" className="monitoring-home__live-dot" />
            {dataView.liveLabel}
          </p>
          {showSamples ? (
            <SamplesBanner>
              Sample monitoring on · video demos. Toggle ▦ to hide. Not Host SSE.
            </SamplesBanner>
          ) : null}
        </div>
        <label className="monitoring-home__search">
          <span className="visually-hidden">{L(labels, "search_traces_and_alerts")}</span>
          <input
            onChange={(event) => setSearch(event.target.value)}
            placeholder={dataView.searchPlaceholder}
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
        {dataView.fleet.map((card) => (
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

      {feedback ? (
        <p aria-live="polite" className="monitoring-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="monitoring-home__body">
        <aside aria-label={L(labels, "monitoring_filters")} className="monitoring-home__filters">
          <h2>{L(labels, "filters")}</h2>
          {dataView.filters.map((filter) => {
            const current = filterValues.get(filter.id) ?? filter.value;
            return (
              <button
                aria-label={`${filter.label}: ${current}. Click to cycle.`}
                className="monitoring-home__filter"
                key={filter.id}
                onClick={() => {
                  const options =
                    MONITORING_FILTER_CYCLES[filter.id] ??
                    Array.from(
                      new Set([
                        filter.value,
                        "All",
                        "demo",
                        "local",
                        "Last 1h",
                        "Last 24h",
                      ]),
                    );
                  const next = cycleOption(options, current);
                  setFilterValues((prev) => {
                    const map = new Map(prev);
                    map.set(filter.id, next);
                    return map;
                  });
                  announce(
                    `Monitoring filter “${filter.label}” set to ${next} (local).`,
                  );
                }}
                type="button"
              >
                <span>{filter.label}</span>
                <strong>{current} ▾</strong>
              </button>
            );
          })}
          <p className="monitoring-home__muted">{dataView.eventTypesNote}</p>
        </aside>

        <div className="monitoring-home__main">
          <div
            aria-label={L(labels, "monitoring_tabs")}
            className="monitoring-home__tabs"
            role="tablist"
          >
            {dataView.tabs.map((entry) => (
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
              view={dataView}
              selectedNodeId={selectedNodeId}
              onSelect={setSelectedNodeId}
              onAnnounce={announce}
              search={search}
             labels={labels} />
          ) : null}
          {tab === "alerts" ? (
            <AlertsPanel view={dataView} onAnnounce={announce}  labels={labels} />
          ) : null}
          {tab === "metrics" ? <MetricsPanel view={dataView}  labels={labels} /> : null}
          {tab === "anomalies" ? (
            <AnomaliesPanel view={dataView} onAnnounce={announce}  labels={labels} />
          ) : null}
        </div>
      </div>

      <p className="monitoring-home__footer">{dataView.footerNote}</p>
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
            View in Execute
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
