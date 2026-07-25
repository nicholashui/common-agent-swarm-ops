import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

import {
  DEFAULT_VISUAL_FIXTURE,
  defaultProjectRoot,
  normalizeFixtureSvg,
} from "./visual-verification";
import {
  SCREEN_DEFINITIONS,
  SCREEN_IDS,
  type ScreenDefinition,
} from "./screen-manifest";
import { verifyScreenInventory } from "./screen-inventory";

interface BaselineSemanticContract {
  readonly semanticRegions: readonly string[];
  readonly controlOrder: readonly string[];
}

function sectionBody(markdown: string, headingPattern: RegExp): string {
  const headings = [...markdown.matchAll(/^##\s+([^\n]+)$/gm)];
  const heading = headings.find((match) => headingPattern.test(match[1] ?? ""));
  if (heading === undefined || heading.index === undefined) return "";
  const nextHeading = headings.find(
    (candidate) => (candidate.index ?? 0) > (heading.index ?? 0),
  );
  return markdown.slice(heading.index, nextHeading?.index ?? markdown.length);
}

function unique(values: readonly string[]): readonly string[] {
  return [...new Set(values.map((value) => value.trim()).filter((value) => value.length > 0))];
}

function extractBaselineContract(markdown: string): BaselineSemanticContract {
  const layout = sectionBody(markdown, /layout|information architecture|menu behavior/i);
  const componentAndInteractionSections = [
    sectionBody(markdown, /components|key components/i),
    sectionBody(markdown, /interactions|flows|behavior and states/i),
    sectionBody(markdown, /wireframe summary/i),
  ].join("\n");

  const semanticRegions = unique([
    ...[...markdown.matchAll(/^##\s+([^\n]+)$/gm)]
      .map((match) => match[1] ?? "")
      .filter((heading) => /layout|component|interaction|wireframe|accessibility|polish|behavior|information|responsive/i.test(heading)),
    ...[...layout.matchAll(/^\s*(?:[-*]|\d+\.)\s+\*\*([^*]+)\*\*/gm)].map(
      (match) => match[1] ?? "",
    ),
  ]);

  const quotedControls = [
    ...componentAndInteractionSections.matchAll(/["“]([^"”\n]{3,100})["”]/g),
  ].map((match) => match[1] ?? "");
  const labelledControls = [
    ...componentAndInteractionSections.matchAll(/^\s*(?:[-*]|\d+\.)\s+\*\*([^*]+)\*\*/gm),
  ].map((match) => match[1] ?? "");
  const orderedControls = [
    ...componentAndInteractionSections.matchAll(/^\s*\d+\.\s+([^\n]+)$/gm),
  ].map((match) => match[1] ?? "");
  const bulletControls = [
    ...componentAndInteractionSections.matchAll(/^\s*-\s+([^\n]+)$/gm),
  ].map((match) => match[1] ?? "");
  const controlOrder = [...unique([
    ...quotedControls,
    ...labelledControls,
    ...orderedControls,
    ...bulletControls,
  ])].sort((left, right) => markdown.indexOf(left) - markdown.indexOf(right));

  return { semanticRegions, controlOrder };
}

function extractSvgSemanticMarkers(svg: string): readonly string[] {
  return unique(
    [...svg.matchAll(/<!--\s*(?:=+\s*)?([^=\n-][^\n]*?)\s*(?:=+\s*)?-->/g)].map(
      (match) => match[1] ?? "",
    ),
  );
}

function normalizedMarkerPositions(
  svg: string,
  markers: readonly string[],
): readonly number[] {
  let previousPosition = -1;
  return markers.map((marker) => {
    const position = svg.indexOf(marker, previousPosition + 1);
    assert.notEqual(position, -1, `Missing semantic baseline marker: ${marker}`);
    previousPosition = position;
    return position;
  });
}

function manifestBaselinePath(definition: ScreenDefinition): string {
  return resolve(defaultProjectRoot(), definition.behaviorBaseline);
}

function manifestSvgPath(definition: ScreenDefinition): string {
  return resolve(defaultProjectRoot(), definition.svgBaseline);
}

test("checks every Markdown baseline for ordered semantic regions and controls at every manifest viewport", async (): Promise<void> => {
  for (const definition of SCREEN_DEFINITIONS) {
    const [markdown, svg] = await Promise.all([
      readFile(manifestBaselinePath(definition), "utf8"),
      readFile(manifestSvgPath(definition), "utf8"),
    ]);
    const contract = extractBaselineContract(markdown);

    assert.ok(
      contract.semanticRegions.length >= 2,
      `${definition.uiId} must declare at least two semantic regions in its Markdown baseline`,
    );
    assert.ok(
      contract.controlOrder.length >= 2,
      `${definition.uiId} must declare an ordered control contract in its Markdown baseline`,
    );

    const controlPositions = contract.controlOrder.map((control) => markdown.indexOf(control));
    assert.ok(
      controlPositions.every((position) => position >= 0),
      `${definition.uiId} control contract must be sourced from its Markdown baseline`,
    );
    assert.deepEqual(
      [...controlPositions].sort((left, right) => left - right),
      controlPositions,
      `${definition.uiId} control contract order must match its Markdown baseline`,
    );

    const markers = extractSvgSemanticMarkers(svg);
    assert.ok(markers.length > 0, `${definition.uiId} SVG baseline must expose semantic region markers`);
    const sourcePositions = normalizedMarkerPositions(svg, markers);

    for (const viewport of definition.viewports) {
      const normalized = normalizeFixtureSvg(
        svg,
        definition,
        viewport,
        DEFAULT_VISUAL_FIXTURE,
      );
      assert.match(
        normalized,
        new RegExp(`data-frontend-viewport="${viewport.width}x${viewport.height}"`),
      );
      assert.match(
        normalized,
        new RegExp(`data-frontend-fixture-id="${definition.fixtureId}"`),
      );

      const viewportPositions = normalizedMarkerPositions(normalized, markers);
      assert.ok(
        viewportPositions.every(
          (position, index) => index === 0 || position > viewportPositions[index - 1]!,
        ),
        `${definition.uiId} ${viewport.width}x${viewport.height} changed semantic region/control order`,
      );
      assert.ok(
        sourcePositions.every(
          (position, index) => index === 0 || position > sourcePositions[index - 1]!,
        ),
        `${definition.uiId} baseline semantic markers are not ordered`,
      );
    }
  }
});

test("manifest inventory has exactly one complete baseline and viewport contract per approved screen", async (): Promise<void> => {
  assert.equal(SCREEN_DEFINITIONS.length, 21);
  assert.equal(new Set(SCREEN_DEFINITIONS.map(({ uiId }) => uiId)).size, 21);

  for (const definition of SCREEN_DEFINITIONS) {
    assert.match(definition.behaviorBaseline, new RegExp(`^docs/frontend_redesign/${definition.uiId}\\.md$`));
    assert.match(definition.svgBaseline, new RegExp(`^docs/frontend_redesign/${definition.uiId}\\.svg$`));
    assert.ok(definition.module.startsWith("src/"));
    assert.ok(definition.viewports.length > 0);
    assert.equal(new Set(definition.viewports.map(({ width, height }) => `${width}x${height}`)).size, definition.viewports.length);
    for (const viewport of definition.viewports) {
      assert.ok(Number.isInteger(viewport.width) && viewport.width > 0);
      assert.ok(Number.isInteger(viewport.height) && viewport.height > 0);
    }
  }
});

test("fails closed when the manifest count or approved screen mapping is incomplete", async (): Promise<void> => {
  const incompleteDefinitions = SCREEN_DEFINITIONS.slice(0, -1);
  const incomplete = await verifyScreenInventory({
    rootDirectory: defaultProjectRoot(),
    visualOutputDirectory: "frontend/.artifacts/missing-manifest-test",
    definitions: incompleteDefinitions,
  });
  assert.equal(incomplete.passed, false);
  assert.match(incomplete.errors.join("\n"), /Expected exactly 21 screen definitions/);
  assert.match(incomplete.errors.join("\n"), /Missing approved screen definition: ui_20_blueprints/);

  const duplicateDefinitions: readonly ScreenDefinition[] = [
    ...incompleteDefinitions,
    SCREEN_DEFINITIONS[0]!,
  ];
  const duplicate = await verifyScreenInventory({
    rootDirectory: defaultProjectRoot(),
    visualOutputDirectory: "frontend/.artifacts/duplicate-manifest-test",
    definitions: duplicateDefinitions,
  });
  assert.equal(duplicate.passed, false);
  assert.match(duplicate.errors.join("\n"), /Duplicate screen definition: ui_00_menu/);
  assert.match(duplicate.errors.join("\n"), /Missing approved screen definition: ui_20_blueprints/);
});
