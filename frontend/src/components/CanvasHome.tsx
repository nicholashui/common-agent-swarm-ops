"use client";

/**
 * @duty CanvasHome — swarm orchestration board (ui_04 redesign)
 * @role Inspect Compose-materialized instance workflow; run when Host authorizes.
 * @controls Design | Inspect | Run modes; workflow diagram; member list; inspector; fail-closed run.
 * @must Primary surface = Agent Workflow–style diagram; fail-closed run authority.
 * @mustnot Invent production activation or claim Canvas is the Orchestrator agent.
 * @redesign docs/frontend_redesign/ui_04_canvas_orchestration_preview.svg
 */
import React, { useEffect, useId, useMemo, useRef, useState } from "react";
import Link from "next/link";

import {
  type CanvasLandingView,
  type CanvasNodeStatus,
  type CanvasPaletteTab,
  type CanvasViewMode,
} from "../lib/projections/canvas-landing";
import {
  applyCanvasSample,
  CANVAS_SAMPLES,
  type CanvasSample,
} from "../lib/projections/canvas-samples";
import { buildWorkflowGraphFromCanvasNodes } from "../lib/projections/composer-workflow";
import { L, type ScreenLabels } from "../lib/projections/screen-labels";
import { clampZoom } from "../lib/ui/local-controls";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";
import { WorkflowDiagramPanel } from "./workflow/WorkflowDiagramPanel";

