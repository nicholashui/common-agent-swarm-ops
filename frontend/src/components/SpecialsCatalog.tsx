"use client";

/**
 * @duty SpecialsCatalog — specials pack catalog panel
 * @role List draft/non-active specials agents; share Registry Hub filters; never production-activate.
 * @controls Optional local search bound to parent registry search; in-app links.
 * @must Show disclaimer/draft status; SafeContent for untrusted summary text.
 * @mustnot Activate specials or claim production readiness.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.5; ui_07_registry_hub.md embed
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type SpecialsLandingView,
} from "../lib/projections/specials-landing";
import { L } from "../lib/projections/screen-labels";
import { filterSpecialAgents } from "../lib/ui/registry-filters";
import { SafeContent } from "./projection/SafeContent";

export function SpecialsCatalog({
  view,
  search = "",
  activeFacets,
  domainFacets = ["video", "specials"],
  onSearchChange,
}: Readonly<{
  view: SpecialsLandingView;
  /** Shared Registry Hub search string (filters this pack too). */
  search?: string;
  activeFacets?: ReadonlySet<string>;
  domainFacets?: readonly string[];
  /** When set, specials search box drives the shared registry search. */
  onSearchChange?: (value: string) => void;
}>): JSX.Element {
  const labels = view.labels;
  const facets = activeFacets ?? new Set<string>();
  const [localQuery, setLocalQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  // Prefer shared registry search when parent wires it; else local-only refine.
  const effectiveSearch = onSearchChange ? search : localQuery || search;

  const agents = useMemo(
    () => filterSpecialAgents(view.agents, effectiveSearch, facets, domainFacets),
    [domainFacets, effectiveSearch, facets, view.agents],
  );

  const onQueryChange = (value: string): void => {
    if (onSearchChange) {
      onSearchChange(value);
      return;
    }
    setLocalQuery(value);
  };

  return (
    <section aria-label={L(labels, "special_agents_pack_catalog")} className="specials-catalog">
      <header className="specials-catalog__header">
        <div>
          <p className="eyebrow">{L(labels, "specials_pack_draft")}</p>
          <h2>{view.title}</h2>
          <p className="lede">{view.subtitle}</p>
        </div>
        <label className="specials-catalog__search">
          <span className="visually-hidden">{L(labels, "search_special_agents")}</span>
          <input
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder={L(labels, "search_specials_by_id_or_title")}
            type="search"
            value={onSearchChange ? search : localQuery}
          />
        </label>
      </header>

      <p className="specials-catalog__disclaimer" role="note">
        {view.disclaimer}
      </p>

      {effectiveSearch.trim().length > 0 || facets.size > 0 ? (
        <p className="specials-catalog__filter-note" role="status">
          Showing <strong>{agents.length}</strong> of {view.agents.length} specials
          {effectiveSearch.trim().length > 0
            ? ` · query: “${effectiveSearch.trim()}”`
            : ""}
          {facets.size > 0
            ? ` · facets: ${[...facets].join(", ")}`
            : ""}
        </p>
      ) : null}

      {statusMessage ? (
        <p aria-live="polite" className="specials-catalog__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      {agents.length === 0 ? (
        <p className="specials-catalog__empty">
          {effectiveSearch.trim().length > 0 || facets.size > 0
            ? "No special agents match the current registry search or facets."
            : view.emptyLabel}
        </p>
      ) : (
        <ul className="specials-catalog__list">
          {agents.map((agent) => (
            <li className="specials-catalog__card" key={agent.agentId}>
              <div className="specials-catalog__card-head">
                <h3>{agent.title}</h3>
                <span className="specials-catalog__pill">{L(labels, "draft_non_active")}</span>
              </div>
              <p className="specials-catalog__id">
                <code>{agent.agentId}</code>
              </p>
              <p className="specials-catalog__summary">
                <SafeContent content={agent.summary} />
              </p>
              <p className="specials-catalog__meta">
                provider: {agent.provider} · tools: {agent.allowedTools.length} · network:{" "}
                {agent.networkAccess ? "on" : "off"} · production activation requested:{" "}
                {agent.productionActivationRequested ? "yes" : "no"}
              </p>
              <p className="specials-catalog__source">
                Provenance: <code>{agent.sourcePath}</code>
              </p>
              <div className="specials-catalog__actions">
                <Link
                  className="specials-catalog__action specials-catalog__action--primary"
                  href={`/registry/agents/${encodeURIComponent(agent.agentId)}`}
                >
                  View agent settings
                </Link>
                <button
                  className="specials-catalog__action"
                  onClick={() =>
                    setStatusMessage(
                      `${agent.agentId} remains draft/non-active. Activate requires separate host approval gates — not available from this catalog.`,
                    )
                  }
                  type="button"
                >
                  Inspect activation policy
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
