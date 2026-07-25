import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import test from "node:test";
import { join } from "node:path";
import { tmpdir } from "node:os";

import {
  calculateEvidenceHash,
  writeVerificationEvidence,
} from "./verification-evidence.mjs";

test("records command, fixture, result, screenshot, and visual comparison integrity metadata", async () => {
  const projectRoot = await mkdtemp(
    join(tmpdir(), "frontend-verification-evidence-"),
  );
  try {
    const screenshotPath = join(projectRoot, "screenshots", "dashboard.png");
    const visualComparisonPath = join(
      projectRoot,
      "comparisons",
      "dashboard.json",
    );
    await mkdir(join(projectRoot, "screenshots"), { recursive: true });
    await mkdir(join(projectRoot, "comparisons"), { recursive: true });
    await writeFile(screenshotPath, "deterministic screenshot");
    await writeFile(visualComparisonPath, "deterministic visual comparison");

    const written = await writeVerificationEvidence({
      projectRoot,
      outputDirectory: "evidence",
      fileName: "run-1.json",
      evidenceId: "run-1.frontend-test",
      command: "npm test -- --silent",
      fixtureVersions: [
        {
          id: "frontend-redesign",
          version: "1.0.0",
          source: "src/test/fixtures/frontend-redesign/v1",
        },
      ],
      result: { status: "passed", exitCode: 0, durationMs: 42 },
      screenshotPaths: [screenshotPath],
      visualComparisonPaths: [visualComparisonPath],
      recordedAt: "2026-01-02T03:04:05.000Z",
    });

    const record = JSON.parse(await readFile(written.path, "utf8"));
    assert.equal(record.command, "npm test -- --silent");
    assert.deepEqual(record.fixtureVersions, [
      {
        id: "frontend-redesign",
        version: "1.0.0",
        source: "src/test/fixtures/frontend-redesign/v1",
      },
    ]);
    assert.deepEqual(record.result, {
      status: "passed",
      exitCode: 0,
      durationMs: 42,
    });
    assert.equal(
      record.artifacts.screenshots[0].path,
      "screenshots/dashboard.png",
    );
    assert.equal(
      record.artifacts.visualComparisonArtifacts[0].path,
      "comparisons/dashboard.json",
    );
    assert.match(record.artifacts.screenshots[0].sha256, /^[a-f0-9]{64}$/);
    assert.match(
      record.artifacts.visualComparisonArtifacts[0].sha256,
      /^[a-f0-9]{64}$/,
    );
    assert.equal(record.integrity.recordHash, calculateEvidenceHash(record));
  } finally {
    await rm(projectRoot, { force: true, recursive: true });
  }
});

test("uses exclusive creation so an evidence record cannot be overwritten", async () => {
  const projectRoot = await mkdtemp(
    join(tmpdir(), "frontend-verification-evidence-"),
  );
  try {
    const input = {
      projectRoot,
      outputDirectory: "evidence",
      fileName: "run-1.json",
      evidenceId: "run-1.frontend-test",
      command: "npm test -- --silent",
      fixtureVersions: ["1.0.0"],
      result: { status: "failed", exitCode: 1 },
      recordedAt: "2026-01-02T03:04:05.000Z",
    };
    await writeVerificationEvidence(input);
    await assert.rejects(
      writeVerificationEvidence(input),
      /already exists|EEXIST/,
    );
  } finally {
    await rm(projectRoot, { force: true, recursive: true });
  }
});

test("rejects evidence output and artifacts outside the project root", async () => {
  const projectRoot = await mkdtemp(
    join(tmpdir(), "frontend-verification-evidence-"),
  );
  try {
    await assert.rejects(
      writeVerificationEvidence({
        projectRoot,
        outputDirectory: "../evidence",
        fileName: "run-1.json",
        evidenceId: "run-1.frontend-test",
        command: "npm test -- --silent",
        fixtureVersions: ["1.0.0"],
        result: { status: "passed", exitCode: 0 },
        recordedAt: "2026-01-02T03:04:05.000Z",
      }),
      /must remain inside/,
    );
  } finally {
    await rm(projectRoot, { force: true, recursive: true });
  }
});
