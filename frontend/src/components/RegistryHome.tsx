"use client";

/**
 * @duty RegistryHome — registry hub projection (ui_07)
 * @role Search/facet agent & pattern cards; embed specials; propose via host intents.
 * @controls Search, facets, cards, proposal actions, specials panel.
 * @must Keep demo proposals fail-closed; specials never activate production.
 * @mustnot Invent registry mutations without action refs.
 * @redesign docs/frontend_redesign/ui_07_registry_hub.md
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type RegistryAgentCard,
  type RegistryLandingView,
  type RegistryPatternCard,
  type RegistryViewMode,
} from "../lib/projections/registry-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { SpecialsCatalog } from "./SpecialsCatalog";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function RegistryHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: RegistryLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [mode, setMode] = useState<RegistryViewMode>("cards");
  const [search, setSearch] = useState("");
  const [activeFacets, setActiveFacets] = useState<ReadonlySet<string>>(
    () => new Set(),
  );
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [reviewOpen, setReviewOpen] = useState(true);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const toggleFacet = (facet: string): void => {
    setActiveFacets((current) => {
      const next = new Set(current);
      if (next.has(facet)) next.delete(facet);
      else next.add(facet);
      return next;
    });
  };

  const filteredAgents = useMemo(() => {
    const q = search.trim().toLowerCase();
    return view.agents.filter((agent) => {
      // Facets are badge or pack tags (video|specials, status, folder-local layout, …).
      for (const facet of activeFacets) {
        const f = facet.toLowerCase();
        const matchesBadge = agent.badges.some((badge) => badge.toLowerCase() === f);
        const matchesDomain = agent.domains.some((domain) => domain.toLowerCase() === f);
        const matchesCategory = (agent.category ?? "").toLowerCase() === f;
        if (!matchesBadge && !matchesDomain && !matchesCategory) {
          return false;
        }
      }
      if (q.length === 0) return true;
      return (
        agent.id.toLowerCase().includes(q) ||
        agent.name.toLowerCase().includes(q) ||
        agent.description.toLowerCase().includes(q) ||
        agent.versionLabel.toLowerCase().includes(q) ||
        agent.badges.some((badge) => badge.toLowerCase().includes(q)) ||
        (agent.category ?? "").toLowerCase().includes(q)
      );
    });
  }, [activeFacets, search, view]);

  return (
    <section aria-label={L(labels, "common_registry_hub")} className="registry-home">
      <header className="registry-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.subtitle}</p>
          <p className="registry-home__workspace">{view.workspaceLabel}</p>
        </div>
        <div className="registry-home__header-actions">
          <button
            className="registry-home__action"
            onClick={() =>
              announce(L(labels, "my_contributions_forks_require_an_authorized_pro"))
            }
            type="button"
          >
            My Contributions
          </button>
          <button
            className="registry-home__action"
            onClick={() => {
              setReviewOpen(true);
              announce(L(labels, "pending_proposals_shown_from_local_fixture"));
            }}
            type="button"
          >
            Pending Proposals
          </button>
          <Link className="registry-home__action registry-home__action--primary" href="/composer">
            ✧ Suggest New
          </Link>
        </div>
      </header>

      <div className="registry-home__toolbar">
        <label className="registry-home__search">
          <span className="visually-hidden">{L(labels, "search_registry")}</span>
          <input
            onChange={(event) => setSearch(event.target.value)}
            placeholder={view.searchPlaceholder}
            value={search}
          />
        </label>
        <div
          aria-label={L(labels, "view_mode")}
          className="registry-home__modes"
          role="group"
        >
          {(
            [
              ["cards", "Cards"],
              ["table", "Table"],
              ["graph", "Graph viz"],
            ] as const
          ).map(([id, label]) => (
            <button
              aria-pressed={mode === id}
              className={
                mode === id
                  ? "registry-home__mode registry-home__mode--active"
                  : "registry-home__mode"
              }
              key={id}
              onClick={() => setMode(id)}
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div
        aria-label={L(labels, "registry_facets")}
        className="registry-home__facets"
        role="group"
      >
        {view.facets.map((facet) => (
          <button
            aria-pressed={activeFacets.has(facet)}
            className={
              activeFacets.has(facet)
                ? "registry-home__facet registry-home__facet--active"
                : "registry-home__facet"
            }
            key={facet}
            onClick={() => toggleFacet(facet)}
            type="button"
          >
            {facet}
          </button>
        ))}
      </div>

      {feedback ? (
        <p aria-live="polite" className="registry-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="registry-home__body">
        <div className="registry-home__main">
          <section aria-labelledby="common-agents-heading">
            <h2 className="registry-home__section-label" id="common-agents-heading">
              Common Agents
            </h2>
            {mode === "cards" ? (
              <div className="registry-home__agent-grid">
                {filteredAgents.map((agent) => (
                  <AgentCard
                    agent={agent}
                    key={agent.id}
                    onAnnounce={announce}
                   labels={labels} />
                ))}
              </div>
            ) : null}
            {mode === "table" ? (
              <AgentTable agents={filteredAgents} onAnnounce={announce}  labels={labels} />
            ) : null}
            {mode === "graph" ? (
              <div className="registry-home__graph-placeholder panel">
                <p>
                  Graph viz is reserved for future knowledge/usage graph
                  projections. Cards and table remain primary discovery views.
                </p>
              </div>
            ) : null}
            {filteredAgents.length === 0 ? (
              <div className="registry-home__empty panel">
                <p>{L(labels, "no_commons_match_the_current_search_or_facets")}</p>
              </div>
            ) : null}
          </section>

          <section
            aria-labelledby="core-patterns-heading"
            className="registry-home__patterns-section"
          >
            <h2 className="registry-home__section-label" id="core-patterns-heading">
              Core Common Swarm Patterns
            </h2>
            <div className="registry-home__pattern-grid">
              {view.patterns.map((pattern) => (
                <PatternCard
                  key={pattern.id}
                  onAnnounce={announce}
                  pattern={pattern}
                />
              ))}
            </div>
          </section>

          <section
            aria-labelledby="proposals-heading"
            className="registry-home__proposals-section"
          >
            <div className="registry-home__section-head">
              <h2 id="proposals-heading">{L(labels, "pending_proposals")}</h2>
              <button
                className="registry-home__linkish"
                onClick={() => setReviewOpen((open) => !open)}
                type="button"
              >
                {reviewOpen ? "Hide review" : "Show review"}
              </button>
            </div>
            <ul className="registry-home__proposals">
              {view.proposals.map((proposal) => (
                <li key={proposal.id}>
                  <div>
                    <strong>{proposal.title}</strong>
                    <span>{proposal.detail}</span>
                  </div>
                  <button
                    className={
                      proposal.primary
                        ? "registry-home__action registry-home__action--primary"
                        : "registry-home__action"
                    }
                    onClick={() => {
                      setReviewOpen(true);
                      announce(
                        "Review & Merge requires an authorized governance action.",
                      );
                    }}
                    type="button"
                  >
                    Review &amp; Merge
                  </button>
                </li>
              ))}
            </ul>

            {reviewOpen ? (
              <div
                aria-label={L(labels, "proposal_review")}
                className="registry-home__review"
              >
                <h3>{view.reviewTitle}</h3>
                <div className="registry-home__review-grid">
                  <section className="registry-home__diff">
                    <h4>{L(labels, "spec_diff_redacted")}</h4>
                    <pre>
                      {view.reviewDiffLines.map((line) => (
                        <span
                          className={
                            line.startsWith("+")
                              ? "registry-home__diff-add"
                              : line.startsWith("-")
                                ? "registry-home__diff-del"
                                : undefined
                          }
                          key={line}
                        >
                          {line}
                          {"\n"}
                        </span>
                      ))}
                    </pre>
                  </section>
                  <section className="registry-home__impact">
                    <h4>{L(labels, "impact_analysis")}</h4>
                    <dl>
                      {view.impactRows.map((row) => (
                        <div key={row.label}>
                          <dt>{row.label}</dt>
                          <dd>{row.value}</dd>
                        </div>
                      ))}
                    </dl>
                    <p>{view.impactDomains}</p>
                    <div className="registry-home__review-actions">
                      <button
                        className="registry-home__action registry-home__action--primary"
                        onClick={() =>
                          announce(
                            "Approve & Merge requires an authorized governance action.",
                          )
                        }
                        type="button"
                      >
                        Approve &amp; Merge
                      </button>
                      <button
                        className="registry-home__action"
                        onClick={() =>
                          announce(
                            "Request Changes requires an authorized governance action.",
                          )
                        }
                        type="button"
                      >
                        Request Changes
                      </button>
                      <button
                        className="registry-home__action registry-home__action--danger"
                        onClick={() =>
                          announce(
                            "Reject requires an authorized governance action.",
                          )
                        }
                        type="button"
                      >
                        Reject
                      </button>
                    </div>
                  </section>
                </div>
              </div>
            ) : null}
          </section>
        </div>

        <aside aria-label={L(labels, "registry_stats_2")} className="registry-home__sidebar">
          <h2>{L(labels, "registry_stats")}</h2>
          <ul className="registry-home__stats">
            {view.stats.map((stat) => (
              <li key={stat.id}>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </li>
            ))}
          </ul>
          <section className="registry-home__your-impact">
            <h3>{L(labels, "your_impact")}</h3>
            <p>{view.yourImpact}</p>
            <Link className="registry-home__linkish" href="/evaluations">
              Full Eval Dashboard →
            </Link>
            <Link className="registry-home__linkish" href="/activity">
              Rollout History →
            </Link>
          </section>
        </aside>
      </div>

      <SpecialsCatalog view={view.specials} />

      <p className="registry-home__footer">{view.footerNote}</p>
    </section>
  );
}

function AgentCard({
  agent,
  onAnnounce,
  labels,
}: Readonly<{
  agent: RegistryAgentCard;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <article className="registry-home__agent-card">
      <div className="registry-home__agent-top">
        <span aria-hidden="true" className="registry-home__agent-icon">
          {agent.name.slice(0, 1)}
        </span>
        <div>
          <div className="registry-home__agent-title-row">
            <h3>{agent.name}</h3>
            {agent.isNew ? <span className="registry-home__new">{L(labels, "new")}</span> : null}
          </div>
          <span className="registry-home__version">{agent.versionLabel}</span>
        </div>
      </div>
      <p>{agent.description}</p>
      <dl className="registry-home__metrics">
        <div>
          <dt>{L(labels, "success")}</dt>
          <dd>{agent.success}</dd>
        </div>
        <div>
          <dt>{L(labels, "avg_tok")}</dt>
          <dd>{agent.avgTokens}</dd>
        </div>
        <div>
          <dt>{L(labels, "latency")}</dt>
          <dd>{agent.latency}</dd>
        </div>
      </dl>
      <p className="registry-home__usage">{agent.usage}</p>
      <ul className="registry-home__badges">
        {agent.badges.map((badge) => (
          <li key={badge}>{badge}</li>
        ))}
      </ul>
      {agent.category || agent.architecture || agent.critiqueCompat ? (
        <p className="registry-home__va">
          {[agent.category, agent.architecture, agent.critiqueCompat]
            .filter(Boolean)
            .join(" · ")}
        </p>
      ) : null}
      <div className="registry-home__card-actions">
        <button
          className="registry-home__action registry-home__action--primary"
          onClick={() =>
            onAnnounce(
              "Add to Swarm / Instantiate requires an authorized draft action.",
            )
          }
          type="button"
        >
          Add to Swarm
        </button>
        <button
          className="registry-home__action"
          onClick={() =>
            onAnnounce(
              "Propose Improvement requires an authorized proposal action.",
            )
          }
          type="button"
        >
          Propose
        </button>
        <Link
          className="registry-home__action"
          href={`/registry/agents/${agent.id}`}
        >
          Detail
        </Link>
      </div>
    </article>
  );
}

function AgentTable({
  agents,
  onAnnounce,
  labels,
}: Readonly<{
  agents: readonly RegistryAgentCard[];
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="registry-home__table-wrap">
      <table className="registry-home__table">
        <thead>
          <tr>
            <th scope="col">{L(labels, "agent")}</th>
            <th scope="col">{L(labels, "version")}</th>
            <th scope="col">{L(labels, "success")}</th>
            <th scope="col">{L(labels, "usage")}</th>
            <th scope="col">{L(labels, "actions")}</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <tr key={agent.id}>
              <td>
                <strong>{agent.name}</strong>
                <span className="registry-home__muted">{agent.description}</span>
              </td>
              <td>
                <span className="registry-home__version">{agent.versionLabel}</span>
              </td>
              <td>{agent.success}</td>
              <td>{agent.usage}</td>
              <td>
                <button
                  className="registry-home__linkish"
                  onClick={() =>
                    onAnnounce(
                      "Add to Swarm requires an authorized draft action.",
                    )
                  }
                  type="button"
                >
                  Add
                </button>
                <Link
                  className="registry-home__linkish"
                  href={`/registry/agents/${agent.id}`}
                >
                  Detail
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PatternCard({
  pattern,
  onAnnounce,
}: Readonly<{
  pattern: RegistryPatternCard;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <article
      className={`registry-home__pattern-card registry-home__pattern-card--${pattern.previewStyle}`}
    >
      <div className="registry-home__pattern-preview" aria-hidden="true">
        <span>{pattern.icon}</span>
        <i />
        <i />
        <i />
      </div>
      <h3>{pattern.name}</h3>
      <p>{pattern.whenToUse}</p>
      <p className="registry-home__usage">{pattern.metrics}</p>
      <div className="registry-home__card-actions">
        <Link
          className="registry-home__action registry-home__action--primary"
          href="/canvas"
        >
          Instantiate in Canvas
        </Link>
        <button
          className="registry-home__action"
          onClick={() =>
            onAnnounce(
              "Fork as Custom Pattern requires an authorized fork action.",
            )
          }
          type="button"
        >
          Fork Pattern
        </button>
      </div>
    </article>
  );
}
