import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { writeVerificationEvidence } from "./verification-evidence.mjs";

const FRONTEND_ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const NPM_EXECUTABLE = process.platform === "win32" ? process.execPath : "npm";
const NPM_CLI =
  process.env.npm_execpath ??
  resolve(
    dirname(process.execPath),
    "node_modules",
    "npm",
    "bin",
    "npm-cli.js",
  );

function npmCommand(args) {
  return {
    executable: NPM_EXECUTABLE,
    args: process.platform === "win32" ? [NPM_CLI, ...args] : args,
    display: ["npm", ...args].join(" "),
  };
}
const FIXTURE_VERSION =
  process.env.FRONTEND_VERIFICATION_FIXTURE_VERSION ?? "1.0.0";
const FIXTURE_ID =
  process.env.FRONTEND_VERIFICATION_FIXTURE_ID ?? "frontend-redesign";
const VISUAL_FIXTURE_VERSION = "frontend-redesign/v1";
const COMMANDS = [
  { name: "frontend-test", ...npmCommand(["test", "--", "--silent"]) },
  { name: "frontend-api", ...npmCommand(["run", "api:ci"]) },
  {
    name: "frontend-source-policy",
    ...npmCommand(["run", "source:policy"]),
  },
];

function artifactPathsFromEnvironment(name) {
  const scopedName = name.toUpperCase().replaceAll("-", "_");
  const scopedValue = process.env[`FRONTEND_VERIFICATION_${scopedName}`];
  const value = scopedValue ?? process.env.FRONTEND_VERIFICATION_ARTIFACTS;
  if (value === undefined || value.length === 0) return [];
  if (value.startsWith("[")) {
    const parsed = JSON.parse(value);
    if (
      !Array.isArray(parsed) ||
      !parsed.every((item) => typeof item === "string")
    )
      throw new Error(
        `FRONTEND_VERIFICATION_${scopedName} must be a JSON array of paths.`,
      );
    return parsed;
  }
  return value
    .split(process.platform === "win32" ? ";" : ":")
    .filter((item) => item.length > 0);
}

async function discoverVisualArtifacts(directory) {
  const screenshots = [];
  const visualComparisonArtifacts = [];

  async function visit(currentDirectory) {
    let entries;
    try {
      entries = await readdir(currentDirectory, { withFileTypes: true });
    } catch (error) {
      if (error?.code === "ENOENT") return;
      throw error;
    }
    for (const entry of entries) {
      const path = join(currentDirectory, entry.name);
      if (entry.isDirectory()) {
        await visit(path);
        continue;
      }
      const name = entry.name.toLowerCase();
      if (name.startsWith("screenshot.")) screenshots.push(path);
      if (
        name === "comparison.json" ||
        name === "baseline.png" ||
        name === "mismatch.png"
      )
        visualComparisonArtifacts.push(path);
    }
  }

  await visit(directory);
  return { screenshots, visualComparisonArtifacts };
}

function runCommand(command) {
  return new Promise((resolvePromise) => {
    const startedAt = Date.now();
    const child = spawn(command.executable, command.args, {
      cwd: FRONTEND_ROOT,
      stdio: "inherit",
    });
    child.once("error", () =>
      resolvePromise({
        status: "failed",
        exitCode: null,
        durationMs: Date.now() - startedAt,
      }),
    );
    child.once("close", (exitCode, signal) =>
      resolvePromise({
        status: exitCode === 0 ? "passed" : "failed",
        exitCode,
        ...(signal === null ? {} : { signal }),
        durationMs: Date.now() - startedAt,
      }),
    );
  });
}

function runId() {
  return (
    process.env.FRONTEND_VERIFICATION_RUN_ID ??
    `${new Date().toISOString().replaceAll(/[^0-9A-Za-z-]/g, "-")}-${randomUUID()}`
  ).replaceAll(/[^0-9A-Za-z_.-]/g, "-");
}

const verificationRunId = runId();
const outputDirectory =
  process.env.FRONTEND_VERIFICATION_OUTPUT_DIR ??
  `artifacts/frontend-verification/${verificationRunId}`;
const visualOutputDirectory = resolve(FRONTEND_ROOT, outputDirectory, "visual");
COMMANDS.push({
  name: "frontend-visual",
  ...npmCommand([
    "run",
    "screens:visual",
    "--",
    "--output",
    visualOutputDirectory,
  ]),
});
const fixtureVersions = [
  {
    id: FIXTURE_ID,
    version: FIXTURE_VERSION,
    source: "src/test/fixtures/frontend-redesign/v1",
  },
];
let failed = false;

for (const [index, command] of COMMANDS.entries()) {
  const result = await runCommand(command);
  failed ||= result.status === "failed";
  const generatedVisualArtifacts =
    command.name === "frontend-visual"
      ? await discoverVisualArtifacts(visualOutputDirectory)
      : { screenshots: [], visualComparisonArtifacts: [] };
  const screenshots = [
    ...artifactPathsFromEnvironment(`${command.name}-SCREENSHOTS`),
    ...generatedVisualArtifacts.screenshots,
  ];
  const visualComparisons = [
    ...artifactPathsFromEnvironment(`${command.name}-VISUAL_COMPARISONS`),
    ...generatedVisualArtifacts.visualComparisonArtifacts,
  ];
  const evidence = await writeVerificationEvidence({
    projectRoot: FRONTEND_ROOT,
    outputDirectory,
    fileName: `${String(index + 1).padStart(2, "0")}-${command.name}.json`,
    evidenceId: `${verificationRunId}.${command.name}`,
    command: command.display,
    result,
    fixtureVersions:
      command.name === "frontend-visual"
        ? [
            ...fixtureVersions,
            {
              id: "frontend-redesign.visual",
              version: VISUAL_FIXTURE_VERSION,
              source: "docs/frontend_redesign",
            },
          ]
        : fixtureVersions,
    screenshotPaths: screenshots,
    visualComparisonPaths: visualComparisons,
  });
  process.stdout.write(`Immutable frontend evidence: ${evidence.path}\n`);
}

process.exitCode = failed ? 1 : 0;
