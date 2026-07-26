import assert from "node:assert/strict";
import test from "node:test";

import {
  OperatorApiError,
  createOperatorApi,
  operatorCorrection,
} from "./contracts";

const preview = {
  action_id: "action-1", summary: "Create a record", intended_effect: "A local record will be created", emitted_at: "2026-01-02T03:04:05Z", rollback_preview: "Delete the record", supporting_evidence: ["case-1"], confidence: 0.9, uncertainty: null, correction_control: "Cancel",
};

test("reads redacted graph state through the versioned Host API only", async () => {
  const paths: string[] = [];
  const api = createOperatorApi({ fetchImpl: async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    paths.push(String(input)); assert.equal(init?.credentials, "include");
    return Response.json({ run_id: "run-1", status: "waiting_for_approval", engine: "legacy", graph_id: null, graph_thread_id: null, updated_at: "2026-01-02T03:04:05Z", failure_code: null, tool_effects: [], action_previews: [preview] });
  } });
  const graph = await api.getGraphState("run-1");
  assert.equal(paths[0], "/api/v1/workflow-runs/run-1/graph-state");
  assert.equal(graph.action_previews[0]?.summary, "Create a record");
});

test("submits only a selected approval decision without a client actor", async () => {
  let requestBody = "";
  let requestHeaders: HeadersInit | undefined;
  const api = createOperatorApi({ fetchImpl: async (_input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    requestBody = String(init?.body);
    requestHeaders = init?.headers;
    return Response.json({ approval_id: "approval-1", run_id: "run-1", actor_id: "host-derived", selected_value: "denied", reason_is_valid: true, value_is_valid: true, resumed: false, gate_status: "paused", submitted_at: "2026-01-02T03:04:05Z", action_preview: preview });
  } });
  const decision = await api.submitApprovalDecision("approval-1", "denied", "Needs review", { idempotencyKey: "decision-key-1" });
  assert.deepEqual(JSON.parse(requestBody), { selected_value: "denied", reason: "Needs review" });
  assert.equal(decision.actor_id, "host-derived");
  const headers = requestHeaders as Record<string, string>;
  assert.equal(headers["Idempotency-Key"], "decision-key-1");
});

test("reports typed Host errors with a safe correction control", async () => {
  const api = createOperatorApi({ fetchImpl: async (): Promise<Response> => Response.json({ detail: { code: "authorization_denied", message: "Sensitive policy omitted", correlation_id: "corr-1", retryable: false } }, { status: 403 }) });
  await assert.rejects(api.getRun("run-1"), (error: unknown): boolean => {
    assert.ok(error instanceof OperatorApiError);
    assert.equal(error.detail.code, "authorization_denied");
    assert.equal(error.detail.correlationId, "corr-1");
    assert.match(operatorCorrection(error), /authority/i);
    return true;
  });
});

test("drops unrendered run output from the redacted client projection", async () => {
  const api = createOperatorApi({ fetchImpl: async (): Promise<Response> => Response.json({ run_id: "run-1", workflow_id: "workflow-1", workflow_version: "1", status: "queued", engine: "legacy", correlation_id: "corr-1", updated_at: "2026-01-02T03:04:05Z", output: { secret: "not rendered" }, failure_code: null, action_preview: null }) });
  const run = await api.getRun("run-1");
  assert.equal("output" in run, false);
});

test("keeps every operator contract call inside the versioned Host namespace", async () => {
  const paths: string[] = [];
  const api = createOperatorApi({ fetchImpl: async (input: RequestInfo | URL): Promise<Response> => {
    paths.push(String(input));
    if (String(input).endsWith("/graph-state")) return Response.json({ run_id: "run-1", status: "queued", engine: "legacy", graph_id: null, graph_thread_id: null, updated_at: "2026-01-02T03:04:05Z", failure_code: null, tool_effects: [], action_previews: [] });
    if (String(input).includes("/approvals/")) return Response.json({ approval_id: "approval-1", run_id: "run-1", risk_tier: "critical", gate_status: "paused", created_at: "2026-01-02T03:04:05Z", action_preview: preview });
    return Response.json({ run_id: "run-1", workflow_id: "workflow-1", workflow_version: "1", status: "queued", engine: "legacy", correlation_id: "corr-1", updated_at: "2026-01-02T03:04:05Z", failure_code: null, action_preview: null });
  } });
  await api.getRun("run-1");
  await api.getGraphState("run-1");
  await api.getApprovalGate("approval-1");
  assert.ok(paths.length === 3 && paths.every((path) => path.startsWith("/api/v1/")));
});

