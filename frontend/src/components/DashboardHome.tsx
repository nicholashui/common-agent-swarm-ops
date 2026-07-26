import React from "react";
import Link from "next/link";

import {
  LOCAL_DASHBOARD_LANDING,
  type DashboardLandingView,
  type DashboardRecentRun,
  type DashboardRunningSwarm,
  type DashboardStatusTone,
} from "../lib/projections/dashboard-landing";

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
          aria-live="polite"
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

      <section
        aria-labelledby="common-health-heading"
        className="dashboard-home__section"
      >
        <h2 className="dashboard-home__section-label" id="common-health-heading">
          Common Health
        </h2>
        <div
          aria-live="polite"
          className="dashboard-home__stats"
          role="region"
        >
          {view.commonHealth.map((card) => {
            const body = (
              <>
                <p className="dashboard-stat__label">{card.label}</p>
                <p className="dashboard-stat__value">{card.value}</p>
                <p className="dashboard-stat__detail">{card.detail}</p>
                <Sparkline points={card.sparkline} tone={card.tone} />
                <p className="dashboard-stat__trend">{card.trend}</p>
              </>
            );
            return card.href ? (
              <Link
                className={`dashboard-stat dashboard-stat--${card.tone} dashboard-stat--link`}
                href={card.href}
                key={card.id}
              >
                {body}
              </Link>
            ) : (
              <article
                className={`dashboard-stat dashboard-stat--${card.tone}`}
                key={card.id}
              >
                {body}
              </article>
            );
          })}
        </div>
      </section>

      <section
        aria-labelledby="quick-actions-heading"
        className="dashboard-home__section"
      >
        <h2 className="dashboard-home__section-label" id="quick-actions-heading">
          Quick Actions
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
              <span aria-hidden="true" className="dashboard-action__icon">
                {action.primary ? "◉" : "◇"}
              </span>
              <span className="dashboard-action__copy">
                <strong>{action.label}</strong>
                <span>{action.description}</span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section
        aria-labelledby="fleet-heading"
        className="dashboard-home__section"
      >
        <h2 className="dashboard-home__fleet-title" id="fleet-heading">
          {view.fleetSectionTitle}
        </h2>
        <div className="dashboard-home__split">
          <section aria-labelledby="running-heading">
            <div className="dashboard-home__section-head">
              <h3 className="dashboard-home__subsection" id="running-heading">
                Running Now
              </h3>
              <Link className="dashboard-home__section-link" href="/canvas">
                Open canvas
              </Link>
            </div>
            {view.runningSwarms.length === 0 ? (
              <div className="dashboard-empty panel">
                <p>No swarms running. Start one from Common Patterns.</p>
                <Link className="dashboard-home__section-link" href="/composer">
                  Start from Common Patterns →
                </Link>
              </div>
            ) : (
              <ul aria-live="polite" className="dashboard-running">
                {view.runningSwarms.map((swarm) => (
                  <RunningSwarmCard key={swarm.id} swarm={swarm} />
                ))}
              </ul>
            )}
          </section>

          <section aria-labelledby="recent-heading">
            <div className="dashboard-home__section-head">
              <h3 className="dashboard-home__subsection" id="recent-heading">
                Recent Activity
              </h3>
              <Link className="dashboard-home__section-link" href="/activity">
                View all →
              </Link>
            </div>
            <div className="dashboard-recent panel">
              <div className="dashboard-recent__head" aria-hidden="true">
                <span>Time</span>
                <span>Swarm · Pattern</span>
                <span>Commons</span>
                <span>Status</span>
                <span>Action</span>
              </div>
              <ul className="dashboard-recent__list">
                {view.recentRuns.map((run) => (
                  <RecentRunRow key={run.id} run={run} />
                ))}
              </ul>
            </div>
          </section>
        </div>
      </section>

      <section
        aria-labelledby="insights-heading"
        className="dashboard-home__section"
      >
        <div>
          <h2 className="dashboard-home__fleet-title" id="insights-heading">
            Common Impact Insights
          </h2>
          <p className="dashboard-home__section-intro">{view.insightsIntro}</p>
        </div>
        <div className="dashboard-insights">
          {view.insights.map((insight) => (
            <article
              className={`dashboard-insight dashboard-insight--${insight.tone}`}
              key={insight.id}
            >
              <div className="dashboard-insight__title-row">
                <h3>{insight.title}</h3>
                {insight.badge ? (
                  <span className="dashboard-insight__badge">{insight.badge}</span>
                ) : null}
              </div>
              <p>{insight.body}</p>
              <div className="dashboard-insight__actions">
                <Link
                  className="dashboard-insight__button"
                  href={insight.primaryActionHref}
                >
                  {insight.primaryActionLabel}
                </Link>
                <Link
                  className="dashboard-insight__button dashboard-insight__button--ghost"
                  href={insight.secondaryActionHref}
                >
                  {insight.secondaryActionLabel}
                </Link>
                {insight.tertiaryActionLabel && insight.tertiaryActionHref ? (
                  <Link
                    className="dashboard-insight__button dashboard-insight__button--ghost"
                    href={insight.tertiaryActionHref}
                  >
                    {insight.tertiaryActionLabel}
                  </Link>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section
        aria-labelledby="control-plane-heading"
        className="dashboard-home__section"
      >
        <h2 className="dashboard-home__fleet-title" id="control-plane-heading">
          Control-Plane Health &amp; Freshness
        </h2>
        <div className="dashboard-control panel">
          <div className="dashboard-control__cell">
            <p className="dashboard-control__label">API / Projection Health</p>
            <p
              className={`dashboard-control__pill dashboard-control__pill--${view.controlPlane.apiHealthTone}`}
            >
              {view.controlPlane.apiHealthLabel}
            </p>
            <p className="dashboard-control__label">Delayed-event warning</p>
            <p className="dashboard-control__value">
              {view.controlPlane.delayedEventWarning}
            </p>
          </div>
          <div className="dashboard-control__cell">
            <p className="dashboard-control__label">Queue / Run Backlog</p>
            <p className="dashboard-control__metric">
              <strong>{view.controlPlane.backlogCount}</strong>
              <span>{view.controlPlane.backlogDetail}</span>
            </p>
            <p className="dashboard-control__label">Approval expiry alert</p>
            <p className="dashboard-control__alert">
              {view.controlPlane.approvalExpiryAlert}
            </p>
          </div>
          <div className="dashboard-control__cell">
            <p className="dashboard-control__label">SSE Transport</p>
            <p className="dashboard-control__pill dashboard-control__pill--stale">
              {view.controlPlane.sseLabel}
            </p>
            <p className="dashboard-control__value">
              {view.controlPlane.sseDetail}
            </p>
            <p className="dashboard-control__mono">
              as_of {view.asOf} · {view.controlPlane.correlationId}
            </p>
          </div>
          <div className="dashboard-control__cell">
            <p className="dashboard-control__label">Affected swarms</p>
            <div className="dashboard-control__affected">
              <p>{view.controlPlane.affectedSummary}</p>
              <Link
                className="dashboard-insight__button"
                href={view.controlPlane.affectedHref}
              >
                View affected →
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section
        aria-labelledby="pinned-heading"
        className="dashboard-home__section"
      >
        <h2 className="dashboard-home__subsection" id="pinned-heading">
          Pinned / Favorites
        </h2>
        <ul className="dashboard-pinned">
          {view.pinned.map((item) => (
            <li key={item.id}>
              <Link className="dashboard-pinned__card" href={item.href}>
                <strong>{item.name}</strong>
                <span
                  className={`dashboard-pinned__kind dashboard-pinned__kind--${item.kindTone}`}
                >
                  {item.kindLabel}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <p className="dashboard-home__footer">{view.footerNote}</p>
    </section>
  );
}

function Sparkline({
  points,
  tone,
}: Readonly<{
  points: readonly number[];
  tone: "indigo" | "green" | "violet" | "amber";
}>): JSX.Element {
  const width = 120;
  const height = 28;
  const max = Math.max(...points, 1);
  const min = Math.min(...points, 0);
  const range = Math.max(max - min, 1);
  const path = points
    .map((point, index) => {
      const x = (index / Math.max(points.length - 1, 1)) * width;
      const y = height - ((point - min) / range) * (height - 4) - 2;
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg
      aria-hidden="true"
      className={`dashboard-sparkline dashboard-sparkline--${tone}`}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      width={width}
    >
      <path d={path} fill="none" strokeWidth="2" />
    </svg>
  );
}

function StatusPill({
  tone,
  label,
}: Readonly<{ tone: DashboardStatusTone; label: string }>): JSX.Element {
  return (
    <span className={`dashboard-status dashboard-status--${tone}`}>
      <span aria-hidden="true" className="dashboard-status__dot" />
      {label}
    </span>
  );
}

function RunningSwarmCard({
  swarm,
}: Readonly<{ swarm: DashboardRunningSwarm }>): JSX.Element {
  return (
    <li className="dashboard-running__card panel">
      <div className="dashboard-running__topline">
        <strong>{swarm.name}</strong>
        <StatusPill label={swarm.statusLabel} tone={swarm.status} />
      </div>
      <p className="dashboard-running__pattern">{swarm.pattern}</p>
      <p className="dashboard-running__progress">
        {swarm.progressLabel} · elapsed {swarm.elapsed} · {swarm.costRate}
      </p>
      <div
        aria-label={`Progress ${swarm.progressPercent} percent`}
        className="dashboard-running__bar"
      >
        <span style={{ width: `${Math.max(0, Math.min(100, swarm.progressPercent))}%` }} />
      </div>
      <div className="dashboard-running__actions">
        <Link className="dashboard-running__primary" href={swarm.canvasHref}>
          View Canvas
        </Link>
        <button className="dashboard-running__secondary" disabled type="button">
          Pause
        </button>
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
      <span className="dashboard-recent__swarm">
        <strong>{run.swarm}</strong>
        <small>{run.pattern}</small>
      </span>
      <span>{run.commons}</span>
      <StatusPill label={run.statusLabel} tone={run.status} />
      <Link className="dashboard-recent__action" href={run.actionHref}>
        {run.actionLabel}
      </Link>
    </li>
  );
}
