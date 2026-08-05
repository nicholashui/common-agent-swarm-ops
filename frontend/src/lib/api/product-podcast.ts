/**
 * Host podcast client (offline outline).
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

export async function outlinePodcast(
  topic: string,
  options: {
    readonly fetchImpl?: typeof fetch;
    readonly durationMin?: number;
  } = {},
): Promise<
  | {
      readonly ok: true;
      readonly segmentCount: number;
      readonly liveTts: boolean;
      readonly titles: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/podcast/outline", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        topic,
        duration_min: options.durationMin ?? 15,
      }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      segments?: unknown[];
      vo_plan?: { live_tts?: boolean };
      title_options?: string[];
    }>(await response.json());
    return {
      ok: true,
      segmentCount: (data.segments ?? []).length,
      liveTts: Boolean(data.vo_plan?.live_tts),
      titles: data.title_options ?? [],
    };
  } catch {
    return { ok: false, message: "Network error calling podcast outline." };
  }
}
