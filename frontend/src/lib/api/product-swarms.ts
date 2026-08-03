/**
 * Browser client for product façade swarm drafts (/api/v1/swarms/*).
 * Used by Registry "Add to Swarm" — Host issues/consumes action references.
 *
 * Note: façade swarms are process-local (in-memory). Backend restart clears them.
 */

import { fetchCommonAgent } from "./product-commons";

export type AddAgentToSwarmResult =
  | {
      readonly ok: true;
      readonly swarmId: string;
      readonly swarmName: string;
      readonly revision: number;
      readonly nodeId: string;
      readonly agentId: string;
      readonly createdSwarm: boolean;
    }
  | { readonly ok: false; readonly message: string };

export type SwarmListItem = {
  readonly id: string;
  readonly name: string;
  readonly status: string;
  readonly revision: number;
  readonly memberCount: number;
  readonly lastRunId: string | null;
  readonly updatedAt: string;
  readonly createdAt: string;
};

export type SwarmDetail = {
  readonly id: string;
  readonly name: string;
  readonly status: string;
  readonly revision: number;
  readonly patternRef: string | null;
  readonly members: readonly {
    readonly nodeId: string;
    readonly agentId: string;
    readonly agentVersion: string;
  }[];
  readonly nodes: readonly {
    readonly id: string;
    readonly kind: string;
    readonly agentId?: string;
    readonly agentVersion?: string;
  }[];
};

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

function idempotencyKey(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${prefix}-${Date.now()}`;
}

async function parseErrorDetail(
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

/**
 * List organization-owned swarms (including drafts). Empty after backend restart.
 */
export async function listSwarms(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | { readonly ok: true; readonly items: readonly SwarmListItem[] }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/swarms", {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return { ok: false, message: `Could not list swarms: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      items?: readonly {
        id?: string;
        name?: string;
        status?: string;
        revision?: number;
        member_count?: number;
        last_run_id?: string | null;
        updated_at?: string;
        created_at?: string;
      }[];
    }>(raw);
    const items = (data.items ?? [])
      .filter((row): row is NonNullable<typeof row> & { id: string } =>
        Boolean(row.id),
      )
      .map((row) => ({
        id: row.id,
        name: row.name ?? row.id,
        status: row.status ?? "draft",
        revision: row.revision ?? 0,
        memberCount: row.member_count ?? 0,
        lastRunId: row.last_run_id ?? null,
        updatedAt: row.updated_at ?? "",
        createdAt: row.created_at ?? "",
      }));
    return { ok: true, items };
  } catch {
    return {
      ok: false,
      message:
        "Could not reach Host swarms list. Start backend and set BACKEND_API_ORIGIN.",
    };
  }
}

/**
 * Read one swarm draft (graph + members). 403/missing when not in this Host process.
 */
