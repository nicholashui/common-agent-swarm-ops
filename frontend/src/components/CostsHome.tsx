"use client";

/**
 * @duty CostsHome — cost projection filters (ui_19)
 * @role Present cost metrics/filters from projection only.
 * @controls Cost filters, range selectors, refresh via onAction when allowed.
 * @must Treat numbers as redacted projection data, not billing authority.
 * @mustnot Adjust billing or invent spend without host contracts.
 * @redesign docs/frontend_redesign/ui_19_costs.md
 */
import React, { useEffect, useMemo, useState } from "react";
import { InfoTooltip } from './design';
import Link from "next/link";

import {
  type CostsLandingView,
} from "../lib/projections/costs-landing";
import { applyCostsSamples } from "../lib/projections/operate-samples";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { cycleOption } from "../lib/ui/local-controls";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";
import { SamplesBanner, SamplesToggle } from "./ui/SamplesToggle";

const COST_PERIODS = [
  "Last 24 hours",
  "Last 7 days",
  "Last 30 days",
  "This month",
  "All time",
] as const;

export function CostsHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: CostsLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const hostEmpty =
    view.swarmBreakdown.length === 0 && view.agentUsage.length === 0;
  const [showSamples, setShowSamples] = useState(hostEmpty);
  const dataView = showSamples ? applyCostsSamples(view) : view;
  const [query, setQuery] = useState("");
  const [selectedSwarmId, setSelectedSwarmId] = useState<string | undefined>();
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [simEnabled, setSimEnabled] = useState(true);
  const [period, setPeriod] = useState(
    () => dataView.periodLabel || COST_PERIODS[1],
  );

  useEffect(() => {
    setShowSamples(hostEmpty);
  }, [hostEmpty]);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const swarms = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return dataView.swarmBreakdown;
    return dataView.swarmBreakdown.filter((row) =>
      row.name.toLowerCase().includes(q),
    );
  }, [query, dataView.swarmBreakdown]);

  const agents = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return dataView.agentUsage;
    return dataView.agentUsage.filter(
      (row) =>
        row.agent.toLowerCase().includes(q) ||
        row.commonVersion.toLowerCase().includes(q),
    );
  }, [query, dataView.agentUsage]);

  return (
    <section aria-label={L(labels, "cost_and_token_analytics")} className="costs-home">
      <header className="costs-home__header">
        <div>
          <p className="eyebrow">{dataView.eyebrow}</p>
          <div className="page-title-row">
            <SamplesToggle
              show={showSamples}
              onToggle={() => setShowSamples((v) => !v)}
              labelShow="Show sample costs"
              labelHide="Hide sample costs"
            />
            <h1>{dataView.title}</h1>
            <InfoTooltip label="About this screen" text={dataView.description} />
          </div>
          {showSamples ? (
            <SamplesBanner>
              Sample costs on · demo bands only (not billing). Toggle ▦ to hide.
            </SamplesBanner>
          ) : null}
        </div>
        <div className="costs-home__header-actions">
          <label className="costs-home__search">
            <span className="visually-hidden">{L(labels, "search_costs")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={dataView.searchPlaceholder}
              value={query}
            />
          </label>
          <button
            aria-label={`Cost period: ${period}. Click to cycle.`}
            className="costs-home__chip"
            onClick={() => {
              const options = dataView.periodLabel
                ? [
                    dataView.periodLabel,
                    ...COST_PERIODS.filter((p) => p !== dataView.periodLabel),
                  ]
                : [...COST_PERIODS];
              const next = cycleOption(options, period);
              setPeriod(next);
              announce(`Cost period set to ${next} (local presentation filter).`);
            }}
            type="button"
          >
            {period} ▾
          </button>
          <button
            className="costs-home__action costs-home__action--primary"
            onClick={() =>
              announce(
                "Export report requires an authorized finance/export action.",
              )
            }
            type="button"
          >
            Export report
          </button>
        </div>
      </header>

      <div className="costs-home__kpis" aria-label={L(labels, "cost_kpis")}>
        {dataView.kpis.map((kpi) => (
          <article
            className={`costs-home__kpi costs-home__kpi--${kpi.tone}`}
            key={kpi.id}
          >
            <p>{kpi.label}</p>
            <strong>{kpi.value}</strong>
            <span>{kpi.detail}</span>
          </article>
        ))}
      </div>

      {feedback ? (
        <p aria-live="polite" className="costs-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="costs-home__body">
        <div className="costs-home__main">
          <section className="costs-home__panel" aria-labelledby="trend-heading">
            <h2 id="trend-heading">{L(labels, "cost_trend")}</h2>
            <p className="costs-home__muted">{dataView.trendNote}</p>
            <div className="costs-home__chart" aria-hidden="true">
              <i style={{ height: "42%" }} />
              <i style={{ height: "48%" }} />
              <i style={{ height: "55%" }} />
              <i style={{ height: "52%" }} />
              <i style={{ height: "68%" }} />
              <i style={{ height: "74%" }} />
              <i style={{ height: "70%" }} />
              <i style={{ height: "82%" }} />
            </div>
            <p className="costs-home__muted">{L(labels, "total_spend_jul_1")}</p>
          </section>

          <section className="costs-home__panel" aria-labelledby="swarm-heading">
            <h2 id="swarm-heading">{L(labels, "cost_by_swarm")}</h2>
            <ul className="costs-home__bars">
              {swarms.map((row) => (
                <li key={row.id}>
                  <button
                    className={
                      selectedSwarmId === row.id
                        ? "costs-home__bar-row costs-home__bar-row--active"
                        : "costs-home__bar-row"
                    }
                    onClick={() => {
                      setSelectedSwarmId(row.id);
                      announce(
                        `Drill to ${row.name} per-agent costs when activity projections connect.`,
                      );
                    }}
                    type="button"
                  >
                    <span className="costs-home__bar-label">
                      <strong>{row.name}</strong>
                      <em>
                        {row.spend} · {row.tokens}
                      </em>
                    </span>
                    <span className="costs-home__bar-track">
                      <i style={{ width: `${row.sharePercent}%` }} />
                    </span>
                  </button>
                </li>
              ))}
            </ul>
            <p className="costs-home__muted">
              Click swarm → drill to per-agent costs · token breakdown
              (input/output/tool calls).
            </p>
            <Link className="costs-home__linkish" href="/activity">
              Open activity with cost filters →
            </Link>
          </section>

          <section className="costs-home__panel" aria-labelledby="agent-heading">
            <h2 id="agent-heading">{L(labels, "token_usage_by_agent")}</h2>
            <div className="costs-home__table-wrap">
              <table className="costs-home__table">
                <thead>
                  <tr>
                    <th scope="col">{L(labels, "agent")}</th>
                    <th scope="col">{L(labels, "common_version")}</th>
                    <th scope="col">{L(labels, "tokens")}</th>
                    <th scope="col">{L(labels, "cost")}</th>
                    <th scope="col">{L(labels, "in_out_tools")}</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((row) => (
                    <tr key={row.id}>
                      <td>
                        <strong>{row.agent}</strong>
                      </td>
                      <td>{row.commonVersion}</td>
                      <td>{row.tokens}</td>
                      <td>{row.cost}</td>
                      <td>
                        {row.inputShare} / {row.outputShare} / {row.toolShare}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="costs-home__hint" role="status">
              ↘ Suggest using video.editor v2.2 instead (−42% tokens, same
              quality).
            </p>
          </section>
        </div>

        <aside className="costs-home__side">
          <section className="costs-home__panel" aria-labelledby="budget-heading">
            <h2 id="budget-heading">{L(labels, "budget_alerts")}</h2>
            <dl className="costs-home__budget">
              <div>
                <dt>{L(labels, "monthly_budget")}</dt>
                <dd>{dataView.budget.monthly}</dd>
              </div>
              <div>
                <dt>{L(labels, "spent")}</dt>
                <dd>{dataView.budget.spent}</dd>
              </div>
              <div>
                <dt>{L(labels, "remaining")}</dt>
                <dd>{dataView.budget.remaining}</dd>
              </div>
              <div>
                <dt>{L(labels, "utilization")}</dt>
                <dd>{dataView.budget.utilization}</dd>
              </div>
              <div>
                <dt>{L(labels, "alert_threshold")}</dt>
                <dd>{dataView.budget.alertThreshold}</dd>
              </div>
            </dl>
            <p className="costs-home__projected">{dataView.budget.projectedEom}</p>
            <button
              className="costs-home__action"
              onClick={() =>
                announce(
                  "Set/edit budget requires an authorized finance action — no client-created budget authority.",
                )
              }
              type="button"
            >
              Edit budget
            </button>
          </section>

          <section className="costs-home__panel" aria-labelledby="savings-heading">
            <h2 id="savings-heading">{L(labels, "commons_savings_impact")}</h2>
            <ul className="costs-home__savings">
              <li>
                <strong>{dataView.savings.savedThisMonth}</strong>
                <span>{L(labels, "saved_this_month_by_using_commons")}</span>
              </li>
              <li>
                <strong>{dataView.savings.efficiencyGain}</strong>
                <span>{L(labels, "token_efficiency_gain_from_commons")}</span>
              </li>
              <li>
                <strong>{dataView.savings.ifAllCommons}</strong>
                <span>{L(labels, "if_all_custom_commons_equivalent")}</span>
              </li>
            </ul>
            <p className="costs-home__muted">
              Upgrade video.copywriter → video.editor v2.2 to realize
              additional savings.
            </p>
          </section>

          <section className="costs-home__panel" aria-labelledby="sim-heading">
            <h2 id="sim-heading">{dataView.simulator.title}</h2>
            <label className="costs-home__check">
              <input
                checked={simEnabled}
                onChange={(event) => setSimEnabled(event.target.checked)}
                type="checkbox"
              />
              Run video.editor v2.2 scenario
            </label>
            <p>{dataView.simulator.scenario}</p>
            {simEnabled ? (
              <p className="costs-home__delta">{dataView.simulator.projectedDelta}</p>
            ) : null}
            <p className="costs-home__guard" role="note">
              {dataView.simulator.qualityGuard}
            </p>
            <button
              className="costs-home__action costs-home__action--primary"
              onClick={() =>
                announce(
                  "Apply recommendation requires proposal + approval stages. Quality gates cannot be silently weakened.",
                )
              }
              type="button"
            >
              Apply recommendation
            </button>
          </section>

          <section className="costs-home__panel" aria-labelledby="rec-heading">
            <h2 id="rec-heading">{L(labels, "optimization_recommendations")}</h2>
            <ul className="costs-home__recs">
              {dataView.recommendations.map((rec) => (
                <li key={rec.id}>
                  <strong>{rec.title}</strong>
                  <p>{rec.body}</p>
                  <span className="costs-home__delta">{rec.savings}</span>
                  <small>{rec.qualityNote}</small>
                </li>
              ))}
            </ul>
          </section>

          <section className="costs-home__panel" aria-labelledby="reports-heading">
            <h2 id="reports-heading">{L(labels, "reports")}</h2>
            <ul className="costs-home__reports">
              {dataView.reports.map((report) => (
                <li key={report}>
                  <button
                    className="costs-home__linkish"
                    onClick={() =>
                      announce(
                        `“${report}” requires an authorized export/report action.`,
                      )
                    }
                    type="button"
                  >
                    {report}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </div>

      <p className="costs-home__safety" role="note">
        {dataView.safetyNote}
      </p>
      <p className="costs-home__footer">{dataView.footerNote}</p>
    </section>
  );
}
