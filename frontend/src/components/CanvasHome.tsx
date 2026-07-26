"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";

import {
  type CanvasLandingView,
  type CanvasNodeStatus,
  type CanvasPaletteTab,
  type CanvasViewMode,
} from "../lib/projections/canvas-landing";
import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";

export function CanvasHome({
  view }: Readonly<{ view: CanvasLandingView }>): JSX.Element {
  const labels = view.labels;
  const [swarmName, setSwarmName] = useState(view.swarmName);
  const [mode, setMode] = useState<CanvasViewMode>(view.viewMode);
  const [paletteTab, setPaletteTab] = useState<CanvasPaletteTab>("common");
  const [selectedId, setSelectedId] = useState<string | undefined>("verifier");
  const [paletteQuery, setPaletteQuery] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const [expandedGroups, setExpandedGroups] = useState<ReadonlySet<string>>(
    () => new Set(view.groups.map((group) => group.id)),
  );
  const [logsOpen, setLogsOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [inspectorTab, setInspectorTab] = useState<
    CanvasLandingView["inspectorTabs"][number]["id"]
  >("task");
  const [focusMode, setFocusMode] = useState(false);

  const selected = view.nodes.find((node) => node.id === selectedId);

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

  const announce = (message: string): void => setStatusMessage(message);

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

  return (
    <section
      aria-label={L(labels, "swarm_canvas")}
      className={
        focusMode ? "canvas-home canvas-home--focus" : "canvas-home"
      }
    >
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
          <Link className="canvas-home__pattern-badge" href="/blueprints">
            {view.patternBadge}
          </Link>
        </div>
        <div aria-label={L(labels, "view_mode")} className="canvas-home__modes" role="group">
          {(["design", "run", "compare"] as const).map((entry) => (
            <button
              aria-pressed={mode === entry}
              className={
                mode === entry
                  ? "canvas-home__mode canvas-home__mode--active"
                  : "canvas-home__mode"
              }
              key={entry}
              onClick={() => setMode(entry)}
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
          <div className="canvas-home__copilot">
            <button
              aria-expanded={copilotOpen}
              className="canvas-home__ghost canvas-home__ghost--violet"
              onClick={() => setCopilotOpen((open) => !open)}
              type="button"
            >
              ✧ Co-Pilot
            </button>
            {copilotOpen ? (
              <ul className="canvas-home__copilot-menu">
                {view.copilotActions.map((action) => (
                  <li key={action}>
                    <button
                      onClick={() => {
                        setCopilotOpen(false);
                        announce(
                          `Co-Pilot “${action}” requires an authorized assist action.`,
                        );
                      }}
                      type="button"
                    >
                      {action}
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
          <button
            className="canvas-home__ghost"
            onClick={() => announce(L(labels, "auto_layout_is_local_only_feedback"))}
            type="button"
          >
            Layout
          </button>
          <button
            className="canvas-home__ghost"
            onClick={() => setFocusMode((open) => !open)}
            type="button"
          >
            {focusMode ? "Exit focus" : "Focus"}
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
          <button
            className="canvas-home__run"
            onClick={() => {
              setMode("run");
              announce(
                "Run command requires an authorized graph action reference.",
              );
            }}
            type="button"
          >
            ▶ Run
          </button>
          <button
            className="canvas-home__ab"
            onClick={() =>
              announce(L(labels, "a_b_test_requires_an_authorized_rollout_contract"))
            }
            type="button"
          >
            A/B Test
          </button>
        </div>
      </header>

      {statusMessage ? (
        <p aria-live="polite" className="canvas-home__status" role="status">
          {statusMessage}
        </p>
      ) : null}

      <div className="canvas-home__body">
        <aside aria-label={L(labels, "node_palette")} className="canvas-home__palette">
          <div
            aria-label={L(labels, "palette_tabs")}
            className="canvas-home__tabs"
            role="tablist"
          >
            {(
              [
                ["common", "Common"],
                ["custom", "Custom"],
                ["patterns", "Patterns"],
              ] as const
            ).map(([id, label]) => (
              <button
                aria-selected={paletteTab === id}
                className={
                  paletteTab === id
                    ? "canvas-home__tab canvas-home__tab--active"
                    : "canvas-home__tab"
                }
                key={id}
                onClick={() => setPaletteTab(id)}
                role="tab"
                type="button"
              >
                {label}
              </button>
            ))}
          </div>
          <label className="canvas-home__ai-suggest">
            <span className="visually-hidden">{L(labels, "ai_suggest_node")}</span>
            <input
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  announce(
                    "AI Suggest Node requires an authorized assist action.",
                  );
                }
              }}
              placeholder={L(labels, "ai_suggest_node_2")}
            />
          </label>
          <label className="canvas-home__search">
            <span className="visually-hidden">{L(labels, "search_common_agents")}</span>
            <input
              onChange={(event) => setPaletteQuery(event.target.value)}
              placeholder={L(labels, "search_common_agents_2")}
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
                      `Local preview: “${item.name}” would be added as a linked node when graph mutations are authorized.`,
                    )
                  }
                  type="button"
                >
                  <span aria-hidden="true" className="canvas-home__palette-icon">
                    {item.kind === "verifier"
                      ? "✓"
                      : item.kind === "fork"
                        ? "⑂"
                        : item.kind === "router"
                          ? "◇"
                          : "●"}
                  </span>
                  <span>
                    <strong>{item.name}</strong>
                    <small>{item.meta}</small>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="canvas-home__main">
          <div aria-label={L(labels, "swarm_graph_canvas")} className="canvas-home__board">
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
                    {group.versionLabel ? (
                      <span className="canvas-home__version-pill">
                        {group.versionLabel}
                      </span>
                    ) : null}
                    <button
                      className="canvas-home__linkish"
                      onClick={() =>
                        announce(
                          "Update all internal commons requires an authorized bulk version action.",
                        )
                      }
                      type="button"
                    >
                      Update all →
                    </button>
                    <button
                      className="canvas-home__ghost canvas-home__ghost--tiny"
                      onClick={() => toggleGroup(group.id)}
                      type="button"
                    >
                      {expanded ? "Collapse" : "Expand"}
                    </button>
                  </header>
                  {expanded ? (
                    <>
                      <div className="canvas-home__group-nodes">
                        {groupNodes.map((node) => (
                          <GraphNodeCard
                            key={node.id}
                            node={node}
                            selected={node.id === selectedId}
                            onSelect={setSelectedId}
                           labels={labels} />
                        ))}
                      </div>
                      {group.cycleLabel ? (
                        <p className="canvas-home__cycle">{group.cycleLabel}</p>
                      ) : null}
                    </>
                  ) : (
                    <p className="canvas-home__muted">
                      Group collapsed · {groupNodes.length} nodes
                    </p>
                  )}
                </section>
              );
            })}

            <div className="canvas-home__ungrouped">
              {view.nodes
                .filter((node) => node.groupId === undefined)
                .map((node) => (
                  <GraphNodeCard
                    key={node.id}
                    node={node}
                    selected={node.id === selectedId}
                    onSelect={setSelectedId}
                   labels={labels} />
                ))}
            </div>

            <section
              aria-label={L(labels, "graph_relationship_semantics")}
              className="canvas-home__edges"
            >
              <h3>{L(labels, "edges")}</h3>
              <ul>
                {view.edges.map((edge) => (
                  <li data-edge-line-style={edge.style} key={edge.id}>
                    <span
                      aria-hidden="true"
                      className={`canvas-home__edge-line canvas-home__edge-line--${edge.style}`}
                    />
                    {edge.label}: {edge.from} → {edge.to}
                  </li>
                ))}
              </ul>
            </section>

            <div className="canvas-home__overlays" aria-hidden="true">
              <div className="canvas-home__minimap">
                <i />
                <i />
                <i />
              </div>
              <div className="canvas-home__zoom">
                <button type="button">+</button>
                <button type="button">−</button>
                <button type="button">⤢</button>
              </div>
            </div>
          </div>

          <div
            aria-live="polite"
            className="canvas-home__runbar"
            role="status"
          >
            <span className="canvas-home__run-dot" />
            <strong>{view.runBar.activeNodesLabel}</strong>
            <span>{view.runBar.progressLabel}</span>
            <span
              aria-label={`Progress ${view.runBar.progressPercent} percent`}
              className="canvas-home__run-progress"
            >
              <i style={{ width: `${view.runBar.progressPercent}%` }} />
            </span>
            <span>
              cost so far {view.runBar.costSoFar} · elapsed {view.runBar.elapsed}
            </span>
            <button
              className="canvas-home__ghost canvas-home__ghost--tiny"
              onClick={() =>
                announce(
                  "Partial replay requires an authorized checkpoint action.",
                )
              }
              type="button"
            >
              Partial replay
            </button>
            <button
              className="canvas-home__cancel"
              onClick={() =>
                announce(L(labels, "cancel_requires_an_authorized_cancel_action"))
              }
              type="button"
            >
              Cancel
            </button>
            <button
              className="canvas-home__ghost canvas-home__ghost--tiny"
              onClick={() => setLogsOpen((open) => !open)}
              type="button"
            >
              ≡ logs
            </button>
          </div>

          {logsOpen ? (
            <section aria-label={L(labels, "streaming_logs")} className="canvas-home__logs">
              <h3>{L(labels, "streaming_logs")}</h3>
              <p className="canvas-home__muted">
                Local preview · live node logs appear when run SSE is authorized.
              </p>
            </section>
          ) : null}
        </div>

        <aside aria-label={L(labels, "canvas_inspector")} className="canvas-home__inspector">
          {selected === undefined ? (
            <>
              <p className="eyebrow">{view.settingsEyebrow}</p>
              <h2>{swarmName}</h2>
              <p className="canvas-home__muted">{view.patternBadge}</p>
              <p className="canvas-home__muted">{view.commonsSummary}</p>
              <button
                className="canvas-home__ghost"
                onClick={() =>
                  announce(
                    "Contribute as pattern requires an authorized proposal.",
                  )
                }
                type="button"
              >
                Contribute swarm as new pattern
              </button>
            </>
          ) : (
            <>
              <p className="eyebrow">
                {view.selectedEyebrowTemplate.replace(
                  "{kind}",
                  selected.kind.toUpperCase(),
                )}
              </p>
              <h2>{selected.label}</h2>
              <div className="canvas-home__inspector-badges">
                <span className="canvas-home__version-pill">
                  {selected.versionLabel}
                </span>
                <StatusPill
                  label={selected.statusLabel}
                  status={selected.status}
                />
              </div>
              {selected.blockedReason ? (
                <p className="canvas-home__blocked" role="status">
                  Blocked: {selected.blockedReason}
                </p>
              ) : null}

              {selected.aggregateEval ? (
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
                    <div>
                      <dt>{L(labels, "avg_tok")}</dt>
                      <dd>{selected.aggregateEval.avgTokens}</dd>
                    </div>
                  </dl>
                </div>
              ) : null}

              {selected.improvementHistory?.length ? (
                <div className="canvas-home__history">
                  <p>{L(labels, "improvement_history")}</p>
                  {selected.improvementHistory.map((item) => (
                    <article key={item.title}>
                      <strong>{item.title}</strong>
                      <span>{item.detail}</span>
                      <em>{item.impact}</em>
                    </article>
                  ))}
                </div>
              ) : null}

              <div className="canvas-home__inspector-actions">
                <button
                  className="canvas-home__primary"
                  onClick={() =>
                    announce(
                      "Update to latest safe requires an authorized version action.",
                    )
                  }
                  type="button"
                >
                  Update to latest safe
                </button>
                <button
                  className="canvas-home__ghost"
                  onClick={() =>
                    announce(L(labels, "pin_version_requires_an_authorized_pin_action"))
                  }
                  type="button"
                >
                  Pin version
                </button>
                <button
                  className="canvas-home__ghost canvas-home__ghost--violet"
                  onClick={() =>
                    announce(
                      "Propose improvement requires an authorized evolution action.",
                    )
                  }
                  type="button"
                >
                  Propose imp.
                </button>
                <Link
                  className="canvas-home__ghost"
                  href="/registry/agents/local-preview"
                >
                  Open Detail (nn_ui_05) →
                </Link>
              </div>

              {selected.liveInspector?.length ? (
                <div className="canvas-home__live">
                  <p>{L(labels, "live_inspector")}</p>
                  <pre>
                    {selected.liveInspector.map((line) => (
                      <span key={line}>
                        {line}
                        {"\n"}
                      </span>
                    ))}
                  </pre>
                </div>
              ) : null}

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
            </>
          )}

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
      {node.iterationLabel ? (
        <span className="canvas-home__iteration">{node.iterationLabel}</span>
      ) : null}
      <span className="canvas-home__node-version">{node.versionLabel}</span>
      <span className="canvas-home__node-metrics">{node.metrics}</span>
      {node.progressPercent !== undefined ? (
        <span
          aria-label={`Progress ${node.progressPercent} percent`}
          className="canvas-home__node-bar"
        >
          <i style={{ width: `${node.progressPercent}%` }} />
        </span>
      ) : null}
      {node.linked ? (
        <span className="canvas-home__node-link">{L(labels, "registry_linked")}</span>
      ) : (
        <span className="canvas-home__node-link canvas-home__node-link--fork">
          Custom — contribute back?
        </span>
      )}
    </button>
  );
}
