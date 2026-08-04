/**
 * Local User Profile fixture for ui_13_profile.md / .svg.
 * Presentation-only. No credentials, secrets, or other users' artifacts.
 * Role/org scope remain server-derived.
 */

import type { ScreenLabels } from "./screen-labels";

export type ProfileSectionId =
  | "overview"
  | "account"
  | "security"
  | "usage"
  | "preferences"
  | "tokens";

export interface ProfileImpactCard {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail: string;
}

export interface ProfileContribution {
  readonly id: string;
  readonly common: string;
  readonly type: string;
  readonly status: string;
  readonly impact: string;
}

export interface ProfileTokenRow {
  readonly id: string;
  readonly name: string;
  readonly scopes: string;
  readonly lastUsed: string;
  readonly status: string;
}

export interface ProfileSectionItem {
  readonly id: ProfileSectionId;
  readonly label: string;
}

export interface ProfileLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly displayName: string;
  readonly handle: string;
  readonly initials: string;
  readonly badge: string;
  readonly roleLabel: string;
  readonly workspaceLabel: string;
  readonly rankLabel: string;
  readonly sections: readonly ProfileSectionItem[];
  readonly defaultSectionId: ProfileSectionId;
  readonly impact: readonly ProfileImpactCard[];
  readonly activitySummary: string;
  readonly badges: readonly string[];
  readonly reputation: readonly { readonly label: string; readonly value: string }[];
  readonly contributions: readonly ProfileContribution[];
  readonly ssoProviders: readonly {
    readonly id: string;
    readonly label: string;
    readonly status: string;
  }[];
  readonly preferences: readonly {
    readonly id: string;
    readonly label: string;
    readonly value: string;
  }[];
  readonly tokens: readonly ProfileTokenRow[];
  readonly usageLinks: readonly { readonly label: string; readonly href: string }[];
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_PROFILE_LANDING: ProfileLandingView = {
  labels: {
    "contribution_activity": "Contribution Activity",
    "less": "Less",
    "more": "More",
    "badges_recognition": "Badges & Recognition",
    "reputation_breakdown": "Reputation breakdown",
    "my_contributions": "My Contributions",
    "common": "Common",
    "type": "Type",
    "status": "Status",
    "impact": "Impact",
    "account": "Account",
    "display_name": "Display name",
    "handle": "Handle",
    "role_server_derived": "Role (server-derived)",
    "workspace_scope_server_derived": "Workspace scope (server-derived)",
    "connected_sso_providers": "Connected SSO providers",
    "security": "Security",
    "personal_settings": "Personal Settings",
    "api_token_manager": "API Token Manager",
    "name": "Name",
    "scopes": "Scopes",
    "last_used": "Last used",
    "actions": "Actions",
    "revoke_requires_confirmation_and_an_authorized_t": "Revoke requires confirmation and an authorized token action.",
    "user_profile_and_preferences": "User profile and preferences",
    "profile_sections": "Profile sections",
    "personal_impact": "Personal impact",
    "personal_settings_2": "Personal settings",
    "api_tokens": "API tokens",
  },
  eyebrow: "PROFILE & CONTRIBUTIONS",
  displayName: "Nicholas Hui",
  handle: "NH",
  initials: "NH",
  badge: "Top Contributor",
  roleLabel: "Owner",
  workspaceLabel: "Video Studio",
  rankLabel: "Rank #12 globally · reputation 4,820 · member since 2025",
  sections: [
    { id: "overview", label: "Overview" },
    { id: "account", label: "Account" },
    { id: "security", label: "Security" },
    { id: "usage", label: "Usage & Impact" },
    { id: "preferences", label: "Preferences" },
    { id: "tokens", label: "API Tokens" },
  ],
  defaultSectionId: "overview",
  impact: [
    {
      id: "commons",
      label: "Commons contributed",
      value: "80",
      detail: "agents + patterns",
    },
    {
      id: "merged",
      label: "Proposals merged",
      value: "37",
      detail: "this year",
    },
    {
      id: "swarms",
      label: "Swarms improved",
      value: "142",
      detail: "via commons updates",
    },
    {
      id: "savings",
      label: "Ecosystem savings driven",
      value: "$18k",
      detail: "redacted estimate",
    },
    {
      id: "streak",
      label: "Streak",
      value: "24d",
      detail: "verified contributions",
    },
  ],
  activitySummary: "248 contributions this year",
  badges: [
    "First merge",
    "Verifier champion",
    "Pattern steward",
    "Reviewer",
  ],
  reputation: [
    { label: "Merged proposals", value: "1,920" },
    { label: "Verifications", value: "1,640" },
    { label: "Reviews given", value: "1,260" },
  ],
  contributions: [
    {
      id: "c1",
      common: "video.judge v3.0",
      type: "agent",
      status: "merged",
      impact: "+12% pass rate",
    },
    {
      id: "c2",
      common: "Parallel + Verify Pattern",
      type: "pattern",
      status: "merged",
      impact: "234 swarms base",
    },
    {
      id: "c3",
      common: "video.webresearch v2.2",
      type: "agent",
      status: "merged",
      impact: "−9% tokens",
    },
    {
      id: "c4",
      common: "video.trendintelligence v1.9",
      type: "agent",
      status: "proposed",
      impact: "+5% quality",
    },
  ],
  ssoProviders: [
    { id: "keycloak", label: "Keycloak (self-hosted)", status: "Connected" },
    { id: "github", label: "GitHub", status: "Connected" },
    { id: "google", label: "Google", status: "Not linked" },
  ],
  preferences: [
    { id: "name", label: "Display name", value: "Nicholas Hui" },
    { id: "lang", label: "Preferred language", value: "EN · 繁體中文 available" },
    { id: "theme", label: "Theme", value: "Light frame (product default)" },
    { id: "workspace", label: "Default workspace", value: "Video Studio" },
    { id: "public", label: "Public profile", value: "Attribution: Public" },
    { id: "contrib", label: "Contribution defaults", value: "Opt-in with provenance" },
    { id: "canvas", label: "Execute defaults", value: "Inspect mode · focus off" },
  ],
  tokens: [
    {
      id: "t1",
      name: "ci-readonly",
      scopes: "activity.read · registry.read",
      lastUsed: "2h ago",
      status: "active · value hidden",
    },
    {
      id: "t2",
      name: "notebook-export",
      scopes: "activity.read",
      lastUsed: "12d ago",
      status: "active · value hidden",
    },
  ],
  usageLinks: [
    { label: "My recent activity →", href: "/activity" },
    { label: "My proposals →", href: "/evaluations" },
    { label: "Registry contributions →", href: "/registry" },
  ],
  safetyNote:
    "Reputation reflects server-attributed provenance — not self-declared. Profile does not grant roles, reveal other users' artifacts/critique, or expose credentials/tool authority. Effective role and organization scope remain server-derived.",
  footerNote:
    "Local preview profile · token values never re-shown after create · Save / Create token / Revoke require authorized profile actions.",
};
