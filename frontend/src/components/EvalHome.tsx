"use client";

/**
 * @duty EvalHome — evaluation campaign projection (ui_11)
 * @role Present eval campaigns/results; run campaign intent via onAction when eligible.
 * @controls Campaign list, run campaign, filters/nav.
 * @must Fail-closed when run campaign action is missing or ineligible.
 * @mustnot Invent campaign results or host eval authority.
 * @redesign docs/frontend_redesign/ui_11_eval.md
 */
import React, { useMemo, useState } from "react";
import { InfoTooltip } from './design';
import Link from "next/link";

import {
  type EvalLandingView,
} from "../lib/projections/eval-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function EvalHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: EvalLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [query, setQuery] = useState("");
  const [selectedIds, setSelectedIds] = useState<ReadonlySet<string>>(
    () => new Set(["p4"]),
  );
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [reviewOpen, setReviewOpen] = useState(false);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

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
    <section aria-label={L(labels, "eval_and_self_improvement_dashboard")} className="eval-home">
      <header className="eval-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <div className="page-title-row">
            <h1>{view.title}</h1>
            <InfoTooltip label="About this screen" text={view.description} />
          </div>
        </div>
        <label className="eval-home__search">
          <span className="visually-hidden">{L(labels, "search_commons_and_proposals")}</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={query}
          />
        </label>
      </header>

      <div
        aria-label={L(labels, "eval_scorecards")}
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

      {feedback ? (
        <p aria-live="polite" className="eval-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="eval-home__body">
        <section
          aria-labelledby="trends-heading"
          className="eval-home__trends"
        >
          <h2 id="trends-heading">{L(labels, "score_trends_l1_l2_l3")}</h2>
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
          <p className="eval-home__muted">{L(labels, "l1_validation_l2_l3_never_masked_by_average")}</p>
        </section>

        <section
          aria-labelledby="insights-heading"
          className="eval-home__insights"
        >
          <h2 id="insights-heading">{L(labels, "meta_critic_insights")}</h2>
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
            <h2 id="proposals-heading">{L(labels, "proposal_queue")}</h2>
            <Link className="eval-home__linkish" href="/registry">
              Open Registry Hub →
            </Link>
          </div>
          <div className="eval-home__table-wrap">
            <table className="eval-home__table">
              <thead>
                <tr>
                  <th scope="col">
                    <span className="visually-hidden">{L(labels, "select")}</span>
                  </th>
                  <th scope="col">{L(labels, "target_common")}</th>
                  <th scope="col">{L(labels, "expected_impact")}</th>
                  <th scope="col">{L(labels, "supporting_traces")}</th>
                  <th scope="col">{L(labels, "l1_l2_l3")}</th>
                  <th scope="col">{L(labels, "status")}</th>
                  <th scope="col">{L(labels, "actions")}</th>
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
            <div className="eval-home__review" aria-label={L(labels, "proposal_review")}>
              <h3>{L(labels, "proposal_review_diff_impact")}</h3>
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
            <h2 id="campaign-heading">{L(labels, "campaign_launcher")}</h2>
            <p>{view.campaignNote}</p>
            <p className="eval-home__muted">
              {selectedIds.size} underperforming commons selected
            </p>
            <button
              className="eval-home__action eval-home__action--primary"
              onClick={() => {
                if (onAction) {
                  void onAction({ kind: "eval.run_campaign" });
                  return;
                }
                announce(
                  "Run Batch Eval Campaign requires an authorized eval action. Results feed proposals only.",
                );
              }}
              type="button"
            >
              Run Batch Eval Campaign
            </button>
          </section>

          <section
            aria-labelledby="history-heading"
            className="eval-home__history"
          >
            <h2 id="history-heading">{L(labels, "improvement_history_a_b_results")}</h2>
            <h3>{L(labels, "merged_proposals_before_after")}</h3>
            <ul>
              {view.history.map((item) => (
                <li key={item.id}>
                  <strong>{item.title}</strong>
                  <span>{item.beforeAfter}</span>
                  <small>{item.metrics}</small>
                </li>
              ))}
            </ul>
            <h3>{L(labels, "a_b_experiments")}</h3>
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
