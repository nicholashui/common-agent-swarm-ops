"use client";

/**
 * @duty Canvas — legacy canvas screen + export alias
 * @role Presentational/legacy canvas path; prefer CanvasHome for routes.
 * @controls Run/node inspect/layout via projection + command intents.
 * @mustnot Run topology without host APIs or invent action refs.
 * @redesign docs/frontend_redesign/ui_04_canvas.md
 */
import React, { useState } from "react";

export { CanvasHome } from "./CanvasHome";

import type { CommandIntent } from "../lib/commands/CommandCoordinator";
import type { GeneratedJsonObject } from "../lib/api/client";
import {
  createGraphCommandIntent,
  isGraphActionDisabled,
  mapGraphProjection,
  type GraphActionView,
  type GraphCommandPayload,
  type GraphNodeView,
  type GraphProjectionView,
} from "../lib/projections/graph-adapters";
import { VersionPill } from "./design";

const DEFAULT_CANVAS_PROJECTION = {
  graph_revision: "graph-revision-42",
  state_label: "Running",
  nodes: [
    { id: "web", label: "video.webresearch", kind: "common", immutable_version: "2.4", provenance_reference: "prov:agent:video.webresearch:2.4", task: { lifecycle: "complete", status_detail: "Research bundle complete" } },
    { id: "trend", label: "video.trendintelligence", kind: "common", immutable_version: "1.3", provenance_reference: "prov:agent:video.trendintelligence:1.3", task: { lifecycle: "running", status_detail: "Scoring hooks" } },
    { id: "writer", label: "video.screenwriter", kind: "custom", fork_origin: "video.screenwriter:1.0", custom_reason: "Series bible terminology", task: { lifecycle: "waiting_for_critique", status_detail: "Awaiting judge critique" } },
  ],
  edges: [
    { id: "web-to-trend", source_id: "web", target_id: "trend", relationship: "data_flow", label: "Research bundle" },
    { id: "trend-to-writer", source_id: "trend", target_id: "writer", relationship: "state_flow", label: "Ready for script" },
    { id: "writer-to-trend", source_id: "writer", target_id: "trend", relationship: "iteration", label: "Critique revision" },
  ],
  validation: {
    eligible: true,
    categories: [
      { category: "version", result: "passed" },
      { category: "schema", result: "passed" },
      { category: "tool_policy", result: "passed" },
      { category: "budget", result: "passed" },
      { category: "verification", result: "passed" },
      { category: "rollback", result: "available" },
      { category: "approval", result: "not_required" },
    ],
  },
  action_references: [
    { id: "run-graph-revision-42", label: "Run swarm", eligible: true, kind: "run" },
    { id: "replay-graph-revision-42", label: "Replay failed task", eligible: true, kind: "replay" },
  ],
} as const satisfies GeneratedJsonObject;

export interface GraphCommandRuntime {
  isActionDisabled(actionReferenceId: string): boolean;
  submit(intent: CommandIntent<GraphCommandPayload>, source: "user"): Promise<unknown>;
}

export interface CanvasProps {
  readonly projection?: GeneratedJsonObject;
  readonly commandRuntime?: GraphCommandRuntime;
}

