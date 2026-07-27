"use client";

/**
 * @duty ShellNavigation — application menu navigation chrome
 * @role Render resolved application menu groups/links for in-app routing only.
 * @controls Nav links, optional mobile menu toggle; no mutate authority.
 * @must Use projection/menu config; highlight active path without inventing routes.
 * @mustnot Expose external untrusted destinations or privileged menu items not projected.
 * @redesign docs/frontend_redesign/ui_00_menu.md
 */
import Link from "next/link";
import { usePathname } from "next/navigation";
import React, {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  type ApplicationMenuProjection,
  type MenuIconName,
  type ResolvedMenuGroup,
  resolveApplicationMenu,
} from "../lib/navigation/application-menu";
import { buildFullPageDocsHref } from "../lib/help/route-docs";
import {
  HELP_PANEL_DEFAULT_WIDTH,
  RightHelpPanel,
  clampHelpPanelWidth,
  readStoredHelpPanelWidth,
  writeStoredHelpPanelWidth,
} from "./help/RightHelpPanel";

const MENU_ICON_PATHS: Readonly<Record<MenuIconName, readonly string[]>> = {
  activity: ["M5 5h14v11H5z", "M8 9h8", "M8 13h5"],
  api: ["m8 7-4 5 4 5", "m16 7 4 5-4 5", "m14 4-4 16"],
  approval: ["M5 12h14", "m9 8 4 4-4 4"],
  audit: ["M6 4h12v16H6z", "M9 8h6", "M9 12h6", "M9 16h4"],
  blueprint: ["M5 5h14v14H5z", "M8 12h8", "M12 8v8"],
  canvas: ["M5 6h5v5H5z", "M14 13h5v5h-5z", "m10 9 4 4"],
  collaboration: [
    "M8 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z",
    "M16 13a4 4 0 1 0 0-8",
    "M3 20c1-4 9-4 10 0",
    "M13 17c3-2 7 0 8 3",
  ],
  compose: ["m12 4 3 5 5 3-5 3-3 5-3-5-5-3 5-3Z"],
  cost: ["M5 7h14v11H5z", "M8 7V5h8v2", "M9 12h6"],
  dashboard: ["M5 5h6v6H5z", "M13 5h6v6h-6z", "M5 13h6v6H5z", "M13 13h6v6h-6z"],
  domain: ["M5 5h14v14H5z", "M8 9h8", "M8 13h6", "M8 17h4"],
  evaluation: [
    "m12 4 2.2 4.5L19 9.2l-3.5 3.4.8 4.8-4.3-2.3-4.3 2.3.8-4.8L5 9.2l4.8-.7Z",
  ],
  help: [
    "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z",
    "M9.8 9a2.3 2.3 0 1 1 3.3 2.1c-.9.5-1.1 1-1.1 1.9",
    "M12 17h.01",
  ],
  knowledge: [
    "M5 5h5a3 3 0 0 1 2 1 3 3 0 0 1 2-1h5v14h-5a3 3 0 0 0-2 1 3 3 0 0 0-2-1H5Z",
    "M12 6v14",
  ],
  monitoring: ["M4 18h16", "M6 15l4-5 3 3 5-7"],
  notification: ["M6 16h12l-1.5-2V9a4.5 4.5 0 0 0-9 0v5Z", "M10 19h4"],
  profile: ["M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M4 21c1-6 15-6 16 0"],
  registry: ["M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16Z", "M8 12h8", "M12 8v8"],
  settings: [
    "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
    "M12 3v3",
    "M12 18v3",
    "M3 12h3",
    "M18 12h3",
    "m5.6 5.6 2.1 2.1",
    "m16.3 16.3 2.1 2.1",
    "m18.4 5.6-2.1 2.1",
    "m7.7 16.3-2.1 2.1",
  ],
};

const COLLAPSED_PREFERENCE_KEY = "casops:menu-collapsed";

const DEFAULT_PROJECTION: ApplicationMenuProjection = {
  workspaceName: "Returned workspace",
  workspaceScopeLabel: "Authorized session scope",
  connectionStateLabel: "Reconnecting",
  connectionDetail: "Status: returned projection · as_of …",
};

