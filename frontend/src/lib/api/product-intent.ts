/**
 * Host intent-analysis client (offline DIA lite).
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

export async function analyzeIntent(
  text: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly primaryIntent: string;
      readonly archetype: string;
      readonly escalateToHitl: boolean;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/intent/analyze", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      primary_intent?: string;
      recommended_archetype?: string;
      escalate_to_hitl?: boolean;
    }>(await response.json());
    return {
      ok: true,
      primaryIntent: data.primary_intent ?? "",
      archetype: data.recommended_archetype ?? "",
      escalateToHitl: Boolean(data.escalate_to_hitl),
    };
  } catch {
    return { ok: false, message: "Network error calling intent analyze." };
  }
}
