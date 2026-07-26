"use client";

import React, { useMemo, useState } from "react";

import {
  LOCAL_KNOWLEDGE_LANDING,
  type KnowledgeDetailTab,
  type KnowledgeLandingView,
} from "../lib/projections/knowledge-landing";

export function KnowledgeHome({
  view = LOCAL_KNOWLEDGE_LANDING,
}: Readonly<{ view?: KnowledgeLandingView }>): JSX.Element {
  const [query, setQuery] = useState("");
  const [facet, setFacet] = useState("All types");
  const [selectedId, setSelectedId] = useState(view.selectedCollectionId);
  const [detailTab, setDetailTab] = useState<KnowledgeDetailTab>("sources");
  const [searchTest, setSearchTest] = useState(view.searchQuery);
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => setStatusMessage(message);

  const collections = useMemo(() => {
    const q = query.trim().toLowerCase();
    return view.collections.filter((collection) => {
      if (facet === "Common" && collection.scope !== "common") return false;
      if (facet === "Business-scoped" && collection.scope !== "business") {
        return false;
      }
      if (facet === "Health" && collection.health !== "healthy") return false;
      if (q.length === 0) return true;
      return (
        collection.name.toLowerCase().includes(q) ||
        collection.syncDetail.toLowerCase().includes(q)
      );
    });
  }, [facet, query, view.collections]);

  const selected =
    view.collections.find((collection) => collection.id === selectedId) ??
    view.collections[0];

  return (
    <section aria-label="Knowledge management hub" className="knowledge-home">
      <header className="knowledge-home__header">
        <div>
          <p className="eyebrow">KNOWLEDGE</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
        </div>
        <div className="knowledge-home__header-actions">
          <label className="knowledge-home__search">
            <span className="visually-hidden">Search collections</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={query}
            />
          </label>
          <button
            className="knowledge-home__action knowledge-home__action--primary"
            onClick={() =>
              announce(
                "Add source requires an authorized ingestion action with server-defined type/size/ownership/retention.",
              )
            }
            type="button"
          >
            + Add source
          </button>
          <button
            className="knowledge-home__action"
            onClick={() =>
              announce(
                "Sync from Git requires an authorized sync job. URLs remain untrusted refs until server ingestion.",
              )
            }
            type="button"
          >
            Sync from Git
          </button>
        </div>
      </header>

      <div
        aria-label="Knowledge facets"
        className="knowledge-home__facets"
        role="group"
      >
        {view.facets.map((entry) => (
          <button
            aria-pressed={facet === entry}
            className={
              facet === entry
                ? "knowledge-home__facet knowledge-home__facet--active"
                : "knowledge-home__facet"
            }
            key={entry}
            onClick={() => setFacet(entry)}
            type="button"
          >
            {entry}
          </button>
        ))}
      </div>

      {statusMessage ? (
        <p aria-live="polite" className="knowledge-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="knowledge-home__body">
        <div className="knowledge-home__main">
          <section aria-labelledby="collections-heading">
            <h2 className="knowledge-home__section-label" id="collections-heading">
              Collections
            </h2>
            {collections.length === 0 ? (
              <div className="knowledge-home__empty panel">
                <p>No collections match the current filters.</p>
              </div>
            ) : (
              <div className="knowledge-home__grid">
                {collections.map((collection) => (
                  <button
                    aria-pressed={selectedId === collection.id}
                    className={
                      selectedId === collection.id
                        ? `knowledge-home__card knowledge-home__card--${collection.health} knowledge-home__card--selected`
                        : `knowledge-home__card knowledge-home__card--${collection.health}`
                    }
                    key={collection.id}
                    onClick={() => setSelectedId(collection.id)}
                    type="button"
                  >
                    <div className="knowledge-home__card-top">
                      <strong>{collection.name}</strong>
                      <span
                        className={`knowledge-home__health knowledge-home__health--${collection.health}`}
                      >
                        {collection.healthLabel}
                      </span>
                    </div>
                    <dl className="knowledge-home__stats">
                      <div>
                        <dt>Chunks</dt>
                        <dd>{collection.chunks}</dd>
                      </div>
                      <div>
                        <dt>Scope</dt>
                        <dd>{collection.scope}</dd>
                      </div>
                    </dl>
                    <p>{collection.syncDetail}</p>
                    <ul className="knowledge-home__bindings">
                      {collection.bindingKinds.map((kind) => (
                        <li key={kind}>{kind}</li>
                      ))}
                    </ul>
                  </button>
                ))}
              </div>
            )}
          </section>

          {selected ? (
            <section
              aria-label={`${selected.name} detail`}
              className="knowledge-home__detail"
            >
              <header className="knowledge-home__detail-head">
                <h2>{selected.name} — Detail</h2>
                <span
                  className={`knowledge-home__health knowledge-home__health--${selected.health}`}
                >
                  {selected.healthLabel}
                </span>
              </header>

              <div
                aria-label="Collection detail tabs"
                className="knowledge-home__tabs"
                role="tablist"
              >
                {(
                  [
                    ["sources", "Sources"],
                    ["search", "Search Test"],
                    ["config", "Config"],
                    ["contributions", "Contributions"],
                    ["analytics", "Analytics"],
                  ] as const
                ).map(([id, label]) => (
                  <button
                    aria-selected={detailTab === id}
                    className={
                      detailTab === id
                        ? "knowledge-home__tab knowledge-home__tab--active"
                        : "knowledge-home__tab"
                    }
                    key={id}
                    onClick={() => setDetailTab(id)}
                    role="tab"
                    type="button"
                  >
                    {label}
                  </button>
                ))}
              </div>

              {detailTab === "sources" ? (
                <SourcesPanel view={view} onAnnounce={announce} />
              ) : null}
              {detailTab === "search" ? (
                <SearchPanel
                  view={view}
                  query={searchTest}
                  onQuery={setSearchTest}
                  onAnnounce={announce}
                />
              ) : null}
              {detailTab === "config" ? <ConfigPanel view={view} /> : null}
              {detailTab === "contributions" ? (
                <ContributionsPanel view={view} onAnnounce={announce} />
              ) : null}
              {detailTab === "analytics" ? (
                <AnalyticsPanel view={view} />
              ) : null}
            </section>
          ) : null}
        </div>

        <aside aria-label="Sync jobs" className="knowledge-home__sidebar">
          <h2>Sync Jobs</h2>
          <ul className="knowledge-home__jobs">
            {view.syncJobs.map((job) => (
              <li key={job.id}>
                <strong>{job.label}</strong>
                <span className="knowledge-home__job-status">{job.status}</span>
                <p>{job.note}</p>
              </li>
            ))}
          </ul>
          <p className="knowledge-home__governance" role="note">
            {view.governanceNote}
          </p>
        </aside>
      </div>

      <p className="knowledge-home__footer">{view.footerNote}</p>
    </section>
  );
}

function SourcesPanel({
  view,
  onAnnounce,
}: Readonly<{
  view: KnowledgeLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="knowledge-home__panel">
      <div className="knowledge-home__table-wrap">
        <table className="knowledge-home__table">
          <thead>
            <tr>
              <th scope="col">Source</th>
              <th scope="col">Type</th>
              <th scope="col">Status</th>
              <th scope="col">Chunks</th>
              <th scope="col">License / kind</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {view.sources.map((source) => (
              <tr key={source.id}>
                <td>
                  <strong>{source.name}</strong>
                </td>
                <td>{source.type}</td>
                <td>{source.status}</td>
                <td>{source.chunks}</td>
                <td>
                  {source.license}
                  <span className="knowledge-home__muted">
                    {source.bindingKind}
                  </span>
                </td>
                <td>
                  <button
                    className="knowledge-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Preview requires an authorized knowledge projection.",
                      )
                    }
                    type="button"
                  >
                    Preview
                  </button>
                  <button
                    className="knowledge-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Reindex requires an authorized knowledge action.",
                      )
                    }
                    type="button"
                  >
                    Reindex
                  </button>
                  <button
                    className="knowledge-home__linkish"
                    onClick={() =>
                      onAnnounce(
                        "Contribute to common requires verification + approval — not retrieval alone.",
                      )
                    }
                    type="button"
                  >
                    Contribute
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="knowledge-home__drop" role="region" aria-label="Upload area">
        <p>
          Drag &amp; drop files · or paste text · or &quot;Sync from Git&quot;
        </p>
        <p className="knowledge-home__muted">
          Server-defined type/size/ownership/retention shown before submit ·
          client checks aren&apos;t authorization
        </p>
      </div>
    </div>
  );
}

function SearchPanel({
  view,
  query,
  onQuery,
  onAnnounce,
}: Readonly<{
  view: KnowledgeLandingView;
  query: string;
  onQuery: (value: string) => void;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="knowledge-home__panel">
      <h3>Search Test</h3>
      <form
        className="knowledge-home__search-test"
        onSubmit={(event) => {
          event.preventDefault();
          onAnnounce(
            "Hybrid search test requires an authorized retrieval endpoint.",
          );
        }}
      >
        <label className="visually-hidden" htmlFor="knowledge-search-test">
          Search test query
        </label>
        <input
          id="knowledge-search-test"
          onChange={(event) => onQuery(event.target.value)}
          value={query}
        />
        <button className="knowledge-home__action knowledge-home__action--primary" type="submit">
          Run search
        </button>
      </form>
      <ul className="knowledge-home__hits">
        {view.searchHits.map((hit) => (
          <li key={hit.id}>
            <div className="knowledge-home__hit-top">
              <strong>{hit.score}</strong>
              <span>{hit.metadata}</span>
            </div>
            <p>{hit.snippet}</p>
            <div className="knowledge-home__actions">
              <button
                className="knowledge-home__linkish"
                onClick={() =>
                  onAnnounce(
                    "Add to prompt is local-preview only until playground context is authorized.",
                  )
                }
                type="button"
              >
                Add to prompt
              </button>
              <button
                className="knowledge-home__linkish"
                onClick={() =>
                  onAnnounce(
                    "Relevance feedback requires an authorized retrieval feedback action.",
                  )
                }
                type="button"
              >
                Relevance feedback
              </button>
            </div>
          </li>
        ))}
      </ul>
      <section aria-label="Redacted retrieval trace" className="knowledge-home__trace">
        <h4>Retrieval trace (redacted)</h4>
        <ul>
          {view.retrievalTrace.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function ConfigPanel({
  view,
}: Readonly<{ view: KnowledgeLandingView }>): JSX.Element {
  return (
    <div className="knowledge-home__panel">
      <h3>Chunking &amp; indexing config</h3>
      <dl className="knowledge-home__config">
        {view.chunkingConfig.map((item) => (
          <div key={item.label}>
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
          </div>
        ))}
      </dl>
      <p className="knowledge-home__muted">
        Distinguishes licensed references, RAG collections, few-shot examples,
        correction/Reflexion memory, constitutional rules, continuity/budget
        memory, and evaluation benchmarks.
      </p>
    </div>
  );
}

function ContributionsPanel({
  view,
  onAnnounce,
}: Readonly<{
  view: KnowledgeLandingView;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="knowledge-home__panel">
      <h3>Contribution Queue (verified runs)</h3>
      <ul className="knowledge-home__contributions">
        {view.contributions.map((item) => (
          <li key={item.id}>
            <div>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
              <span className="knowledge-home__muted">{item.verification}</span>
            </div>
            <button
              className="knowledge-home__action knowledge-home__action--primary"
              onClick={() =>
                onAnnounce(
                  "Approve contribution requires verification + governance approval. Not promoted solely because retrieved/generated.",
                )
              }
              type="button"
            >
              Approve
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AnalyticsPanel({
  view,
}: Readonly<{ view: KnowledgeLandingView }>): JSX.Element {
  return (
    <div className="knowledge-home__panel">
      <h3>Analytics</h3>
      <p className="knowledge-home__muted">
        Query patterns and agent usage analytics appear when authorized metrics
        projections are available. Local preview only.
      </p>
      <ul className="knowledge-home__analytics">
        <li>
          <strong>Collections</strong>
          <span>{view.collections.length}</span>
        </li>
        <li>
          <strong>Sources in detail</strong>
          <span>{view.sources.length}</span>
        </li>
        <li>
          <strong>Pending contributions</strong>
          <span>{view.contributions.length}</span>
        </li>
      </ul>
    </div>
  );
}
