/**
 * Host creative (GCA) client — offline SSOR-lite ideation + patterns.
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

async function parseError(response: Response, fallback: string): Promise<string> {
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

type IdeateCandidate = {
  candidate_id?: string;
  overall_cr?: number;
  ssor?: number;
  outlier_count?: number;
  outlier_dimensions?: unknown[];
};

type HandoffPayload = {
  best_candidate_id?: string;
  concept?: string;
  prompt_steer?: string;
  overall_cr?: number;
  next_agents?: string[];
  creative_direction?: { logline?: string; domain?: string };
};

export async function ideateCreative(
  brief: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly nCandidates?: number;
    readonly domain?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly candidateCount: number;
      readonly bestId: string;
      readonly logline: string;
      /** Offline SSOR-lite domain (video / scientific / …). */
      readonly domain: string;
      /** Top ranked overall creative score (overall_cr). */
      readonly topOverallCr: number;
      /** Outlier dimension count on the best candidate (≤4). */
      readonly topOutlierCount: number;
      /** Whether the Host returned a phase_trace audit list. */
      readonly hasPhaseTrace: boolean;
      /** Process-local learned pattern count (not durable memory). */
      readonly learnedPatternCount: number;
      /** Explicit next-agent handoff summary for Host orchestration. */
      readonly handoffBestId: string;
      readonly handoffPromptSteer: string;
      readonly handoffNextAgentCount: number;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const body: Record<string, unknown> = {
      brief,
      n_candidates: options.nCandidates ?? 4,
    };
    if (options.domain) {
      body.domain = options.domain;
    }
    const response = await fetchImpl("/api/v1/creative/ideate", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      candidates?: IdeateCandidate[];
      best_candidate_id?: string;
      creative_direction?: { logline?: string };
      domain?: string;
      phase_trace?: unknown[];
      learned_patterns?: unknown[];
      handoff?: HandoffPayload;
    }>(await response.json());
    const candidates = data.candidates ?? [];
    const best =
      candidates.find((c) => c.candidate_id === data.best_candidate_id) ?? candidates[0];
    const topOverallCr = Number(best?.overall_cr ?? best?.ssor ?? 0);
    const topOutlierCount = Number(
      best?.outlier_count ??
        (Array.isArray(best?.outlier_dimensions) ? best.outlier_dimensions.length : 0),
    );
    const handoff = data.handoff ?? {};
    return {
      ok: true,
      candidateCount: candidates.length,
      bestId: data.best_candidate_id ?? "",
      logline: data.creative_direction?.logline ?? "",
      domain: data.domain ?? "",
      topOverallCr,
      topOutlierCount,
      hasPhaseTrace: Array.isArray(data.phase_trace) && data.phase_trace.length > 0,
      learnedPatternCount: Array.isArray(data.learned_patterns)
        ? data.learned_patterns.length
        : 0,
      handoffBestId: handoff.best_candidate_id ?? data.best_candidate_id ?? "",
      handoffPromptSteer: handoff.prompt_steer ?? "",
      handoffNextAgentCount: Array.isArray(handoff.next_agents)
        ? handoff.next_agents.length
        : 0,
    };
  } catch {
    return { ok: false, message: "Network error calling creative ideate." };
  }
}

/** Lean process-local learned motifs (not full run history). */
export async function listCreativePatterns(
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly limit?: number;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly count: number;
      readonly scope: string;
      readonly motifs: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const limit = options.limit ?? 12;
  try {
    const response = await fetchImpl(`/api/v1/creative/patterns?limit=${limit}`, {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      count?: number;
      scope?: string;
      items?: Array<{ seed_motif?: string }>;
    }>(await response.json());
    const items = data.items ?? [];
    return {
      ok: true,
      count: Number(data.count ?? items.length),
      scope: data.scope ?? "process_local",
      motifs: items.map((i) => i.seed_motif ?? "").filter(Boolean),
    };
  } catch {
    return { ok: false, message: "Network error calling creative patterns." };
  }
}
