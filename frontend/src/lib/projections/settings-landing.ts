/**
 * Local Global Settings fixture for ui_08_settings.md / .svg.
 * Presentation-only until authorized settings projections connect.
 * Secrets values are never included in this fixture.
 */

import type { ScreenLabels } from "./screen-labels";

export type SettingsSectionId =
  | "providers"
  | "secrets"
  | "integrations"
  | "policies"
  | "defaults"
  | "ui"
  | "workspaces";

export interface SettingsNavItem {
  readonly id: SettingsSectionId;
  readonly label: string;
}

export interface SettingsProviderCard {
  readonly id: string;
  readonly name: string;
  readonly icon: string;
  readonly status: "connected" | "degraded" | "disconnected";
  readonly statusLabel: string;
  readonly models: string;
}

export interface SettingsSecretRow {
  readonly id: string;
  readonly name: string;
  readonly scope: string;
  readonly lastRotated: string;
  readonly status: string;
}

export interface SettingsIntegrationCard {
  readonly id: string;
  readonly name: string;
  readonly health: "healthy" | "watch" | "down";
  readonly healthLabel: string;
  readonly detail: string;
}

export interface SettingsPolicyItem {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly enabled: boolean;
  readonly impactLabel: string;
}

export interface SettingsDefaultItem {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly note: string;
}

export interface SettingsMemberRow {
  readonly id: string;
  readonly initials: string;
  readonly name: string;
  readonly role: string;
  readonly status: string;
}

export interface SettingsLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly nav: readonly SettingsNavItem[];
  readonly providers: readonly SettingsProviderCard[];
  readonly secrets: readonly SettingsSecretRow[];
  readonly secretsNote: string;
  readonly integrations: readonly SettingsIntegrationCard[];
  readonly policies: readonly SettingsPolicyItem[];
  readonly policyImpact: {
    readonly title: string;
    readonly body: string;
    readonly affectedLabel: string;
  };
  readonly defaults: readonly SettingsDefaultItem[];
  readonly uiPrefs: readonly {
    readonly id: string;
    readonly label: string;
    readonly value: string;
  }[];
  readonly members: readonly SettingsMemberRow[];
  readonly vaNote: string;
  readonly footerNote: string;
}

export const SETTINGS_NAV: readonly SettingsNavItem[] = [
  { id: "providers", label: "LLM Providers & Models" },
  { id: "secrets", label: "Credentials & Secrets Vault" },
  { id: "integrations", label: "Integrations" },
  { id: "policies", label: "Policies & Guardrails" },
  { id: "defaults", label: "Defaults (Swarm / Common)" },
  { id: "ui", label: "UI & Preferences" },
  { id: "workspaces", label: "Workspaces & Access" },
];

