/**
 * One-shot: extract hardcoded JSX text / announce() strings from *Home.tsx
 * into landing `labels`, and rewrite components to use L(view.labels, key).
 *
 * Safe for product chrome strings; leaves template expressions alone.
 */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join, basename } from "node:path";

const componentsDir = join(process.cwd(), "src/components");
const projectionsDir = join(process.cwd(), "src/lib/projections");

const HOME_TO_LANDING = {
  ActivityHome: "activity-landing.ts",
  AgentDetailHome: "agent-detail-landing.ts",
  ApiPortalHome: "api-portal-landing.ts",
  AuditHome: "audit-landing.ts",
  BlueprintsHome: "blueprints-landing.ts",
  CanvasHome: "canvas-landing.ts",
  CollaborationHome: "collaboration-landing.ts",
  ComposerHome: "composer-landing.ts",
  CostsHome: "costs-landing.ts",
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

function slugKey(text, used) {
  let base = text
    .toLowerCase()
    .replace(/&amp;/g, "and")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 48);
  if (!base || /^\d/.test(base)) base = `label_${base || "x"}`;
  let key = base;
  let i = 2;
  while (used.has(key)) {
    key = `${base}_${i++}`;
  }
  used.add(key);
  return key;
}

function extractStrings(source) {
  const found = [];
  // JSX text: >Plain text here<
  const jsxRe = />([^<>{}\n][^<>{}\n]{0,120})</g;
  let m;
  while ((m = jsxRe.exec(source))) {
    const text = m[1].trim();
    if (!text) continue;
    if (!/[A-Za-z\u4e00-\u9fff]/.test(text)) continue;
    if (text.includes("{")) continue;
    // skip pure numbers / short noise
    if (text.length < 2) continue;
    found.push({ text, raw: m[0], kind: "jsx" });
  }
  // announce("...")
  const annRe = /announce\(\s*(["'`])([^"'`]+)\1\s*\)/g;
  while ((m = annRe.exec(source))) {
    found.push({ text: m[2], raw: m[0], kind: "announce" });
  }
  // setStatusMessage("...")
  const statusRe = /setStatusMessage\(\s*(["'`])([^"'`]+)\1\s*\)/g;
  while ((m = statusRe.exec(source))) {
    found.push({ text: m[2], raw: m[0], kind: "status" });
  }
  // placeholder="..."
  const phRe = /placeholder=(["'])([^"']+)\1/g;
  while ((m = phRe.exec(source))) {
    found.push({ text: m[2], raw: m[0], kind: "placeholder" });
  }
  // aria-label="..." static
  const ariaRe = /aria-label=(["'])([^"'{]+)\1/g;
  while ((m = ariaRe.exec(source))) {
    found.push({ text: m[2], raw: m[0], kind: "aria" });
  }
  return found;
}

function decodeHtml(text) {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"');
}

function processHome(componentName, landingFile) {
  const homePath = join(componentsDir, `${componentName}.tsx`);
  const landingPath = join(projectionsDir, landingFile);
  let home = readFileSync(homePath, "utf8");
  let landing = readFileSync(landingPath, "utf8");

  const extracted = extractStrings(home);
  if (extracted.length === 0) {
    console.log(`skip ${componentName}: no extractable strings`);
    return;
  }

  // Dedupe by text
  const used = new Set();
  const textToKey = new Map();
  const labels = {};
  for (const item of extracted) {
    const text = decodeHtml(item.text.trim());
    if (!textToKey.has(text)) {
      const key = slugKey(text, used);
      textToKey.set(text, key);
      labels[key] = text;
    }
  }

  // Ensure labels import + field on landing
  if (!landing.includes('from "./screen-labels"') && !landing.includes("ScreenLabels")) {
    landing = landing.replace(
      /^(?:\s*\/\*\*[\s\S]*?\*\/\s*)?/,
      (prefix) =>
        `${prefix}import type { ScreenLabels } from "./screen-labels";\n\n`,
    );
  }
  if (!landing.includes("readonly labels: ScreenLabels")) {
    landing = landing.replace(
      /(export interface \w+LandingView \{)/,
      `$1\n  readonly labels: ScreenLabels;`,
    );
  }

  // Inject labels object into LOCAL constant if missing
  if (!landing.includes("labels: {") && !landing.includes("labels:{")) {
    const labelsLiteral = Object.entries(labels)
      .map(([k, v]) => `    ${JSON.stringify(k)}: ${JSON.stringify(v)},`)
      .join("\n");
    // Insert after opening of LOCAL_*_LANDING =
    landing = landing.replace(
      /(export const LOCAL_\w+_LANDING: \w+LandingView = \{\n)/,
      `$1  labels: {\n${labelsLiteral}\n  },\n`,
    );
  } else {
    // Merge new keys into existing labels block
    const labelsLiteral = Object.entries(labels)
      .map(([k, v]) => `    ${JSON.stringify(k)}: ${JSON.stringify(v)},`)
      .join("\n");
    landing = landing.replace(
      /(labels:\s*\{)([\s\S]*?)(\n\s*\},)/,
      (full, a, body, c) => {
        const existingKeys = new Set(
          [...body.matchAll(/["']?([a-zA-Z0-9_]+)["']?\s*:/g)].map((x) => x[1]),
        );
        const extras = Object.entries(labels)
          .filter(([k]) => !existingKeys.has(k))
          .map(([k, v]) => `    ${JSON.stringify(k)}: ${JSON.stringify(v)},`)
          .join("\n");
        if (!extras) return full;
        return `${a}${body}\n${extras}${c}`;
      },
    );
  }

  // Ensure home imports L/Lfmt
  if (!home.includes('from "../lib/projections/screen-labels"')) {
    home = home.replace(
      /(from "\.\.\/lib\/projections\/[^"]+";\n)/,
      `$1import { L, Lfmt } from "../lib/projections/screen-labels";\n`,
    );
  }

  // Ensure const labels = view.labels near start of function
  if (!home.includes("const labels = view.labels")) {
    home = home.replace(
      /(export function \w+\(\{[\s\S]*?view[\s\S]*?\}[\s\S]*?\{)\n/,
      `$1\n  const labels = view.labels;\n`,
    );
  }

  // Replace JSX text nodes
  for (const [text, key] of textToKey) {
    // encode for HTML entities in source
    const variants = [
      text,
      text.replace(/&/g, "&amp;"),
    ];
    for (const variant of variants) {
      // >variant<
      const jsxNeedle = `>${variant}<`;
      const jsxRepl = `>{L(labels, ${JSON.stringify(key)})}<`;
      home = home.split(jsxNeedle).join(jsxRepl);
    }
    // announce("text")
    home = home.replace(
      new RegExp(`announce\\(\\s*(["'\`])${escapeReg(text)}\\1\\s*\\)`, "g"),
      `announce(L(labels, ${JSON.stringify(key)}))`,
    );
    home = home.replace(
      new RegExp(`setStatusMessage\\(\\s*(["'\`])${escapeReg(text)}\\1\\s*\\)`, "g"),
      `setStatusMessage(L(labels, ${JSON.stringify(key)}))`,
    );
    home = home.replace(
      new RegExp(`placeholder=(["'])${escapeReg(text)}\\1`, "g"),
      `placeholder={L(labels, ${JSON.stringify(key)})}`,
    );
    home = home.replace(
      new RegExp(`aria-label=(["'])${escapeReg(text)}\\1`, "g"),
      `aria-label={L(labels, ${JSON.stringify(key)})}`,
    );
  }

  writeFileSync(landingPath, landing);
  writeFileSync(homePath, home);
  console.log(`updated ${componentName}: ${textToKey.size} labels`);
}

function escapeReg(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

for (const [home, landing] of Object.entries(HOME_TO_LANDING)) {
  try {
    processHome(home, landing);
  } catch (err) {
    console.error(`FAILED ${home}:`, err);
    process.exitCode = 1;
  }
}
