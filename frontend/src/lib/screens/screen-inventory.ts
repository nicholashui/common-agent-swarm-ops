import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { basename, relative, resolve, sep } from "node:path";

import {
  SCREEN_DEFINITIONS,
  SCREEN_FIXTURE_REGISTRY,
  SCREEN_IDS,
  type ScreenDefinition,
  type ScreenId,
  type ScreenViewport,
} from "./screen-manifest";
import {
  DEFAULT_VISUAL_FIXTURE,
  type VisualFixture,
} from "./visual-verification";

export const SCREEN_INVENTORY_SCHEMA_VERSION =
  "frontend-redesign.screen-inventory/v1";

export interface ScreenViewportEvidence {
  readonly viewport: ScreenViewport;
  readonly screenshot: string;
  readonly visualComparisonArtifact: string;
  readonly screenshotPresent: boolean;
  readonly visualComparisonArtifactPresent: boolean;
}

export interface ScreenInventoryRecord {
  readonly uiId: ScreenId;
  readonly requiredCapability: ScreenDefinition["requiredCapability"];
  readonly behaviorBaseline: string;
  readonly svgBaseline: string;
  readonly routeOrShell: string;
  readonly module: string;
  readonly fixtureId: string;
  readonly fixtureVersion: string;
  readonly visualFixtureVersion: string;
  readonly viewports: readonly ScreenViewportEvidence[];
  readonly complete: boolean;
  readonly errors: readonly string[];
}

export interface ScreenInventoryVerificationResult {
  readonly schemaVersion: typeof SCREEN_INVENTORY_SCHEMA_VERSION;
  readonly screenCount: number;
  readonly viewportCount: number;
  readonly passed: boolean;
  readonly results: readonly ScreenInventoryRecord[];
  readonly errors: readonly string[];
}

export interface ScreenInventoryOptions {
  readonly rootDirectory: string;
  readonly visualOutputDirectory: string;
  readonly definitions?: readonly ScreenDefinition[];
  readonly fixture?: VisualFixture;
}

interface ComparisonArtifact {
  readonly schemaVersion: string;
  readonly uiId: string;
  readonly fixtureId: string;
  readonly fixtureVersion: string;
  readonly viewport: ScreenViewport;
  readonly screenshotSha256: string;
  readonly passed: boolean;
}

const PNG_SIGNATURE = Buffer.from([
  137, 80, 78, 71, 13, 10, 26, 10,
]);