export function Canvas({ projection = DEFAULT_CANVAS_PROJECTION, commandRuntime }: CanvasProps): JSX.Element {
  const graph = mapGraphProjection(projection);
  const [selectedId, setSelectedId] = useState<string | undefined>(graph.nodes[0]?.id);
  const [swarmName, setSwarmName] = useState("Returned swarm graph");
  const [statusNote, setStatusNote] = useState<string | undefined>();
  const selected = graph.nodes.find((node) => node.id === selectedId);

  return <div className="canvas-page"><header className="canvas-toolbar"><div><h1>Swarm canvas</h1><input aria-label="Swarm name" onChange={(event): void => setSwarmName(event.target.value)} value={swarmName} /><p>{graph.graphRevision === undefined ? null : <VersionPill label="Graph revision" version={graph.graphRevision} />} {graph.statusLabel === undefined ? null : <span>{graph.statusLabel}</span>}</p>{statusNote ? <p aria-live="polite" role="status">{statusNote}</p> : null}</div><div className="toolbar-actions"><button className="button button--secondary" onClick={(): void => {
    const summary = graph.validation.categories
      .map((category) => `${category.category}: ${category.result}`)
      .join("; ");
    setStatusNote(`Local validation for “${swarmName}”: ${summary || "no categories returned"}.`);
  }} type="button">Validate</button><GraphActionControls graph={graph} commandRuntime={commandRuntime} /></div></header><div className="canvas-layout"><section className="graph-canvas" aria-label="Swarm graph canvas"><div className="graph-edges" aria-label="Graph relationship semantics"><ul>{graph.edges.map((edge) => <li data-edge-line-style={edge.semantics.lineStyle} data-edge-marker={edge.semantics.marker} key={edge.id}><span className={`graph-edge-line graph-edge-line--${edge.semantics.lineStyle}`} aria-hidden="true" />{edge.semantics.textLabel}: {edge.sourceId} to {edge.targetId}{edge.label === undefined ? null : ` — ${edge.label}`}</li>)}</ul></div><div className="node-row">{graph.nodes.map((node) => <GraphNode key={node.id} node={node} selected={node.id === selectedId} onSelect={setSelectedId} />)}</div></section><aside className="canvas-inspector"><p className="eyebrow">SELECTED NODE</p>{selected === undefined ? <p className="muted">Select a returned graph node.</p> : <NodeInspector node={selected} />}<section className="graph-validation" aria-label="Returned graph validation"><h2>Returned validation</h2><ul>{graph.validation.categories.map((category) => <li key={category.category}><strong>{category.category}</strong>: {category.result}{category.detail === undefined ? null : ` — ${category.detail}`}</li>)}</ul></section></aside></div></div>;
}

function GraphActionControls({ graph, commandRuntime }: { readonly graph: GraphProjectionView; readonly commandRuntime: GraphCommandRuntime | undefined }): JSX.Element {
  const [, setCommandVersion] = useState(0);
  return <>{graph.actions.map((action) => <GraphActionControl action={action} commandRuntime={commandRuntime} graph={graph} key={action.id} onSubmitted={(): void => setCommandVersion((version) => version + 1)} />)}</>;
}

function GraphActionControl({ action, commandRuntime, graph, onSubmitted }: { readonly action: GraphActionView; readonly commandRuntime: GraphCommandRuntime | undefined; readonly graph: GraphProjectionView; readonly onSubmitted: () => void }): JSX.Element {
  const intent = createGraphCommandIntent(action, graph.graphRevision);
  const disabled = intent === undefined || isGraphActionDisabled(action, graph.validation) || commandRuntime === undefined || commandRuntime.isActionDisabled(action.id);
  return <button className={action.kind === "run" ? "button button--primary" : "button button--secondary"} data-action-reference-id={action.id} disabled={disabled} onClick={(): void => {
    if (intent === undefined || disabled || commandRuntime === undefined) return;
    void commandRuntime.submit(intent, "user").finally(onSubmitted);
  }} type="button">{action.label}</button>;
}

function GraphNode({ node, selected, onSelect }: { readonly node: GraphNodeView; readonly selected: boolean; readonly onSelect: (id: string) => void }): JSX.Element {
  const provenance = node.kind === "common" ? node.provenanceReference : node.forkOrigin ?? node.customReason;
  return <button aria-pressed={selected} className={`graph-node graph-node--${node.kind}${selected ? " graph-node--selected" : ""}`} onClick={(): void => onSelect(node.id)} type="button"><strong>{node.label}</strong>{node.kind === "common" && node.immutableVersion !== undefined ? <VersionPill version={node.immutableVersion} label="Common version" /> : null}<small>{node.kind === "common" ? `Provenance: ${provenance ?? ""}` : `Custom: ${provenance ?? ""}`}</small>{node.task === undefined ? null : <div><span>{node.task.lifecycle}</span><span>{node.task.statusDetail}</span></div>}</button>;
}

function NodeInspector({ node }: { readonly node: GraphNodeView }): JSX.Element {
  return <><h2>{node.label}</h2>{node.kind === "common" ? <><p>Common version: {node.immutableVersion}</p><p>Provenance: {node.provenanceReference}</p></> : <><p>Fork origin: {node.forkOrigin}</p><p>Custom reason: {node.customReason}</p></>}{node.task === undefined ? null : <><p>Lifecycle: {node.task.lifecycle}</p>{node.task.statusDetail === undefined ? null : <p>Status detail: {node.task.statusDetail}</p>}</>}</>;
}
