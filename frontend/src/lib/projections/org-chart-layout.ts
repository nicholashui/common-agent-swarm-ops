/**
 * Pure layout helpers for Registry Org Chart (non-special pack hierarchies).
 * Hierarchy: top management → VA category departments → member agents.
 */

import type {
  OrgChartEdge,
  OrgChartPackGroup,
  OrgChartPayload,
} from "./org-chart.generated";
import { ORG_CHART_PAYLOAD } from "./org-chart.generated";

export interface OrgChartFlowNodeData extends Record<string, unknown> {
  readonly kind: "top" | "department" | "agent";
  readonly title: string;
  readonly subtitle: string;
  readonly href?: string;
  readonly categoryId?: string;
  readonly memberCount?: number;
  readonly isTopManagement?: boolean;
  readonly status?: string;
}

export interface OrgChartFlowNode {
  readonly id: string;
  readonly type: "orgNode";
  readonly position: { readonly x: number; readonly y: number };
  readonly data: OrgChartFlowNodeData;
  readonly draggable: false;
  readonly connectable: false;
}

export interface OrgChartFlowEdge {
  readonly id: string;
  readonly source: string;
  readonly target: string;
  readonly type: "smoothstep";
  readonly animated: boolean;
  readonly className: string;
  readonly data: { readonly kind: string };
}

export interface OrgChartLayoutResult {
  readonly nodes: readonly OrgChartFlowNode[];
  readonly edges: readonly OrgChartFlowEdge[];
  readonly group: OrgChartPackGroup;
}

const NODE_W = 200;
const NODE_H = 72;
const H_GAP = 28;
const V_GAP = 110;
const DEPT_GAP = 48;
const DEPTS_PER_ROW = 4;
const DEPT_ROW_GAP = 72;
const AGENT_COL_W = NODE_W + H_GAP;

export function listOrgChartGroups(
  payload: OrgChartPayload = ORG_CHART_PAYLOAD,
): readonly OrgChartPackGroup[] {
  return payload.groups;
}

export function getOrgChartGroup(
  packId: string,
  payload: OrgChartPayload = ORG_CHART_PAYLOAD,
): OrgChartPackGroup | undefined {
  return payload.groups.find((g) => g.packId === packId);
}

/**
 * Build React Flow nodes/edges for one pack group.
 * When showCritique is true, dashed critique edges overlay hierarchy.
 */
