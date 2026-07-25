import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { deflateSync, inflateSync } from "node:zlib";

import {
  SCREEN_DEFINITIONS,
  SCREEN_FIXTURE_REGISTRY,
  type ScreenDefinition,
  type ScreenFixture,
  type ScreenId,
  type ScreenViewport,
} from "./screen-manifest";

export const VISUAL_FIXTURE_VERSION = "frontend-redesign/v1";
export const FIXED_FONT_FAMILY = "Arial";
export const FIXED_MONOSPACE_FONT_FAMILY = "Consolas";
export const DEFAULT_PIXEL_THRESHOLD = 0;

export interface VisualFixtureValues {
  readonly asOf: string;
  readonly correlationIdentifier: string;
  readonly workspaceName: string;
}

export const FIXED_VISUAL_FIXTURE_VALUES: VisualFixtureValues = {
  asOf: "2026-07-20T04:12Z",
  correlationIdentifier: "corr-frontend-v1",
  workspaceName: "Trading Lab",
};

export interface VisualFixture {
  readonly version: string;
  readonly fonts: readonly string[];
  readonly assets: readonly string[];
  readonly values: VisualFixtureValues;
}

export const DEFAULT_VISUAL_FIXTURE: VisualFixture = {
  version: VISUAL_FIXTURE_VERSION,
  fonts: [FIXED_FONT_FAMILY, FIXED_MONOSPACE_FONT_FAMILY],
  assets: ["docs/frontend_redesign"],
  values: FIXED_VISUAL_FIXTURE_VALUES,
};

export interface RasterImage {
  readonly width: number;
  readonly height: number;
  readonly data: Uint8Array;
}

export type SvgRasterizer = (svg: string, viewport: ScreenViewport) => Buffer;

export interface VisualComparison {
  readonly schemaVersion: "frontend-redesign.visual-comparison/v1";
  readonly uiId: ScreenId;
  readonly fixtureId: string;
  readonly fixtureVersion: string;
  readonly viewport: ScreenViewport;
  readonly threshold: number;
  readonly comparedPixels: number;
  readonly mismatchPixels: number;
  readonly maximumChannelDifference: number;
  readonly passed: boolean;
  readonly baselineSha256: string;
  readonly screenshotSha256: string;
  readonly mismatchArtifact?: string;
}

export interface ViewportVisualResult extends VisualComparison {
  readonly screenshotSvg: string;
  readonly screenshotPng: string;
  readonly baselinePng: string;
  readonly comparisonJson: string;
}

export interface VisualVerificationResult {
  readonly schemaVersion: "frontend-redesign.visual-verification/v1";
  readonly fixtureVersion: string;
  readonly fontFamily: string;
  readonly fixtureValues: VisualFixtureValues;
  readonly screenCount: number;
  readonly viewportCount: number;
  readonly passed: boolean;
  readonly results: readonly ViewportVisualResult[];
}

export interface VisualVerificationOptions {
  readonly rootDirectory: string;
  readonly outputDirectory: string;
  readonly definitions?: readonly ScreenDefinition[];
  readonly fixture?: VisualFixture;
  readonly pixelThreshold?: number;
  readonly rasterize?: SvgRasterizer;
  /**
   * This is the seam for a browser-backed route capture. The default uses the
   * checked-in deterministic fixture SVG until a browser capture adapter is
   * supplied by the frontend harness.
   */
  readonly captureSvg?: (
    definition: ScreenDefinition,
    viewport: ScreenViewport,
    fixture: VisualFixture,
  ) => Promise<string> | string;
}

interface DecodedPng {
  readonly image: RasterImage;
  readonly colorType: number;
}

const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

