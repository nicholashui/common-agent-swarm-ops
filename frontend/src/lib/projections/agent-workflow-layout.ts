/**
 * Pure layout for Agent Workflow call flowcharts (React Flow).
 * Nodes = agents in the selected template; edges = handoff/phase/gate calls.
 */
import type { Edge, Node } from "@xyflow/react";

import type {
  AgentWorkflowEdge,
  AgentWorkflowPackGroup,
  AgentWorkflowPayload,
  AgentWorkflowTemplate,
} from "./agent-workflow.generated";

export type WorkflowFlowNodeKind = "agent" | "phase";

export interface WorkflowFlowNodeData extends Record<string, unknown> {
  readonly kind: WorkflowFlowNodeKind;
  readonly title: string;
  readonly subtitle: string;
  readonly href?: string;
  readonly phase?: string;
  readonly humanGate?: boolean;
}

const NODE_W = 168;
const NODE_H = 72;
const COL_GAP = 56;
const ROW_GAP = 36;
const PHASE_GAP_Y = 110;

export function listWorkflowGroups(
  payload: AgentWorkflowPayload,
): readonly AgentWorkflowPackGroup[] {
  return payload.groups;
}

export function listTemplatesForGroup(
  group: AgentWorkflowPackGroup | undefined,
): readonly AgentWorkflowTemplate[] {
  return group?.templates ?? [];
}

export function findTemplate(
  group: AgentWorkflowPackGroup | undefined,
  templateId: string,
): AgentWorkflowTemplate | undefined {
  if (!group) return undefined;
  return group.templates.find((t) => t.id === templateId) ?? group.templates[0];
}

function agentPhaseMap(template: AgentWorkflowTemplate): Map<string, string> {
  const map = new Map<string, string>();
  for (const step of template.steps) {
    if (!map.has(step.agentId)) {
      map.set(step.agentId, step.phase);
    }
  }
  return map;
}

function agentsByPhase(template: AgentWorkflowTemplate): Map<string, string[]> {
  const phaseMap = agentPhaseMap(template);
  const byPhase = new Map<string, string[]>();
  const order = template.phaseOrder.length
    ? template.phaseOrder
    : [...new Set(template.steps.map((s) => s.phase))];

  for (const phase of order) {
    byPhase.set(phase, []);
  }
  for (const agent of template.agents) {
    const phase = phaseMap.get(agent.id) ?? "workflow";
    if (!byPhase.has(phase)) byPhase.set(phase, []);
    const list = byPhase.get(phase)!;
    if (!list.includes(agent.id)) list.push(agent.id);
  }
  // orphan agents not in steps
  for (const agent of template.agents) {
    let found = false;
    for (const list of byPhase.values()) {
      if (list.includes(agent.id)) {
        found = true;
        break;
      }
    }
    if (!found) {
      if (!byPhase.has("workflow")) byPhase.set("workflow", []);
      byPhase.get("workflow")!.push(agent.id);
    }
  }
  return byPhase;
}

export function buildWorkflowLayout(template: AgentWorkflowTemplate): {
  readonly nodes: Node<WorkflowFlowNodeData>[];
  readonly edges: Edge[];
} {
  const byPhase = agentsByPhase(template);
  const agentById = new Map(template.agents.map((a) => [a.id, a]));
  const nodes: Node<WorkflowFlowNodeData>[] = [];
  const phaseKeys = [...byPhase.keys()].filter((k) => (byPhase.get(k) ?? []).length > 0);

  let y = 0;
  for (const phase of phaseKeys) {
    const memberIds = byPhase.get(phase) ?? [];
    // phase band label node (optional lightweight header)
    nodes.push({
      id: `phase:${phase}`,
      type: "workflowNode",
      position: { x: 0, y },
      data: {
        kind: "phase",
        title: phase.replace(/_/g, " "),
        subtitle: `${memberIds.length} agents`,
        phase,
      },
      draggable: false,
      selectable: false,
      style: { width: NODE_W },
    });

    memberIds.forEach((agentId, index) => {
      const agent = agentById.get(agentId);
      const col = index % 5;
      const row = Math.floor(index / 5);
      nodes.push({
        id: agentId,
        type: "workflowNode",
        position: {
          x: (col + 1) * (NODE_W + COL_GAP),
          y: y + row * (NODE_H + ROW_GAP),
        },
        data: {
          kind: "agent",
          title: agent?.name ?? agentId,
          subtitle: agentId,
          href: agent?.href ?? `/registry/agents/${agentId}`,
          phase,
          humanGate: template.steps.some(
            (s) => s.agentId === agentId && s.humanGate,
          ),
        },
        draggable: false,
        style: { width: NODE_W },
      });
    });

    const rows = Math.max(1, Math.ceil(memberIds.length / 5));
    y += Math.max(PHASE_GAP_Y, rows * (NODE_H + ROW_GAP) + 48);
  }

  const edges: Edge[] = template.callEdges.map((edge: AgentWorkflowEdge, i) => {
    const stroke =
      edge.kind === "gate"
        ? "#c2410c"
        : edge.kind === "phase"
          ? "#1d4ed8"
          : "#0f766e";
    return {
      id: `e-${i}-${edge.fromId}-${edge.toId}`,
      source: edge.fromId,
      target: edge.toId,
      type: "smoothstep",
      animated: edge.kind === "gate",
      label: edge.label,
      className: `agent-workflow-edge agent-workflow-edge--${edge.kind}`,
      style: { stroke, strokeWidth: edge.kind === "phase" ? 2 : 1.5 },
      labelStyle: { fontSize: 9, fill: "#57534e" },
      labelBgStyle: { fill: "#fafaf9", fillOpacity: 0.9 },
    };
  });

  // Drop edges whose endpoints are not in the graph
  const nodeIds = new Set(nodes.map((n) => n.id));
  const filtered = edges.filter(
    (e) => nodeIds.has(e.source) && nodeIds.has(e.target),
  );

  return { nodes, edges: filtered };
}