function MenuIcon({ name }: Readonly<{ name: MenuIconName }>): JSX.Element {
  return (
    <svg
      aria-hidden="true"
      className="menu-link-icon"
      fill="none"
      viewBox="0 0 24 24"
    >
      {MENU_ICON_PATHS[name].map((path, index) => (
        <path d={path} key={`${name}-${index}`} />
      ))}
    </svg>
  );
}

function ProductMark(): JSX.Element {
  return (
    <span aria-hidden="true" className="menu-product-mark">
      <svg fill="none" viewBox="0 0 34 34">
        <circle cx="17" cy="10" r="2.3" />
        <circle cx="10" cy="23" r="2.3" />
        <circle cx="24" cy="23" r="2.3" />
        <path d="m17 12.5-6 8.5m6-8.5 6 8.5m-11.5 2h11" />
      </svg>
    </span>
  );
}

function readCollapsedPreference(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.sessionStorage.getItem(COLLAPSED_PREFERENCE_KEY) === "1";
  } catch {
    return false;
  }
}

function writeCollapsedPreference(collapsed: boolean): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(
      COLLAPSED_PREFERENCE_KEY,
      collapsed ? "1" : "0",
    );
  } catch {
    // Session-safe preference is best-effort only.
  }
}

function groupDomId(groupId: string): string {
  return `menu-group-${groupId}`;
}

export interface ShellNavigationProps {
  readonly children: ReactNode;
  /** Optional returned navigation/shell projection. Absence hides authorized-only items. */
  readonly menuProjection?: ApplicationMenuProjection;
  /** Test/override path; production uses the Next.js router pathname. */
  readonly pathname?: string;
}

export interface ApplicationMenuViewProps {
  readonly children: ReactNode;
  readonly pathname: string;
  readonly menuProjection?: ApplicationMenuProjection;
}

export function ShellNavigation({
  children,
  menuProjection,
  pathname: pathnameOverride,
}: ShellNavigationProps): JSX.Element {
  const routerPathname = usePathname();
  const pathname = pathnameOverride ?? routerPathname ?? "/";
  return (
    <ApplicationMenuView menuProjection={menuProjection} pathname={pathname}>
      {children}
    </ApplicationMenuView>
  );
}

