/**
 * Host skills catalog client.
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

export async function fetchSkillsCatalog(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  | {
      readonly ok: true;
      readonly count: number;
      readonly skillIds: readonly string[];
    }
  | { readonly ok: false; readonly message: string }
> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl("/api/v1/skills/catalog", {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: await parseError(response, `HTTP ${response.status}`) };
    }
    const data = unwrapData<{
      count?: number;
      items?: { skill_id?: string }[];
    }>(await response.json());
    return {
      ok: true,
      count: data.count ?? 0,
      skillIds: (data.items ?? []).map((i) => i.skill_id ?? "").filter(Boolean),
    };
  } catch {
    return { ok: false, message: "Network error calling skills catalog." };
  }
}