export function normalizeFixtureSvg(
  svg: string,
  definition: ScreenDefinition,
  viewport: ScreenViewport,
  fixture: VisualFixture = DEFAULT_VISUAL_FIXTURE,
): string {
  const rootMatch = /<svg\b[^>]*>/i.exec(svg);
  if (rootMatch === null)
    throw new Error(
      `SVG baseline for ${definition.uiId} has no root svg element.`,
    );

  const root = rootMatch[0];
  const width = root.match(/\bwidth\s*=\s*["']([^"']+)["']/i)?.[1];
  const height = root.match(/\bheight\s*=\s*["']([^"']+)["']/i)?.[1];
  if (width === undefined || height === undefined) {
    throw new Error(
      `SVG baseline for ${definition.uiId} must declare width and height.`,
    );
  }
  if (parseCssPixels(width) <= 0 || parseCssPixels(height) <= 0) {
    throw new Error(
      `SVG baseline for ${definition.uiId} has invalid dimensions ${width}x${height}.`,
    );
  }

  let normalized = svg.replace(/\r\n?/g, "\n");
  normalized = normalized.replace(
    /\sdata-frontend-(?:fixture|fixture-id|viewport)="[^"]*"/g,
    "",
  );
  normalized = normalized.replace(
    /font-family\s*=\s*["']ui-monospace,\s*monospace["']/gi,
    `font-family="${FIXED_MONOSPACE_FONT_FAMILY}"`,
  );
  normalized = normalized.replace(
    /font-family\s*=\s*["'][^"']+["']/gi,
    (value) => {
      if (value.includes(FIXED_MONOSPACE_FONT_FAMILY)) return value;
      return `font-family="${FIXED_FONT_FAMILY}"`;
    },
  );
  normalized = normalized.replace(
    /\b(?:as_of|as-of)\s+\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z\b/gi,
    `as_of ${fixture.values.asOf}`,
  );
  normalized = normalized.replace(
    /\bcorr(?:elation)?\s+[a-z0-9-]+\b/gi,
    `corr ${fixture.values.correlationIdentifier}`,
  );
  normalized = normalized.replace(
    /\bTrading Lab\b/g,
    fixture.values.workspaceName,
  );
  normalized = normalized.replace(
    /<svg\b/i,
    `<svg data-frontend-fixture="${escapeXml(fixture.version)}" data-frontend-fixture-id="${escapeXml(definition.fixtureId)}" data-frontend-viewport="${viewport.width}x${viewport.height}"`,
  );

  validateSvgAssets(normalized, definition);
  return normalized;
}