/** Pure authenticated menu shell (ui_00_menu) for production and deterministic tests. */
export function ApplicationMenuView({
  children,
  pathname,
  menuProjection,
}: ApplicationMenuViewProps): JSX.Element {
  const menuRef = useRef<HTMLElement>(null);
  const menuTriggerRef = useRef<HTMLButtonElement>(null);
  const [isCompact, setIsCompact] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  // Groups start expanded (spec keyboard/source order). Only explicit collapses persist in state.
  const [collapsedGroups, setCollapsedGroups] = useState<ReadonlySet<string>>(
    () => new Set(),
  );
  /** Workspace-owned help drawer state (help_spec.md). */
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [rightPanelWidth, setRightPanelWidth] = useState(HELP_PANEL_DEFAULT_WIDTH);
  const [rightPanelDragging, setRightPanelDragging] = useState(false);
  const baseId = useId();

  const projection = menuProjection ?? DEFAULT_PROJECTION;
  const groups = useMemo(
    () => resolveApplicationMenu(pathname, projection),
    [pathname, projection],
  );

  useEffect(() => {
    setIsCompact(readCollapsedPreference());
    setRightPanelWidth(readStoredHelpPanelWidth());
  }, []);

  useEffect(() => {
    writeStoredHelpPanelWidth(rightPanelWidth);
  }, [rightPanelWidth]);

  // Close mobile left drawer when viewport returns to desktop.
  useEffect(() => {
    if (typeof window === "undefined") return undefined;
    const media = window.matchMedia("(min-width: 961px)");
    const onChange = (): void => {
      if (media.matches) setIsMenuOpen(false);
    };
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    if (!isMenuOpen) return undefined;

    const previousOverflow = document.body.style.overflow;
    const menu = menuRef.current;
    const focusableElements = (): HTMLElement[] =>
      Array.from(
        menu?.querySelectorAll<HTMLElement>(
          "a[href], button:not([disabled])",
        ) ?? [],
      ).filter((element) => element.offsetParent !== null);

    document.body.style.overflow = "hidden";
    focusableElements()[0]?.focus();

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        event.preventDefault();
        setIsMenuOpen(false);
        return;
      }
      if (event.key !== "Tab") return;

      const elements = focusableElements();
      const firstElement = elements[0];
      const lastElement = elements.at(-1);
      if (!firstElement || !lastElement) return;

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
      menuTriggerRef.current?.focus();
    };
  }, [isMenuOpen]);

  const closeMenu = (): void => setIsMenuOpen(false);

  const toggleGroup = (groupId: string): void => {
    setCollapsedGroups((current) => {
      const next = new Set(current);
      if (next.has(groupId)) next.delete(groupId);
      else next.add(groupId);
      return next;
    });
  };

  const toggleCompact = (): void => {
    setIsCompact((current) => {
      const next = !current;
      writeCollapsedPreference(next);
      return next;
    });
  };

  const workspaceName = projection.workspaceName ?? "Returned workspace";
  const workspaceScope =
    projection.workspaceScopeLabel ?? "Authorized session scope";
  const connectionLabel = projection.connectionStateLabel ?? "Reconnecting";
  const connectionDetail =
    projection.connectionDetail ?? "Status: returned projection · as_of …";
  const environmentLabel = projection.environmentLabel;
  const correlationId = projection.correlationIdentifier;

  return (
    <div className={isCompact ? "app-shell app-shell--compact" : "app-shell"}>
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="menu-mobile-bar">
        <Link aria-label="Dashboard" className="menu-mobile-brand" href="/">
          <ProductMark />
          <span>common-agent-swarm-ops</span>
        </Link>
        <button
          aria-controls="application-menu"
          aria-expanded={isMenuOpen}
          aria-label="Open application menu"
          className="menu-mobile-trigger"
          onClick={() => setIsMenuOpen(true)}
          ref={menuTriggerRef}
          type="button"
        >
          <span aria-hidden="true">☰</span>
        </button>
      </header>
      <div className="workspace menu-workspace">
        <button
          aria-label="Close application menu"
          className={
            isMenuOpen ? "menu-overlay menu-overlay--visible" : "menu-overlay"
          }
          onClick={closeMenu}
          tabIndex={-1}
          type="button"
        />
        <aside
          aria-label="Application menu"
          className={
            isMenuOpen ? "menu-sidebar menu-sidebar--open" : "menu-sidebar"
          }
          id="application-menu"
          ref={menuRef}
        >
          <div className="menu-sidebar-header">
            <Link
              aria-label="Dashboard"
              className="menu-product"
              href="/"
              onClick={closeMenu}
              title="common-agent-swarm-ops"
            >
              <ProductMark />
              <span className="menu-product-copy">
                <strong>common-agent-swarm-ops</strong>
                <small>Common-first control plane</small>
              </span>
            </Link>
            <button
              aria-label="Close application menu"
              className="menu-close"
              onClick={closeMenu}
              type="button"
            >
              ×
            </button>
            <div
              aria-label={`Current workspace: ${workspaceName}`}
              className="menu-workspace-state"
              role="status"
              title={`${workspaceName} — ${workspaceScope}`}
            >
              <span aria-hidden="true" className="menu-workspace-indicator">
                <i />
              </span>
              <span className="menu-workspace-copy">
                <strong>{workspaceName}</strong>
                <small>{workspaceScope}</small>
                {environmentLabel ? (
                  <small className="menu-environment">{environmentLabel}</small>
                ) : null}
              </span>
            </div>
          </div>
          <nav aria-label="Main navigation" className="menu-navigation">
            {groups.map((group) => (
              <MenuGroupSection
                baseId={baseId}
                group={group}
                isExpanded={!collapsedGroups.has(group.id)}
                key={group.id}
                onNavigate={closeMenu}
                onToggle={() => toggleGroup(group.id)}
              />
            ))}
          </nav>
          <footer className="menu-footer">
            <div
              className="menu-connection"
              role="status"
              title={`${connectionLabel} — ${connectionDetail}`}
            >
              <span
                aria-hidden="true"
                className="menu-connection-dot"
                data-status-icon="reconnecting"
              />
              <span className="menu-connection-copy">
                <strong>
                  <span className="visually-hidden">Connection status: </span>
                  {connectionLabel}
                </strong>
                <small>{connectionDetail}</small>
                {correlationId ? (
                  <small className="menu-correlation">
                    Correlation: {correlationId}
                  </small>
                ) : null}
              </span>
              <Link
                aria-label="Profile"
                className="menu-footer-profile"
                href="/profile"
                onClick={closeMenu}
              >
                <MenuIcon name="profile" />
                <span className="menu-profile-copy">Profile</span>
              </Link>
            </div>
            <button
              aria-label={
                isCompact
                  ? "Expand application menu"
                  : "Collapse application menu"
              }
              className="menu-collapse"
              onClick={toggleCompact}
              title={
                isCompact
                  ? "Expand application menu"
                  : "Collapse application menu"
              }
              type="button"
            >
              <span aria-hidden="true">{isCompact ? "›" : "‹"}</span>
              <span className="menu-collapse-copy">
                {isCompact ? "Expand menu" : "Collapse menu"}
              </span>
            </button>
          </footer>
        </aside>
        <div
          className={
            rightPanelOpen
              ? "menu-workspace-main menu-workspace-main--help-open"
              : "menu-workspace-main"
          }
        >
          <header className="workspace-topbar" aria-label="Workspace actions">
            <div className="workspace-topbar__spacer" />
            <div className="workspace-topbar__actions">
              <Link
                aria-label="Open full document page"
                className="workspace-topbar__icon"
                href={buildFullPageDocsHref(pathname, "userguide")}
                title="Open document page"
              >
                <MenuIcon name="knowledge" />
                <span className="visually-hidden">Documents</span>
              </Link>
              <button
                aria-label={
                  rightPanelOpen ? "Close help panel" : "Open help panel"
                }
                aria-pressed={rightPanelOpen}
                className={
                  rightPanelOpen
                    ? "workspace-topbar__icon workspace-topbar__icon--pressed"
                    : "workspace-topbar__icon"
                }
                onClick={() => setRightPanelOpen((open) => !open)}
                title="Toggle help panel"
                type="button"
              >
                <MenuIcon name="help" />
                <span className="visually-hidden">Help</span>
              </button>
            </div>
          </header>
          <main className="app-main menu-main" id="main-content">
            {children}
          </main>
          <RightHelpPanel
            dragging={rightPanelDragging}
            onClose={() => setRightPanelOpen(false)}
            onDraggingChange={setRightPanelDragging}
            onWidthChange={(width) =>
              setRightPanelWidth(clampHelpPanelWidth(width))
            }
            open={rightPanelOpen}
            pathname={pathname}
            width={rightPanelWidth}
          />
        </div>
      </div>
      <div
        aria-atomic="true"
        aria-live="polite"
        className="visually-hidden"
        id="operational-live-region"
        role="status"
      />
    </div>
  );
}

