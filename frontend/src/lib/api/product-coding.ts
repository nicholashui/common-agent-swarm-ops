/**
 * Host coding-agent client (offline plan-only).
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

export async function planCodingWork(
  goal: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly stepCount: number;
      readonly touchCount: number;
      readonly tests: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/coding/plan", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({ goal }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      plan_steps?: unknown[];
      touch_points?: unknown[];
      suggested_tests?: string[];
    }>(await response.json());
    return {
      ok: true,
      stepCount: (data.plan_steps ?? []).length,
      touchCount: (data.touch_points ?? []).length,
      tests: data.suggested_tests ?? [],
    };
  } catch {
    return { ok: false, message: "Network error calling coding plan." };
  }
}
