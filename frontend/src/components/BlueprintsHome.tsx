"use client";

/**
 * @duty BlueprintsHome — blueprint gallery projection (ui_20)
 * @role Gallery of blueprint cards; instantiate only via host intents when eligible.
 * @controls Search/filter, gallery cards, instantiate actions via onAction.
 * @must Note pack_spine is not blueprint realization; fail-closed without contract.
 * @mustnot Realize blueprints or claim pack authority in the browser.
 * @redesign docs/frontend_redesign/ui_20_blueprints.md
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type BlueprintCard,
  type BlueprintsLandingView,
} from "../lib/projections/blueprints-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function BlueprintsHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: BlueprintsLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [query, setQuery] = useState("");
  const [facet, setFacet] = useState(view.filters[0] ?? "All (24)");
  const [sort, setSort] = useState(view.sorts[0] ?? "Most deployed");
  const [selectedId, setSelectedId] = useState(
    view.blueprints.find((b) => b.featured)?.id ?? view.blueprints[0]?.id,
  );
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const blueprints = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = view.blueprints.filter((bp) => {
      if (!facet.startsWith("All")) {
        const domain = facet;
        if (!bp.domains.some((d) => d === domain || d.includes(domain))) {
          // also match Content filter loosely
          if (
            domain === "Content" &&
            !bp.domains.some((d) =>
              /content|creative|video|bilingual/i.test(d),
            )
          ) {
            return false;
          }
          if (
            domain !== "Content" &&
            !bp.domains.includes(domain) &&
            !bp.description.toLowerCase().includes(domain.toLowerCase())
          ) {
            return false;
          }
        }
      }
      if (q.length === 0) return true;
      return (
        bp.name.toLowerCase().includes(q) ||
        bp.description.toLowerCase().includes(q) ||
        bp.pattern.toLowerCase().includes(q) ||
        bp.domains.some((d) => d.toLowerCase().includes(q))
      );
    });
    if (sort === "Highest rated") {
      list = [...list].sort((a, b) =>
        (b.rating ?? "").localeCompare(a.rating ?? ""),
      );
    }
    return list;
  }, [facet, query, sort, view.blueprints]);

  const selected =
    blueprints.find((bp) => bp.id === selectedId) ??
    blueprints[0] ??
    view.blueprints[0];

  return (
    <section aria-label={L(labels, "blueprints_and_templates_gallery")} className="blueprints-home">
      <header className="blueprints-home__header">
        <div>
          <p className="eyebrow">{view.eyebrow}</p>
          <h1>{view.title}</h1>
          <p className="lede">{view.description}</p>
          <p className="blueprints-home__migration" role="note">
            {view.migrationNote}
          </p>
        </div>
        <div className="blueprints-home__header-actions">
          <label className="blueprints-home__search">
            <span className="visually-hidden">{L(labels, "search_blueprints")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={view.searchPlaceholder}
              value={query}
            />
          </label>
          <button
            className="blueprints-home__action blueprints-home__action--primary"
            onClick={() =>
              announce(
                "Publish Blueprint requires evaluation pass and an authorized publish action.",
              )
            }
            type="button"
          >
            + Publish Blueprint
          </button>
        </div>
      </header>

      <div className="blueprints-home__toolbar">
        <div
          aria-label={L(labels, "domain_filters")}
          className="blueprints-home__facets"
          role="group"
        >
          {view.filters.map((entry) => (
            <button
              aria-pressed={facet === entry}
              className={
                facet === entry
                  ? "blueprints-home__facet blueprints-home__facet--active"
                  : "blueprints-home__facet"
              }
              key={entry}
              onClick={() => setFacet(entry)}
              type="button"
            >
              {entry}
            </button>
          ))}
        </div>
        <div
          aria-label={L(labels, "sort_blueprints")}
          className="blueprints-home__sorts"
          role="group"
        >
          {view.sorts.map((entry) => (
            <button
              aria-pressed={sort === entry}
              className={
                sort === entry
                  ? "blueprints-home__facet blueprints-home__facet--active"
                  : "blueprints-home__facet"
              }
              key={entry}
              onClick={() => setSort(entry)}
              type="button"
            >
              {entry}
            </button>
          ))}
        </div>
      </div>

      {feedback ? (
        <p aria-live="polite" className="blueprints-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="blueprints-home__body">
        <div className="blueprints-home__gallery">
          {blueprints.map((bp) => (
            <BlueprintCardView
              blueprint={bp}
              key={bp.id}
              selected={selected?.id === bp.id}
              onSelect={() => setSelectedId(bp.id)}
              onAnnounce={announce}
             labels={labels} />
          ))}
          {blueprints.length === 0 ? (
            <p className="blueprints-home__muted">
              No blueprints match the current filters.
            </p>
          ) : null}

          <section
            aria-labelledby="create-blueprint-heading"
            className="blueprints-home__create"
          >
            <h2 id="create-blueprint-heading">{L(labels, "create_your_own_blueprint")}</h2>
            <p>{view.createNote}</p>
            <div className="blueprints-home__actions">
              <button
                className="blueprints-home__action blueprints-home__action--primary"
                onClick={() =>
                  announce(
                    "Save Current Swarm as Blueprint requires an authorized blueprint create action from a returned graph revision.",
                  )
                }
                type="button"
              >
                Save Current Swarm as Blueprint
              </button>
              <button
                className="blueprints-home__action"
                onClick={() =>
                  announce(
                    "Import from JSON / YAML requires an authorized import with validation.",
                  )
                }
                type="button"
              >
                Import from JSON / YAML
              </button>
            </div>
            <p className="blueprints-home__muted">{view.publishNote}</p>
          </section>
        </div>

        {selected ? (
          <aside
            aria-label={`${selected.name} detail`}
            className="blueprints-home__detail"
          >
            <p className="eyebrow">
              {selected.featured ? "Featured" : "Blueprint detail"}
            </p>
            <h2>{selected.name}</h2>
            <p>{selected.description}</p>
            <div
              aria-hidden="true"
              className={`blueprints-home__preview blueprints-home__preview--${selected.previewStyle}`}
            >
              <i />
              <i />
              <i />
              <i />
            </div>
            <dl className="blueprints-home__meta-list">
              <div>
                <dt>{L(labels, "pattern")}</dt>
                <dd>{selected.pattern}</dd>
              </div>
              <div>
                <dt>{L(labels, "agents")}</dt>
                <dd>{selected.agentCount}</dd>
              </div>
              <div>
                <dt>{L(labels, "knowledge")}</dt>
                <dd>{selected.knowledge}</dd>
              </div>
              <div>
                <dt>{L(labels, "metrics")}</dt>
                <dd>{selected.metrics}</dd>
              </div>
              <div>
                <dt>{L(labels, "governance")}</dt>
                <dd>{selected.governance}</dd>
              </div>
              {selected.rating ? (
                <div>
                  <dt>{L(labels, "rating")}</dt>
                  <dd>{selected.rating}</dd>
                </div>
              ) : null}
            </dl>
            <h3>{L(labels, "pinned_versions")}</h3>
            <ul className="blueprints-home__pins">
              {selected.pins.map((pin) => (
                <li key={pin}>{pin}</li>
              ))}
            </ul>
            <button
              className="blueprints-home__action"
              onClick={() =>
                announce(
                  "Update pins to latest safe requires impact preview and an authorized version action.",
                )
              }
              type="button"
            >
              Update pins to latest safe
            </button>
            {selected.maturityLabel ? (
              <>
                <h3>{L(labels, "pack_maturity_migration_safe")}</h3>
                <p className="blueprints-home__maturity">{selected.maturityLabel}</p>
              </>
            ) : null}
            <h3>{L(labels, "va_compatible_preview_hints")}</h3>
            <ul className="blueprints-home__hints">
              {selected.vaHints.map((hint) => (
                <li key={hint}>{hint}</li>
              ))}
            </ul>
            <div className="blueprints-home__actions">
              <button
                className="blueprints-home__action blueprints-home__action--primary"
                onClick={() =>
                  announce(
                    "Deploy requires an authorized blueprint action. Catalog/stub previews never activate production agents, providers, or network paths.",
                  )
                }
                type="button"
              >
                Deploy to Workspace
              </button>
              <Link className="blueprints-home__action" href="/composer">
                Customize
              </Link>
              <button
                className="blueprints-home__action"
                onClick={() =>
                  announce(
                    "Fork creates a personal blueprint when authorized — provenance retained.",
                  )
                }
                type="button"
              >
                Fork
              </button>
              <button
                className="blueprints-home__action"
                onClick={() =>
                  announce(
                    "Share requires an authorized collaboration action.",
                  )
                }
                type="button"
              >
                Share
              </button>
            </div>
            <p className="blueprints-home__safety" role="note">
              {view.safetyNote}
            </p>
          </aside>
        ) : null}
      </div>

      <p className="blueprints-home__footer">{view.footerNote}</p>
    </section>
  );
}

function BlueprintCardView({
  blueprint,
  selected,
  onSelect,
  onAnnounce,
  labels,
}: Readonly<{
  blueprint: BlueprintCard;
  selected: boolean;
  onSelect: () => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <article
      className={
        blueprint.featured
          ? selected
            ? "blueprints-home__card blueprints-home__card--featured blueprints-home__card--selected"
            : "blueprints-home__card blueprints-home__card--featured"
          : selected
            ? "blueprints-home__card blueprints-home__card--selected"
            : "blueprints-home__card"
      }
    >
      <button
        className="blueprints-home__card-hit"
        onClick={onSelect}
        type="button"
      >
        {blueprint.featured ? (
          <span className="blueprints-home__featured-pill">{L(labels, "featured")}</span>
        ) : null}
        <span
          className={`blueprints-home__gov blueprints-home__gov--${blueprint.governance}`}
        >
          {blueprint.governance === "beta" ? "β Beta" : blueprint.governance}
        </span>
        <div
          aria-hidden="true"
          className={`blueprints-home__preview blueprints-home__preview--${blueprint.previewStyle}`}
        >
          <i />
          <i />
          <i />
        </div>
        <h2>{blueprint.name}</h2>
        <p>{blueprint.description}</p>
        <p className="blueprints-home__pattern">{blueprint.pattern}</p>
        <p className="blueprints-home__muted">
          {blueprint.agentCount} · {blueprint.knowledge}
        </p>
        <p className="blueprints-home__metrics">{blueprint.metrics}</p>
        <p className="blueprints-home__muted">
          {blueprint.author}
          {blueprint.rating ? ` · ${blueprint.rating}` : ""}
        </p>
        <ul className="blueprints-home__domains">
          {blueprint.domains.map((domain) => (
            <li key={domain}>{domain}</li>
          ))}
        </ul>
      </button>
      <div className="blueprints-home__card-actions">
        <button
          className="blueprints-home__action blueprints-home__action--primary"
          onClick={() => {
            onSelect();
            onAnnounce(
              "Deploy requires an authorized blueprint action. Previews never enable production activation.",
            );
          }}
          type="button"
        >
          {blueprint.featured ? "Deploy to Workspace" : "Deploy"}
        </button>
        <Link className="blueprints-home__action" href="/composer">
          Customize
        </Link>
        <button
          className="blueprints-home__action"
          onClick={() => {
            onSelect();
            onAnnounce("Preview opens detail drawer (local presentation).");
          }}
          type="button"
        >
          Preview
        </button>
      </div>
    </article>
  );
}
