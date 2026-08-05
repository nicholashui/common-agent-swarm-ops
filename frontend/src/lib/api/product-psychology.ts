/**
 * Host psychology client (offline audience profile / hooks).
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

export async function buildPsychProfile(
  brief: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly profileId: string;
      readonly cohortId: string;
      readonly valence: number;
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/psychology/profile", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify({ brief }),
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      profile?: {
        profile_id?: string;
        cohort_id?: string;
        emotional_target?: { valence?: number };
      };
    }>(await response.json());
    const p = data.profile ?? {};
    return {
      ok: true,
      profileId: p.profile_id ?? "",
      cohortId: p.cohort_id ?? "",
      valence: p.emotional_target?.valence ?? 0,
    };
  } catch {
    return { ok: false, message: "Network error calling psychology profile." };
  }
}
