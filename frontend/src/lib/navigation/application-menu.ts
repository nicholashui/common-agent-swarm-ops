/**
 * Application menu catalog for ui_00_menu.
 *
 * Static presentation labels and routes come from the redesign IA. Authorization,
 * eligibility, badges, and domain visibility must merge from returned projections
 * when available — absence hides an item; it never invents protected resources.
 */

export type MenuIconName =
  | "activity"
  | "api"
  | "approval"
  | "audit"
  | "blueprint"
  | "canvas"
  | "collaboration"
  | "compose"
  | "cost"
  | "dashboard"
  | "domain"
  | "evaluation"
  | "help"
  | "knowledge"
  | "monitoring"
  | "notification"
  | "profile"
  | "logout"
  | "registry"
  | "settings";

export type MenuItemVisibility =
  | "always"
  /** Shown only when the resolved pathname is a scoped child resource. */
  | "scoped_path"
  /** Shown only when the shell projection authorizes the item id. */
  | "authorized";

export interface ApplicationMenuItem {
  readonly id: string;
  readonly label: string;
  readonly href: string;
  readonly icon: MenuIconName;
  readonly groupId: ApplicationMenuGroupId;
  readonly badge?: string;
  readonly tone?: "common" | "domain";
  readonly visibility: MenuItemVisibility;
  /** Path prefixes that mark this item current (in addition to href). */
  readonly activePathPrefixes?: readonly string[];
  /** Exact paths that mark this item current. */
  readonly activeExactPaths?: readonly string[];
  /** For scoped_path items: pathname must start with one of these prefixes. */
  readonly scopedPathPrefixes?: readonly string[];
  /**
   * When true, this item does not steal aria-current from a more specific sibling
   * (for example Registry Hub while Agent Detail is active).
   */
  readonly deferActiveToScopedChildren?: boolean;
  readonly scopedChildPrefixes?: readonly string[];
}

export type ApplicationMenuGroupId =
  | "home"
  | "build"
  | "common"
  | "operate"
  | "knowledge-quality"
  | "domain"
  | "governance"
  | "developer-help"
  | "account";

export interface ApplicationMenuGroup {
  readonly id: ApplicationMenuGroupId;
  readonly label: string;
  readonly itemIds: readonly string[];
}

/** IA groups from docs/frontend_redesign/ui_00_menu.md. */
export const APPLICATION_MENU_GROUPS: readonly ApplicationMenuGroup[] = [
  { id: "home", label: "Home", itemIds: ["dashboard"] },
  {
    id: "build",
    label: "Build",
    itemIds: ["compose", "swarm-canvas", "blueprints"],
  },
  {
    id: "common",
    label: "Common",
    itemIds: ["registry-hub", "agent-pattern-detail"],
  },
  {
    id: "operate",
    label: "Operate",
    itemIds: [
      "activity",
      "monitoring",
      "approvals-rollouts",
      "notifications",
      "costs",
    ],
  },
  {
    id: "knowledge-quality",
    label: "Knowledge & Quality",
    itemIds: ["knowledge", "eval-improvement"],
  },
  { id: "domain", label: "Domain", itemIds: ["va-production"] },
  {
    id: "governance",
    label: "Governance",
    itemIds: ["audit", "collaboration"],
  },
  {
    id: "developer-help",
    label: "Developer & Help",
    itemIds: ["api-portal", "onboarding-help"],
  },
  { id: "account", label: "Account", itemIds: ["settings", "profile"] },
] as const;

/**
 * Full menu table items. Routes align with screen-manifest where a route exists.
 * Swarm Canvas uses the non-inventing /canvas entry; nested swarm canvas paths
 * still mark it active.
 */