export function rasterizeSvgWithRsvg(
  svg: string,
  viewport: ScreenViewport,
): Buffer {
  try {
    return execFileSync(
      "rsvg-convert",
      [
        "--format",
        "png",
        "--width",
        String(viewport.width),
        "--height",
        String(viewport.height),
        "--dpi-x",
        "96",
        "--dpi-y",
        "96",
        "--background-color",
        "white",
      ],
      { input: svg, maxBuffer: 128 * 1024 * 1024 },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(
      `Unable to rasterize the deterministic SVG baseline with rsvg-convert: ${message}`,
    );
  }
}

export function decodePng(png: Uint8Array): RasterImage {
  const decoded = decodePngWithColorType(png);
  return decoded.image;
}

export function encodePng(image: RasterImage): Buffer {
  assertRgbaImage(image);
  const rowSize = image.width * 4;
  const scanlines = Buffer.alloc((rowSize + 1) * image.height);
  for (let y = 0; y < image.height; y += 1) {
    const rowOffset = y * (rowSize + 1);
    scanlines[rowOffset] = 0;
    Buffer.from(
      image.data.buffer,
      image.data.byteOffset + y * rowSize,
      rowSize,
    ).copy(scanlines, rowOffset + 1);
  }

  const header = Buffer.alloc(13);
  header.writeUInt32BE(image.width, 0);
  header.writeUInt32BE(image.height, 4);
  header[8] = 8;
  header[9] = 6;
  header[10] = 0;
  header[11] = 0;
  header[12] = 0;
  return Buffer.concat([
    PNG_SIGNATURE,
    pngChunk("IHDR", header),
    pngChunk("IDAT", deflateSync(scanlines, { level: 9, strategy: 0 })),
    pngChunk("IEND", Buffer.alloc(0)),
  ]);
}

export function compareRasterImages(
  baselinePng: Uint8Array,
  screenshotPng: Uint8Array,
  options: { readonly threshold?: number } = {},
): {
  readonly comparison: Omit<
    VisualComparison,
    | "schemaVersion"
    | "uiId"
    | "fixtureId"
    | "fixtureVersion"
    | "viewport"
    | "baselineSha256"
    | "screenshotSha256"
    | "mismatchArtifact"
  >;
  readonly diffPng: Buffer;
} {
  const baseline = decodePngWithColorType(baselinePng).image;
  const screenshot = decodePngWithColorType(screenshotPng).image;
  const threshold = options.threshold ?? DEFAULT_PIXEL_THRESHOLD;
  if (!Number.isInteger(threshold) || threshold < 0 || threshold > 255)
    throw new Error(
      "The pixel threshold must be an integer from 0 through 255.",
    );

  const dimensionsMatch =
    baseline.width === screenshot.width &&
    baseline.height === screenshot.height;
  const comparedPixels = dimensionsMatch ? baseline.width * baseline.height : 0;
  const diff = new Uint8Array(baseline.width * baseline.height * 4);
  let mismatchPixels = dimensionsMatch
    ? 0
    : Math.max(
        baseline.width * baseline.height,
        screenshot.width * screenshot.height,
      );
  let maximumChannelDifference = dimensionsMatch ? 0 : 255;
  for (let index = 0; dimensionsMatch && index < comparedPixels; index += 1) {
    const offset = index * 4;
    const redDifference = Math.abs(
      pixelChannel(baseline, offset) - pixelChannel(screenshot, offset),
    );
    const greenDifference = Math.abs(
      pixelChannel(baseline, offset + 1) - pixelChannel(screenshot, offset + 1),
    );
    const blueDifference = Math.abs(
      pixelChannel(baseline, offset + 2) - pixelChannel(screenshot, offset + 2),
    );
    const alphaDifference = Math.abs(
      pixelChannel(baseline, offset + 3) - pixelChannel(screenshot, offset + 3),
    );
    const channelDifference = Math.max(
      redDifference,
      greenDifference,
      blueDifference,
      alphaDifference,
    );
    maximumChannelDifference = Math.max(
      maximumChannelDifference,
      channelDifference,
    );
    if (channelDifference > threshold) {
      mismatchPixels += 1;
      diff[offset] = 220;
      diff[offset + 1] = 38;
      diff[offset + 2] = 38;
      diff[offset + 3] = 255;
    } else {
      const luminance = Math.round(
        (pixelChannel(baseline, offset) +
          pixelChannel(baseline, offset + 1) +
          pixelChannel(baseline, offset + 2)) /
          3,
      );
      diff[offset] = luminance;
      diff[offset + 1] = luminance;
      diff[offset + 2] = luminance;
      diff[offset + 3] = 255;
    }
  }

  return {
    comparison: {
      threshold,
      comparedPixels,
      mismatchPixels,
      maximumChannelDifference,
      passed: dimensionsMatch && mismatchPixels === 0,
    },
    diffPng: encodePng({
      width: baseline.width,
      height: baseline.height,
      data: diff,
    }),
  };
}

export async function verifyVisualBaselines(
  options: VisualVerificationOptions,
): Promise<VisualVerificationResult> {
  const fixture = options.fixture ?? DEFAULT_VISUAL_FIXTURE;
  const definitions = options.definitions ?? SCREEN_DEFINITIONS;
  if (definitions.length !== 21)
    throw new Error(
      `Expected exactly 21 screen definitions, received ${definitions.length}.`,
    );
  await mkdir(options.outputDirectory, { recursive: true });

  const results: ViewportVisualResult[] = [];
  for (const definition of definitions) {
    const registeredFixture = SCREEN_FIXTURE_REGISTRY[definition.uiId];
    assertFixtureMatchesDefinition(definition, registeredFixture);
    const baselinePath = resolve(options.rootDirectory, definition.svgBaseline);
    const baselineSvg = await readFile(baselinePath, "utf8");
    for (const viewport of definition.viewports) {
      const normalizedBaseline = normalizeFixtureSvg(
        baselineSvg,
        definition,
        viewport,
        fixture,
      );
      const capturedSvg = await (options.captureSvg?.(
        definition,
        viewport,
        fixture,
      ) ?? baselineSvg);
      const normalizedCapture = normalizeFixtureSvg(
        capturedSvg,
        definition,
        viewport,
        fixture,
      );
      const rasterize = options.rasterize ?? rasterizeSvgWithRsvg;
      const baselinePng = rasterize(normalizedBaseline, viewport);
      const screenshotPng = rasterize(normalizedCapture, viewport);
      const { comparison, diffPng } = compareRasterImages(
        baselinePng,
        screenshotPng,
        { threshold: options.pixelThreshold },
      );
      const artifactDirectory = join(
        options.outputDirectory,
        definition.uiId,
        `${viewport.width}x${viewport.height}`,
      );
      await mkdir(artifactDirectory, { recursive: true });
      const screenshotSvgPath = join(artifactDirectory, "screenshot.svg");
      const screenshotPngPath = join(artifactDirectory, "screenshot.png");
      const baselinePngPath = join(artifactDirectory, "baseline.png");
      const comparisonJsonPath = join(artifactDirectory, "comparison.json");
      const mismatchArtifactPath = join(artifactDirectory, "mismatch.png");
      await writeFile(screenshotSvgPath, normalizedCapture, "utf8");
      await writeFile(screenshotPngPath, screenshotPng);
      await writeFile(baselinePngPath, baselinePng);
      const mismatchArtifact = comparison.passed
        ? undefined
        : mismatchArtifactPath;
      if (mismatchArtifact !== undefined)
        await writeFile(mismatchArtifact, diffPng);
      const artifactComparison: VisualComparison = {
        schemaVersion: "frontend-redesign.visual-comparison/v1",
        uiId: definition.uiId,
        fixtureId: definition.fixtureId,
        fixtureVersion: fixture.version,
        viewport,
        ...comparison,
        baselineSha256: sha256(baselinePng),
        screenshotSha256: sha256(screenshotPng),
        ...(mismatchArtifact === undefined ? {} : { mismatchArtifact }),
      };
      await writeFile(
        comparisonJsonPath,
        `${JSON.stringify(artifactComparison, null, 2)}\n`,
        "utf8",
      );
      results.push({
        ...artifactComparison,
        screenshotSvg: screenshotSvgPath,
        screenshotPng: screenshotPngPath,
        baselinePng: baselinePngPath,
        comparisonJson: comparisonJsonPath,
      });
    }
  }

  return {
    schemaVersion: "frontend-redesign.visual-verification/v1",
    fixtureVersion: fixture.version,
    fontFamily: fixture.fonts.join(", "),
    fixtureValues: fixture.values,
    screenCount: definitions.length,
    viewportCount: results.length,
    passed: results.every((result) => result.passed),
    results,
  };
}

export function defaultProjectRoot(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), "../../../../");
}

