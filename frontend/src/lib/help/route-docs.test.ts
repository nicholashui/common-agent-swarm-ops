import assert from "node:assert/strict";
import test from "node:test";

import {
  buildFullPageDocsHref,
  normalizeRoutePath,
  resolveHelpMarkdownCandidates,
  stripDynamicRouteSegments,
} from "./route-docs";

test("normalizeRoutePath trims trailing slashes", () => {
  assert.equal(normalizeRoutePath("/registry/"), "/registry");
  assert.equal(normalizeRoutePath("registry"), "/registry");
  assert.equal(normalizeRoutePath("/"), "/");
});

test("stripDynamicRouteSegments drops ids and keeps static segments", () => {
  assert.equal(
    stripDynamicRouteSegments("/registry/agents/video.orchestrator"),
    "/registry/agents",
  );
  assert.equal(stripDynamicRouteSegments("/registry"), "/registry");
  assert.equal(
    stripDynamicRouteSegments("/swarms/swarm-abc/canvas"),
    "/swarms/canvas",
  );
  assert.equal(
    stripDynamicRouteSegments("/developer/api"),
    "/developer/api",
  );
});

test("resolveHelpMarkdownCandidates prefers exact then stripped", () => {
  const paths = resolveHelpMarkdownCandidates(
    "/registry/agents/video.x",
    "userguide",
  );
  assert.equal(paths[0], "/docs/registry/agents/video.x/userguide.md");
  assert.ok(paths.includes("/docs/registry/agents/userguide.md"));
  assert.ok(paths.includes("/docs/userguide.md"));
});

test("buildFullPageDocsHref encodes primary candidate", () => {
  const href = buildFullPageDocsHref("/registry", "spec");
  assert.match(href, /^\/docs\/view\?path=/);
  assert.match(href, /registry%2Fspec\.md|registry\/spec\.md/);
});
