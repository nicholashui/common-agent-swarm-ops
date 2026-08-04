/**
 * Browser client for product-ops / product-extended façade GETs.
 * Same-origin only; Host must be reachable via Next rewrite + trusted context.
 */

export type ProductOpsResult<T> =
  | { readonly ok: true; readonly data: T }
  | { readonly ok: false; readonly message: string };

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

async function getJson<T>(
  path: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<T>> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(path, {
      method: "GET",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errBody = (await response.json()) as {
          error?: { message?: string };
          detail?: { message?: string };
        };
        detail =
          errBody.error?.message ?? errBody.detail?.message ?? detail;
      } catch {
        /* keep detail */
      }
      return { ok: false, message: `Could not load ${path}: ${detail}` };
    }
    const raw: unknown = await response.json();
    return { ok: true, data: unwrapData<T>(raw) };
  } catch {
    return {
      ok: false,
      message: `Could not reach Host (${path}). Start backend and set BACKEND_API_ORIGIN.`,
    };
  }
}

export type ActivityItem = {
  readonly id: string;
  readonly category: string;
  readonly severity: string;
  readonly summary: string;
  readonly subject_reference: string;
  readonly status: string;
  readonly occurred_at: string;
  readonly correlation_id?: string;
};

export type ActivityFeed = {
  readonly items: readonly ActivityItem[];
  readonly page?: { readonly next_cursor?: string | null; readonly limit?: number };
  readonly freshness?: { readonly as_of?: string; readonly state?: string };
};

export async function fetchActivityFeed(
  options: { readonly limit?: number; readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<ActivityFeed>> {
  const limit = options.limit ?? 50;
  return getJson<ActivityFeed>(`/api/v1/activity?limit=${limit}`, options);
}

export async function fetchActivityInsights(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly event_count: number;
    readonly categories: readonly string[];
    readonly freshness?: { readonly as_of?: string; readonly state?: string };
  }>
> {
  return getJson("/api/v1/activity/insights", options);
}

export async function fetchCommonsHealth(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly total_agents: number;
    readonly by_pack: Record<string, number>;
    readonly patterns: number;
    readonly as_of: string;
    readonly state: string;
  }>
> {
  return getJson("/api/v1/commons/health", options);
}

export async function fetchCommonsPatterns(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<{ readonly items?: readonly unknown[] } | unknown>> {
  return getJson("/api/v1/commons/patterns", options);
}

export async function fetchKnowledgeSources(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly items: readonly Record<string, unknown>[];
    readonly actions?: readonly unknown[];
    readonly freshness?: { readonly as_of?: string };
  }>
> {
  return getJson("/api/v1/knowledge/sources", options);
}

export async function fetchFinanceSummary(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly budget_limit?: number | null;
    readonly spend_mtd?: number;
    readonly currency?: string;
    readonly actions?: readonly unknown[];
    readonly freshness?: { readonly as_of?: string };
  }>
> {
  return getJson("/api/v1/finance/summary", options);
}

export async function fetchNotifications(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly items: readonly Record<string, unknown>[];
    readonly actions?: readonly unknown[];
    readonly freshness?: { readonly as_of?: string };
  }>
> {
  return getJson("/api/v1/notifications", options);
}

export async function fetchBlueprints(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly items: readonly Record<string, unknown>[];
    readonly actions?: readonly unknown[];
  }>
> {
  return getJson("/api/v1/blueprints", options);
}

export async function fetchWorkspaceSettings(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly workspace?: Record<string, unknown>;
    readonly providers?: readonly Record<string, unknown>[];
    readonly actions?: readonly unknown[];
  }>
> {
  return getJson("/api/v1/settings/workspace", options);
}

export async function fetchPreferences(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<Record<string, unknown>>> {
  return getJson("/api/v1/actors/me/preferences", options);
}

export async function fetchApprovalsInbox(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly items: readonly Record<string, unknown>[];
    readonly freshness?: { readonly as_of?: string };
  }>
> {
  return getJson("/api/v1/approvals", options);
}

export type PackageApprovalDetail = {
  readonly approval_id?: string;
  readonly swarm_id?: string;
  readonly gate_status?: string;
  readonly summary?: string;
  readonly canvas_path?: string;
  readonly note?: string;
  readonly spine_status?: string;
  readonly actions?: readonly {
    readonly id?: string;
    readonly kind?: string;
    readonly label?: string;
  }[];
};

export async function fetchPackageApproval(
  approvalId: string,
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<PackageApprovalDetail>> {
  return getJson(
    `/api/v1/package-approvals/${encodeURIComponent(approvalId)}`,
    options,
  );
}

export async function decidePackageApproval(
  approvalId: string,
  body: {
    readonly actionReferenceId: string;
    readonly decision: "approved" | "denied";
    readonly reason: string;
  },
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<Record<string, unknown>>> {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  try {
    const response = await fetchImpl(
      `/api/v1/package-approvals/${encodeURIComponent(approvalId)}/decision`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          action_reference_id: body.actionReferenceId,
          decision: body.decision,
          reason: body.reason,
        }),
      },
    );
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errBody = (await response.json()) as {
          error?: { message?: string };
          detail?: { message?: string };
        };
        detail = errBody.error?.message ?? errBody.detail?.message ?? detail;
      } catch {
        /* keep */
      }
      return { ok: false, message: detail };
    }
    const raw: unknown = await response.json();
    return { ok: true, data: unwrapData(raw) };
  } catch {
    return {
      ok: false,
      message: "Could not reach Host for package decision.",
    };
  }
}

export async function fetchCollaborationPresence(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<ProductOpsResult<Record<string, unknown>>> {
  return getJson("/api/v1/collaboration/presence", options);
}

export async function fetchRunningSwarms(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly items: readonly {
      id?: string;
      name?: string;
      status?: string;
      revision?: number;
      member_count?: number;
      last_run_id?: string | null;
      updated_at?: string;
      created_at?: string;
      has_spine?: boolean;
      spine_status?: string | null;
      spine_workflow_id?: string | null;
      approval_id?: string | null;
      note?: string | null;
    }[];
    readonly freshness?: { readonly as_of?: string };
  }>
> {
  return getJson("/api/v1/swarms/running", options);
}

export async function fetchCommonImpact(
  options: { readonly fetchImpl?: typeof fetch } = {},
): Promise<
  ProductOpsResult<{
    readonly total_agents?: number;
    readonly impact?: readonly unknown[];
    readonly note?: string;
  }>
> {
  return getJson("/api/v1/insights/common-impact", options);
}
