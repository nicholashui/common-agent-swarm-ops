"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  LOCAL_COSTS_LANDING,
  type CostsLandingView,
} from "../lib/projections/costs-landing";

export function CostsHome({
  view = LOCAL_COSTS_LANDING,
}: Readonly<{ view?: CostsLandingView }>): JSX.Element {
  const [query, setQuery] = useState("");
  const [selectedSwarmId, setSelectedSwarmId] = useState<string | undefined>();
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [simEnabled, setSimEnabled] = useState(true);

  const announce = (message: string): void => setStatusMessage(message);

  const swarms = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.swarmBreakdown;
    return view.swarmBreakdown.filter((row) =>
      row.name.toLowerCase().includes(q),
    );
  }, [query, view.swarmBreakdown]);

  const agents = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.agentUsage;
    return view.agentUsage.filter(
      (row) =>
        row.agent.toLowerCase().includes(q) ||
        row.commonVersion.toLowerCase().includes(q),
    );
  }, [query, view.agentUsage]);

  return (
    <section aria-label="Cost and token analytics" className="costs-home">
      <header className="costs-home__header">
        <div>
          <p className="eyebrow">COSTS</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <div className="costs-home__header-actions">
          <label className="costs-home__search">
            <span className="visually-hidden">Search costs</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={query}
            />
          </label>
          <button className="costs-home__chip" type="button">
            {view.periodLabel} ▾
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

      <div className="costs-home__kpis" aria-label="Cost KPIs">
        {view.kpis.map((kpi) => (
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

      {statusMessage ? (
        <p aria-live="polite" className="costs-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="costs-home__body">
        <div className="costs-home__main">
          <section className="costs-home__panel" aria-labelledby="trend-heading">
            <h2 id="trend-heading">Cost Trend</h2>
            <p className="costs-home__muted">{view.trendNote}</p>
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
            <p className="costs-home__muted">↑ Total spend · Jul 1</p>
          </section>

          <section className="costs-home__panel" aria-labelledby="swarm-heading">
            <h2 id="swarm-heading">Cost by Swarm</h2>
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
            <h2 id="agent-heading">Token Usage by Agent</h2>
            <div className="costs-home__table-wrap">
              <table className="costs-home__table">
                <thead>
                  <tr>
                    <th scope="col">Agent</th>
                    <th scope="col">Common version</th>
                    <th scope="col">Tokens</th>
                    <th scope="col">Cost</th>
                    <th scope="col">In / Out / Tools</th>
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
              ↘ Suggest using CommonReportAgent v2.2 instead (−42% tokens, same
              quality).
            </p>
          </section>
        </div>

        <aside className="costs-home__side">
          <section className="costs-home__panel" aria-labelledby="budget-heading">
            <h2 id="budget-heading">Budget &amp; Alerts</h2>
            <dl className="costs-home__budget">
              <div>
                <dt>Monthly budget</dt>
                <dd>{view.budget.monthly}</dd>
              </div>
              <div>
                <dt>Spent</dt>
                <dd>{view.budget.spent}</dd>
              </div>
              <div>
                <dt>Remaining</dt>
                <dd>{view.budget.remaining}</dd>
              </div>
              <div>
                <dt>Utilization</dt>
                <dd>{view.budget.utilization}</dd>
              </div>
              <div>
                <dt>Alert threshold</dt>
                <dd>{view.budget.alertThreshold}</dd>
              </div>
            </dl>
            <p className="costs-home__projected">{view.budget.projectedEom}</p>
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
            <h2 id="savings-heading">Commons Savings Impact</h2>
            <ul className="costs-home__savings">
              <li>
                <strong>{view.savings.savedThisMonth}</strong>
                <span>Saved this month by using commons</span>
              </li>
              <li>
                <strong>{view.savings.efficiencyGain}</strong>
                <span>Token efficiency gain from commons</span>
              </li>
              <li>
                <strong>{view.savings.ifAllCommons}</strong>
                <span>If all custom → commons-equivalent</span>
              </li>
            </ul>
            <p className="costs-home__muted">
              Upgrade CustomReportAgent → CommonReportAgent v2.2 to realize
              additional savings.
            </p>
          </section>

          <section className="costs-home__panel" aria-labelledby="sim-heading">
            <h2 id="sim-heading">{view.simulator.title}</h2>
            <label className="costs-home__check">
              <input
                checked={simEnabled}
                onChange={(event) => setSimEnabled(event.target.checked)}
                type="checkbox"
              />
              Run CommonReportAgent v2.2 scenario
            </label>
            <p>{view.simulator.scenario}</p>
            {simEnabled ? (
              <p className="costs-home__delta">{view.simulator.projectedDelta}</p>
            ) : null}
            <p className="costs-home__guard" role="note">
              {view.simulator.qualityGuard}
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
            <h2 id="rec-heading">Optimization Recommendations</h2>
            <ul className="costs-home__recs">
              {view.recommendations.map((rec) => (
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
            <h2 id="reports-heading">Reports</h2>
            <ul className="costs-home__reports">
              {view.reports.map((report) => (
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
        {view.safetyNote}
      </p>
      <p className="costs-home__footer">{view.footerNote}</p>
    </section>
  );
}
