import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

import { defaultProjectRoot } from "./visual-verification";

const FIXTURE_DIRECTORY = resolve(
  defaultProjectRoot(),
  "frontend/src/test/fixtures/frontend-redesign/v1",
);

const EXPECTED_FIXTURE_FILES = [
  "generated-client.expectations.json",
  "live-projection-traces.json",
  "openapi.json",
  "projection-redaction.json",
  "public-error.json",
  "public-success.json",
  "reference-origin.json",
] as const;

interface JsonRecord {
  readonly [key: string]: unknown;
}

interface CoverageCase {
  readonly requirement: string;
  readonly source: string;
  readonly markers: readonly string[];
}

const DETERMINISTIC_COVERAGE: readonly CoverageCase[] = [
  {
    requirement: "11.1",
    source: "src/lib/api/generated-contract.test.ts",
    markers: ["versioned OpenAPI fixture", "expected contract surface"],
  },
  {
    requirement: "11.2–11.3",
    source: "src/lib/commands/CommandCoordinator.integration.test.ts",
    markers: [
      "duplicate click",
      "queued response",
      "ambiguous transport outcome",
      "retry exhaustion",
      "returned rate, denial, and manual recovery",
      "cancellation",
      "idempotency",
    ],
  },
  {
    requirement: "11.4–11.5",
    source: "src/lib/live/LiveProjectionController.deterministic.test.tsx",
    markers: [
      "generated REST snapshots before SSE",
      "every fixed replay anomaly",
      "serializes simultaneous replay anomalies",
    ],
  },
  {
    requirement: "11.6",
    source: "src/components/projection/ingestion-controls.test.tsx",
    markers: ["ingestion controls", "quarantined", "artifact adapter blocks delivery"],
  },
  {
    requirement: "11.7",
    source: "src/components/projection/ingestion-controls.test.tsx",
    markers: ["external navigation needs", "unsafe destinations"],
  },
  {
    requirement: "11.8",
    source: "src/lib/projections/projection-boundary.test.tsx",
    markers: ["absent protected", "reference controls"],
  },
  {
    requirement: "11.9",
    source: "src/components/projection/ingestion-controls.test.tsx",
    markers: ["untrusted content", "non-authoritative"],
  },
  {
    requirement: "11.10",
    source: "src/components/browser-boundaries.test.tsx",
    markers: ["accessible control names", "minimum mobile interaction targets", "focus"],
  },
  {
    requirement: "11.11–11.12",
    source: "src/components/screen-composition.test.tsx",
    markers: [
      "representative dashboard, registry, and activity",
      "semantic relationships",
      "data-action-reference-id",
      "data-evidence-reference-id",
    ],
  },
  {
    requirement: "11.13",
    source: "src/components/browser-boundaries.test.tsx",
    markers: ["same-origin generated requests", "security policy"],
  },
  {
    requirement: "11.14",
    source: "scripts/verification-evidence.test.mjs",
    markers: ["command, fixture, result, screenshot, and visual comparison integrity metadata", "exclusive creation"],
  },
] as const;

function asRecord(value: unknown, description: string): JsonRecord {
  assert.ok(value !== null && typeof value === "object" && !Array.isArray(value), description);
  return value as JsonRecord;
}

function stringValue(record: JsonRecord, key: string): string {
  const value = record[key];
  if (typeof value !== "string") {
    throw new TypeError(`Expected ${key} to be a string.`);
  }
  return value;
}

async function readFixture(fileName: string): Promise<JsonRecord> {
  const parsed: unknown = JSON.parse(
    await readFile(resolve(FIXTURE_DIRECTORY, fileName), "utf8"),
  );
  return asRecord(parsed, `${fileName} must contain a JSON object.`);
}

test("keeps the versioned deterministic fixture registry complete and internally consistent", async (): Promise<void> => {
  const actualFiles = (await readdir(FIXTURE_DIRECTORY)).sort();
  assert.deepEqual(actualFiles, [...EXPECTED_FIXTURE_FILES].sort());

  for (const fileName of EXPECTED_FIXTURE_FILES) {
    const fixture = await readFixture(fileName);
    if (fileName === "openapi.json") {
      assert.equal(stringValue(fixture, "openapi"), "3.1.0", fileName);
    } else {
      assert.equal(stringValue(fixture, "fixtureVersion"), "frontend-redesign/v1", fileName);
    }
  }
});

test("covers every deterministic command, replay, ingress, redaction, and evidence scenario in fixtures", async (): Promise<void> => {
  const success = await readFixture("public-success.json");
  assert.deepEqual(Object.keys(asRecord(success.data, "success data")).sort(), ["run_id", "status"]);
  assert.deepEqual(Object.keys(asRecord(success.meta, "success meta")), ["correlation_id"]);
  assert.equal(success.internal_trace, "must-not-reach-view-state");

  const error = await readFixture("public-error.json");
  const errorData = asRecord(error.error, "public error");
  assert.deepEqual(
    Object.keys(errorData).sort(),
    ["action_reference", "code", "correlation_id", "internal_trace", "message", "retry_after", "retryable"],
  );
  assert.equal(errorData.code, "rate_limited");
  assert.equal(errorData.retry_after, 7);
  assert.equal(errorData.internal_trace, "must-not-reach-view-state");

  const redaction = await readFixture("projection-redaction.json");
  const redactionProjection = asRecord(redaction.projection, "redaction projection");
  const allowedFields = redaction.allowedFields;
  assert.deepEqual(allowedFields, ["status", "summary"]);
  assert.deepEqual(Object.keys(redactionProjection).sort(), ["internal_trace", "protected_field", "raw_prompt", "status", "summary"]);
  assert.equal(redactionProjection.protected_field, "PROTECTED_SENTINEL");
  assert.equal(redactionProjection.raw_prompt, "RAW_SENTINEL");

  const reference = await readFixture("reference-origin.json");
  for (const referenceKey of ["opaque", "action", "evidence"]) {
    const referenceValue = asRecord(reference[referenceKey], `${referenceKey} reference`);
    assert.ok(typeof referenceValue.id === "string");
    assert.ok(typeof referenceValue.label === "string");
    assert.equal(referenceValue.internal_note, "returned-but-not-rendered");
  }

  const live = await readFixture("live-projection-traces.json");
  assert.deepEqual(live.authorizedTopics, ["run.updated"]);
  assert.deepEqual(live.replayAnomalies, [
    "bounded",
    "expired",
    "denied",
    "schema_mismatch",
    "duplicate",
    "out_of_order",
    "sequence_gap",
  ]);
  assert.equal(asRecord(live.initial, "initial snapshot").expectedSequence, 7);
  assert.equal(asRecord(live.replacement, "replacement snapshot").expectedSequence, 30);
  assert.equal(asRecord(asRecord(live.unavailable, "unavailable state").action, "unavailable action").kind, "refresh");
});

test("retains focused test coverage for every Requirement 11 deterministic verification family", async (): Promise<void> => {
  for (const coverage of DETERMINISTIC_COVERAGE) {
    const source = (await readFile(resolve(defaultProjectRoot(), "frontend", coverage.source), "utf8")).toLowerCase();
    for (const marker of coverage.markers) {
      assert.ok(
        source.includes(marker.toLowerCase()),
        `${coverage.requirement} is missing deterministic coverage marker: ${marker}`,
      );
    }
  }
});
