"use client";

/**
 * @duty AgentWorkflowHome — Registry agent workflow flowchart
 * @role Show production-scale and DNA workflow templates; how agents call each other.
 * @controls Pack selector, workflow template dropdown, fit-view, agent detail links.
 * @must Use generated agent-workflow payload only.
 * @mustnot Invent handoffs outside template callEdges / DNA steps.
 */
import React, { useEffect, useMemo, useState } from "react";
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

import type {
  AgentWorkflowPackGroup,
  AgentWorkflowPayload,
  AgentWorkflowTemplate,
} from "../lib/projections/agent-workflow.generated";
import {
  buildWorkflowLayout,
  findTemplate,
  listTemplatesForGroup,
  listWorkflowGroups,
  type WorkflowFlowNodeData,
} from "../lib/projections/agent-workflow-layout";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

type WfFlowNode = Node<WorkflowFlowNodeData, "workflowNode">;

function WorkflowNode({ data }: NodeProps<WfFlowNode>): JSX.Element {
  const kindClass =
    data.kind === "phase"
      ? "agent-workflow-node--phase"
      : data.humanGate
        ? "agent-workflow-node--gate"
        : "agent-workflow-node--agent";

  const body = (
    <>
      <Handle type="target" position={Position.Left} className="agent-workflow-handle" />
      <div className="agent-workflow-node__title">{data.title}</div>
      <div className="agent-workflow-node__subtitle" title={data.subtitle}>
        {data.subtitle}
      </div>
      {data.kind === "phase" ? (
        <span className="agent-workflow-node__badge">Phase</span>
      ) : null}
      {data.humanGate ? (
        <span className="agent-workflow-node__badge agent-workflow-node__badge--gate">
          Human gate
        </span>
      ) : null}
      <Handle type="source" position={Position.Right} className="agent-workflow-handle" />
    </>
  );

  if (data.href && data.kind === "agent") {
    return (
      <Link href={data.href} className={`agent-workflow-node ${kindClass}`}>
        {body}
      </Link>
    );
  }
  return <div className={`agent-workflow-node ${kindClass}`}>{body}</div>;
}

const nodeTypes = {
  workflowNode: WorkflowNode,
} satisfies NodeTypes;

function WorkflowCanvas({
  template,
}: Readonly<{ template: AgentWorkflowTemplate }>): JSX.Element {
  const layout = useMemo(() => buildWorkflowLayout(template), [template]);
  const nodes = layout.nodes as WfFlowNode[];
  const edges = [...layout.edges];
  const rf = useReactFlow();
  const flowHeight = useStore((state) => state.height);

  useEffect(() => {
    rf.fitView({ padding: 0.06, maxZoom: 1.5 });
    const vp = rf.getViewport();
    const minY = layout.nodes.reduce(
      (min, node) => Math.min(min, node.position.y),
      Infinity,
    );
    const topInset = flowHeight * 0.05;
    rf.setViewport({ x: vp.x, y: topInset - minY * vp.zoom, zoom: vp.zoom });
  }, [rf, flowHeight, layout]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.06, maxZoom: 1.5 }}
      minZoom={0.12}
      maxZoom={1.5}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable
      proOptions={{ hideAttribution: true }}
      className="agent-workflow-flow"
    >
      <Background gap={18} size={1} color="#e7e5e4" />
      <Controls showInteractive={false} />
      <MiniMap
        pannable
        zoomable
        nodeStrokeWidth={2}
        className="agent-workflow-minimap"
        nodeColor={(node) => {
          const data = node.data as WorkflowFlowNodeData | undefined;
          if (data?.kind === "phase") return "#a8a29e";
          if (data?.humanGate) return "#c2410c";
          return "#0f766e";
        }}
      />
    </ReactFlow>
  );
}

function TemplateMeta({
  template,
}: Readonly<{ template: AgentWorkflowTemplate }>): JSX.Element {
  return (
    <div className="agent-workflow-page__meta" aria-label="Workflow template details">
      <div>
        <h2>Background</h2>
        <p>{template.background}</p>
      </div>
      <div>
        <h2>When to use</h2>
        <p>{template.whenToUse}</p>
      </div>
      <div>
        <h2>Who should use</h2>
        <p>{template.whoShouldUse}</p>
      </div>
      <div>
        <h2>How to use</h2>
        <p>{template.howToUse}</p>
      </div>
      {template.archetypes.length > 0 ? (
        <div>
          <h2>Archetypes</h2>
          <p>{template.archetypes.join(" · ")}</p>
        </div>
      ) : null}
      {template.dnaWorkflowId ? (
        <div>
          <h2>DNA workflow</h2>
          <p>
            <code>{template.dnaWorkflowId}</code>
          </p>
        </div>
      ) : null}
    </div>
  );
}

