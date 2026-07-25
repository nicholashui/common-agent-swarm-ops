import assert from "node:assert/strict";
import { rm } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

import {
  defaultProjectRoot,
  encodePng,
  verifyVisualBaselines,
  type RasterImage,
} from "./visual-verification";
import { verifyScreenInventory } from "./screen-inventory";
import {
  SCREEN_DEFINITIONS,
  type ScreenDefinition,
} from "./screen-manifest";

function solidImage(red: number, green: number, blue: number): Buffer {
  const image: RasterImage = {
    width: 2,
    height: 2,
    data: new Uint8Array([
      red,
      green,
      blue,
      255,
      red,
      green,
      blue,
      255,
      red,
      green,
      blue,
      255,
      red,
      green,
      blue,
      255,
    ]),
  };
  return encodePng(image);
}

async function withVisualArtifacts(
  callback: (outputDirectory: string) => Promise<void>,
): Promise<void> {
  const outputDirectory = join(
    defaultProjectRoot(),
    "frontend",
    ".artifacts",
    "screen-inventory-test",
  );
  await rm(outputDirectory, { force: true, recursive: true });
  try {
    await verifyVisualBaselines({
      rootDirectory: defaultProjectRoot(),
      outputDirectory,
      rasterize: () => solidImage(1, 2, 3),
    });
    await callback(outputDirectory);
  } finally {
    await rm(outputDirectory, { force: true, recursive: true });
  }
}

test("produces exactly 21 complete records with evidence for every manifest viewport", async () => {
  await withVisualArtifacts(async (outputDirectory) => {
    const completeDefinitions: readonly ScreenDefinition[] = SCREEN_DEFINITIONS.map(
      (definition) =>
        definition.uiId === "ui_10_knowledge"
          ? {
              ...definition,
              module: "src/components/KnowledgeArtifactScreens.tsx",
            }
          : definition,
    );
    const inventory = await verifyScreenInventory({
      rootDirectory: defaultProjectRoot(),
      visualOutputDirectory: outputDirectory,
      definitions: completeDefinitions,
    });

    assert.equal(inventory.passed, true);
    assert.equal(inventory.screenCount, 21);
    assert.equal(inventory.results.length, 21);
    assert.equal(
      inventory.viewportCount,
      inventory.results.reduce((count, result) => count + result.viewports.length, 0),
    );
    assert.ok(inventory.results.every((result) => result.complete));
    assert.ok(
      inventory.results.every((result) =>
        result.viewports.every(
          (evidence) =>
            evidence.screenshotPresent &&
            evidence.visualComparisonArtifactPresent,
        ),
      ),
    );
  });
});

test("fails closed when a specified viewport screenshot is missing", async () => {
  await withVisualArtifacts(async (outputDirectory) => {
    const missingScreenshot = join(
      outputDirectory,
      "ui_00_menu",
      "1440x1000",
      "screenshot.png",
    );
    await rm(missingScreenshot);

    const inventory = await verifyScreenInventory({
      rootDirectory: defaultProjectRoot(),
      visualOutputDirectory: outputDirectory,
    });

    assert.equal(inventory.passed, false);
    const menu = inventory.results.find((result) => result.uiId === "ui_00_menu");
    assert.ok(menu);
    assert.equal(menu.complete, false);
    assert.equal(menu.viewports[0]?.screenshotPresent, false);
    assert.match(inventory.errors.join("\n"), /missing deterministic fixture screenshot/);
  });
});

test("fails closed when a visual comparison artifact reports a mismatch", async () => {
  const outputDirectory = join(
    defaultProjectRoot(),
    "frontend",
    ".artifacts",
    "screen-inventory-mismatch-test",
  );
  await rm(outputDirectory, { force: true, recursive: true });
  try {
    await verifyVisualBaselines({
      rootDirectory: defaultProjectRoot(),
      outputDirectory,
      captureSvg: () =>
        '<svg width="1" height="1"><rect width="1" height="1" fill="#ff0000" /></svg>',
      rasterize: (svg) =>
        solidImage(svg.includes("#ff0000") ? 255 : 0, 0, 0),
    });

    const inventory = await verifyScreenInventory({
      rootDirectory: defaultProjectRoot(),
      visualOutputDirectory: outputDirectory,
    });

    assert.equal(inventory.passed, false);
    assert.match(inventory.errors.join("\n"), /visual comparison failed/);
  } finally {
    await rm(outputDirectory, { force: true, recursive: true });
  }
});
