import assert from "node:assert/strict";
import test from "node:test";

import { ORG_CHART_PAYLOAD } from "./org-chart.generated";
import {
  buildOrgChartLayout,
  countEdgesByKind,
  getOrgChartGroup,
  listOrgChartGroups,
} from "./org-chart-layout";

test("org chart payload excludes specials and includes video pack", () => {
  const groups = listOrgChartGroups();
  assert.ok(groups.length >= 1);
  assert.equal(
    groups.some((g) => g.packId === "specials"),
    false,
  );
  const video = getOrgChartGroup("video");
  assert.ok(video);
  assert.equal(video.folderPath, "business/video");
  assert.equal(video.agentCount, 114);
  assert.equal(video.primaryTopId, "video.orchestrator");
  assert.ok(video.topManagementIds.includes("video.orchestrator"));
});

test("video hierarchy is Planner → Orchestrator → departments → agents", () => {
  const video = getOrgChartGroup("video")!;
  const layout = buildOrgChartLayout(video);
  const orchestrator = layout.nodes.find((n) => n.id === "video.orchestrator");
  const planner = layout.nodes.find((n) => n.id === "video.planner");
  assert.ok(orchestrator);
  assert.ok(planner);
  assert.equal(orchestrator.data.kind, "top");
  assert.equal(planner.data.kind, "top");
  // Planner above Orchestrator (pipeline order)
  assert.ok(planner.position.y < orchestrator.position.y);
  assert.ok(
    layout.edges.some(
      (e) =>
        e.source === "video.planner" &&
        e.target === "video.orchestrator" &&
        e.data.kind === "management",
    ),
  );
  assert.ok(
    video.hierarchyEdges.some(
      (e) =>
        e.fromId === "video.planner" &&
        e.toId === "video.orchestrator" &&
        e.kind === "management",
    ),
  );
  // Departments hang under Orchestrator only
  assert.ok(
    layout.edges
      .filter((e) => e.data.kind === "department")
      .every((e) => e.source === "video.orchestrator"),
  );

  const depts = layout.nodes.filter((n) => n.data.kind === "department");
  assert.ok(depts.length >= 8);
  assert.ok(depts.every((d) => d.position.y > orchestrator.position.y));

  const agents = layout.nodes.filter((n) => n.data.kind === "agent");
  assert.ok(agents.length >= 100);
  const minDeptY = Math.min(...depts.map((d) => d.position.y));
  assert.ok(agents.every((a) => a.position.y > minDeptY));

  const kinds = countEdgesByKind([...video.hierarchyEdges]);
  assert.ok((kinds.department ?? 0) >= 8);
  assert.ok((kinds.member ?? 0) >= 100);
  assert.ok((kinds.management ?? 0) >= 1);
});

test("critique overlay adds animated critique edges only when enabled", () => {
  const video = getOrgChartGroup("video")!;
  const base = buildOrgChartLayout(video, { showCritique: false });
  const withCritique = buildOrgChartLayout(video, { showCritique: true });
  assert.ok(withCritique.edges.length > base.edges.length);
  assert.ok(
    withCritique.edges.some((e) => e.className.includes("critique")),
  );
  assert.equal(
    base.edges.some((e) => e.className.includes("critique")),
    false,
  );
});

test("payload schema version is stable", () => {
  assert.equal(ORG_CHART_PAYLOAD.schemaVersion, "1.0");
  assert.match(ORG_CHART_PAYLOAD.source, /non-special/i);
});