export const APPLICATION_MENU_ITEMS: readonly ApplicationMenuItem[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    href: "/",
    icon: "dashboard",
    groupId: "home",
    badge: "HOME",
    visibility: "always",
    activeExactPaths: ["/"],
  },
  {
    id: "compose",
    label: "Compose",
    href: "/composer",
    icon: "compose",
    groupId: "build",
    visibility: "always",
    activePathPrefixes: ["/composer"],
  },
  {
    id: "swarm-canvas",
    label: "Swarm Canvas",
    href: "/canvas",
    icon: "canvas",
    groupId: "build",
    visibility: "always",
    activeExactPaths: ["/canvas"],
    activePathPrefixes: ["/swarms/"],
  },
  {
    id: "blueprints",
    label: "Blueprints",
    href: "/blueprints",
    icon: "blueprint",
    groupId: "build",
    visibility: "always",
    activePathPrefixes: ["/blueprints"],
  },
  {
    id: "registry-hub",
    label: "Registry Hub",
    href: "/registry",
    icon: "registry",
    groupId: "common",
    tone: "common",
    visibility: "always",
    activeExactPaths: ["/registry"],
    activePathPrefixes: ["/registry"],
    deferActiveToScopedChildren: true,
    scopedChildPrefixes: ["/registry/agents/"],
  },
  {
    id: "agent-pattern-detail",
    label: "Agent & Pattern Detail",
    href: "/registry",
    icon: "registry",
    groupId: "common",
    visibility: "scoped_path",
    scopedPathPrefixes: ["/registry/agents/"],
    activePathPrefixes: ["/registry/agents/"],
  },
  {
    id: "activity",
    label: "Activity",
    href: "/activity",
    icon: "activity",
    groupId: "operate",
    visibility: "always",
    activePathPrefixes: ["/activity"],
  },
  {
    id: "monitoring",
    label: "Monitoring",
    href: "/operations",
    icon: "monitoring",
    groupId: "operate",
    visibility: "always",
    activeExactPaths: ["/operations"],
    activePathPrefixes: ["/operations"],
  },
  {
    id: "approvals-rollouts",
    label: "Approvals & Rollouts",
    href: "/operations",
    icon: "approval",
    groupId: "operate",
    visibility: "always",
    // Shares the monitoring projection route until a dedicated approvals route exists.
    activeExactPaths: ["/operations"],
  },
  {
    id: "notifications",
    label: "Notifications",
    href: "/notifications",
    icon: "notification",
    groupId: "operate",
    visibility: "always",
    activePathPrefixes: ["/notifications"],
  },
  {
    id: "costs",
    label: "Costs",
    href: "/costs",
    icon: "cost",
    groupId: "operate",
    visibility: "always",
    activePathPrefixes: ["/costs"],
  },
  {
    id: "knowledge",
    label: "Knowledge",
    href: "/knowledge",
    icon: "knowledge",
    groupId: "knowledge-quality",
    visibility: "always",
    activePathPrefixes: ["/knowledge"],
  },
  {
    id: "eval-improvement",
    label: "Eval & Improvement",
    href: "/evaluations",
    icon: "evaluation",
    groupId: "knowledge-quality",
    visibility: "always",
    activePathPrefixes: ["/evaluations"],
  },
  {
    id: "va-production",
    label: "VA Production",
    href: "/registry",
    icon: "domain",
    groupId: "domain",
    tone: "domain",
    visibility: "authorized",
  },
  {
    id: "audit",
    label: "Audit",
    href: "/audit",
    icon: "audit",
    groupId: "governance",
    visibility: "always",
    activePathPrefixes: ["/audit"],
  },
  {
    id: "collaboration",
    label: "Collaboration",
    href: "/collaboration",
    icon: "collaboration",
    groupId: "governance",
    visibility: "always",
    activePathPrefixes: ["/collaboration"],
  },
  {
    id: "api-portal",
    label: "API Portal",
    href: "/developer/api",
    icon: "api",
    groupId: "developer-help",
    visibility: "always",
    activePathPrefixes: ["/developer/api"],
  },
  {
    id: "onboarding-help",
    label: "Onboarding & Help",
    href: "/onboarding",
    icon: "help",
    groupId: "developer-help",
    visibility: "always",
    activePathPrefixes: ["/onboarding"],
  },
  {
    id: "settings",
    label: "Settings",
    href: "/settings",
    icon: "settings",
    groupId: "account",
    visibility: "always",
    activePathPrefixes: ["/settings"],
  },
  {
    id: "profile",
    label: "Profile",
    href: "/profile",
    icon: "profile",
    groupId: "account",
    visibility: "always",
    activePathPrefixes: ["/profile"],
  },
] as const;

