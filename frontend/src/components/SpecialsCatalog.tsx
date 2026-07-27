"use client";

/**
 * @duty SpecialsCatalog — specials pack catalog panel
 * @role List draft/non-active specials agents; local search; never production-activate.
 * @controls Search input; in-app links; announce-only buttons fail-closed if governed.
 * @must Show disclaimer/draft status; SafeContent for untrusted summary text.
 * @mustnot Activate specials or claim production readiness.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.5; ui_07_registry_hub.md embed
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type SpecialsLandingView,
} from "../lib/projections/specials-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { SafeContent } from "./projection/SafeContent";

export function SpecialsCatalog({
  view }: Readonly<{ view: SpecialsLandingView }>): JSX.Element {
  const labels = view.labels;
  const [query, setQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const agents = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length === 0) return view.agents;
    return view.agents.filter(
      (agent) =>
        agent.title.toLowerCase().includes(q)
        || agent.agentId.toLowerCase().includes(q)
        || agent.summary.toLowerCase().includes(q),
    );
  }, [query, view.agents]);

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
            onChange={(event) => setQuery(event.target.value)}
            placeholder={L(labels, "search_specials_by_id_or_title")}
            value={query}
          />
        </label>
      </header>

      <p className="specials-catalog__disclaimer" role="note">
        {view.disclaimer}
      </p>

      {statusMessage ? (
        <p aria-live="polite" className="specials-catalog__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      {agents.length === 0 ? (
        <p className="specials-catalog__empty">{view.emptyLabel}</p>
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
              <SafeContent content={agent.summary} />
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