export const LOCAL_SETTINGS_LANDING: SettingsLandingView = {
  labels: {
    "search_across_settings": "Search across settings",
    "name": "Name",
    "scope": "Scope",
    "last_rotated": "Last rotated",
    "status": "Status",
    "actions": "Actions",
    "workspaces_access_control": "Workspaces & Access Control",
    "member": "Member",
    "role": "Role",
    "global_settings": "Global settings",
    "settings_sections": "Settings sections",
  },
  eyebrow: "SETTINGS",
  title: "Global Settings & Configuration",
  description:
    "Self-hosted control center · policy-approved defaults · impact-aware changes.",
  searchPlaceholder: "Search across settings…",
  nav: SETTINGS_NAV,
  providers: [
    {
      id: "xai",
      name: "xAI · Grok",
      icon: "✗",
      status: "connected",
      statusLabel: "Connected",
      models: "Models: grok-3 · grok-3-mini · grok-vision",
    },
    {
      id: "openai",
      name: "OpenAI",
      icon: "◈",
      status: "connected",
      statusLabel: "Connected",
      models: "Models: gpt-4o · gpt-4o-mini · o3",
    },
    {
      id: "ollama",
      name: "Local / Ollama",
      icon: "◎",
      status: "degraded",
      statusLabel: "Degraded",
      models: "Models: llama-3.3 · qwen-2.5",
    },
  ],
  secrets: [
    {
      id: "s1",
      name: "XAI_API_KEY",
      scope: "workspace",
      lastRotated: "12d ago",
      status: "active · value hidden",
    },
    {
      id: "s2",
      name: "STRAPI_TOKEN",
      scope: "global",
      lastRotated: "3d ago",
      status: "active · value hidden",
    },
  ],
  secretsNote:
    "Values never shown to browser after save · reveal is audit-logged · never stored plaintext client-side.",
  integrations: [
    {
      id: "i1",
      name: "Keycloak OIDC",
      health: "healthy",
      healthLabel: "Healthy",
      detail: "Realm-linked session entry · callback authorized",
    },
    {
      id: "i2",
      name: "Strapi CMS",
      health: "watch",
      healthLabel: "Watch",
      detail: "Content import path · untrusted until audited",
    },
    {
      id: "i3",
      name: "Webhook egress",
      health: "healthy",
      healthLabel: "Healthy",
      detail: "Allowlisted destinations only",
    },
  ],
  policies: [
    {
      id: "p1",
      label: "Version pinning policy",
      description:
        "Pinned Common versions cannot be silently replaced mid-run.",
      enabled: true,
      impactLabel: "Affects 14 running swarms",
    },
    {
      id: "p2",
      label: "Contribution defaults",
      description:
        "Verified runs may propose commons contributions with provenance.",
      enabled: true,
      impactLabel: "Affects 8 active commons",
    },
    {
      id: "p3",
      label: "A/B testing defaults",
      description: "Canary split and monitoring duration for rollouts.",
      enabled: false,
      impactLabel: "Affects 0 active campaigns",
    },
    {
      id: "p4",
      label: "Tool scope enforcement",
      description:
        "Runtime tool authorization remains server-side; UI cannot widen scopes.",
      enabled: true,
      impactLabel: "Platform-wide",
    },
  ],
  policyImpact: {
    title: "Policy change impact",
    body: "This change affects 14 running swarms. Workspace settings cannot override an immutable agent version, a required approval, or tool authorization for a live run.",
    affectedLabel: "14 swarms · 3 commons",
  },
  defaults: [
    {
      id: "d1",
      label: "Model routing",
      value: "quality-cost balanced",
      note: "Policy-approved routing only",
    },
    {
      id: "d2",
      label: "Retry / concurrency / budget",
      value: "retry 2 · concurrency 4 · budget band redacted",
      note: "Runtime limits referenced by agent versions",
    },
    {
      id: "d3",
      label: "Artifact retention & rights",
      value: "retain 30d · rights policy enforced",
      note: "Provenance required on release decisions",
    },
    {
      id: "d4",
      label: "Gate / notification defaults",
      value: "L2 gate + notify on block",
      note: "Human approval when gate requires it",
    },
  ],
  uiPrefs: [
    { id: "u1", label: "Theme", value: "Light frame (product default)" },
    { id: "u2", label: "Language", value: "EN · 繁體中文 available" },
    { id: "u3", label: "Density", value: "Comfortable" },
    { id: "u4", label: "Live regions", value: "Status announcements on" },
  ],
  members: [
    {
      id: "m1",
      initials: "NH",
      name: "Nicholas",
      role: "Owner",
      status: "Active",
    },
    {
      id: "m2",
      initials: "AL",
      name: "Alex",
      role: "Operator",
      status: "Active",
    },
  ],
  vaNote:
    "Settings configure only policy-approved defaults (model routing, tool scopes, runtime limits, artifact rights, provenance, gates). They cannot override immutable agent versions or live-run tool authorization.",
  footerNote:
    "Local preview settings · no secret values rendered · Test / Save / Invite require authorized settings actions.",
};
