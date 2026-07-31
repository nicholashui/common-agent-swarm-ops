import assert from "node:assert/strict";
import test from "node:test";

import { AGENT_WORKFLOW_PAYLOAD } from "./agent-workflow.generated";
import {
  buildWorkflowLayout,
  findTemplate,
  listTemplatesForGroup,
  listWorkflowGroups,
} from "./agent-workflow-layout";

test("workflow payload has video pack with scale and DNA templates", () => {
  const groups = listWorkflowGroups(AGENT_WORKFLOW_PAYLOAD);
  assert.ok(groups.length >= 1);
  const video = groups.find((g) => g.packId === "video");
  assert.ok(video);
  assert.equal(video!.folderPath, "business/video");
  const templates = listTemplatesForGroup(video);
  assert.ok(templates.length >= 10);
  const scales = templates.filter((t) => t.kind === "scale");
  const dnas = templates.filter((t) => t.kind === "dna");
  assert.equal(scales.length, 7);
  assert.ok(dnas.length >= 10);
  assert.ok(scales.some((t) => t.scaleId === "S1"));
  assert.ok(scales.some((t) => t.scaleId === "S7"));
});

test("workflow layout builds nodes and call edges for S1", () => {
  const video = listWorkflowGroups(AGENT_WORKFLOW_PAYLOAD).find(
    (g) => g.packId === "video",
  )!;
  const s1 = findTemplate(
    video,
    video.templates.find((t) => t.scaleId === "S1")!.id,
  )!;
  assert.ok(s1.agentIds.length >= 10);
  assert.ok(s1.callEdges.length >= 5);
  const layout = buildWorkflowLayout(s1);
  const agentNodes = layout.nodes.filter(
    (n) => (n.data as { kind?: string }).kind === "agent",
  );
  assert.ok(agentNodes.length >= 10);
  assert.ok(layout.edges.length >= 1);
  // edges only connect agents present in the template
  const ids = new Set(layout.nodes.map((n) => n.id));
  for (const e of layout.edges) {
    assert.ok(ids.has(e.source));
    assert.ok(ids.has(e.target));
  }
});

test("DNA viral hook template has sequential agent handoffs", () => {
  const video = listWorkflowGroups(AGENT_WORKFLOW_PAYLOAD).find(
    (g) => g.packId === "video",
  )!;
  const dna = video.templates.find((t) =>
    (t.dnaWorkflowId ?? "").includes("viral_hook"),
  );
  assert.ok(dna);
  assert.ok(dna!.callEdges.length >= 1);
  const layout = buildWorkflowLayout(dna!);
  assert.ok(layout.nodes.some((n) => n.id === "video.orchestrator"));
  assert.ok(layout.edges.length >= 1);
});
