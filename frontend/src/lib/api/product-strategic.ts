/**
 * Host strategic goal client (offline milestones/KRs).
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

export async function planStrategicGoal(
  goal: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly horizon?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly milestoneCount: number;
      readonly krCount: number;
      readonly objective: string;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/strategic/plan", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        goal,
        horizon: options.horizon ?? "project",
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      milestones?: unknown[];
      key_results?: unknown[];
      objective?: string;
    }>(await response.json());
    return {
      ok: true,
      milestoneCount: (data.milestones ?? []).length,
      krCount: (data.key_results ?? []).length,
      objective: data.objective ?? "",
    };
  } catch {
    return { ok: false, message: "Network error calling strategic plan." };
  }
}
