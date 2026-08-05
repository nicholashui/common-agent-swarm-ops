/**
 * Host skill golden-eval client (offline harness).
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

export async function runSkillEvals(
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly skills?: readonly string[];
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly passed: number;
      readonly failed: number;
      readonly total: number;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/skill-evals/run", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        skills: options.skills ? [...options.skills] : [],
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      ok?: boolean;
      passed?: number;
      failed?: number;
      total?: number;
    }>(await response.json());
    return {
      ok: true,
      passed: data.passed ?? 0,
      failed: data.failed ?? 0,
      total: data.total ?? 0,
    };
  } catch {
    return { ok: false, message: "Network error calling skill-evals run." };
  }
}
