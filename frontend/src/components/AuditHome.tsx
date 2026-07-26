"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type AuditLandingView,
  type AuditLogRow,
} from "../lib/projections/audit-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function AuditHome({
  view }: Readonly<{ view: AuditLandingView }>): JSX.Element {
  const labels = view.labels;
  const [query, setQuery] = useState("");
  const [actionFilter, setActionFilter] = useState<string | undefined>();
  const [selectedId, setSelectedId] = useState(view.rows[0]?.id);
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => setStatusMessage(message);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return view.rows.filter((row) => {
      if (actionFilter) {
        const needle = actionFilter.toLowerCase();
        if (
          !row.actionType.includes(needle) &&
          !row.action.toLowerCase().includes(needle)
        ) {
          return false;
        }
      }
      if (q.length === 0) return true;
      return (
        row.actor.toLowerCase().includes(q) ||
        row.action.toLowerCase().includes(q) ||
        row.target.toLowerCase().includes(q) ||
        row.correlationId.toLowerCase().includes(q) ||
        row.summary.toLowerCase().includes(q)
      );
    });
  }, [actionFilter, query, view.rows]);

  const selected =
    rows.find((row) => row.id === selectedId) ?? rows[0] ?? view.rows[0];

  return (
    <section aria-label={L(labels, "governance_and_audit_trail")} className="audit-home">
      <header className="audit-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <div className="audit-home__header-actions">
          <label className="audit-home__search">
            <span className="visually-hidden">{L(labels, "search_audit_log")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={query}
            />
          </label>
          <button
            className="audit-home__action audit-home__action--primary"
            onClick={() =>
              announce(
                "Export CSV/JSON requires an authorized export job. Full payloads only via authorized export.",
              )
            }
            type="button"
          >
            Export CSV
          </button>
          <button
            className="audit-home__action"
            onClick={() =>
              announce(
                "Verify integrity requires an authorized compliance action.",
              )
            }
            type="button"
          >
            Verify integrity
          </button>
        </div>
      </header>

      {statusMessage ? (
        <p aria-live="polite" className="audit-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="audit-home__body">
        <aside aria-label={L(labels, "audit_filters")} className="audit-home__filters">
          <h2>{L(labels, "filters")}</h2>
          <button className="audit-home__filter" type="button">
            <span>{L(labels, "time_range")}</span>
            <strong>{view.timeRangeLabel} ▾</strong>
          </button>
          <button className="audit-home__filter" type="button">
            <span>{L(labels, "actor")}</span>
            <strong>{view.actorFilterLabel} ▾</strong>
          </button>
          <div className="audit-home__action-types" role="group" aria-label={L(labels, "action_type")}>
            <p>{L(labels, "action_type")}</p>
            {view.actionTypes.map((type) => (
              <button
                aria-pressed={actionFilter === type}
                className={
                  actionFilter === type
                    ? "audit-home__chip audit-home__chip--active"
                    : "audit-home__chip"
                }
                key={type}
                onClick={() =>
                  setActionFilter((current) =>
                    current === type ? undefined : type,
                  )
                }
                type="button"
              >
                {type}
              </button>
            ))}
          </div>
          <label className="audit-home__correlation">
            <span>{L(labels, "correlation_id")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={L(labels, "b7f2c9d0")}
              value={query}
            />
          </label>
          <div className="audit-home__integrity" role="status">
            <strong>{view.integrity.label}</strong>
            <p>{view.integrity.detail}</p>
            <code>{view.integrity.lastHash}</code>
          </div>
          <div className="audit-home__reports">
            <h3>{L(labels, "pre_built_reports")}</h3>
            <ul>
              {view.reports.map((report) => (
                <li key={report}>
                  <button
                    className="audit-home__linkish"
                    onClick={() =>
                      announce(
                        `Report “${report}” requires an authorized compliance query.`,
                      )
                    }
                    type="button"
                  >
                    {report}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <p className="audit-home__safety" role="note">
            {view.safetyNote}
          </p>
        </aside>

        <div className="audit-home__main">
          <div className="audit-home__table-wrap" role="region" aria-label={L(labels, "audit_table")}>
            <table className="audit-home__table">
              <thead>
                <tr>
                  <th scope="col">{L(labels, "timestamp_utc")}</th>
                  <th scope="col">{L(labels, "user_actor")}</th>
                  <th scope="col">{L(labels, "action")}</th>
                  <th scope="col">{L(labels, "target")}</th>
                  <th scope="col">{L(labels, "before_after_summary")}</th>
                  <th scope="col">{L(labels, "status")}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    className={
                      selected?.id === row.id
                        ? "audit-home__row audit-home__row--selected"
                        : "audit-home__row"
                    }
                    key={row.id}
                    onClick={() => setSelectedId(row.id)}
                  >
                    <td>
                      <button
                        className="audit-home__row-btn"
                        onClick={() => setSelectedId(row.id)}
                        type="button"
                      >
                        {row.timestamp}
                      </button>
                    </td>
                    <td>{row.actor}</td>
                    <td>
                      <code>{row.action}</code>
                    </td>
                    <td>{row.target}</td>
                    <td>{row.summary}</td>
                    <td>
                      <span
                        className={`audit-home__status-pill audit-home__status-pill--${row.status}`}
                      >
                        {row.statusLabel}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="audit-home__pagination">{view.paginationLabel}</p>

          {selected ? (
            <EventDetail
              row={selected}
              onAnnounce={announce}
             labels={labels} />
          ) : null}
        </div>
      </div>

      <p className="audit-home__footer">{view.footerNote}</p>
    </section>
  );
}

function EventDetail({
  row,
  onAnnounce,
  labels,
}: Readonly<{
  row: AuditLogRow;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <aside aria-label={L(labels, "event_detail_2")} className="audit-home__detail">
      <header className="audit-home__detail-head">
        <div>
          <p className="eyebrow">{L(labels, "event_detail")}</p>
          <h2>{row.action}</h2>
        </div>
        <span
          className={`audit-home__status-pill audit-home__status-pill--${row.status}`}
        >
          {row.statusLabel}
        </span>
      </header>
      <dl className="audit-home__detail-grid">
        <div>
          <dt>{L(labels, "actor")}</dt>
          <dd>{row.actor}</dd>
        </div>
        <div>
          <dt>{L(labels, "timestamp")}</dt>
          <dd>{row.timestamp} UTC</dd>
        </div>
        <div>
          <dt>{L(labels, "target")}</dt>
          <dd>{row.target}</dd>
        </div>
        <div>
          <dt>{L(labels, "reason_summary")}</dt>
          <dd>{row.summary}</dd>
        </div>
        <div>
          <dt>{L(labels, "correlation_id")}</dt>
          <dd>
            <code>{row.correlationId}</code>
          </dd>
        </div>
        <div>
          <dt>{L(labels, "prev_hash")}</dt>
          <dd>
            <code>{row.prevHash}</code>
          </dd>
        </div>
        <div>
          <dt>{L(labels, "entry_hash")}</dt>
          <dd>
            <code>{row.entryHash}</code>
          </dd>
        </div>
        {row.graphRevision ? (
          <div>
            <dt>{L(labels, "graph_revision")}</dt>
            <dd>{row.graphRevision}</dd>
          </div>
        ) : null}
        {row.commonVersion ? (
          <div>
            <dt>{L(labels, "common_version")}</dt>
            <dd>{row.commonVersion}</dd>
          </div>
        ) : null}
      </dl>

      <h3>{L(labels, "context_redacted")}</h3>
      <ul className="audit-home__detail-lines">
        {row.detailLines.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>

      <pre className="audit-home__diff" aria-label={L(labels, "redacted_diff")}>
        {`# redacted structured diff
- value: [REDACTED]
+ value: [REDACTED]
# private tool parameters are not inferable from this projection`}
      </pre>

      {row.links.length > 0 ? (
        <div className="audit-home__links">
          <h3>{L(labels, "linked_context")}</h3>
          <ul>
            {row.links.map((link) => (
              <li key={link.label}>
                <Link className="audit-home__linkish" href={link.href}>
                  → {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <p className="audit-home__muted">
        Values redacted · full payloads only via authorized export. Historical
        records are immutable.
      </p>
      <button
        className="audit-home__action"
        onClick={() =>
          onAnnounce(
            "Authorized export required for full payload. Audit history cannot be mutated.",
          )
        }
        type="button"
      >
        Request authorized export
      </button>
    </aside>
  );
}
