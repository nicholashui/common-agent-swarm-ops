/**
 * Host agent-loop fleet client (offline Plan→Act→Self-Review).
 */

function unwrapData<T>(payload: unknown): T {
  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    "meta" in payload
  ) {
    return (payload as { data: T }).data;
  }
  return payload as T;
}

async function parseError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const errBody = (await response.json()) as {
      error?: { message?: string };
      detail?: { message?: string };
    };
    return errBody.error?.message ?? errBody.detail?.message ?? fallback;
  } catch {
    return fallback;
  }
}

export async function fetchAgentLoopInventory(
  options: { readonly fetchImpl?: typeof fetch; readonly refresh?: boolean } = {},
): Promise<
  | {
      readonly ok: true;
      readonly totalAgents: number;
      readonly loopCapable: number;
      readonly items: readonly { readonly agentId: string; readonly loopCapable: boolean }[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const q = options.refresh ? "?refresh=true" : "";
  try {
    const response = await fetchImpl(`/api/v1/agent-loops/inventory${q}`, {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      total_agents?: number;
      loop_capable?: number;
      items?: readonly { agent_id?: string; loop_capable?: boolean }[];
    }>(await response.json());
    return {
      ok: true,
      totalAgents: data.total_agents ?? 0,
      loopCapable: data.loop_capable ?? 0,
      items: (data.items ?? []).map((i) => ({
        agentId: i.agent_id ?? "",
        loopCapable: Boolean(i.loop_capable),
      })),
    };
  } catch {
    return { ok: false, message: "Could not load agent-loop inventory." };
  }
}

export async function runSwarmMemberLoops(
  swarmId: string,
  actionReferenceId: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly agentIds?: readonly string[];
    readonly goal?: string;
  } = {},
): Promise<
  | { readonly ok: true; readonly passed: number; readonly failed: number; readonly completed: number }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/agent-loops`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          action_reference_id: actionReferenceId,
          ...(options.goal ? { goal: options.goal } : {}),
          ...(options.agentIds ? { agent_ids: options.agentIds } : {}),
        }),
      },
    );
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      crew?: { passed?: number; failed?: number; completed?: number };
    }>(await response.json());
    return {
      ok: true,
      passed: data.crew?.passed ?? 0,
      failed: data.crew?.failed ?? 0,
      completed: data.crew?.completed ?? 0,
    };
  } catch {
    return { ok: false, message: "Network error running member loops." };
  }
}

export async function fetchAgentLoopTools(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly mediaLiveEnv: boolean;
      readonly tools: readonly { readonly toolId: string; readonly activeMode: string }[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/agent-loops/tools", {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      media_live_env?: boolean;
      tools?: readonly { tool_id?: string; active_mode?: string }[];
    }>(await response.json());
    return {
      ok: true,
      mediaLiveEnv: Boolean(data.media_live_env),
      tools: (data.tools ?? []).map((t) => ({
        toolId: t.tool_id ?? "",
        activeMode: t.active_mode ?? "stub",
      })),
    };
  } catch {
    return { ok: false, message: "Could not load tool catalog." };
  }
}

export async function runWorkflowLoops(
  workflowId: string,
  goal: string,
  options: { readonly fetchImpl?: typeof fetch; readonly maxNodes?: number } = {},
): Promise<
  | {
      readonly ok: true;
      readonly passed: number;
      readonly failed: number;
      readonly completed: number;
      readonly workflowId: string;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/agent-loops/workflows/${encodeURIComponent(workflowId)}/run`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          goal,
          max_nodes: options.maxNodes ?? 16,
          stop_on_failure: false,
        }),
      },
    );
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      workflow_id?: string;
      passed?: number;
      failed?: number;
      completed?: number;
    }>(await response.json());
    return {
      ok: true,
      workflowId: data.workflow_id ?? workflowId,
      passed: data.passed ?? 0,
      failed: data.failed ?? 0,
      completed: data.completed ?? 0,
    };
  } catch {
    return { ok: false, message: "Network error running workflow loops." };
  }
}
