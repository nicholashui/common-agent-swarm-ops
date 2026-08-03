import assert from "node:assert/strict";
import test from "node:test";

import { buildComposerWorkflowGraph } from "./composer-workflow";

test("buildComposerWorkflowGraph orders meta → craft → gate", () => {
  const graph = buildComposerWorkflowGraph(
    [
      { id: "1", label: "Orchestrator", agentId: "video.orchestrator" },
      { id: "2", label: "Planner", agentId: "video.planner" },
      { id: "3", label: "Director", agentId: "video.director" },
      { id: "4", label: "Judge", agentId: "video.judge", verified: true },
    ],
    "Hierarchical Supervisor",
  );
  assert.ok(graph.phaseCount >= 2);
  assert.equal(graph.agentCount >= 2, true);
  assert.equal(graph.gateCount >= 1, true);
  const agentNodes = graph.nodes.filter((n) => n.kind !== "phase");
  assert.equal(agentNodes[0]!.agentId, "video.orchestrator");
  assert.ok(agentNodes.some((n) => n.kind === "gate"));
  assert.ok(graph.edges.some((e) => e.style === "refine" || e.style === "gate"));
});

test("buildComposerWorkflowGraph empty shows await phase", () => {
  const graph = buildComposerWorkflowGraph([]);
  assert.equal(graph.agentCount, 0);
  assert.match(graph.nodes[0]!.title, /AWAITING|PHASE/i);
});