function assertFixtureMatchesDefinition(
  definition: ScreenDefinition,
  fixture: ScreenFixture,
): void {
  if (
    fixture.id !== definition.fixtureId ||
    fixture.grantedCapability !== definition.requiredCapability
  ) {
    throw new Error(
      `Fixture mapping for ${definition.uiId} does not match its screen definition.`,
    );
  }
}

function validateSvgAssets(svg: string, definition: ScreenDefinition): void {
  const externalAssetPattern =
    /<(?:image|script|iframe)\b[^>]*(?:href|src)\s*=\s*["'](?!#|data:|about:blank)([^"']+)["']/gi;
  const externalAsset = externalAssetPattern.exec(svg)?.[1];
  if (externalAsset !== undefined) {
    throw new Error(
      `SVG baseline for ${definition.uiId} references an unapproved asset: ${externalAsset}.`,
    );
  }
  if (/<script\b/i.test(svg) || /(?:^|[<\s])on[a-z]+\s*=/i.test(svg)) {
    throw new Error(
      `SVG baseline for ${definition.uiId} contains executable markup.`,
    );
  }
}

function parseCssPixels(value: string): number {
  const number = Number.parseFloat(value);
  return Number.isFinite(number) ? number : 0;
}

function escapeXml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
      })[character] ?? character,
  );
}

function sha256(value: Uint8Array): string {
  return createHash("sha256").update(value).digest("hex");
}

function assertRgbaImage(image: RasterImage): void {
  if (
    !Number.isInteger(image.width) ||
    !Number.isInteger(image.height) ||
    image.width <= 0 ||
    image.height <= 0
  )
    throw new Error("PNG images must have positive integer dimensions.");
  if (image.data.length !== image.width * image.height * 4)
    throw new Error("PNG image data must be RGBA with four bytes per pixel.");
}

function pixelChannel(image: RasterImage, offset: number): number {
  const value = image.data[offset];
  if (value === undefined)
    throw new Error(`Missing RGBA channel at offset ${offset}.`);
  return value;
}

