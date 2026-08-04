"use client";

/**
 * @duty ComposerHome — ACC Swarm Composer (ui_03 redesign)
 * @role Requirements in → AI binds available agents → workflow diagram out.
 * @controls Spec chat, AI plan, HITL conflicts only, materialize → Canvas.
 * @must AI-pick mainly; human only for needs_hitl; closed-world agent ids.
 * @mustnot Invent production activation or human agent shopping as primary path.
 * @redesign docs/frontend_redesign/ui_03_swarm_composer_acc_preview.svg
 */
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
  type ComposerLandingView,
  type ComposerPatternCard,
  type ComposerSample,
} from "../lib/projections/composer-landing";
import {
  buildComposerWorkflowGraph,
  type ComposerWorkflowGraph,
} from "../lib/projections/composer-workflow";
import { L, type ScreenLabels } from "../lib/projections/screen-labels";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";
import { InfoTooltip } from "./design";
import { WithTooltip } from "./ui/tooltip";

type ActiveRec = {
  readonly patternId: string;
  readonly patternName: string;
  readonly version: string;
  readonly rationale: string;
  readonly metrics: string;
  readonly slots: readonly {
    readonly id: string;
    readonly label: string;
    readonly version: string;
    readonly verified?: boolean;
    readonly agentId?: string;
  }[];
};

type StepId = 1 | 2 | 3 | 4 | 5;

