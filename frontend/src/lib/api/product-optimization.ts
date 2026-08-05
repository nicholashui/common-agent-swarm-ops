/**
 * Host optimization client (offline prompt/cost/retention recommendations).
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

export async function recommendOptimization(
  goal: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly kind?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly kind: string;
      readonly suggestionCount: number;
      readonly titles: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/optimization/recommend", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        goal,
        kind: options.kind ?? "auto",
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      kind?: string;
      suggestions?: { title?: string }[];
    }>(await response.json());
    const suggestions = data.suggestions ?? [];
    return {
      ok: true,
      kind: data.kind ?? "",
      suggestionCount: suggestions.length,
      titles: suggestions.map((s) => s.title ?? "").filter(Boolean),
    };
  } catch {
    return { ok: false, message: "Network error calling optimization recommend." };
  }
}
