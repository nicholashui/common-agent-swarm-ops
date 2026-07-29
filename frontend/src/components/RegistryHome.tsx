"use client";

/**
 * @duty RegistryHome — registry hub projection (ui_07)
 * @role Search/facet agent & pattern cards; embed specials; propose via host intents.
 * @controls Search, facets, cards/table/graph modes, proposal actions, specials panel.
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
import {
  REGISTRY_VIEW_MODES,
  filterRegistryAgents,
  filterRegistryPatterns,
  toggleFacetSelection,
} from "../lib/ui/registry-filters";
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
  const [contributionsOpen, setContributionsOpen] = useState(false);
  const [selectedGraphId, setSelectedGraphId] = useState<string | undefined>();
  /** Progressive list window — keeps first paint light when catalog is large. */
  const [visibleLimit, setVisibleLimit] = useState(36);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const filteredAgents = useMemo(
    () =>
      filterRegistryAgents(
        view.agents,
        search,
        activeFacets,
        view.domainFacets,
      ),
    [activeFacets, search, view.agents, view.domainFacets],
  );

  const filteredPatterns = useMemo(
    () => filterRegistryPatterns(view.patterns, search),
    [search, view.patterns],
  );

  const visibleAgents = useMemo(
    () => filteredAgents.slice(0, visibleLimit),
    [filteredAgents, visibleLimit],
  );

  // Reset window when filters change so search feels instant on small result sets.
  React.useEffect(() => {
    setVisibleLimit(36);
  }, [search, activeFacets]);

  const onToggleFacet = (facet: string): void => {
    setActiveFacets((current) => {
      const next = toggleFacetSelection(current, facet);
      const applied = next.has(facet);
      setStatusMessage(
        applied
          ? `Facet “${facet}” on · ${filterRegistryAgents(view.agents, search, next, view.domainFacets).length} agents`
          : `Facet “${facet}” off · ${filterRegistryAgents(view.agents, search, next, view.domainFacets).length} agents`,
      );
      return next;
    });
  };

  const onModeChange = (next: RegistryViewMode): void => {
    setMode(next);
    setStatusMessage(
      next === "graph"
        ? `Graph viz · ${filteredAgents.length} agents (local layout)`
        : next === "table"
          ? `Table view · ${filteredAgents.length} agents`
          : `Cards view · ${filteredAgents.length} agents`,
    );
  };

  const clearFilters = (): void => {
    setSearch("");
    setActiveFacets(new Set());
    setStatusMessage(`Filters cleared · ${view.agents.length} agents`);
  };

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
            aria-expanded={contributionsOpen}
            className={
              contributionsOpen
                ? "registry-home__action registry-home__action--primary"
                : "registry-home__action"
            }
            onClick={() => {
              setContributionsOpen((open) => {
                const next = !open;
                setStatusMessage(
                  next
                    ? L(labels, "my_contributions_local_note")
                    : "My Contributions panel closed.",
                );
                return next;
              });
            }}
            type="button"
          >
            My Contributions
          </button>
          <button
            className="registry-home__action"
            onClick={() => {
              setReviewOpen(true);
              const count = (view.proposals ?? []).length;
              setStatusMessage(
                count === 0
                  ? L(labels, "pending_proposals_empty_note")
                  : Lfmt(labels, "pending_proposals_count_note", {
                      count: String(count),
                    }),
              );
              if (typeof document !== "undefined") {
                document
                  .getElementById("proposals-heading")
                  ?.scrollIntoView({ behavior: "smooth", block: "start" });
              }
            }}
            type="button"
          >
            Pending Proposals
            {(view.proposals ?? []).length > 0
              ? ` (${(view.proposals ?? []).length})`
              : ""}
          </button>
          <Link className="registry-home__action registry-home__action--primary" href="/composer">
            ✧ Suggest New
          </Link>
        </div>
      </header>

      {contributionsOpen ? (
        <section
          aria-label="My contributions and forks"
          className="registry-home__contributions"
        >
          <h2>My Contributions &amp; Forks</h2>
          <p className="registry-home__muted">
            {L(labels, "my_contributions_local_note")}
          </p>
          <ul className="registry-home__contributions-list">
            <li>
              <strong>Proposals</strong>
              <span>
                {(view.proposals ?? []).length} pending in this workspace
                projection (not necessarily yours alone).
              </span>
            </li>
            <li>
              <strong>Personal forks</strong>
              <span>
                None listed in the local pack catalog. Host contribution
                projection will populate this list when linked.
              </span>
            </li>
          </ul>
          <p className="registry-home__muted">
            To propose an improvement, open an agent card and use{" "}
            <strong>Propose</strong> when the Host returns an eligible action
            reference — or use pack-backed detail for inspection only.
          </p>
        </section>
      ) : null}

      <div className="registry-home__toolbar">
        <label className="registry-home__search">
          <span className="visually-hidden">{L(labels, "search_registry")}</span>
          <input
            aria-controls="registry-agent-results"
            autoComplete="off"
            name="registry-search"
            onChange={(event) => {
              const value = event.target.value;
              setSearch(value);
              const count = filterRegistryAgents(
                view.agents,
                value,
                activeFacets,
                view.domainFacets,
              ).length;
              setStatusMessage(
                value.trim().length === 0
                  ? `Search cleared · ${count} agents`
                  : `Search “${value.trim()}” · ${count} agents`,
              );
            }}
            placeholder={view.searchPlaceholder}
            type="search"
            value={search}
          />
        </label>
        <div
          aria-label={L(labels, "view_mode")}
          className="registry-home__modes"
          role="group"
        >
          {REGISTRY_VIEW_MODES.map((entry) => (
            <button
              aria-pressed={mode === entry.id}
              className={
                mode === entry.id
                  ? "registry-home__mode registry-home__mode--active"
                  : "registry-home__mode"
              }
              key={entry.id}
              onClick={() => onModeChange(entry.id)}
              type="button"
            >
              {entry.label}
            </button>
          ))}
        </div>
        {search.trim().length > 0 || activeFacets.size > 0 ? (
          <button
            className="registry-home__action"
            onClick={clearFilters}
            type="button"
          >
            Clear filters
          </button>
        ) : null}
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
            onClick={() => onToggleFacet(facet)}
            type="button"
          >
            {facet}
          </button>
        ))}
      </div>

      <p
        aria-live="polite"
        className="registry-home__result-meta"
        id="registry-agent-results"
        role="status"
      >
        Showing <strong>{filteredAgents.length}</strong> of {view.agents.length}{" "}
        agents
        {activeFacets.size > 0
          ? ` · facets: ${[...activeFacets].join(", ")}`
          : ""}
        {search.trim().length > 0 ? ` · query: “${search.trim()}”` : ""}
        {` · view: ${mode}`}
      </p>

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
              <div className="registry-home__agent-grid" data-registry-view="cards">
                {visibleAgents.map((agent) => (
                  <AgentCard
                    agent={agent}
                    key={agent.id}
                    labels={labels}
                    onAction={onAction}
                    onAnnounce={announce}
                  />
                ))}
              </div>
            ) : null}
            {mode === "table" ? (
              <div data-registry-view="table">
                <AgentTable
                  agents={visibleAgents}
                  labels={labels}
                  onAnnounce={announce}
                />
              </div>
            ) : null}
            {mode === "graph" ? (
              <RegistryGraph
                agents={filteredAgents}
                labels={labels}
                onSelect={setSelectedGraphId}
                selectedId={selectedGraphId}
              />
            ) : null}
            {filteredAgents.length > visibleLimit && mode !== "graph" ? (
              <div className="registry-home__more">
                <button
                  className="registry-home__action registry-home__action--primary"
                  onClick={() =>
                    setVisibleLimit((n) => Math.min(n + 36, filteredAgents.length))
                  }
                  type="button"
                >
                  Show more ({visibleLimit} of {filteredAgents.length})
                </button>
              </div>
            ) : null}
            {filteredAgents.length === 0 ? (
              <div className="registry-home__empty panel">
                <p>{L(labels, "no_commons_match_the_current_search_or_facets")}</p>
                <button
                  className="registry-home__action registry-home__action--primary"
                  onClick={clearFilters}
                  type="button"
                >
                  Clear filters
                </button>
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
              {filteredPatterns.map((pattern) => (
                <PatternCard
                  key={pattern.id}
                  onAnnounce={announce}
                  pattern={pattern}
                />
              ))}
            </div>
            {filteredPatterns.length === 0 ? (
              <p className="registry-home__empty panel">
                No patterns match the current search.
              </p>
            ) : null}
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
            {(view.proposals ?? []).length === 0 ? (
              <p className="registry-home__empty panel">
                {L(labels, "pending_proposals_empty_note")}
              </p>
            ) : (
              <ul className="registry-home__proposals">
                {(view.proposals ?? []).map((proposal) => (
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
            )}

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
          <p className="registry-home__sidebar-filter">
            Filtered view: <strong>{filteredAgents.length}</strong>
          </p>
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

      <SpecialsCatalog
        activeFacets={activeFacets}
        domainFacets={view.domainFacets}
        onSearchChange={setSearch}
        search={search}
        view={view.specials}
      />

      <p className="registry-home__footer">{view.footerNote}</p>
    </section>
  );
}

function AgentCard({
  agent,
  onAnnounce,
  onAction,
  labels,
}: Readonly<{
  agent: RegistryAgentCard;
  onAnnounce: (message: string) => void;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
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
          onClick={() => {
            if (onAction) {
              void onAction({
                kind: "commons.propose",
                agentId: agent.id,
                summary: `Improvement proposal for ${agent.name} (${agent.id}).`,
              });
              return;
            }
            onAnnounce(
              "Propose Improvement requires an authorized proposal action.",
            );
          }}
          type="button"
        >
          Propose
        </button>
        <Link
          className="registry-home__action"
          href={`/registry/agents/${encodeURIComponent(agent.id)}`}
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
                <span className="registry-home__muted">{agent.id}</span>
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
                  href={`/registry/agents/${encodeURIComponent(agent.id)}`}
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

function RegistryGraph({
  agents,
  selectedId,
  onSelect,
  labels,
}: Readonly<{
  agents: readonly RegistryAgentCard[];
  selectedId?: string;
  onSelect: (id: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  const nodes = agents.slice(0, 48);
  const selected =
    nodes.find((agent) => agent.id === selectedId) ?? nodes[0];

  return (
    <div className="registry-home__graph panel" data-registry-view="graph">
      <p className="registry-home__graph-note">
        Local graph layout of up to 48 matching agents (not a host topology run).
        Select a node to inspect pack identity.
      </p>
      <div
        aria-label={L(labels, "common_registry_hub")}
        className="registry-home__graph-canvas"
        role="list"
      >
        {nodes.map((agent) => (
          <button
            aria-pressed={selected?.id === agent.id}
            className={
              selected?.id === agent.id
                ? "registry-home__graph-node registry-home__graph-node--selected"
                : "registry-home__graph-node"
            }
            key={agent.id}
            onClick={() => onSelect(agent.id)}
            role="listitem"
            title={agent.id}
            type="button"
          >
            <strong>{agent.name}</strong>
            <span>{agent.category ?? agent.badges[0] ?? "agent"}</span>
          </button>
        ))}
      </div>
      {selected ? (
        <div className="registry-home__graph-detail">
          <h3>{selected.name}</h3>
          <p>
            <code>{selected.id}</code>
          </p>
          <p>{selected.description}</p>
          <Link
            className="registry-home__action registry-home__action--primary"
            href={`/registry/agents/${encodeURIComponent(selected.id)}`}
          >
            Open detail
          </Link>
        </div>
      ) : null}
      {nodes.length === 0 ? (
        <p className="registry-home__empty">No agents to layout for this filter.</p>
      ) : null}
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
