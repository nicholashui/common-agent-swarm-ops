/**
 * Build a simple workflow graph view from AI-picked agent slots (ACC Compose).
 * Visual language aligned with Agent Workflow (phase / agent / gate).
 */

export type ComposerWorkflowNodeKind = "phase" | "agent" | "gate";

export type ComposerWorkflowNode = {
  readonly id: string;
  readonly kind: ComposerWorkflowNodeKind;
  readonly title: string;
  readonly subtitle: string;
  readonly agentId?: string;
};

export type ComposerWorkflowEdge = {
  readonly id: string;
  readonly from: string;
  readonly to: string;
  readonly style: "handoff" | "gate" | "refine";
};

export type ComposerWorkflowGraph = {
  readonly nodes: readonly ComposerWorkflowNode[];
  readonly edges: readonly ComposerWorkflowEdge[];
  readonly phaseCount: number;
  readonly agentCount: number;
  readonly gateCount: number;
};

type SlotLike = {
  readonly id: string;
  readonly label: string;
  readonly agentId?: string;
  readonly verified?: boolean;
};

function isMeta(agentId: string, label: string): boolean {
  const h = `${agentId} ${label}`.toLowerCase();
  return h.includes("orchestrat") || h.includes("planner");
}

function isGate(agentId: string, label: string, verified?: boolean): boolean {
  if (verified) return true;
  const h = `${agentId} ${label}`.toLowerCase();
  return (
    h.includes("judge") ||
    h.includes("gate") ||
    h.includes("verifier") ||
    h.includes("qa") ||
    h.includes("compliance")
  );
}

/**
 * Build workflow graph from canvas / swarm node labels (Agent Workflow style).
 */
export function buildWorkflowGraphFromCanvasNodes(
  nodes: readonly {
    readonly id: string;
    readonly label: string;
    readonly kind?: string;
    readonly versionLabel?: string;
  }[],
  patternName?: string,
): ComposerWorkflowGraph {
  return buildComposerWorkflowGraph(
    nodes.map((n) => {
      const hay = `${n.id} ${n.label} ${n.kind ?? ""}`.toLowerCase();
      return {
        id: n.id,
        label: n.label,
        agentId: n.label.includes(".") ? n.label : n.id,
        verified:
          n.kind === "verifier" ||
          hay.includes("verif") ||
          hay.includes("judge") ||
          hay.includes("gate") ||
          hay.includes("supervisor"),
      };
    }),
    patternName,
  );
}

/**
 * Layout: control meta → craft agents → gate (if any), with sequential handoffs.
 */
export function buildComposerWorkflowGraph(
  slots: readonly SlotLike[],
  patternName?: string,
): ComposerWorkflowGraph {
  if (slots.length === 0) {
    return {
      nodes: [
        {
          id: "phase-empty",
          kind: "phase",
          title: "PHASE · AWAITING AI",
          subtitle: patternName ?? "Run AI plan on a goal/spec",
        },
      ],
      edges: [],
      phaseCount: 1,
      agentCount: 0,
      gateCount: 0,
    };
  }

  const meta = slots.filter((s) =>
    isMeta(s.agentId ?? "", s.label),
  );
  const gates = slots.filter(
    (s) =>
      !isMeta(s.agentId ?? "", s.label) &&
      isGate(s.agentId ?? "", s.label, s.verified),
  );
  const craft = slots.filter(
    (s) =>
      !isMeta(s.agentId ?? "", s.label) &&
      !isGate(s.agentId ?? "", s.label, s.verified),
  );

  const nodes: ComposerWorkflowNode[] = [];
  const edges: ComposerWorkflowEdge[] = [];

  nodes.push({
    id: "phase-control",
    kind: "phase",
    title: "PHASE · CONTROL",
    subtitle: patternName ?? "Hierarchical control",
  });
  nodes.push({
    id: "phase-craft",
    kind: "phase",
    title: "PHASE · CRAFT PIPELINE",
    subtitle: `${craft.length || slots.length} craft roles`,
  });
  if (gates.length > 0) {
    nodes.push({
      id: "phase-verify",
      kind: "phase",
      title: "PHASE · VERIFY",
      subtitle: "Critic / gate",
    });
  }

  const ordered = [...meta, ...craft, ...gates];
  const agentNodes: ComposerWorkflowNode[] = ordered.map((s, index) => {
    const agentId = s.agentId ?? s.id;
    const gate = isGate(agentId, s.label, s.verified);
    return {
      id: `n-${index}-${agentId.replace(/\./g, "_")}`,
      kind: gate ? "gate" : "agent",
      title: s.label.replace(/\s*\([^)]*\)\s*$/, "") || agentId,
      subtitle: agentId,
      agentId,
    };
  });
  nodes.push(...agentNodes);

  for (let i = 0; i < agentNodes.length - 1; i += 1) {
    const from = agentNodes[i]!;
    const to = agentNodes[i + 1]!;
    const style: ComposerWorkflowEdge["style"] =
      to.kind === "gate" ? "gate" : "handoff";
    edges.push({
      id: `e-${from.id}-${to.id}`,
      from: from.id,
      to: to.id,
      style,
    });
  }

  const lastGate = [...agentNodes].reverse().find((n) => n.kind === "gate");
  const lastCraft = [...agentNodes]
    .reverse()
    .find((n) => n.kind === "agent" && !isMeta(n.agentId ?? "", n.title));
  if (lastGate && lastCraft) {
    edges.push({
      id: `e-refine-${lastGate.id}-${lastCraft.id}`,
      from: lastGate.id,
      to: lastCraft.id,
      style: "refine",
    });
  }

  return {
    nodes,
    edges,
    phaseCount: nodes.filter((n) => n.kind === "phase").length,
    agentCount: nodes.filter((n) => n.kind === "agent").length,
    gateCount: nodes.filter((n) => n.kind === "gate").length,
  };
}
