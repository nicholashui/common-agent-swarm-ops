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
  Panel,
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
import {
  STUB_RUN_HONESTY,
  VIDEO_SPINE_TEMPLATE_ID,
  VIDEO_SPINE_WORKFLOW_ID,
  buildVideoSpineWorkflowTemplate,
  isVideoSpineTemplateId,
} from "../lib/projections/video-spine-template";
import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";

/** Inject Host product spine template into video pack (Epic E). */
function withProductSpineTemplate(
  group: AgentWorkflowPackGroup | undefined,
): AgentWorkflowPackGroup | undefined {
  if (!group || group.packId !== "video") return group;
  if (
    group.templates.some(
      (t) =>
        t.id === VIDEO_SPINE_TEMPLATE_ID ||
        t.dnaWorkflowId === VIDEO_SPINE_WORKFLOW_ID,
    )
  ) {
    return group;
  }
  const spine = buildVideoSpineWorkflowTemplate();
  return {
    ...group,
    templateCount: group.templateCount + 1,
    templates: [spine, ...group.templates],
  };
}

function readTemplateQuery(): string {
  if (typeof window === "undefined") return "";
  try {
    return new URLSearchParams(window.location.search).get("template") ?? "";
  } catch {
    return "";
  }
}

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
      <TemplateNotesPanel template={template} />
    </ReactFlow>
  );
}

/**
 * Compact template remarks (Background → Archetypes) as a small in-diagram note,
 * not a full-width page panel.
 */
