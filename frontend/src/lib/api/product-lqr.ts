/**
 * Host LQR overview client (offline archetype E scaffold).
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

export async function fetchLqrOverview(
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly logline?: string;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly phaseCount: number;
      readonly archetype: string;
      readonly principles: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/lqr/overview", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        ...(options.logline ? { logline: options.logline } : {}),
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      phases?: unknown[];
      archetype?: string;
      principles?: string[];
    }>(await response.json());
    return {
      ok: true,
      phaseCount: (data.phases ?? []).length,
      archetype: data.archetype ?? "",
      principles: data.principles ?? [],
    };
  } catch {
    return { ok: false, message: "Network error calling LQR overview." };
  }
}