export async function verifyScreenInventory(
  options: ScreenInventoryOptions,
): Promise<ScreenInventoryVerificationResult> {
  const rootDirectory = resolve(options.rootDirectory);
  const frontendRoot = resolveFrontendRoot(rootDirectory);
  const visualOutputDirectory = resolve(
    rootDirectory,
    options.visualOutputDirectory,
  );
  const fixture = options.fixture ?? DEFAULT_VISUAL_FIXTURE;
  const definitions = options.definitions ?? SCREEN_DEFINITIONS;
  const errors: string[] = [];
  const seenScreenIds = new Set<string>();

  if (definitions.length !== SCREEN_IDS.length) {
    errors.push(
      `Expected exactly ${SCREEN_IDS.length} screen definitions, received ${definitions.length}.`,
    );
  }

  const results: ScreenInventoryRecord[] = [];
  for (const definition of definitions) {
    const recordErrors: string[] = [];
    if (seenScreenIds.has(definition.uiId)) {
      recordErrors.push(`Duplicate screen definition: ${definition.uiId}.`);
    }
    seenScreenIds.add(definition.uiId);
    if (!SCREEN_IDS.includes(definition.uiId)) {
      recordErrors.push(`Unknown approved screen ID: ${definition.uiId}.`);
    }

    const registeredFixture = SCREEN_FIXTURE_REGISTRY[definition.uiId];
    if (
      registeredFixture.id !== definition.fixtureId ||
      registeredFixture.grantedCapability !== definition.requiredCapability
    ) {
      recordErrors.push(
        `Fixture mapping for ${definition.uiId} does not match its capability mapping.`,
      );
    }

    await requireFile(
      rootDirectory,
      definition.behaviorBaseline,
      `${definition.uiId} behavior baseline`,
      recordErrors,
    );
    await requireFile(
      rootDirectory,
      definition.svgBaseline,
      `${definition.uiId} SVG baseline`,
      recordErrors,
    );
    await requireFile(
      frontendRoot,
      definition.module,
      `${definition.uiId} route or shell module`,
      recordErrors,
    );

    const viewports = uniqueValidViewports(definition, recordErrors);
    const viewportEvidence: ScreenViewportEvidence[] = [];
    for (const viewport of viewports) {
      const artifactDirectory = resolve(
        visualOutputDirectory,
        definition.uiId,
        `${viewport.width}x${viewport.height}`,
      );
      const screenshotPath = resolve(artifactDirectory, "screenshot.png");
      const comparisonPath = resolve(artifactDirectory, "comparison.json");
      const screenshot = artifactPath(rootDirectory, screenshotPath);
      const visualComparisonArtifact = artifactPath(
        rootDirectory,
        comparisonPath,
      );
      const screenshotPresent = await isFile(screenshotPath);
      const visualComparisonArtifactPresent = await isFile(comparisonPath);
      const evidenceErrors: string[] = [];

      if (!screenshotPresent) {
        evidenceErrors.push(
          `${definition.uiId} ${formatViewport(viewport)} is missing deterministic fixture screenshot: ${screenshot}.`,
        );
      }
      if (!visualComparisonArtifactPresent) {
        evidenceErrors.push(
          `${definition.uiId} ${formatViewport(viewport)} is missing visual-comparison artifact: ${visualComparisonArtifact}.`,
        );
      }

      if (screenshotPresent && visualComparisonArtifactPresent) {
        const comparisonErrors = await validateComparisonArtifact({
          comparisonPath,
          screenshotPath,
          definition,
          viewport,
          fixtureVersion: fixture.version,
        });
        evidenceErrors.push(...comparisonErrors);
      }

      viewportEvidence.push({
        viewport,
        screenshot,
        visualComparisonArtifact,
        screenshotPresent,
        visualComparisonArtifactPresent,
      });
      recordErrors.push(...evidenceErrors);
    }

    const complete = recordErrors.length === 0;
    results.push({
      uiId: definition.uiId,
      requiredCapability: definition.requiredCapability,
      behaviorBaseline: projectPath(
        rootDirectory,
        resolve(rootDirectory, definition.behaviorBaseline),
      ),
      svgBaseline: projectPath(
        rootDirectory,
        resolve(rootDirectory, definition.svgBaseline),
      ),
      routeOrShell: definition.routeOrShell,
      module: definition.module,
      fixtureId: definition.fixtureId,
      fixtureVersion: registeredFixture.version,
      visualFixtureVersion: fixture.version,
      viewports: viewportEvidence,
      complete,
      errors: recordErrors,
    });
    errors.push(...recordErrors);
  }

  for (const screenId of SCREEN_IDS) {
    if (!seenScreenIds.has(screenId)) {
      errors.push(`Missing approved screen definition: ${screenId}.`);
    }
  }

  return {
    schemaVersion: SCREEN_INVENTORY_SCHEMA_VERSION,
    screenCount: definitions.length,
    viewportCount: results.reduce(
      (count, result) => count + result.viewports.length,
      0,
    ),
    passed: errors.length === 0 && results.length === SCREEN_IDS.length,
    results,
    errors,
  };
}