test("E1 operator contract keeps redacted projections on same-origin versioned routes", async () => {
  const calls: Array<{ readonly path: string; readonly method: string; readonly credentials: RequestCredentials | undefined; readonly body: string | undefined }> = [];
  const api = createOperatorApi({ fetchImpl: async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    calls.push({ path: String(input), method: init?.method ?? "GET", credentials: init?.credentials, body: typeof init?.body === "string" ? init.body : undefined });
    const path = String(input);
    if (path.endsWith("/graph-state")) return Response.json({ run_id: "run-1", status: "waiting_for_approval", engine: "legacy", graph_id: null, graph_thread_id: null, updated_at: "2026-01-02T03:04:05Z", failure_code: null, tool_effects: [], action_previews: [preview] });
    if (path.endsWith("/decision")) return Response.json({ approval_id: "approval-1", run_id: "run-1", actor_id: "host-derived", selected_value: "approved", reason_is_valid: true, value_is_valid: true, resumed: true, gate_status: "resumed", submitted_at: "2026-01-02T03:04:05Z", action_preview: preview });
    if (path.includes("/approvals/")) return Response.json({ approval_id: "approval-1", run_id: "run-1", risk_tier: "critical", gate_status: "paused", created_at: "2026-01-02T03:04:05Z", action_preview: preview });
    return Response.json({ run_id: "run-1", workflow_id: "workflow-1", workflow_version: "1", status: "queued", engine: "legacy", correlation_id: "corr-1", updated_at: "2026-01-02T03:04:05Z", output: { secret: "not rendered" }, failure_code: null, action_preview: null });
  } });

  const run = await api.getRun("run-1");
  const graph = await api.getGraphState("run-1");
  const gate = await api.getApprovalGate("approval-1");
  const decision = await api.submitApprovalDecision("approval-1", "approved", "Reviewed locally.");

  assert.equal("output" in run, false);
  assert.equal(graph.action_previews[0]?.action_id, "action-1");
  assert.equal(gate.gate_status, "paused");
  assert.equal(decision.actor_id, "host-derived");
  assert.ok(calls.every((call) => call.path.startsWith("/api/v1/")));
  assert.ok(calls.every((call) => call.credentials === "include"));
  assert.deepEqual(calls.map((call) => call.path), [
    "/api/v1/workflow-runs/run-1",
    "/api/v1/workflow-runs/run-1/graph-state",
    "/api/v1/approvals/approval-1",
    "/api/v1/approvals/approval-1/decision",
  ]);
  assert.equal(calls[3]?.body, JSON.stringify({ selected_value: "approved", reason: "Reviewed locally." }));
});

test("legacy operator mutations always send Idempotency-Key on /api/v1 only", async () => {
  const headersSeen: Array<Record<string, string>> = [];
  const api = createOperatorApi({ fetchImpl: async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    assert.equal(String(input), "/api/v1/approvals/approval-1/decision");
    headersSeen.push({ ...(init?.headers as Record<string, string>) });
    return Response.json({
      approval_id: "approval-1", run_id: "run-1", actor_id: "host-derived", selected_value: "approved",
      reason_is_valid: true, value_is_valid: true, resumed: true, gate_status: "resumed",
      submitted_at: "2026-01-02T03:04:05Z", action_preview: preview,
    });
  } });
  await api.submitApprovalDecision("approval-1", "approved", "Reviewed.", { idempotencyKey: "stable-key" });
  await api.submitApprovalDecision("approval-1", "approved", "Reviewed.");
  assert.equal(headersSeen[0]?.["Idempotency-Key"], "stable-key");
  assert.ok(typeof headersSeen[1]?.["Idempotency-Key"] === "string" && headersSeen[1]["Idempotency-Key"].length > 0);
});