export async function getSwarm(
  swarmId: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | { readonly ok: true; readonly swarm: SwarmDetail }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const id = swarmId.trim();
  if (!id) {
    return { ok: false, message: "swarmId is required." };
  }
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(id)}`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return {
        ok: false,
        message:
          response.status === 403 || response.status === 404
            ? `Swarm ${id} was not found on this Host. Drafts are in-memory — restart or a different backend process loses them. Create again via Registry → Add to Swarm.`
            : `Could not load swarm ${id}: ${detail}`,
      };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      id?: string;
      name?: string;
      status?: string;
      revision?: number;
      pattern_ref?: string | null;
      members?: readonly {
        node_id?: string;
        agent_id?: string;
        agent_version?: string;
      }[];
      nodes?: readonly {
        id?: string;
        kind?: string;
        common_agent?: { id?: string; version?: string };
      }[];
    }>(raw);
    const swarmIdResolved = data.id ?? id;
    return {
      ok: true,
      swarm: {
        id: swarmIdResolved,
        name: data.name ?? swarmIdResolved,
        status: data.status ?? "draft",
        revision: data.revision ?? 0,
        patternRef: data.pattern_ref ?? null,
        members: (data.members ?? []).map((m) => ({
          nodeId: m.node_id ?? "",
          agentId: m.agent_id ?? "",
          agentVersion: m.agent_version ?? "current",
        })),
        nodes: (data.nodes ?? []).map((n) => ({
          id: n.id ?? "",
          kind: n.kind ?? "common_agent",
          agentId: n.common_agent?.id,
          agentVersion: n.common_agent?.version,
        })),
      },
    };
  } catch {
    return {
      ok: false,
      message: `Network error loading swarm ${id}. Is the backend running?`,
    };
  }
}

/**
 * Create an organization draft swarm (Host may issue compose action when none provided).
 */
export async function createSwarmDraft(
  options: {
    readonly name: string;
    readonly goalSummary?: string;
    readonly fetchImpl?: typeof fetch;
  },
): Promise<
  | {
      readonly ok: true;
      readonly swarmId: string;
      readonly revision: number;
      readonly status: string;
      readonly name: string;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/swarms", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
        "Idempotency-Key": idempotencyKey("swarm-create"),
      },
      body: JSON.stringify({
        name: options.name,
        ...(options.goalSummary
          ? { goal_summary: options.goalSummary }
          : {}),
      }),
    });
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return {
        ok: false,
        message: `Could not create swarm draft: ${detail}`,
      };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      swarm_id?: string;
      revision?: number;
      status?: string;
      name?: string;
    }>(raw);
    if (!data.swarm_id) {
      return { ok: false, message: "Host response missing swarm_id." };
    }
    return {
      ok: true,
      swarmId: data.swarm_id,
      revision: data.revision ?? 0,
      status: data.status ?? "draft",
      name: data.name ?? options.name,
    };
  } catch {
    return {
      ok: false,
      message:
        "Could not reach Host swarms API. Start backend and set BACKEND_API_ORIGIN.",
    };
  }
}

/**
 * Registry "Add to Swarm": issue/consume Host add_to_swarm action and attach
 * the common agent as a graph member node.
 *
 * - If `swarmId` is set: add into that existing draft.
 * - Else: create a new draft, then add the agent.
 *
 * Does not invent action ids; does not activate production.
 */
export async function addAgentToSwarmDraft(
  agentId: string,
  options: {
    readonly swarmId?: string;
    readonly swarmName?: string;
    readonly agentVersion?: string;
    readonly fetchImpl?: typeof fetch;
  } = {},
): Promise<AddAgentToSwarmResult> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);

  const agent = await fetchCommonAgent(agentId, fetchImpl);
  if (!agent.ok) {
    return agent;
  }
  const addAction = agent.actions.find(
    (a) => a.kind === "add_to_swarm" && a.eligible,
  );
  if (!addAction) {
    return {
      ok: false,
      message:
        "Host returned no eligible add_to_swarm action for this agent. " +
        "Ensure backend product façade is running with local trust.",
    };
  }

  let swarmId = options.swarmId?.trim() || "";
  let swarmName = options.swarmName?.trim() || "";
  let createdSwarm = false;
  let baseRevision = 0;

  if (!swarmId) {
    const draftName = swarmName || `Draft with ${agentId}`;
    const created = await createSwarmDraft({
      name: draftName,
      goalSummary: `Registry Add to Swarm: ${agentId}`,
      fetchImpl,
    });
    if (!created.ok) {
      return created;
    }
    swarmId = created.swarmId;
    swarmName = created.name;
    baseRevision = created.revision;
    createdSwarm = true;
  } else if (!swarmName) {
    swarmName = swarmId;
  }

  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/members`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          "Idempotency-Key": idempotencyKey("swarm-member"),
        },
        body: JSON.stringify({
          action_reference_id: addAction.id,
          agent_id: agentId,
          agent_version: options.agentVersion ?? "current",
          pin_policy: "exact",
        }),
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return {
        ok: false,
        message: createdSwarm
          ? `Swarm ${swarmId} was created, but adding ${agentId} failed: ${detail}`
          : `Could not add ${agentId} to swarm ${swarmId}: ${detail}`,
      };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      swarm_id?: string;
      revision?: number;
      node_id?: string;
      member?: { agent_id?: string };
    }>(raw);
    return {
      ok: true,
      swarmId: data.swarm_id ?? swarmId,
      swarmName,
      revision: data.revision ?? baseRevision + 1,
      nodeId: data.node_id ?? `node_${agentId.replace(/\./g, "_")}`,
      agentId: data.member?.agent_id ?? agentId,
      createdSwarm,
    };
  } catch {
    return {
      ok: false,
      message: createdSwarm
        ? `Swarm ${swarmId} was created, but network error while adding ${agentId}.`
        : `Network error while adding ${agentId} to swarm ${swarmId}.`,
    };
  }
}
