import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from "node:fs/promises";
import test from "node:test";
import { join } from "node:path";
import { tmpdir } from "node:os";

import {
  calculateEvidenceHash,
  writeVerificationEvidence,
} from "./verification-evidence.mjs";

test("records every CI evidence field and makes the evidence record immutable", async () => {
  const projectRoot = await mkdtemp(join(tmpdir(), "frontend-evidence-metadata-"));
  try {
    const screenshotPath = join(projectRoot, "visual", "ui_02_dashboard", "390x844", "screenshot.png");
    const comparisonPath = join(projectRoot, "visual", "ui_02_dashboard", "390x844", "comparison.json");
    await mkdir(join(projectRoot, "visual", "ui_02_dashboard", "390x844"), { recursive: true });
    await writeFile(screenshotPath, Buffer.from([137, 80, 78, 71]));
    await writeFile(comparisonPath, JSON.stringify({ passed: true, fixtureVersion: "frontend-redesign/v1" }));

    const result = await writeVerificationEvidence({
      projectRoot,
      outputDirectory: "evidence/run-1",
      fileName: "01-frontend-visual.json",
      evidenceId: "run-1.frontend-visual",
      command: "npm run screens:visual -- --output artifacts/frontend-visual",
      fixtureVersions: [
        { id: "frontend-redesign", version: "1.0.0", source: "src/test/fixtures/frontend-redesign/v1" },
        { id: "frontend-redesign.visual", version: "frontend-redesign/v1", source: "docs/frontend_redesign" },
      ],
      result: { status: "passed", exitCode: 0, durationMs: 17 },
      screenshotPaths: [screenshotPath],
      visualComparisonPaths: [comparisonPath],
      recordedAt: "2026-07-20T04:12:00.000Z",
    });

    const record = JSON.parse(await readFile(result.path, "utf8"));
    assert.equal(record.schemaVersion, "frontend-verification-evidence.v1");
    assert.equal(record.evidenceId, "run-1.frontend-visual");
    assert.equal(record.command, "npm run screens:visual -- --output artifacts/frontend-visual");
    assert.deepEqual(record.fixtureVersions, [
      { id: "frontend-redesign", version: "1.0.0", source: "src/test/fixtures/frontend-redesign/v1" },
      { id: "frontend-redesign.visual", version: "frontend-redesign/v1", source: "docs/frontend_redesign" },
    ]);
    assert.deepEqual(record.result, { status: "passed", exitCode: 0, durationMs: 17 });
    assert.equal(record.artifacts.screenshots.length, 1);
    assert.equal(record.artifacts.visualComparisonArtifacts.length, 1);
    assert.match(record.artifacts.screenshots[0].sha256, /^[a-f0-9]{64}$/);
    assert.match(record.artifacts.visualComparisonArtifacts[0].sha256, /^[a-f0-9]{64}$/);
    assert.equal(record.integrity.recordHash, calculateEvidenceHash(record));
    assert.equal((await stat(result.path)).mode & 0o777, 0o444);
  } finally {
    await rm(projectRoot, { force: true, recursive: true });
  }
});
