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
  const api = createOperatorApi({ fetchImpl: async (_input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    requestBody = String(init?.body);
    return Response.json({ approval_id: "approval-1", run_id: "run-1", actor_id: "host-derived", selected_value: "denied", reason_is_valid: true, value_is_valid: true, resumed: false, gate_status: "paused", submitted_at: "2026-01-02T03:04:05Z", action_preview: preview });
  } });
  const decision = await api.submitApprovalDecision("approval-1", "denied", "Needs review");
  assert.deepEqual(JSON.parse(requestBody), { selected_value: "denied", reason: "Needs review" });
  assert.equal(decision.actor_id, "host-derived");
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
  assert.throws(() => createOperatorApi({ baseUrl: "https://host.invalid/api" }), OperatorApiError);
});
