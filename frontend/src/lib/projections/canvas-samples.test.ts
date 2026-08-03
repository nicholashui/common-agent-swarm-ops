import assert from "node:assert/strict";
import test from "node:test";

import { LOCAL_CANVAS_LANDING } from "./canvas-landing";
import { applyCanvasSample, CANVAS_SAMPLES } from "./canvas-samples";

test("canvas samples cover multiple crews with nodes", () => {
  assert.ok(CANVAS_SAMPLES.length >= 4);
  assert.ok(CANVAS_SAMPLES.every((s) => s.nodes.length >= 3));
  assert.ok(CANVAS_SAMPLES.some((s) => s.id === "canvas-wuxia"));
});

test("applyCanvasSample overlays crew onto base view", () => {
  const sample = CANVAS_SAMPLES.find((s) => s.id === "canvas-wuxia");
  assert.ok(sample);
  const next = applyCanvasSample(LOCAL_CANVAS_LANDING, sample!);
  assert.equal(next.swarmName, sample!.swarmName);
  assert.equal(next.nodes.length, sample!.nodes.length);
  assert.equal(next.instanceId, "sample-canvas-wuxia");
  assert.equal(next.groups.length, 0);
  assert.ok(next.edges.length >= 1);
  assert.match(next.footerNote, /Sample/i);
  assert.equal(next.labels, LOCAL_CANVAS_LANDING.labels);
  assert.equal(next.palette, LOCAL_CANVAS_LANDING.palette);
});
