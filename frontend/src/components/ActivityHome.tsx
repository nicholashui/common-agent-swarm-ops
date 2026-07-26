"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  LOCAL_ACTIVITY_LANDING,
  type ActivityCardStatus,
  type ActivityExecutionCard,
  type ActivityLandingView,
  type ActivityViewMode,
} from "../lib/projections/activity-landing";

export function ActivityHome({
  view = LOCAL_ACTIVITY_LANDING,
}: Readonly<{ view?: ActivityLandingView }>): JSX.Element {
  const [mode, setMode] = useState<ActivityViewMode>("board");
  const [liveUpdate, setLiveUpdate] = useState(true);
  const [search, setSearch] = useState("");
  const [outdatedOnly, setOutdatedOnly] = useState(false);
  const [contributedOnly, setContributedOnly] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [selectedIds, setSelectedIds] = useState<ReadonlySet<string>>(
    () => new Set(),
  );

  const announce = (message: string): void => setStatusMessage(message);

  const filteredColumns = useMemo(() => {
    const q = search.trim().toLowerCase();
    return view.boardColumns.map((column) => ({
      ...column,
      cards: column.cards.filter((card) => {
        if (outdatedOnly && !/v1\.|v2\.0|Fork/.test(card.versionLabel)) {
          return false;
        }
        if (
          contributedOnly &&
          !(card.teaser?.toLowerCase().includes("contributed") ?? false)
        ) {
          return false;
        }
        if (q.length === 0) return true;
        return (
          card.agentName.toLowerCase().includes(q) ||
          card.versionLabel.toLowerCase().includes(q) ||
          card.meta.toLowerCase().includes(q) ||
          (card.teaser?.toLowerCase().includes(q) ?? false) ||
          column.title.toLowerCase().includes(q)
        );
      }),
    }));
  }, [outdatedOnly, contributedOnly, search, view.boardColumns]);

  const filteredTableRows = useMemo(() => {
    const q = search.trim().toLowerCase();
    return view.tableRows.filter((row) => {
      if (q.length === 0) return true;
      return (
        row.swarm.toLowerCase().includes(q) ||
        row.agent.toLowerCase().includes(q) ||
        row.version.toLowerCase().includes(q) ||
        row.id.toLowerCase().includes(q) ||
        (row.error?.toLowerCase().includes(q) ?? false)
      );
    });
  }, [search, view.tableRows]);

  const toggleSelected = (id: string): void => {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <section aria-label="Activity and ops intelligence" className="activity-home">
      <header className="activity-home__header">
        <div>
          <p className="eyebrow">ACTIVITY</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
          <p className="activity-home__workspace">{view.workspaceLabel}</p>
        </div>
        <div className="activity-home__header-controls">
          <label className="activity-home__search">
            <span className="visually-hidden">Search activity</span>
            <input
              onChange={(event) => setSearch(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={search}
            />
          </label>
          <button className="activity-home__chip" type="button">
            {view.dateRangeLabel} ▾
          </button>
          <div
            aria-label="View mode"
            className="activity-home__modes"
            role="group"
          >
            {(["board", "table", "timeline"] as const).map((entry) => (
              <button
                aria-pressed={mode === entry}
                className={
                  mode === entry
                    ? "activity-home__mode activity-home__mode--active"
                    : "activity-home__mode"
                }
                key={entry}
                onClick={() => setMode(entry)}
                type="button"
              >
                {entry[0]?.toUpperCase()}
                {entry.slice(1)}
              </button>
            ))}
          </div>
          <label className="activity-home__live">
            <input
              checked={liveUpdate}
              onChange={(event) => setLiveUpdate(event.target.checked)}
              type="checkbox"
            />
            Live Update
          </label>
        </div>
      </header>

      <div
        aria-label="Activity filters"
        className="activity-home__filters"
        role="group"
      >
        {view.filterChips.map((chip) => (
          <button className="activity-home__chip" key={chip} type="button">
            {chip} ▾
          </button>
        ))}
        {view.toggleFilters.map((toggle) => (
          <label className="activity-home__toggle" key={toggle.id}>
            <input
              checked={
                toggle.id === "outdated" ? outdatedOnly : contributedOnly
              }
              onChange={(event) => {
                if (toggle.id === "outdated") {
                  setOutdatedOnly(event.target.checked);
                } else {
                  setContributedOnly(event.target.checked);
                }
              }}
              type="checkbox"
            />
            {toggle.label}
          </label>
        ))}
      </div>

      {statusMessage ? (
        <p aria-live="polite" className="activity-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      {liveUpdate ? (
        <p aria-live="polite" className="activity-home__live-note" role="status">
          Live Update on · new activity appears when run SSE is authorized
        </p>
      ) : null}

      <div className="activity-home__body">
        <div className="activity-home__main">
          {mode === "board" ? (
            <BoardView
              columns={filteredColumns}
              onAction={announce}
            />
          ) : null}
          {mode === "table" ? (
            <TableView
              rows={filteredTableRows}
              selectedIds={selectedIds}
              onToggle={toggleSelected}
              onAction={announce}
            />
          ) : null}
          {mode === "timeline" ? (
            <TimelineView view={view} onAction={announce} />
          ) : null}

          {selectedIds.size > 0 ? (
            <div className="activity-home__bulk" role="region" aria-label="Bulk actions">
              <span>{selectedIds.size} selected</span>
              {view.bulkActions.map((action) => (
                <button
                  className="activity-home__action"
                  key={action}
                  onClick={() =>
                    announce(
                      `${action} requires server-determined eligibility and preserves immutable version provenance.`,
                    )
                  }
                  type="button"
                >
                  {action}
                </button>
              ))}
            </div>
          ) : null}
        </div>

        <aside aria-label="Ops intelligence" className="activity-home__insights">
          <h2>Ops Intelligence</h2>
          <ul className="activity-home__kpis">
            {view.kpis.map((kpi) => (
              <li key={kpi.id}>
                <strong>{kpi.value}</strong>
                <span>{kpi.label}</span>
                {kpi.detail ? <small>{kpi.detail}</small> : null}
              </li>
            ))}
          </ul>
          <div className="activity-home__chart" aria-hidden="true">
            <p>{view.chartNote}</p>
            <div className="activity-home__chart-bars">
              <i style={{ height: "40%" }} />
              <i style={{ height: "62%" }} />
              <i style={{ height: "55%" }} />
              <i style={{ height: "78%" }} />
              <i style={{ height: "70%" }} />
              <i style={{ height: "88%" }} />
            </div>
          </div>

          <h3>Rollout Opportunities &amp; Anomalies</h3>
          <ul className="activity-home__rollouts">
            {view.rolloutCards.map((card) => (
              <li
                className={`activity-home__rollout activity-home__rollout--${card.tone}`}
                key={card.id}
              >
                <strong>{card.title}</strong>
                <p>{card.body}</p>
                <div className="activity-home__rollout-actions">
                  {card.actions.map((action) => (
                    <button
                      className={
                        action === "Approve" || action === "Rollback"
                          ? "activity-home__action activity-home__action--primary"
                          : "activity-home__action"
                      }
                      key={action}
                      onClick={() =>
                        announce(
                          `${action} requires an authorized rollout or recovery action.`,
                        )
                      }
                      type="button"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </li>
            ))}
          </ul>

          <section className="activity-home__impact">
            <h3>Collective Improvement Impact</h3>
            <p>{view.collectiveImpact}</p>
            <div className="activity-home__bulk-inline">
              {view.bulkActions.map((action) => (
                <button
                  className="activity-home__action"
                  key={action}
                  onClick={() =>
                    announce(
                      `${action} requires server-determined eligibility.`,
                    )
                  }
                  type="button"
                >
                  {action}
                </button>
              ))}
            </div>
          </section>

          <p className="activity-home__freshness" role="status">
            {view.freshnessLabel}
          </p>
        </aside>
      </div>

      <p className="activity-home__footer">{view.footerNote}</p>
    </section>
  );
}

function BoardView({
  columns,
  onAction,
}: Readonly<{
  columns: ActivityLandingView["boardColumns"];
  onAction: (message: string) => void;
}>): JSX.Element {
  const totalCards = columns.reduce((sum, column) => sum + column.cards.length, 0);
  if (totalCards === 0) {
    return (
      <div className="activity-home__empty panel">
        <p>No activity yet — start a swarm from Common Patterns.</p>
        <Link className="activity-home__link" href="/composer">
          Start from Common Patterns →
        </Link>
      </div>
    );
  }

  return (
    <div className="activity-home__board" role="region" aria-label="Activity board">
      {columns.map((column) => (
        <section
          aria-label={column.title}
          className={`activity-home__column activity-home__column--${column.healthTone}`}
          key={column.id}
        >
          <header className="activity-home__column-head">
            <h2>{column.title}</h2>
            <span className="activity-home__pattern">{column.patternLabel}</span>
            <p>{column.stats}</p>
          </header>
          <ul className="activity-home__cards">
            {column.cards.map((card) => (
              <li key={card.id}>
                <ExecutionCard card={card} onAction={onAction} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

function ExecutionCard({
  card,
  onAction,
}: Readonly<{
  card: ActivityExecutionCard;
  onAction: (message: string) => void;
}>): JSX.Element {
  return (
    <article
      className={`activity-home__card activity-home__card--${card.status}${card.custom ? " activity-home__card--custom" : ""}`}
    >
      <div className="activity-home__card-top">
        <strong>{card.agentName}</strong>
        <StatusPill label={card.statusLabel} status={card.status} />
      </div>
      <span
        className={
          card.custom
            ? "activity-home__version activity-home__version--custom"
            : "activity-home__version"
        }
      >
        {card.versionLabel}
      </span>
      <p className="activity-home__meta">{card.meta}</p>
      {card.teaser ? <p className="activity-home__teaser">{card.teaser}</p> : null}
      <div className="activity-home__card-actions">
        {card.actions.map((action) => {
          if (action === "View in Canvas") {
            return (
              <Link className="activity-home__linkish" href="/canvas" key={action}>
                {action}
              </Link>
            );
          }
          if (action === "Open Detail") {
            return (
              <Link
                className="activity-home__linkish"
                href="/registry/agents/local-preview"
                key={action}
              >
                {action}
              </Link>
            );
          }
          return (
            <button
              className="activity-home__linkish"
              key={action}
              onClick={() =>
                onAction(
                  `${action} requires server-determined eligibility and preserves immutable version provenance.`,
                )
              }
              type="button"
            >
              {action}
            </button>
          );
        })}
      </div>
    </article>
  );
}

function TableView({
  rows,
  selectedIds,
  onToggle,
  onAction,
}: Readonly<{
  rows: ActivityLandingView["tableRows"];
  selectedIds: ReadonlySet<string>;
  onToggle: (id: string) => void;
  onAction: (message: string) => void;
}>): JSX.Element {
  if (rows.length === 0) {
    return (
      <div className="activity-home__empty panel">
        <p>No activity matches the current filters.</p>
      </div>
    );
  }

  return (
    <div className="activity-home__table-wrap" role="region" aria-label="Activity table">
      <table className="activity-home__table">
        <thead>
          <tr>
            <th scope="col">
              <span className="visually-hidden">Select</span>
            </th>
            <th scope="col">Timestamp</th>
            <th scope="col">Swarm · Business</th>
            <th scope="col">Pattern</th>
            <th scope="col">Agent · Version</th>
            <th scope="col">Status</th>
            <th scope="col">Duration / Tokens / Cost</th>
            <th scope="col">Lifecycle · Checkpoint</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>
                <input
                  aria-label={`Select ${row.swarm} ${row.agent}`}
                  checked={selectedIds.has(row.id)}
                  onChange={() => onToggle(row.id)}
                  type="checkbox"
                />
              </td>
              <td>{row.timestamp}</td>
              <td>
                <strong>{row.swarm}</strong>
                <span className="activity-home__muted">{row.business}</span>
              </td>
              <td>{row.pattern}</td>
              <td>
                <strong>{row.agent}</strong>
                <span className="activity-home__version">{row.version}</span>
              </td>
              <td>
                <StatusPill label={row.statusLabel} status={row.status} />
                {row.error ? (
                  <span className="activity-home__error">{row.error}</span>
                ) : null}
              </td>
              <td>
                {row.duration} · {row.tokens} · {row.cost}
              </td>
              <td>
                <span className="activity-home__muted">
                  {row.lifecycle} · rev {row.graphRevision}
                </span>
                <span className="activity-home__muted">{row.checkpoint}</span>
              </td>
              <td>
                <button
                  className="activity-home__linkish"
                  onClick={() =>
                    onAction(
                      "Replay with latest commons requires server eligibility; provenance is preserved.",
                    )
                  }
                  type="button"
                >
                  Replay
                </button>
                <Link className="activity-home__linkish" href="/canvas">
                  Canvas
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TimelineView({
  view,
  onAction,
}: Readonly<{
  view: ActivityLandingView;
  onAction: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="activity-home__timeline" role="region" aria-label="Activity timeline">
      <p className="activity-home__timeline-note">
        Gantt-style lanes by subworkflow · bars show execution spans and common
        versions · click opens detail when authorized.
      </p>
      <ul className="activity-home__lanes">
        {view.timelineLanes.map((lane) => (
          <li key={lane.id}>
            <div className="activity-home__lane-label">{lane.label}</div>
            <div className="activity-home__lane-track">
              {lane.bars.map((bar) => (
                <button
                  className={`activity-home__bar activity-home__bar--${bar.tone}`}
                  key={bar.id}
                  onClick={() =>
                    onAction(
                      `Timeline bar “${bar.label}” — open detail requires authorized projection.`,
                    )
                  }
                  style={{ left: `${bar.startPct}%`, width: `${bar.widthPct}%` }}
                  type="button"
                >
                  {bar.label}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function StatusPill({
  status,
  label,
}: Readonly<{ status: ActivityCardStatus; label: string }>): JSX.Element {
  return (
    <span className={`activity-home__status-pill activity-home__status-pill--${status}`}>
      {label}
    </span>
  );
}