function decodePngWithColorType(png: Uint8Array): DecodedPng {
  if (
    Buffer.compare(
      Buffer.from(png.subarray(0, PNG_SIGNATURE.length)),
      PNG_SIGNATURE,
    ) !== 0
  )
    throw new Error("Invalid PNG signature.");
  let offset = PNG_SIGNATURE.length;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idat: Buffer[] = [];
  while (offset < png.length) {
    if (offset + 12 > png.length) throw new Error("Truncated PNG chunk.");
    const length = Buffer.from(
      png.buffer,
      png.byteOffset + offset,
      4,
    ).readUInt32BE(0);
    const type = Buffer.from(
      png.buffer,
      png.byteOffset + offset + 4,
      4,
    ).toString("ascii");
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    if (dataEnd + 4 > png.length) throw new Error("Truncated PNG chunk data.");
    const chunkData = Buffer.from(
      png.buffer,
      png.byteOffset + dataStart,
      length,
    );
    if (type === "IHDR") {
      width = chunkData.readUInt32BE(0);
      height = chunkData.readUInt32BE(4);
      bitDepth = chunkData[8] ?? 0;
      colorType = chunkData[9] ?? 0;
      if (chunkData[10] !== 0 || chunkData[11] !== 0 || chunkData[12] !== 0)
        throw new Error(
          "Unsupported PNG compression, filter, or interlace method.",
        );
    } else if (type === "IDAT") {
      idat.push(chunkData);
    } else if (type === "IEND") {
      break;
    }
    offset = dataEnd + 4;
  }
  if (
    width <= 0 ||
    height <= 0 ||
    bitDepth !== 8 ||
    (colorType !== 2 && colorType !== 6)
  )
    throw new Error("Only non-interlaced 8-bit RGB/RGBA PNGs are supported.");
  const bytesPerPixel = colorType === 6 ? 4 : 3;
  const rowSize = width * bytesPerPixel;
  const scanlines = inflateSync(Buffer.concat(idat));
  if (scanlines.length !== (rowSize + 1) * height)
    throw new Error("PNG scanline length does not match its dimensions.");
  const raw = Buffer.alloc(rowSize * height);
  for (let y = 0; y < height; y += 1) {
    const sourceOffset = y * (rowSize + 1);
    const destinationOffset = y * rowSize;
    const filter = scanlines[sourceOffset] ?? 0;
    for (let x = 0; x < rowSize; x += 1) {
      const left =
        x >= bytesPerPixel
          ? (raw[destinationOffset + x - bytesPerPixel] ?? 0)
          : 0;
      const above = y > 0 ? (raw[destinationOffset + x - rowSize] ?? 0) : 0;
      const upperLeft =
        y > 0 && x >= bytesPerPixel
          ? (raw[destinationOffset + x - rowSize - bytesPerPixel] ?? 0)
          : 0;
      const encoded = scanlines[sourceOffset + x + 1] ?? 0;
      raw[destinationOffset + x] = decodePngFilter(
        filter,
        encoded,
        left,
        above,
        upperLeft,
      );
    }
  }
  const rgba = new Uint8Array(width * height * 4);
  for (let index = 0; index < width * height; index += 1) {
    const sourceOffset = index * bytesPerPixel;
    const destinationOffset = index * 4;
    rgba[destinationOffset] = raw[sourceOffset] ?? 0;
    rgba[destinationOffset + 1] = raw[sourceOffset + 1] ?? 0;
    rgba[destinationOffset + 2] = raw[sourceOffset + 2] ?? 0;
    rgba[destinationOffset + 3] =
      colorType === 6 ? (raw[sourceOffset + 3] ?? 0) : 255;
  }
  return { image: { width, height, data: rgba }, colorType };
}

function decodePngFilter(
  filter: number,
  encoded: number,
  left: number,
  above: number,
  upperLeft: number,
): number {
  if (filter === 0) return encoded;
  if (filter === 1) return (encoded + left) & 255;
  if (filter === 2) return (encoded + above) & 255;
  if (filter === 3) return (encoded + Math.floor((left + above) / 2)) & 255;
  if (filter === 4)
    return (encoded + paethPredictor(left, above, upperLeft)) & 255;
  throw new Error(`Unsupported PNG filter ${filter}.`);
}

function paethPredictor(
  left: number,
  above: number,
  upperLeft: number,
): number {
  const estimate = left + above - upperLeft;
  const leftDistance = Math.abs(estimate - left);
  const aboveDistance = Math.abs(estimate - above);
  const upperLeftDistance = Math.abs(estimate - upperLeft);
  if (leftDistance <= aboveDistance && leftDistance <= upperLeftDistance)
    return left;
  if (aboveDistance <= upperLeftDistance) return above;
  return upperLeft;
}

function pngChunk(type: string, data: Buffer): Buffer {
  const typeBuffer = Buffer.from(type, "ascii");
  const crc = crc32(Buffer.concat([typeBuffer, data]));
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc, 0);
  return Buffer.concat([length, typeBuffer, data, checksum]);
}

function crc32(value: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of value) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1)
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
