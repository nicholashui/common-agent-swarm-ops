import assert from "node:assert/strict";
import test from "node:test";

import {
  STUB_RUN_HONESTY,
  VIDEO_SPINE_TEMPLATE_ID,
  VIDEO_SPINE_WORKFLOW_ID,
  agentWorkflowSpineHref,
  buildVideoSpineWorkflowTemplate,
  isVideoSpineTemplateId,
} from "./video-spine-template";

test("Host product spine template matches Host DNA id", () => {
  const t = buildVideoSpineWorkflowTemplate();
  assert.equal(t.id, VIDEO_SPINE_TEMPLATE_ID);
  assert.equal(t.dnaWorkflowId, VIDEO_SPINE_WORKFLOW_ID);
  assert.equal(t.dnaWorkflowId, "wf_video_spine_v1");
  assert.ok(t.steps.length >= 8);
  const packageStep = t.steps.find((s) => s.id === "package");
  assert.equal(packageStep?.humanGate, true);
  assert.ok(t.agentIds.includes("video.orchestrator"));
  assert.ok(t.agentIds.includes("video.producer"));
  assert.match(t.howToUse, /stub run/i);
  assert.match(STUB_RUN_HONESTY, /not production media/);
});

test("spine template deep link and id helpers", () => {
  assert.equal(isVideoSpineTemplateId(VIDEO_SPINE_TEMPLATE_ID), true);
  assert.equal(isVideoSpineTemplateId(VIDEO_SPINE_WORKFLOW_ID), true);
  assert.equal(isVideoSpineTemplateId("other"), false);
  assert.match(agentWorkflowSpineHref(), /agent-workflow/);
  assert.match(agentWorkflowSpineHref(), /wf_video_spine_v1/);
});
