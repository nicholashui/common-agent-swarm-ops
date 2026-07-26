import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const map = {
  ActivityHome: "activity-landing.ts",
  AgentDetailHome: "agent-detail-landing.ts",
  ApiPortalHome: "api-portal-landing.ts",
  AuditHome: "audit-landing.ts",
  BlueprintsHome: "blueprints-landing.ts",
  CanvasHome: "canvas-landing.ts",
  CollaborationHome: "collaboration-landing.ts",
  ComposerHome: "composer-landing.ts",
  CostsHome: "costs-landing.ts",
  DashboardHome: "dashboard-landing.ts",
  EvalHome: "eval-landing.ts",
  KnowledgeHome: "knowledge-landing.ts",
  MobileHome: "mobile-landing.ts",
  MonitoringHome: "monitoring-landing.ts",
  NotificationsHome: "notifications-landing.ts",
  OnboardingHome: "onboarding-landing.ts",
  ProfileHome: "profile-landing.ts",
  RegistryHome: "registry-landing.ts",
  SettingsHome: "settings-landing.ts",
  SpecialsCatalog: "specials-landing.ts",
};

/** Humanize key back to default text for missing keys. */
function humanize(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

let fixed = 0;
for (const [comp, land] of Object.entries(map)) {
  const homePath = join("src/components", `${comp}.tsx`);
  const landingPath = join("src/lib/projections", land);
  const home = readFileSync(homePath, "utf8");
  let landing = readFileSync(landingPath, "utf8");
  const keys = [...home.matchAll(/L(?:fmt)?\(\s*labels\s*,\s*"([^"]+)"/g)].map(
    (m) => m[1],
  );
  const miss = [...new Set(keys)].filter((k) => !landing.includes(`"${k}":`));
  if (miss.length === 0) continue;
  console.log(`${comp}: missing ${miss.length} -> injecting defaults`);
  const extras = miss.map((k) => `    "${k}": ${JSON.stringify(humanize(k))},`).join("\n");
  if (landing.includes("labels: {")) {
    landing = landing.replace(/(labels:\s*\{)/, `$1\n${extras}`);
  } else {
    landing = landing.replace(
      /(export const LOCAL_\w+_LANDING: \w+LandingView = \{)/,
      `$1\n  labels: {\n${extras}\n  },`,
    );
  }
  writeFileSync(landingPath, landing);
  fixed += 1;
}
console.log(`fixed ${fixed} landings`);
