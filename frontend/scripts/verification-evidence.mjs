import { createHash } from "node:crypto";
import { chmod, mkdir, open, readFile } from "node:fs/promises";
import { isAbsolute, relative, resolve, sep } from "node:path";

export const VERIFICATION_EVIDENCE_SCHEMA_VERSION =
  "frontend-verification-evidence.v1";
const RESULT_STATUSES = new Set(["passed", "failed", "skipped"]);

function canonicalize(value) {
  if (Array.isArray(value))
    return `[${value.map((item) => canonicalize(item)).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function relativeProjectPath(projectRoot, targetPath) {
  const projectPath = resolve(projectRoot);
  const candidatePath = resolve(targetPath);
  const candidateRelativePath = relative(projectPath, candidatePath);
  if (
    candidateRelativePath === "" ||
    candidateRelativePath === ".." ||
    candidateRelativePath.startsWith(`..${sep}`) ||
    isAbsolute(candidateRelativePath)
  ) {
    throw new Error(
      `Verification evidence path must remain inside ${projectPath}: ${candidatePath}`,
    );
  }
  return candidateRelativePath.split(sep).join("/");
}

function normalizeFixtureVersions(fixtureVersions) {
  if (!Array.isArray(fixtureVersions) || fixtureVersions.length === 0) {
    throw new Error(
      "Verification evidence requires at least one fixture version.",
    );
  }

  return fixtureVersions.map((fixture) => {
    if (typeof fixture === "string")
      return { id: "frontend-redesign", version: fixture };
    if (
      fixture === null ||
      typeof fixture !== "object" ||
      typeof fixture.id !== "string" ||
      typeof fixture.version !== "string"
    ) {
      throw new Error(
        "Each fixture version must contain string id and version fields.",
      );
    }
    return {
      id: fixture.id,
      version: fixture.version,
      ...(typeof fixture.source === "string" ? { source: fixture.source } : {}),
    };
  });
}

function normalizeResult(result) {
  if (
    result === null ||
    typeof result !== "object" ||
    typeof result.status !== "string" ||
    !RESULT_STATUSES.has(result.status)
  ) {
    throw new Error(
      "Verification evidence requires a passed, failed, or skipped result status.",
    );
  }
  if (
    result.exitCode !== null &&
    result.exitCode !== undefined &&
    !Number.isInteger(result.exitCode)
  ) {
    throw new Error("Verification result exitCode must be an integer or null.");
  }
  return {
    status: result.status,
    exitCode: result.exitCode ?? null,
    ...(typeof result.signal === "string" ? { signal: result.signal } : {}),
    ...(Number.isInteger(result.durationMs)
      ? { durationMs: result.durationMs }
      : {}),
  };
}

async function captureArtifacts(projectRoot, paths) {
  if (!Array.isArray(paths))
    throw new Error("Verification artifact paths must be arrays.");
  return Promise.all(
    paths.map(async (artifactPath) => {
      if (typeof artifactPath !== "string" || artifactPath.length === 0)
        throw new Error(
          "Verification artifact paths must be non-empty strings.",
        );
      const absolutePath = resolve(projectRoot, artifactPath);
      const path = relativeProjectPath(projectRoot, absolutePath);
      const bytes = await readFile(absolutePath);
      return { path, sha256: sha256(bytes), sizeBytes: bytes.length };
    }),
  );
}

export function calculateEvidenceHash(record) {
  if (record === null || typeof record !== "object")
    throw new Error("A verification evidence record is required.");
  const { integrity: _integrity, ...unsignedRecord } = record;
  return sha256(canonicalize(unsignedRecord));
}

export function createVerificationEvidence({
  evidenceId,
  command,
  fixtureVersions,
  result,
  screenshots = [],
  visualComparisonArtifacts = [],
  recordedAt,
}) {
  if (typeof evidenceId !== "string" || evidenceId.length === 0)
    throw new Error("Verification evidence requires an evidenceId.");
  if (typeof command !== "string" || command.length === 0)
    throw new Error("Verification evidence requires the executed command.");
  if (typeof recordedAt !== "string" || recordedAt.length === 0)
    throw new Error("Verification evidence requires recordedAt.");

  const unsignedRecord = {
    schemaVersion: VERIFICATION_EVIDENCE_SCHEMA_VERSION,
    evidenceId,
    recordedAt,
    command,
    fixtureVersions: normalizeFixtureVersions(fixtureVersions),
    result: normalizeResult(result),
    artifacts: {
      screenshots,
      visualComparisonArtifacts,
    },
  };
  const recordHash = sha256(canonicalize(unsignedRecord));
  return {
    ...unsignedRecord,
    integrity: {
      algorithm: "sha256",
      recordHash,
    },
  };
}

export async function writeVerificationEvidence({
  projectRoot = process.cwd(),
  outputDirectory,
  fileName,
  evidenceId,
  command,
  fixtureVersions,
  result,
  screenshotPaths = [],
  visualComparisonPaths = [],
  recordedAt = new Date().toISOString(),
}) {
  const root = resolve(projectRoot);
  if (typeof outputDirectory !== "string" || outputDirectory.length === 0)
    throw new Error("Verification evidence requires an output directory.");
  if (
    typeof fileName !== "string" ||
    fileName.length === 0 ||
    fileName.includes("/") ||
    fileName.includes("\\") ||
    !fileName.endsWith(".json")
  ) {
    throw new Error(
      "Verification evidence fileName must be a JSON file name without path separators.",
    );
  }

  const output = resolve(root, outputDirectory);
  relativeProjectPath(root, output);
  const screenshots = await captureArtifacts(root, screenshotPaths);
  const visualComparisonArtifacts = await captureArtifacts(
    root,
    visualComparisonPaths,
  );
  const record = createVerificationEvidence({
    evidenceId,
    command,
    fixtureVersions,
    result,
    screenshots,
    visualComparisonArtifacts,
    recordedAt,
  });

  await mkdir(output, { recursive: true });
  const target = resolve(output, fileName);
  relativeProjectPath(root, target);
  const handle = await open(target, "wx");
  try {
    await handle.writeFile(`${JSON.stringify(record, null, 2)}\n`, "utf8");
  } finally {
    await handle.close();
  }
  await chmod(target, 0o444);
  return { path: target, record };
}