export function buildOrgChartLayout(
  group: OrgChartPackGroup,
  options?: { readonly showCritique?: boolean },
): OrgChartLayoutResult {
  const showCritique = options?.showCritique ?? false;
  const agentById = new Map(group.agents.map((a) => [a.id, a]));
  const nodes: OrgChartFlowNode[] = [];
  const edges: OrgChartFlowEdge[] = [];

  // Orchestration pipeline (common-agent-structure.svg, vertical):
  //   Planner → Orchestrator → departments → agents
  const pipelineTopIds =
    group.topManagementIds.length > 0
      ? [...group.topManagementIds]
      : [group.primaryTopId];
  // Prefer explicit planner → orchestrator order for layout when both exist
  const orderedPipeline = (() => {
    const planner = pipelineTopIds.find(
      (id) => id.endsWith(".planner") || id.split(".").pop() === "planner",
    );
    const orchestrator = pipelineTopIds.find(
      (id) =>
        id.endsWith(".orchestrator") || id.split(".").pop() === "orchestrator",
    );
    const rest = pipelineTopIds.filter(
      (id) => id !== planner && id !== orchestrator,
    );
    const ordered: string[] = [];
    if (planner) ordered.push(planner);
    if (orchestrator) ordered.push(orchestrator);
    ordered.push(...rest);
    return ordered.length > 0 ? ordered : [group.primaryTopId];
  })();
  const executionTopId =
    orderedPipeline.find(
      (id) =>
        id.endsWith(".orchestrator") || id.split(".").pop() === "orchestrator",
    ) ?? orderedPipeline[orderedPipeline.length - 1]!;

  // Department columns — measure widths first for centering
  const deptLayouts = group.departments.map((dept) => {
    const members = dept.memberIds.filter((id) => !group.topManagementIds.includes(id));
    const cols = Math.max(1, Math.min(4, Math.ceil(Math.sqrt(Math.max(members.length, 1)))));
    const rows = Math.max(1, Math.ceil(members.length / cols));
    const width = Math.max(NODE_W, cols * AGENT_COL_W - H_GAP);
    return { dept, members, cols, rows, width };
  });

  // Departments wrap into rows (max DEPTS_PER_ROW per row) so the chart is
  // roughly square instead of one very wide strip.
  const deptRows: (typeof deptLayouts)[] = [];
  for (let i = 0; i < deptLayouts.length; i += DEPTS_PER_ROW) {
    deptRows.push(deptLayouts.slice(i, i + DEPTS_PER_ROW));
  }
  const rowWidthOf = (row: typeof deptLayouts): number =>
    row.reduce((sum, d) => sum + d.width, 0) +
    Math.max(0, row.length - 1) * DEPT_GAP;
  const totalWidth = Math.max(NODE_W, ...deptRows.map(rowWidthOf));
  const originX = 40;
  const topY = 24;
  const centerX = originX + totalWidth / 2;

  // Pipeline tops stacked vertically (Planner above Orchestrator)
  orderedPipeline.forEach((id, index) => {
    const agent = agentById.get(id);
    const leaf = id.split(".").pop()?.toLowerCase() ?? "";
    const subtitle =
      leaf === "planner"
        ? "Scope & task graph"
        : leaf === "orchestrator"
          ? "State, retries, fan-out"
          : "Pack entry";
    nodes.push({
      id,
      type: "orgNode",
      position: {
        x: centerX - NODE_W / 2,
        y: topY + index * (NODE_H + V_GAP * 0.65),
      },
      data: {
        kind: "top",
        title: agent?.name ?? id,
        subtitle,
        href: agent?.href,
        isTopManagement: true,
        status: agent?.status,
        categoryId: agent?.categoryId,
      },
      draggable: false,
      connectable: false,
    });
    if (index > 0) {
      const prev = orderedPipeline[index - 1]!;
      edges.push({
        id: `pipeline-${prev}-${id}`,
        source: prev,
        target: id,
        type: "smoothstep",
        animated: false,
        className: "org-chart-edge org-chart-edge--management",
        data: { kind: "management" },
      });
    }
  });

  const deptY =
    topY +
    orderedPipeline.length * (NODE_H + V_GAP * 0.65) +
    V_GAP * 0.35;

  const deptBlockHeight = (layout: { rows: number }): number =>
    NODE_H + V_GAP * 0.75 + layout.rows * (NODE_H + 20);

  let rowTopY = deptY;
  for (const deptRow of deptRows) {
    const rowWidth = rowWidthOf(deptRow);
    let cursorX = originX + (totalWidth - rowWidth) / 2;
    let rowHeight = 0;
    for (const layout of deptRow) {
      const { dept, members, cols, width } = layout;
      const deptX = cursorX + width / 2 - NODE_W / 2;

      nodes.push({
        id: dept.id,
        type: "orgNode",
        position: { x: deptX, y: rowTopY },
        data: {
          kind: "department",
          title: dept.label,
          subtitle: `${dept.categoryId} · ${members.length + dept.memberIds.filter((id) => group.topManagementIds.includes(id)).length} agents`,
          categoryId: dept.categoryId,
          memberCount: dept.memberIds.length,
        },
        draggable: false,
        connectable: false,
      });

      // Only Orchestrator (execution top) fans out to departments
      edges.push({
        id: `dept-${executionTopId}-${dept.id}`,
        source: executionTopId,
        target: dept.id,
        type: "smoothstep",
        animated: false,
        className: "org-chart-edge org-chart-edge--department",
        data: { kind: "department" },
      });

      const agentStartY = rowTopY + NODE_H + V_GAP * 0.75;
      members.forEach((memberId, index) => {
        const agent = agentById.get(memberId);
        const col = index % cols;
        const gridRow = Math.floor(index / cols);
        const blockLeft = cursorX + (width - cols * AGENT_COL_W + H_GAP) / 2;
        const x = blockLeft + col * AGENT_COL_W;
        const y = agentStartY + gridRow * (NODE_H + 20);

        nodes.push({
          id: memberId,
          type: "orgNode",
          position: { x, y },
          data: {
            kind: "agent",
            title: agent?.name ?? memberId,
            subtitle: agent?.role ?? memberId,
            href: agent?.href,
            categoryId: agent?.categoryId,
            status: agent?.status,
            isTopManagement: false,
          },
          draggable: false,
          connectable: false,
        });

        edges.push({
          id: `member-${dept.id}-${memberId}`,
          source: dept.id,
          target: memberId,
          type: "smoothstep",
          animated: false,
          className: "org-chart-edge org-chart-edge--member",
          data: { kind: "member" },
        });
      });

      cursorX += width + DEPT_GAP;
      rowHeight = Math.max(rowHeight, deptBlockHeight(layout));
    }
    rowTopY += rowHeight + DEPT_ROW_GAP;
  }

  if (showCritique) {
    const nodeIds = new Set(nodes.map((n) => n.id));
    for (const link of group.critiqueEdges) {
      if (!nodeIds.has(link.fromId) || !nodeIds.has(link.toId)) continue;
      // Skip if identical hierarchy edge already exists
      const edgeId = `critique-${link.kind}-${link.fromId}-${link.toId}`;
      edges.push({
        id: edgeId,
        source: link.fromId,
        target: link.toId,
        type: "smoothstep",
        animated: true,
        className: "org-chart-edge org-chart-edge--critique",
        data: { kind: link.kind },
      });
    }
  }

  return { nodes, edges, group };
}

/** Count hierarchy edges by kind (for tests / stats). */
export function countEdgesByKind(
  edges: readonly OrgChartEdge[],
): Readonly<Record<string, number>> {
  const counts: Record<string, number> = {};
  for (const edge of edges) {
    counts[edge.kind] = (counts[edge.kind] ?? 0) + 1;
  }
  return counts;
}
