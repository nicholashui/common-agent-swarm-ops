import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
  DEFAULT_VISUAL_FIXTURE,
  defaultProjectRoot,
  encodePng,
  normalizeFixtureSvg,
  compareRasterImages,
  verifyVisualBaselines,
  type RasterImage,
} from "./visual-verification";
import { getScreenDefinition } from "./screen-manifest";

function solidImage(red: number, green: number, blue: number): Buffer {
  const image: RasterImage = { width: 2, height: 2, data: new Uint8Array([red, green, blue, 255, red, green, blue, 255, red, green, blue, 255, red, green, blue, 255]) };
  return encodePng(image);
}

test("normalizes baselines to fixed fonts, fixture values, and capture metadata", () => {
  const definition = getScreenDefinition("ui_02_dashboard");
  const normalized = normalizeFixtureSvg(
    '<svg width="1440" height="1480" font-family="Inter, system-ui, sans-serif"><text>as_of 2026-01-01T00:00Z corr old-value Video Studio</text></svg>',
    definition,
    { width: 390, height: 844 },
  );

  assert.match(normalized, /font-family="Arial"/);
  assert.match(normalized, /as_of 2026-07-20T04:12Z/);
  assert.match(normalized, /corr corr-frontend-v1/);
  assert.match(normalized, /data-frontend-fixture-id="fixture\.ui_02_dashboard"/);
  assert.match(normalized, /data-frontend-viewport="390x844"/);
});

test("reports exact raster equality and emits a useful mismatch diff", () => {
  const baseline = solidImage(255, 255, 255);
  const same = compareRasterImages(baseline, baseline);
  assert.equal(same.comparison.passed, true);
  assert.equal(same.comparison.mismatchPixels, 0);

  const different = compareRasterImages(baseline, solidImage(255, 0, 0));
  assert.equal(different.comparison.passed, false);
  assert.equal(different.comparison.mismatchPixels, 4);
  assert.ok(different.comparison.maximumChannelDifference > 0);
  assert.notDeepEqual(different.diffPng, baseline);
});

test("captures every manifest viewport and writes per-viewport comparison artifacts", async () => {
  const outputDirectory = await mkdtemp(join(tmpdir(), "frontend-visual-verification-"));
  try {
    const result = await verifyVisualBaselines({
      rootDirectory: defaultProjectRoot(),
      outputDirectory,
      rasterize: () => solidImage(1, 2, 3),
    });

    assert.equal(result.screenCount, 21);
    assert.equal(result.viewportCount, result.results.length);
    assert.equal(result.passed, true);
    assert.ok(result.results.every((item) => item.passed));
    const comparison = JSON.parse(await readFile(result.results[0]?.comparisonJson ?? "", "utf8")) as { readonly fixtureVersion: string };
    assert.equal(comparison.fixtureVersion, DEFAULT_VISUAL_FIXTURE.version);
  } finally {
    await rm(outputDirectory, { recursive: true, force: true });
  }
});

test("writes a mismatch artifact when a captured viewport differs from its SVG baseline", async () => {
  const outputDirectory = await mkdtemp(join(tmpdir(), "frontend-visual-mismatch-"));
  try {
    const result = await verifyVisualBaselines({
      rootDirectory: defaultProjectRoot(),
      outputDirectory,
      captureSvg: () => '<svg width="1" height="1"><rect width="1" height="1" fill="#ff0000" /></svg>',
      rasterize: (svg) => solidImage(svg.includes("#ff0000") ? 255 : 0, 0, 0),
    });

    assert.equal(result.passed, false);
    const mismatches = result.results.filter((item) => !item.passed);
    assert.equal(mismatches.length, result.results.length);
    assert.ok(mismatches.every((item) => item.mismatchArtifact !== undefined));
    assert.ok(mismatches.every((item) => item.mismatchArtifact !== undefined && item.mismatchArtifact.endsWith("mismatch.png")));
  } finally {
    await rm(outputDirectory, { recursive: true, force: true });
  }
});