export function CanvasHome({
  view: baseView,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: CanvasLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const [sampleView, setSampleView] = useState<CanvasLandingView | null>(null);
  const view = sampleView ?? baseView;
  const labels = view.labels;
  const [swarmName, setSwarmName] = useState(view.swarmName);
  const [mode, setMode] = useState<CanvasViewMode>(
    view.viewMode === "compare" ? "inspect" : view.viewMode || "inspect",
  );
  const [paletteTab, setPaletteTab] = useState<CanvasPaletteTab>("common");
  const [selectedId, setSelectedId] = useState<string | undefined>(
    () => view.nodes.find((n) => n.kind === "verifier")?.id ?? view.nodes[0]?.id,
  );
  const [paletteQuery, setPaletteQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [expandedGroups, setExpandedGroups] = useState<ReadonlySet<string>>(
    () => new Set(view.groups.map((group) => group.id)),
  );
  const [logsOpen, setLogsOpen] = useState(false);
  const [inspectorTab, setInspectorTab] = useState<
    CanvasLandingView["inspectorTabs"][number]["id"]
  >("task");
  const [zoom, setZoom] = useState(1);
  const [aiSuggest, setAiSuggest] = useState("");
  const [designToolsOpen, setDesignToolsOpen] = useState(false);
  const [samplesOpen, setSamplesOpen] = useState(false);
  const samplesDialogTitleId = useId();
  const samplesCloseRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!samplesOpen) return;
    samplesCloseRef.current?.focus();
    const onKey = (event: globalThis.KeyboardEvent): void => {
      if (event.key === "Escape") setSamplesOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [samplesOpen]);

  useEffect(() => {
    if (sampleView) return;
    setSwarmName(baseView.swarmName);
    if (
      baseView.nodes.length > 0 &&
      !baseView.nodes.some((n) => n.id === selectedId)
    ) {
      setSelectedId(baseView.nodes[0]?.id);
    }
  }, [baseView, sampleView, selectedId]);

  useEffect(() => {
    setSwarmName(view.swarmName);
    const pick =
      view.nodes.find((n) => n.kind === "verifier")?.id ?? view.nodes[0]?.id;
    if (pick) setSelectedId(pick);
    setMode("inspect");
  }, [view.instanceId, view.swarmName, view.nodes]);

  const selected = view.nodes.find((node) => node.id === selectedId);

  const workflowGraph = useMemo(
    () =>
      buildWorkflowGraphFromCanvasNodes(
        view.nodes,
        view.patternBadge || view.swarmName,
      ),
    [view.nodes, view.patternBadge, view.swarmName],
  );

  const loadSample = (sample: CanvasSample): void => {
    const next = applyCanvasSample(baseView, sample);
    setSampleView(next);
    setSwarmName(next.swarmName);
    setSamplesOpen(false);
    setMode("inspect");
    setSelectedId(
      next.nodes.find((n) => n.kind === "verifier")?.id ?? next.nodes[0]?.id,
    );
    announce(
      `Loaded sample “${sample.label}” on Canvas (${sample.nodes.length} agents). Local/demo only.`,
    );
  };

  const clearSample = (): void => {
    setSampleView(null);
    setSwarmName(baseView.swarmName);
    setSelectedId(
      baseView.nodes.find((n) => n.kind === "verifier")?.id ??
        baseView.nodes[0]?.id,
    );
    announce("Cleared sample. Restored Host/live or demo landing view.");
  };

  const paletteItems = useMemo(() => {
    const q = paletteQuery.trim().toLowerCase();
    return view.palette.filter((item) => {
      if (item.tab !== paletteTab) return false;
      if (q.length === 0) return true;
      return (
        item.name.toLowerCase().includes(q) ||
        item.meta.toLowerCase().includes(q)
      );
    });
  }, [paletteQuery, paletteTab, view.palette]);

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const toggleGroup = (groupId: string): void => {
    setExpandedGroups((current) => {
      const next = new Set(current);
      if (next.has(groupId)) next.delete(groupId);
      else next.add(groupId);
      return next;
    });
  };

  const activeInspector =
    view.inspectorTabs.find((tab) => tab.id === inspectorTab) ??
    view.inspectorTabs[0];

  const isLiveInstance =
    Boolean(view.instanceId) && view.instanceId !== "demo-landing";
  const lifecycleStep: 1 | 2 | 3 | 4 = isLiveInstance ? 3 : 3;

  const runInstance = (): void => {
    setMode("run");
    if (onAction) {
      void onAction({
        kind: "canvas.run",
        workflowId:
          view.instanceId ??
          (view.swarmName.replace(/\s+/g, "-").toLowerCase() || "default"),
        version: String(view.instanceRevision ?? 1),
      });
      return;
    }
    announce("Run instance requires an authorized Host graph action reference.");
  };

  const modes: CanvasViewMode[] = ["design", "inspect", "run"];

  return (
    <section
      aria-label={L(labels, "swarm_canvas")}
      className="canvas-home canvas-home--orch"
    >
      {/* ── Toolbar ── */}
      <header className="canvas-home__toolbar">
        <div className="canvas-home__toolbar-left">
          <label className="canvas-home__name">
            <span className="visually-hidden">{L(labels, "swarm_name")}</span>
            <input
              aria-label={L(labels, "swarm_name")}
              onChange={(event) => setSwarmName(event.target.value)}
              value={swarmName}
            />
          </label>
          {view.instanceId ? (
            <span className="canvas-home__instance-meta">
              instance{" "}
              <code>
                {view.instanceId.length > 18
                  ? `${view.instanceId.slice(0, 14)}…`
                  : view.instanceId}
              </code>
              {view.instanceStatus ? ` · ${view.instanceStatus}` : ""}
              {view.instanceRevision !== undefined
                ? ` · rev ${view.instanceRevision}`
                : ""}
            </span>
          ) : null}
          <span className="canvas-home__pattern-badge">{view.patternBadge}</span>
          {view.fromCompose ? (
            <span className="canvas-home__pill canvas-home__pill--indigo">
              From Compose
            </span>
          ) : (
            <span className="canvas-home__pill">Demo / local landing</span>
          )}
          {isLiveInstance ? (
            <span className="canvas-home__pill canvas-home__pill--ok">
              Live draft
            </span>
          ) : null}
        </div>

        <div
          aria-label={L(labels, "view_mode")}
          className="canvas-home__modes"
          role="group"
        >
          {modes.map((entry) => (
            <button
              aria-pressed={mode === entry}
              className={
                mode === entry
                  ? "canvas-home__mode canvas-home__mode--active"
                  : "canvas-home__mode"
              }
              key={entry}
              onClick={() => {
                setMode(entry);
                if (entry === "design") setDesignToolsOpen(true);
              }}
              type="button"
            >
              {entry[0]?.toUpperCase()}
              {entry.slice(1)}
            </button>
          ))}
        </div>

        <p className="canvas-home__commons" role="status">
          {view.commonsSummary}
        </p>

        <div className="canvas-home__toolbar-right">
          <button
            className="canvas-home__ghost"
            onClick={() => {
              if (onAction) {
                void onAction({
                  kind: "local.layout",
                  detail: L(labels, "auto_layout_is_local_only_feedback"),
                });
                return;
              }
              announce(L(labels, "auto_layout_is_local_only_feedback"));
            }}
            type="button"
          >
            Layout
          </button>
          <button
            className="canvas-home__ghost"
            onClick={() =>
              announce(L(labels, "export_requires_an_authorized_export_action"))
            }
            type="button"
          >
            Export
          </button>
          <button className="canvas-home__run" onClick={runInstance} type="button">
            ▶ Run instance
          </button>
          <Link className="canvas-home__ghost" href="/composer">
            ← Compose
          </Link>
        </div>
      </header>

      {/* ── Lifecycle strip ── */}
      <ol className="canvas-home__lifecycle" aria-label="Instance lifecycle">
        <li
          className={
            lifecycleStep >= 1
              ? "canvas-home__life canvas-home__life--done"
              : "canvas-home__life"
          }
        >
          <span className="canvas-home__life-n">1</span>
          Compose created workflow
        </li>
        <li className="canvas-home__life-sep" aria-hidden="true">
          →
        </li>
        <li
          className={
            isLiveInstance
              ? "canvas-home__life canvas-home__life--done"
              : "canvas-home__life"
          }
        >
          <span className="canvas-home__life-n">2</span>
          Materialized draft instance
        </li>
        <li className="canvas-home__life-sep" aria-hidden="true">
          →
        </li>
        <li className="canvas-home__life canvas-home__life--active">
          <span className="canvas-home__life-n">3</span>
          Canvas inspect / run board
        </li>
        <li className="canvas-home__life-sep" aria-hidden="true">
          →
        </li>
        <li
          className={
            mode === "run"
              ? "canvas-home__life canvas-home__life--active"
              : "canvas-home__life"
          }
        >
          <span className="canvas-home__life-n">4</span>
          Host run (fail-closed)
        </li>
        <li className="canvas-home__life-meta">
          {workflowGraph.agentCount + workflowGraph.gateCount} agents ·{" "}
          {workflowGraph.phaseCount} phases · {workflowGraph.gateCount} gate ·
          production: off
        </li>
      </ol>

      {feedback ? (
        <p aria-live="polite" className="canvas-home__status" role="status">
          {feedback}
        </p>
      ) : null}

      <div className="canvas-home__body canvas-home__body--orch">
        {/* ── LEFT: instance + members ── */}
        <aside className="canvas-home__rail" aria-label="Instance crew">
          <div className="canvas-home__rail-head">
            <p className="canvas-home__rail-kicker">INSTANCE</p>
            <button
              aria-haspopup="dialog"
              aria-expanded={samplesOpen}
              className="canvas-home__samples-trigger"
              onClick={() => setSamplesOpen(true)}
              title="Sample instances (load into UI)"
              type="button"
            >
              <span aria-hidden="true">▦</span>
              <span className="visually-hidden">Open sample instances</span>
            </button>
          </div>
          <h2 className="canvas-home__rail-title">Swarm draft</h2>
          <p className="canvas-home__rail-id">
            <code>{view.instanceId ?? "local-demo"}</code>
          </p>
          {sampleView ? (
            <button
              className="canvas-home__ghost canvas-home__ghost--tiny"
              onClick={clearSample}
              type="button"
            >
              Clear sample · restore view
            </button>
          ) : null}

          <div className="canvas-home__rail-card">
            <strong>Source</strong>
            <span>{view.sourceLabel ?? "Local canvas projection"}</span>
            <span className="canvas-home__rail-muted">
              {view.fromCompose
                ? "closed-world catalog · AI-pick"
                : "Use Compose → Accept AI for live Host draft"}
            </span>
          </div>

          <p className="canvas-home__rail-kicker">CREW MEMBERS</p>
          <ul className="canvas-home__member-list">
            {view.nodes.map((node) => {
              const isGate =
                node.kind === "verifier" ||
                /judge|gate|verif/i.test(node.label);
              const isMeta = /orchestrat|planner|supervisor/i.test(
                `${node.label} ${node.kind}`,
              );
              return (
                <li key={node.id}>
                  <button
                    className={
                      selectedId === node.id
                        ? "canvas-home__member canvas-home__member--selected"
                        : isGate
                          ? "canvas-home__member canvas-home__member--gate"
                          : isMeta
                            ? "canvas-home__member canvas-home__member--meta"
                            : "canvas-home__member"
                    }
                    onClick={() => setSelectedId(node.id)}
                    type="button"
                  >
                    <strong>{node.label}</strong>
                    <span>
                      {node.versionLabel}
                      {isGate ? " · GATE" : isMeta ? " · meta" : ""}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>

          <p className="canvas-home__rail-kicker">DESIGN TOOLS</p>
          <button
            className="canvas-home__design-toggle"
            onClick={() => {
              setDesignToolsOpen((o) => !o);
              setMode("design");
            }}
            type="button"
          >
            {designToolsOpen || mode === "design"
              ? "Hide palette · AI suggest · Patterns"
              : "Palette · AI suggest · Patterns"}
          </button>
          <p className="canvas-home__rail-muted">
            Available in Design mode. Inspect prioritizes workflow.
          </p>

          {(designToolsOpen || mode === "design") && (
            <div className="canvas-home__palette canvas-home__palette--embedded">
              <div className="canvas-home__tabs" role="group">
                {(["common", "custom", "patterns"] as const).map((tab) => (
                  <button
                    aria-pressed={paletteTab === tab}
                    className={
                      paletteTab === tab
                        ? "canvas-home__tab canvas-home__tab--active"
                        : "canvas-home__tab"
                    }
                    key={tab}
                    onClick={() => setPaletteTab(tab)}
                    type="button"
                  >
                    {tab[0]?.toUpperCase()}
                    {tab.slice(1)}
                  </button>
                ))}
              </div>
              <label className="canvas-home__ai-suggest">
                <span className="visually-hidden">AI Suggest Node</span>
                <input
                  onChange={(e) => setAiSuggest(e.target.value)}
                  placeholder="✧ AI Suggest Node…"
                  value={aiSuggest}
                />
              </label>
              <label className="canvas-home__search">
                <span className="visually-hidden">Search</span>
                <input
                  onChange={(e) => setPaletteQuery(e.target.value)}
                  placeholder="Search Common Agents…"
                  value={paletteQuery}
                />
              </label>
              <ul className="canvas-home__palette-list">
                {paletteItems.map((item) => (
                  <li key={item.id}>
                    <button
                      className={`canvas-home__palette-item canvas-home__palette-item--${item.kind}`}
                      onClick={() =>
                        announce(
                          `Local preview: “${item.name}” would be added when graph mutations are authorized.`,
                        )
                      }
                      type="button"
                    >
                      <strong>{item.name}</strong>
                      <small>{item.meta}</small>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="canvas-home__fail-closed" role="note">
            <strong>Fail-closed run</strong>
            <p>Run needs Host action reference.</p>
            <p>No silent production activation.</p>
            <p>Drafts process-local (restart clears).</p>
          </div>

          <Link className="canvas-home__rail-link" href="/composer">
            ← Edit in Compose
          </Link>
          <Link className="canvas-home__rail-link canvas-home__rail-link--ghost" href="/registry">
            All Host drafts…
          </Link>
        </aside>

        {/* ── CENTER: workflow diagram ── */}
        <div className="canvas-home__main">
          <section
            aria-label="Workflow diagram"
            className="canvas-home__workflow-panel"
          >
            <header className="canvas-home__workflow-head">
              <p className="canvas-home__workflow-kicker">
                WORKFLOW DIAGRAM · ORCHESTRATION BOARD
              </p>
              <h2>Crew workflow (Agent Workflow style)</h2>
              <p>
                Inspect the instance graph: phases · agents · gates. Run when
                Host authorizes · fail-closed. Human board ≠ Orchestrator agent.
              </p>
            </header>
            <div style={{ transform: `scale(${zoom})`, transformOrigin: "top left" }}>
              <WorkflowDiagramPanel
                emptyHint="No agents on this canvas yet. Materialize from Compose (Accept AI → Canvas) or open /swarms/{id}/canvas."
                graph={workflowGraph}
              />
            </div>
            <div className="canvas-home__board-tools">
              <button
                aria-label="Zoom in"
                className="canvas-home__ghost canvas-home__ghost--tiny"
                onClick={() => setZoom((z) => clampZoom(z + 0.1))}
                type="button"
              >
                +
              </button>
              <button
                aria-label="Zoom out"
                className="canvas-home__ghost canvas-home__ghost--tiny"
                onClick={() => setZoom((z) => clampZoom(z - 0.1))}
                type="button"
              >
                −
              </button>
              <button
                className="canvas-home__ghost canvas-home__ghost--tiny"
                onClick={() => setZoom(1)}
                type="button"
              >
                100%
              </button>
            </div>
          </section>

          {mode === "design" && view.groups.length > 0 ? (
            <div className="canvas-home__legacy-groups">
              <p className="canvas-home__rail-kicker">
                DESIGN MODE · LEGACY GROUPS
              </p>
              {view.groups.map((group) => {
                const groupNodes = view.nodes.filter(
                  (node) => node.groupId === group.id,
                );
                const expanded = expandedGroups.has(group.id);
                return (
                  <section
                    aria-label={group.title}
                    className={`canvas-home__group canvas-home__group--${group.tone}`}
                    key={group.id}
                  >
                    <header className="canvas-home__group-head">
                      <h2>{group.title}</h2>
                      <button
                        className="canvas-home__ghost canvas-home__ghost--tiny"
                        onClick={() => toggleGroup(group.id)}
                        type="button"
                      >
                        {expanded ? "Collapse" : "Expand"}
                      </button>
                    </header>
                    {expanded ? (
                      <div className="canvas-home__group-nodes">
                        {groupNodes.map((node) => (
                          <GraphNodeCard
                            key={node.id}
                            labels={labels}
                            node={node}
                            onSelect={setSelectedId}
                            selected={node.id === selectedId}
                          />
                        ))}
                      </div>
                    ) : (
                      <p className="canvas-home__muted">
                        Group collapsed · {groupNodes.length} nodes
                      </p>
                    )}
                  </section>
                );
              })}
            </div>
          ) : null}

          <div className="canvas-home__runbar" role="status">
            <span className="canvas-home__run-dot" />
            <strong>{view.runBar.activeNodesLabel}</strong>
            <span>{view.runBar.progressLabel}</span>
            <span className="canvas-home__run-progress">
              <i style={{ width: `${view.runBar.progressPercent}%` }} />
            </span>
            <span>
              cost {view.runBar.costSoFar} · elapsed {view.runBar.elapsed}
            </span>
            <button
              className="canvas-home__cancel"
              onClick={() =>
                announce(
                  L(labels, "cancel_requires_an_authorized_cancel_action"),
                )
              }
              type="button"
            >
              Cancel
            </button>
            <button
              className="canvas-home__ghost canvas-home__ghost--tiny"
              onClick={() => setLogsOpen((o) => !o)}
              type="button"
            >
              ≡ logs
            </button>
          </div>
          {logsOpen ? (
            <section className="canvas-home__logs" aria-label="Streaming logs">
              <p className="canvas-home__muted">
                Local preview · live node logs when run SSE is authorized.
              </p>
            </section>
          ) : null}
        </div>

        {/* ── RIGHT: inspector ── */}
        <aside
          aria-label={L(labels, "canvas_inspector")}
          className="canvas-home__inspector canvas-home__inspector--orch"
        >
          <p className="canvas-home__rail-kicker">INSPECTOR</p>
          {selected ? (
            <>
              <h2 className="canvas-home__rail-title">
                Selected · {selected.label}
              </h2>
              <div className="canvas-home__inspector-badges">
                <span className="canvas-home__version-pill">
                  {selected.versionLabel}
                </span>
                <StatusPill
                  label={selected.statusLabel}
                  status={selected.status}
                />
              </div>

              <div
                aria-label={L(labels, "inspector_tabs")}
                className="canvas-home__inspector-tabs"
                role="tablist"
              >
                {view.inspectorTabs.map((tab) => (
                  <button
                    aria-selected={inspectorTab === tab.id}
                    className={
                      inspectorTab === tab.id
                        ? "canvas-home__inspector-tab canvas-home__inspector-tab--active"
                        : "canvas-home__inspector-tab"
                    }
                    key={tab.id}
                    onClick={() => setInspectorTab(tab.id)}
                    role="tab"
                    type="button"
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              {activeInspector ? (
                <ul className="canvas-home__tab-lines">
                  {activeInspector.lines.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              ) : null}

              <div className="canvas-home__rail-card">
                <strong>Node metrics</strong>
                <span>{selected.metrics}</span>
                {selected.linked ? (
                  <span>{L(labels, "registry_linked")}</span>
                ) : (
                  <span>Custom — contribute back?</span>
                )}
              </div>
            </>
          ) : (
            <>
              <h2 className="canvas-home__rail-title">{swarmName}</h2>
              <p className="canvas-home__muted">{view.patternBadge}</p>
            </>
          )}

          <p className="canvas-home__rail-kicker">RUN READINESS</p>
          <ul className="canvas-home__readiness">
            <li data-ok={view.nodes.length > 0 ? "true" : "false"}>
              Graph has members ({view.nodes.length})
            </li>
            <li data-ok="true">Closed-world agent ids</li>
            <li data-ok="warn">Run action: needs Host ref</li>
          </ul>

          <div className="canvas-home__orch-note">
            <strong>Human board ≠ Orchestrator agent</strong>
            <p>Canvas is the inspect/run console.</p>
            <p>
              Orchestrator (when bound) is a <em>node</em> on the graph.
            </p>
            <p>Host owns real execution authority.</p>
          </div>

          <button className="canvas-home__run canvas-home__run--block" onClick={runInstance} type="button">
            ▶ Run instance (Host)
          </button>
          <button
            className="canvas-home__ghost canvas-home__ghost--block"
            onClick={() =>
              announce(
                "Validate graph requires an authorized validate_swarm action.",
              )
            }
            type="button"
          >
            Validate graph
          </button>
          <Link className="canvas-home__ghost canvas-home__ghost--block" href="/activity">
            Open events / Activity
          </Link>

          {selected?.aggregateEval ? (
            <div className="canvas-home__aggregate">
              <p>{L(labels, "aggregate_eval_all_swarms")}</p>
              <dl>
                <div>
                  <dt>{L(labels, "runs")}</dt>
                  <dd>{selected.aggregateEval.runs}</dd>
                </div>
                <div>
                  <dt>{L(labels, "success")}</dt>
                  <dd>{selected.aggregateEval.success}</dd>
                </div>
              </dl>
            </div>
          ) : null}

          <section
            aria-label={L(labels, "returned_graph_validation")}
            className="canvas-home__validation"
          >
            <h3>{L(labels, "returned_validation")}</h3>
            <ul>
              {view.validation.map((item) => (
                <li key={item.category}>
                  <strong>{item.category}</strong>: {item.result}
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </div>

      <p className="canvas-home__footer">{view.footerNote}</p>

      {samplesOpen ? (
        <div className="canvas-home__modal-root" role="presentation">
          <button
            aria-label="Close sample instances"
            className="canvas-home__modal-backdrop"
            onClick={() => setSamplesOpen(false)}
            type="button"
          />
          <div
            aria-labelledby={samplesDialogTitleId}
            aria-modal="true"
            className="canvas-home__modal"
            role="dialog"
          >
            <header className="canvas-home__modal-head">
              <div>
                <h2 id={samplesDialogTitleId}>
                  Sample instances (load into UI)
                </h2>
                <p>
                  Loads a local demo crew onto the workflow diagram — same idea
                  as Compose samples. Does not create a Host draft.
                </p>
              </div>
              <button
                ref={samplesCloseRef}
                className="canvas-home__modal-close"
                onClick={() => setSamplesOpen(false)}
                type="button"
              >
                ✕
              </button>
            </header>
            <ul className="canvas-home__sample-list">
              {CANVAS_SAMPLES.map((sample) => (
                <li
                  className={
                    sample.kind === "lean"
                      ? "canvas-home__sample canvas-home__sample--lean"
                      : "canvas-home__sample"
                  }
                  key={sample.id}
                >
                  <div className="canvas-home__sample-copy">
                    <strong>{sample.label}</strong>
                    <span>{sample.summary}</span>
                    <span className="canvas-home__sample-meta">
                      {sample.nodes.length} agents · {sample.patternBadge}
                    </span>
                  </div>
                  <button
                    className="canvas-home__primary canvas-home__primary--small"
                    onClick={() => loadSample(sample)}
                    type="button"
                  >
                    Load
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function StatusPill({
  status,
  label,
}: Readonly<{ status: CanvasNodeStatus; label: string }>): JSX.Element {
  return (
    <span
      className={`canvas-home__status-pill canvas-home__status-pill--${status}`}
    >
      <span aria-hidden="true" />
      {label}
    </span>
  );
}

function GraphNodeCard({
  node,
  selected,
  onSelect,
  labels,
}: Readonly<{
  node: CanvasLandingView["nodes"][number];
  selected: boolean;
  onSelect: (id: string) => void;
  labels: ScreenLabels;
}>): JSX.Element {
  return (
    <button
      aria-pressed={selected}
      className={`canvas-home__node canvas-home__node--${node.kind}${selected ? " canvas-home__node--selected" : ""}`}
      onClick={() => onSelect(node.id)}
      type="button"
    >
      <div className="canvas-home__node-top">
        <strong>{node.label}</strong>
        <StatusPill label={node.statusLabel} status={node.status} />
      </div>
      <span className="canvas-home__node-version">{node.versionLabel}</span>
      <span className="canvas-home__node-metrics">{node.metrics}</span>
      {node.linked ? (
        <span className="canvas-home__node-link">
          {L(labels, "registry_linked")}
        </span>
      ) : (
        <span className="canvas-home__node-link canvas-home__node-link--fork">
          Custom — contribute back?
        </span>
      )}
    </button>
  );
}
