import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ScreenBoundary } from "../../components/ScreenBoundary";
import { ProjectionMapper } from "../projections/ProjectionMapper";
import {
  SCREEN_DEFINITIONS,
  SCREEN_FIXTURE_REGISTRY,
  SCREEN_IDS,
  getScreenDefinition,
  getScreenFixture,
} from "./screen-manifest";

test("maps every approved UI ID to one fixed fixture, baseline, capability, route module, and viewport list", () => {
  assert.equal(SCREEN_IDS.length, 21);
  assert.equal(SCREEN_DEFINITIONS.length, 21);

  for (const screenId of SCREEN_IDS) {
    const definition = getScreenDefinition(screenId);
    const fixture = getScreenFixture(screenId);

    assert.equal(definition.uiId, screenId);
    assert.equal(fixture, SCREEN_FIXTURE_REGISTRY[screenId]);
    assert.equal(fixture.id, definition.fixtureId);
    assert.equal(fixture.grantedCapability, definition.requiredCapability);
    assert.equal(fixture.version, "1.0.0");
    assert.equal(definition.behaviorBaseline, `docs/frontend_redesign/${screenId}.md`);
    assert.equal(definition.svgBaseline, `docs/frontend_redesign/${screenId}.svg`);
    assert.match(definition.module, /^src\/(app|components)\//);
    assert.ok(definition.viewports.length > 0);
    assert.ok(definition.viewports.every(({ width, height }) => width > 0 && height > 0));
  }

  assert.deepEqual(getScreenDefinition("ui_17_mobile").viewports, [{ width: 390, height: 844 }]);
});

test("renders approved screen content only when the required generated capability is returned", () => {
  const definition = getScreenDefinition("ui_08_settings");
  const markup = renderToStaticMarkup(
    <ScreenBoundary
      capabilities={[{ key: definition.requiredCapability }]}
      definition={definition}
      shell={<header>Authorized shell context</header>}
    >
      <div>Authorized settings projection</div>
    </ScreenBoundary>,
  );

  assert.match(markup, /Authorized shell context/);
  assert.match(markup, /Authorized settings projection/);
  assert.doesNotMatch(markup, /Screen unavailable/);
});

test("preserves the authorized shell but suppresses protected screen content when capability is unavailable", () => {
  const definition = getScreenDefinition("ui_15_api_portal");
  const recoveryAction = new ProjectionMapper().mapActionReference({
    id: "action-retry-1",
    label: "Retry developer projection",
    eligible: true,
  });
  if (recoveryAction === null) throw new Error("Expected a returned recovery action reference.");

  const markup = renderToStaticMarkup(
    <ScreenBoundary
      capabilities={[]}
      definition={definition}
      shell={<header>Authorized shell context</header>}
      unavailableState={{
        error: { code: "capability_unavailable", message: "The developer projection is unavailable." },
        recoveryAction,
      }}
    >
      <div>Protected API token and portal data</div>
    </ScreenBoundary>,
  );

  assert.match(markup, /Authorized shell context/);
  assert.match(markup, /The developer projection is unavailable\./);
  assert.match(markup, /Retry developer projection/);
  assert.match(markup, /data-action-reference-id="action-retry-1"/);
  assert.doesNotMatch(markup, /Protected API token and portal data/);
});
