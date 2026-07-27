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
