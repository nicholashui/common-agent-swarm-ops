"use client";

import React, { useState } from "react";
import Link from "next/link";

import {
  AGENT_DETAIL_TABS,
  type AgentDetailLandingView,
  type AgentDetailTabId,
  type AgentDetailUsageRow,
} from "../lib/projections/agent-detail-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function AgentDetailHome({
  view,
  agentId,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: AgentDetailLandingView;
  agentId?: string;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [tab, setTab] = useState<AgentDetailTabId>("history");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [playgroundInput, setPlaygroundInput] = useState("");
  const [knowledgeQuery, setKnowledgeQuery] = useState("");

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  return (
    <section aria-label={L(labels, "common_agent_detail")} className="agent-detail">
      <header className="agent-detail__header">
        <div className="agent-detail__header-main">
          <div className="agent-detail__identity">
            <span aria-hidden="true" className="agent-detail__mark">
              VL
            </span>
            <div>
              <p className="eyebrow">{view.eyebrow}</p>
              <h1>{view.agentName}</h1>
              <div className="agent-detail__badges">
                <span className="agent-detail__version-pill">
                  {view.versionBadge}
                </span>
                <span className="agent-detail__live-pill">{view.statusLabel}</span>
                <span className="agent-detail__velocity">
                  {view.velocityLabel}
                </span>
              </div>
              {agentId ? (
                <p className="agent-detail__opaque-id">
                  Opaque reference: {agentId}
                </p>
              ) : null}
            </div>
          </div>
          <ul className="agent-detail__header-stats">
            {view.headerStats.map((stat) => (
              <li key={stat.id}>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
                {stat.detail ? <small>{stat.detail}</small> : null}
              </li>
            ))}
          </ul>
        </div>

        <div className="agent-detail__actions" role="group" aria-label={L(labels, "quick_actions")}>
          <button
            className="agent-detail__action agent-detail__action--primary"
            onClick={() =>
              announce(
                "Propose Improvement requires an authorized commons proposal action.",
              )
            }
            type="button"
          >
            ✦ Propose Improvement
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              announce(L(labels, "a_b_test_requires_an_authorized_rollout_contract"))
            }
            type="button"
          >
            A/B Test vs newer
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              announce(L(labels, "fork_to_custom_requires_an_authorized_fork_actio"))
            }
            type="button"
          >
            Fork to Custom
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              announce(
                "Pin / Update in swarms requires an authorized bulk version action.",
              )
            }
            type="button"
          >
            Pin / Update in swarms
          </button>
          <Link className="agent-detail__action" href="/registry">
            Open in Registry Hub
          </Link>
          <button
            className="agent-detail__action agent-detail__action--violet"
            onClick={() => {
              setTab("playground");
              announce(L(labels, "playground_is_local_preview_only_until_authorize"));
            }}
            type="button"
          >
            Run Playground
          </button>
        </div>
      </header>

      {feedback ? (
        <p aria-live="polite" className="agent-detail__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div
        aria-label={L(labels, "agent_detail_tabs")}
        className="agent-detail__tabs"
        role="tablist"
      >
        {AGENT_DETAIL_TABS.map((entry) => (
          <button
            aria-selected={tab === entry.id}
            className={
              tab === entry.id
                ? "agent-detail__tab agent-detail__tab--active"
                : "agent-detail__tab"
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

      <div className="agent-detail__panel">
        {tab === "history" ? (
          <HistoryTab
            view={view}
            labels={labels}
            onReplay={() =>
              announce(
                "Replay with latest common requires an authorized checkpoint action.",
              )
            }
          />
        ) : null}
        {tab === "config" ? (
          <ConfigTab
            view={view}
            onAnnounce={announce}
          />
        ) : null}
        {tab === "playground" ? (
          <PlaygroundTab
            view={view}
            input={playgroundInput}
            onInput={setPlaygroundInput}
            onAnnounce={announce}
           labels={labels} />
        ) : null}
        {tab === "knowledge" ? (
          <KnowledgeTab
            view={view}
            query={knowledgeQuery}
            onQuery={setKnowledgeQuery}
            onAnnounce={announce}
           labels={labels} />
        ) : null}
        {tab === "ops" ? <OpsTab view={view} onAnnounce={announce}  labels={labels} /> : null}
      </div>

      <p className="agent-detail__footer">{view.footerNote}</p>
    </section>
  );
}

function HistoryTab({
  view,
  onReplay,
  labels,
}: Readonly<{
  view: AgentDetailLandingView;
  onReplay: () => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="agent-detail__history">
      <div className="agent-detail__insight" role="status">
        <p>{view.insightStrip}</p>
        <button className="agent-detail__linkish" type="button">
          {view.yourUsageNote}
        </button>
      </div>

      <div
        aria-label={L(labels, "history_filters")}
        className="agent-detail__filters"
        role="group"
      >
        {view.historyFilters.map((filter) => (
          <button className="agent-detail__filter" key={filter} type="button">
            {filter} ▾
          </button>
        ))}
      </div>

      <div className="agent-detail__table-wrap" role="region" aria-label={L(labels, "cross_swarm_usage")}>
        <table className="agent-detail__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "timestamp")}</th>
              <th scope="col">{L(labels, "swarm_pattern")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "duration_tokens_cost")}</th>
              <th scope="col">{L(labels, "summary")}</th>
              <th scope="col">{L(labels, "action")}</th>
            </tr>
          </thead>
          <tbody>
            {view.usageRows.map((row) => (
              <UsageRow key={row.id} onReplay={onReplay} row={row} />
            ))}
          </tbody>
        </table>
      </div>
      <p className="agent-detail__pagination">{view.paginationLabel}</p>
    </div>
  );
}

function UsageRow({
  row,
  onReplay,
}: Readonly<{
  row: AgentDetailUsageRow;
  onReplay: () => void;
}>): JSX.Element {
  return (
    <tr>
      <td>{row.timestamp}</td>
      <td>
        <strong>{row.swarm}</strong>
        <span className="agent-detail__muted">{row.pattern}</span>
      </td>
      <td>
        <span
          className={`agent-detail__status-pill agent-detail__status-pill--${row.statusTone}`}
        >
          {row.status}
        </span>
      </td>
      <td className="agent-detail__metrics-cell">
        {row.duration} · {row.tokens} · {row.cost}
      </td>
      <td>{row.summary}</td>
      <td>
        <button className="agent-detail__linkish" onClick={onReplay} type="button">
          Replay ↻
        </button>
      </td>
    </tr>
  );
}

function ConfigTab({
  view,
  onAnnounce,
}: Readonly<{
  view: AgentDetailLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="agent-detail__config">
      <section
        aria-labelledby="version-timeline-heading"
        className="agent-detail__versions"
      >
        <h2 id="version-timeline-heading">
          Version Timeline &amp; Meta-Critic Rationale
        </h2>
        <ol className="agent-detail__version-list">
          {view.versions.map((version) => (
            <li
              className={`agent-detail__version agent-detail__version--${version.state}`}
              key={version.id}
            >
              <strong>{version.label}</strong>
              {version.delta ? <span>{version.delta}</span> : null}
            </li>
          ))}
        </ol>
        <article className="agent-detail__version-note">
          <p>{view.currentVersionNote}</p>
          <p>{view.metaCriticNote}</p>
          <p className="agent-detail__muted">{view.evidenceNote}</p>
        </article>
        <div className="agent-detail__config-actions">
          <button
            className="agent-detail__action agent-detail__action--primary"
            onClick={() =>
              onAnnounce(
                "Save as v3.1 proposal requires an authorized proposal action.",
              )
            }
            type="button"
          >
            Save as v3.1 proposal
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              onAnnounce("Compare versions is local-preview only.")
            }
            type="button"
          >
            Compare versions
          </button>
        </div>
      </section>

      <div className="agent-detail__config-grid">
        {view.configSummaries.map((section) => (
          <section className="agent-detail__config-card" key={section.id}>
            <h3>{section.title}</h3>
            <ul>
              {section.lines.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}

function PlaygroundTab({
  view,
  input,
  onInput,
  onAnnounce,
  labels,
}: Readonly<{
  view: AgentDetailLandingView;
  input: string;
  onInput: (value: string) => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="agent-detail__playground">
      <div className="agent-detail__chat">
        <div className="agent-detail__chat-options" role="group" aria-label={L(labels, "playground_options")}>
          <button className="agent-detail__filter" type="button">
            Model override ▾
          </button>
          <label className="agent-detail__check">
            <input defaultChecked type="checkbox" /> Enable Tools
          </label>
          <label className="agent-detail__check">
            <input defaultChecked type="checkbox" /> Stream
          </label>
          <button
            className="agent-detail__filter"
            onClick={() =>
              onAnnounce(
                "Inject Workflow / Pattern Context requires authorized swarm context.",
              )
            }
            type="button"
          >
            Inject Pattern Context ▾
          </button>
        </div>
        <ul className="agent-detail__messages">
          {view.playgroundMessages.map((message) => (
            <li
              className={`agent-detail__message agent-detail__message--${message.role}`}
              key={message.id}
            >
              <strong>{message.role}</strong>
              <p>{message.text}</p>
            </li>
          ))}
        </ul>
        <form
          className="agent-detail__composer"
          onSubmit={(event) => {
            event.preventDefault();
            onAnnounce(
              "Playground test requires an authorized playground action reference.",
            );
            onInput("");
          }}
        >
          <label className="visually-hidden" htmlFor="agent-playground-input">
            Playground prompt
          </label>
          <textarea
            id="agent-playground-input"
            onChange={(event) => onInput(event.target.value)}
            placeholder={L(labels, "test_this_common_agent_with_a_prompt")}
            rows={3}
            value={input}
          />
          <button className="agent-detail__action agent-detail__action--primary" type="submit">
            Run test
          </button>
        </form>
      </div>

      <aside className="agent-detail__side-panels" aria-label={L(labels, "playground_panels")}>
        <section className="agent-detail__side-card">
          <h3>{L(labels, "eval_harness")}</h3>
          <ul>
            {view.evalScores.map((score) => (
              <li key={score.metric}>
                <span>{score.metric}</span>
                <strong>{score.score}</strong>
              </li>
            ))}
          </ul>
          <button
            className="agent-detail__action"
            onClick={() =>
              onAnnounce("Common Eval Rubric requires an authorized eval action.")
            }
            type="button"
          >
            Run Common Eval Rubric
          </button>
        </section>
        <section className="agent-detail__side-card">
          <h3>{L(labels, "live_metrics")}</h3>
          <p className="agent-detail__muted">
            Tokens · cost · latency · tool usage appear when a playground run is authorized.
          </p>
        </section>
        <section className="agent-detail__side-card">
          <h3>{L(labels, "after_good_run")}</h3>
          <button
            className="agent-detail__action"
            onClick={() =>
              onAnnounce(
                "Training guide contribution requires an authorized contribution action.",
              )
            }
            type="button"
          >
            Mark as high-quality example
          </button>
          <button
            className="agent-detail__action agent-detail__action--violet"
            onClick={() =>
              onAnnounce(
                "Contribute to Common Knowledge requires an authorized contribution.",
              )
            }
            type="button"
          >
            Contribute to Common Knowledge?
          </button>
        </section>
      </aside>
    </div>
  );
}

function KnowledgeTab({
  view,
  query,
  onQuery,
  onAnnounce,
  labels,
}: Readonly<{
  view: AgentDetailLandingView;
  query: string;
  onQuery: (value: string) => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="agent-detail__knowledge">
      <ul className="agent-detail__knowledge-stats">
        {view.knowledgeStats.map((stat) => (
          <li key={stat.id}>
            <strong>{stat.value}</strong>
            <span>{stat.label}</span>
          </li>
        ))}
      </ul>

      <label className="agent-detail__search">
        <span className="visually-hidden">{L(labels, "search_knowledge")}</span>
        <input
          onChange={(event) => onQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              onAnnounce(
                "Knowledge search is local-preview only until retrieval is authorized.",
              );
            }
          }}
          placeholder={L(labels, "search_test_chunk_text_score_source")}
          value={query}
        />
      </label>

      <div className="agent-detail__table-wrap">
        <table className="agent-detail__table">
          <thead>
            <tr>
              <th scope="col">{L(labels, "name")}</th>
              <th scope="col">{L(labels, "type")}</th>
              <th scope="col">{L(labels, "status")}</th>
              <th scope="col">{L(labels, "chunks")}</th>
              <th scope="col">{L(labels, "added")}</th>
              <th scope="col">{L(labels, "actions")}</th>
            </tr>
          </thead>
          <tbody>
            {view.knowledgeSources.map((source) => (
              <tr key={source.id}>
                <td>
                  <strong>{source.name}</strong>
                </td>
                <td>{source.type}</td>
                <td>{source.status}</td>
                <td>{source.chunks}</td>
                <td>{source.added}</td>
                <td>
                  <button
                    className="agent-detail__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Source actions require authorized knowledge operations.",
                      )
                    }
                    type="button"
                  >
                    Preview
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="agent-detail__knowledge-actions">
        <button
          className="agent-detail__action"
          onClick={() =>
            onAnnounce("Add sources requires an authorized import action.")
          }
          type="button"
        >
          Add sources
        </button>
        <button
          className="agent-detail__action agent-detail__action--primary"
          onClick={() =>
            onAnnounce(
              "Distill / Synthesize to Common Knowledge requires an authorized contribution.",
            )
          }
          type="button"
        >
          Distill / Synthesize to Common Knowledge
        </button>
      </div>
      <p className="agent-detail__muted">
        Knowledge distinguishes RAG sources, few-shot examples, correction memory,
        constitutional rules, and evaluation benchmarks.
      </p>
    </div>
  );
}

function OpsTab({
  view,
  onAnnounce,
  labels,
}: Readonly<{
  view: AgentDetailLandingView;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="agent-detail__ops">
      <div className="agent-detail__ops-alert" role="status">
        <span aria-hidden="true">!</span>
        <p>{view.opsAlert}</p>
      </div>

      <ul className="agent-detail__ops-metrics">
        {view.opsMetrics.map((metric) => (
          <li key={metric.id}>
            <strong>{metric.value}</strong>
            <span>{metric.label}</span>
          </li>
        ))}
      </ul>

      <section className="agent-detail__ops-card">
        <h3>{L(labels, "where_used_this_exact_version")}</h3>
        <p>{view.opsWhereUsed}</p>
        <div className="agent-detail__ops-actions">
          <button
            className="agent-detail__action agent-detail__action--primary"
            onClick={() =>
              onAnnounce(
                "Safe Rollout All requires an authorized rollout action and approval workflow.",
              )
            }
            type="button"
          >
            Safe Rollout All
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              onAnnounce("A/B v3.0 vs v2.9 requires an authorized rollout contract.")
            }
            type="button"
          >
            A/B v3.0 vs v2.9
          </button>
          <button
            className="agent-detail__action"
            onClick={() =>
              onAnnounce("View Impact Analysis is local-preview only.")
            }
            type="button"
          >
            View Impact Analysis
          </button>
        </div>
        <p className="agent-detail__muted">
          Rollout is a separate server-governed action · approval workflow if shared
          commons.
        </p>
      </section>
    </div>
  );
}
