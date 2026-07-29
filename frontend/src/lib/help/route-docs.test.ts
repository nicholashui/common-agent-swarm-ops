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

test("resolveHelpMarkdownCandidates prefers pack user_guide for agent detail", () => {
  const paths = resolveHelpMarkdownCandidates(
    "/registry/agents/specials.aesthetics-agent",
    "userguide",
  );
  assert.equal(paths[0], "/docs/agents/specials.aesthetics-agent/user_guide.md");
  assert.ok(paths.includes("/docs/agents/specials.aesthetics-agent/userguide.md"));
  assert.ok(paths.includes("/docs/registry/agents/specials.aesthetics-agent/userguide.md"));
  assert.ok(paths.includes("/docs/registry/agents/userguide.md"));
  assert.ok(paths.includes("/docs/userguide.md"));
});

test("resolveHelpMarkdownCandidates prefers exact then stripped for non-agent routes", () => {
  const paths = resolveHelpMarkdownCandidates("/registry", "userguide");
  assert.equal(paths[0], "/docs/registry/userguide.md");
  assert.ok(paths.includes("/docs/userguide.md"));
});

test("buildFullPageDocsHref encodes primary candidate", () => {
  const href = buildFullPageDocsHref("/registry", "spec");
  assert.match(href, /^\/docs\/view\?path=/);
  assert.match(href, /registry%2Fspec\.md|registry\/spec\.md/);
});
