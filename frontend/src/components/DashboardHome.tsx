import React from "react";
import Link from "next/link";

import {
  LOCAL_DASHBOARD_LANDING,
  type DashboardLandingView,
  type DashboardRecentRun,
  type DashboardRunningSwarm,
} from "../lib/projections/dashboard-landing";
import { StatusBadge } from "./design";

export function DashboardHome({
  view = LOCAL_DASHBOARD_LANDING,
}: Readonly<{ view?: DashboardLandingView }>): JSX.Element {
  return (
    <section aria-label="Dashboard projection" className="dashboard-home">
      <header className="dashboard-home__header">
        <div>
          <p className="eyebrow">DASHBOARD</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <p
          className={
            view.stale
              ? "dashboard-home__freshness dashboard-home__freshness--stale"
              : "dashboard-home__freshness"
          }
          role="status"
        >
          <span aria-hidden="true" className="dashboard-home__freshness-dot" />
          {view.freshnessLabel}
          <span className="dashboard-home__as-of"> · as_of {view.asOf}</span>
        </p>
      </header>

      <section aria-labelledby="common-health-heading" className="dashboard-home__section">
        <h2 className="dashboard-home__section-label" id="common-health-heading">
          Common Health
        </h2>
        <div className="dashboard-home__stats">
          {view.commonHealth.map((card) => (
            <article
              className={`dashboard-stat dashboard-stat--${card.tone}`}
              key={card.id}
            >
              <p className="dashboard-stat__label">{card.label}</p>
              <p className="dashboard-stat__value">{card.value}</p>
              <p className="dashboard-stat__detail">{card.detail}</p>
              <p className="dashboard-stat__trend">{card.trend}</p>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="quick-actions-heading" className="dashboard-home__section">
        <h2 className="dashboard-home__section-label" id="quick-actions-heading">
          Quick Common Actions
        </h2>
        <div className="dashboard-home__actions">
          {view.quickActions.map((action) => (
            <Link
              className={
                action.primary
                  ? "dashboard-action dashboard-action--primary"
                  : "dashboard-action"
              }
              href={action.href}
              key={action.id}
            >
              <strong>{action.label}</strong>
              <span>{action.description}</span>
            </Link>
          ))}
        </div>
      </section>

      <div className="dashboard-home__split">
        <section aria-labelledby="running-heading" className="dashboard-home__section">
          <div className="dashboard-home__section-head">
            <h2 className="dashboard-home__section-label" id="running-heading">
              Running Now
            </h2>
            <Link className="dashboard-home__section-link" href="/canvas">
              Open canvas
            </Link>
          </div>
          {view.runningSwarms.length === 0 ? (
            <div className="dashboard-empty panel">
              <p>No swarms running. Start one from Common Patterns.</p>
              <Link className="dashboard-home__section-link" href="/composer">
                Compose from patterns →
              </Link>
            </div>
          ) : (
            <ul className="dashboard-running">
              {view.runningSwarms.map((swarm) => (
                <RunningSwarmCard key={swarm.id} swarm={swarm} />
              ))}
            </ul>
          )}
        </section>

        <section aria-labelledby="recent-heading" className="dashboard-home__section">
          <div className="dashboard-home__section-head">
            <h2 className="dashboard-home__section-label" id="recent-heading">
              Recent Activity
            </h2>
            <Link className="dashboard-home__section-link" href="/activity">
              View all activity →
            </Link>
          </div>
          <div className="dashboard-recent panel">
            <div className="dashboard-recent__head" aria-hidden="true">
              <span>Time</span>
              <span>Swarm</span>
              <span>Commons</span>
              <span>Status</span>
              <span>Duration</span>
              <span>Cost</span>
            </div>
            <ul className="dashboard-recent__list">
              {view.recentRuns.map((run) => (
                <RecentRunRow key={run.id} run={run} />
              ))}
            </ul>
          </div>
        </section>
      </div>

      <section aria-labelledby="insights-heading" className="dashboard-home__section">
        <h2 className="dashboard-home__section-label" id="insights-heading">
          Common Impact Insights
        </h2>
        <div className="dashboard-insights">
          {view.insights.map((insight) => (
            <article
              className={`dashboard-insight dashboard-insight--${insight.tone}`}
              key={insight.id}
            >
              <h3>{insight.title}</h3>
              <p>{insight.body}</p>
              <div className="dashboard-insight__actions">
                <Link
                  className="dashboard-insight__button"
                  href={
                    insight.tone === "opportunity" ? "/operations" : "/registry"
                  }
                >
                  {insight.primaryActionLabel}
                </Link>
                <Link
                  className="dashboard-insight__button dashboard-insight__button--ghost"
                  href={
                    insight.tone === "opportunity" ? "/evaluations" : "/activity"
                  }
                >
                  {insight.secondaryActionLabel}
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>

      <p className="dashboard-home__footer">{view.footerNote}</p>
    </section>
  );
}

function RunningSwarmCard({
  swarm,
}: Readonly<{ swarm: DashboardRunningSwarm }>): JSX.Element {
  return (
    <li className="dashboard-running__card panel">
      <div className="dashboard-running__topline">
        <strong>{swarm.name}</strong>
        <StatusBadge status={swarm.status} />
      </div>
      <p className="dashboard-running__pattern">{swarm.pattern}</p>
      <p className="dashboard-running__progress">{swarm.progressLabel}</p>
      <dl className="dashboard-running__metrics">
        <div>
          <dt>Elapsed</dt>
          <dd>{swarm.elapsed}</dd>
        </div>
        <div>
          <dt>Cost rate</dt>
          <dd>{swarm.costRate}</dd>
        </div>
        <div>
          <dt>Commons</dt>
          <dd>{swarm.commonsOnLatest}</dd>
        </div>
      </dl>
      <div className="dashboard-running__actions">
        <Link href={swarm.canvasHref}>View Live Canvas</Link>
      </div>
    </li>
  );
}

function RecentRunRow({
  run,
}: Readonly<{ run: DashboardRecentRun }>): JSX.Element {
  return (
    <li className="dashboard-recent__row">
      <span>{run.time}</span>
      <strong>{run.swarm}</strong>
      <span>{run.commons}</span>
      <StatusBadge status={run.status} />
      <span>{run.duration}</span>
      <span>{run.cost}</span>
    </li>
  );
}
