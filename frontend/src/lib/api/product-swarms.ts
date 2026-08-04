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
  /** Host product spine attached (Epic C/E). */
  readonly hasSpine?: boolean;
  readonly spineStatus?: string | null;
  readonly spineWorkflowId?: string | null;
  readonly briefId?: string | null;
};

export type SwarmSpineStep = {
  readonly id: string;
  readonly agentId: string;
  readonly status: string;
  readonly artifactRef: string | null;
  readonly humanGateRequired: boolean;
  readonly note: string | null;
  readonly stubTool: string | null;
};

export type SwarmSpine = {
  readonly workflowId: string;
  readonly status: string;
  readonly productionReady: false;
  readonly mode: string;
  readonly approvalId: string | null;
  readonly note: string;
  readonly steps: readonly SwarmSpineStep[];
  readonly artifacts: Readonly<
    Record<
      string,
      {
        readonly ref: string;
        readonly kind: string;
        readonly stepId: string;
        readonly summary: string;
        readonly stub: true;
      }
    >
  >;
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
  readonly actions: readonly {
    readonly id: string;
    readonly kind: string;
    readonly label: string;
  }[];
  readonly brief: {
    readonly briefId: string;
    readonly text: string;
    readonly locale: string;
    readonly scaleProfile: string | null;
    readonly archetype: string | null;
  } | null;
  readonly spine: SwarmSpine | null;
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
        has_spine?: boolean;
        spine_status?: string | null;
        spine_workflow_id?: string | null;
        brief_id?: string | null;
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
        hasSpine: Boolean(row.has_spine),
        spineStatus: row.spine_status ?? null,
        spineWorkflowId: row.spine_workflow_id ?? null,
        briefId: row.brief_id ?? null,
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
      actions?: readonly {
        id?: string;
        kind?: string;
        label?: string;
      }[];
      brief?: {
        brief_id?: string;
        text?: string;
        locale?: string;
        scale_profile?: string | null;
        archetype?: string | null;
      } | null;
      spine?: {
        workflow_id?: string;
        status?: string;
        mode?: string;
        approval_id?: string | null;
        note?: string;
        steps?: readonly {
          id?: string;
          agent_id?: string;
          status?: string;
          artifact_ref?: string | null;
          human_gate_required?: boolean;
          note?: string | null;
          stub_tool?: string | null;
        }[];
        artifacts?: Record<
          string,
          {
            ref?: string;
            kind?: string;
            step_id?: string;
            summary?: string;
            stub?: boolean;
          }
        >;
      } | null;
    }>(raw);
    const swarmIdResolved = data.id ?? id;
    const spineRaw = data.spine;
    const artifacts: SwarmSpine["artifacts"] = {};
    if (spineRaw?.artifacts) {
      for (const [ref, art] of Object.entries(spineRaw.artifacts)) {
        artifacts[ref] = {
          ref: art.ref ?? ref,
          kind: art.kind ?? "",
          stepId: art.step_id ?? "",
          summary: art.summary ?? "",
          stub: true,
        };
      }
    }
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
        actions: (data.actions ?? [])
          .filter((a) => Boolean(a.id && a.kind))
          .map((a) => ({
            id: a.id ?? "",
            kind: a.kind ?? "",
            label: a.label ?? a.kind ?? "",
          })),
        brief: data.brief
          ? {
              briefId: data.brief.brief_id ?? "",
              text: data.brief.text ?? "",
              locale: data.brief.locale ?? "en",
              scaleProfile: data.brief.scale_profile ?? null,
              archetype: data.brief.archetype ?? null,
            }
          : null,
        spine: spineRaw
          ? {
              workflowId: spineRaw.workflow_id ?? "wf_video_spine_v1",
              status: spineRaw.status ?? "ready",
              productionReady: false,
              mode: spineRaw.mode ?? "stub",
              approvalId: spineRaw.approval_id ?? null,
              note: spineRaw.note ?? "stub run · not production media",
              steps: (spineRaw.steps ?? []).map((s) => ({
                id: s.id ?? "",
                agentId: s.agent_id ?? "",
                status: s.status ?? "queued",
                artifactRef: s.artifact_ref ?? null,
                humanGateRequired: Boolean(s.human_gate_required),
                note: s.note ?? null,
                stubTool: s.stub_tool ?? null,
              })),
              artifacts,
            }
          : null,
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
 * Advance one video spine stub step (requires Host action reference).
 */
