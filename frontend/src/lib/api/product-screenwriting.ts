/**
 * Host screenwriting client (offline beat sheet).
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

export async function planScreenplay(
  loglineOrGoal: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly form?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly beatCount: number;
      readonly controllingIdea: string;
      readonly genre: string;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/screenwriting/plan", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        logline_or_goal: loglineOrGoal,
        form: options.form ?? "short",
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      beats?: unknown[];
      controlling_idea?: string;
      genre?: string;
    }>(await response.json());
    return {
      ok: true,
      beatCount: (data.beats ?? []).length,
      controllingIdea: data.controlling_idea ?? "",
      genre: data.genre ?? "",
    };
  } catch {
    return { ok: false, message: "Network error calling screenwriting plan." };
  }
}
