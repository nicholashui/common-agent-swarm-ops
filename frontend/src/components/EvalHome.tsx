"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  LOCAL_EVAL_LANDING,
  type EvalLandingView,
} from "../lib/projections/eval-landing";

export function EvalHome({
  view = LOCAL_EVAL_LANDING,
}: Readonly<{ view?: EvalLandingView }>): JSX.Element {
  const [query, setQuery] = useState("");
  const [selectedIds, setSelectedIds] = useState<ReadonlySet<string>>(
    () => new Set(["p4"]),
  );
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [reviewOpen, setReviewOpen] = useState(false);

  const announce = (message: string): void => setStatusMessage(message);

  const proposals = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.proposals;
    return view.proposals.filter(
      (row) =>
        row.target.toLowerCase().includes(q) ||
        row.impact.toLowerCase().includes(q) ||
        row.status.toLowerCase().includes(q),
    );
  }, [query, view.proposals]);

  const toggleSelected = (id: string): void => {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <section aria-label="Eval and self-improvement dashboard" className="eval-home">
      <header className="eval-home__header">
        <div>
          <p className="eyebrow">EVAL</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <label className="eval-home__search">
          <span className="visually-hidden">Search commons and proposals</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={query}
          />
        </label>
      </header>

      <div
        aria-label="Eval scorecards"
        className="eval-home__scorecards"
        role="region"
      >
        {view.scorecards.map((card) => (
          <article
            className={`eval-home__scorecard eval-home__scorecard--${card.tone}`}
            key={card.id}
          >
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.trend}</span>
          </article>
        ))}
      </div>

      <p className="eval-home__layer-note" role="note">
        {view.layerNote}
      </p>

      {statusMessage ? (
        <p aria-live="polite" className="eval-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="eval-home__body">
        <section
          aria-labelledby="trends-heading"
          className="eval-home__trends"
        >
          <h2 id="trends-heading">Score Trends (L1 / L2 / L3)</h2>
          <ul className="eval-home__trend-legend">
            {view.trendLabels.map((label) => (
              <li key={label}>{label}</li>
            ))}
          </ul>
          <div className="eval-home__chart" aria-hidden="true">
            <i style={{ height: "72%" }} />
            <i style={{ height: "84%" }} />
            <i style={{ height: "68%" }} />
            <i style={{ height: "90%" }} />
            <i style={{ height: "78%" }} />
            <i style={{ height: "94%" }} />
          </div>
          <p className="eval-home__muted">↑ L1 validation · L2/L3 never masked by average</p>
        </section>

        <section
          aria-labelledby="insights-heading"
          className="eval-home__insights"
        >
          <h2 id="insights-heading">Meta-Critic Insights</h2>
          <ul>
            {view.insights.map((insight) => (
              <li key={insight.id}>
                <strong>{insight.title}</strong>
                <p>{insight.body}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="eval-home__main">
        <section
          aria-labelledby="proposals-heading"
          className="eval-home__proposals"
        >
          <div className="eval-home__section-head">
            <h2 id="proposals-heading">Proposal Queue</h2>
            <Link className="eval-home__linkish" href="/registry">
              Open Registry Hub →
            </Link>
          </div>
          <div className="eval-home__table-wrap">
            <table className="eval-home__table">
              <thead>
                <tr>
                  <th scope="col">
                    <span className="visually-hidden">Select</span>
                  </th>
                  <th scope="col">Target common</th>
                  <th scope="col">Expected impact</th>
                  <th scope="col">Supporting traces</th>
                  <th scope="col">L1 / L2 / L3</th>
                  <th scope="col">Status</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {proposals.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <input
                        aria-label={`Select ${row.target}`}
                        checked={selectedIds.has(row.id)}
                        onChange={() => toggleSelected(row.id)}
                        type="checkbox"
                      />
                    </td>
                    <td>
                      <strong>{row.target}</strong>
                    </td>
                    <td>{row.impact}</td>
                    <td>{row.traces}</td>
                    <td>{row.layers}</td>
                    <td>{row.status}</td>
                    <td>
                      <button
                        className="eval-home__linkish"
                        onClick={() => {
                          setReviewOpen(true);
                          announce(
                            "Review opens redacted diff + impact — merge requires authorized governance.",
                          );
                        }}
                        type="button"
                      >
                        Review
                      </button>
                      <button
                        className="eval-home__linkish"
                        onClick={() =>
                          announce(
                            "Approve requires proposal + approval + canary stages. Eval pass alone does not publish.",
                          )
                        }
                        type="button"
                      >
                        Approve
                      </button>
                      <button
                        className="eval-home__linkish"
                        onClick={() =>
                          announce(
                            "Reject requires an authorized governance action.",
                          )
                        }
                        type="button"
                      >
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {reviewOpen ? (
            <div className="eval-home__review" aria-label="Proposal review">
              <h3>Proposal Review — Diff + Impact</h3>
              <pre className="eval-home__diff">
                {`- max_iterations: 3
+ max_iterations: 5
+ verification_step: structured_rubric
  # redacted diff · evidence refs only
  meta-critic: reduced hallucinations 18% across 2.1k runs`}
              </pre>
              <p className="eval-home__muted">{view.evidenceNote}</p>
              <div className="eval-home__actions">
                <button
                  className="eval-home__action eval-home__action--primary"
                  onClick={() =>
                    announce(
                      "Approve & merge requires authorized proposal workflow — not eval pass alone.",
                    )
                  }
                  type="button"
                >
                  Approve &amp; Merge
                </button>
                <button
                  className="eval-home__action"
                  onClick={() => setReviewOpen(false)}
                  type="button"
                >
                  Close review
                </button>
              </div>
            </div>
          ) : null}
        </section>

        <div className="eval-home__side-column">
          <section
            aria-labelledby="campaign-heading"
            className="eval-home__campaign"
          >
            <h2 id="campaign-heading">Campaign Launcher</h2>
            <p>{view.campaignNote}</p>
            <p className="eval-home__muted">
              {selectedIds.size} underperforming commons selected
            </p>
            <button
              className="eval-home__action eval-home__action--primary"
              onClick={() =>
                announce(
                  "Run Batch Eval Campaign requires an authorized eval action. Results feed proposals only.",
                )
              }
              type="button"
            >
              Run Batch Eval Campaign
            </button>
          </section>

          <section
            aria-labelledby="history-heading"
            className="eval-home__history"
          >
            <h2 id="history-heading">Improvement History &amp; A/B Results</h2>
            <h3>Merged proposals (before → after)</h3>
            <ul>
              {view.history.map((item) => (
                <li key={item.id}>
                  <strong>{item.title}</strong>
                  <span>{item.beforeAfter}</span>
                  <small>{item.metrics}</small>
                </li>
              ))}
            </ul>
            <h3>A/B Experiments</h3>
            <ul>
              {view.experiments.map((item) => (
                <li key={item.id}>
                  <strong>{item.title}</strong>
                  <span>{item.result}</span>
                  <small>{item.recommendation}</small>
                  <button
                    className="eval-home__action"
                    onClick={() =>
                      announce(
                        "Promote winner requires proposal, approval, canary, and rollback stages.",
                      )
                    }
                    type="button"
                  >
                    Promote winner
                  </button>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>

      <p className="eval-home__footer">{view.footerNote}</p>
    </section>
  );
}