export function AgentWorkflowHome({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: AgentWorkflowPayload;
  onAction?: (action: ScreenUiAction) => void | Promise<void | boolean>;
  statusMessage?: string;
}>): JSX.Element {
  const groups = useMemo(() => listWorkflowGroups(view), [view]);
  const [packId, setPackId] = useState(() => groups[0]?.packId ?? "");
  const [templateId, setTemplateId] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const activeGroup: AgentWorkflowPackGroup | undefined = useMemo(
    () => groups.find((g) => g.packId === packId) ?? groups[0],
    [groups, packId],
  );

  const templates = useMemo(
    () => listTemplatesForGroup(activeGroup),
    [activeGroup],
  );

  // Keep template selection valid when pack changes
  useEffect(() => {
    if (!activeGroup) return;
    const exists = activeGroup.templates.some((t) => t.id === templateId);
    if (!exists) {
      setTemplateId(activeGroup.templates[0]?.id ?? "");
    }
  }, [activeGroup, templateId]);

  const activeTemplate = useMemo(
    () => findTemplate(activeGroup, templateId),
    [activeGroup, templateId],
  );

  const onPackChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    setPackId(event.target.value);
    announce(`Agent group changed to ${event.target.value}.`);
  };

  const onTemplateChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ): void => {
    setTemplateId(event.target.value);
    announce(`Workflow template changed.`);
  };

  if (!activeGroup || !activeTemplate) {
    return (
      <section className="agent-workflow-page" aria-labelledby="agent-workflow-title">
        <header className="agent-workflow-page__header">
          <p className="eyebrow">Registry · Agent Workflow</p>
          <h1 id="agent-workflow-title">Agent Workflow</h1>
          <p className="agent-workflow-page__lede">
            No workflow templates were found to visualize.
          </p>
        </header>
      </section>
    );
  }

  const scaleTemplates = templates.filter((t) => t.kind === "scale");
  const dnaTemplates = templates.filter((t) => t.kind === "dna");

  return (
    <section className="agent-workflow-page" aria-labelledby="agent-workflow-title">
      <header className="agent-workflow-page__header">
        <div className="agent-workflow-page__intro">
          <p className="eyebrow">Registry · Agent Workflow</p>
          <h1 id="agent-workflow-title">Agent Workflow</h1>
          <p className="agent-workflow-page__lede">
            Production-scale and DNA workflow templates for{" "}
            <strong>{activeGroup.folderPath}</strong>. Select a template to see
            how agents call each other (handoffs, phase transitions, human
            gates). Click an agent node for Registry detail.
          </p>
        </div>

        <div
          className="agent-workflow-page__toolbar"
          role="toolbar"
          aria-label="Agent workflow controls"
        >
          <label className="agent-workflow-page__field">
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

          <label className="agent-workflow-page__field agent-workflow-page__field--wide">
            <span>Workflow template</span>
            <select
              value={activeTemplate.id}
              onChange={onTemplateChange}
              aria-label="Select workflow template"
            >
              {scaleTemplates.length > 0 ? (
                <optgroup label="Production scale framework">
                  {scaleTemplates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label} ({t.agentIds.length} agents)
                    </option>
                  ))}
                </optgroup>
              ) : null}
              {dnaTemplates.length > 0 ? (
                <optgroup label="DNA archetypes (A–J)">
                  {dnaTemplates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label} ({t.agentIds.length} agents)
                    </option>
                  ))}
                </optgroup>
              ) : null}
            </select>
          </label>

          <div className="agent-workflow-page__stats" aria-live="polite">
            <span>{activeTemplate.agentIds.length} agents</span>
            <span>{activeTemplate.callEdges.length} call links</span>
            <span>{activeTemplate.phaseOrder.length} phases</span>
            {activeTemplate.scaleId ? (
              <span>Scale {activeTemplate.scaleId}</span>
            ) : (
              <span>DNA</span>
            )}
          </div>
          {feedback ? <p role="status">{feedback}</p> : null}
        </div>
      </header>

      <TemplateMeta template={activeTemplate} />

      <div
        className="agent-workflow-page__legend"
        aria-label="Edge legend"
      >
        <span className="agent-workflow-legend agent-workflow-legend--handoff">
          Handoff
        </span>
        <span className="agent-workflow-legend agent-workflow-legend--phase">
          Phase transition
        </span>
        <span className="agent-workflow-legend agent-workflow-legend--gate">
          Human gate
        </span>
      </div>

      <div
        className="agent-workflow-page__canvas"
        aria-label={`${activeTemplate.label} agent call flowchart`}
      >
        <ReactFlowProvider>
          <WorkflowCanvas template={activeTemplate} />
        </ReactFlowProvider>
      </div>

      <footer className="agent-workflow-page__footer">
        <p>
          Source: <code>{activeTemplate.source}</code> · Pack{" "}
          <code>{activeGroup.folderPath}</code> · Generated from{" "}
          <code>{view.source}</code>
        </p>
      </footer>
    </section>
  );
}
