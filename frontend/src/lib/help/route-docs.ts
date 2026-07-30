/**
 * Generic route → public/docs markdown path resolution (help_spec.md).
 * No business-module hardcoding: candidates are derived only from the URL.
 */

export type HelpTabConfig = {
  readonly id: string;
  readonly label: string;
  /** Optional fixed path; null means compute from route + id. */
  readonly mdPath: string | null;
};

export const DEFAULT_HELP_TABS: readonly HelpTabConfig[] = [
  { id: "userguide", label: "User guide", mdPath: null },
  { id: "func_spec", label: "Func spec", mdPath: null },
  { id: "test_scenario", label: "Test scenarios", mdPath: null },
] as const;

/** Normalize pathname: ensure leading slash, drop trailing slash (except root). */
export function normalizeRoutePath(pathname: string): string {
  let path = (pathname || "/").trim();
  if (!path.startsWith("/")) path = `/${path}`;
  if (path.length > 1 && path.endsWith("/")) path = path.slice(0, -1);
  return path === "" ? "/" : path;
}

/**
 * Strip likely dynamic/param segments for fallback docs.
 * Removes any segment that looks like an ID (uuids, dotted ids, pure numbers),
 * not only trailing ones — e.g. /swarms/:id/canvas → /swarms/canvas.
 */
export function stripDynamicRouteSegments(pathname: string): string {
  const normalized = normalizeRoutePath(pathname);
  if (normalized === "/") return "/";
  const parts = normalized.split("/").filter(Boolean);
  const kept = parts.filter((segment) => !looksLikeParamSegment(segment));
  return kept.length === 0 ? "/" : `/${kept.join("/")}`;
}

/** Known static path segments used by this app (not treated as parameters). */
const STATIC_ROUTE_SEGMENTS = new Set([
  "activity",
  "agents",
  "api",
  "audit",
  "blueprints",
  "canvas",
  "collaboration",
  "composer",
  "costs",
  "developer",
  "docs",
  "evaluations",
  "knowledge",
  "login",
  "mobile",
  "notifications",
  "onboarding",
  "operations",
  "org-chart",
  "profile",
  "registry",
  "settings",
  "swarms",
  "view",
]);

function looksLikeParamSegment(segment: string): boolean {
  const lower = segment.toLowerCase();
  if (STATIC_ROUTE_SEGMENTS.has(lower)) return false;
  if (/^\d+$/.test(segment)) return true;
  if (/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(segment)) {
    return true;
  }
  // Dotted resource ids (e.g. video.orchestrator)
  if (segment.includes(".")) return true;
  // Long opaque tokens
  if (segment.length >= 24 && /^[A-Za-z0-9_-]+$/.test(segment)) return true;
  // Any other non-static segment is treated as a route parameter for doc fallback.
  return true;
}

/**
 * When the route is an agent detail page (/registry/agents/:agentId), surface
 * pack-exported operator guides under /docs/agents/:agentId/ first.
 * Convention only — no pack-specific agent names.
 */
function packAgentHelpCandidates(
  pathname: string,
  tabId: string,
): readonly string[] {
  const exact = normalizeRoutePath(pathname);
  const match = exact.match(/^\/registry\/agents\/([^/]+)$/i);
  if (!match) return [];
  const agentId = match[1];
  if (!agentId || !looksLikeParamSegment(agentId)) return [];
  // reject path traversal / unsafe ids
  if (agentId.includes("..") || agentId.includes("/") || agentId.includes("\\")) {
    return [];
  }

  const tab = tabId.replace(/[^a-z0-9_-]/gi, "").toLowerCase() || "doc";
  const out: string[] = [];
  if (tab === "userguide") {
    // Pack export writes both names; prefer the product filename.
    out.push(`/docs/agents/${agentId}/user_guide.md`);
    out.push(`/docs/agents/${agentId}/userguide.md`);
    // Soft fallback to SPEC if guide not yet exported
    out.push(`/docs/agents/${agentId}/SPEC.md`);
  } else {
    out.push(`/docs/agents/${agentId}/${tab}.md`);
  }
  return out;
}

/**
 * Build candidate markdown URLs under /docs for a tab on the current route.
 * Order: pack agent guide (when on agent detail), exact route path, then fallbacks.
 */
export function resolveHelpMarkdownCandidates(
  pathname: string,
  tabId: string,
  fixedPath: string | null = null,
): readonly string[] {
  if (fixedPath && fixedPath.trim().length > 0) {
    const path = fixedPath.startsWith("/") ? fixedPath : `/${fixedPath}`;
    return [path];
  }

  const exact = normalizeRoutePath(pathname);
  const stripped = stripDynamicRouteSegments(pathname);
  const file = `${tabId.replace(/[^a-z0-9_-]/gi, "").toLowerCase() || "doc"}.md`;

  const candidates: string[] = [];

  for (const packPath of packAgentHelpCandidates(pathname, tabId)) {
    if (!candidates.includes(packPath)) candidates.push(packPath);
  }

  const exactDoc =
    exact === "/" ? `/docs/${file}` : `/docs${exact}/${file}`;
  if (!candidates.includes(exactDoc)) candidates.push(exactDoc);

  if (stripped !== exact) {
    const strippedDoc =
      stripped === "/" ? `/docs/${file}` : `/docs${stripped}/${file}`;
    if (!candidates.includes(strippedDoc)) candidates.push(strippedDoc);
  }

  // Ultimate soft fallback: root docs of this type
  const rootDoc = `/docs/${file}`;
  if (!candidates.includes(rootDoc)) candidates.push(rootDoc);

  return candidates;
}

export function buildFullPageDocsHref(pathname: string, tabId = "userguide"): string {
  const candidates = resolveHelpMarkdownCandidates(pathname, tabId);
  const primary = candidates[0] ?? "/docs/userguide.md";
  // Full-page viewer route: /docs/view?path=/docs/...
  return `/docs/view?path=${encodeURIComponent(primary)}`;
}
