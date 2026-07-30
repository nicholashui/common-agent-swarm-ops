"use client";

/**
 * @duty OrgChartHome — Registry agent organization chart
 * @role Visualize non-special pack hierarchy (orchestrator top management → departments → agents).
 * @controls Pack selector, critique-edge toggle, fit-view, agent detail links.
 * @must Use pack-generated hierarchy only; specials excluded.
 * @mustnot Invent management relationships outside generated org-chart payload.
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  Handle,
  Position,
  useReactFlow,
  useStore,
  type Node,
  type NodeProps,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import {
  ORG_CHART_PAYLOAD,
  type OrgChartPackGroup,
} from "../lib/projections/org-chart.generated";
import {
  buildOrgChartLayout,
  listOrgChartGroups,
  type OrgChartFlowNodeData,
} from "../lib/projections/org-chart-layout";

type OrgFlowNode = Node<OrgChartFlowNodeData, "orgNode">;

function OrgChartNode({ data }: NodeProps<OrgFlowNode>): JSX.Element {
  const kindClass =
    data.kind === "top"
      ? "org-chart-node--top"
      : data.kind === "department"
        ? "org-chart-node--department"
        : "org-chart-node--agent";

  const body = (
    <>
      <Handle type="target" position={Position.Top} className="org-chart-handle" />
      <div className="org-chart-node__title">{data.title}</div>
      <div className="org-chart-node__subtitle" title={data.subtitle}>
        {data.subtitle}
      </div>
      {data.kind === "top" ? (
        <span className="org-chart-node__badge">Top management</span>
      ) : null}
      {data.kind === "department" && data.memberCount != null ? (
        <span className="org-chart-node__badge org-chart-node__badge--dept">
          {data.memberCount} members
        </span>
      ) : null}
      <Handle type="source" position={Position.Bottom} className="org-chart-handle" />
    </>
  );

  if (data.href) {
    return (
      <Link href={data.href} className={`org-chart-node ${kindClass}`}>
        {body}
      </Link>
    );
  }

  return <div className={`org-chart-node ${kindClass}`}>{body}</div>;
}

const nodeTypes = {
  orgNode: OrgChartNode,
} satisfies NodeTypes;

function OrgChartCanvas({
  group,
  showCritique,
}: Readonly<{
  group: OrgChartPackGroup;
  showCritique: boolean;
}>): JSX.Element {
  const layout = useMemo(
    () => buildOrgChartLayout(group, { showCritique }),
    [group, showCritique],
  );

  const nodes = layout.nodes as OrgFlowNode[];
  const edges = [...layout.edges];

  const rf = useReactFlow();
  const flowHeight = useStore((state) => state.height);

  // Fit the chart to the square, then anchor it to the top edge instead of
  // leaving it vertically centered with empty space above it.
  useEffect(() => {
    rf.fitView({ padding: 0.04, maxZoom: 1.75 });
    const vp = rf.getViewport();
    const minY = layout.nodes.reduce(
      (min, node) => Math.min(min, node.position.y),
      Infinity,
    );
    const topInset = flowHeight * 0.04;
    rf.setViewport({ x: vp.x, y: topInset - minY * vp.zoom, zoom: vp.zoom });
  }, [rf, flowHeight, layout]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.04, maxZoom: 1.75 }}
      minZoom={0.15}
      maxZoom={1.75}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable
      proOptions={{ hideAttribution: true }}
      className="org-chart-flow"
    >
      <Background gap={18} size={1} color="#e7e5e4" />
      <Controls showInteractive={false} />
      <MiniMap
        pannable
        zoomable
        nodeStrokeWidth={2}
        className="org-chart-minimap"
        nodeColor={(node) => {
          const kind = (node.data as OrgChartFlowNodeData | undefined)?.kind;
          if (kind === "top") return "#1d4ed8";
          if (kind === "department") return "#0f766e";
          return "#78716c";
        }}
      />
    </ReactFlow>
  );
}

export function OrgChartHome({
  payload = ORG_CHART_PAYLOAD,
}: Readonly<{
  payload?: typeof ORG_CHART_PAYLOAD;
}>): JSX.Element {
  const groups = useMemo(() => listOrgChartGroups(payload), [payload]);
  const [packId, setPackId] = useState(() => groups[0]?.packId ?? "");
  const [showCritique, setShowCritique] = useState(false);

  const activeGroup = useMemo(
    () => groups.find((g) => g.packId === packId) ?? groups[0],
    [groups, packId],
  );

  const onPackChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      setPackId(event.target.value);
    },
    [],
  );

  if (!activeGroup) {
    return (
      <section className="org-chart-page" aria-labelledby="org-chart-title">
        <header className="org-chart-page__header">
          <p className="eyebrow">Registry · Agent Org Chart</p>
          <h1 id="org-chart-title">Agent Org Chart</h1>
          <p className="org-chart-page__lede">
            No agent groups were found to visualize.
          </p>
        </header>
      </section>
    );
  }

  const topNames = activeGroup.topManagementIds
    .map((id) => activeGroup.agents.find((a) => a.id === id)?.name ?? id)
    .join(", ");

  return (
    <section className="org-chart-page" aria-labelledby="org-chart-title">
      <header className="org-chart-page__header">
        <div className="org-chart-page__intro">
          <p className="eyebrow">Registry · Agent Org Chart</p>
          <h1 id="org-chart-title">Agent Org Chart</h1>
          <p className="org-chart-page__lede">
            Organization hierarchy for agent groups.{" "}
            <strong>{topNames || activeGroup.primaryTopId}</strong> is top
            management and orchestrates the group's agents. Agents are grouped
            into category departments.
          </p>
        </div>

        <div className="org-chart-page__toolbar" role="toolbar" aria-label="Org chart controls">
          <label className="org-chart-page__field">
            <span>Agent group</span>
            <select
              value={activeGroup.packId}
              onChange={onPackChange}
              aria-label="Select agent group"
            >
              {groups.map((g) => (
                <option key={g.packId} value={g.packId}>
                  {g.label} ({g.agentCount} agents · {g.folderPath})
                </option>
              ))}
            </select>
          </label>

          <label className="org-chart-page__toggle">
            <input
              type="checkbox"
              checked={showCritique}
              onChange={(e) => setShowCritique(e.target.checked)}
            />
            <span>Show critique interconnections</span>
          </label>

          <div className="org-chart-page__stats" aria-live="polite">
            <span>{activeGroup.agentCount} agents</span>
            <span>{activeGroup.departmentCount} departments</span>
            <span>{activeGroup.hierarchyEdges.length} hierarchy links</span>
            {showCritique ? (
              <span>{activeGroup.critiqueEdges.length} critique links</span>
            ) : null}
          </div>
        </div>
      </header>

      <div className="org-chart-page__canvas" aria-label={`${activeGroup.label} organization chart`}>
        <ReactFlowProvider>
          <OrgChartCanvas group={activeGroup} showCritique={showCritique} />
        </ReactFlowProvider>
      </div>

      <footer className="org-chart-page__footer">
        <p>
          Source: <code>{payload.source}</code> · Pack{" "}
          <code>{activeGroup.folderPath}</code> · Click an agent node to open
          Registry detail.
        </p>
      </footer>
    </section>
  );
}
