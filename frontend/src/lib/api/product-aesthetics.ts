/**
 * Host aesthetics client (offline Critic / Aligner / Taste-Keeper foundation).
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

export type AestheticEvaluateSuccess = {
  readonly ok: true;
  readonly aestheticQuality: number;
  readonly hackLikelihood: number;
  readonly topFailing: readonly string[];
  readonly critiques: readonly string[];
  readonly escalateToHitl?: boolean;
  readonly verdictMarkdown?: string;
};

export type AestheticFail = { readonly ok: false; readonly message: string };

export async function evaluateAesthetics(
  artifactRef: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly mode?: string;
    readonly mediaType?: string;
    readonly profileId?: string;
    readonly shotIntentText?: string;
  } = {},
): Promise<AestheticEvaluateSuccess | AestheticFail> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/aesthetics/evaluate", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        artifact_ref: artifactRef,
        mode: options.mode ?? "score",
        media_type: options.mediaType ?? "image",
        profile_id: options.profileId ?? null,
        intent: {
          shot_intent_text: options.shotIntentText ?? "",
        },
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      verdict?: {
        aesthetic_quality?: number;
        hack_likelihood?: number;
        top_failing_dimensions?: string[];
        actionable_critique?: string[];
        escalate_to_hitl?: boolean;
      };
      verdict_markdown?: string;
    }>(await response.json());
    const v = data.verdict ?? {};
    return {
      ok: true,
      aestheticQuality: v.aesthetic_quality ?? 0,
      hackLikelihood: v.hack_likelihood ?? 0,
      topFailing: v.top_failing_dimensions ?? [],
      critiques: v.actionable_critique ?? [],
      escalateToHitl: v.escalate_to_hitl,
      verdictMarkdown: data.verdict_markdown,
    };
  } catch {
    return { ok: false, message: "Network error calling aesthetics evaluate." };
  }
}

export async function compareAesthetics(
  candidates: readonly string[],
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly mediaType?: string;
    readonly profileId?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly bestArtifactRef: string;
      readonly ranking: readonly {
        readonly artifactRef: string;
        readonly aestheticQuality: number;
      }[];
    }
  | AestheticFail
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/aesthetics/compare", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        candidates: [...candidates],
        media_type: options.mediaType ?? "image",
        profile_id: options.profileId ?? null,
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      best_artifact_ref?: string;
      ranking?: { artifact_ref?: string; aesthetic_quality?: number }[];
    }>(await response.json());
    return {
      ok: true,
      bestArtifactRef: data.best_artifact_ref ?? "",
      ranking: (data.ranking ?? []).map((r) => ({
        artifactRef: r.artifact_ref ?? "",
        aestheticQuality: r.aesthetic_quality ?? 0,
      })),
    };
  } catch {
    return { ok: false, message: "Network error calling aesthetics compare." };
  }
}

export async function fetchAestheticsPolicy(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly liveVision: boolean;
      readonly productionMedia: boolean;
      readonly modes: readonly string[];
    }
  | AestheticFail
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/aesthetics/policy", {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      activation_policy?: { live_vision?: boolean; production_media?: boolean };
      modes?: string[];
    }>(await response.json());
    return {
      ok: true,
      liveVision: data.activation_policy?.live_vision ?? false,
      productionMedia: data.activation_policy?.production_media ?? false,
      modes: data.modes ?? [],
    };
  } catch {
    return { ok: false, message: "Network error calling aesthetics policy." };
  }
}

export async function attachAestheticHandoff(
  handoff: Record<string, unknown>,
  verdict: Record<string, unknown>,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | { readonly ok: true; readonly qcStatus: string; readonly handoff: Record<string, unknown> }
  | AestheticFail
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/aesthetics/handoff/attach", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({ handoff, verdict }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      handoff?: { qc_status?: string } & Record<string, unknown>;
    }>(await response.json());
    const h = data.handoff ?? {};
    return {
      ok: true,
      qcStatus: String(h.qc_status ?? ""),
      handoff: h,
    };
  } catch {
    return { ok: false, message: "Network error calling aesthetics handoff attach." };
  }
}