export function ComposerHome({
  view,
  onAction,
  statusMessage: externalStatus,
  onNavigate,
}: Readonly<{
  view: ComposerLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
  onNavigate?: (path: string) => void;
}>): JSX.Element {
  const labels = view.labels;
  const [swarmName, setSwarmName] = useState(view.swarmName);
  const [goal, setGoal] = useState("");
  const [scaleProfile, setScaleProfile] = useState<string>("");
  const [archetype, setArchetype] = useState<string>("");
  const [briefLocale, setBriefLocale] = useState<string>("en");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const feedback = externalStatus ?? statusMessage;
  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const [architectOpen, setArchitectOpen] = useState(true);
  const [messages, setMessages] = useState<readonly ComposerChatMessage[]>(
    view.messages,
  );
  const [lastGoal, setLastGoal] = useState("");
  const [aiBusy, setAiBusy] = useState(false);
  const [humanResolutions, setHumanResolutions] = useState<
    Record<string, string>
  >({});
  const [pendingHitlIds, setPendingHitlIds] = useState<readonly string[]>([]);
  const [activeRec, setActiveRec] = useState<ActiveRec | null>(null);
  const [lastCanvasPath, setLastCanvasPath] = useState<string | null>(null);
  const [decisionStatus, setDecisionStatus] = useState<
    "idle" | "ai_resolved" | "needs_hitl"
  >("idle");
  const [step, setStep] = useState<StepId>(1);
  const [samplesOpen, setSamplesOpen] = useState(false);
  const architectPanelId = useId();
  const samplesDialogTitleId = useId();
  const samplesCloseRef = useRef<HTMLButtonElement | null>(null);

  const workflowGraph: ComposerWorkflowGraph = useMemo(
    () =>
      buildComposerWorkflowGraph(
        activeRec?.slots ?? [],
        activeRec?.patternName,
      ),
    [activeRec],
  );

  const samples = view.samples ?? [];

  useEffect(() => {
    if (!samplesOpen) return;
    samplesCloseRef.current?.focus();
    const onKey = (event: globalThis.KeyboardEvent): void => {
      if (event.key === "Escape") {
        setSamplesOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [samplesOpen]);

  const loadSample = (sample: ComposerSample, runPlan: boolean): void => {
    setGoal(sample.body);
    if (sample.locale) setBriefLocale(sample.locale);
    if (sample.scaleProfile) setScaleProfile(sample.scaleProfile);
    else setScaleProfile("");
    if (sample.archetype) setArchetype(sample.archetype);
    else setArchetype("");
    setStep(1);
    setSamplesOpen(false);
    const metaBits = [
      sample.scaleProfile ? `scale ${sample.scaleProfile}` : null,
      sample.archetype ? `archetype ${sample.archetype}` : null,
    ]
      .filter(Boolean)
      .join(" · ");
    announce(
      runPlan
        ? `Loaded sample “${sample.label}”${metaBits ? ` (${metaBits})` : ""} and running AI plan…`
        : `Loaded sample “${sample.label}”${metaBits ? ` (${metaBits})` : ""} into requirements. Review text, then AI plan.`,
    );
    if (runPlan) {
      void handleAiPlan(undefined, sample.body);
    }
  };

  const setRecFromSlots = (
    rec: {
      pattern?: {
        id: string;
        name: string;
        versionLabel: string;
        rationale: string;
      } | null;
      slots: readonly {
        id: string;
        label: string;
        version: string;
        verified: boolean;
        agentId: string;
      }[];
    },
    metrics: string,
  ): ActiveRec => {
    const active: ActiveRec = {
      patternId: rec.pattern?.id ?? "ai-workflow",
      patternName: rec.pattern?.name ?? "AI workflow",
      version: rec.pattern?.versionLabel ?? "1.0",
      rationale: rec.pattern?.rationale ?? "AI pick from available agents.",
      metrics,
      slots: rec.slots.map((s) => ({
        id: s.id,
        label: s.label,
        version: s.version,
        verified: s.verified,
        agentId: s.agentId,
      })),
    };
    setActiveRec(active);
    setSwarmName(`AI · ${active.patternName}`);
    return active;
  };

  const appendHitlMessage = (rec: {
    openQuestions: readonly {
      id: string;
      kind: string;
      severity: string;
      question: string;
      options: readonly { id: string; label: string }[];
    }[];
    note: string;
  }): void => {
    setDecisionStatus("needs_hitl");
    setStep(2);
    setPendingHitlIds(rec.openQuestions.map((q) => q.id));
    setMessages((current) => [
      ...current,
      {
        id: `hitl-${Date.now()}`,
        role: "assistant",
        text: "AI cannot determine a safe solution yet — human resolution required (not agent picking):",
        hitl: {
          questions: rec.openQuestions.map((q) => ({
            id: q.id,
            kind: q.kind,
            severity: q.severity,
            question: q.question,
            options: q.options,
          })),
        },
      },
    ]);
    setStatusMessage(
      rec.note ||
        "Answer the conflict question(s) — AI continues after resolutions.",
    );
  };

  const materializeAndOpen = async (
    goalText?: string,
    resolutions?: Record<string, string>,
  ): Promise<void> => {
    const g = (goalText ?? lastGoal).trim();
    if (!g) {
      setStatusMessage("Send a goal/spec first so AI can pick the workflow.");
      return;
    }
    if (aiBusy) return;
    setAiBusy(true);
    setStep(4);
    setStatusMessage("AI materializing draft swarm…");
    try {
      const { materializeAiComposition } = await import(
        "../lib/api/product-composer"
      );
      const result = await materializeAiComposition(g, {
        swarmName,
        humanResolutions: resolutions ?? humanResolutions,
        brief: {
          locale: briefLocale || "en",
          ...(scaleProfile ? { scaleProfile } : {}),
          ...(archetype ? { archetype } : {}),
        },
      });
      if (!result.ok) {
        setStatusMessage(result.message);
        return;
      }
      if (result.decisionStatus === "needs_hitl") {
        appendHitlMessage(result.recommendation);
        return;
      }
      setPendingHitlIds([]);
      setDecisionStatus("ai_resolved");
      setStep(5);
      const spineNote = result.spineWorkflowId
        ? ` · spine ${result.spineWorkflowId} · stub run · not production media`
        : "";
      const active = setRecFromSlots(
        result.recommendation,
        `${result.memberCount} members · materialize · draft only${spineNote}`,
      );
      setLastCanvasPath(result.canvasPath);
      setMessages((current) => [
        ...current,
        {
          id: `mat-${Date.now()}`,
          role: "assistant",
          text: result.spineWorkflowId
            ? `AI resolved and materialised workflow (spine ${result.spineWorkflowId}; stub run · not production media):`
            : "AI resolved and materialised workflow:",
          recommendation: {
            patternId: active.patternId,
            patternName: active.patternName,
            version: active.version,
            rationale: active.rationale,
            metrics: active.metrics,
            slots: active.slots,
          },
        },
      ]);
      setStatusMessage(
        `AI draft ${result.swarmId} ready (${result.memberCount} members${spineNote}). Opening canvas…`,
      );
      if (onNavigate) {
        onNavigate(result.canvasPath);
      } else if (typeof window !== "undefined") {
        window.location.assign(result.canvasPath);
      }
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Materialize failed.",
      );
    } finally {
      setAiBusy(false);
    }
  };

  /** AI plan: recommend only so the workflow diagram stays on screen. */
  const handleAiPlan = async (
    event?: FormEvent,
    goalOverride?: string,
    resolutions?: Record<string, string>,
  ): Promise<void> => {
    event?.preventDefault();
    const trimmed = (goalOverride ?? goal).trim();
    if (trimmed.length === 0) {
      announce(L(labels, "enter_a_goal_before_sending"));
      return;
    }
    if (aiBusy) return;
    setAiBusy(true);
    setLastGoal(trimmed);
    if (!resolutions) {
      setHumanResolutions({});
      setPendingHitlIds([]);
    }
    setStep(2);
    if (!goalOverride || goalOverride === goal) {
      setMessages((current) => [
        ...current,
        { id: `u-${Date.now()}`, role: "user", text: trimmed },
      ]);
      if (!goalOverride) setGoal("");
    }
    setStatusMessage(
      "AI planning workflow from available agents (closed world)…",
    );
    try {
      const { recommendComposition } = await import(
        "../lib/api/product-composer"
      );
      const result = await recommendComposition(trimmed, {
        humanResolutions: resolutions ?? humanResolutions,
        brief: {
          locale: briefLocale || "en",
          ...(scaleProfile ? { scaleProfile } : {}),
          ...(archetype ? { archetype } : {}),
        },
      });
      if (!result.ok) {
        const fallback = buildLocalAssistantReply(trimmed, view.patterns);
        setMessages((current) => [...current, fallback]);
        if (fallback.recommendation) {
          setActiveRec({
            patternId: fallback.recommendation.patternId,
            patternName: fallback.recommendation.patternName,
            version: fallback.recommendation.version,
            rationale: fallback.recommendation.rationale,
            metrics: fallback.recommendation.metrics,
            slots: fallback.recommendation.slots,
          });
          setDecisionStatus("ai_resolved");
          setStep(3);
        }
        setStatusMessage(result.message);
        return;
      }
      if (result.recommendation.decisionStatus === "needs_hitl") {
        appendHitlMessage(result.recommendation);
        return;
      }
      setPendingHitlIds([]);
      setDecisionStatus("ai_resolved");
      setStep(3);
      const active = setRecFromSlots(
        result.recommendation,
        `${result.recommendation.slots.length} agents · AI pick · draft ready`,
      );
      setMessages((current) => [
        ...current,
        {
          id: `ai-${Date.now()}`,
          role: "assistant",
          text: "AI pick complete — workflow ready (not human agent shopping):",
          recommendation: {
            patternId: active.patternId,
            patternName: active.patternName,
            version: active.version,
            rationale: active.rationale,
            metrics: active.metrics,
            slots: active.slots,
          },
        },
      ]);
      setStatusMessage(
        `AI selected ${active.patternName} with ${active.slots.length} agents. Review diagram, then Accept AI → Execute.`,
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "AI plan failed.",
      );
    } finally {
      setAiBusy(false);
    }
  };

  const resolveHitlOption = (questionId: string, optionId: string): void => {
    const next = { ...humanResolutions, [questionId]: optionId };
    setHumanResolutions(next);
    setMessages((current) => [
      ...current,
      {
        id: `res-${Date.now()}`,
        role: "user",
        text: `Resolved ${questionId} → ${optionId}`,
      },
    ]);
    const stillOpen = pendingHitlIds.filter((id) => id !== questionId);
    setPendingHitlIds(stillOpen);
    if (stillOpen.length === 0 && lastGoal) {
      void handleAiPlan(undefined, lastGoal, next);
    } else {
      setStatusMessage(
        `Recorded ${questionId}. ${stillOpen.length} conflict(s) still open.`,
      );
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      void handleAiPlan();
    }
  };

  const hitlOpen = pendingHitlIds.length;
  const aiSelectedPattern =
    view.patterns.find((p) => p.id === activeRec?.patternId) ??
    view.patterns.find((p) =>
      activeRec?.patternName
        ? p.name
            .toLowerCase()
            .includes(activeRec.patternName.toLowerCase().slice(0, 12))
        : false,
    ) ??
    view.patterns.find((p) => p.recommended) ??
    view.patterns[0];

  return (
    <section
      aria-label={L(labels, "swarm_composer")}
      className="composer-home composer-home--acc"
    >
      <header className="composer-home__toolbar">
        <div className="composer-home__toolbar-main">
          <div className="composer-home__title-row">
            <h1 className="composer-home__title">{view.title}</h1>
            <InfoTooltip label="About Plan" text={view.description} />
            <label className="composer-home__name">
              <span className="visually-hidden">{L(labels, "swarm_name")}</span>
              <input
                aria-label={L(labels, "swarm_name")}
                onChange={(event) => setSwarmName(event.target.value)}
                placeholder={L(labels, "swarm_name")}
                value={swarmName}
              />
            </label>
          </div>
          {decisionStatus === "ai_resolved" ? (
            <WithTooltip content="AI resolved conflicts and bound agents from the closed-world catalog.">
              <span className="composer-home__pill composer-home__pill--ok" tabIndex={0}>
                AI resolved
              </span>
            </WithTooltip>
          ) : null}
          {decisionStatus === "needs_hitl" ? (
            <WithTooltip content="Human required — AI could not decide a conflict (e.g. cost vs quality).">
              <span className="composer-home__pill composer-home__pill--hitl" tabIndex={0}>
                needs_hitl
              </span>
            </WithTooltip>
          ) : null}
          <WithTooltip content="AI picks pattern and agents from the Host catalog. You only resolve conflicts (needs_hitl).">
            <span className="composer-home__pill composer-home__pill--ai" tabIndex={0}>
              AI-pick mainly
            </span>
          </WithTooltip>
        </div>
        <div className="composer-home__toolbar-actions">
          <button
            className="composer-home__ghost"
            onClick={() =>
              announce(L(labels, "save_draft_requires_an_authorized_compose_contra"))
            }
            type="button"
          >
            Save Draft
          </button>
          <button
            className="composer-home__primary"
            disabled={aiBusy || !lastGoal}
            onClick={() => void materializeAndOpen()}
            type="button"
          >
            Accept AI → Execute
          </button>
          <Link
            aria-label={L(labels, "close_composer")}
            className="composer-home__close"
            href="/"
          >
            ✕
          </Link>
        </div>
      </header>

      <ol className="composer-home__steps" aria-label="Composition process">
        {(
          [
            [1, "Requirements"],
            [2, "AI plan & bind"],
            [3, "Workflow diagram"],
            [4, "Materialize draft"],
            [5, "Execute inspect"],
          ] as const
        ).map(([n, label], index, all) => (
          <li
            className={
              step >= n
                ? step === n
                  ? "composer-home__step composer-home__step--active"
                  : "composer-home__step composer-home__step--done"
                : "composer-home__step"
            }
            key={n}
          >
            <span className="composer-home__step-inner">
              {n === 1 ? (
                <button
                  aria-haspopup="dialog"
                  aria-expanded={samplesOpen}
                  className="composer-home__samples-trigger composer-home__samples-trigger--step"
                  onClick={() => setSamplesOpen(true)}
                  title="Sample requirements (load into UI)"
                  type="button"
                >
                  <span aria-hidden="true" className="composer-home__samples-icon">
                    ▦
                  </span>
                  <span className="visually-hidden">
                    Open sample requirements
                  </span>
                </button>
              ) : null}
              <span className="composer-home__step-n" aria-hidden="true">
                {n}
              </span>
              <span className="composer-home__step-label">{label}</span>
            </span>
            {index < all.length - 1 ? (
              <span aria-hidden="true" className="composer-home__step-sep">
                →
              </span>
            ) : null}
          </li>
        ))}
        <li className="composer-home__step-meta">HITL: {hitlOpen} open</li>
      </ol>

      {feedback ? (
        <p className="composer-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="composer-home__layout composer-home__layout--acc">
        {/* ── LEFT: requirements thread ── */}
        <section
          aria-label={L(labels, "chat_composer")}
          className="composer-home__chat panel"
        >
          <div className="composer-home__architect">
            <div className="composer-home__architect-row">
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
                  <strong id={architectPanelId}>{view.architectTitle}</strong>
                </span>
                <span aria-hidden="true">{architectOpen ? "⌃" : "⌄"}</span>
              </button>
              <InfoTooltip
                label={view.architectTitle}
                text={view.architectSubtitle}
              />
            </div>
          </div>

          <p className="composer-home__section-label">
            Requirements{" "}
            <InfoTooltip
              label="Requirements"
              text="Paste a goal or short production spec. AI binds catalog agents and draws the crew workflow."
            />
          </p>
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
                    {message.hitl ? (
                      <article className="composer-home__hitl">
                        <p className="composer-home__slots-label">
                          Human required — AI conflict resolution
                        </p>
                        {message.hitl.questions.map((q) => (
                          <div className="composer-home__hitl-q" key={q.id}>
                            <p>
                              <strong>{q.severity}</strong> · {q.question}
                            </p>
                            <div className="composer-home__hitl-options">
                              {q.options.map((opt) => (
                                <button
                                  className="composer-home__primary composer-home__primary--small"
                                  disabled={
                                    aiBusy || Boolean(humanResolutions[q.id])
                                  }
                                  key={opt.id}
                                  onClick={() =>
                                    resolveHitlOption(q.id, opt.id)
                                  }
                                  type="button"
                                >
                                  {opt.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        ))}
                      </article>
                    ) : null}
                    {message.recommendation ? (
                      <article className="composer-home__rec">
                        <div className="composer-home__rec-card">
                          <strong>
                            {message.recommendation.patternName}{" "}
                            <span className="composer-home__badge">
                              AI selected pattern
                            </span>
                          </strong>
                          <p>{message.recommendation.rationale}</p>
                          <p className="composer-home__metrics">
                            {message.recommendation.metrics}
                          </p>
                        </div>
                        <p className="composer-home__slots-label">
                          AI-bound Common Agent slots
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
                              {slot.label}
                              {slot.agentId ? ` · ${slot.agentId}` : ""} ·{" "}
                              {slot.version}
                            </li>
                          ))}
                        </ul>
                        <div className="composer-home__rec-actions">
                          <button
                            className="composer-home__primary"
                            disabled={aiBusy || !lastGoal}
                            onClick={() => void materializeAndOpen()}
                            type="button"
                          >
                            Accept AI → Execute
                          </button>
                          <button
                            className="composer-home__ghost"
                            disabled={aiBusy || !lastGoal}
                            onClick={() =>
                              void handleAiPlan(undefined, lastGoal)
                            }
                            type="button"
                          >
                            Re-run AI
                          </button>
                          <button
                            className="composer-home__ghost composer-home__ghost--violet"
                            onClick={() =>
                              announce(
                                "Propose as new Pattern requires an authorized proposal contract.",
                              )
                            }
                            type="button"
                          >
                            Propose pattern
                          </button>
                        </div>
                      </article>
                    ) : null}
                  </div>
                </div>
              ),
            )}
          </div>

          {activeRec ? (
            <dl className="composer-home__metrics-strip">
              <div>
                <dt>Agents / slots</dt>
                <dd>{activeRec.slots.length}</dd>
              </div>
              <div>
                <dt>Pipeline depth</dt>
                <dd>{Math.max(2, workflowGraph.phaseCount)}</dd>
              </div>
              <div>
                <dt>Verify</dt>
                <dd className="composer-home__metrics">
                  {workflowGraph.gateCount > 0 ? "full gate" : "optional"}
                </dd>
              </div>
            </dl>
          ) : null}

          <div className="composer-home__hitl-banner" role="status">
            <strong>
              Human exception path (needs_hitl){" "}
              <InfoTooltip
                label="Human exception path"
                text="Shown only when AI cannot decide — e.g. cost vs quality, domain mix, or missing catalog capability. Not for agent shopping."
              />
            </strong>
            <p>
              Current:{" "}
              {hitlOpen === 0
                ? "no open questions · AI proceeding"
                : `${hitlOpen} open question(s)`}
            </p>
          </div>

          <div className="composer-home__inventory">
            <p className="composer-home__section-label">
              Available agents (building blocks){" "}
              <InfoTooltip
                label="Available agents"
                text="Host catalog · closed world · AI binds only agent_id present in inventory · never invents roles."
              />
            </p>
          </div>

          <form
            className="composer-home__input"
            onSubmit={(e) => void handleAiPlan(e)}
          >
            <label className="visually-hidden" htmlFor="composer-goal">
              {L(labels, "send_goal")}
            </label>
            <textarea
              id="composer-goal"
              onChange={(event) => setGoal(event.target.value)}
              onKeyDown={onKeyDown}
              placeholder={view.inputPlaceholder}
              rows={3}
              value={goal}
            />
            <div
              className="composer-home__brief-meta"
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "0.5rem",
                alignItems: "center",
                marginTop: "0.35rem",
                fontSize: "0.8rem",
              }}
            >
              <label>
                Locale{" "}
                <select
                  aria-label="Brief locale"
                  onChange={(e) => setBriefLocale(e.target.value)}
                  value={briefLocale}
                >
                  <option value="en">en</option>
                  <option value="zh-Hant">zh-Hant</option>
                </select>
              </label>
              <label>
                Scale{" "}
                <select
                  aria-label="Scale profile"
                  onChange={(e) => setScaleProfile(e.target.value)}
                  value={scaleProfile}
                >
                  <option value="">—</option>
                  {["S1", "S2", "S3", "S4", "S5"].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Archetype{" "}
                <select
                  aria-label="Archetype"
                  onChange={(e) => setArchetype(e.target.value)}
                  value={archetype}
                >
                  <option value="">—</option>
                  {["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"].map(
                    (a) => (
                      <option key={a} value={a}>
                        {a}
                      </option>
                    ),
                  )}
                </select>
              </label>
              <InfoTooltip
                label="User brief metadata"
                text="Optional UserBriefV1 fields stored on the draft when AI materializes. Free-text goal remains the brief text. No secrets."
              />
            </div>
            <div className="composer-home__input-tools">
              <label
                className="composer-home__attach"
                title={L(labels, "attach_requirements_file")}
              >
                <span aria-hidden="true">📎</span>
                <input
                  accept=".md,.txt,.pdf"
                  onChange={() =>
                    announce(
                      "File attach is local-only until Host parse contract is authorized.",
                    )
                  }
                  type="file"
                />
              </label>
              <button
                className="composer-home__send-label"
                disabled={aiBusy}
                type="submit"
              >
                {aiBusy ? "…" : "AI plan"}
              </button>
            </div>
          </form>

          {samplesOpen ? (
            <div
              className="composer-home__modal-root"
              role="presentation"
            >
              <button
                aria-label="Close sample requirements"
                className="composer-home__modal-backdrop"
                onClick={() => setSamplesOpen(false)}
                type="button"
              />
              <div
                aria-labelledby={samplesDialogTitleId}
                aria-modal="true"
                className="composer-home__modal"
                role="dialog"
              >
                <header className="composer-home__modal-head">
                  <div>
                    <h2 id={samplesDialogTitleId}>
                      Sample requirements (load into UI)
                    </h2>
                    <p>
                      Load fills the requirements box. Load + AI plan runs Host
                      composition.
                    </p>
                  </div>
                  <button
                    ref={samplesCloseRef}
                    className="composer-home__modal-close"
                    onClick={() => setSamplesOpen(false)}
                    type="button"
                  >
                    ✕
                  </button>
                </header>
                <ul className="composer-home__sample-list">
                  {samples.map((sample) => (
                    <li
                      className={
                        sample.kind === "hitl_demo"
                          ? "composer-home__sample composer-home__sample--hitl"
                          : "composer-home__sample"
                      }
                      key={sample.id}
                    >
                      <div className="composer-home__sample-copy">
                        <strong>{sample.label}</strong>
                        <span>{sample.summary}</span>
                        {sample.kind === "hitl_demo" ? (
                          <span className="composer-home__sample-tag">
                            HITL demo
                          </span>
                        ) : null}
                      </div>
                      <div className="composer-home__sample-actions">
                        <button
                          className="composer-home__ghost composer-home__primary--small"
                          disabled={aiBusy}
                          onClick={() => loadSample(sample, false)}
                          type="button"
                        >
                          Load
                        </button>
                        <button
                          className="composer-home__primary composer-home__primary--small"
                          disabled={aiBusy}
                          onClick={() => loadSample(sample, true)}
                          type="button"
                        >
                          Load + AI plan
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
                {samples.length === 0 && view.goalChips.length > 0 ? (
                  <div className="composer-home__chips">
                    {view.goalChips.map((chip) => (
                      <button
                        className="composer-home__chip"
                        key={chip}
                        onClick={() => {
                          setGoal(chip);
                          setSamplesOpen(false);
                          announce(`Loaded “${chip}”. Run AI plan when ready.`);
                        }}
                        type="button"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}

          <div className="composer-home__pattern-context">
            <p className="composer-home__section-label">
              AI pattern context{" "}
              <InfoTooltip
                label="AI pattern context"
                text="Bias only — not a human pick list. AI selects the pattern from Host catalog context."
              />
            </p>
            <ul>
              {view.patterns.slice(0, 3).map((pattern) => (
                <li
                  className={
                    aiSelectedPattern?.id === pattern.id
                      ? "composer-home__pattern-chip composer-home__pattern-chip--active"
                      : "composer-home__pattern-chip"
                  }
                  key={pattern.id}
                  title={
                    aiSelectedPattern?.id === pattern.id
                      ? "AI selected · bias only"
                      : "Considered · not primary pick"
                  }
                >
                  <strong>{pattern.name}</strong>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── RIGHT: workflow diagram ── */}
        <section
          aria-label="Generated workflow diagram"
          className="composer-home__workflow panel"
        >
          <header className="composer-home__workflow-head">
            <p className="composer-home__section-label">
              Generated workflow{" "}
              <InfoTooltip
                label="Generated workflow"
                text="Primary output of Plan. Same visual language as Registry → Agent Workflow: phases · agents · gates."
              />
            </p>
            <div className="page-title-row">
              <h2>Crew workflow diagram</h2>
              <InfoTooltip
                label="Crew workflow diagram"
                text="AI-composed crew graph. Materialize creates a draft instance for Execute — production stays fail-closed."
              />
            </div>
          </header>

          <div className="composer-home__workflow-toolbar">
            <span className="composer-home__wf-stat">
              Template: {activeRec ? "AI composed" : "—"}
            </span>
            <span className="composer-home__wf-stat composer-home__wf-stat--indigo">
              {workflowGraph.agentCount + workflowGraph.gateCount} nodes
            </span>
            <span className="composer-home__wf-stat composer-home__wf-stat--violet">
              {workflowGraph.phaseCount} phases
            </span>
            <span className="composer-home__wf-stat composer-home__wf-stat--ok">
              {workflowGraph.gateCount} gate
            </span>
            <button
              className="composer-home__primary composer-home__primary--small"
              disabled={aiBusy || !lastGoal}
              onClick={() => void materializeAndOpen()}
              type="button"
            >
              Materialize draft
            </button>
          </div>

          <ul className="composer-home__workflow-legend">
            <li className="composer-home__legend composer-home__legend--phase">
              Phase
            </li>
            <li className="composer-home__legend composer-home__legend--agent">
              Agent
            </li>
            <li className="composer-home__legend composer-home__legend--gate">
              Critic / verify
            </li>
            <li className="composer-home__legend composer-home__legend--edge">
              handoff
            </li>
            <li className="composer-home__legend composer-home__legend--refine">
              refine cycle
            </li>
          </ul>

          <WorkflowDiagram graph={workflowGraph} />

          <div className="composer-home__workflow-footer">
            <p className="composer-home__section-label">
              Output package (Host){" "}
              <InfoTooltip
                label="Output package"
                text={[
                  "workflow graph · pattern_ref · agent pins · edges · critic_status · canvas handoff",
                  "Materialize creates draft swarm members only · production activation stays fail-closed",
                  ...view.handoffNotes,
                ]
                  .filter(Boolean)
                  .join(" · ")}
              />
            </p>
            <div className="composer-home__rec-actions">
              <button
                className="composer-home__ghost"
                onClick={() =>
                  announce(
                    "Export graph requires an authorized export action reference.",
                  )
                }
                type="button"
              >
                Export
              </button>
              {lastCanvasPath ? (
                <Link className="composer-home__primary" href={lastCanvasPath}>
                  Execute
                </Link>
              ) : (
                <button
                  className="composer-home__primary"
                  disabled={aiBusy || !lastGoal}
                  onClick={() => void materializeAndOpen()}
                  type="button"
                >
                  Execute
                </button>
              )}
            </div>
          </div>
        </section>
      </div>

      {view.footerNote ? (
        <p className="composer-home__footer composer-home__footer--tip">
          <InfoTooltip label="Plan notes" text={view.footerNote} />
        </p>
      ) : null}
    </section>
  );
}

function WorkflowDiagram({
  graph,
}: Readonly<{ graph: ComposerWorkflowGraph }>): JSX.Element {
  const phases = graph.nodes.filter((n) => n.kind === "phase");
  const agents = graph.nodes.filter((n) => n.kind !== "phase");

  return (
    <div className="composer-home__wf-canvas" aria-label="Workflow graph">
      <div className="composer-home__wf-phases">
        {phases.map((phase) => (
          <div className="composer-home__wf-phase" key={phase.id}>
            {phase.title}
          </div>
        ))}
      </div>
      <div className="composer-home__wf-nodes">
        {agents.length === 0 ? (
          <p className="composer-home__wf-empty">
            Run <strong>AI plan</strong> on a goal/spec to generate the crew
            workflow diagram.
          </p>
        ) : (
          agents.map((node, index) => (
            <React.Fragment key={node.id}>
              {index > 0 ? (
                <span
                  aria-hidden="true"
                  className={
                    node.kind === "gate"
                      ? "composer-home__wf-arrow composer-home__wf-arrow--gate"
                      : "composer-home__wf-arrow"
                  }
                >
                  →
                </span>
              ) : null}
              <article
                className={
                  node.kind === "gate"
                    ? "composer-home__wf-node composer-home__wf-node--gate"
                    : "composer-home__wf-node"
                }
              >
                {node.kind === "gate" ? (
                  <span className="composer-home__wf-badge">GATE</span>
                ) : (
                  <span className="composer-home__wf-badge composer-home__wf-badge--agent">
                    agent
                  </span>
                )}
                <strong>{node.title}</strong>
                <span title={node.subtitle}>{node.subtitle}</span>
              </article>
            </React.Fragment>
          ))
        )}
      </div>
      {graph.edges.some((e) => e.style === "refine") ? (
        <p className="composer-home__wf-refine">
          refine ≤3 · verify cycle back to craft (Agent Workflow style)
        </p>
      ) : null}
      <div className="composer-home__wf-callouts">
        <div>
          <strong>Closed world</strong>
          <span>0 invented agents</span>
        </div>
        <div>
          <strong>Trace · brief → slots</strong>
          <span>AI binds catalog only</span>
        </div>
      </div>
    </div>
  );
}

// Keep type export used by tests for pattern cards if needed
export type { ComposerPatternCard, ScreenLabels };
