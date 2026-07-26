/**
 * Local User Profile fixture for ui_13_profile.md / .svg.
 * Presentation-only. No credentials, secrets, or other users' artifacts.
 * Role/org scope remain server-derived.
 */

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

export interface ProfileLandingView {
  readonly displayName: string;
  readonly handle: string;
  readonly initials: string;
  readonly badge: string;
  readonly roleLabel: string;
  readonly workspaceLabel: string;
  readonly rankLabel: string;
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
  displayName: "Nicholas Hui",
  handle: "NH",
  initials: "NH",
  badge: "Top Contributor",
  roleLabel: "Owner",
  workspaceLabel: "Trading Lab",
  rankLabel: "Rank #12 globally · reputation 4,820 · member since 2025",
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
      common: "VerifierNode v3.0",
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
      common: "DataFetcher v2.2",
      type: "agent",
      status: "merged",
      impact: "−9% tokens",
    },
    {
      id: "c4",
      common: "SentimentAgent v1.9",
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
    { id: "workspace", label: "Default workspace", value: "Trading Lab" },
    { id: "public", label: "Public profile", value: "Attribution: Public" },
    { id: "contrib", label: "Contribution defaults", value: "Opt-in with provenance" },
    { id: "canvas", label: "Canvas defaults", value: "Design mode · focus off" },
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