export async function runSpineStep(
  swarmId: string,
  actionReferenceId: string,
  options: {
    readonly stepId?: string;
    readonly fetchImpl?: typeof fetch;
  } = {},
): Promise<
  | { readonly ok: true; readonly spine: SwarmSpine | null; readonly approvalId: string | null }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/spine/steps`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          action_reference_id: actionReferenceId,
          ...(options.stepId ? { step_id: options.stepId } : {}),
        }),
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(response, `HTTP ${response.status}`);
      return { ok: false, message: `Spine step failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      spine?: {
        workflow_id?: string;
        status?: string;
        mode?: string;
        approval_id?: string | null;
        note?: string;
        steps?: readonly {
          id?: string;
          agent_id?: string;
          status?: string;
          artifact_ref?: string | null;
          human_gate_required?: boolean;
          note?: string | null;
          stub_tool?: string | null;
        }[];
        artifacts?: Record<
          string,
          {
            ref?: string;
            kind?: string;
            step_id?: string;
            summary?: string;
          }
        >;
      };
      approval_id?: string | null;
    }>(raw);
    const spineRaw = data.spine;
    if (!spineRaw) {
      return { ok: true, spine: null, approvalId: data.approval_id ?? null };
    }
    const artifacts: SwarmSpine["artifacts"] = {};
    for (const [ref, art] of Object.entries(spineRaw.artifacts ?? {})) {
      artifacts[ref] = {
        ref: art.ref ?? ref,
        kind: art.kind ?? "",
        stepId: art.step_id ?? "",
        summary: art.summary ?? "",
        stub: true,
      };
    }
    return {
      ok: true,
      approvalId: data.approval_id ?? spineRaw.approval_id ?? null,
      spine: {
        workflowId: spineRaw.workflow_id ?? "wf_video_spine_v1",
        status: spineRaw.status ?? "ready",
        productionReady: false,
        mode: spineRaw.mode ?? "stub",
        approvalId: spineRaw.approval_id ?? null,
        note: spineRaw.note ?? "stub run · not production media",
        steps: (spineRaw.steps ?? []).map((s) => ({
          id: s.id ?? "",
          agentId: s.agent_id ?? "",
          status: s.status ?? "queued",
          artifactRef: s.artifact_ref ?? null,
          humanGateRequired: Boolean(s.human_gate_required),
          note: s.note ?? null,
          stubTool: s.stub_tool ?? null,
        })),
        artifacts,
      },
    };
  } catch {
    return { ok: false, message: "Network error running spine step." };
  }
}

/**
 * Human package gate decision (approve | denied).
 */
export async function decidePackageGate(
  swarmId: string,
  actionReferenceId: string,
  decision: "approved" | "denied",
  reason: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | { readonly ok: true; readonly status: string }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/spine/package-decision`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          action_reference_id: actionReferenceId,
          decision,
          reason,
        }),
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(response, `HTTP ${response.status}`);
      return { ok: false, message: `Package decision failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{ spine?: { status?: string } }>(raw);
    return { ok: true, status: data.spine?.status ?? decision };
  } catch {
    return { ok: false, message: "Network error on package decision." };
  }
}

/**
 * Dry-run advance stub spine until package human gate.
 */
