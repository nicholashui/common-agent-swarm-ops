/**
 * Real UI interaction runtime: local store mutations + generated /api/v1 calls.
 * Presentation homes should use this instead of fake announce-only handlers.
 */

"use client";

import { useCallback, useMemo, useState } from "react";

import { createPublicApiClient, type PublicApiClient } from "../api/client";
import type { GeneratedOperationId, GeneratedOperationRequest } from "../api/generated";
import { createOperatorApi, type OperatorApi } from "../contracts";
import {
  getScreenParameters,
  setScreenParameters,
  updateScreenParameters,
  type ScreenParameterKey,
  type ScreenParameterMap,
} from "../projections/screen-parameters";

export type InteractionStatusKind = "idle" | "busy" | "success" | "error" | "info";

export interface InteractionStatus {
  readonly kind: InteractionStatusKind;
  readonly message: string;
  readonly correlationId?: string;
}

export interface InteractionRuntime {
  readonly status: InteractionStatus;
  readonly busy: boolean;
  readonly api: PublicApiClient;
  readonly operator: OperatorApi;
  readonly setInfo: (message: string) => void;
  readonly setError: (message: string, correlationId?: string) => void;
  readonly setSuccess: (message: string, correlationId?: string) => void;
  readonly clearStatus: () => void;
  /** Persist a full screen view into the parameter store (re-renders bound homes). */
  readonly replaceScreen: <K extends ScreenParameterKey>(
    key: K,
    view: ScreenParameterMap[K],
  ) => void;
  /** Shallow-merge fields into a stored screen view. */
  readonly patchScreen: <K extends ScreenParameterKey>(
    key: K,
    patch: Partial<ScreenParameterMap[K]>,
  ) => ScreenParameterMap[K];
  /** Execute a generated Public API operation with real fetch + feedback. */
  readonly requestGenerated: <TId extends GeneratedOperationId>(
    operationId: TId,
    request: GeneratedOperationRequest<TId>,
    options?: { readonly idempotencyKey?: string; readonly successMessage?: string },
  ) => Promise<boolean>;
  /** Inspect a workflow run through the real operator API. */
  readonly inspectRun: (runId: string) => Promise<boolean>;
  /** Load an approval gate by id through the real operator API. */
  readonly loadApproval: (approvalId: string) => Promise<boolean>;
  /** Submit an approval decision with a stable Idempotency-Key. */
  readonly decideApproval: (
    approvalId: string,
    value: "approved" | "denied",
    reason: string,
    idempotencyKey?: string,
  ) => Promise<boolean>;
  /** Read authenticated context from /api/v1/context. */
  readonly refreshContext: () => Promise<boolean>;
  /** Retrieve memory through the real memory API. */
  readonly retrieveMemory: (query: string, agentId?: string) => Promise<boolean>;
  /** Create a workflow run via Public API. */
  readonly createRun: (workflowId: string, version?: string) => Promise<string | null>;
  /** Dispatch an existing run (confirm after preview when required). */
  readonly dispatchRun: (runId: string, confirm?: boolean) => Promise<boolean>;
  /** Create a run then dispatch it (canvas / composer run path). */
  readonly createAndDispatchRun: (
    workflowId: string,
    version?: string,
  ) => Promise<boolean>;
  /** Run an evaluation campaign via Public API. */
  readonly runEvaluation: (configuration?: Record<string, unknown>) => Promise<boolean>;
  /** Load workflow topology into the canvas footer. */
  readonly loadTopology: (workflowId: string) => Promise<boolean>;
}

