import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";

import { createPublicApiClient } from "./client";
import type { RunResponse } from "./generated";

const RUN_OPERATION = "read_run_api_v1_workflow_runs__run_id__get" as const;
const SENSITIVE_SENTINEL = "private-envelope-sentinel";
const safeText = fc.oneof(fc.string(), fc.constant("密碼 🔒 <script>alert(1)</script>")).filter((value: string): boolean => !value.includes(SENSITIVE_SENTINEL));
const runResponseArbitrary: fc.Arbitrary<RunResponse> = fc.tuple(
  safeText,
  safeText,
  safeText,
  safeText,
  safeText,
  safeText,
  safeText,
).map(([correlation_id, engine, run_id, status, updated_at, workflow_id, workflow_version]): RunResponse => ({
  correlation_id,
  engine,
  run_id,
  status,
  updated_at,
  workflow_id,
  workflow_version,
}));

interface SuccessScenario { readonly kind: "success"; readonly data: RunResponse; readonly correlationId: string; }
interface ErrorScenario { readonly kind: "error"; readonly code: string; readonly message: string; readonly retryable: boolean; readonly correlationId?: string; readonly retryAfterSeconds?: number; readonly actionReference?: { readonly id: string }; }
type Scenario = SuccessScenario | ErrorScenario;

const actionReferenceArbitrary: fc.Arbitrary<{ readonly id: string }> = safeText.map((id: string): { readonly id: string } => ({ id }));
const successScenarioArbitrary: fc.Arbitrary<SuccessScenario> = fc.tuple(runResponseArbitrary, safeText)
  .map(([data, correlationId]): SuccessScenario => ({ kind: "success", data, correlationId }));
const errorScenarioArbitrary: fc.Arbitrary<ErrorScenario> = fc.tuple(
  safeText,
  safeText,
  fc.boolean(),
  fc.option(safeText, { nil: undefined }),
  fc.option(fc.integer({ min: 0, max: 1_000_000 }), { nil: undefined }),
  fc.option(actionReferenceArbitrary, { nil: undefined }),
).map(([code, message, retryable, correlationId, retryAfterSeconds, actionReference]): ErrorScenario => ({
  kind: "error",
  code,
  message,
  retryable,
  ...(correlationId === undefined ? {} : { correlationId }),
  ...(retryAfterSeconds === undefined ? {} : { retryAfterSeconds }),
  ...(actionReference === undefined ? {} : { actionReference }),
}));
const scenarioArbitrary: fc.Arbitrary<Scenario> = fc.oneof(successScenarioArbitrary, errorScenarioArbitrary);

// Feature: frontend-redesign, Property 1: Envelope mapping is schema-bounded and redaction-safe
// Validates: Requirements 1.4, 1.5
test("maps arbitrary public envelopes to the approved redaction-safe state", async (): Promise<void> => {
  await fc.assert(fc.asyncProperty(scenarioArbitrary, async (scenario: Scenario): Promise<void> => {
    const payload = scenario.kind === "success"
      ? { data: scenario.data, meta: { correlation_id: scenario.correlationId, internal_trace: SENSITIVE_SENTINEL }, internal_trace: SENSITIVE_SENTINEL }
      : { error: { code: scenario.code, message: scenario.message, retryable: scenario.retryable, ...(scenario.correlationId === undefined ? {} : { correlation_id: scenario.correlationId }), ...(scenario.retryAfterSeconds === undefined ? {} : { retry_after: scenario.retryAfterSeconds }), ...(scenario.actionReference === undefined ? {} : { action_reference: scenario.actionReference }), internal_trace: SENSITIVE_SENTINEL }, internal_trace: SENSITIVE_SENTINEL };
    const client = createPublicApiClient({ fetchImpl: async (): Promise<Response> => Response.json(payload, { status: scenario.kind === "success" ? 200 : 400 }) });
    const result = await client.request(RUN_OPERATION, { path: { run_id: "run-1" } });
    const expected = scenario.kind === "success" ? { ok: true, data: scenario.data, correlationId: scenario.correlationId } : { ok: false, code: scenario.code, message: scenario.message, retryable: scenario.retryable, ...(scenario.correlationId === undefined ? {} : { correlationId: scenario.correlationId }), ...(scenario.retryAfterSeconds === undefined ? {} : { retryAfterSeconds: scenario.retryAfterSeconds }), ...(scenario.actionReference === undefined ? {} : { actionReference: scenario.actionReference }) };
    assert.deepEqual(result, expected);
    assert.equal(JSON.stringify(result).includes(SENSITIVE_SENTINEL), false);
  }), { numRuns: 100 });
});