export async function runSpineToPackage(
  swarmId: string,
  actionReferenceId: string,
  options: { readonly fetchImpl?: typeof fetch; readonly maxSteps?: number } = {},
): Promise<
  | {
      readonly ok: true;
      readonly stepsRun: number;
      readonly spine: SwarmSpine | null;
      readonly approvalId: string | null;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/spine/run-to-package`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          action_reference_id: actionReferenceId,
          max_steps: options.maxSteps ?? 12,
        }),
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(response, `HTTP ${response.status}`);
      return { ok: false, message: `Dry-run to package failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      steps_run?: number;
      approval_id?: string | null;
      spine?: {
        workflow_id?: string;
        status?: string;
        mode?: string;
        approval_id?: string | null;
        note?: string;
        steps?: readonly {
          id?: string;
          agent_id?: string;
          status?: string;
          artifact_ref?: string | null;
          human_gate_required?: boolean;
          note?: string | null;
          stub_tool?: string | null;
        }[];
        artifacts?: Record<
          string,
          { ref?: string; kind?: string; step_id?: string; summary?: string }
        >;
      };
    }>(raw);
    const spineRaw = data.spine;
    if (!spineRaw) {
      return {
        ok: true,
        stepsRun: data.steps_run ?? 0,
        spine: null,
        approvalId: data.approval_id ?? null,
      };
    }
    const artifacts: SwarmSpine["artifacts"] = {};
    for (const [ref, art] of Object.entries(spineRaw.artifacts ?? {})) {
      artifacts[ref] = {
        ref: art.ref ?? ref,
        kind: art.kind ?? "",
        stepId: art.step_id ?? "",
        summary: art.summary ?? "",
        stub: true,
      };
    }
    return {
      ok: true,
      stepsRun: data.steps_run ?? 0,
      approvalId: data.approval_id ?? spineRaw.approval_id ?? null,
      spine: {
        workflowId: spineRaw.workflow_id ?? "wf_video_spine_v1",
        status: spineRaw.status ?? "ready",
        productionReady: false,
        mode: spineRaw.mode ?? "stub",
        approvalId: spineRaw.approval_id ?? null,
        note: spineRaw.note ?? "stub run · not production media",
        steps: (spineRaw.steps ?? []).map((s) => ({
          id: s.id ?? "",
          agentId: s.agent_id ?? "",
          status: s.status ?? "queued",
          artifactRef: s.artifact_ref ?? null,
          humanGateRequired: Boolean(s.human_gate_required),
          note: s.note ?? null,
          stubTool: s.stub_tool ?? null,
        })),
        artifacts,
      },
    };
  } catch {
    return { ok: false, message: "Network error on spine dry-run." };
  }
}

/**
 * List redacted stub artifact handoffs for a spine draft.
 */
export async function listSwarmArtifacts(
  swarmId: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly items: readonly {
        readonly ref: string;
        readonly kind: string;
        readonly stepId: string;
        readonly summary: string;
        readonly stub: true;
      }[];
      readonly count: number;
      readonly note: string;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/artifacts`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(response, `HTTP ${response.status}`);
      return { ok: false, message: `Artifact list failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      items?: readonly {
        ref?: string;
        kind?: string;
        step_id?: string;
        summary?: string;
      }[];
      count?: number;
      note?: string;
    }>(raw);
    const items = (data.items ?? []).map((a) => ({
      ref: a.ref ?? "",
      kind: a.kind ?? "",
      stepId: a.step_id ?? "",
      summary: a.summary ?? "",
      stub: true as const,
    }));
    return {
      ok: true,
      items,
      count: data.count ?? items.length,
      note: data.note ?? "stub run · not production media",
    };
  } catch {
    return { ok: false, message: "Network error listing artifacts." };
  }
}

/**
 * Fetch redacted stub artifact by opaque ref.
 */
export async function getSwarmArtifact(
  swarmId: string,
  artifactRef: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly artifact: {
        readonly ref: string;
        readonly kind: string;
        readonly stepId: string;
        readonly summary: string;
        readonly stub: true;
        readonly note: string;
      };
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/swarms/${encodeURIComponent(swarmId)}/artifacts/${encodeURIComponent(artifactRef)}`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) {
      const detail = await parseErrorDetail(response, `HTTP ${response.status}`);
      return { ok: false, message: `Artifact load failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      ref?: string;
      kind?: string;
      step_id?: string;
      summary?: string;
      note?: string;
    }>(raw);
    return {
      ok: true,
      artifact: {
        ref: data.ref ?? artifactRef,
        kind: data.kind ?? "",
        stepId: data.step_id ?? "",
        summary: data.summary ?? "",
        stub: true,
        note: data.note ?? "stub run · not production media",
      },
    };
  } catch {
    return { ok: false, message: "Network error loading artifact." };
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
