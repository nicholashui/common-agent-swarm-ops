"use client";

/**
 * @duty OnboardingHome — onboarding steps projection (ui_16)
 * @role Guide continue/next steps from projection; no host authority inventions.
 * @controls Step navigation, continue, optional skip when projection allows.
 * @must Keep progress presentation-only or session-scoped unless host persists.
 * @mustnot Skip host gates or claim production readiness from onboarding alone.
 * @redesign docs/frontend_redesign/ui_16_onboarding.md
 */
import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type OnboardingLandingView,
} from "../lib/projections/onboarding-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

export function OnboardingHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: OnboardingLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const labels = view.labels;
  const [stepIndex, setStepIndex] = useState(view.defaultStepIndex);
  const [facet, setFacet] = useState(view.agentFilters[0] ?? "");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ReadonlySet<string>>(
    () =>
      new Set(
        view.agents
          .filter((agent) => agent.selectedByDefault)
          .map((agent) => agent.id),
      ),
  );
  const [helpQuery, setHelpQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [aiPrompt, setAiPrompt] = useState(view.defaultHelpPrompt ?? "");

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;
  const step = view.steps[stepIndex] ?? view.steps[0];
  const stepNumber = stepIndex + 1;

  const agents = useMemo(() => {
    const q = query.trim().toLowerCase();
    return view.agents.filter((agent) => {
      if (!facet.startsWith("All") && agent.domain !== facet) return false;
      if (q.length === 0) return true;
      return (
        agent.name.toLowerCase().includes(q) ||
        agent.description.toLowerCase().includes(q) ||
        agent.versionLabel.toLowerCase().includes(q)
      );
    });
  }, [facet, query, view.agents]);

  const selectedAgents = view.agents.filter((agent) => selected.has(agent.id));

  const helpCategories = useMemo(() => {
    const q = helpQuery.trim().toLowerCase();
    if (q.length === 0) return view.helpCategories;
    return view.helpCategories.filter(
      (category) =>
        category.title.toLowerCase().includes(q) ||
        category.description.toLowerCase().includes(q) ||
        category.articles.some((article) => article.toLowerCase().includes(q)),
    );
  }, [helpQuery, view.helpCategories]);

  const toggleAgent = (id: string): void => {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const clearAll = (): void => setSelected(new Set());

  const goNext = (): void => {
    if (stepIndex < view.steps.length - 1) setStepIndex((value) => value + 1);
    else
      announce(
        "Tour complete (local preview). Progress will persist when preference projections connect.",
      );
  };

  const goBack = (): void => {
    if (stepIndex > 0) setStepIndex((value) => value - 1);
  };

  return (
    <section aria-label={L(labels, "onboarding_and_help")} className="onboarding-home">
      <header className="onboarding-home__topbar">
        <Link className="onboarding-home__brand" href="/">
          common-agent-swarm-ops
        </Link>
        <Link className="onboarding-home__skip" href="/">
          Skip for now →
        </Link>
      </header>

      <div
        aria-label={L(labels, "tour_progress")}
        className="onboarding-home__progress"
        role="list"
      >
        {view.steps.map((entry, index) => (
          <button
            aria-current={index === stepIndex ? "step" : undefined}
            className={
              index === stepIndex
                ? "onboarding-home__step-dot onboarding-home__step-dot--active"
                : index < stepIndex
                  ? "onboarding-home__step-dot onboarding-home__step-dot--done"
                  : "onboarding-home__step-dot"
            }
            key={entry.id}
            onClick={() => setStepIndex(index)}
            role="listitem"
            type="button"
          >
            {index + 1}
          </button>
        ))}
      </div>

      {feedback ? (
        <p aria-live="polite" className="onboarding-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="onboarding-home__wizard">
        <header className="onboarding-home__wizard-head">
          <p className="eyebrow">
            {view.stepProgressTemplate
              .replace("{step}", String(stepNumber))
              .replace("{total}", String(view.steps.length))}
          </p>
          <h1>{stepIndex === 2 ? view.title : step?.title}</h1>
          <p className="lede">
            {stepIndex === 2 ? view.subtitle : step?.body}
          </p>
        </header>

        {stepIndex === 2 ? (
          <SelectAgentsPanel
            view={view}
            agents={agents}
            facet={facet}
            query={query}
            selected={selected}
            selectedAgents={selectedAgents}
            onFacet={setFacet}
            onQuery={setQuery}
            onToggle={toggleAgent}
            onClear={clearAll}
            onAnnounce={announce}
           labels={labels} />
        ) : (
          <GenericStepPanel
            view={view}
            step={step}
            onAnnounce={announce}
          />
        )}

        <footer className="onboarding-home__wizard-foot">
          <button
            className="onboarding-home__action"
            disabled={stepIndex === 0}
            onClick={goBack}
            type="button"
          >
            ← Back
          </button>
          <p className="onboarding-home__muted">
            Step {stepNumber} of {view.steps.length} · You can always adjust later
            in Registry Hub.
          </p>
          {step?.href && stepIndex !== 2 ? (
            <Link
              className="onboarding-home__action onboarding-home__action--primary"
              href={step.href}
            >
              {step.ctaLabel} →
            </Link>
          ) : (
            <button
              className="onboarding-home__action onboarding-home__action--primary"
              onClick={goNext}
              type="button"
            >
              {stepIndex === view.steps.length - 1 ? "Finish" : "Next →"}
            </button>
          )}
        </footer>
      </div>

      <section
        aria-labelledby="help-center-heading"
        className="onboarding-home__help"
      >
        <div className="onboarding-home__help-head">
          <div>
            <h2 id="help-center-heading">{L(labels, "help_center")}</h2>
            <p className="onboarding-home__muted">
              Searchable docs · bilingual-ready · contextual guidance
            </p>
          </div>
          <label className="onboarding-home__search">
            <span className="visually-hidden">{L(labels, "search_help")}</span>
            <input
              onChange={(event) => setHelpQuery(event.target.value)}
              placeholder={L(labels, "search_docs")}
              value={helpQuery}
            />
          </label>
        </div>

        <div className="onboarding-home__help-grid">
          {helpCategories.map((category) => (
            <article className="onboarding-home__help-card" key={category.id}>
              <h3>{category.title}</h3>
              <p>{category.description}</p>
              <ul>
                {category.articles.map((article) => (
                  <li key={article}>
                    <button
                      className="onboarding-home__linkish"
                      onClick={() =>
                        announce(
                          `Doc “${article}” is local-preview only until CMS/static docs connect.`,
                        )
                      }
                      type="button"
                    >
                      {article}
                    </button>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        <div className="onboarding-home__split">
          <section className="onboarding-home__panel" aria-label={L(labels, "ai_help")}>
            <h3>{L(labels, "ai_help_chat")}</h3>
            <p className="onboarding-home__muted">
              Contextual help over docs + commons knowledge (authorized assist).
            </p>
            <label className="visually-hidden" htmlFor="onboarding-ai-help">
              Ask AI
            </label>
            <textarea
              id="onboarding-ai-help"
              onChange={(event) => setAiPrompt(event.target.value)}
              rows={3}
              value={aiPrompt}
            />
            <button
              className="onboarding-home__action onboarding-home__action--primary"
              onClick={() =>
                announce(
                  "Ask AI requires an authorized assist endpoint. No private run data is sent from this preview.",
                )
              }
              type="button"
            >
              Ask AI
            </button>
          </section>

          <section className="onboarding-home__panel" aria-label={L(labels, "sample_projects")}>
            <h3>{L(labels, "sample_guided_projects")}</h3>
            <ul className="onboarding-home__samples">
              {view.sampleProjects.map((project) => (
                <li key={project.id}>
                  <div>
                    <strong>{project.title}</strong>
                    <p>{project.description}</p>
                  </div>
                  <Link
                    className="onboarding-home__action"
                    href={project.href}
                  >
                    Use this sample
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </div>

        <section className="onboarding-home__panel" aria-label={L(labels, "core_concepts")}>
          <h3>{L(labels, "what_you_are_learning")}</h3>
          <ul className="onboarding-home__concepts">
            {view.tourConcepts.map((concept) => (
              <li key={concept}>{concept}</li>
            ))}
          </ul>
          <p className="onboarding-home__va" role="note">
            {view.vaNote}
          </p>
        </section>

        <section className="onboarding-home__panel" aria-label={L(labels, "feedback")}>
          <h3>{L(labels, "feedback_contribution")}</h3>
          <div className="onboarding-home__actions">
            <button
              className="onboarding-home__action"
              onClick={() =>
                announce(
                  "Request new common pattern requires an authorized contribution form.",
                )
              }
              type="button"
            >
              Request new common pattern
            </button>
            <button
              className="onboarding-home__action"
              onClick={() =>
                announce(
                  "Report commons issue requires an authorized feedback action.",
                )
              }
              type="button"
            >
              Report commons issue
            </button>
          </div>
        </section>
      </section>

      <p className="onboarding-home__footer">{view.footerNote}</p>
    </section>
  );
}

function SelectAgentsPanel({
  view,
  agents,
  facet,
  query,
  selected,
  selectedAgents,
  onFacet,
  onQuery,
  onToggle,
  onClear,
  onAnnounce,
  labels,
}: Readonly<{
  view: OnboardingLandingView;
  agents: OnboardingLandingView["agents"];
  facet: string;
  query: string;
  selected: ReadonlySet<string>;
  selectedAgents: OnboardingLandingView["agents"];
  onFacet: (value: string) => void;
  onQuery: (value: string) => void;
  onToggle: (id: string) => void;
  onClear: () => void;
  onAnnounce: (message: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <div className="onboarding-home__select">
      <label className="onboarding-home__search onboarding-home__search--wide">
        <span className="visually-hidden">{L(labels, "search_commons")}</span>
        <input
          onChange={(event) => onQuery(event.target.value)}
          placeholder={L(labels, "search_or_describe_what_you_need")}
          value={query}
        />
      </label>

      <div
        aria-label={L(labels, "agent_domain_filters")}
        className="onboarding-home__facets"
        role="group"
      >
        {view.agentFilters.map((entry) => (
          <button
            aria-pressed={facet === entry}
            className={
              facet === entry
                ? "onboarding-home__facet onboarding-home__facet--active"
                : "onboarding-home__facet"
            }
            key={entry}
            onClick={() => onFacet(entry)}
            type="button"
          >
            {entry}
          </button>
        ))}
      </div>

      <div className="onboarding-home__agent-grid">
        {agents.map((agent) => {
          const isSelected = selected.has(agent.id);
          return (
            <button
              aria-pressed={isSelected}
              className={
                isSelected
                  ? "onboarding-home__agent onboarding-home__agent--selected"
                  : "onboarding-home__agent"
              }
              key={agent.id}
              onClick={() => onToggle(agent.id)}
              type="button"
            >
              <strong>{agent.name}</strong>
              <span className="onboarding-home__version">
                {agent.versionLabel}
              </span>
              <p>{agent.description}</p>
              <small>{agent.usage}</small>
            </button>
          );
        })}
      </div>

      <div className="onboarding-home__selection-bar">
        <div>
          <strong>
            {selectedAgents.length} commons selected
          </strong>
          <p>
            {selectedAgents.length === 0
              ? "None selected"
              : selectedAgents.map((agent) => agent.name).join(" · ")}
          </p>
        </div>
        <button className="onboarding-home__linkish" onClick={onClear} type="button">
          Clear all
        </button>
      </div>

      <aside className="onboarding-home__pattern" aria-label={L(labels, "recommended_pattern")}>
        <p className="eyebrow">{view.recommendedPattern.eyebrow}</p>
        <h3>{view.recommendedPattern.name}</h3>
        <p>{view.recommendedPattern.detail}</p>
        <div className="onboarding-home__actions">
          <Link
            className="onboarding-home__action onboarding-home__action--primary"
            href="/canvas"
          >
            Use this pattern
          </Link>
          <button
            className="onboarding-home__action"
            onClick={() =>
              onAnnounce(
                "Pattern pre-load is local-preview until authorized swarm draft creation connects.",
              )
            }
            type="button"
          >
            Preview only
          </button>
        </div>
      </aside>
    </div>
  );
}

function GenericStepPanel({
  view,
  step,
  onAnnounce,
}: Readonly<{
  view: OnboardingLandingView;
  step: OnboardingLandingView["steps"][number] | undefined;
  onAnnounce: (message: string) => void;
}>): JSX.Element {
  return (
    <div className="onboarding-home__generic-step">
      <ul className="onboarding-home__concepts">
        {view.tourConcepts.map((concept) => (
          <li key={concept}>{concept}</li>
        ))}
      </ul>
      {step?.href ? (
        <Link
          className="onboarding-home__action onboarding-home__action--primary"
          href={step.href}
        >
          {step.ctaLabel} →
        </Link>
      ) : (
        <button
          className="onboarding-home__action"
          onClick={() =>
            onAnnounce("Continue the tour with Next, or open a sample project below.")
          }
          type="button"
        >
          Continue tour
        </button>
      )}
    </div>
  );
}
