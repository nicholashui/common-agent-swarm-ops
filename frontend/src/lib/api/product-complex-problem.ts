/**
 * Host complex-problem process client (offline).
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

export async function solveComplexProblem(
  problem: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly planSteps: number;
      readonly recommendedOption: string;
      readonly gateCount: number;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/complex-problem/solve", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({ problem }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      plan?: unknown[];
      recommended_option?: string;
      gates?: unknown[];
    }>(await response.json());
    return {
      ok: true,
      planSteps: (data.plan ?? []).length,
      recommendedOption: data.recommended_option ?? "",
      gateCount: (data.gates ?? []).length,
    };
  } catch {
    return { ok: false, message: "Network error calling complex-problem solve." };
  }
}
