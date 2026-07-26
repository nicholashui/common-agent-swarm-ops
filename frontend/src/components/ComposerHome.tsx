"use client";

import React, { useMemo, useState, type FormEvent, type KeyboardEvent } from "react";
import Link from "next/link";

import {
  LOCAL_COMPOSER_LANDING,
  type ComposerLandingView,
  type ComposerPatternCard,
} from "../lib/projections/composer-landing";

export function ComposerHome({
  view = LOCAL_COMPOSER_LANDING,
}: Readonly<{ view?: ComposerLandingView }>): JSX.Element {
  const [swarmName, setSwarmName] = useState(view.swarmName);
  const [goal, setGoal] = useState("");
  const [activeFilter, setActiveFilter] = useState(view.activeFilter);
  const [selectedPatternId, setSelectedPatternId] = useState(
    view.patterns.find((pattern) => pattern.recommended)?.id ??
      view.patterns[0]?.id,
  );
  const [query, setQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const filteredPatterns = useMemo(() => {
    const q = query.trim().toLowerCase();
    return view.patterns.filter((pattern) => {
      const matchesQuery =
        q.length === 0 ||
        pattern.name.toLowerCase().includes(q) ||
        pattern.whenToUse.toLowerCase().includes(q);
      const matchesFilter =
        activeFilter === "All domains" ||
        pattern.domainTags.includes(activeFilter);
      return matchesQuery && matchesFilter;
    });
  }, [activeFilter, query, view.patterns]);

  const selectedPattern =
    filteredPatterns.find((pattern) => pattern.id === selectedPatternId) ??
    filteredPatterns[0] ??
    view.patterns[0];

  const applyChip = (chip: string): void => {
    setGoal(chip);
    setStatusMessage(`Goal chip applied: ${chip}`);
  };

  const handleSend = (event?: FormEvent): void => {
    event?.preventDefault();
    if (goal.trim().length === 0) {
      setStatusMessage("Enter a goal before sending.");
      return;
    }
    setStatusMessage(
      "Local preview: composer recommendation API is not connected. Browse patterns or load the canvas draft.",
    );
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <section aria-label="Swarm composer" className="composer-home">
      <header className="composer-home__toolbar">
        <div className="composer-home__toolbar-main">
          <label className="composer-home__name">
            <span className="visually-hidden">Swarm name</span>
            <input
              aria-label="Swarm name"
              onChange={(event) => setSwarmName(event.target.value)}
              value={swarmName}
            />
          </label>
        </div>
        <div className="composer-home__toolbar-actions">
          <button className="composer-home__ghost" type="button">
            Save Draft
          </button>
          <button className="composer-home__ghost" type="button">
            Load Template
          </button>
          <Link aria-label="Close composer" className="composer-home__close" href="/">
            ✕
          </Link>
        </div>
      </header>

      <div className="composer-home__intro">
        <h1>{view.title}</h1>
        <p>{view.description}</p>
      </div>

      {statusMessage ? (
        <p className="composer-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="composer-home__layout">
        <section
          aria-label="Chat composer"
          className="composer-home__chat panel"
        >
          <div className="composer-home__architect">
            <span aria-hidden="true" className="composer-home__architect-mark">
              ✓
            </span>
            <div>
              <strong>{view.architectTitle}</strong>
              <p>{view.architectSubtitle}</p>
            </div>
          </div>

          <div className="composer-home__messages" role="log">
            {view.messages.map((message) =>
              message.role === "user" ? (
                <div className="composer-home__bubble composer-home__bubble--user" key={message.id}>
                  {(message.lines ?? [message.text ?? ""]).map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </div>
              ) : (
                <div className="composer-home__assistant" key={message.id}>
                  <span aria-hidden="true" className="composer-home__ai">
                    AI
                  </span>
                  <div className="composer-home__assistant-body">
                    {message.text ? <p>{message.text}</p> : null}
                    {message.recommendation ? (
                      <article className="composer-home__rec">
                        <div className="composer-home__rec-card">
                          <div>
                            <strong>
                              {message.recommendation.patternName} v
                              {message.recommendation.version}
                            </strong>
                            <span className="composer-home__badge">
                              Recommended for goal
                            </span>
                            <p>{message.recommendation.rationale}</p>
                            <p className="composer-home__metrics">
                              {message.recommendation.metrics}
                            </p>
                          </div>
                        </div>
                        <p className="composer-home__slots-label">
                          Suggested Common Agent slots
                        </p>
                        <ul className="composer-home__slots">
                          {message.recommendation.slots.map((slot) => (
                            <li
                              className={
                                slot.verified
                                  ? "composer-home__slot composer-home__slot--verified"
                                  : "composer-home__slot"
                              }
                              key={slot.id}
                            >
                              <span aria-hidden="true" />
                              {slot.label} · {slot.version}
                            </li>
                          ))}
                        </ul>
                        <div className="composer-home__rec-actions">
                          <Link className="composer-home__primary" href="/canvas">
                            Load into Canvas →
                          </Link>
                          <button className="composer-home__ghost" type="button">
                            Fork &amp; Customize
                          </button>
                          <button className="composer-home__ghost composer-home__ghost--violet" type="button">
                            Propose as new Pattern
                          </button>
                        </div>
                        <p className="composer-home__hint">
                          Iterate: &quot;make verification stricter&quot;, &quot;use cheaper models for data agents&quot;…
                        </p>
                      </article>
                    ) : null}
                  </div>
                </div>
              ),
            )}
          </div>

          <div className="composer-home__chips" role="group" aria-label="Goal examples">
            {view.goalChips.map((chip) => (
              <button
                className="composer-home__chip"
                key={chip}
                onClick={() => applyChip(chip)}
                type="button"
              >
                {chip}
              </button>
            ))}
          </div>

          <form className="composer-home__input" onSubmit={handleSend}>
            <label className="visually-hidden" htmlFor="composer-goal">
              Describe your swarm goal
            </label>
            <textarea
              id="composer-goal"
              onChange={(event) => setGoal(event.target.value)}
              onKeyDown={onKeyDown}
              placeholder={view.inputPlaceholder}
              value={goal}
            />
            <button aria-label="Send goal" className="composer-home__send" type="submit">
              ↑
            </button>
          </form>
        </section>

        <aside
          aria-label="Common Pattern Browser"
          className="composer-home__browser"
        >
          <h2>Common Pattern Browser</h2>
          <label className="composer-home__search">
            <span className="visually-hidden">Search patterns</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search patterns…"
              value={query}
            />
          </label>
          <div className="composer-home__filters" role="group" aria-label="Pattern filters">
            {view.filters.map((filter) => (
              <button
                aria-pressed={activeFilter === filter}
                className={
                  activeFilter === filter
                    ? "composer-home__filter composer-home__filter--active"
                    : "composer-home__filter"
                }
                key={filter}
                onClick={() => setActiveFilter(filter)}
                type="button"
              >
                {filter}
              </button>
            ))}
          </div>
          <ul className="composer-home__patterns">
            {filteredPatterns.map((pattern) => (
              <li key={pattern.id}>
                <PatternCard
                  onSelect={() => setSelectedPatternId(pattern.id)}
                  pattern={pattern}
                  selected={selectedPattern?.id === pattern.id}
                />
              </li>
            ))}
          </ul>
          {selectedPattern ? (
            <div className="composer-home__preview panel">
              <p className="composer-home__preview-label">Preview</p>
              <strong>{selectedPattern.name}</strong>
              <p>{selectedPattern.whenToUse}</p>
              <div className="composer-home__mini-graph" aria-hidden="true">
                <i />
                <i />
                <i />
                <b />
                <b />
              </div>
              <p className="composer-home__metrics">{selectedPattern.metrics}</p>
              <Link className="composer-home__primary" href="/canvas">
                Instantiate in Canvas →
              </Link>
            </div>
          ) : null}
        </aside>
      </div>

      <p className="composer-home__footer">{view.footerNote}</p>
    </section>
  );
}

function PatternCard({
  pattern,
  selected,
  onSelect,
}: Readonly<{
  pattern: ComposerPatternCard;
  selected: boolean;
  onSelect: () => void;
}>): JSX.Element {
  return (
    <button
      aria-pressed={selected}
      className={
        selected
          ? "composer-home__pattern composer-home__pattern--selected"
          : "composer-home__pattern"
      }
      onClick={onSelect}
      type="button"
    >
      {pattern.recommended ? (
        <span className="composer-home__badge">Recommended</span>
      ) : null}
      <strong>
        {pattern.name}
        <span className="composer-home__version">v{pattern.version}</span>
      </strong>
      <span className="composer-home__when">{pattern.whenToUse}</span>
      <span className="composer-home__metrics">{pattern.metrics}</span>
      <span className="composer-home__used">{pattern.usedIn}</span>
      <span className="composer-home__pattern-actions">
        <span className="composer-home__ghost">Instantiate</span>
        <span className="composer-home__ghost">Fork as Custom</span>
      </span>
    </button>
  );
}
