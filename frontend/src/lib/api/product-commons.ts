/**
 * Browser client for product façade commons routes (/api/v1/commons/*).
 * Same-origin only; Host must be reachable via Next rewrite + trusted context.
 */

export type ProductActionReference = {
  readonly id: string;
  readonly label: string;
  readonly kind: string;
  readonly eligible: boolean;
  readonly resource_ref?: string | null;
};

export type ProposeAgentResult =
  | {
      readonly ok: true;
      readonly proposalId: string;
      readonly status: string;
      readonly targetId: string;
    }
  | { readonly ok: false; readonly message: string };

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

/**
 * Fetch agent projection (includes propose_improvement action references).
 */
export async function fetchCommonAgent(
  agentId: string,
  fetchImpl: typeof fetch = globalThis.fetch.bind(globalThis),
): Promise<
  | { readonly ok: true; readonly actions: readonly ProductActionReference[] }
  | { readonly ok: false; readonly message: string }
> {
  try {
    const response = await fetchImpl(
      `/api/v1/commons/agents/${encodeURIComponent(agentId)}`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) {
      return {
        ok: false,
        message:
          response.status === 401 || response.status === 403
            ? "Host denied agent read (auth). Ensure backend is running with local trust (CASOPS_DEV_TRUST=1) and BACKEND_API_ORIGIN is set."
            : `Could not load agent ${agentId} (HTTP ${response.status}).`,
      };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{ actions?: ProductActionReference[] }>(raw);
    const actions = Array.isArray(data.actions) ? data.actions : [];
    return { ok: true, actions };
  } catch {
    return {
      ok: false,
      message:
        "Could not reach Host commons API. Start backend and set BACKEND_API_ORIGIN on the frontend.",
    };
  }
}

export type StartRolloutResult =
  | {
      readonly ok: true;
      readonly rolloutId: string;
      readonly status: string;
      readonly type: string;
      readonly agentId: string;
      readonly baselineVersion: string;
      readonly candidateVersion: string;
      readonly productionActivation: boolean;
    }
  | { readonly ok: false; readonly message: string };

/**
 * Start a sandbox/canary A/B or safe rollout using a Host-issued action reference.
 * Never invents action ids; never claims production activation.
 */
export async function startAgentRollout(
  agentId: string,
  options: {
    readonly type: "ab_test" | "safe_rollout";
    readonly baselineVersion?: string;
    readonly candidateVersion?: string;
    readonly summary?: string;
    readonly fetchImpl?: typeof fetch;
  },
): Promise<StartRolloutResult> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const actionKind =
    options.type === "ab_test" ? "rollout.ab_test" : "rollout.safe_all";
  const agent = await fetchCommonAgent(agentId, fetchImpl);
  if (!agent.ok) {
    return agent;
  }
  const action = agent.actions.find(
    (a) => a.kind === actionKind && a.eligible,
  );
  if (!action) {
    return {
      ok: false,
      message: `Host returned no eligible ${actionKind} action for this agent.`,
    };
  }
  try {
    const response = await fetchImpl(
      `/api/v1/commons/agents/${encodeURIComponent(agentId)}/rollouts`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          "Idempotency-Key":
            typeof crypto !== "undefined" && "randomUUID" in crypto
              ? crypto.randomUUID()
              : `rollout-${Date.now()}`,
        },
        body: JSON.stringify({
          action_reference_id: action.id,
          type: options.type,
          baseline_version: options.baselineVersion ?? "current",
          candidate_version: options.candidateVersion ?? "candidate",
          summary:
            options.summary ??
            (options.type === "ab_test"
              ? `A/B canary for ${agentId}`
              : `Safe rollout canary for ${agentId}`),
        }),
      },
    );
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errBody = (await response.json()) as {
          error?: { message?: string };
          detail?: { message?: string };
        };
        detail =
          errBody.error?.message ?? errBody.detail?.message ?? detail;
      } catch {
        // keep detail
      }
      return { ok: false, message: `Rollout rejected: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      rollout_id?: string;
      status?: string;
      type?: string;
      agent_id?: string;
      baseline_version?: string;
      candidate_version?: string;
      production_activation?: boolean;
    }>(raw);
    if (!data.rollout_id) {
      return { ok: false, message: "Host response missing rollout_id." };
    }
    return {
      ok: true,
      rolloutId: data.rollout_id,
      status: data.status ?? "active_canary",
      type: data.type ?? options.type,
      agentId: data.agent_id ?? agentId,
      baselineVersion: data.baseline_version ?? "current",
      candidateVersion: data.candidate_version ?? "candidate",
      productionActivation: data.production_activation === true,
    };
  } catch {
    return {
      ok: false,
      message: "Network error while starting rollout on Host.",
    };
  }
}

/**
 * Submit improvement proposal using a Host-issued action reference.
 */
export async function proposeAgentImprovement(
  agentId: string,
  options: {
    readonly summary?: string;
    readonly fetchImpl?: typeof fetch;
  } = {},
): Promise<ProposeAgentResult> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const agent = await fetchCommonAgent(agentId, fetchImpl);
  if (!agent.ok) {
    return agent;
  }
  const propose = agent.actions.find(
    (a) => a.kind === "propose_improvement" && a.eligible,
  );
  if (!propose) {
    return {
      ok: false,
      message:
        "Host returned no eligible propose_improvement action for this agent.",
    };
  }
  try {
    const response = await fetchImpl(
      `/api/v1/commons/agents/${encodeURIComponent(agentId)}/proposals`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          "Idempotency-Key":
            typeof crypto !== "undefined" && "randomUUID" in crypto
              ? crypto.randomUUID()
              : `propose-${Date.now()}`,
        },
        body: JSON.stringify({
          action_reference_id: propose.id,
          base_version: "current",
          summary:
            options.summary ??
            `Improvement proposal for ${agentId} (submitted from console).`,
          evidence_refs: [],
        }),
      },
    );
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errBody = (await response.json()) as {
          error?: { message?: string };
          detail?: { message?: string };
        };
        detail =
          errBody.error?.message ??
          errBody.detail?.message ??
          detail;
      } catch {
        // keep detail
      }
      return {
        ok: false,
        message: `Proposal rejected: ${detail}`,
      };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      proposal_id?: string;
      status?: string;
      target_id?: string;
    }>(raw);
    if (!data.proposal_id) {
      return { ok: false, message: "Host response missing proposal_id." };
    }
    return {
      ok: true,
      proposalId: data.proposal_id,
      status: data.status ?? "submitted",
      targetId: data.target_id ?? agentId,
    };
  } catch {
    return {
      ok: false,
      message: "Network error while submitting proposal to Host.",
    };
  }
}