const ITEM_BY_ID: ReadonlyMap<string, ApplicationMenuItem> = new Map(
  APPLICATION_MENU_ITEMS.map((item) => [item.id, item]),
);

export interface ApplicationMenuProjection {
  /** Item ids authorized by a returned shell/navigation projection. */
  readonly authorizedItemIds?: readonly string[];
  readonly workspaceName?: string;
  readonly workspaceScopeLabel?: string;
  readonly connectionStateLabel?: string;
  readonly connectionDetail?: string;
  readonly correlationIdentifier?: string;
  readonly environmentLabel?: string;
}

export interface ResolvedMenuItem extends ApplicationMenuItem {
  readonly href: string;
  readonly active: boolean;
}

export interface ResolvedMenuGroup {
  readonly id: ApplicationMenuGroupId;
  readonly label: string;
  readonly items: readonly ResolvedMenuItem[];
}

function pathStartsWith(pathname: string, prefix: string): boolean {
  return pathname === prefix || pathname.startsWith(`${prefix}/`) || pathname.startsWith(prefix);
}

function isScopedChildActive(
  pathname: string,
  item: ApplicationMenuItem,
): boolean {
  if (!item.deferActiveToScopedChildren || !item.scopedChildPrefixes) {
    return false;
  }
  return item.scopedChildPrefixes.some((prefix) => pathStartsWith(pathname, prefix));
}

export function isMenuItemActive(
  pathname: string,
  item: ApplicationMenuItem,
): boolean {
  if (isScopedChildActive(pathname, item)) {
    return false;
  }

  if (item.activeExactPaths?.includes(pathname)) {
    return true;
  }

  if (item.activePathPrefixes) {
    for (const prefix of item.activePathPrefixes) {
      if (prefix === "/") {
        if (pathname === "/") return true;
        continue;
      }
      // Swarm canvas: any /swarms/*/canvas path.
      if (prefix === "/swarms/") {
        if (/^\/swarms\/[^/]+\/canvas(?:\/|$)/.test(pathname)) {
          return true;
        }
        continue;
      }
      if (pathStartsWith(pathname, prefix)) {
        return true;
      }
    }
  }

  if (item.href === "/") {
    return pathname === "/";
  }

  return pathStartsWith(pathname, item.href.split("#", 1)[0] ?? item.href);
}

export function isMenuItemVisible(
  pathname: string,
  item: ApplicationMenuItem,
  projection: ApplicationMenuProjection | undefined,
): boolean {
  switch (item.visibility) {
    case "always":
      return true;
    case "scoped_path": {
      const prefixes = item.scopedPathPrefixes ?? [];
      return prefixes.some((prefix) => pathStartsWith(pathname, prefix));
    }
    case "authorized": {
      const authorized = projection?.authorizedItemIds;
      if (!authorized) return false;
      return authorized.includes(item.id);
    }
    default:
      return false;
  }
}

function resolveItemHref(pathname: string, item: ApplicationMenuItem): string {
  if (
    item.visibility === "scoped_path" &&
    item.scopedPathPrefixes?.some((prefix) => pathStartsWith(pathname, prefix))
  ) {
    return pathname;
  }
  return item.href;
}

/** Merge static IA labels with returned authorization and the active route. */
export function resolveApplicationMenu(
  pathname: string,
  projection?: ApplicationMenuProjection,
): readonly ResolvedMenuGroup[] {
  const groups: ResolvedMenuGroup[] = [];

  for (const group of APPLICATION_MENU_GROUPS) {
    const items: ResolvedMenuItem[] = [];
    for (const itemId of group.itemIds) {
      const item = ITEM_BY_ID.get(itemId);
      if (!item) continue;
      if (!isMenuItemVisible(pathname, item, projection)) continue;
      items.push({
        ...item,
        href: resolveItemHref(pathname, item),
        active: isMenuItemActive(pathname, item),
      });
    }
    if (items.length > 0) {
      groups.push({ id: group.id, label: group.label, items });
    }
  }

  return groups;
}

/** Labels in IA table order for verification. */
export function listApplicationMenuLabels(): readonly string[] {
  return APPLICATION_MENU_ITEMS.map((item) => item.label);
}

export function getApplicationMenuItem(
  id: string,
): ApplicationMenuItem | undefined {
  return ITEM_BY_ID.get(id);
}