async function validateComparisonArtifact({
  comparisonPath,
  screenshotPath,
  definition,
  viewport,
  fixtureVersion,
}: {
  readonly comparisonPath: string;
  readonly screenshotPath: string;
  readonly definition: ScreenDefinition;
  readonly viewport: ScreenViewport;
  readonly fixtureVersion: string;
}): Promise<readonly string[]> {
  const errors: string[] = [];
  let comparison: ComparisonArtifact;
  try {
    const parsed: unknown = JSON.parse(await readFile(comparisonPath, "utf8"));
    if (!isComparisonArtifact(parsed)) {
      errors.push(
        `${definition.uiId} ${formatViewport(viewport)} has an invalid visual-comparison artifact schema.`,
      );
      return errors;
    }
    comparison = parsed;
  } catch (error: unknown) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual-comparison artifact cannot be read: ${errorMessage(error)}.`,
    );
    return errors;
  }

  if (comparison.schemaVersion !== "frontend-redesign.visual-comparison/v1") {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual-comparison artifact has an unsupported schema version.`,
    );
  }
  if (comparison.uiId !== definition.uiId) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual-comparison artifact identifies ${comparison.uiId}.`,
    );
  }
  if (comparison.fixtureId !== definition.fixtureId) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual-comparison artifact has the wrong fixture ID.`,
    );
  }
  if (comparison.fixtureVersion !== fixtureVersion) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual-comparison artifact has fixture version ${comparison.fixtureVersion}, expected ${fixtureVersion}.`,
    );
  }
  if (
    comparison.viewport.width !== viewport.width ||
    comparison.viewport.height !== viewport.height
  ) {
    errors.push(
      `${definition.uiId} visual-comparison artifact viewport ${formatViewport(comparison.viewport)} does not match ${formatViewport(viewport)}.`,
    );
  }
  if (!comparison.passed) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} visual comparison failed.`,
    );
  }

  const screenshotBytes = await readFile(screenshotPath);
  if (!Buffer.from(screenshotBytes.subarray(0, PNG_SIGNATURE.length)).equals(PNG_SIGNATURE)) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} deterministic fixture screenshot is not a PNG.`,
    );
  }
  if (sha256(screenshotBytes) !== comparison.screenshotSha256) {
    errors.push(
      `${definition.uiId} ${formatViewport(viewport)} screenshot hash does not match its visual-comparison artifact.`,
    );
  }
  return errors;
}

function uniqueValidViewports(
  definition: ScreenDefinition,
  errors: string[],
): readonly ScreenViewport[] {
  const seen = new Set<string>();
  const valid: ScreenViewport[] = [];
  for (const viewport of definition.viewports) {
    const key = formatViewport(viewport);
    if (
      !Number.isInteger(viewport.width) ||
      !Number.isInteger(viewport.height) ||
      viewport.width <= 0 ||
      viewport.height <= 0
    ) {
      errors.push(`${definition.uiId} has an invalid viewport ${key}.`);
      continue;
    }
    if (seen.has(key)) {
      errors.push(`${definition.uiId} repeats viewport ${key}.`);
      continue;
    }
    seen.add(key);
    valid.push(viewport);
  }
  if (valid.length === 0) {
    errors.push(`${definition.uiId} has no specified viewports.`);
  }
  return valid;
}

function resolveFrontendRoot(rootDirectory: string): string {
  return basename(rootDirectory).toLowerCase() === "frontend"
    ? rootDirectory
    : resolve(rootDirectory, "frontend");
}

async function requireFile(
  rootDirectory: string,
  relativePath: string,
  description: string,
  errors: string[],
): Promise<void> {
  const target = resolve(rootDirectory, relativePath);
  let displayPath: string;
  try {
    displayPath = projectPath(rootDirectory, target);
  } catch (error: unknown) {
    errors.push(`${description} path is outside the project root: ${errorMessage(error)}.`);
    return;
  }
  if (!(await isFile(target))) {
    errors.push(`Missing ${description}: ${displayPath}.`);
  }
}

async function isFile(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isFile();
  } catch {
    return false;
  }
}

function projectPath(rootDirectory: string, targetPath: string): string {
  const candidate = resolve(targetPath);
  const candidateRelativePath = relative(resolve(rootDirectory), candidate);
  if (
    candidateRelativePath === "" ||
    candidateRelativePath === ".." ||
    candidateRelativePath.startsWith(`..${sep}`)
  ) {
    throw new Error(`path is outside the project root: ${candidate}`);
  }
  return candidateRelativePath.split(sep).join("/");
}

function artifactPath(rootDirectory: string, targetPath: string): string {
  const candidate = resolve(targetPath);
  const candidateRelativePath = relative(resolve(rootDirectory), candidate);
  if (
    candidateRelativePath === ".." ||
    candidateRelativePath.startsWith(`..${sep}`)
  ) {
    return candidate.split(sep).join("/");
  }
  return candidateRelativePath.split(sep).join("/");
}

function isComparisonArtifact(value: unknown): value is ComparisonArtifact {
  if (value === null || typeof value !== "object") return false;
  const candidate = value as Record<string, unknown>;
  const viewport = candidate.viewport;
  if (viewport === null || typeof viewport !== "object") return false;
  const candidateViewport = viewport as Record<string, unknown>;
  return (
    typeof candidate.schemaVersion === "string" &&
    typeof candidate.uiId === "string" &&
    typeof candidate.fixtureId === "string" &&
    typeof candidate.fixtureVersion === "string" &&
    typeof candidate.screenshotSha256 === "string" &&
    typeof candidate.passed === "boolean" &&
    Number.isInteger(candidateViewport.width) &&
    Number.isInteger(candidateViewport.height)
  );
}

function formatViewport(viewport: ScreenViewport): string {
  return `${viewport.width}x${viewport.height}`;
}

function sha256(value: Uint8Array): string {
  return createHash("sha256").update(value).digest("hex");
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
