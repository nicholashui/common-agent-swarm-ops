"use client";

import React, {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import Link from "next/link";

import {
  buildLocalAssistantReply,
  type ComposerChatMessage,
  type ComposerGraphStyle,
  type ComposerLandingView,
  type ComposerPatternCard,
} from "../lib/projections/composer-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function ComposerHome({
  view }: Readonly<{ view: ComposerLandingView }>): JSX.Element {
  const labels = view.labels;
  const [swarmName, setSwarmName] = useState(view.swarmName);
  const [goal, setGoal] = useState("");
  const [activeFilter, setActiveFilter] = useState(view.activeFilter);
  const [selectedPatternId, setSelectedPatternId] = useState(
    view.patterns.find((pattern) => pattern.recommended)?.id ??
      view.patterns[0]?.id,
  );
  const [query, setQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [architectOpen, setArchitectOpen] = useState(true);
  const [patternsOpen, setPatternsOpen] = useState(false);
  const [messages, setMessages] = useState<readonly ComposerChatMessage[]>(
    view.messages,
  );
  const patternRefs = useRef(new Map<string, HTMLLIElement | null>());
  const architectPanelId = useId();

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
    view.patterns.find((pattern) => pattern.id === selectedPatternId) ??
    filteredPatterns[0] ??
    view.patterns[0];

  useEffect(() => {
    const latestRec = [...messages]
      .reverse()
      .find((message) => message.recommendation)?.recommendation;
    if (!latestRec) return;
    setSelectedPatternId(latestRec.patternId);
    const node = patternRefs.current.get(latestRec.patternId);
    node?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [messages]);

  const applyChip = (chip: string): void => {
    setGoal(chip);
    setStatusMessage(L(labels, "goal_chip_applied_chip"));
  };

  const selectPattern = (patternId: string): void => {
    setSelectedPatternId(patternId);
    const pattern = view.patterns.find((entry) => entry.id === patternId);
    if (pattern) {
      setSwarmName(`Untitled Swarm from ${pattern.name}`);
    }
  };

  const instantiatePattern = (pattern: ComposerPatternCard): void => {
    selectPattern(pattern.id);
    setMessages((current) => [
      ...current,
      {
        id: `inst-${Date.now()}`,
        role: "user",
        text: `Start with common pattern ${pattern.name} v${pattern.version}.`,
      },
      {
        id: `inst-a-${Date.now()}`,
        role: "assistant",
        text: "Pattern selected from browser:",
        recommendation: {
          patternId: pattern.id,
          patternName: pattern.name,
          version: pattern.version,
          rationale: pattern.whenToUse,
          metrics: pattern.metrics,
          slots: [
            { id: "slot-a", label: "Slot A", version: "Common" },
            { id: "slot-b", label: "Slot B", version: "Common" },
            {
              id: "slot-v",
              label: "Verifier",
              version: "Common",
              verified: true,
            },
          ],
        },
      },
    ]);
    setStatusMessage(
      `Instantiated ${pattern.name} into chat recommendation (local preview).`,
    );
    setPatternsOpen(false);
  };

  const handleSend = (event?: FormEvent): void => {
    event?.preventDefault();
    const trimmed = goal.trim();
    if (trimmed.length === 0) {
      setStatusMessage(L(labels, "enter_a_goal_before_sending"));
      return;
    }
    const userMessage: ComposerChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      text: trimmed,
    };
    const assistant = buildLocalAssistantReply(trimmed, view.patterns);
    setMessages((current) => [...current, userMessage, assistant]);
    setGoal("");
    setStatusMessage(
      "Local preview recommendation appended. Browse patterns or load the canvas draft.",
    );
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <section aria-label={L(labels, "swarm_composer")} className="composer-home">
      <header className="composer-home__toolbar">
        <div className="composer-home__toolbar-main">
          <label className="composer-home__name">
            <span className="visually-hidden">{L(labels, "swarm_name")}</span>
            <input
              aria-label={L(labels, "swarm_name")}
              onChange={(event) => setSwarmName(event.target.value)}
              value={swarmName}
            />
          </label>
        </div>
        <div className="composer-home__toolbar-actions">
          <button
            className="composer-home__ghost"
            onClick={() =>
              setStatusMessage(L(labels, "save_draft_requires_an_authorized_compose_contra"))
            }
            type="button"
          >
            Save Draft
          </button>
          <button
            className="composer-home__ghost"
            onClick={() =>
              setStatusMessage(L(labels, "load_template_requires_an_authorized_template_pr"))
            }
            type="button"
          >
            Load Template
          </button>
          <Link aria-label={L(labels, "close_composer")} className="composer-home__close" href="/">
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
        <section aria-label={L(labels, "chat_composer")} className="composer-home__chat panel">
          <div className="composer-home__architect">
            <button
              aria-controls={architectPanelId}
              aria-expanded={architectOpen}
              className="composer-home__architect-toggle"
              onClick={() => setArchitectOpen((open) => !open)}
              type="button"
            >
              <span aria-hidden="true" className="composer-home__architect-mark">
                ✓
              </span>
              <span className="composer-home__architect-copy">
                <strong>{view.architectTitle}</strong>
                {architectOpen ? (
                  <span id={architectPanelId}>{view.architectSubtitle}</span>
                ) : (
                  <span>{L(labels, "show_system_context")}</span>
                )}
              </span>
              <span aria-hidden="true">{architectOpen ? "⌃" : "⌄"}</span>
            </button>
          </div>

          <div className="composer-home__messages" role="log">
            {messages.map((message) =>
              message.role === "user" ? (
                <div
                  className="composer-home__bubble composer-home__bubble--user"
                  key={message.id}
                >
                  {(message.lines ?? [message.text ?? ""]).map((line) => (
                    <p key={`${message.id}-${line}`}>{line}</p>
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
                        <button
                          className="composer-home__rec-card"
                          onClick={() =>
                            selectPattern(message.recommendation!.patternId)
                          }
                          type="button"
                        >
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
                        </button>
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
                          <button
                            className="composer-home__ghost"
                            onClick={() =>
                              setStatusMessage(
                                "Fork & Customize requires an authorized fork action.",
                              )
                            }
                            type="button"
                          >
                            Fork &amp; Customize
                          </button>
                          <button
                            className="composer-home__ghost composer-home__ghost--violet"
                            onClick={() =>
                              setStatusMessage(
                                "Propose as new Pattern requires an authorized proposal contract.",
                              )
                            }
                            type="button"
                          >
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

          <div className="composer-home__bottom-bar">
            <button
              className="composer-home__ghost"
              onClick={() =>
                setStatusMessage(L(labels, "regenerate_requires_the_composer_recommend_strea"))
              }
              type="button"
            >
              Regenerate
            </button>
            <Link className="composer-home__ghost" href="/canvas">
              Start from blank graph instead
            </Link>
            <button
              className="composer-home__ghost"
              onClick={() =>
                setStatusMessage(
                  "Save conversation as template requires an authorized template write.",
                )
              }
              type="button"
            >
              Save this conversation as template
            </button>
          </div>

          <div
            aria-label={L(labels, "goal_examples")}
            className="composer-home__chips"
            role="group"
          >
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
            <div className="composer-home__input-tools">
              <label className="composer-home__attach">
                <span className="visually-hidden">{L(labels, "attach_requirements_file")}</span>
                <input
                  accept=".md,.pdf,text/markdown,application/pdf"
                  onChange={() =>
                    setStatusMessage(
                      "File attach is local-only feedback; server ingestion is not connected.",
                    )
                  }
                  type="file"
                />
                📎
              </label>
              <button
                aria-label={L(labels, "send_goal")}
                className="composer-home__send"
                type="submit"
              >
                ↑
              </button>
            </div>
          </form>
        </section>

        <aside
          aria-label={L(labels, "common_pattern_browser")}
          className={
            patternsOpen
              ? "composer-home__browser composer-home__browser--open"
              : "composer-home__browser"
          }
          id="composer-pattern-browser"
        >
          <div className="composer-home__browser-head">
            <h2>{L(labels, "common_pattern_browser")}</h2>
            <button
              className="composer-home__browser-close"
              onClick={() => setPatternsOpen(false)}
              type="button"
            >
              Close
            </button>
          </div>
          <label className="composer-home__search">
            <span className="visually-hidden">{L(labels, "search_patterns")}</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder={L(labels, "search_patterns_2")}
              value={query}
            />
          </label>
          <div
            aria-label={L(labels, "pattern_filters")}
            className="composer-home__filters"
            role="group"
          >
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
              <li
                key={pattern.id}
                ref={(node) => {
                  patternRefs.current.set(pattern.id, node);
                }}
              >
                <PatternCard
                  onInstantiate={() => instantiatePattern(pattern)}
                  onSelect={() => selectPattern(pattern.id)}
                  pattern={pattern}
                  selected={selectedPattern?.id === pattern.id}
                  labels={labels}
                />
              </li>
            ))}
          </ul>

          {selectedPattern ? (
            <div className="composer-home__preview panel">
              <p className="composer-home__preview-label">
                Live Preview — {selectedPattern.name} v{selectedPattern.version}
              </p>
              <MiniGraph style={selectedPattern.graphStyle}  labels={labels} />
              <dl className="composer-home__summary">
                <div>
                  <dt>{L(labels, "total_agents_slots")}</dt>
                  <dd>{selectedPattern.previewSummary.totalSlots}</dd>
                </div>
                <div>
                  <dt>{L(labels, "parallelism_factor")}</dt>
                  <dd>{selectedPattern.previewSummary.parallelism}</dd>
                </div>
                <div>
                  <dt>{L(labels, "est_cost_latency")}</dt>
                  <dd>{selectedPattern.previewSummary.estCostLatency}</dd>
                </div>
                <div>
                  <dt>{L(labels, "verification_coverage")}</dt>
                  <dd className="composer-home__metrics">
                    {selectedPattern.previewSummary.verificationCoverage}
                  </dd>
                </div>
              </dl>
              <Link className="composer-home__primary" href="/canvas">
                Load into Canvas →
              </Link>
            </div>
          ) : null}

          <button
            className="composer-home__suggest"
            onClick={() =>
              setStatusMessage(
                "Suggest new Common Pattern requires an authorized proposal action.",
              )
            }
            type="button"
          >
            {view.suggestNewLabel}
          </button>
          {view.handoffNotes.map((note) => (
            <p className="composer-home__handoff-note" key={note}>
              {note}
            </p>
          ))}
        </aside>
      </div>

      <button
        aria-controls="composer-pattern-browser"
        aria-expanded={patternsOpen}
        className="composer-home__fab"
        onClick={() => setPatternsOpen((open) => !open)}
        type="button"
      >
        Browse Patterns
      </button>

      <p className="composer-home__footer">{view.footerNote}</p>
    </section>
  );
}

function PatternCard({
  pattern,
  selected,
  onSelect,
  onInstantiate,
  labels,
}: Readonly<{
  pattern: ComposerPatternCard;
  selected: boolean;
  onSelect: () => void;
  onInstantiate: () => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <article
      className={
        selected
          ? "composer-home__pattern composer-home__pattern--selected"
          : "composer-home__pattern"
      }
    >
      <button
        aria-pressed={selected}
        className="composer-home__pattern-select"
        onClick={onSelect}
        type="button"
      >
        {pattern.recommended ? (
          <span className="composer-home__badge">{L(labels, "recommended")}</span>
        ) : null}
        <strong>
          {pattern.name}
          <span className="composer-home__version">v{pattern.version}</span>
        </strong>
        <MiniGraph style={pattern.graphStyle}  labels={labels} />
        <span className="composer-home__when">{pattern.whenToUse}</span>
        <span className="composer-home__metrics">{pattern.metrics}</span>
      </button>
      <div className="composer-home__pattern-actions">
        <button
          className="composer-home__primary composer-home__primary--small"
          onClick={onInstantiate}
          type="button"
        >
          Instantiate
        </button>
        <button
          className="composer-home__ghost"
          onClick={onSelect}
          type="button"
        >
          Fork
        </button>
      </div>
    </article>
  );
}

function MiniGraph({
  style,
  labels,
}: Readonly<{
  style: ComposerGraphStyle;
  labels: ScreenLabels;
}>): JSX.Element {
  if (style === "verification_loop") {
    return (
      <div
        aria-hidden="true"
        className="composer-home__mini-graph composer-home__mini-graph--loop"
      >
        <span>{L(labels, "agent")}</span>
        <i>→</i>
        <span className="composer-home__mini-graph-verify">{L(labels, "verify")}</span>
        <b>↺</b>
      </div>
    );
  }
  if (style === "dynamic_router") {
    return (
      <div
        aria-hidden="true"
        className="composer-home__mini-graph composer-home__mini-graph--router"
      >
        <em>◇</em>
        <span>{L(labels, "b1")}</span>
        <span>{L(labels, "b2")}</span>
      </div>
    );
  }
  if (style === "supervisor") {
    return (
      <div
        aria-hidden="true"
        className="composer-home__mini-graph composer-home__mini-graph--supervisor"
      >
        <span className="composer-home__mini-graph-hub">S</span>
        <span>A</span>
        <span>B</span>
        <span>C</span>
      </div>
    );
  }
  return (
    <div
      aria-hidden="true"
      className="composer-home__mini-graph composer-home__mini-graph--parallel"
    >
      <span>A</span>
      <span>B</span>
      <span>C</span>
      <i>→</i>
      <span className="composer-home__mini-graph-verify">{L(labels, "verify")}</span>
      <small>{L(labels, "big_rows_verifier_cycle")}</small>
    </div>
  );
}