function mintKey(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") return globalThis.crypto.randomUUID();
  return `ui-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export function useInteractionRuntime(): InteractionRuntime {
  const [status, setStatus] = useState<InteractionStatus>({ kind: "idle", message: "" });
  const api = useMemo(() => createPublicApiClient(), []);
  const operator = useMemo(() => createOperatorApi(), []);

  const setInfo = useCallback((message: string): void => {
    setStatus({ kind: "info", message });
  }, []);
  const setError = useCallback((message: string, correlationId?: string): void => {
    setStatus({
      kind: "error",
      message,
      ...(correlationId === undefined ? {} : { correlationId }),
    });
  }, []);
  const setSuccess = useCallback((message: string, correlationId?: string): void => {
    setStatus({
      kind: "success",
      message,
      ...(correlationId === undefined ? {} : { correlationId }),
    });
  }, []);
  const clearStatus = useCallback((): void => {
    setStatus({ kind: "idle", message: "" });
  }, []);

  const replaceScreen = useCallback(<K extends ScreenParameterKey>(
    key: K,
    view: ScreenParameterMap[K],
  ): void => {
    setScreenParameters(key, view);
  }, []);

  const patchScreen = useCallback(<K extends ScreenParameterKey>(
    key: K,
    patch: Partial<ScreenParameterMap[K]>,
  ): ScreenParameterMap[K] => updateScreenParameters(key, patch), []);

  const requestGenerated = useCallback(async <TId extends GeneratedOperationId>(
    operationId: TId,
    request: GeneratedOperationRequest<TId>,
    options: { readonly idempotencyKey?: string; readonly successMessage?: string } = {},
  ): Promise<boolean> => {
    setStatus({ kind: "busy", message: "Request in progress…" });
    const headers = options.idempotencyKey === undefined
      ? undefined
      : { "Idempotency-Key": options.idempotencyKey };
    const result = await api.request(operationId, request, headers === undefined ? {} : { headers });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    setSuccess(
      options.successMessage ?? "Request completed.",
      result.correlationId,
    );
    return true;
  }, [api, setError, setSuccess]);

  const inspectRun = useCallback(async (runId: string): Promise<boolean> => {
    const trimmed = runId.trim();
    if (trimmed.length === 0) {
      setError("Enter a run id.");
      return false;
    }
    setStatus({ kind: "busy", message: "Loading run projection…" });
    try {
      const [run, graph] = await Promise.all([
        operator.getRun(trimmed),
        operator.getGraphState(trimmed),
      ]);
      const monitoring = getScreenParameters("monitoring");
      patchScreen("monitoring", {
        traceMeta: `Run ${run.run_id} · ${run.status} · graph ${graph.status}`,
        footerNote: `Last live inspect: ${run.run_id} · corr ${run.correlation_id} · as_of ${run.updated_at} · ${monitoring.footerNote}`,
      });
      setSuccess(`Loaded run ${run.run_id} (${run.status}).`, run.correlation_id);
      return true;
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Run inspection failed.");
      return false;
    }
  }, [operator, patchScreen, setError, setSuccess]);

  const loadApproval = useCallback(async (approvalId: string): Promise<boolean> => {
    const trimmed = approvalId.trim();
    if (trimmed.length === 0) {
      setError("Enter an approval id.");
      return false;
    }
    setStatus({ kind: "busy", message: "Loading approval gate…" });
    try {
      const gate = await operator.getApprovalGate(trimmed);
      const current = getScreenParameters("approval");
      setScreenParameters("approval", {
        ...current,
        approval_id: gate.approval_id,
        run_id: gate.run_id,
        risk_tier: gate.risk_tier,
        gate_status: gate.gate_status,
        created_at: gate.created_at,
        state_label: gate.gate_status,
        pending_operation: gate.action_preview.summary,
        action_preview: {
          action_id: gate.action_preview.action_id,
          summary: gate.action_preview.summary,
          intended_effect: gate.action_preview.intended_effect,
          emitted_at: gate.action_preview.emitted_at,
          rollback_preview: gate.action_preview.rollback_preview,
          supporting_evidence: [...gate.action_preview.supporting_evidence],
          confidence: gate.action_preview.confidence,
          uncertainty: gate.action_preview.uncertainty,
          correction_control: gate.action_preview.correction_control,
        },
      });
      setSuccess(`Loaded approval ${gate.approval_id} (${gate.gate_status}).`);
      return true;
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Approval load failed.");
      return false;
    }
  }, [operator, setError, setSuccess]);

  const decideApproval = useCallback(async (
    approvalId: string,
    value: "approved" | "denied",
    reason: string,
    idempotencyKey?: string,
  ): Promise<boolean> => {
    const trimmed = approvalId.trim();
    if (trimmed.length === 0) {
      setError("Enter an approval id.");
      return false;
    }
    if (reason.trim().length === 0) {
      setError("A decision reason is required.");
      return false;
    }
    setStatus({ kind: "busy", message: "Submitting approval decision…" });
    try {
      const decision = await operator.submitApprovalDecision(
        trimmed,
        value,
        reason,
        { idempotencyKey: idempotencyKey ?? mintKey() },
      );
      setSuccess(
        `Decision recorded: ${decision.selected_value} · gate ${decision.gate_status}.`,
      );
      return true;
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Approval decision failed.");
      return false;
    }
  }, [operator, setError, setSuccess]);

  const refreshContext = useCallback(async (): Promise<boolean> => {
    setStatus({ kind: "busy", message: "Refreshing authenticated context…" });
    const result = await api.request("read_authenticated_context_api_v1_context_get", {
      path: {},
    });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    setSuccess(
      `Context actor=${result.data.actor_id} org=${result.data.organization_id}.`,
      result.correlationId,
    );
    return true;
  }, [api, setError, setSuccess]);

  const retrieveMemory = useCallback(async (query: string): Promise<boolean> => {
    const q = query.trim();
    if (q.length === 0) {
      setError("Enter a retrieval query.");
      return false;
    }
    setStatus({ kind: "busy", message: "Retrieving memory…" });
    const result = await api.request("retrieve_memory_api_v1_memory_retrieve_post", {
      path: {},
      body: { query: q },
    });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    const count = result.data.results.length;
    const knowledge = getScreenParameters("knowledge");
    patchScreen("knowledge", {
      searchResultNote: result.data.no_knowledge
        ? "No knowledge returned for this query."
        : `Retrieved ${count} reference(s) at ${result.data.retrieved_at}.`,
      footerNote: `Last retrieval corr ${result.data.correlation_id} · ${knowledge.footerNote}`,
    });
    setSuccess(
      result.data.no_knowledge
        ? "Memory retrieve: no knowledge."
        : `Memory retrieve returned ${count} result(s).`,
      result.correlationId ?? result.data.correlation_id,
    );
    return true;
  }, [api, patchScreen, setError, setSuccess]);

  const createRun = useCallback(async (
    workflowId: string,
    version = "1",
  ): Promise<string | null> => {
    const wf = workflowId.trim();
    if (wf.length === 0) {
      setError("workflow_id is required to create a run.");
      return null;
    }
    setStatus({ kind: "busy", message: "Creating workflow run…" });
    const result = await api.request("create_run_api_v1_workflows__workflow_id__run_post", {
      path: { workflow_id: wf },
      body: { version },
    });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return null;
    }
    setSuccess(
      `Created run ${result.data.run_id} (${result.data.status}).`,
      result.correlationId ?? result.data.correlation_id,
    );
    return result.data.run_id;
  }, [api, setError, setSuccess]);

  const dispatchRun = useCallback(async (
    runId: string,
    confirm = true,
  ): Promise<boolean> => {
    const id = runId.trim();
    if (id.length === 0) {
      setError("run_id is required to dispatch.");
      return false;
    }
    setStatus({ kind: "busy", message: "Dispatching run…" });
    const key = mintKey();
    const result = await api.request(
      "dispatch_run_api_v1_workflow_runs_dispatch_post",
      {
        path: {},
        body: { run_id: id, idempotency_key: key, confirm },
      },
      { headers: { "Idempotency-Key": key } },
    );
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    setSuccess(
      `Dispatch ${result.data.executed ? "executed" : "preview"} · ${result.data.status} · run ${result.data.run_id}.`,
      result.correlationId,
    );
    return true;
  }, [api, setError, setSuccess]);

  const createAndDispatchRun = useCallback(async (
    workflowId: string,
    version = "1",
  ): Promise<boolean> => {
    const runId = await createRun(workflowId, version);
    if (runId === null) return false;
    return dispatchRun(runId, true);
  }, [createRun, dispatchRun]);

  const runEvaluation = useCallback(async (
    configuration: Record<string, unknown> = {},
  ): Promise<boolean> => {
    setStatus({ kind: "busy", message: "Running evaluation…" });
    const result = await api.request("run_evaluation_api_v1_evaluations_post", {
      path: {},
      body: { configuration: configuration as never },
    });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    patchScreen("eval", {
      footerNote: `Last eval ${result.data.evaluation_run_id} · results ${result.data.result_count} · completed ${result.data.completed} · ${result.data.completed_at}`,
    });
    setSuccess(
      `Evaluation ${result.data.evaluation_run_id}: ${result.data.result_count} result(s).`,
      result.correlationId,
    );
    return true;
  }, [api, patchScreen, setError, setSuccess]);

  const loadTopology = useCallback(async (workflowId: string): Promise<boolean> => {
    const wf = workflowId.trim();
    if (wf.length === 0) {
      setError("workflow_id is required for topology.");
      return false;
    }
    setStatus({ kind: "busy", message: "Loading topology…" });
    const result = await api.request("read_topology_api_v1_workflows__workflow_id__topology_get", {
      path: { workflow_id: wf },
    });
    if (!result.ok) {
      setError(result.message, result.correlationId);
      return false;
    }
    patchScreen("canvas", {
      footerNote: `Topology ${result.data.workflow_id}@${result.data.version} · ${result.data.nodes.length} nodes · ${result.data.edges.length} edges · pattern ${result.data.pattern}`,
    });
    setSuccess(
      `Loaded topology for ${result.data.workflow_id} (${result.data.nodes.length} nodes).`,
      result.correlationId,
    );
    return true;
  }, [api, patchScreen, setError, setSuccess]);

  return {
    status,
    busy: status.kind === "busy",
    api,
    operator,
    setInfo,
    setError,
    setSuccess,
    clearStatus,
    replaceScreen,
    patchScreen,
    requestGenerated,
    inspectRun,
    loadApproval,
    decideApproval,
    refreshContext,
    retrieveMemory,
    createRun,
    dispatchRun,
    createAndDispatchRun,
    runEvaluation,
    loadTopology,
  };
}