function MenuGroupSection({
  group,
  isExpanded,
  onToggle,
  onNavigate,
  baseId,
}: Readonly<{
  group: ResolvedMenuGroup;
  isExpanded: boolean;
  onToggle: () => void;
  onNavigate: () => void;
  baseId: string;
}>): JSX.Element {
  const labelId = `${baseId}-${groupDomId(group.id)}-label`;
  const panelId = `${baseId}-${groupDomId(group.id)}-panel`;

  return (
    <section
      aria-labelledby={labelId}
      className="menu-group"
      data-menu-group={group.id}
    >
      <h2 className="menu-group-heading" id={labelId}>
        <button
          aria-controls={panelId}
          aria-expanded={isExpanded}
          className="menu-group-toggle"
          onClick={onToggle}
          type="button"
        >
          <span className="menu-group-label">{group.label}</span>
        </button>
      </h2>
      <div
        className={
          isExpanded
            ? "menu-group-items"
            : "menu-group-items menu-group-items--collapsed"
        }
        hidden={!isExpanded}
        id={panelId}
      >
        {group.items.map((item) => {
          const itemClassName = [
            "menu-link",
            item.active ? "menu-link--active" : "",
            item.visibility === "scoped_path" ? "menu-link--contextual" : "",
            item.tone ? `menu-link--${item.tone}` : "",
          ]
            .filter(Boolean)
            .join(" ");
          return (
            <Link
              aria-current={item.active ? "page" : undefined}
              className={itemClassName}
              data-menu-item={item.id}
              href={item.href}
              key={item.id}
              onClick={onNavigate}
              title={item.label}
            >
              <MenuIcon name={item.icon} />
              <span className="menu-link-copy">{item.label}</span>
              {item.badge ? (
                <span className="menu-item-badge">{item.badge}</span>
              ) : null}
            </Link>
          );
        })}
      </div>
    </section>
  );
}
