/**
 * AI-first composer client — Host picks pattern + agents.
 * Human only when decision_status === needs_hitl (requirement conflicts).
 */

export type ComposerSlot = {
  readonly id: string;
  readonly agentId: string;
  readonly label: string;
  readonly role: string;
  readonly version: string;
  readonly pack: string;
  readonly verified: boolean;
  readonly rationale: string;
};

export type ComposerOpenQuestion = {
  readonly id: string;
  readonly kind: string;
  readonly severity: string;
  readonly question: string;
  readonly options: readonly { readonly id: string; readonly label: string }[];
};

export type ComposerRecommendation = {
  readonly mode: "ai_pick";
  readonly decisionStatus: "ai_resolved" | "needs_hitl";
  readonly autoMaterialize: boolean;
  readonly goal: string;
  readonly pattern: {
    readonly id: string;
    readonly name: string;
    readonly versionLabel: string;
    readonly whenToUse: string;
    readonly rationale: string;
  } | null;
  readonly slots: readonly ComposerSlot[];
  readonly openQuestions: readonly ComposerOpenQuestion[];
  readonly procedureSteps: readonly string[];
  readonly note: string;
};

export type ComposerMaterializeResult =
  | {
      readonly ok: true;
      readonly decisionStatus: "ai_resolved";
      readonly swarmId: string;
      readonly name: string;
      readonly revision: number;
      readonly memberCount: number;
      readonly canvasPath: string;
      readonly recommendation: ComposerRecommendation;
    }
  | {
      readonly ok: true;
      readonly decisionStatus: "needs_hitl";
      readonly recommendation: ComposerRecommendation;
      readonly message: string;
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

type RawRecommendation = {
  mode?: string;
  decision_status?: string;
  auto_materialize?: boolean;
  goal?: string;
  pattern?: {
    id?: string;
    name?: string;
    version_label?: string;
    when_to_use?: string;
    rationale?: string;
  } | null;
  slots?: readonly {
    id?: string;
    agent_id?: string;
    label?: string;
    role?: string;
    version?: string;
    pack?: string;
    verified?: boolean;
    rationale?: string;
  }[];
  open_questions?: readonly {
    id?: string;
    kind?: string;
    severity?: string;
    question?: string;
    options?: readonly { id?: string; label?: string }[];
  }[];
  procedure_steps?: readonly string[];
  note?: string;
};

function mapRecommendation(raw: RawRecommendation): ComposerRecommendation {
  const status =
    raw.decision_status === "needs_hitl" ? "needs_hitl" : "ai_resolved";
  return {
    mode: "ai_pick",
    decisionStatus: status,
    autoMaterialize: Boolean(raw.auto_materialize) && status === "ai_resolved",
    goal: raw.goal ?? "",
    pattern: raw.pattern
      ? {
          id: raw.pattern.id ?? "",
          name: raw.pattern.name ?? "AI pattern",
          versionLabel: raw.pattern.version_label ?? "1.0",
          whenToUse: raw.pattern.when_to_use ?? "",
          rationale: raw.pattern.rationale ?? "",
        }
      : null,
    slots: (raw.slots ?? [])
      .filter((s) => Boolean(s.agent_id))
      .map((s) => ({
        id: s.id ?? s.agent_id ?? "",
        agentId: s.agent_id ?? "",
        label: s.label ?? s.agent_id ?? "",
        role: s.role ?? "",
        version: s.version ?? "current",
        pack: s.pack ?? "",
        verified: Boolean(s.verified),
        rationale: s.rationale ?? "AI-selected",
      })),
    openQuestions: (raw.open_questions ?? [])
      .filter((q) => Boolean(q.id && q.question))
      .map((q) => ({
        id: q.id ?? "",
        kind: q.kind ?? "requirement_conflict",
        severity: q.severity ?? "blocker",
        question: q.question ?? "",
        options: (q.options ?? [])
          .filter((o) => Boolean(o.id))
          .map((o) => ({ id: o.id ?? "", label: o.label ?? o.id ?? "" })),
      })),
    procedureSteps: raw.procedure_steps ?? [],
    note: raw.note ?? "",
  };
}

/**
 * Host AI-picks pattern + agents, or returns open_questions when blocked.
 */
export async function recommendComposition(
  goal: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly maxSlots?: number;
    readonly humanResolutions?: Readonly<Record<string, string>>;
  } = {},
): Promise<
  | { readonly ok: true; readonly recommendation: ComposerRecommendation }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const trimmed = goal.trim();
  if (!trimmed) {
    return { ok: false, message: "Enter a goal/spec — AI picks the crew." };
  }
  try {
    const response = await fetchImpl("/api/v1/composer/recommend", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        goal: trimmed,
        max_slots: options.maxSlots ?? 8,
        human_resolutions: options.humanResolutions ?? {},
      }),
    });
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return { ok: false, message: `AI recommend failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<RawRecommendation>(raw);
    const recommendation = mapRecommendation(data);
    if (
      recommendation.decisionStatus === "ai_resolved" &&
      recommendation.slots.length === 0
    ) {
      return { ok: false, message: "AI returned no agent slots." };
    }
    return { ok: true, recommendation };
  } catch {
    return {
      ok: false,
      message:
        "Could not reach Host composer. Start backend and set BACKEND_API_ORIGIN.",
    };
  }
}

/**
 * AI materialize, or needs_hitl without creating a swarm.
 */
export async function materializeAiComposition(
  goal: string,
  options: {
    readonly swarmName?: string;
    readonly fetchImpl?: typeof fetch;
    readonly maxSlots?: number;
    readonly humanResolutions?: Readonly<Record<string, string>>;
  } = {},
): Promise<ComposerMaterializeResult> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const trimmed = goal.trim();
  if (!trimmed) {
    return { ok: false, message: "Enter a goal/spec — AI builds the swarm." };
  }
  try {
    const response = await fetchImpl("/api/v1/composer/materialize", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        goal: trimmed,
        max_slots: options.maxSlots ?? 8,
        human_resolutions: options.humanResolutions ?? {},
        ...(options.swarmName ? { swarm_name: options.swarmName } : {}),
      }),
    });
    if (!response.ok) {
      const detail = await parseErrorDetail(
        response,
        `HTTP ${response.status}`,
      );
      return { ok: false, message: `AI materialize failed: ${detail}` };
    }
    const raw: unknown = await response.json();
    const data = unwrapData<{
      decision_status?: string;
      swarm_id?: string | null;
      name?: string;
      revision?: number;
      member_count?: number;
      canvas_path?: string | null;
      message?: string;
      recommendation?: RawRecommendation;
    }>(raw);

    if (data.decision_status === "needs_hitl" || !data.swarm_id) {
      return {
        ok: true,
        decisionStatus: "needs_hitl",
        message:
          data.message ??
          "Human resolution required before AI can materialize.",
        recommendation: mapRecommendation(data.recommendation ?? {}),
      };
    }

    return {
      ok: true,
      decisionStatus: "ai_resolved",
      swarmId: data.swarm_id,
      name: data.name ?? data.swarm_id,
      revision: data.revision ?? 0,
      memberCount: data.member_count ?? 0,
      canvasPath:
        data.canvas_path ??
        `/swarms/${encodeURIComponent(data.swarm_id)}/canvas`,
      recommendation: mapRecommendation(data.recommendation ?? {}),
    };
  } catch {
    return {
      ok: false,
      message: "Network error while AI materializing swarm draft.",
    };
  }
}