function TemplateNotesPanel({
  template,
}: Readonly<{ template: AgentWorkflowTemplate }>): JSX.Element {
  const archetypes =
    template.archetypes.length > 0
      ? template.archetypes.join(" · ")
      : null;
  const summaryBits = [
    template.background ? "Background" : null,
    template.whenToUse ? "When" : null,
    template.whoShouldUse ? "Who" : null,
    template.howToUse ? "How" : null,
    archetypes ? "Archetypes" : null,
    template.dnaWorkflowId ? "DNA" : null,
  ].filter(Boolean);

  return (
    <Panel
      position="top-left"
      className="agent-workflow-notes-panel"
      aria-label="Template notes"
    >
      <details className="agent-workflow-notes">
        <summary className="agent-workflow-notes__summary">
          <span className="agent-workflow-notes__kicker">Notes</span>
          <span className="agent-workflow-notes__peek">
            {summaryBits.join(" · ") || "Template remarks"}
          </span>
        </summary>
        <dl className="agent-workflow-notes__list">
          {template.background ? (
            <div>
              <dt>Background</dt>
              <dd>{template.background}</dd>
            </div>
          ) : null}
          {template.whenToUse ? (
            <div>
              <dt>When to use</dt>
              <dd>{template.whenToUse}</dd>
            </div>
          ) : null}
          {template.whoShouldUse ? (
            <div>
              <dt>Who should use</dt>
              <dd>{template.whoShouldUse}</dd>
            </div>
          ) : null}
          {template.howToUse ? (
            <div>
              <dt>How to use</dt>
              <dd>{template.howToUse}</dd>
            </div>
          ) : null}
          {archetypes ? (
            <div>
              <dt>Archetypes</dt>
              <dd>{archetypes}</dd>
            </div>
          ) : null}
          {template.dnaWorkflowId ? (
            <div>
              <dt>DNA workflow</dt>
              <dd>
                <code>{template.dnaWorkflowId}</code>
              </dd>
            </div>
          ) : null}
        </dl>
      </details>
    </Panel>
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
  const [packId, setPackId] = useState(() => groups[0]?.packId ?? "video");
  const [templateId, setTemplateId] = useState(() => {
    const q = readTemplateQuery();
    return isVideoSpineTemplateId(q) ? VIDEO_SPINE_TEMPLATE_ID : q || "";
  });
  const [statusMessage, setStatusMessage] = useState<string | undefined>();

  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;

  const activeGroup: AgentWorkflowPackGroup | undefined = useMemo(() => {
    const base = groups.find((g) => g.packId === packId) ?? groups[0];
    return withProductSpineTemplate(base);
  }, [groups, packId]);

  const templates = useMemo(
    () => listTemplatesForGroup(activeGroup),
    [activeGroup],
  );

  // Keep template selection valid when pack changes; honor ?template= deep link once
  useEffect(() => {
    if (!activeGroup) return;
    const query = readTemplateQuery();
    if (query) {
      const fromQuery = activeGroup.templates.find(
        (t) =>
          t.id === query ||
          t.dnaWorkflowId === query ||
          isVideoSpineTemplateId(query),
      );
      if (fromQuery && templateId !== fromQuery.id) {
        setTemplateId(fromQuery.id);
        return;
      }
    }
    const exists = activeGroup.templates.some((t) => t.id === templateId);
    if (!exists) {
      setTemplateId(activeGroup.templates[0]?.id ?? "");
    }
  }, [activeGroup, templateId]);

  const activeTemplate = useMemo(
    () => findTemplate(activeGroup, templateId),
    [activeGroup, templateId],
  );

  const openSpineTemplate = (): void => {
    setPackId("video");
    setTemplateId(VIDEO_SPINE_TEMPLATE_ID);
    announce(
      `Opened Host product spine ${VIDEO_SPINE_WORKFLOW_ID} · ${STUB_RUN_HONESTY}.`,
    );
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("template", VIDEO_SPINE_TEMPLATE_ID);
      window.history.replaceState({}, "", url.toString());
    }
  };

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

  const hostSpineTemplates = templates.filter(
    (t) => t.id === VIDEO_SPINE_TEMPLATE_ID,
  );
  const scaleTemplates = templates.filter((t) => t.kind === "scale");
  const dnaTemplates = templates.filter(
    (t) => t.kind === "dna" && t.id !== VIDEO_SPINE_TEMPLATE_ID,
  );
  const spineSelected = isVideoSpineTemplateId(activeTemplate.id) ||
    activeTemplate.dnaWorkflowId === VIDEO_SPINE_WORKFLOW_ID;

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
          {spineSelected ? (
            <p className="agent-workflow-page__honesty" role="status">
              Host product spine <code>{VIDEO_SPINE_WORKFLOW_ID}</code> ·{" "}
              <strong>{STUB_RUN_HONESTY}</strong> · package step is always HITL
              · not production activation.
            </p>
          ) : null}
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
              {hostSpineTemplates.length > 0 ? (
                <optgroup label="Host product spine">
                  {hostSpineTemplates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label} ({t.agentIds.length} agents)
                    </option>
                  ))}
                </optgroup>
              ) : null}
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

          <button
            className="agent-workflow-page__spine-link"
            onClick={openSpineTemplate}
            type="button"
          >
            Open spine template
          </button>

          <div className="agent-workflow-page__stats" aria-live="polite">
            <span>{activeTemplate.agentIds.length} agents</span>
            <span>{activeTemplate.callEdges.length} call links</span>
            <span>{activeTemplate.phaseOrder.length} phases</span>
            {activeTemplate.scaleId ? (
              <span>Scale {activeTemplate.scaleId}</span>
            ) : activeTemplate.dnaWorkflowId ? (
              <span>
                DNA <code>{activeTemplate.dnaWorkflowId}</code>
              </span>
            ) : (
              <span>DNA</span>
            )}
          </div>
          {feedback ? <p role="status">{feedback}</p> : null}
        </div>
      </header>

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
          {spineSelected ? (
            <>
              {" "}
              · Host dry-run id <code>{VIDEO_SPINE_WORKFLOW_ID}</code> ·{" "}
              {STUB_RUN_HONESTY}
            </>
          ) : null}
        </p>
      </footer>
    </section>
  );
}
